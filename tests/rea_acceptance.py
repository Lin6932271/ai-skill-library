"""Real offline installation and MCP analysis in an isolated, non-ASCII home."""
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import SkillManager, PROVIDERS
from rea_config import McpConfig


def run():
    output = ROOT / 'artifacts/rea-acceptance'
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='rea-offline-') as temporary:
        sandbox = Path(temporary) / '新用户 空格目录'
        manager = SkillManager(sandbox / 'data', sandbox / 'home', use_env=False)
        stop = threading.Event()
        def monitor():
            previous = None
            while not stop.wait(2):
                current = manager.rea.progress_status()
                if current != previous:
                    print(json.dumps(current, ensure_ascii=False), flush=True)
                    previous = current
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        matrix = []
        try:
            with patch('socket.socket', side_effect=AssertionError('Python network access prohibited during injection')):
                for provider in PROVIDERS:
                    before = time.monotonic()
                    result = manager.inject(provider, 'builtin')
                    assert result['verification']['ok'], result['verification']['summary']
                    matrix.append({'provider':provider, 'configuration_valid': True,
                                   'cli_mcp_probe': manager.state['installed'][provider]['rea']['probe'],
                                   'seconds': round(time.monotonic() - before, 2)})
                    print(json.dumps(matrix[-1], ensure_ascii=False), flush=True)
            fixture = sandbox / 'sample'
            fixture.mkdir()
            (fixture / 'main.js').write_text('import {normalize} from "./search.js"; export const search = x => normalize(x);', encoding='utf-8')
            (fixture / 'search.js').write_text('export const normalize = x => String(x).toLowerCase();', encoding='utf-8')
            runtime = manager.state['installed']['codex']['rea']['runtime']
            analysis = manager.rea.probe(runtime, fixture)
            encoded = json.dumps(analysis['analysis'])
            assert 'main.js' in encoded and 'search.js' in encoded
            (output / 'analysis.json').write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding='utf-8')
            for provider in PROVIDERS:
                result = manager.revoke(provider)
                assert result['removed'], result
                adapter = McpConfig(provider, manager.root(provider), manager.home)
                assert not adapter.path.exists(), str(adapter.path)
            assert manager.rea.ready(runtime), 'Shared runtime must survive revocation'
            evidence = {'passed':True, 'matrix':matrix, 'python_network_disabled_during_injection':True,
                'non_ascii_path':True, 'mcp_sample_analysis':True, 'exact_config_restore':True,
                'shared_runtime_retained':True, 'actual_agent_client_loaded':False,
                'seconds':round(time.monotonic()-started,2)}
            (output / 'result.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(evidence, ensure_ascii=False), flush=True)
        finally:
            stop.set()
            thread.join(timeout=3)

if __name__ == '__main__':
    run()
