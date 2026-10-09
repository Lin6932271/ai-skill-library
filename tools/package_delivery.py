"""Package only explicit source/evidence paths after final EXE acceptance passes."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT.parent / 'delivery'
LOGS = ROOT.parent / 'rea-deployment-20261009'
VERSION = '1.4.0'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def add_folder(archive, folder, prefix):
    for path in sorted(folder.rglob('*')):
        if any(part in ('__pycache__', '.pytest_cache', '.venv', 'node_modules') for part in path.relative_to(folder).parts):
            continue
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError(f'Unexpected linked source: {path}')
        if path.is_file() and path.suffix != '.pyc':
            archive.write(path, prefix + '/' + path.relative_to(folder).as_posix())


def build():
    original_sha256 = digest(DELIVERY / 'ai技能库-1.3.2.exe')
    ui = json.loads((ROOT / 'artifacts/acceptance/exe-browser-result.json').read_text('utf-8'))
    native = json.loads((ROOT / 'artifacts/rea-native.json').read_text('utf-8'))
    real = json.loads((ROOT / 'artifacts/rea-acceptance/result.json').read_text('utf-8'))
    assert ui['pass'] and ui['one_click_rea_upgrade_action'] and ui['rea_after_app_exit']['passed']
    assert native['pass'] and real['passed'] and len(real['matrix']) == 7
    tests = (LOGS / 'app-tests.log').read_text('utf-8-sig', errors='replace')
    assert 'Ran 33 tests' in tests and tests.rstrip().endswith('OK')
    manifest = json.loads((ROOT / 'runtime/manifest.json').read_text('utf-8'))
    assert digest(ROOT / 'runtime' / manifest['archive']) == manifest['sha256']
    DELIVERY.mkdir(exist_ok=True)
    history = DELIVERY / 'history'
    history.mkdir(exist_ok=True)
    for name in ('ai技能库.exe', 'ai技能库-源码.zip', '使用说明.md', 'NOTICE.md', 'SHA256SUMS.txt'):
        old = DELIVERY / name
        preserved = history / ('before-1.4.0-' + name)
        if old.is_file() and not preserved.exists():
            shutil.copy2(old, preserved)
    exe = DELIVERY / f'ai技能库-{VERSION}.exe'
    built_exe = ROOT / 'dist/AISkillLibrary.exe'
    if not exe.is_file() or digest(exe) != digest(built_exe):
        shutil.copy2(built_exe, exe)
    alias_exe = DELIVERY / 'ai技能库.exe'
    if not alias_exe.is_file() or digest(alias_exe) != digest(exe):
        shutil.copy2(exe, alias_exe)
    shutil.copy2(ROOT / 'docs/USAGE.md', DELIVERY / '使用说明.md')
    shutil.copy2(ROOT / 'NOTICE.md', DELIVERY / 'NOTICE.md')
    shutil.copy2(ROOT / 'docs/REA_INTEGRATION.md', DELIVERY / f'REA更新与验收-{VERSION}.md')
    files = [exe, DELIVERY / f'REA更新与验收-{VERSION}.md']
    portable = DELIVERY / f'AISkillLibrary-{VERSION}-windows-x64.zip'
    with zipfile.ZipFile(portable, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(exe, 'ai技能库.exe')
        archive.write(ROOT / 'docs/USAGE.md', '使用说明.md')
        archive.write(ROOT / 'NOTICE.md', 'NOTICE.md')
        archive.write(ROOT / 'docs/REA_INTEGRATION.md', 'REA更新与验收.md')
        with zipfile.ZipFile(ROOT / 'runtime' / manifest['archive']) as runtime:
            for name in manifest['license_paths']:
                archive.writestr('licenses/' + name.replace('/', '-'), runtime.read(name))
    files.append(portable)
    shutil.copy2(ROOT / 'artifacts/acceptance/exe-console-light.png', ROOT / 'docs/images/console.png')
    source = DELIVERY / f'AISkillLibrary-{VERSION}-source.zip'
    with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in ('.gitattributes', '.gitignore', 'AISkillLibrary.spec', 'backend.py', 'main.py', 'rea_config.py',
                     'rea_runtime.py', 'build.ps1', 'generate_extensions.py', 'NOTICE.md', 'README.md',
                     'requirements.txt', 'requirements-dev.txt', 'requirements-audit.txt', 'version_info.txt'):
            archive.write(ROOT / name, 'ai技能库-源码/' + name)
        for name in ('frontend', 'skills', 'runtime', 'docs', 'tests', 'tools'):
            add_folder(archive, ROOT / name, 'ai技能库-源码/' + name)
    shutil.copy2(source, DELIVERY / 'ai技能库-源码.zip')
    files.append(source)
    evidence = DELIVERY / f'AISkillLibrary-{VERSION}-evidence.zip'
    with zipfile.ZipFile(evidence, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in ('acceptance', 'rea-acceptance'):
            add_folder(archive, ROOT / 'artifacts' / name, name)
        for name in ('rea-native.json', 'rea-native.png', 'rea-native-startup.png'):
            archive.write(ROOT / 'artifacts' / name, name)
        for name in ('app-tests.log', 'app-build.log', 'exe-browser.log', 'rea-real-acceptance.log'):
            archive.write(LOGS / name, 'logs/' + name)
        archive.write(ROOT / 'runtime/manifest.json', 'runtime-manifest.json')
        archive.write(ROOT / 'docs/REA_INTEGRATION.md', 'REA更新与验收.md')
    files.append(evidence)
    for path in (portable, source, evidence):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, str(path)
    lines = '\n'.join(digest(path) + '  ' + path.name for path in files) + '\n'
    (DELIVERY / f'AISkillLibrary-{VERSION}-SHA256SUMS.txt').write_text(lines, encoding='utf-8')
    aliases = [DELIVERY / 'ai技能库.exe', DELIVERY / 'ai技能库-源码.zip', DELIVERY / 'ai技能库-1.3.2.exe']
    (DELIVERY / 'SHA256SUMS.txt').write_text(lines + ''.join(digest(path) + '  ' + path.name + '\n' for path in aliases), encoding='utf-8')
    assert digest(DELIVERY / 'ai技能库-1.3.2.exe') == original_sha256
    summary = {'version':VERSION, 'passed':True, 'original_1_3_2_retained':True, 'original_1_3_2_sha256': original_sha256,
        'files':[{'name':p.name, 'bytes':p.stat().st_size, 'sha256':digest(p)} for p in files],
        'unit_tests':33, 'configuration_matrix':7, 'mcp_tools':138, 'actual_agent_client_loaded':False,
        'published_remotely':False}
    (DELIVERY / f'verification-{VERSION}.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    build()
