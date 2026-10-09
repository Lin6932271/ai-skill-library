"""Apply the pinned REA 6.1.0 NUL-regex interoperability patch offline."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PATCH_ID = 'portable-regex-v1'
UPSTREAM_SHA = 'e0d430658952113b23c0099e21131af6d554e2bac6742cf36af16389fb46d494'
PREFIX = 'cli/node_modules/rea-agents/dist/'
TARGETS = {
    'contracts/native/nativeToolContracts.js': 1,
    'domain/javascript/electronActiveObservation.js': 1,
    'domain/localPath.js': 1,
    'domain/native/nativeCallObservation.js': 3,
    'domain/process/processScenario.js': 2,
    'domain/apple/dylibResolution.js': 1,
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def patch():
    manifest_path = ROOT / 'runtime/manifest.json'
    manifest = json.loads(manifest_path.read_text('utf-8'))
    archive = manifest_path.parent / manifest['archive']
    if manifest.get('compatibility_patch') == PATCH_ID:
        assert digest(archive.read_bytes()) == manifest['sha256']
        if 'upstream_critical_files' not in manifest:
            original = ROOT.parent / 'rea-compatibility-20261009/original/manifest.json'
            manifest['upstream_critical_files'] = json.loads(original.read_text('utf-8'))['critical_files']
            manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print('REA compatibility patch already applied')
        return
    assert manifest['rea_version'] == '6.1.0'
    backup = ROOT.parent / 'rea-compatibility-20261009/original'
    backup.mkdir(parents=True, exist_ok=True)
    for source in (archive, manifest_path):
        if not (backup / source.name).exists():
            shutil.copy2(source, backup / source.name)
    upstream_archive = backup / archive.name
    assert digest(upstream_archive.read_bytes()) == UPSTREAM_SHA
    upstream_manifest = json.loads((backup / manifest_path.name).read_text('utf-8'))
    manifest = upstream_manifest
    replacement = archive.with_suffix('.patched.zip')
    changes = []
    with zipfile.ZipFile(upstream_archive) as original:
        index = json.loads(original.read('files.json'))
        with zipfile.ZipFile(replacement, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
            for member in original.infolist():
                if member.filename == 'files.json':
                    continue
                data = original.read(member.filename)
                relative = member.filename.removeprefix(PREFIX)
                if relative in TARGETS and member.filename.startswith(PREFIX):
                    before = digest(data)
                    lines = data.decode('utf-8').splitlines(keepends=True)
                    count = sum(line.count(r'\0') for line in lines if '.regex(' in line or 'const ROOT_RELATIVE_PATH =' in line)
                    assert count == TARGETS[relative], (relative, count)
                    text = ''.join(line.replace(r'\0', r'\x00') if '.regex(' in line or 'const ROOT_RELATIVE_PATH =' in line else line
                                   for line in lines)
                    if relative == 'domain/process/processScenario.js':
                        text = text.replace(r'/^(?!REA_PROCESS_RUN_ID(?![\s\S]))[^=\x00]+$/u', r'/^[^=\x00]+$/u')
                        needle = '\n});\nconst childProcessString'
                        assert needle in text
                        text = text.replace(needle, '\n}).refine((name) => name !== reservedRunIdEnvironmentName, `${reservedRunIdEnvironmentName} is reserved by the process adapter`);\nconst childProcessString', 1)
                    elif relative == 'domain/apple/dylibResolution.js':
                        needle = 'z.string().min(1).regex(ROOT_RELATIVE_PATH)'
                        assert needle in text
                        text = text.replace(needle, r'z.string().min(1).regex(/^[^\\\x00]+$/u).refine((path) => ROOT_RELATIVE_PATH.test(path), "Expected a normalized path below the analyzed root")', 1)
                    data = text.encode('utf-8')
                    index[member.filename] = digest(data)
                    changes.append({'path': member.filename, 'before_sha256': before,
                                    'after_sha256': digest(data), 'replacements': count})
                output.writestr(member, data)
            output.writestr('files.json', json.dumps(index, sort_keys=True).encode('utf-8'))
    assert len(changes) == len(TARGETS) and sum(c['replacements'] for c in changes) == 9
    with zipfile.ZipFile(replacement) as patched:
        assert patched.testzip() is None
        manifest['unpacked_bytes'] = sum(item.file_size for item in patched.infolist() if item.filename != 'files.json')
    replacement.replace(archive)
    manifest.update({'sha256': digest(archive.read_bytes()), 'compatibility_patch': PATCH_ID,
                     'upstream_archive_sha256': UPSTREAM_SHA, 'patched_files': changes,
                     'upstream_critical_files': dict(upstream_manifest['critical_files'])})
    manifest['critical_files'].update({change['path']: change['after_sha256'] for change in changes})
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'patch': PATCH_ID, 'files': len(changes), 'replacements': 9,
                      'archive_sha256': manifest['sha256']}))


if __name__ == '__main__':
    patch()
