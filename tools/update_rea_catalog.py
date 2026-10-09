"""Register the package-matched REA skill in the built-in collection."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = ROOT / "skills/builtin-catalog.json"
data = json.loads(catalog.read_text("utf-8"))
data["items"] = [item for item in data["items"] if item["skill_name"] != "reverse-engineer-anything"]
skill = ROOT / "skills/builtin/library/reverse-engineer-anything/SKILL.md"
data["items"].append({"id": "builtin-reverse-engineer-anything", "skill_name": "reverse-engineer-anything",
    "name": "REA 自动分析工具", "description": "统一分析应用、二进制和资源；开启技能时自动准备环境与连接",
    "category": "逆向", "kind": "module", "dependencies": [],
    "keywords": ["rea", "使用技能", "Electron", "JavaScript", "ASAR", "反编译", "版本对比"],
    "builtin": True, "collection": "builtin", "content_sha256": hashlib.sha256(skill.read_bytes()).hexdigest()})
catalog.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
index_path = ROOT / "skills/builtin/SKILL.md"
index = index_path.read_text("utf-8").replace("本库包含 53 项技能", "本库包含 54 项技能")
if "../reverse-engineer-anything/SKILL.md" not in index:
    index += "\n| `reverse-engineer-anything` | REA 应用与二进制统一分析 | [读取](../reverse-engineer-anything/SKILL.md) |\n"
index_path.write_text(index, encoding="utf-8")
for relative in ("version_info.txt", "frontend/index.html", "README.md", "docs/USAGE.md"):
    path = ROOT / relative
    text = path.read_text("utf-8").replace("1.3.2", "1.4.0").replace("53 项", "54 项")
    text = text.replace("(1, 3, 2, 0)", "(1, 4, 0, 0)")
    text = text.replace("**首次公开发布 · AI 开发 · 程序版本", "**AI 开发 · 程序版本")
    text = text.replace("ai技能库首次公开发布，程序版本", "ai技能库程序版本")
    path.write_text(text, encoding="utf-8")
print("Registered 54 built-in skills; release metadata is 1.4.0")
