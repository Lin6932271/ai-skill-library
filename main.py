"""Desktop window and local UI service for AI Skill Library."""
from __future__ import annotations

import argparse
import hmac
import json
import mimetypes
import os
import re
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from backend import SkillManager, VERSION


class App:
    def __init__(self, manager: SkillManager):
        self.manager = manager
        self.window = None
        self.token = secrets.token_urlsafe(32)
        self.server = None
        self.restore_frame_callback = None

    def invoke(self, command: str, args: dict) -> dict:
        if command == "finish_startup":
            restored = self.restore_frame_callback() if self.restore_frame_callback else False
            return {"ok": True, "data": {"restored": restored}}
        if command in ("pick_directory", "pick_skill", "pick_skill_directory"):
            if not self.window:
                return {"ok": False, "error": "文件选择需要桌面窗口；可直接填写路径"}
            import webview
            if command in ("pick_directory", "pick_skill_directory"):
                selected = self.window.create_file_dialog(webview.FileDialog.FOLDER)
            else:
                selected = self.window.create_file_dialog(webview.FileDialog.OPEN, allow_multiple=False,
                            file_types=("技能文件 (*.md;*.zip)", "所有文件 (*.*)"))
            return {"ok": True, "data": {"path": selected[0] if selected else ""}}
        if command == "open_directory":
            root = self.manager.root(args["provider"])
            if not root.is_dir():
                return {"ok": False, "error": "目录尚不存在，开启技能后会创建"}
            os.startfile(str(root))
            return {"ok": True, "data": {"path": str(root)}}
        if command == "export_diagnostics":
            if not self.window:
                return {"ok": True, "data": self.manager.diagnostics()}
            import webview
            selected = self.window.create_file_dialog(webview.FileDialog.SAVE, save_filename="ai技能库-诊断.json",
                                                     file_types=("JSON 文件 (*.json)",))
            if selected:
                dest = Path(selected[0] if isinstance(selected, (tuple, list)) else selected)
                dest.write_text(json.dumps(self.manager.diagnostics(), ensure_ascii=False, indent=2), encoding="utf-8")
                return {"ok": True, "data": {"path": str(dest)}}
            return {"ok": True, "data": {"cancelled": True}}
        return self.manager.dispatch(command, args)

    def start_server(self, port: int = 0) -> str:
        app = self
        static = self.manager.bundle_dir / "frontend"

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def send(self, code: int, data: bytes, mime: str, headers: dict | None = None):
                self.send_response(code)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'none'")
                for key, value in (headers or {}).items():
                    self.send_header(key, value)
                self.end_headers()
                try:
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # A closed window may cancel an in-flight video response.

            def json(self, code: int, payload: dict):
                self.send(code, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

            def valid_host(self):
                return self.headers.get("Host") == f"127.0.0.1:{app.server.server_port}"

            def do_GET(self):
                if not self.valid_host():
                    return self.json(403, {"ok": False, "error": "Host mismatch"})
                raw = urlsplit(self.path).path
                if raw == "/health":
                    return self.json(200, {"ok": True, "version": VERSION, "network": "disabled"})
                if raw == "/":
                    data = (static / "index.html").read_bytes().replace(b"{{TOKEN}}", app.token.encode())
                    return self.send(200, data, "text/html; charset=utf-8")
                rel = raw.lstrip("/")
                dest = static / rel
                if not dest.resolve().is_relative_to(static.resolve()) or not dest.is_file():
                    return self.json(404, {"ok": False, "error": "Not found"})
                mime = mimetypes.guess_type(dest.name)[0] or "application/octet-stream"
                if dest.suffix in (".js", ".css", ".html"):
                    mime += "; charset=utf-8"
                if dest.suffix == ".mp4":
                    data = dest.read_bytes()
                    size = len(data)
                    headers = {"Accept-Ranges": "bytes"}
                    requested = self.headers.get("Range")
                    if requested:
                        match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested)
                        try:
                            if not match or not any(match.groups()):
                                raise ValueError("Invalid range")
                            left, right = match.groups()
                            start = int(left) if left else max(0, size - int(right))
                            end = min(size - 1, int(right)) if left and right else size - 1
                            if start >= size or end < start or (not left and int(right) == 0):
                                raise ValueError("Unsatisfiable range")
                        except ValueError:
                            return self.send(416, b"", mime, {**headers, "Content-Range": f"bytes */{size}"})
                        headers["Content-Range"] = f"bytes {start}-{end}/{size}"
                        return self.send(206, data[start:end + 1], mime, headers)
                    return self.send(200, data, mime, headers)
                return self.send(200, dest.read_bytes(), mime)

            def do_POST(self):
                origin = f"http://127.0.0.1:{app.server.server_port}"
                if (not self.valid_host() or self.headers.get("Origin") != origin
                        or not hmac.compare_digest(self.headers.get("X-Pojia-Local", ""), app.token)):
                    return self.json(403, {"ok": False, "error": "本地请求验证失败"})
                if self.path != "/api":
                    return self.json(404, {"ok": False, "error": "Not found"})
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length <= 0 or length > 1024 * 1024:
                        raise ValueError("请求大小无效")
                    payload = json.loads(self.rfile.read(length))
                    if not isinstance(payload, dict) or not isinstance(payload.get("command"), str):
                        raise ValueError("请求格式无效")
                    args = payload.get("args", {})
                    if not isinstance(args, dict):
                        raise ValueError("参数格式无效")
                    result = app.invoke(payload["command"], args)
                    return self.json(200, result)
                except (ValueError, KeyError, OSError) as exc:
                    return self.json(400, {"ok": False, "error": str(exc)})
                except Exception as exc:
                    # Do not return stack traces, environment variables, or file contents.
                    return self.json(500, {"ok": False, "error": f"本地操作失败：{type(exc).__name__}"})

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.server.server_port}"


class DesktopFrame:
    """Start without a caption; restore the standard frame on the GUI thread."""
    def __init__(self, window):
        self.window = window
        self.restored = False
        self.lock = threading.Lock()

    def restore(self):
        with self.lock:
            if self.restored:
                return True
            native = self.window.native
            if native is None or native.IsDisposed:
                return False
            from System import Action
            from System.Windows.Forms import FormBorderStyle

            def apply():
                bounds = native.Bounds
                native.FormBorderStyle = FormBorderStyle.Sizable
                native.frameless = False
                self.window.frameless = False
                # Changing decoration must not resize or move the application window.
                native.Bounds = bounds
                self.restored = True

            if native.InvokeRequired:
                native.Invoke(Action(apply))
            else:
                apply()
            return self.restored


def capture_native_window(window, path):
    """Capture this window alone, including its native decoration if present."""
    import ctypes
    from ctypes import wintypes
    from PIL import Image
    user32 = ctypes.windll.user32
    gdi = ctypes.windll.gdi32
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
    user32.GetWindowDC.argtypes = [wintypes.HWND]
    user32.GetWindowDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    gdi.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi.CreateCompatibleDC.restype = wintypes.HDC
    gdi.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi.SelectObject.restype = wintypes.HGDIOBJ
    gdi.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi.DeleteDC.argtypes = [wintypes.HDC]
    gdi.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT,
                            ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT]
    handle = int(window.native.Handle.ToInt64())
    rect = wintypes.RECT()
    user32.GetWindowRect(handle, ctypes.byref(rect))
    width, height = rect.right - rect.left, rect.bottom - rect.top
    source_dc = user32.GetWindowDC(handle)
    dest_dc = gdi.CreateCompatibleDC(source_dc)
    bitmap = gdi.CreateCompatibleBitmap(source_dc, width, height)
    old = gdi.SelectObject(dest_dc, bitmap)
    try:
        user32.PrintWindow(handle, dest_dc, 2)
        class BitmapInfo(ctypes.Structure):
            _fields_ = [("size", wintypes.DWORD), ("width", wintypes.LONG), ("height", wintypes.LONG),
                        ("planes", wintypes.WORD), ("bits", wintypes.WORD), ("compression", wintypes.DWORD),
                        ("image_size", wintypes.DWORD), ("x", wintypes.LONG), ("y", wintypes.LONG),
                        ("colors", wintypes.DWORD), ("important", wintypes.DWORD)]
        info = BitmapInfo(40, width, -height, 1, 32, 0, 0, 0, 0, 0, 0)
        buffer = ctypes.create_string_buffer(width * height * 4)
        gdi.GetDIBits(dest_dc, bitmap, 0, height, buffer, ctypes.byref(info), 0)
        Image.frombytes("RGB", (width, height), buffer.raw, "raw", "BGRX").save(path)
    finally:
        gdi.SelectObject(dest_dc, old)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(dest_dc)
        user32.ReleaseDC(handle, source_dc)
    return [width, height]


def main():
    parser = argparse.ArgumentParser(description="ai技能库")
    parser.add_argument("--serve", action="store_true", help="仅启动本地界面服务，供验收或浏览器使用")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--home", type=Path)
    parser.add_argument("--sandbox", action="store_true", help="忽略真实客户端环境变量")
    parser.add_argument("--ready-file", type=Path)
    parser.add_argument("--smoke-file", type=Path, help="启动真实桌面窗口，记录界面验收后关闭")
    args = parser.parse_args()
    bundle = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    manager = SkillManager(args.data_dir, args.home, bundle, use_env=not args.sandbox)
    # Hold a process-level lock throughout the session to avoid conflicting writes.
    instance_guard = open(manager.data_dir / ".instance.lock", "a+b")
    if not instance_guard.tell():
        instance_guard.write(b"1")
        instance_guard.flush()
    instance_guard.seek(0)
    if os.name == "nt":
        import msvcrt
        try:
            msvcrt.locking(instance_guard.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            instance_guard.close()
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, "ai技能库已在运行，请使用现有窗口。", "ai技能库", 0)
            return
    app = App(manager)
    url = app.start_server(args.port)
    if args.ready_file:
        args.ready_file.parent.mkdir(parents=True, exist_ok=True)
        args.ready_file.write_text(json.dumps({"url": url, "pid": os.getpid()}), encoding="utf-8")
    if args.serve:
        if sys.stdout:
            print(url, flush=True)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            app.server.shutdown()
        return
    import webview
    if os.name == "nt":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AISkillLibrary.Desktop")
    window = webview.create_window("ai技能库", url, width=1200, height=860,
                                  min_size=(900, 640), background_color="#000000",
                                  frameless=True, easy_drag=False, shadow=False)
    app.window = window
    frame = DesktopFrame(window)
    app.restore_frame_callback = frame.restore
    # Recover normal window controls even if the frontend fails to load.
    frame_watchdog = threading.Timer(20, frame.restore)
    frame_watchdog.daemon = True
    window.events.shown += frame_watchdog.start
    if args.smoke_file:
        def native_acceptance():
            result = {"pass": False, "pid": os.getpid(), "runtime": "WebView2 desktop"}
            try:
                result['startup_border_style'] = str(window.native.FormBorderStyle)
                bounds = window.native.Bounds
                result['startup_window_bounds'] = [bounds.X, bounds.Y, bounds.Width, bounds.Height]
                for _ in range(45):
                    current = window.evaluate_js("document.querySelector('#startup-video').currentTime")
                    if current > .5:
                        break
                    time.sleep(.1)
                startup_screenshot = args.smoke_file.with_name(args.smoke_file.stem + '-startup.png')
                result['startup_window_pixels'] = capture_native_window(window, startup_screenshot)
                result['startup_screenshot'] = str(startup_screenshot)
                result['startup_layout'] = window.evaluate_js("""(() => {
                    const video = document.querySelector('#startup-video');
                    const box = video.getBoundingClientRect();
                    return {poster: video.getAttribute('poster'),
                            images: document.querySelectorAll('#startup img').length,
                            fit: getComputedStyle(video).objectFit,
                            bounds: {x: box.x, y: box.y, width: box.width, height: box.height},
                            viewport: {width: window.innerWidth, height: window.innerHeight},
                            // WebView2 can report fractional CSS pixels at Windows display scaling.
                            fills_window: Math.abs(box.x) < 1 && Math.abs(box.y) < 1 &&
                                Math.abs(box.width - window.innerWidth) < 1 &&
                                Math.abs(box.height - window.innerHeight) < 1,
                            fullscreen: document.fullscreenElement !== null};
                })()""")
                result['window_state'] = str(window.native.WindowState)
                for _ in range(220):
                    count = window.evaluate_js("document.querySelectorAll('.pj-service-card').length")
                    finished = window.evaluate_js("document.querySelector('#startup').hidden")
                    if count == 7 and finished:
                        break
                    time.sleep(.1)
                body = window.evaluate_js("document.body.innerText")
                result.update({"cards": count, "title": window.evaluate_js("document.title"),
                               "viewport": window.evaluate_js("[window.innerWidth, window.innerHeight]"),
                               "removed_account_ui": not any(s in body for s in ("账户", "订阅", "反馈")),
                               "network": "local-only", "startup": window.evaluate_js("window.startupStatus"),
                               "native_title": str(window.native.Text),
                               "restored_border_style": str(window.native.FormBorderStyle),
                               "native_icon_size": [window.native.Icon.Width, window.native.Icon.Height],
                               "no_skip_button": window.evaluate_js("!document.querySelector('#startup button')")})
                result["pass"] = (count == 7 and result["removed_account_ui"] and finished
                                  and result["title"] == "ai技能库" and result["native_title"] == "ai技能库"
                                  and result["startup"]["playing"] and result["startup"]["reason"] == "ended"
                                  and result["no_skip_button"]
                                  and result['startup_layout']['poster'] is None
                                  and result['startup_layout']['images'] == 0
                                  and result['startup_layout']['fit'] == 'cover'
                                  and result['startup_layout']['fills_window']
                                  and not result['startup_layout']['fullscreen']
                                  and result['window_state'] == 'Normal')
                bounds = window.native.Bounds
                result['restored_window_bounds'] = [bounds.X, bounds.Y, bounds.Width, bounds.Height]
                result['pass'] = (result['pass'] and result['startup_border_style'] == 'None'
                                  and result['restored_border_style'] == 'Sizable'
                                  and result['startup_window_bounds'] == result['restored_window_bounds']
                                  and result['startup']['native_frame_restored'])
                scroll = window.evaluate_js("""(() => {
                    window.scrollTo(0, document.scrollingElement.scrollHeight);
                    const last = document.querySelector('#service-card-workbuddy_ai').getBoundingClientRect();
                    return {body_overflow: getComputedStyle(document.body).overflowY,
                            root_overflow: getComputedStyle(document.documentElement).overflowY,
                            y: window.scrollY, viewport: window.innerHeight,
                            last_card_visible: last.top >= 0 && last.bottom <= window.innerHeight};
                })()""")
                result["scroll_layout"] = scroll
                result["pass"] = (result["pass"] and scroll["body_overflow"] == "visible"
                                  and scroll["root_overflow"] == "auto" and scroll["y"] > 0
                                  and scroll["last_card_visible"])
                window.evaluate_js("window.scrollTo(0, 0)")
                if os.name == "nt":
                    time.sleep(.3)
                    screenshot = args.smoke_file.with_suffix(".png")
                    result["window_pixels"] = capture_native_window(window, screenshot)
                    result["screenshot"] = str(screenshot)
            except Exception as exc:
                result["error"] = f"{type(exc).__name__}: {exc}"
            finally:
                args.smoke_file.parent.mkdir(parents=True, exist_ok=True)
                args.smoke_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                window.destroy()
        window.events.loaded += native_acceptance
    try:
        webview.start(gui="edgechromium", private_mode=True,
                      icon=str(bundle / "frontend/assets/app-icon.ico"))
    finally:
        frame_watchdog.cancel()
        app.server.shutdown()
        instance_guard.close()


if __name__ == "__main__":
    main()
