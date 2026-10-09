"""Package accepted artifacts for the current version, preserving prior releases."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import VERSION


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def add_folder(archive, folder, prefix):
    for path in sorted(folder.rglob('*')):
        if any(part in ('__pycache__', '.pytest_cache', '.venv', 'node_modules') for part in path.relative_to(folder).parts):
            continue
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError('Unexpected linked source: ' + str(path))
        if path.is_file() and path.suffix != '.pyc':
            archive.write(path, prefix + '/' + path.relative_to(folder).as_posix())


def sanitize(data):
    text = data.decode('utf-8-sig', errors='replace')
    for location, marker in ((str(ROOT.parent), '<workspace>'), (str(Path.home()), '<user-home>')):
        for form in (location.replace('\\', '\\\\'), location, location.replace('\\', '/')):
            text = text.replace(form, marker)
    return text.encode('utf-8')


def main(logs):
    delivery = ROOT.parent / 'delivery'
    out = ROOT.parent / 'github-upload/release' / ('v' + VERSION)
    out.mkdir(parents=True, exist_ok=True)
    ui = json.loads((ROOT / 'artifacts/acceptance/exe-browser-result.json').read_text('utf-8'))
    real = json.loads((ROOT / 'artifacts/rea-acceptance/result.json').read_text('utf-8'))
    schema = json.loads((logs / 'schema-regression.json').read_text('utf-8'))
    assert ui['pass'] and ui['app_version'] == VERSION and ui['orphan_deepseek_repair_preserves_plugins']
    assert real['passed'] and len(real['matrix']) == 7 and schema['passed']
    tests = (logs / 'unit-tests.log').read_text('utf-8-sig')
    assert tests.rstrip().endswith('OK')
    unit_count = int(re.search(r'Ran (\d+) tests', tests).group(1))
    manifest = json.loads((ROOT / 'runtime/manifest.json').read_text('utf-8'))
    assert digest(ROOT / 'runtime' / manifest['archive']) == manifest['sha256']
    exe = out / f'AISkillLibrary-{VERSION}-windows-x64.exe'
    shutil.copy2(ROOT / 'dist/AISkillLibrary.exe', exe)
    shutil.copy2(exe, delivery / f'ai技能库-{VERSION}.exe')
    notes = out / f'AISkillLibrary-{VERSION}-rea-verification.md'
    shutil.copy2(ROOT / 'docs/REA_COMPATIBILITY.md', notes)
    portable = out / f'AISkillLibrary-{VERSION}-windows-x64.zip'
    with zipfile.ZipFile(portable, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(exe, 'ai技能库.exe')
        archive.write(ROOT / 'docs/USAGE.md', '使用说明.md')
        archive.write(ROOT / 'NOTICE.md', 'NOTICE.md')
        archive.write(notes, 'DeepSeek修复与恢复.md')
        with zipfile.ZipFile(ROOT / 'runtime' / manifest['archive']) as runtime:
            for name in manifest['license_paths']:
                archive.writestr('licenses/' + name.replace('/', '-'), runtime.read(name))
    shutil.copy2(ROOT / 'artifacts/acceptance/exe-console-light.png', ROOT / 'docs/images/console.png')
    source = out / f'AISkillLibrary-{VERSION}-source.zip'
    with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in ('.gitattributes', '.gitignore', 'AISkillLibrary.spec', 'backend.py', 'main.py', 'rea_config.py',
                     'rea_runtime.py', 'build.ps1', 'generate_extensions.py', 'NOTICE.md', 'README.md',
                     'requirements.txt', 'requirements-dev.txt', 'requirements-audit.txt', 'version_info.txt'):
            archive.write(ROOT / name, 'ai技能库-源码/' + name)
        for name in ('frontend', 'skills', 'runtime', 'docs', 'tests', 'tools'):
            add_folder(archive, ROOT / name, 'ai技能库-源码/' + name)
    evidence = out / f'AISkillLibrary-{VERSION}-evidence.zip'
    evidence_paths = [*logs.glob('*.log'), logs / 'schema-regression.json',
        ROOT / 'artifacts/acceptance/exe-browser-result.json', ROOT / 'artifacts/acceptance/patched-tool-schemas.json',
        ROOT / 'artifacts/rea-acceptance/result.json', ROOT / 'artifacts/rea-acceptance/analysis.json']
    with zipfile.ZipFile(evidence, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in evidence_paths:
            assert path.is_file(), str(path)
            archive.writestr(path.name, sanitize(path.read_bytes()))
        for path in (ROOT / 'artifacts/acceptance').glob('exe-*.png'):
            archive.write(path, 'images/' + path.name)
        archive.write(ROOT / 'runtime/manifest.json', 'runtime-manifest.json')
        archive.write(notes, '修复说明.md')
    files = [exe, portable, source, evidence, notes]
    for path in (portable, source, evidence):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
    assets = [{'name':p.name, 'bytes':p.stat().st_size, 'sha256':digest(p)} for p in files]
    sums = out / 'SHA256SUMS.txt'
    sums.write_text(''.join(a['sha256'] + '  ' + a['name'] + '\n' for a in assets), encoding='utf-8')
    assets.append({'name':sums.name, 'bytes':sums.stat().st_size, 'sha256':digest(sums)})
    result = {'version':VERSION, 'repo':'Lin6932271/ai-skill-library', 'unit_tests':unit_count,
              'configuration_matrix':7, 'mcp_tools':138, 'schema_patterns':schema['patterns'],
              'deepseek_official_api_chat_verified':False, 'assets':assets, 'published_remotely':False}
    (out / 'preparation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    for path in (portable, source, evidence, notes):
        shutil.copy2(path, delivery / path.name)
    shutil.copy2(sums, delivery / f'AISkillLibrary-{VERSION}-SHA256SUMS.txt')
    (delivery / f'verification-{VERSION}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-dir', required=True, type=Path)
    main(parser.parse_args().log_dir)
