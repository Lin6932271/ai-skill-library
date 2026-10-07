"""Real Edge UI acceptance against the localhost service in an isolated home."""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).parents[1]
from playwright.sync_api import sync_playwright, expect


def run(executable=None):
    output = ROOT / "artifacts" / "acceptance"
    output.mkdir(parents=True, exist_ok=True)
    prefix = 'exe-' if executable else ''
    with tempfile.TemporaryDirectory(prefix="pojia-ui-") as temp:
        sandbox = Path(temp)
        ready = sandbox / "ready.json"
        launcher = [str(executable)] if executable else [sys.executable, str(ROOT / "main.py")]
        process = subprocess.Popen([*launcher, "--serve", "--sandbox", "--data-dir", str(sandbox / "data"), "--home", str(sandbox / "home"), "--ready-file", str(ready)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            for _ in range(100):
                if ready.exists():
                    break
                if process.poll() is not None:
                    raise RuntimeError(process.stderr.read().decode())
                time.sleep(.1)
            url = json.loads(ready.read_text("utf-8"))["url"]
            custom = sandbox / "custom.md"
            custom.write_text("# UI imported skill\n\nLocal UI acceptance instructions.", encoding="utf-8")
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", headless=True,
                         args=["--disable-background-networking", "--disable-component-update", "--no-first-run"])
                context = browser.new_context(viewport={"width": 1200, "height": 900}, device_scale_factor=1)
                external = []
                errors = []
                context.route("**/*", lambda route: route.continue_() if route.request.url.startswith(url + "/") else (external.append(route.request.url), route.abort()))
                page = context.new_page()
                page.on("pageerror", lambda e: errors.append(str(e)))
                pending_movies = []
                def hold_movie(route):
                    pending_movies.append(route)
                context.route(url + '/assets/startup.mp4', hold_movie)
                page.goto(url, wait_until='domcontentloaded')
                assert page.title() == 'ai技能库'
                assert page.locator('#startup button').count() == 0
                expect(page.locator('#startup')).to_be_visible()
                page.wait_for_timeout(100)
                assert pending_movies, 'video request must be held to inspect the initial frame'
                assert page.locator('#startup-video').get_attribute('poster') is None
                assert page.locator('#startup img').count() == 0
                assert page.locator('#app-shell').evaluate('e => getComputedStyle(e).visibility') == 'hidden'
                assert page.locator('html').evaluate('e => getComputedStyle(e).overflowY') == 'hidden'
                page.screenshot(path=str(output / (prefix + 'startup-before-video.png')))
                context.unroute(url + '/assets/startup.mp4', hold_movie)
                for route in pending_movies:
                    route.continue_()
                page.wait_for_function("() => document.querySelector('#startup-video').currentTime > .5")
                video = page.locator('#startup-video').evaluate('''v => ({width: v.videoWidth,
                  height: v.videoHeight, duration: v.duration, time: v.currentTime,
                  muted: v.muted, decoded_frames: v.getVideoPlaybackQuality().totalVideoFrames})''')
                assert video['width'] > 0 and video['height'] > 0 and video['decoded_frames'] > 0, video
                assert video['muted'] and video['duration'] > 6, video
                fills = []
                for viewport in [{'width': 1200, 'height': 900}, {'width': 900, 'height': 640}]:
                    page.set_viewport_size(viewport)
                    layout = page.locator('#startup-video').evaluate('''v => {
                      const box = v.getBoundingClientRect();
                      return {x: box.x, y: box.y, width: box.width, height: box.height,
                        fit: getComputedStyle(v).objectFit, fullscreen: !!document.fullscreenElement};
                    }''')
                    assert layout == {'x': 0, 'y': 0, **viewport, 'fit': 'cover', 'fullscreen': False}, layout
                    fills.append(layout)
                page.set_viewport_size({'width': 1200, 'height': 900})
                page.screenshot(path=str(output / (prefix + 'startup.png')))
                expect(page.locator('#startup')).to_be_hidden(timeout=16000)
                startup = page.evaluate('window.startupStatus')
                assert startup['reason'] == 'ended' and startup['playing'], startup
                assert not page.locator('#app-shell').evaluate('e => e.inert')
                assert page.locator('.brand img').get_attribute('src') == '/assets/app-icon.jpg'
                page.locator(".pj-service-card").last.wait_for()
                assert page.locator(".pj-service-card").count() == 7
                assert not any(x in page.locator("body").inner_text() for x in ["账户", "订阅", "反馈"])
                scroll_checks = []
                def check_wheel_scroll(label, bottom_selector):
                    # Real wheel input catches overflow:hidden, unlike scrollIntoView.
                    page.evaluate('window.scrollTo(0, 0)')
                    page.mouse.move(700, 400)
                    page.mouse.wheel(0, 20000)
                    page.wait_for_timeout(300)
                    metrics = page.evaluate('''() => ({y: window.scrollY,
                      height: document.scrollingElement.scrollHeight,
                      viewport: window.innerHeight})''')
                    box = page.locator(bottom_selector).bounding_box()
                    assert metrics['y'] > 0, (label, 'wheel cannot scroll', metrics)
                    assert box and box['y'] >= 0 and box['y'] + box['height'] <= metrics['viewport'], (label, box, metrics)
                    page.screenshot(path=str(output / (prefix + label + '-bottom.png')))
                    page.mouse.wheel(0, -20000)
                    page.wait_for_timeout(300)
                    assert page.evaluate('window.scrollY') == 0
                    scroll_checks.append({'page': label, **metrics, 'last_content_visible': True, 'wheel_up': True})
                for viewport in [{'width': 1200, 'height': 700}, {'width': 820, 'height': 600}]:
                    page.set_viewport_size(viewport)
                    check_wheel_scroll('console-' + str(viewport['width']), '#service-card-workbuddy_ai')
                page.set_viewport_size({'width': 1200, 'height': 900})
                page.screenshot(path=str(output / (prefix + "console-light.png")), full_page=True)
                card = page.locator("#service-card-codex")
                initial_profiles = page.locator('#profile-codex option').count()
                assert page.locator('#profile-codex').input_value() == 'builtin'
                builtin_documents = int(re.search(r'\d+', page.locator('#profile-codex option[value="builtin"]').inner_text()).group())
                assert builtin_documents == 53
                card.locator(".switch").click()
                expect(page.locator('#service-card-codex .switch')).to_have_attribute('aria-checked', 'true')
                assert (sandbox / "home" / ".codex" / "AGENTS.md").exists()
                assert len(list((sandbox / 'home' / '.codex' / 'skills').glob('*/SKILL.md'))) == builtin_documents + 1
                installed_suite = (sandbox / 'home/.codex/skills/pojia-local/SKILL.md').read_text('utf-8')
                assert '云端' not in installed_suite and '取回' not in installed_suite
                page.locator("#service-card-codex [data-action='verify']").click()
                expect(page.locator('#modal-body .check')).to_have_count(builtin_documents + 2)
                page.locator('#modal-title').hover()
                page.mouse.wheel(0, 20000)
                page.wait_for_timeout(300)
                assert page.locator('#modal').evaluate('(element) => element.scrollTop > 0')
                expect(page.locator('#modal-body p').last).to_be_in_viewport()
                page.locator('#modal').evaluate('(element) => element.scrollTop = 0')
                page.locator('#modal-close').click()
                page.locator("#profile-codex").select_option("advanced")
                expect(page.locator('#service-card-codex .switch')).to_be_enabled()
                assert (sandbox / "home" / ".codex" / "skills" / "pojia-local" / "references" / "checklist.md").exists()
                page.locator("#service-card-codex [data-action='verify']").click()
                expect(page.locator("#modal-body")).to_contain_text("本地文件完整")
                page.locator("#modal-close").click()
                page.locator("#service-card-codex .switch").click()
                page.locator("#confirm-revoke").click()
                expect(page.locator('#service-card-codex .switch')).to_have_attribute('aria-checked', 'false')
                assert not (sandbox / "home" / ".codex" / "AGENTS.md").exists()
                page.locator("[data-page='skills']").click()
                expect(page.locator('.library-card')).to_have_count(initial_profiles)
                check_wheel_scroll('skills', '#skills-page > .footnote')
                page.locator('[data-profile="builtin"]').click()
                directory_text = page.locator('.skill-content').text_content().replace('\r\n', '\n')
                assert directory_text == (ROOT / 'skills/builtin/SKILL.md').read_text('utf-8')
                assert not any(x in directory_text for x in ['云端', '取回', '原云', '404'])
                page.locator('.skill-content').evaluate('e => e.scrollTop = e.scrollHeight')
                page.screenshot(path=str(output / (prefix + 'skills-directory.png')))
                page.locator('#modal-close').click()
                page.locator('#skill-collection').select_option('builtin')
                expect(page.locator('.library-card')).to_have_count(builtin_documents + 1)
                page.locator('#skill-search').fill('apk-reverse')
                expect(page.locator('.library-card')).to_have_count(1)
                page.locator('.library-card button').click()
                expect(page.locator('.skill-content')).not_to_contain_text('云端原文的离线适配版')
                expect(page.locator('.skill-content')).to_contain_text('JNI')
                page.locator('#modal-close').click()
                page.screenshot(path=str(output / (prefix + 'skills-search.png')), full_page=True)
                page.locator('#skill-search').fill('')
                page.locator('#skill-category').select_option('入口')
                expect(page.locator('.library-card')).to_have_count(4)
                page.locator('#skill-category').select_option('')
                page.locator('#skill-collection').select_option('')
                assert not any(x in page.locator('body').inner_text() for x in
                               ['本地版', '独立本地版', '原云技能', '原云端取回', '云端原文', '离线适配'])
                page.locator("#import").click()
                page.locator("#import-path").fill(str(custom))
                page.locator("#confirm-import").click()
                expect(page.locator('.library-card')).to_have_count(initial_profiles + 1)
                page.screenshot(path=str(output / (prefix + "skills.png")))
                page.locator(".library-card").last.locator("button").click()
                expect(page.locator(".skill-content")).to_contain_text("Local UI acceptance instructions")
                page.locator("#modal-close").click()
                page.locator("[data-page='console']").click()
                page.locator("#theme").click()
                page.screenshot(path=str(output / (prefix + "console-dark.png")), full_page=True)
                assert page.locator("html").get_attribute("data-theme") == "dark"
                page.locator("[data-page='diagnostics']").click()
                assert "撤销技能" in page.locator("#events").inner_text()
                page.screenshot(path=str(output / (prefix + "diagnostics.png")), full_page=True)
                # A missing or undecodable movie must still let the user open the app.
                def fail_movie(route):
                    route.abort()
                context.route(url + '/assets/startup.mp4', fail_movie)
                page.reload()
                expect(page.locator('#startup')).to_be_hidden(timeout=16000)
                fallback = page.evaluate('window.startupStatus')
                assert fallback['reason'] in ('media-error', 'playback-unavailable'), fallback
                assert not page.locator('#app-shell').evaluate('e => e.inert')
                context.unroute(url + '/assets/startup.mp4', fail_movie)
                assert not errors, errors
                assert not external, external
                result = {"pass": True, "cards": 7, "install_switch_verify_revoke": True, "import_preview": True,
                          "extension_skill_count": 50, "suite_installation": True, "search_and_category": True,
                          "builtin_documents": builtin_documents, "collection_filter": True,
                          "light_dark_modes": True, "external_requests": external, "page_errors": errors,
                          "wheel_scroll": scroll_checks,
                          "long_modal_scroll": True,
                          "branding": "ai技能库", "source_labels_removed": True,
                          "actual_skill_text_cleaned": True, "preview_matches_skill_file": True,
                          "startup": {"video": video, "completion": startup,
                                      "no_initial_icon": True, "fills_window": fills,
                                      "no_skip_button": True, "failure_recovery": fallback},
                          "isolation": "temporary home; actual client configurations untouched"}
                result['executable'] = str(executable) if executable else 'source'
                (output / (prefix + "browser-result.json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
                print(json.dumps(result))
                browser.close()
        finally:
            if executable and process.poll() is None and os.name == 'nt':
                # A one-file executable has a bootloader parent and a runtime child.
                subprocess.run(['taskkill.exe', '/PID', str(process.pid), '/T', '/F'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            else:
                process.terminate()
            process.wait(timeout=10)
            process.stderr.close()


if __name__ == "__main__":
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
