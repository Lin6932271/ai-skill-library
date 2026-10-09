"""Skill installation, import, backup, verification and revocation."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import tempfile
import threading
import time
import uuid
import zipfile
from pathlib import Path
from rea_config import McpConfig, ReaError
from rea_runtime import ReaRuntime

VERSION = "1.4.1"
BEGIN = b"<!-- POJIA-LOCAL:BEGIN -->"
END = b"<!-- POJIA-LOCAL:END -->"
MAX_IMPORT = 32 * 1024 * 1024
PROVIDERS = {
    "codex": ("Codex", "CODEX_HOME", ".codex", "AGENTS.md", "codex"),
    "claude": ("Claude", "CLAUDE_CONFIG_DIR", ".claude", "CLAUDE.md", "claudecode-C-I2ikfH.png"),
    "deepseek": ("DeepSeek Harness", "DSH_HOME", ".dsh", "AGENTS.md", "deepseek-D7HLyW1e.png"),
    "hermes": ("Hermes", "HERMES_HOME", ".hermes", "HERMES.md", "hermes-B4tfm5PS.png"),
    "zcode": ("ZCode", "ZCODE_HOME", ".zcode", "AGENTS.md", "zcode-CpHpZiag.png"),
    "workbuddy": ("WorkBuddy 国内版", "WORKBUDDY_CONFIG_DIR", ".workbuddy", "CODEBUDDY.md", "workbuddy-bXUtzuef.png"),
    "workbuddy_ai": ("WorkBuddy 国际版", "WORKBUDDY_AI_CONFIG_DIR", ".workbuddy-ai", "CODEBUDDY.md", "workbuddy-bXUtzuef.png"),
}


class LocalError(Exception):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".pojia-local-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def assert_regular_path(path: Path) -> None:
    # Junctions and symlinks may escape the selected configuration folder.
    for part in [path, *path.parents]:
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise LocalError(f"目录包含链接或目录联接，请选择实际目录：{part}")
    if path.exists() and not path.is_file():
        raise LocalError(f"目标不是普通文件：{path}")


def read_file(path: Path) -> bytes | None:
    assert_regular_path(path)
    return path.read_bytes() if path.exists() else None


def split_block(data: bytes) -> tuple[bytes, bytes, bytes] | None:
    if BEGIN not in data and END not in data:
        return None
    if data.count(BEGIN) != 1 or data.count(END) != 1:
        raise LocalError("指令文件的管理标记异常；请先检查文件，未修改原文")
    start = data.index(BEGIN)
    stop = data.index(END) + len(END)
    if start >= stop - len(END):
        raise LocalError("指令文件的管理标记顺序异常")
    return data[:start], data[start:stop], data[stop:]


class SkillManager:
    def __init__(self, data_dir: Path | None = None, home: Path | None = None,
                 bundle_dir: Path | None = None, use_env: bool = True):
        self.home = (home or Path.home()).absolute()
        self.bundle_dir = bundle_dir or Path(__file__).parent
        self.data_dir = (data_dir or Path(os.environ.get("LOCALAPPDATA", self.home)) / "PojiaLocal").absolute()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.use_env = use_env
        self.state_file = self.data_dir / "state.json"
        self.state = {"schema": 1, "paths": {}, "installed": {}, "custom": {}, "events": []}
        if self.state_file.exists():
            try:
                loaded = json.loads(self.state_file.read_text("utf-8"))
                if loaded.get("schema") != 1:
                    raise ValueError("schema")
                for key in self.state:
                    if key in loaded:
                        self.state[key] = loaded[key]
            except (ValueError, OSError) as exc:
                raise LocalError("本地状态文件损坏，已保留原文件；请从备份恢复") from exc
        self.started = time.time()
        catalog_path = self.bundle_dir / "skills" / "extensions-catalog.json"
        self.catalog = json.loads(catalog_path.read_text("utf-8"))["items"] if catalog_path.exists() else []
        self.extensions = {item["id"]: item for item in self.catalog}
        builtin_path = self.bundle_dir / "skills" / "builtin-catalog.json"
        self.builtin_catalog = json.loads(builtin_path.read_text("utf-8"))["items"] if builtin_path.exists() else []
        self.builtins = {item["id"]: item for item in self.builtin_catalog}
        self.indexed = {**self.extensions, **self.builtins}
        self.rea = ReaRuntime(self.bundle_dir, self.data_dir)

    def save(self) -> None:
        atomic_write(self.state_file, json.dumps(self.state, ensure_ascii=False, indent=2).encode("utf-8"))

    def event(self, action: str, provider: str, detail: str) -> None:
        self.state["events"].append({"time": time.strftime("%Y-%m-%d %H:%M:%S"),
                                     "action": action, "provider": provider, "detail": detail})
        self.state["events"] = self.state["events"][-100:]
        self.save()

    def root(self, provider: str) -> Path:
        if provider not in PROVIDERS:
            raise LocalError("未知客户端")
        selected = self.state["paths"].get(provider)
        if selected:
            return Path(selected)
        aliases = {
            "claude": ("CLAUDE_CONFIG_DIR", "CLAUDE_HOME", "ANTHROPIC_CONFIG_DIR"),
            "deepseek": ("DSH_HOME", "DEEPSEEK_HOME", "DEEPSEEK_CONFIG_DIR"),
            "hermes": ("HERMES_HOME", "HERMES_CONFIG_DIR"),
            "workbuddy": ("WORKBUDDY_CONFIG_DIR", "CODEBUDDY_CONFIG_DIR"),
            "workbuddy_ai": ("WORKBUDDY_AI_CONFIG_DIR",),
        }
        env = next((os.environ[key].strip() for key in aliases.get(provider, (PROVIDERS[provider][1],))
                    if os.environ.get(key, "").strip()), None) if self.use_env else None
        if env:
            root = Path(env).expanduser().absolute()
            if provider == "claude" and root.name.lower() == "claude.md":
                root = root.parent
        else:
            root = self.home / PROVIDERS[provider][2]
            if provider == "hermes" and self.use_env and os.name == "nt" and not root.is_dir():
                root = Path(os.environ.get("LOCALAPPDATA", self.home / "AppData" / "Local")) / "hermes"
        if provider == "hermes" and self.use_env:
            active = os.environ.get("HERMES_PROFILE", "").strip()
            if not active and (root / "active_profile").is_file():
                active = (root / "active_profile").read_text("utf-8-sig").strip()
            if active and active != "default":
                if active in (".", "..") or any(c in active for c in "/\\:"):
                    raise LocalError("Hermes 当前 profile 名称无效，请手动选择配置目录")
                root = root / "profiles" / active
        return root

    def set_path(self, provider: str, value: str) -> dict:
        with self.lock:
            self.root(provider)
            if self.state["installed"].get(provider):
                raise LocalError("请先撤销该客户端的本地技能，再切换目录")
            if value:
                if any(ord(c) < 32 for c in value):
                    raise LocalError("目录不能包含控制字符")
                path = Path(value).expanduser()
                if not path.is_absolute() or path == Path(path.anchor):
                    raise LocalError("请选择完整的客户端目录，不能使用磁盘根目录")
                for part in [path, *path.parents]:
                    if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                        raise LocalError("请选择实际目录，不支持链接或目录联接")
                if path.exists() and not path.is_dir():
                    raise LocalError("请选择文件夹")
                for other in ("workbuddy", "workbuddy_ai"):
                    if provider in ("workbuddy", "workbuddy_ai") and other != provider:
                        if path.resolve() == self.root(other).resolve():
                            raise LocalError("WorkBuddy 国内版和国际版须使用不同目录")
                self.state["paths"][provider] = str(path.absolute())
            else:
                self.state["paths"].pop(provider, None)
            self.save()
            return {"path": str(self.root(provider))}

    def profiles(self) -> list[dict]:
        result = ([{"id": "extended", "name": "扩展技能库 · 50 项", "description": "安装扩展入口与模块，按任务读取", "builtin": True, "collection": "extension", "category": "整套"}] if self.catalog else []) + [
            {"id": "basic", "name": "基础技能", "description": "通用开发流程、证据与验收规范", "builtin": True},
            {"id": "advanced", "name": "进阶技能", "description": "增加调试、审查与变更交付规范", "builtin": True},
        ]
        if self.builtin_catalog:
            result.insert(0, {"id": "builtin", "name": f"完整技能库 · {len(self.builtin_catalog)} 项", "description": "安装全部入口与模块，按任务读取", "builtin": True, "collection": "builtin", "category": "整套"})
            result.extend(self.builtin_catalog)
        result.extend(self.catalog)
        result.extend({"id": key, "name": value["name"], "description": "从本地导入", "builtin": False}
                      for key, value in self.state["custom"].items())
        return result

    @staticmethod
    def normalize_profile(profile: str) -> str:
        aliases = {"original": "basic", "curated": "advanced",
                   "cloud-all": "builtin", "rebuilt-all": "extended"}
        if profile in aliases:
            return aliases[profile]
        for before, after in (("cloud-", "builtin-"), ("rebuilt-", "extension-")):
            if profile.startswith(before):
                return after + profile[len(before):]
        return profile

    def profile_root(self, profile: str) -> Path:
        profile = self.normalize_profile(profile)
        if profile in ("basic", "advanced", "extended", "builtin"):
            return self.bundle_dir / "skills" / profile
        if profile in self.extensions:
            return self.bundle_dir / "skills" / "extended" / "library" / self.extensions[profile]["skill_name"]
        if profile in self.builtins:
            return self.bundle_dir / "skills" / "builtin" / "library" / self.builtins[profile]["skill_name"]
        if profile not in self.state["custom"] or not re.fullmatch(r"local-[a-f0-9]{16}", profile):
            raise LocalError("未找到技能方案")
        return self.data_dir / "imports" / profile

    def profile_files(self, profile: str) -> dict[str, bytes]:
        root = self.profile_root(profile)
        files = {}
        total = 0
        for path in sorted(root.rglob("*")):
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                raise LocalError("技能包含链接，未导入")
            if not path.is_file():
                continue
            data = path.read_bytes()
            total += len(data)
            if total > MAX_IMPORT or len(files) >= 2000:
                raise LocalError("技能资源超过 32 MB 或 2000 个文件")
            files[path.relative_to(root).as_posix()] = data
        if "SKILL.md" not in files:
            raise LocalError("技能目录需要 SKILL.md")
        return files

    def _profile_deployment_files(self, profile: str) -> dict[str, bytes]:
        profile = self.normalize_profile(profile)
        files = self.profile_files(profile)
        if profile in ("extended", "builtin"):
            return {(rel.removeprefix("library/") if rel.startswith("library/") else "pojia-local/" + rel): data
                    for rel, data in files.items()}
        folder = self.indexed[profile]["skill_name"] if profile in self.indexed else "pojia-local"
        deployed = {folder + "/" + rel: data for rel, data in files.items()}
        if profile in self.indexed:
            for dependency in self.indexed[profile].get("dependencies", []):
                child_files = self.profile_files(("builtin-" if profile in self.builtins else "extension-") + dependency)
                deployed.update({dependency + "/" + rel: data for rel, data in child_files.items()})
        return deployed

    def deployment_files(self, profile: str) -> dict[str, bytes]:
        files = self._profile_deployment_files(profile)
        for rel, data in self.profile_files("builtin-reverse-engineer-anything").items():
            files["reverse-engineer-anything/" + rel] = data
        return files

    @staticmethod
    def installed_files(record: dict) -> dict[Path, dict]:
        # Records without files_root use the instruction entry directory.
        base = Path(record.get("files_root", str(Path(record["root"]) / "skills" / "pojia-local")))
        return {base / rel: expected for rel, expected in record["files"].items()}

    def read_profile(self, profile: str) -> dict:
        profile = self.normalize_profile(profile)
        files = self.profile_files(profile)
        return {"profile": profile, "content": files["SKILL.md"].decode("utf-8-sig"),
                "files": [{"name": key, "size": len(value)} for key, value in files.items()]}

    def import_skill(self, source: str) -> dict:
        with self.lock:
            path = Path(source)
            if not path.exists():
                raise LocalError("技能路径不存在")
            staging = Path(tempfile.mkdtemp(prefix="skill-", dir=self.data_dir))
            try:
                if path.suffix.lower() == ".zip" and path.is_file():
                    with zipfile.ZipFile(path) as archive:
                        total = 0
                        if len(archive.infolist()) > 2000:
                            raise LocalError("压缩包文件数量超过限制")
                        names = set()
                        for item in archive.infolist():
                            rel = Path(item.filename.replace("\\", "/"))
                            if rel.is_absolute() or ".." in rel.parts or ":" in item.filename:
                                raise LocalError("压缩包包含越界路径")
                            dest = staging / rel
                            if not dest.resolve().is_relative_to(staging.resolve()):
                                raise LocalError("压缩包包含越界路径")
                            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                                raise LocalError("压缩包包含符号链接")
                            normalized = str(rel).casefold()
                            if normalized in names:
                                raise LocalError("压缩包包含重复路径")
                            names.add(normalized)
                            total += item.file_size
                            if total > MAX_IMPORT:
                                raise LocalError("解压后的技能资源超过 32 MB")
                            if item.is_dir():
                                dest.mkdir(parents=True, exist_ok=True)
                            else:
                                dest.parent.mkdir(parents=True, exist_ok=True)
                                with archive.open(item) as stream:
                                    data = stream.read(MAX_IMPORT + 1)
                                if len(data) != item.file_size:
                                    raise LocalError("压缩包内容大小无效")
                                dest.write_bytes(data)
                    candidates = list(staging.rglob("SKILL.md"))
                    if len(candidates) != 1:
                        raise LocalError("每次导入一个技能，压缩包中须恰有一个 SKILL.md")
                    root = candidates[0].parent
                elif path.is_dir():
                    root = path
                elif path.is_file() and path.suffix.lower() == ".md":
                    shutil.copyfile(path, staging / "SKILL.md")
                    root = staging
                else:
                    raise LocalError("支持 SKILL.md、技能文件夹或 ZIP 文件")
                # Validate before copying; never execute imported scripts.
                files = {}
                size = 0
                for file in root.rglob("*"):
                    if file.is_symlink() or (hasattr(file, "is_junction") and file.is_junction()):
                        raise LocalError("技能包含链接")
                    if file.is_file():
                        data = file.read_bytes()
                        size += len(data)
                        if size > MAX_IMPORT or len(files) >= 2000:
                            raise LocalError("技能超过导入限制")
                        files[file.relative_to(root).as_posix()] = data
                if "SKILL.md" not in files:
                    raise LocalError("技能文件夹缺少 SKILL.md")
                body = files["SKILL.md"].decode("utf-8-sig")
                if not body.strip():
                    raise LocalError("技能正文不能为空")
                heading = re.search(r"(?m)^#\s+(.+)$", body)
                name = heading.group(1).strip() if heading else path.stem
                key = "local-" + uuid.uuid4().hex[:16]
                if not body.startswith("---"):
                    body = f"---\nname: pojia-local\ndescription: {json.dumps(name, ensure_ascii=False)}\n---\n\n{body}"
                    files["SKILL.md"] = body.encode("utf-8")
                dest = self.data_dir / "imports" / key
                for rel, data in files.items():
                    atomic_write(dest / rel, data)
                self.state["custom"][key] = {"name": name, "imported_at": time.time()}
                self.event("import", "", name)
                return {"id": key, "name": name}
            finally:
                shutil.rmtree(staging)

    def block(self, provider: str, profile: str, runtime: dict | None = None) -> bytes:
        content = self.profile_files(profile)["SKILL.md"].decode("utf-8-sig")
        # Frontmatter belongs to the skill file, not the global instruction file.
        if content.startswith("---"):
            match = re.match(r"\A---\s*\n.*?\n---\s*\n", content, re.S)
            if match:
                content = content[match.end():]
        if BEGIN.decode() in content or END.decode() in content:
            raise LocalError("技能正文不能包含本助手的管理标记")
        folder = self.indexed[profile]["skill_name"] if profile in self.indexed else "pojia-local"
        relative = f"skills/{folder}/SKILL.md"
        content = (f"\n# ai技能库\n\n"
                   f"此段由 ai技能库 管理。完整技能资源：`{relative}`。\n"
                   "用户发送 `hi` 时，简短报告当前技能已读取；未读取时如实说明。\n\n" + content.strip() + "\n")
        content += ("\n## 自动选择技能与 REA\n\n"
                    "用户只说‘使用技能’时，根据目标和任务自行选择、组合相关技能；不要求用户知道技能名称或配置 MCP。\n"
                    "涉及打包应用、二进制、Electron/JavaScript 或版本行为对比时，按需读取 "
                    "`skills/reverse-engineer-anything/SKILL.md`。普通源码开发按对应工程技能处理。\n"
                    "REA 连接由客户端自动启动。工具未出现在当前会话时，提示重启客户端；不重复安装已配置的 REA。\n"
                    "环境准备和 MCP 启动测试通过不等于客户端已连接，也不等于全部反编译引擎可用。\n")
        if runtime:
            content += (f"\n已配置的 REA MCP 名称：`ai_skill_library_rea`。"
                        f"无 MCP 工具时，可通过已内置的 CLI：`{runtime['cli']}` 使用支持的命令；"
                        "先查看 `--help`，无需安装 npm 包。\n")
        return BEGIN + content.encode("utf-8") + END

    def inject(self, provider: str, profile: str = "basic") -> dict:
        profile = self.normalize_profile(profile)
        with self.lock:
            root = self.root(provider)
            instruction = root / PROVIDERS[provider][3]
            old = self.state["installed"].get(provider)
            original = read_file(instruction)
            parts = split_block(original or b"")
            if parts and not old:
                raise LocalError("发现不属于当前安装记录的管理段；请检查后再安装")
            if parts and old and sha(parts[1]) != old["block_hash"]:
                raise LocalError("本地技能管理段被外部修改，已保留；请手动合并或恢复备份")
            if old and not parts:
                raise LocalError("原管理段已被外部删除，已保留安装记录；请先撤销")
            block = self.block(provider, profile)
            prefix = b"" if not original or original.endswith(b"\n") else b"\n"
            if parts:
                new_instruction = parts[0] + block + parts[2]
            else:
                new_instruction = (original or b"") + prefix + block
            files = self.deployment_files(profile)
            skill_root = root / "skills"
            desired = {skill_root / rel: data for rel, data in files.items()}
            updates = {instruction: new_instruction}
            previous = {}
            old_files = self.installed_files(old) if old else {}
            for path in sorted(set(desired) | set(old_files)):
                current = read_file(path)
                record = old_files.get(path)
                if record:
                    if current is None or sha(current) != record["hash"]:
                        raise LocalError(f"技能文件被外部修改或删除，未覆盖：{path}")
                elif current is not None:
                    raise LocalError(f"同名技能文件已经存在，未覆盖：{path}")
                updates[path] = desired.get(path)
                previous[path] = current
            previous[instruction] = original
            # Prepare only our bundled executable. Imported skill scripts are never executed.
            try:
                adapter = McpConfig(provider, root, self.home)
                mcp_original = read_file(adapter.path)
                adapter.parse(mcp_original)
                runtime = self.rea.ensure()
                mcp_value, mcp_record = adapter.prepare(mcp_original, runtime, (old or {}).get("rea", {}).get("config"), sha)
                probe = self.rea.probe(runtime)
                block = self.block(provider, profile, runtime)
                updates[instruction] = parts[0] + block + parts[2] if parts else (original or b"") + prefix + block
                updates[adapter.path] = mcp_value
                previous[adapter.path] = mcp_original
            except ReaError as exc:
                self.rea.update(str(exc), 0, "failed")
                raise LocalError(str(exc)) from exc
            # Runtime preparation can take seconds; do not overwrite edits made in that interval.
            for path, expected in previous.items():
                if read_file(path) != expected:
                    self.rea.update("配置在准备期间发生变化，未覆盖", 0, "failed")
                    raise LocalError(f"文件在 REA 准备期间被修改，请刷新后重试：{path}")
            backup = self.data_dir / "backups" / (time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
            backup.mkdir(parents=True)
            atomic_write(backup / "snapshot.json", json.dumps({str(p): None if d is None else base64.b64encode(d).decode()
                         for p, d in previous.items()}, ensure_ascii=False, indent=2).encode("utf-8"))
            done = []
            try:
                for path, value in updates.items():
                    if value is None:
                        path.unlink()
                    else:
                        atomic_write(path, value)
                    done.append(path)
                record = {"root": str(root), "profile": profile, "instruction": str(instruction),
                          "block_hash": sha(block), "prefix": (old or {}).get("prefix", prefix.decode()),
                          "original_instruction_existed": (old or {}).get("original_instruction_existed", original is not None),
                          "backup": str(backup), "updated_at": time.time(),
                          "files_root": str(skill_root),
                          "rea": {"runtime": runtime, "probe": probe, "config": mcp_record},
                          "files": {rel: {"hash": sha(data)} for rel, data in files.items()}}
                self.state["installed"][provider] = record
                self.event("inject", provider, profile)
            except Exception:
                self.rea.update("写入未完成，正在恢复原配置", 0, "failed")
                for path in reversed(done):
                    data = previous[path]
                    if data is None:
                        if path.exists():
                            path.unlink()
                    else:
                        atomic_write(path, data)
                if old:
                    self.state["installed"][provider] = old
                else:
                    self.state["installed"].pop(provider, None)
                raise
            return {"provider": provider, "profile": profile, "backup": str(backup), "verification": self.verify(provider)}

    def recoverable_rea(self, provider):
        if self.state['installed'].get(provider):
            return None
        adapter = McpConfig(provider, self.root(provider), self.home)
        data = read_file(adapter.path)
        entry = adapter.entry(adapter.parse(data))
        if not entry:
            return None
        launch = entry.get('config', {}) if provider == 'deepseek' else entry
        runtime = self.rea.owned_runtime(launch)
        if runtime is None or entry != adapter.make_entry(runtime):
            return None
        return adapter, data, runtime

    def repair_rea(self, provider, profile='builtin'):
        """Recover an intact managed installation or replace a verified orphan entry."""
        with self.lock:
            if self.state['installed'].get(provider):
                return self.inject(provider, profile)
            recovery = self.recoverable_rea(provider)
            if recovery is None:
                raise LocalError('无法确认这是本软件遗留的 REA 连接，已保留原配置；请导出诊断')
            adapter, original, runtime = recovery
            root = self.root(provider)
            instruction = root / PROVIDERS[provider][3]
            instruction_data = read_file(instruction)
            parts = split_block(instruction_data or b'')
            baseline = adapter.parse(original)
            adapter.set_entry(baseline, None)
            baseline_data = adapter.dump(baseline) if baseline else None
            if parts:
                matched = next((item['id'] for item in self.profiles()
                                if self.block(provider, item['id'], runtime) == parts[1]), None)
                if matched is None:
                    raise LocalError('遗留指令已被修改，未覆盖；请导出诊断')
                files = self.deployment_files(matched)
                for rel, expected in files.items():
                    if read_file(root / 'skills' / rel) != expected:
                        raise LocalError('遗留技能被修改或缺失，未覆盖；请导出诊断')
            else:
                matched, files = None, {}
            backup = self.data_dir / 'backups' / ('recovery-' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
            backup.mkdir(parents=True)
            snapshot = {str(adapter.path):base64.b64encode(original).decode(),
                        str(instruction):None if instruction_data is None else base64.b64encode(instruction_data).decode()}
            snapshot.update({str(root / 'skills' / rel):base64.b64encode(data).decode() for rel,data in files.items()})
            atomic_write(backup / 'snapshot.json', json.dumps(snapshot, ensure_ascii=False, indent=2).encode('utf-8'))
            if read_file(adapter.path) != original or read_file(instruction) != instruction_data:
                raise LocalError('恢复期间配置被修改，未覆盖；请刷新后重试')
            if matched:
                self.state['installed'][provider] = {
                    'root':str(root), 'profile':matched, 'instruction':str(instruction),
                    'block_hash':sha(parts[1]), 'prefix':'', 'original_instruction_existed':bool(parts[0] or parts[2]),
                    'backup':str(backup), 'updated_at':time.time(), 'files_root':str(root / 'skills'),
                    'files':{rel:{'hash':sha(data)} for rel,data in files.items()},
                    'rea':{'runtime':runtime, 'probe':{'ok':True, 'recovered':True, 'client_connected':False},
                           'config':{'path':str(adapter.path), 'installed_entry':adapter.make_entry(runtime),
                                     'hash':sha(original), 'original':None if baseline_data is None else base64.b64encode(baseline_data).decode()}}}
                self.event('recover', provider, 'installation record recovered from verified files')
                return self.inject(provider, profile)
            # No managed skill block remains: back up and replace only the verified row.
            try:
                if baseline_data is None:
                    adapter.path.unlink()
                else:
                    atomic_write(adapter.path, baseline_data)
                return self.inject(provider, profile)
            except Exception:
                atomic_write(adapter.path, original)
                raise

    def verify(self, provider: str, live: bool = False) -> dict:
        with self.lock:
            root = self.root(provider)
            record = self.state["installed"].get(provider)
            if not record:
                return {"ok": False, "installed": False, "checks": [], "summary": "尚未写入本地技能"}
            checks = []
            try:
                instruction = Path(record["instruction"])
                parts = split_block(read_file(instruction) or b"")
                valid = bool(parts and sha(parts[1]) == record["block_hash"])
                checks.append({"name": "指令管理段", "ok": valid, "path": str(instruction)})
                for path, expected in self.installed_files(record).items():
                    data = read_file(path)
                    checks.append({"name": path.name, "ok": data is not None and sha(data) == expected["hash"], "path": str(path)})
                rea = record.get("rea")
                if rea:
                    adapter = McpConfig(provider, Path(record["root"]), self.home)
                    checks.append({"name": "REA 自动连接配置", "ok": adapter.check(read_file(adapter.path), rea["config"]), "path": str(adapter.path)})
                    current = self.rea.is_current(rea["runtime"])
                    checks.append({"name": "REA 运行包版本", "ok": current, "detail": "已安装当前运行包" if current else "运行包需要升级，请点击更新 REA"})
                    ready = current and self.rea.ready(rea["runtime"])
                    checks.append({"name": "REA 内置运行环境", "ok": ready, "path": rea["runtime"]["root"]})
                    if live and ready:
                        try:
                            probe = self.rea.probe(rea["runtime"])
                            checks.append({"name": "REA CLI/MCP 启动测试", "ok": probe["ok"], "detail": f"REA {probe['version']}，{probe['tool_count']} 个工具；客户端连接待确认"})
                        except ReaError as exc:
                            checks.append({"name": "REA CLI/MCP 启动测试", "ok": False, "detail": str(exc)})
            except (LocalError, OSError) as exc:
                checks.append({"name": "文件读取", "ok": False, "detail": str(exc)})
            ok = all(c["ok"] for c in checks)
            return {"ok": ok, "installed": True, "checks": checks,
                    "summary": ("本地文件完整；REA 已就绪，重启客户端后自动连接" if record.get("rea") else "本地文件完整；请重新开启技能以配置 REA") if ok else ("REA 运行包需要升级，请点击更新 REA" if record.get("rea") and not self.rea.is_current(record['rea']['runtime']) else "检测到文件变更，请检查后恢复"),
                    "rea": record.get("rea", {}).get("probe"),
                    "model_read_confirmed": False}

    def revoke(self, provider: str) -> dict:
        with self.lock:
            self.root(provider)
            record = self.state["installed"].get(provider)
            if not record:
                return {"provider": provider, "removed": True, "conflicts": []}
            conflicts = []
            rea = record.get("rea")
            if rea:
                adapter = McpConfig(provider, Path(record["root"]), self.home)
                try:
                    restored_mcp = adapter.restore(read_file(adapter.path), rea["config"], sha)
                    if restored_mcp is None:
                        if adapter.path.exists():
                            adapter.path.unlink()
                    else:
                        atomic_write(adapter.path, restored_mcp)
                except (ReaError, LocalError, OSError):
                    conflicts.append(str(adapter.path))
            instruction = Path(record["instruction"])
            data = read_file(instruction)
            parts = split_block(data or b"")
            if parts and sha(parts[1]) != record["block_hash"]:
                conflicts.append(str(instruction))
            if not conflicts and parts:
                left = parts[0]
                prefix = record.get("prefix", "").encode()
                if prefix and left.endswith(prefix):
                    left = left[:-len(prefix)]
                restored = left + parts[2]
                if not restored and not record["original_instruction_existed"]:
                    instruction.unlink()
                else:
                    atomic_write(instruction, restored)
            remaining = {}
            for rel, expected in record["files"].items():
                base = Path(record.get("files_root", str(Path(record["root"]) / "skills" / "pojia-local")))
                path = base / rel
                current = read_file(path)
                if current is not None and sha(current) != expected["hash"]:
                    conflicts.append(str(path))
                    remaining[rel] = expected
                elif current is not None:
                    path.unlink()
            if conflicts:
                record["files"] = remaining
                # Preserve the original block identity if the instruction conflicted.
                self.state["installed"][provider] = record
            else:
                self.state["installed"].pop(provider, None)
            self.event("revoke", provider, "conflicts" if conflicts else "ok")
            return {"provider": provider, "removed": not conflicts, "conflicts": conflicts}

    def status(self) -> dict:
        with self.lock:
            items = []
            for key, spec in PROVIDERS.items():
                root = self.root(key)
                record = self.state["installed"].get(key)
                verification = self.verify(key)
                try:
                    recoverable = not record and self.recoverable_rea(key) is not None
                except (ReaError, LocalError, OSError):
                    recoverable = False
                items.append({"key": key, "name": spec[0], "icon": spec[4], "path": str(root),
                              "instruction": spec[3], "exists": root.is_dir(), "installed": bool(record),
                              "profile": self.normalize_profile((record or {}).get("profile", "builtin" if self.builtin_catalog else "extended" if self.catalog else "basic")), "verification": verification,
                              "rea": (record or {}).get("rea", {}).get("probe"),
                              "rea_needs_update": bool(record and record.get('rea') and not self.rea.is_current(record['rea']['runtime'])),
                              "rea_recovery_available": bool(recoverable),
                              "adapter": "客户端的实际读取需要新会话验收"})
            return {"version": VERSION, "mode": "local", "network": "disabled", "providers": items,
                    "profiles": self.profiles(), "data_dir": str(self.data_dir),
                    "builtin_documents": len(self.builtin_catalog),
                    "rea_runtime": self.rea.summary(),
                    "events": list(reversed(self.state["events"][-12:]))}

    def diagnostics(self) -> dict:
        return {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "version": VERSION,
                "network": "disabled", "state": self.status(),
                "limitations": ["只校验文件，不证明模型已读取技能",
                                f"包含 {len(self.builtin_catalog)} 项内置技能和 {len(self.catalog)} 项扩展技能；工具、脚本与附件需按本机环境核对",
                                "客户端实际读取需要在新会话中确认"]}

    def dispatch(self, command: str, args: dict | None = None) -> dict:
        args = args or {}
        if command == "rea_progress":
            return {"ok": True, "data": self.rea.progress_status()}
        with self.lock:
            try:
                if command == "status":
                    data = self.status()
                elif command == "inject":
                    data = self.inject(args["provider"], args.get("profile", "basic"))
                elif command == "repair_rea":
                    data = self.repair_rea(args['provider'], args.get('profile', 'builtin'))
                elif command == "revoke":
                    data = self.revoke(args["provider"])
                elif command == "verify":
                    data = self.verify(args["provider"], live=True)
                elif command == "set_path":
                    data = self.set_path(args["provider"], args.get("path", ""))
                elif command == "read_profile":
                    data = self.read_profile(args["profile"])
                elif command == "import_skill":
                    data = self.import_skill(args["path"])
                elif command == "diagnostics":
                    data = self.diagnostics()
                else:
                    raise LocalError("未知操作")
                return {"ok": True, "data": data}
            except (LocalError, OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
                return {"ok": False, "error": str(exc)}
