"""Build a relocatable, offline Windows x64 REA runtime from a pinned installation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def build(node_dir, cli_dir):
    package = cli_dir / "node_modules/rea-agents"
    version = json.loads((package / "package.json").read_text("utf-8"))["version"]
    node_version = subprocess.check_output([str(node_dir / "node.exe"), "--version"], text=True).strip()
    target = ROOT / "runtime"
    target.mkdir(exist_ok=True)
    archive = target / "rea-windows-x64.zip"
    files = {}
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for prefix, folder in (("node", node_dir), ("cli", cli_dir)):
            for path in sorted(folder.rglob("*")):
                if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                    raise ValueError(f"Linked package member: {path}")
                if not path.is_file():
                    continue
                relative = prefix + "/" + path.relative_to(folder).as_posix()
                data = path.read_bytes()
                files[relative] = hashlib.sha256(data).hexdigest()
                output.writestr(relative, data)
        output.writestr("files.json", json.dumps(files, sort_keys=True).encode("utf-8"))
    critical = ["node/node.exe", "cli/node_modules/rea-agents/scripts/rea.mjs", "cli/node_modules/rea-agents/package.json"]
    manifest = {"schema": 1, "rea_version": version, "node_version": node_version,
                "platform": "win32-x64", "archive": archive.name,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "file_count": len(files), "unpacked_bytes": sum(p.stat().st_size for d in (node_dir, cli_dir) for p in d.rglob("*") if p.is_file()),
                "critical_files": {key: files[key] for key in critical},
                "origins": ["https://nodejs.org", "https://registry.npmjs.org/rea-agents"],
                "license_paths": ["node/LICENSE", "cli/node_modules/rea-agents/LICENSE"]}
    for rel in manifest["license_paths"]:
        if rel not in files:
            raise ValueError(f"Missing redistribution license: {rel}")
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    import shutil
    skill_dest = ROOT / "skills/builtin/library/reverse-engineer-anything"
    shutil.copytree(package / "skills/reverse-engineer-anything", skill_dest, dirs_exist_ok=True)
    print(json.dumps({"archive": str(archive), "archive_bytes": archive.stat().st_size, **manifest}, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-dir", type=Path, required=True)
    parser.add_argument("--cli-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.node_dir, args.cli_dir)
