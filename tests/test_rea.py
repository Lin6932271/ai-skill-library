"""Ownership, rollback and client-format acceptance for automatic REA integration."""
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
from backend import SkillManager, LocalError, PROVIDERS, sha
from rea_config import McpConfig, ReaError, SERVER_NAME


class ReaConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "用户目录"
        self.runtime = {"root": str(self.home / "rea"), "node": str(self.home / "rea/node.exe"),
            "entry": str(self.home / "rea/rea.mjs"), "cli": str(self.home / "rea/rea.cmd"), "version": "6.1.0"}

    def adapter(self, provider):
        return McpConfig(provider, self.home / PROVIDERS[provider][2], self.home)

    def original(self, provider):
        if provider == "codex":
            return b'# user comment\nmodel = "existing-model"\n[mcp_servers.other]\ncommand = "existing"\n'
        if provider == "hermes":
            return b'# keep comment\nmodel: existing-model\nmcp_servers:\n  other:\n    command: existing\n'
        if provider == "deepseek":
            return b'# keep expression without executing it\n- insert:\n    - id: custom\n      name: custom-plugin\n      config:\n        cwd: !!js process.cwd()\n'
        if provider == "zcode":
            return b'{"model":"existing-model", "mcp":{"servers":{"other":{"command":"existing"}}}}'
        return b'{"model":"existing-model", "mcpServers":{"other":{"command":"existing"}}}'

    def test_all_seven_formats_preserve_other_entries_and_exact_original(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider):
                adapter = self.adapter(provider)
                original = self.original(provider)
                changed, record = adapter.prepare(original, self.runtime, None, sha)
                self.assertTrue(adapter.check(changed, record))
                self.assertIn(b'existing', changed) if provider != 'deepseek' else self.assertIn(b'!!js', changed)
                if provider in ('codex', 'hermes', 'deepseek'):
                    self.assertIn(b'# keep' if provider != 'codex' else b'# user comment', changed)
                self.assertEqual(adapter.restore(changed, record, sha), original)

    def test_later_user_changes_survive_revoke(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider):
                adapter = self.adapter(provider)
                changed, record = adapter.prepare(self.original(provider), self.runtime, None, sha)
                document = adapter.parse(changed)
                if provider == 'deepseek':
                    document.append({'insert': [{'id': 'later-user-plugin', 'name': 'user-plugin'}]})
                else:
                    document['user_added'] = 'keep this'
                    adapter.servers(document, create=True)['later'] = {'command': 'later-command'}
                edited = adapter.dump(document)
                restored = adapter.restore(edited, record, sha)
                self.assertIn(b'later', restored)
                self.assertIsNone(adapter.entry(adapter.parse(restored)))

    def test_same_name_unowned_registration_is_not_overwritten(self):
        adapter = self.adapter('codex')
        source = b'[mcp_servers.ai_skill_library_rea]\ncommand="user-command"\n'
        with self.assertRaises(ReaError):
            adapter.prepare(source, self.runtime, None, sha)

    def test_owned_entry_edit_blocks_reinstall_and_revoke(self):
        adapter = self.adapter('claude')
        data, record = adapter.prepare(self.original('claude'), self.runtime, None, sha)
        document = adapter.parse(data)
        document['mcpServers'][SERVER_NAME]['command'] = 'user-override'
        edited = adapter.dump(document)
        with self.assertRaises(ReaError):
            adapter.prepare(edited, self.runtime, record, sha)
        with self.assertRaises(ReaError):
            adapter.restore(edited, record, sha)

    def test_reinjection_remembers_original_config(self):
        adapter = self.adapter('hermes')
        original = self.original('hermes')
        data, record = adapter.prepare(original, self.runtime, None, sha)
        updated = dict(self.runtime, entry=str(self.home / 'new/rea.mjs'))
        data2, record2 = adapter.prepare(data, updated, record, sha)
        self.assertEqual(adapter.restore(data2, record2, sha), original)

    def test_malformed_configuration_is_rejected(self):
        for provider, source in [('codex', b'[broken'), ('claude', b'{broken'), ('hermes', b'a: [')]:
            with self.subTest(provider=provider):
                with self.assertRaises(ReaError):
                    self.adapter(provider).prepare(source, self.runtime, None, sha)

    def test_new_config_can_be_removed_exactly(self):
        for provider in PROVIDERS:
            adapter = self.adapter(provider)
            data, record = adapter.prepare(None, self.runtime, None, sha)
            self.assertIsNone(adapter.restore(data, record, sha))

    def test_inline_toml_settings_are_preserved(self):
        adapter = self.adapter('codex')
        original = b'model="old"\nmcp_servers={other={command="existing"}}\n'
        data, record = adapter.prepare(original, self.runtime, None, sha)
        self.assertIn(b'existing', data)
        self.assertEqual(adapter.restore(data, record, sha), original)

    def test_injection_failure_leaves_client_files_unchanged(self):
        manager = SkillManager(self.home / 'data', self.home, use_env=False)
        root = manager.root('codex')
        root.mkdir(parents=True)
        instruction = root / 'AGENTS.md'
        instruction.write_bytes(b'original instructions')
        config = root / 'config.toml'
        original = self.original('codex')
        config.write_bytes(original)
        with patch.object(manager.rea, 'ensure', return_value=self.runtime), patch.object(manager.rea, 'probe', side_effect=ReaError('startup failed')):
            result = manager.dispatch('inject', {'provider': 'codex', 'profile': 'builtin'})
        self.assertFalse(result['ok'])
        self.assertEqual(config.read_bytes(), original)
        self.assertEqual(instruction.read_bytes(), b'original instructions')
        self.assertFalse(list((root / 'skills').glob('*/SKILL.md')))
        self.assertFalse(manager.state['installed'])

    def test_write_failure_rolls_back_mcp_skills_and_instructions(self):
        manager = SkillManager(self.home / 'data', self.home, use_env=False)
        adapter = self.adapter('codex')
        adapter.path.parent.mkdir(parents=True)
        adapter.path.write_bytes(self.original('codex'))
        import backend
        original_write = backend.atomic_write
        def failing_write(path, data):
            if path == adapter.path and SERVER_NAME.encode() in data:
                raise OSError('simulated disk failure')
            return original_write(path, data)
        with patch.object(manager.rea, 'ensure', return_value=self.runtime), patch.object(manager.rea, 'probe', return_value={'ok':True}), patch('backend.atomic_write', side_effect=failing_write):
            result = manager.dispatch('inject', {'provider':'codex','profile':'basic'})
        self.assertFalse(result['ok'])
        self.assertEqual(adapter.path.read_bytes(), self.original('codex'))
        self.assertFalse((adapter.path.parent / 'AGENTS.md').exists())
        self.assertFalse(list((adapter.path.parent / 'skills').glob('*/SKILL.md')))

    def test_user_edit_during_runtime_preparation_is_not_overwritten(self):
        manager = SkillManager(self.home / 'data', self.home, use_env=False)
        adapter = self.adapter('codex')
        adapter.path.parent.mkdir(parents=True)
        original = self.original('codex')
        adapter.path.write_bytes(original)
        updated = original + b'# added while preparing\n'
        def user_edit(runtime):
            adapter.path.write_bytes(updated)
            return {'ok': True}
        with patch.object(manager.rea, 'ensure', return_value=self.runtime), patch.object(manager.rea, 'probe', side_effect=user_edit):
            result = manager.dispatch('inject', {'provider': 'codex', 'profile': 'builtin'})
        self.assertFalse(result['ok'])
        self.assertEqual(adapter.path.read_bytes(), updated)
        self.assertFalse((adapter.path.parent / 'AGENTS.md').exists())


if __name__ == '__main__':
    unittest.main()
