"""Reproduce static release checks and an optional isolated native observation.

Use Python 3.14 and requirements-audit.txt. The static check reads code objects;
it does not execute extracted Python or any imported skill resources.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.metadata
import ipaddress
import json
import marshal
import os
import platform
import subprocess
import sys
import sysconfig
import time
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pefile
import psutil
import PyInstaller
from PyInstaller.archive.readers import CArchiveReader


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def code_shape(value):
    if isinstance(value, types.CodeType):
        fields = ['co_name', 'co_qualname', 'co_argcount', 'co_posonlyargcount',
                  'co_kwonlyargcount', 'co_nlocals', 'co_stacksize', 'co_flags',
                  'co_code', 'co_consts', 'co_names', 'co_varnames', 'co_freevars',
                  'co_cellvars', 'co_exceptiontable', 'co_firstlineno', 'co_linetable']
        return {'code': {name: code_shape(getattr(value, name)) for name in fields}}
    if isinstance(value, bytes):
        return {'bytes': value.hex()}
    if isinstance(value, tuple):
        return {'tuple': [code_shape(item) for item in value]}
    if isinstance(value, frozenset):
        return {'frozenset': sorted((code_shape(item) for item in value), key=repr)}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return {'type': type(value).__name__, 'repr': repr(value)}


def compare_code(packed, path):
    source = path.read_bytes()
    expected = compile(source, packed.co_filename, 'exec', dont_inherit=True, optimize=0)
    left = json.dumps(code_shape(packed), ensure_ascii=True, sort_keys=True).encode()
    right = json.dumps(code_shape(expected), ensure_ascii=True, sort_keys=True).encode()
    return {'file': path.name, 'source_sha256': sha(source),
            'packed_code_sha256': sha(left), 'compiled_source_code_sha256': sha(right),
            'matches': left == right,
            'method': 'recursive code-object fields including bytecode/constants/import names/line tables; filename excluded'}


def qualified_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return qualified_name(node.value) + '.' + node.attr
    return '<expression>'


def static_checks(exe, source, output, native_reference_dirs=()):
    packed = CArchiveReader(str(exe))
    pyz_name = next(name for name in packed.toc if name.endswith('.pyz'))
    pyz = packed.open_embedded_archive(pyz_name)
    core = [compare_code(marshal.loads(packed.extract('main')), source / 'main.py'),
            compare_code(pyz.extract('backend'), source / 'backend.py')]
    assert all(row['matches'] for row in core), 'Packed application code differs from supplied source'

    manifest = []
    assets = []
    scripts = []
    stock_root = Path(PyInstaller.__file__).parent
    for name, info in sorted(packed.toc.items()):
        data = packed.extract(name)
        normalized = name.replace('\\', '/')
        item = {'name': normalized, 'type': info[-1], 'bytes': len(data), 'sha256': sha(data)}
        manifest.append(item)
        if normalized.startswith(('frontend/', 'skills/')):
            path = source / normalized
            assets.append({**item, 'matches_source': path.is_file() and data == path.read_bytes()})
        if info[-1] in ('s', 'm') and name != 'main':
            if name.startswith(('pyimod', 'pyiboot')):
                reference = stock_root / 'loader' / (name + '.py')
            elif name.startswith('pyi_rth_'):
                reference = stock_root / 'hooks' / 'rthooks' / (name + '.py')
            elif name == 'struct':
                reference = Path(sysconfig.get_path('stdlib')) / 'struct.py'
            else:
                reference = None
            scripts.append({'name': name, 'reference_available': bool(reference and reference.is_file()),
                            **(compare_code(marshal.loads(data), reference) if reference and reference.is_file() else {})})
    assert assets and all(item['matches_source'] for item in assets)
    write_json(output / 'archive-members.json', manifest)
    write_json(output / 'bundled-resource-comparison.json', assets)
    write_json(output / 'packed-python-comparison.json', {'application': core, 'bootstrap_and_hooks': scripts})
    write_json(output / 'pyz-module-index.json', sorted(pyz.toc))

    image = pefile.PE(str(exe))
    stock = pefile.PE(str(stock_root / 'bootloader' / 'Windows-64bit-intel' / 'runw.exe'))
    stock_sections = {section.Name.rstrip(b'\0').decode(): section.get_data() for section in stock.sections}
    sections = [{'name': section.Name.rstrip(b'\0').decode(), 'bytes': len(section.get_data()),
                 'sha256': sha(section.get_data()),
                 'matches_installed_bootloader': section.get_data() == stock_sections.get(section.Name.rstrip(b'\0').decode())}
                for section in image.sections]
    imports = [{'dll': library.dll.decode(), 'function': symbol.name.decode() if symbol.name else 'ordinal:' + str(symbol.ordinal)}
               for library in getattr(image, 'DIRECTORY_ENTRY_IMPORT', []) for symbol in library.imports]
    rdata = next(section for section in image.sections if section.Name.rstrip(b'\0') == b'.rdata')
    stock_rdata = next(section for section in stock.sections if section.Name.rstrip(b'\0') == b'.rdata')
    normalized_rdata = bytearray(rdata.get_data())
    normalized_stock_rdata = bytearray(stock_rdata.get_data())
    timestamp_offsets = []
    for debug in getattr(image, 'DIRECTORY_ENTRY_DEBUG', []):
        offset = debug.struct.get_file_offset() + debug.struct.get_field_relative_offset('TimeDateStamp') - rdata.PointerToRawData
        if 0 <= offset <= len(normalized_rdata) - 4:
            normalized_rdata[offset:offset + 4] = b'\0' * 4
            timestamp_offsets.append(offset)
    for debug in getattr(stock, 'DIRECTORY_ENTRY_DEBUG', []):
        offset = debug.struct.get_file_offset() + debug.struct.get_field_relative_offset('TimeDateStamp') - stock_rdata.PointerToRawData
        if 0 <= offset <= len(normalized_stock_rdata) - 4:
            normalized_stock_rdata[offset:offset + 4] = b'\0' * 4
    native_comparison = []
    for member in manifest:
        name = member['name']
        if Path(name).suffix.lower() not in ('.dll', '.pyd'):
            continue
        locations = [('python-environment', Path(sys.prefix) / name),
                     ('python-installation', Path(sys.base_prefix) / name),
                     ('python-dlls', Path(sys.base_prefix) / 'DLLs' / name),
                     ('installed-package', Path(sysconfig.get_path('purelib')) / name),
                     ('windows-system32', Path(os.environ.get('WINDIR', 'C:/Windows')) / 'System32' / name),
                     ('windows-downlevel', Path(os.environ.get('WINDIR', 'C:/Windows')) / 'System32' / 'downlevel' / name)]
        locations.extend(('build-native-runtime-reference', Path(folder) / Path(name).name)
                         for folder in native_reference_dirs)
        references = [{'category': category, 'sha256': sha(path.read_bytes())}
                      for category, path in locations if path.is_file()]
        matching = [item for item in references if item['sha256'] == member['sha256']]
        native_comparison.append({'name': name, 'sha256': member['sha256'],
                                  'matches_installed_reference': bool(matching),
                                  'matched_reference_categories': sorted({item['category'] for item in matching}),
                                  'reference_available': bool(references)})
    write_json(output / 'native-library-comparison.json', native_comparison)
    with (output / 'pe-imports.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['dll', 'function'])
        writer.writeheader()
        writer.writerows(imports)
    manifests = []
    for kind in getattr(image, 'DIRECTORY_ENTRY_RESOURCE', type('Empty', (), {'entries': []})()).entries:
        if kind.id == 24:
            for entry in kind.directory.entries:
                for lang in entry.directory.entries:
                    resource = lang.data.struct
                    manifests.append(image.get_data(resource.OffsetToData, resource.Size).decode('utf-8', 'replace'))
    security = image.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']]
    pe = {'machine': hex(image.FILE_HEADER.Machine), 'subsystem': image.OPTIONAL_HEADER.Subsystem,
          'authenticode_certificate_bytes': security.Size, 'sections': sections,
          'requested_execution_level': 'asInvoker' if any('asInvoker' in text for text in manifests) else 'not-confirmed',
          'import_count': len(imports), 'embedded_manifest': manifests,
          'rdata_matches_after_debug_timestamp_normalization': normalized_rdata == normalized_stock_rdata,
          'debug_timestamp_offsets_in_rdata': timestamp_offsets,
          'resource_type_ids': [kind.id for kind in getattr(image, 'DIRECTORY_ENTRY_RESOURCE', type('Empty', (), {'entries': []})()).entries],
          'bootloader_reference': 'PyInstaller ' + PyInstaller.__version__ + ' stock Windows-64bit-intel/runw.exe'}
    write_json(output / 'pe-analysis.json', pe)

    calls = []
    imports_own = []
    for name in ['main.py', 'backend.py']:
        tree = ast.parse((source / name).read_text('utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                calls.append({'file': name, 'line': node.lineno, 'call': qualified_name(node.func)})
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports_own.append({'file': name, 'line': node.lineno,
                                    'module': node.module if isinstance(node, ast.ImportFrom) else ','.join(alias.name for alias in node.names)})
    write_json(output / 'application-call-index.json', calls)
    write_json(output / 'application-import-index.json', imports_own)
    bandit = subprocess.run([sys.executable, '-m', 'bandit', str(source / 'main.py'), str(source / 'backend.py'),
                             '-f', 'json', '-q'], capture_output=True, encoding='utf-8', timeout=45)
    assert bandit.returncode in (0, 1), 'Bandit could not complete'
    findings = json.loads(bandit.stdout)
    # Publish repository-relative filenames rather than local user/workspace paths.
    findings['metrics'] = {Path(name).name if name != '_totals' else name: value for name, value in findings['metrics'].items()}
    for finding in findings['results']:
        finding['filename'] = Path(finding['filename']).name
    write_json(output / 'bandit.json', findings)
    return {'application_code_matches_source': True, 'application_modules': core,
            'bootstrap_hook_checks': scripts, 'archive_entries': len(manifest),
            'pyz_modules': len(pyz.toc), 'bundled_resources_checked': len(assets),
            'all_bundled_resources_match': True, 'pe': pe,
            'native_library_comparison': {'checked': len(native_comparison),
                                          'matching': sum(item['matches_installed_reference'] for item in native_comparison),
                                          'unmatched': [item['name'] for item in native_comparison if not item['matches_installed_reference']]},
            'bandit': {'version': importlib.metadata.version('bandit'),
                       'results': findings['results'], 'errors': findings['errors'],
                       'metrics': findings['metrics']['_totals']}}


def persistence_snapshot():
    import winreg
    values = {}
    for hive_name, hive in [('HKCU', winreg.HKEY_CURRENT_USER), ('HKLM', winreg.HKEY_LOCAL_MACHINE)]:
        for view_name, view in [('64', winreg.KEY_WOW64_64KEY), ('32', winreg.KEY_WOW64_32KEY)]:
            for name in ['Run', 'RunOnce']:
                key_name = hive_name + ':' + view_name + ':' + name
                try:
                    with winreg.OpenKey(hive, 'Software\\Microsoft\\Windows\\CurrentVersion\\' + name,
                                        0, winreg.KEY_READ | view) as key:
                        entries = []
                        for index in range(winreg.QueryInfoKey(key)[1]):
                            entries.append(winreg.EnumValue(key, index))
                        values[key_name] = sha(json.dumps(sorted(entries), default=repr).encode())
                except FileNotFoundError:
                    values[key_name] = 'missing'
                except PermissionError:
                    values[key_name] = 'unreadable'
    startup_locations = [Path(os.environ['APPDATA']) / 'Microsoft/Windows/Start Menu/Programs/Startup',
                         Path(os.environ['PROGRAMDATA']) / 'Microsoft/Windows/Start Menu/Programs/Startup']
    for number, folder in enumerate(startup_locations):
        values['startup-folder-' + str(number)] = sha(json.dumps(sorted(
            (item.name, item.stat().st_size, item.stat().st_mtime_ns) for item in folder.iterdir()), default=repr).encode()) if folder.is_dir() else 'missing'
    values['service-names'] = sha(json.dumps(sorted(service.name() for service in psutil.win_service_iter())).encode())
    tasks = subprocess.run(['powershell', '-NoProfile', '-Command',
                            'Get-ScheduledTask | Sort-Object TaskPath,TaskName | Select-Object TaskPath,TaskName,Actions | ConvertTo-Json -Depth 6 -Compress'],
                           capture_output=True, timeout=20)
    values['scheduled-task-definitions'] = sha(tasks.stdout) if tasks.returncode == 0 else 'unreadable'
    return values


def observe(exe, output):
    sandbox = output / 'native-sandbox'
    sandbox.mkdir(parents=True, exist_ok=True)
    smoke = sandbox / 'native.json'
    started_at = time.time()
    before = persistence_snapshot()
    process = subprocess.Popen([str(exe), '--sandbox', '--home', str(sandbox / 'home'),
                                '--data-dir', str(sandbox / 'data'), '--smoke-file', str(smoke)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    root = psutil.Process(process.pid)
    identities = {process.pid: root.create_time()}
    names = {}
    connections = set()
    errors = 0
    samples = 0
    interval_times = []
    previous_sample = None
    start = time.monotonic()
    while time.monotonic() - start < 55:
        now = time.monotonic()
        if previous_sample is not None:
            interval_times.append(now - previous_sample)
        previous_sample = now
        try:
            candidates = [root, *root.children(recursive=True)]
        except psutil.NoSuchProcess:
            candidates = []
        for item in candidates:
            try:
                identities[item.pid] = item.create_time()
                names[item.pid] = item.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        try:
            for connection in psutil.net_connections(kind='inet'):
                if connection.pid not in identities:
                    continue
                local = tuple(connection.laddr) if connection.laddr else ()
                remote = tuple(connection.raddr) if connection.raddr else ()
                connections.add((names.get(connection.pid, 'unknown'), local, remote, str(connection.status)))
            samples += 1
        except psutil.AccessDenied:
            errors += 1
        if process.poll() is not None:
            break
        time.sleep(.1)
    duration = time.monotonic() - start
    closed_naturally = process.poll() is not None
    if not closed_naturally:
        for pid, created in identities.items():
            try:
                item = psutil.Process(pid)
                if item.create_time() == created:
                    item.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        raise RuntimeError('Isolated native acceptance did not finish')
    after = persistence_snapshot()
    assert smoke.is_file() and smoke.stat().st_mtime >= started_at
    native = json.loads(smoke.read_text('utf-8'))
    sockets = [{'process': name, 'local': list(local), 'remote': list(remote), 'status': state,
                'external_remote': bool(remote and not ipaddress.ip_address(remote[0]).is_loopback)}
               for name, local, remote, state in sorted(connections, key=repr)]
    result = {'native_acceptance_pass': native['pass'], 'closed_naturally': True,
              'process_names': sorted(set(names.values())), 'observed_process_count': len(names),
              'duration_seconds': round(duration, 3), 'requested_sampling_interval_seconds': .1,
              'mean_sampling_interval_seconds': round(sum(interval_times) / len(interval_times), 3) if interval_times else None,
              'successful_socket_samples': samples, 'socket_sampling_errors': errors,
              'connections': sockets, 'external_remote_connections_observed': sum(row['external_remote'] for row in sockets),
              'persistence_snapshots': {key: {'available': before[key] != 'unreadable' and after[key] != 'unreadable',
                                             'unchanged': before[key] == after[key]} for key in before},
              'scope': 'isolated native startup, automatic animation completion, main UI rendering and page scroll; sampled TCP/UDP tables, not packet capture',
              'isolation': 'explicit temporary home/data paths and --sandbox; no real AI client installs'}
    write_json(output / 'native-observation.json', result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--out', type=Path, default=Path('artifacts/security-audit'))
    parser.add_argument('--observe', action='store_true', help='run an isolated native startup observation on Windows')
    parser.add_argument('--native-reference-dir', type=Path, action='append', default=[],
                        help='optional build-time native runtime directory used for reference hashes')
    args = parser.parse_args()
    exe, source, output = args.exe.resolve(), args.source.resolve(), args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    before_hash = sha(exe.read_bytes())
    result = {'name': 'ai技能库', 'version': '1.3.2', 'exe_filename': exe.name,
              'exe_bytes': exe.stat().st_size, 'exe_sha256': before_hash,
              'examined_at': datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
              'python': platform.python_version(), 'platform': platform.platform(),
              'tools': {name: importlib.metadata.version(name) for name in ['pyinstaller', 'pefile', 'psutil', 'bandit']}}
    result['static'] = static_checks(exe, source, output, args.native_reference_dir)
    print(json.dumps({'stage': 'static-complete', 'core_matches': True,
                      'archive_entries': result['static']['archive_entries'],
                      'resource_matches': result['static']['bundled_resources_checked']}, ensure_ascii=False), flush=True)
    if args.observe:
        result['runtime'] = observe(exe, output)
        print(json.dumps({'stage': 'runtime-complete', 'native_pass': result['runtime']['native_acceptance_pass'],
                          'external_connections_observed': result['runtime']['external_remote_connections_observed']}, ensure_ascii=False), flush=True)
    result['sample_unchanged_after_analysis'] = sha(exe.read_bytes()) == before_hash
    assert result['sample_unchanged_after_analysis']
    write_json(output / 'audit-summary.json', result)


if __name__ == '__main__':
    main()
