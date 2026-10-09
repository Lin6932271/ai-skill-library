import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
from backend import SkillManager, LocalError, PROVIDERS, BEGIN, END
from main import App


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manager = SkillManager(self.root / "data", self.root / "home", use_env=False)
        manifest = self.manager.rea.manifest
        runtime_root = self.root / ('rea-' + manifest['rea_version'] + '-' + manifest['sha256'][:12])
        runtime = {"root": str(runtime_root), "node": str(runtime_root / "node.exe"),
                   "entry": str(runtime_root / "rea.mjs"), "cli": str(runtime_root / "rea.cmd"), "version": "6.1.0"}
        self.runtime_patches = [patch('rea_runtime.ReaRuntime.ensure', return_value=runtime),
            patch('rea_runtime.ReaRuntime.probe', return_value={"ok": True, "version": "6.1.0", "tool_count": 138, "client_connected": False}),
            patch('rea_runtime.ReaRuntime.ready', return_value=True)]
        for runtime_patch in self.runtime_patches:
            runtime_patch.start()
            self.addCleanup(runtime_patch.stop)

    def tearDown(self):
        self.temp.cleanup()

    def test_extensions_suite_all_names_seven_clients_and_individual_switch(self):
        index = json.loads((self.manager.bundle_dir / 'skills' / 'routing-index.json').read_text('utf-8'))
        names = {row['name'] for row in index['entries'] + index['modules']} | set(index['extra_mapping_names'])
        self.assertEqual(len(names), 50)
        self.assertEqual(names, {row['skill_name'] for row in self.manager.catalog})
        for provider, spec in PROVIDERS.items():
            with self.subTest(provider=provider):
                root = self.manager.root(provider)
                root.mkdir(parents=True)
                instruction = root / spec[3]
                original = b'\xef\xbb\xbfExisting instructions\r\n'
                instruction.write_bytes(original)
                self.manager.inject(provider, 'extended')
                self.assertEqual(len(self.manager.verify(provider)['checks']), 61)
                self.assertTrue(self.manager.verify(provider)['ok'])
                for name in names:
                    skill = root / 'skills' / name / 'SKILL.md'
                    self.assertNotIn('本地重建版', skill.read_text('utf-8'))
                self.manager.inject(provider, 'extension-apk-reverse')
                self.assertTrue((root / 'skills' / 'apk-reverse' / 'SKILL.md').exists())
                self.assertFalse((root / 'skills' / 'l-reverse' / 'SKILL.md').exists())
                self.assertIn(b'skills/apk-reverse/SKILL.md', instruction.read_bytes())
                self.manager.inject(provider, 'extended')
                self.assertTrue(self.manager.revoke(provider)['removed'])
                self.assertEqual(instruction.read_bytes(), original)
                self.assertFalse(list((root / 'skills').rglob('SKILL.md')))

    def test_extensions_suite_collision_keeps_every_existing_byte(self):
        root = self.manager.root('codex')
        path = root / 'skills' / 'l-reverse' / 'SKILL.md'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'user skill')
        with self.assertRaises(LocalError):
            self.manager.inject('codex', 'extended')
        self.assertEqual(path.read_bytes(), b'user skill')
        self.assertFalse((root / 'AGENTS.md').exists())
        self.assertEqual(list((root / 'skills').rglob('SKILL.md')), [path])

    def test_previous_release_record_migrates_without_losing_files(self):
        self.manager.inject('codex', 'advanced')
        record = self.manager.state['installed']['codex']
        # The legacy format predates REA and contains only the pojia-local folder.
        from rea_config import McpConfig
        adapter = McpConfig('codex', self.manager.root('codex'), self.manager.home)
        restored = adapter.restore(adapter.path.read_bytes(), record.pop('rea')['config'], __import__('backend').sha)
        if restored is None:
            adapter.path.unlink()
        else:
            adapter.path.write_bytes(restored)
        for name in list(record['files']):
            if name.startswith('reverse-engineer-anything/'):
                (self.manager.root('codex') / 'skills' / name).unlink()
                record['files'].pop(name)
        record.pop('files_root')
        record['files'] = {name.removeprefix('pojia-local/'): value for name, value in record['files'].items()}
        self.manager.save()
        reloaded = SkillManager(self.root / 'data', self.root / 'home', use_env=False)
        self.assertTrue(reloaded.verify('codex')['ok'])
        reloaded.inject('codex', 'extended')
        self.assertFalse((reloaded.root('codex') / 'skills' / 'pojia-local' / 'references' / 'checklist.md').exists())
        self.assertTrue(reloaded.verify('codex')['ok'])
        self.assertTrue(reloaded.revoke('codex')['removed'])

    def test_extensions_links_resolve_in_deployed_suite(self):
        import re
        files = self.manager.deployment_files('extended')
        for rel, content in files.items():
            for target in re.findall(r'\]\(([^)]+)\)', content.decode('utf-8')):
                if target.startswith(('https://', 'http://', '#')):
                    continue
                resolved = (Path('/skills') / rel).parent / target
                import posixpath
                normalized = posixpath.normpath(resolved.as_posix()).removeprefix('/skills/')
                self.assertTrue(normalized in files, (rel, target))

    def test_single_entry_installs_referenced_modules(self):
        self.manager.inject('claude', 'extension-l-license')
        root = self.manager.root('claude') / 'skills'
        expected = {'l-license', 'reverse-engineering', 'dotnet-reverse', 'apk-reverse', 'thick-client', 'reverse-engineer-anything'}
        self.assertEqual({p.parent.name for p in root.glob('*/SKILL.md')}, expected)
        self.assertTrue(self.manager.verify('claude')['ok'])
        self.assertTrue(self.manager.revoke('claude')['removed'])

    def test_builtin_suite_all_clients_switch_and_restore(self):
        self.assertEqual(len(self.manager.builtin_catalog), 54)
        for provider, spec in PROVIDERS.items():
            with self.subTest(provider=provider):
                root = self.manager.root(provider)
                root.mkdir(parents=True)
                instruction = root / spec[3]
                original = b'Original user instructions\r\n'
                instruction.write_bytes(original)
                self.manager.inject(provider, 'extended')
                self.manager.inject(provider, 'builtin')
                self.assertTrue(self.manager.verify(provider)['ok'])
                self.assertEqual(len(list((root/'skills').glob('*/SKILL.md'))), 55)
                self.assertFalse((root/'skills/container-runtime/SKILL.md').exists())
                self.assertTrue((root/'skills/docs-generator/SKILL.md').exists())
                self.manager.inject(provider, 'builtin-apk-reverse')
                content = (root/'skills/apk-reverse/SKILL.md').read_text('utf-8')
                self.assertIn('JNI', content)
                self.assertNotIn('云端原文的离线适配版', content)
                self.assertTrue(self.manager.revoke(provider)['removed'])
                self.assertEqual(instruction.read_bytes(), original)

    def test_builtin_content_hashes_and_entry_dependencies(self):
        import hashlib
        for item in self.manager.builtin_catalog:
            content = self.manager.profile_files(item['id'])['SKILL.md']
            self.assertEqual(hashlib.sha256(content).hexdigest(), item['content_sha256'])
            self.assertNotIn('raw_sha256', item)
            self.assertNotIn(b'L-SKILL CONTENT-PROTECTION:START', content)
            self.assertNotIn(b'skills-api/redeem', content)
            self.assertNotIn('云端原文的离线适配版', content.decode('utf-8'))
            self.assertNotIn(b'cloud routing entry', content)
            self.assertNotIn(b'No redeem request', content)
        suite = self.manager.profile_files('builtin')['SKILL.md'].decode('utf-8')
        self.assertNotIn('云端', suite)
        self.assertNotIn('取回', suite)
        self.assertIn('../cloud-k8s/SKILL.md', suite)
        self.manager.inject('codex', 'builtin-l-reverse')
        deployed = {p.parent.name for p in (self.manager.root('codex')/'skills').glob('*/SKILL.md')}
        entry = self.manager.builtins['builtin-l-reverse']
        self.assertEqual(deployed, {'l-reverse', *entry['dependencies'], 'reverse-engineer-anything'})
        self.assertTrue(self.manager.verify('codex')['ok'])

    def test_extension_generation_keeps_metadata_neutral(self):
        import generate_extensions
        with patch.object(generate_extensions, 'ROOT', self.root / 'generated'):
            generate_extensions.build(self.manager.bundle_dir / 'skills/routing-index.json')
        generated = self.root / 'generated'
        catalog = json.loads((generated / 'skills/extensions-catalog.json').read_text('utf-8'))
        self.assertEqual(len(catalog['items']), 50)
        self.assertNotIn('origin', catalog)
        for item in catalog['items']:
            content = (generated / 'skills/extended/library' / item['skill_name'] / 'SKILL.md').read_text('utf-8')
            self.assertNotIn('本地重建版', content)
            self.assertNotIn('reconstructed', item)
        router = (generated / 'skills/extended/SKILL.md').read_text('utf-8')
        self.assertNotIn('原 EXE', router)
        self.assertNotIn('原索引', router)

    def test_existing_profile_aliases_install_switch_and_restore(self):
        root = self.manager.root('codex')
        root.mkdir(parents=True)
        instruction = root / 'AGENTS.md'
        original = b'Existing instructions\r\n'
        instruction.write_bytes(original)
        self.manager.inject('codex', 'cloud-all')
        self.manager.state['installed']['codex']['profile'] = 'cloud-all'
        self.manager.save()
        loaded = SkillManager(self.root / 'data', self.root / 'home', use_env=False)
        self.assertEqual(loaded.status()['providers'][0]['profile'], 'builtin')
        loaded.inject('codex', 'rebuilt-apk-reverse')
        self.assertTrue(loaded.verify('codex')['ok'])
        loaded.revoke('codex')
        self.assertEqual(instruction.read_bytes(), original)

    def test_all_seven_clients_install_switch_verify_and_exact_restore(self):
        for provider, spec in PROVIDERS.items():
            with self.subTest(provider=provider):
                root = self.manager.root(provider)
                root.mkdir(parents=True)
                instruction = root / spec[3]
                original = b"\xef\xbb\xbf# Original\r\n\r\nExisting custom instructions."
                instruction.write_bytes(original)
                unrelated = root / "skills" / "user-skill" / "SKILL.md"
                unrelated.parent.mkdir(parents=True)
                unrelated.write_bytes(b"keep me")
                result = self.manager.inject(provider, "basic")
                self.assertTrue(result["verification"]["ok"])
                self.assertTrue((Path(result["backup"]) / "snapshot.json").is_file())
                self.assertTrue(instruction.read_bytes().startswith(original))
                self.manager.inject(provider, "advanced")
                self.assertTrue((root / "skills" / "pojia-local" / "references" / "checklist.md").exists())
                self.manager.inject(provider, "basic")
                self.assertFalse((root / "skills" / "pojia-local" / "references" / "checklist.md").exists())
                self.assertTrue(self.manager.verify(provider)["ok"])
                self.assertTrue(self.manager.revoke(provider)["removed"])
                self.assertEqual(instruction.read_bytes(), original)
                self.assertEqual(unrelated.read_bytes(), b"keep me")

    def test_new_instruction_is_removed_on_revoke(self):
        path = self.manager.root("codex") / "AGENTS.md"
        self.manager.inject("codex")
        self.manager.revoke("codex")
        self.assertFalse(path.exists())

    def test_external_text_outside_managed_block_survives(self):
        path = self.manager.root("claude") / "CLAUDE.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"existing")
        self.manager.inject("claude")
        path.write_bytes(path.read_bytes() + b"\nUSER ADDED THIS")
        self.manager.revoke("claude")
        self.assertEqual(path.read_bytes(), b"existing\nUSER ADDED THIS")

    def test_changed_managed_block_is_never_overwritten(self):
        self.manager.inject("codex")
        path = self.manager.root("codex") / "AGENTS.md"
        modified = path.read_bytes().replace(b"# ", b"# CUSTOM ", 1)
        path.write_bytes(modified)
        self.assertFalse(self.manager.verify("codex")["ok"])
        with self.assertRaises(LocalError):
            self.manager.inject("codex", "advanced")
        result = self.manager.revoke("codex")
        self.assertFalse(result["removed"])
        self.assertEqual(path.read_bytes(), modified)

    def test_changed_skill_is_preserved_and_can_be_resolved(self):
        self.manager.inject("codex")
        path = self.manager.root("codex") / "skills" / "pojia-local" / "SKILL.md"
        original = path.read_bytes()
        path.write_bytes(b"user edited this")
        result = self.manager.revoke("codex")
        self.assertFalse(result["removed"])
        self.assertEqual(path.read_bytes(), b"user edited this")
        path.write_bytes(original)
        self.assertTrue(self.manager.revoke("codex")["removed"])

    def test_existing_unowned_skill_is_not_replaced(self):
        path = self.manager.root("codex") / "skills" / "pojia-local" / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"another owner")
        with self.assertRaises(LocalError):
            self.manager.inject("codex")
        self.assertEqual(path.read_bytes(), b"another owner")
        self.assertFalse((path.parents[2] / "AGENTS.md").exists())

    def test_multi_file_import_and_reload(self):
        folder = self.root / "custom"
        (folder / "references").mkdir(parents=True)
        (folder / "SKILL.md").write_text("# My Local Skill\n\nLocal instructions.", encoding="utf-8")
        (folder / "references" / "guide.md").write_bytes(b"my reference")
        result = self.manager.import_skill(str(folder))
        self.manager.inject("codex", result["id"])
        self.assertEqual((self.manager.root("codex") / "skills" / "pojia-local" / "references" / "guide.md").read_bytes(), b"my reference")
        reload = SkillManager(self.root / "data", self.root / "home", use_env=False)
        self.assertTrue(reload.verify("codex")["ok"])
        self.assertIn(result["id"], [p["id"] for p in reload.profiles()])

    def test_zip_traversal_and_duplicate_names_are_rejected(self):
        for names in [("SKILL.md", "../escape.txt"), ("SKILL.md", "skill.md")]:
            archive = self.root / "bad.zip"
            with zipfile.ZipFile(archive, "w") as stream:
                for name in names:
                    stream.writestr(name, b"# local")
            with self.assertRaises(LocalError):
                self.manager.import_skill(str(archive))
        self.assertFalse((self.root / "escape.txt").exists())

    def test_invalid_directory_and_workbuddy_collision(self):
        with self.assertRaises(LocalError):
            self.manager.set_path("codex", "relative")
        with self.assertRaises(LocalError):
            self.manager.set_path("codex", str(Path(self.root.anchor)))
        with self.assertRaises(LocalError):
            self.manager.set_path("workbuddy_ai", str(self.manager.root("workbuddy")))
        self.manager.inject("codex")
        with self.assertRaises(LocalError):
            self.manager.set_path("codex", str(self.root / "elsewhere"))

    def test_transaction_rolls_back_if_file_write_fails(self):
        import backend
        real_write = backend.atomic_write
        failed = False
        def fail_once(path, data):
            nonlocal failed
            if path.name == "SKILL.md" and not failed:
                failed = True
                raise OSError("simulated disk failure")
            return real_write(path, data)
        with patch("backend.atomic_write", side_effect=fail_once):
            with self.assertRaises(OSError):
                self.manager.inject("codex")
        self.assertFalse((self.manager.root("codex") / "AGENTS.md").exists())
        self.assertFalse(self.manager.state["installed"])

    def test_all_core_operations_work_when_sockets_are_disabled(self):
        def no_network(*_a, **_k):
            raise AssertionError("unexpected network")
        with patch("socket.socket", side_effect=no_network), patch("socket.create_connection", side_effect=no_network):
            self.manager.inject("claude")
            self.assertTrue(self.manager.verify("claude")["ok"])
            self.manager.status()
            self.manager.diagnostics()
            self.manager.revoke("claude")

    def test_video_ranges_support_complete_playback_and_reject_bad_ranges(self):
        import urllib.request
        import urllib.error
        movie = (self.manager.bundle_dir / 'frontend/assets/startup.mp4').read_bytes()
        app = App(self.manager)
        url = app.start_server()
        try:
            for requested, start, end in [('bytes=0-255', 0, 255),
                                           ('bytes=-128', len(movie) - 128, len(movie) - 1),
                                           (f'bytes={len(movie)-64}-', len(movie) - 64, len(movie) - 1)]:
                req = urllib.request.Request(url + '/assets/startup.mp4', headers={'Range': requested})
                with urllib.request.urlopen(req, timeout=3) as response:
                    self.assertEqual(response.status, 206)
                    self.assertEqual(response.headers['Content-Range'], f'bytes {start}-{end}/{len(movie)}')
                    self.assertEqual(response.read(), movie[start:end + 1])
            for requested in [f'bytes={len(movie)}-', 'bytes=-0', 'bytes=100-20', 'bytes=0-1,3-4', 'bytes=-']:
                req = urllib.request.Request(url + '/assets/startup.mp4', headers={'Range': requested})
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(req, timeout=3)
                self.assertEqual(raised.exception.code, 416)
                self.assertEqual(raised.exception.headers['Content-Range'], f'bytes */{len(movie)}')
                raised.exception.close()
        finally:
            app.server.shutdown()
            app.server.server_close()

    def test_local_api_rejects_remote_origin_and_invalid_token(self):
        import http.client
        import socket
        from contextlib import contextmanager
        app = App(self.manager)
        url = app.start_server()
        @contextmanager
        def request(origin, token):
            payload = b'{"command":"status"}'
            headers = (f"POST /api HTTP/1.0\r\n"
                       f"Host: 127.0.0.1:{app.server.server_port}\r\n"
                       f"Content-Type: application/json\r\n"
                       f"Content-Length: {len(payload)}\r\n"
                       f"Origin: {origin}\r\n"
                       f"X-Pojia-Local: {token}\r\n\r\n").encode('ascii')
            with socket.create_connection(('127.0.0.1', app.server.server_port), timeout=3) as connection:
                connection.sendall(headers + payload)
                response = http.client.HTTPResponse(connection)
                try:
                    response.begin()
                    yield response
                finally:
                    response.close()
        try:
            for origin, token in [("https://external.example", app.token), (url, "wrong")]:
                with request(origin, token) as response:
                    self.assertEqual(response.status, 403)
                    self.assertFalse(json.loads(response.read())["ok"])
            with request(url, app.token) as response:
                self.assertEqual(response.status, 200)
                value = json.loads(response.read())
                self.assertTrue(value["ok"])
                self.assertEqual(len(value["data"]["providers"]), 7)
        finally:
            app.server.shutdown()
            app.server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
