"""Exercise the real local UI and filesystem in an isolated home, then restore it."""
import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

sys.stdout.reconfigure(encoding="utf-8")
CASE = Path(__file__).resolve().parent
SOURCE = CASE.parents[1] / "local-rewrite"
if not SOURCE.is_dir():
    SOURCE = CASE.parent
parser = argparse.ArgumentParser()
parser.add_argument("--exe", type=Path)
parser.add_argument("--reuse-sandbox", type=Path)
args = parser.parse_args()
label = "exe-ui" if args.exe else "source-ui"
OUT = CASE / label
OUT.mkdir(exist_ok=True)
run = args.reuse_sandbox or Path(tempfile.mkdtemp(prefix="run-", dir=OUT))
if not run.resolve().is_relative_to(OUT.resolve()):
    raise SystemExit("Sandbox must be within this verification output directory")
ready = run / "ready.json"
ready.unlink(missing_ok=True)
home, data = run / "home", run / "data"
instruction = home / ".codex/AGENTS.md"
instruction.parent.mkdir(parents=True, exist_ok=True)
original_instruction = b"# User instructions\r\nKeep this content.\r\n"
instruction.write_bytes(original_instruction)
config = home / ".codex/config.toml"
original_config = b'model = "preserve-model"\n[mcp_servers.existing]\ncommand = "preserve-tool"\n'
config.write_bytes(original_config)
unrelated = home / ".codex/skills/user-skill/SKILL.md"
unrelated.parent.mkdir(parents=True, exist_ok=True)
unrelated.write_bytes(b"Preserve unrelated skill\n")
catalogs = {name: json.loads((SOURCE / "skills" / (name + "-catalog.json")).read_text("utf-8")) for name in ["builtin", "premium"]}
expected = {name: {row["skill_name"] for row in value["items"]} for name, value in catalogs.items()}
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = 0
command = [str(args.exe)] if args.exe else [sys.executable, str(SOURCE / "main.py")]
command += ["--serve", "--sandbox", "--home", str(home), "--data-dir", str(data), "--ready-file", str(ready)]
log = (run / "process.log").open("w", encoding="utf-8")
process = subprocess.Popen(command, stdout=log, stderr=log, startupinfo=startupinfo, cwd=SOURCE)
version = next(node.value.value for node in ast.parse((SOURCE / "backend.py").read_text("utf-8")).body
               if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets))
result = {"pass": False, "platform": "Windows / Edge", "version": version, "target": str(args.exe or SOURCE / "main.py"), "sandbox": str(run)}
errors, external = [], []
expect.set_options(timeout=360000)

def state():
    return json.loads((data / "state.json").read_text("utf-8"))

def deployed():
    return {path.parent.name for path in (home / ".codex/skills").glob("*/SKILL.md")} - {"user-skill"}

def assert_edition_files(edition):
    assert deployed() == expected[edition] | {"pojia-local", "reverse-engineer-anything"}
    for item in catalogs[edition]["items"]:
        actual = home / ".codex/skills" / item["skill_name"] / "SKILL.md"
        assert hashlib.sha256(actual.read_bytes()).hexdigest() == item["content_sha256"], item["skill_name"]

try:
    for _ in range(900):
        if ready.exists():
            break
        if process.poll() is not None:
            raise RuntimeError("Application exited before ready")
        time.sleep(0.1)
    url = json.loads(ready.read_text("utf-8"))["url"]
    with sync_playwright() as automation:
        browser = automation.chromium.launch(executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True, args=["--disable-background-networking", "--no-first-run"])
        context = browser.new_context(viewport={"width": 1200, "height": 1000})
        context.route("**/*", lambda route: route.continue_() if route.request.url.startswith(url + "/") else (external.append(route.request.url), route.abort()))
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url)
        expect(page.locator("#startup")).to_be_hidden()
        if args.reuse_sandbox:
            assert not state()["installed"], "A partially installed sandbox requires review before reuse"
            for key in ["codex", "claude", "deepseek", "hermes", "zcode", "workbuddy", "workbuddy_ai"]:
                switch = page.locator(f"#service-card-{key} .edition-switch")
                if switch.get_attribute("aria-checked") == "true":
                    switch.click()
                    expect(switch).to_have_attribute("aria-checked", "false")
                    expect(switch).to_be_enabled()
        assert page.locator(".edition-switch").count() == 7
        assert page.locator(".edition-switch[aria-checked='false']").count() == 7
        expect(page.locator("#library-banner-summary")).to_contain_text("原版 49 项")
        expect(page.locator("#library-banner-summary")).to_contain_text("精品 161 项")
        page.screenshot(path=str(OUT / "original-default.png"), full_page=True)
        for key in ["codex", "claude", "deepseek", "hermes", "zcode", "workbuddy", "workbuddy_ai"]:
            page.locator(f"#service-card-{key} .edition-switch").click()
            expect(page.locator(f"#service-card-{key} .edition-switch")).to_have_attribute("aria-checked", "true")
            expect(page.locator(f"#service-card-{key} .edition-switch")).to_be_enabled()
        assert not state()["installed"]
        assert all(value == "premium" for value in state()["selected_profiles"].values())
        assert not (home / ".claude").exists()
        page.reload()
        expect(page.locator("#startup")).to_be_hidden()
        assert page.locator(".edition-switch[aria-checked='true']").count() == 7
        for key in ["claude", "deepseek", "hermes", "zcode", "workbuddy", "workbuddy_ai"]:
            page.locator(f"#service-card-{key} .edition-switch").click()
            expect(page.locator(f"#service-card-{key} .edition-switch")).to_have_attribute("aria-checked", "false")
            expect(page.locator(f"#service-card-{key} .edition-switch")).to_be_enabled()
        codex = page.locator("#service-card-codex")
        edition = codex.locator(".edition-switch")
        enabled = codex.locator('[data-action="toggle"]')
        enabled.click()
        expect(enabled).to_have_attribute("aria-checked", "true")
        expect(edition).to_be_enabled()
        assert state()["installed"]["codex"]["profile"] == "premium"
        assert_edition_files("premium")
        page.locator("#theme").click()
        page.screenshot(path=str(OUT / "premium-enabled.png"), full_page=True)
        edition.click()
        expect(edition).to_have_attribute("aria-checked", "false")
        expect(edition).to_be_enabled()
        assert state()["installed"]["codex"]["profile"] == "builtin"
        assert_edition_files("builtin")
        edition.click()
        expect(edition).to_have_attribute("aria-checked", "true")
        expect(edition).to_be_enabled()
        assert_edition_files("premium")
        assert len(list((data / "backups").glob("*/snapshot.json"))) >= 3
        edited = home / ".codex/skills/l-reverse/SKILL.md"
        correct = edited.read_bytes()
        edited.write_bytes(b"User edit; do not overwrite.\n")
        before_instruction = instruction.read_bytes()
        edition.click()
        expect(page.locator("#toast")).to_contain_text("外部修改")
        expect(edition).to_be_enabled()
        expect(edition).to_have_attribute("aria-checked", "true")
        assert state()["installed"]["codex"]["profile"] == "premium"
        assert state()["selected_profiles"]["codex"] == "premium"
        assert edited.read_bytes() == b"User edit; do not overwrite.\n"
        assert instruction.read_bytes() == before_instruction
        edited.write_bytes(correct)
        page.locator('[data-page="skills"]').click()
        expect(page.locator(".library-card")).to_have_count(50)
        page.locator("#skill-collection").select_option("premium-suite")
        expect(page.locator(".library-card")).to_have_count(162)
        assert page.locator('.library-card button[disabled]').count() == len(catalogs['premium']['missing_ids'])
        codes = page.locator(".library-card code").all_text_contents()
        assert len(codes) == len(set(codes)) == 161
        page.screenshot(path=str(OUT / "premium-library.png"), full_page=True)
        page.locator('[data-page="console"]').click()
        context.set_default_timeout(120000)
        page.set_viewport_size({"width": 900, "height": 640})
        page.screenshot(path=str(OUT / "console-900.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.set_viewport_size({"width": 1200, "height": 1000})
        enabled.click()
        page.locator("#confirm-revoke").click()
        expect(enabled).to_have_attribute("aria-checked", "false")
        expect(edition).to_be_enabled()
        assert not state()["installed"]
        assert state()["selected_profiles"]["codex"] == "premium"
        assert instruction.read_bytes() == original_instruction
        assert config.read_bytes() == original_config
        assert unrelated.read_bytes() == b"Preserve unrelated skill\n"
        assert deployed() == set()
        page.reload()
        expect(page.locator("#startup")).to_be_hidden()
        expect(edition).to_have_attribute("aria-checked", "true")
        expect(enabled).to_have_attribute("aria-checked", "false")
        assert not errors, errors
        assert not external, external
        result.update({"pass": True, "seven_independent_choices": True, "choice_survives_reload_and_revoke": True,
            "original_catalog_documents": 49, "premium_expected_documents": 161, "premium_available_documents": len(catalogs['premium']['items']),
            "premium_missing_documents": len(catalogs['premium']['missing_ids']), "independent_content_hashes": True, "conflict_rolls_back_choice": True,
            "backup_switch_revoke": True, "user_configuration_restored": True, "responsive_layout": True,
            "browser_errors": errors, "external_requests": external, "real_clients_modified": False})
        browser.close()
except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"
    raise
finally:
    (OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), "utf-8")
    if process.poll() is None:
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.wait(timeout=30)
    log.close()
print(json.dumps(result, ensure_ascii=False), flush=True)
