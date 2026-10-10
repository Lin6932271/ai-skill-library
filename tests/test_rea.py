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
from rea_runtime import ReaRuntime, validate_tool_schemas


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

    def test_current_runtime_detection_and_upgrade_status(self):
        manager = SkillManager(self.home / 'data', self.home, use_env=False)
        manifest = manager.rea.manifest
        current = dict(self.runtime, root=str(self.home / ('rea-' + manifest['rea_version'] + '-' + manifest['sha256'][:12])))
        self.assertTrue(manager.rea.is_current(current))
        self.assertFalse(manager.rea.is_current(self.runtime))
        with patch.object(manager.rea, 'ensure', return_value=self.runtime), patch.object(manager.rea, 'probe', return_value={'ok':True}):
            manager.inject('deepseek', 'builtin')
        provider = next(p for p in manager.status()['providers'] if p['key'] == 'deepseek')
        self.assertTrue(provider['rea_needs_update'])
        self.assertIn('更新 REA', provider['verification']['summary'])

    def test_schema_preflight_rejects_reported_and_lookahead_patterns(self):
        for pattern in (r'^[^\0]*$', r'^(?!reserved)[a-z]+$', r'^[^\s[\]]+$'):
            with self.assertRaises(ReaError):
                validate_tool_schemas([{'inputSchema': {'type':'string', 'pattern':pattern}}])
        self.assertEqual(validate_tool_schemas([{'inputSchema': {'type':'string', 'pattern':r'^[^\x00]*$'}}]), 1)

    def test_schema_preflight_accepts_explicit_bracket_literals(self):
        for pattern in (r'^[^\s\x5b\x5d]+$', r'^[^\s\[\]]+$', r'^\[[a-z]+\]$'):
            self.assertEqual(validate_tool_schemas([{'inputSchema':{'type':'string','pattern':pattern}}]),1)

    def test_previous_patched_runtime_is_recoverable_only_when_unchanged(self):
        manager = SkillManager(self.home / 'data', self.home, use_env=False)
        previous_hash = sha(b'previous trusted runtime')
        root = manager.data_dir / 'rea' / ('rea-6.1.0-' + previous_hash[:12])
        files = {'node/node.exe':b'original node',
                 'cli/node_modules/rea-agents/scripts/rea.mjs':b'original entry'}
        for name,data in files.items():
            (root/name).parent.mkdir(parents=True,exist_ok=True)
            (root/name).write_bytes(data)
        (root/'.ready.json').write_text(json.dumps({'archive_sha256':previous_hash}),encoding='utf-8')
        manager.rea.manifest = {'rea_version':'6.1.0','sha256':sha(b'current runtime'),
                               'previous_runtimes':[{'rea_version':'6.1.0','sha256':previous_hash,
                                                    'critical_files':{name:sha(data) for name,data in files.items()}}]}
        launch = {'command':str(root/'node/node.exe'),
                  'args':[str(root/'cli/node_modules/rea-agents/scripts/rea.mjs'),'mcp']}
        self.assertIsNotNone(manager.rea.owned_runtime(launch))
        (root/'node/node.exe').write_bytes(b'externally modified')
        self.assertIsNone(manager.rea.owned_runtime(launch))

    def test_schema_preflight_ignores_property_names_and_example_values(self):
        schema = {'type':'object', 'properties': {'pattern': {'type':'string'},
                  'value': {'type':'string', 'pattern':r'^[^\x00]*$'}},
                  'examples': [{'pattern':r'\0'}], 'default': {'pattern':r'\0'}}
        self.assertEqual(validate_tool_schemas([{'inputSchema':schema}]), 1)

    def test_missing_record_recovery_preserves_other_plugins_and_revoke(self):
        manager = SkillManager(self.home / 'data', self.home, use_env=False)
        adapter = self.adapter('deepseek')
        adapter.path.parent.mkdir(parents=True)
        original = self.original('deepseek')
        adapter.path.write_bytes(original)
        with patch.object(manager.rea, 'ensure', return_value=self.runtime), patch.object(manager.rea, 'probe', return_value={'ok':True}), patch.object(manager.rea, 'owned_runtime', return_value=self.runtime):
            manager.inject('deepseek', 'builtin')
            manager.state['installed'].clear()
            manager.save()
            self.assertTrue(next(p for p in manager.status()['providers'] if p['key']=='deepseek')['rea_recovery_available'])
            manager.repair_rea('deepseek', 'builtin')
            self.assertTrue(manager.revoke('deepseek')['removed'])
        self.assertIn(b'!!js', adapter.path.read_bytes())
        self.assertIn(b'custom-plugin', adapter.path.read_bytes())
        self.assertIsNone(adapter.entry(adapter.parse(adapter.path.read_bytes())))

    def test_recovery_rejects_changed_skills_and_external_registration(self):
        manager = SkillManager(self.home / 'data', self.home, use_env=False)
        with patch.object(manager.rea, 'ensure', return_value=self.runtime), patch.object(manager.rea, 'probe', return_value={'ok':True}), patch.object(manager.rea, 'owned_runtime', return_value=self.runtime):
            manager.inject('deepseek', 'builtin')
            manager.state['installed'].clear()
            adapter = self.adapter('deepseek')
            original = adapter.path.read_bytes()
            (manager.root('deepseek') / 'skills/pojia-local/SKILL.md').write_bytes(b'user edits')
            with self.assertRaises(LocalError):
                manager.repair_rea('deepseek')
            self.assertEqual(adapter.path.read_bytes(), original)
        with patch.object(manager.rea, 'owned_runtime', return_value=None):
            self.assertIsNone(manager.recoverable_rea('deepseek'))

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
