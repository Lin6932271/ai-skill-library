"""Install and test the trusted, bundled REA runtime without network or system changes."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import queue
import re
import shutil
import stat
import subprocess
import tempfile
import threading
import time
import uuid
import zipfile

from rea_config import ReaError


def iter_schema_patterns(schema):
    """Walk schema positions, excluding examples/defaults and property names."""
    if not isinstance(schema, dict):
        return
    if 'pattern' in schema:
        yield schema['pattern']
    for key in ('properties', 'patternProperties', '$defs', 'definitions', 'dependentSchemas'):
        mapping = schema.get(key, {})
        if isinstance(mapping, dict):
            if key == 'patternProperties':
                yield from mapping.keys()
            for child in mapping.values():
                yield from iter_schema_patterns(child)
    for key in ('anyOf', 'oneOf', 'allOf', 'prefixItems'):
        for child in schema.get(key, []):
            yield from iter_schema_patterns(child)
    for key in ('items', 'additionalProperties', 'contains', 'propertyNames', 'not', 'if', 'then', 'else',
                'unevaluatedProperties', 'unevaluatedItems'):
        child = schema.get(key)
        for item in child if isinstance(child, list) else [child]:
            yield from iter_schema_patterns(item)


def validate_tool_schemas(tools):
    """Reject malformed patterns and known cross-engine incompatibilities."""
    count = 0
    for tool in tools:
        for pattern in iter_schema_patterns(tool.get('inputSchema', {})):
            if (not isinstance(pattern, str) or re.search(r'(?<!\\)(?:\\\\)*\\0(?![0-9])', pattern)
                    or any(token in pattern for token in ('(?=', '(?!', '(?<=', '(?<!'))
                    or has_nested_character_class(pattern)):
                raise ReaError('REA 工具参数包含不兼容正则，请使用修复版运行包')
            try:
                re.compile(pattern)
            except re.error as exc:
                raise ReaError('REA 工具参数正则格式异常，未写入客户端连接') from exc
            count += 1
    return count


def has_nested_character_class(pattern):
    """Exclude nested/literal unescaped '[' from the advertised regex subset.

    Different engines interpret it as either a literal or a nested character set.
    An escaped bracket or its hexadecimal notation is portable.
    """
    inside = escaped = False
    for char in pattern:
        if escaped:
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == '[':
            if inside:
                return True
            inside = True
        elif char == ']':
            inside = False
    return False


def digest_file(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_directory(path: Path):
    for parent in [path, *path.parents]:
        if parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()):
            raise ReaError(f"REA 目录包含链接或目录联接：{parent}")
    if path.exists() and not path.is_dir():
        raise ReaError(f"REA 环境目录不是文件夹：{path}")


class ReaRuntime:
    def __init__(self, bundle_dir: Path, data_dir: Path):
        self.bundle_dir, self.data_dir = bundle_dir, data_dir
        self.progress_lock = threading.Lock()
        self.progress = {"stage": "idle", "message": "", "percent": 0}
        self.last_probe = None
        manifest = bundle_dir / "runtime/manifest.json"
        self.manifest = json.loads(manifest.read_text("utf-8")) if manifest.is_file() else None

    def update(self, message, percent, stage="preparing"):
        with self.progress_lock:
            self.progress = {"stage": stage, "message": message, "percent": percent}

    def progress_status(self):
        with self.progress_lock:
            return dict(self.progress)

    def summary(self):
        return {"bundled": bool(self.manifest), "version": (self.manifest or {}).get("rea_version"),
                "offline": True, "message": "内置 REA；开启技能时自动准备环境和连接" if self.manifest else "缺少内置 REA 环境"}

    def is_current(self, runtime):
        if not self.manifest or not runtime:
            return False
        expected = 'rea-' + self.manifest['rea_version'] + '-' + self.manifest['sha256'][:12]
        return Path(runtime.get('root', '')).name == expected

    def owned_runtime(self, launch):
        """Recognize only unchanged executables previously released by this app."""
        try:
            node = Path(launch['command'])
            root = node.parent.parent
            safe_directory(root)
            if root.resolve().parent != (self.data_dir / 'rea').resolve():
                return None
            marker = json.loads((root / '.ready.json').read_text('utf-8'))
            archive_hash = marker['archive_sha256']
            if archive_hash == self.manifest['sha256']:
                critical = self.manifest['critical_files']
            elif archive_hash == self.manifest.get('upstream_archive_sha256'):
                critical = self.manifest['upstream_critical_files']
            else:
                previous = next((item for item in self.manifest.get('previous_runtimes', [])
                                 if item.get('sha256') == archive_hash and item.get('rea_version') == self.manifest['rea_version']), None)
                if previous is None:
                    return None
                critical = previous['critical_files']
            if root.name != 'rea-' + self.manifest['rea_version'] + '-' + archive_hash[:12]:
                return None
            entry = root / 'cli/node_modules/rea-agents/scripts/rea.mjs'
            if node != root / 'node/node.exe' or launch.get('args') != [str(entry), 'mcp']:
                return None
            if not all(digest_file(root / rel) == expected for rel, expected in critical.items()):
                return None
            return {'root':str(root), 'node':str(node), 'entry':str(entry),
                    'cli':str(root / 'rea.cmd'), 'version':self.manifest['rea_version']}
        except (OSError, ValueError, KeyError, TypeError, ReaError):
            return None

    def ready(self, runtime):
        try:
            root = Path(runtime["root"])
            safe_directory(root)
            return bool(self.manifest and all(digest_file(root / rel) == value
                        for rel, value in self.manifest["critical_files"].items()))
        except (OSError, ReaError, KeyError):
            return False

    def ensure(self):
        manifest = self.manifest
        if not manifest:
            raise ReaError("程序缺少内置 REA 运行环境，请使用完整新版安装包")
        if os.name != "nt":
            raise ReaError("内置 REA 运行环境需要 Windows x64")
        self.update("正在准备 REA 内置环境", 5)
        folder = self.data_dir / "rea" / ("rea-" + manifest["rea_version"] + "-" + manifest["sha256"][:12])
        safe_directory(folder)
        marker = folder / ".ready.json"
        if not marker.is_file():
            if folder.exists():
                raise ReaError("REA 环境不完整，原文件已保留；请使用新的数据目录或从备份恢复")
            archive = self.bundle_dir / "runtime" / manifest["archive"]
            if digest_file(archive) != manifest["sha256"]:
                raise ReaError("内置 REA 安装包校验失败，未运行任何程序")
            folder.parent.mkdir(parents=True, exist_ok=True)
            staging = Path(tempfile.mkdtemp(prefix=".rea-prepare-", dir=folder.parent))
            try:
                with zipfile.ZipFile(archive) as bundle:
                    entries = bundle.infolist()
                    names = set()
                    total = 0
                    for index, member in enumerate(entries):
                        rel = PurePosixPath(member.filename)
                        target = staging / member.filename
                        name = member.filename.casefold()
                        total += member.file_size
                        if (rel.is_absolute() or ".." in rel.parts or "\\" in member.filename
                                or ":" in member.filename or name in names
                                or stat.S_ISLNK(member.external_attr >> 16)
                                or total > 512 * 1024 * 1024 or len(entries) > 20000):
                            raise ReaError("内置 REA 安装包成员异常")
                        names.add(name)
                        if member.is_dir():
                            target.mkdir(parents=True, exist_ok=True)
                            continue
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with bundle.open(member) as source, target.open("wb") as output:
                            shutil.copyfileobj(source, output)
                        if index % 200 == 0:
                            self.update("正在释放 REA 内置环境，请稍候", 10 + int(index / len(entries) * 60))
                file_index = json.loads((staging / "files.json").read_text("utf-8"))
                if len(file_index) != manifest["file_count"]:
                    raise ReaError("内置 REA 文件数量校验失败")
                self.update("正在校验 REA 内置文件", 70)
                for index, (rel, expected) in enumerate(file_index.items()):
                    file = staging / rel
                    parts = PurePosixPath(rel)
                    if (parts.is_absolute() or ".." in parts.parts or "\\" in rel or ":" in rel
                            or file.is_symlink() or digest_file(file) != expected):
                        raise ReaError("内置 REA 文件完整性校验失败")
                    if index % 200 == 0:
                        self.update("正在校验 REA 内置文件", 70 + int(index / len(file_index) * 9))
                marker_data = {"archive_sha256": manifest["sha256"], "installed_at": time.time()}
                (staging / marker.name).write_text(json.dumps(marker_data), encoding="utf-8")
                os.replace(staging, folder)
            finally:
                if staging.exists():
                    shutil.rmtree(staging)
        try:
            if json.loads(marker.read_text("utf-8"))["archive_sha256"] != manifest["sha256"]:
                raise ReaError("REA 环境版本校验失败")
            for rel, expected in manifest["critical_files"].items():
                if digest_file(folder / rel) != expected:
                    raise ReaError("REA 运行文件被更改，已保留；请从备份恢复")
        except (OSError, ValueError, KeyError) as exc:
            raise ReaError("REA 环境缺失或被更改，未运行") from exc
        runtime = {"root": str(folder), "node": str(folder / "node/node.exe"),
                   "entry": str(folder / "cli/node_modules/rea-agents/scripts/rea.mjs"),
                   "version": manifest["rea_version"], "cli": str(folder / "rea.cmd")}
        wrapper = ('@echo off\r\nchcp 65001 >nul\r\nsetlocal\r\nset "PATH=' + str(folder / "node") + ';%PATH%"\r\n'
                   + '"' + runtime["node"] + '" "' + runtime["entry"] + '" %*\r\nexit /b %errorlevel%\r\n')
        (folder / "rea.cmd").write_text(wrapper, encoding="utf-8")
        self.update("REA 环境已准备，正在测试启动", 80)
        return runtime

    @staticmethod
    def process_options(runtime):
        env = dict(os.environ)
        env["PATH"] = str(Path(runtime["node"]).parent) + os.pathsep + env.get("PATH", "")
        return {"env": env, "creationflags": subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0}

    def probe(self, runtime, analyze_path=None, schema_output=None):
        self.update("正在测试 REA CLI 和 MCP 连接", 85, "testing")
        options = self.process_options(runtime)
        try:
            version = subprocess.run([runtime["node"], runtime["entry"], "--version"],
                                     capture_output=True, text=True, encoding="utf-8", timeout=45, **options)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ReaError("REA CLI 无法启动或测试超时") from exc
        if version.returncode or version.stdout.strip() != runtime["version"]:
            raise ReaError("REA CLI 启动测试失败，请查看诊断")
        process = subprocess.Popen([runtime["node"], runtime["entry"], "mcp"], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, encoding="utf-8", **options)
        messages = queue.Queue()
        errors = []

        def stdout_reader():
            for line in process.stdout:
                try:
                    messages.put(json.loads(line))
                except ValueError:
                    messages.put({"invalid": True})
            messages.put({"exited": True})

        def stderr_reader():
            for line in process.stderr:
                if len(errors) < 50:
                    errors.append(line[-1000:])

        readers = [threading.Thread(target=stdout_reader, daemon=True), threading.Thread(target=stderr_reader, daemon=True)]
        for reader in readers:
            reader.start()
        counter = 0

        def send(payload):
            process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
            process.stdin.flush()

        def request(method, params=None):
            nonlocal counter
            counter += 1
            send({"jsonrpc": "2.0", "id": counter, "method": method, "params": params or {}})
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                try:
                    message = messages.get(timeout=max(.1, deadline - time.monotonic()))
                except queue.Empty as exc:
                    raise ReaError("REA MCP 连接测试超时") from exc
                if message.get("invalid") or message.get("exited"):
                    raise ReaError("REA MCP 启动失败，请查看诊断")
                if message.get("id") == counter:
                    if "error" in message:
                        raise ReaError("REA MCP 返回错误")
                    return message["result"]
            raise ReaError("REA MCP 连接测试超时")

        try:
            initialized = request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "ai-skill-library", "version": "1.4.2"}})
            send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            tools, cursor = [], None
            while True:
                page = request("tools/list", {"cursor": cursor} if cursor else {})
                tools.extend(page["tools"])
                cursor = page.get("nextCursor")
                if not cursor:
                    break
            pattern_count = validate_tool_schemas(tools)
            if schema_output is not None:
                Path(schema_output).write_text(json.dumps(tools, ensure_ascii=False, indent=2), encoding='utf-8')
            if not tools or initialized.get("serverInfo", {}).get("version") != runtime["version"]:
                raise ReaError("REA MCP 工具或版本校验失败")
            result = {"ok": True, "version": runtime["version"], "tool_count": len(tools),
                      "checked_at": time.time(), "client_connected": False,
                      "schema_patterns_checked": pattern_count,
                      "compatibility_patch": self.manifest.get('compatibility_patch')}
            if analyze_path is not None:
                tool = next(t for t in tools if t["name"] == "analyze_javascript_application")
                if "input_path" not in tool["inputSchema"]["properties"]:
                    raise ReaError("REA 分析接口格式变化")
                analysis = request("tools/call", {"name": tool["name"], "arguments": {"input_path": str(analyze_path)}})
                if analysis.get("isError"):
                    raise ReaError("REA 样例分析失败")
                result["analysis"] = analysis
            self.last_probe = result
            self.update("REA 已就绪，重启客户端后自动连接", 100, "ready")
            return result
        except (OSError, KeyError, ValueError, StopIteration) as exc:
            raise ReaError("REA MCP 测试失败，未报告连接成功") from exc
        finally:
            try:
                process.stdin.close()
                process.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                process.kill()
                process.wait(timeout=5)
            for reader in readers:
                reader.join(timeout=1)
            for stream in (process.stdout, process.stderr):
                stream.close()
