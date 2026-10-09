"""Scoped MCP registration; preserve all unrelated settings and later user edits."""
from __future__ import annotations

import base64
from collections.abc import Mapping
import io
import json
from pathlib import Path

import tomlkit
from ruamel.yaml import YAML

SERVER_NAME = "ai_skill_library_rea"


class ReaError(ValueError):
    pass


class McpConfig:
    def __init__(self, provider: str, root: Path, home: Path):
        self.provider = provider
        if provider == "codex":
            self.path, self.format, self.keys = root / "config.toml", "toml", ["mcp_servers"]
        elif provider == "claude":
            self.path = home / ".claude.json" if root == home / ".claude" else root / ".claude.json"
            self.format, self.keys = "json", ["mcpServers"]
        elif provider == "deepseek":
            self.path, self.format, self.keys = root / "cordis.patch.yml", "patch", []
        elif provider == "hermes":
            self.path, self.format, self.keys = root / "config.yaml", "yaml", ["mcp_servers"]
        elif provider == "zcode":
            self.path, self.format, self.keys = root / "cli/config.json", "json", ["mcp", "servers"]
        elif provider in ("workbuddy", "workbuddy_ai"):
            self.path, self.format, self.keys = root / "mcp.json", "json", ["mcpServers"]
        else:
            raise ReaError("此客户端尚无 REA 连接适配")

    def parse(self, data: bytes | None):
        text = (data or b"").decode("utf-8-sig")
        try:
            if self.format == "toml":
                result = tomlkit.parse(text)
            elif self.format == "json":
                result = json.loads(text) if text.strip() else {}
            else:
                yaml = YAML()
                yaml.preserve_quotes = True
                result = yaml.load(text)
                if result is None:
                    result = [] if self.format == "patch" else {}
            expected = list if self.format == "patch" else Mapping
            if not isinstance(result, expected):
                # TOMLDocument and ruamel maps implement dict.
                raise ValueError("配置根结构不正确")
            if self.provider == "zcode" and result.get("features", {}).get("mcp") is False:
                raise ReaError("ZCode 设置中已关闭 MCP；已保留该设置，请先在 ZCode 开启 MCP")
            return result
        except ReaError:
            raise
        except Exception as exc:
            raise ReaError(f"客户端配置格式异常，未修改原文件：{self.path}") from exc

    def dump(self, document) -> bytes:
        if self.format == "toml":
            return tomlkit.dumps(document).encode("utf-8")
        if self.format == "json":
            return (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 4096
        output = io.StringIO()
        yaml.dump(document, output)
        return output.getvalue().encode("utf-8")

    def servers(self, document, create=False):
        current = document
        for key in self.keys:
            if key not in current:
                if not create:
                    return {}
                current[key] = tomlkit.table() if self.format == "toml" else {}
            current = current[key]
            if not isinstance(current, Mapping):
                raise ReaError(f"MCP 设置不是映射，未覆盖：{self.path}")
        return current

    @staticmethod
    def patch_rows(document):
        for patch in document:
            if not isinstance(patch, dict):
                raise ReaError("DeepSeek patch 项目格式异常，未覆盖")
            for row in patch.get("insert", []):
                if not isinstance(row, dict):
                    raise ReaError("DeepSeek insert 配置格式异常")
                yield patch, row

    def entry(self, document):
        if self.format != "patch":
            return self.servers(document).get(SERVER_NAME)
        rows = [row for _, row in self.patch_rows(document)
                if row.get("id") == SERVER_NAME or row.get("config", {}).get("serverName") == SERVER_NAME]
        if len(rows) > 1:
            raise ReaError("DeepSeek 已存在重复的 REA 配置，未覆盖")
        return rows[0] if rows else None

    def set_entry(self, document, entry):
        if self.format != "patch":
            servers = self.servers(document, create=entry is not None)
            if entry is None:
                servers.pop(SERVER_NAME, None)
            else:
                servers[SERVER_NAME] = entry
            return
        for patch, row in list(self.patch_rows(document)):
            if row.get("id") == SERVER_NAME or row.get("config", {}).get("serverName") == SERVER_NAME:
                patch["insert"].remove(row)
                if not patch["insert"] and set(patch) == {"insert"}:
                    document.remove(patch)
        if entry is not None:
            document.append({"insert": [entry]})

    def make_entry(self, runtime: dict):
        entry = {"command": runtime["node"], "args": [runtime["entry"], "mcp"]}
        if self.provider == "codex":
            entry.update(startup_timeout_sec=60, tool_timeout_sec=360)
        elif self.provider == "hermes":
            entry.update(enabled=True, connect_timeout=60, timeout=360)
        elif self.provider == "zcode":
            entry.update(type="stdio", enabled=True, timeoutMs=360000)
        elif self.provider == "deepseek":
            entry = {"id": SERVER_NAME, "name": "@deepseek-ai/dsh-mcp-client", "config": {
                "serverName": SERVER_NAME, "transport": "stdio", **entry,
                "env": {}, "cwd": str(self.path.parent), "toolCallTimeoutMs": 360000,
                "failOnStartupError": False}}
        return entry

    def prepare(self, original: bytes | None, runtime: dict, old: dict | None, digest):
        document = self.parse(original)
        current = self.entry(document)
        if old:
            if str(self.path) != old["path"] or current != old["installed_entry"]:
                raise ReaError(f"REA 配置被外部修改或删除，已保留：{self.path}")
        elif current is not None:
            raise ReaError(f"同名 REA 配置已存在，未覆盖：{self.path}")
        baseline = (old or {}).get("original", None if original is None else base64.b64encode(original).decode())
        entry = self.make_entry(runtime)
        self.set_entry(document, entry)
        data = self.dump(document)
        if self.entry(self.parse(data)) != entry:
            raise ReaError("REA 配置写入前校验失败")
        return data, {"path": str(self.path), "installed_entry": entry, "hash": digest(data), "original": baseline}

    def check(self, data, record) -> bool:
        try:
            return self.entry(self.parse(data)) == record["installed_entry"]
        except (ReaError, ValueError):
            return False

    def restore(self, data: bytes | None, record: dict, digest):
        original = None if record["original"] is None else base64.b64decode(record["original"])
        if data is None:
            return None
        if digest(data) == record["hash"]:
            return original
        document = self.parse(data)
        current = self.entry(document)
        if current is not None and current != record["installed_entry"]:
            raise ReaError(f"REA 配置被外部修改，已保留：{self.path}")
        if current is None:
            return data
        self.set_entry(document, None)
        # Remove empty containers only if they did not exist before installation.
        if self.format != "patch":
            baseline = self.parse(original)
            for depth in range(len(self.keys), 0, -1):
                parent, prior = document, baseline
                for key in self.keys[:depth - 1]:
                    parent = parent.get(key, {})
                    prior = prior.get(key, {})
                key = self.keys[depth - 1]
                if not parent.get(key) and key not in prior:
                    parent.pop(key, None)
        return self.dump(document)
