"""Package a verified local upgrade without publishing or changing client settings."""
import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(ROOT))
from backend import VERSION, SkillManager

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def add_folder(archive, folder, prefix):
    for path in sorted(folder.rglob('*')):
        relative = path.relative_to(folder)
        if any(part in ('__pycache__', '.pytest_cache', '.venv', 'node_modules') for part in relative.parts):
            continue
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError(f'Unexpected linked source: {path}')
        if path.is_file() and path.suffix != '.pyc':
            archive.write(path, prefix + '/' + relative.as_posix())

def main(evidence):
    delivery = ROOT.parent / 'delivery'
    inputs = {name: json.loads((evidence / name).read_text('utf-8'))
              for name in ('packaged-verification.json', 'unit-test-result.json', 'exe-native/result.json', 'exe-api/result.json', 'exe-ui/result.json')}
    assert all(result['pass'] for result in inputs.values())
    static = inputs['packaged-verification.json']
    api = inputs['exe-api/result.json']
    ui = inputs['exe-ui/result.json']
    assert static['version'] == api['version'] == VERSION
    exe = delivery / f'ai技能库-{VERSION}.exe'
    assert digest(exe) == static['exe_sha256'] == digest(ROOT / 'dist/AISkillLibrary.exe')
    runtime = json.loads((ROOT / 'runtime/manifest.json').read_text('utf-8'))
    assert digest(ROOT / 'runtime' / runtime['archive']) == runtime['sha256']
    backups = evidence / 'delivery-before-upgrade'
    backups.mkdir(exist_ok=True)
    for name in ('ai技能库.exe', 'ai技能库-源码.zip', '使用说明.md', 'NOTICE.md', 'SHA256SUMS.txt'):
        previous = delivery / name
        preserved = backups / name
        if previous.is_file() and not preserved.exists():
            shutil.copy2(previous, preserved)
    shutil.copy2(exe, delivery / 'ai技能库.exe')
    shutil.copy2(ROOT / 'NOTICE.md', delivery / 'NOTICE.md')
    shutil.copy2(ROOT / 'docs/USAGE.md', delivery / '使用说明.md')
    notes = delivery / f'ai技能库-{VERSION}-升级说明.md'
    upgrade_name = 'UPGRADE_' + VERSION.replace('.', '_') + '.md'
    shutil.copy2(ROOT / 'docs' / upgrade_name, notes)
    screenshot = evidence / 'exe-native/result.png'
    assert screenshot.is_file()
    shutil.copy2(screenshot, ROOT / 'docs/images/console.png')

    portable = delivery / f'AISkillLibrary-{VERSION}-windows-x64.zip'
    with zipfile.ZipFile(portable, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(exe, 'ai技能库.exe')
        archive.write(ROOT / 'NOTICE.md', 'NOTICE.md')
        archive.write(ROOT / 'docs/USAGE.md', '使用说明.md')
        archive.write(notes, '升级说明.md')
        with zipfile.ZipFile(ROOT / 'runtime' / runtime['archive']) as bundle:
            for name in runtime['license_paths']:
                archive.writestr('licenses/' + name.replace('/', '-'), bundle.read(name))
    import tempfile
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        manager = SkillManager(folder / 'data', folder / 'home', ROOT, use_env=False)
        files = manager.deployment_files('premium')
        skills = delivery / f'AISkillLibrary-{VERSION}-skills-premium.zip'
        with zipfile.ZipFile(skills, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, data in sorted(files.items()):
                archive.writestr(name, data)
    source = delivery / f'AISkillLibrary-{VERSION}-source.zip'
    with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in ('.gitattributes', '.gitignore', 'AISkillLibrary.spec', 'backend.py', 'main.py', 'rea_config.py',
                     'rea_runtime.py', 'build.ps1', 'generate_extensions.py', 'NOTICE.md', 'README.md',
                     'requirements.txt', 'requirements-dev.txt', 'requirements-audit.txt', 'version_info.txt'):
            archive.write(ROOT / name, 'ai技能库-源码/' + name)
        for name in ('frontend', 'skills', 'runtime', 'tests', 'tools'):
            add_folder(archive, ROOT / name, 'ai技能库-源码/' + name)
        for name in ('USAGE.md', 'CHANGELOG.md', upgrade_name, 'BUILD.md', 'REA_COMPATIBILITY.md', 'REA_INTEGRATION.md', 'images/console.png'):
            archive.write(ROOT / 'docs' / name, 'ai技能库-源码/docs/' + name)
        for name in ('UPGRADE_1_5_0.md', 'security/REVERSE_ANALYSIS.md', 'security/REPRODUCE.md'):
            if name != upgrade_name and (ROOT / 'docs' / name).is_file():
                archive.write(ROOT / 'docs' / name, 'ai技能库-源码/docs/' + name)
    shutil.copy2(source, delivery / 'ai技能库-源码.zip')
    for path in (portable, skills, source):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, path.name
    with zipfile.ZipFile(portable) as archive:
        assert hashlib.sha256(archive.read('ai技能库.exe')).hexdigest() == static['exe_sha256']
        for name in ('NOTICE.md', '使用说明.md', '升级说明.md'):
            text = archive.read(name).decode('utf-8')
            for marker in ('取回', 'TASK_LIMIT', '服务器内容比较', '专业版正文'):
                assert marker not in text, (name, marker)
    assets = [exe, portable, skills, source, notes]
    result = {'version': VERSION, 'passed': True, 'unit_tests': inputs['unit-test-result.json']['tests'],
              'native_desktop_smoke_passed': True, 'local_api_passed': True, 'browser_ui_passed': True,
              'premium_suite_documents': api['premium_suite_documents'],
              'recommended_default': api.get('recommended_default', False),
              'legacy_profiles_preserved': ui['legacy_profiles_preserved'],
              'advanced_options_collapsed': ui['advanced_options_collapsed'],
              'default_enablement_documents': ui['default_enablement_documents'],
              'recommended_library_unique_names': ui['recommended_library_unique_names'],
              'explicit_upgrade_and_backup': ui['explicit_upgrade_and_backup'],
              'client_installations_modified': False, 'actual_ai_chat_verified': False,
              'published_remotely': False, 'public_origin_labels': False,
              'assets': [{'name': path.name, 'bytes': path.stat().st_size, 'sha256': digest(path)} for path in assets]}
    verification = delivery / f'verification-{VERSION}.json'
    verification.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    assets.append(verification)
    sums = ''.join(digest(path) + '  ' + path.name + '\n' for path in assets)
    (delivery / f'AISkillLibrary-{VERSION}-SHA256SUMS.txt').write_text(sums, encoding='utf-8')
    aliases = [delivery / name for name in ('ai技能库.exe', 'ai技能库-源码.zip', '使用说明.md', 'NOTICE.md')]
    (delivery / 'SHA256SUMS.txt').write_text(sums + ''.join(digest(path) + '  ' + path.name + '\n' for path in aliases), encoding='utf-8')
    assert digest(delivery / 'ai技能库.exe') == digest(exe)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-dir', type=Path, required=True)
    main(parser.parse_args().evidence_dir.resolve())
