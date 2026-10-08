#!/usr/bin/env python3
"""Prepare one instrumented S03 release package from saved private discovery, without import."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/s08'))
from lifecycle_diagnostic import ENGINE, ENGINE_SHA
from observe import launch

TPZ = Path('/tmp/s08-observation-stpco415/Godot_v4.8-dev7_export_templates.tpz')
TEMPLATE = Path('/tmp/s08-observation-stpco415/custom_template/release')
RELEASE_SHA = 'c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695'


def identity(path):
    """Read actual input bytes instead of relying on an old temporary receipt."""
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'bytes': path.stat().st_size, 'sha256': digest}


def save(path, value):
    """Retain structured package bindings and failures without replacing historical evidence."""
    path.write_text(json.dumps(value, indent=2) + '\n')


def bind_templates(task):
    """Verify already-present exact template archive and four members; never acquire anything."""
    expected = {'bytes': 1436879719,
        'sha256': '95c2677555b4f66c7eeca1a41368674703497e1907aad3fe56576423ca3c8cc6'}
    if identity(TPZ) != expected:
        raise RuntimeError('existing exact TPZ unavailable/different')
    expected_members = {
        'linux_debug.x86_64': (78405256, '8b2871a1e2f8baf482282422f7e64cd7cfcc713eb53d8db671025b041bb23eb9'),
        'linux_release.x86_64': (78376584, RELEASE_SHA),
        'windows_debug_x86_64.exe': (105650176, 'c3287ae1c7fad6f6f2e0e09b0ebbb1321b49ec2423b74d513f12649e4c03bff6'),
        'windows_release_x86_64.exe': (111895040, 'b538554df997ea699122d5b31f2ea8929301bcf3017e12dba664d85d351f60cd'),
    }
    rows = []
    with zipfile.ZipFile(TPZ) as archive:
        version = archive.read('templates/version.txt').decode().strip()
        if version != '4.8.dev7':
            raise RuntimeError('template version differs')
        for name, expected_member in expected_members.items():
            path = 'templates/' + name
            with archive.open(path) as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            actual = (archive.getinfo(path).file_size, digest)
            if actual != expected_member:
                raise RuntimeError('template member differs: ' + name)
            rows.append({'path': path, 'bytes': actual[0], 'sha256': actual[1]})
    if identity(TEMPLATE) != {'bytes': 78376584, 'sha256': RELEASE_SHA}:
        raise RuntimeError('existing Linux release template differs')
    target = task / 'custom_template/release'
    target.parent.mkdir()
    shutil.copyfile(TEMPLATE, target)
    save(task / 'template-binding.json', {'tpz_path': str(TPZ), **expected,
        'version': version, 'members': rows, 'release_template': identity(target)})


def inspect_pack(task):
    """Bind every actual exported member/remap/UID and exclude all other fixture families."""
    folder = task / 'export-folder'
    actual = sorted(path.name for path in folder.iterdir())
    if actual != ['FunThingsS08.pck', 'FunThingsS08.x86_64']:
        raise RuntimeError('unexpected export-folder set')
    executable = folder / 'FunThingsS08.x86_64'
    if identity(executable) != {'bytes': 78376584, 'sha256': RELEASE_SHA}:
        raise RuntimeError('external-PCK binary differs from exact template')
    pack = folder / 'FunThingsS08.pck'
    data = pack.read_bytes()
    magic, version, major, minor, patch, flags = struct.unpack_from('<6I', data)
    file_base, directory = struct.unpack_from('<QQ', data, 24)
    if (magic, version, major, minor, patch, flags) != (0x43504447, 4, 4, 8, 0, 2):
        raise RuntimeError('unexpected pack header')
    count = struct.unpack_from('<I', data, directory)[0]
    position, members, payloads = directory + 4, [], {}
    for _ in range(count):
        length = struct.unpack_from('<I', data, position)[0]
        position += 4
        name = data[position:position + length].rstrip(b'\0').decode()
        position += length
        offset, size = struct.unpack_from('<QQ', data, position)
        md5 = data[position + 16:position + 32].hex()
        entry_flags = struct.unpack_from('<I', data, position + 32)[0]
        position += 36
        start = file_base + offset
        payload = data[start:start + size]
        if (name in payloads or '..' in Path(name).parts or entry_flags
                or len(payload) != size or hashlib.md5(payload).hexdigest() != md5):
            raise RuntimeError('unsafe/invalid pack member: ' + name)
        payloads[name] = payload
        members.append({'path': name, 'offset': start, 'bytes': size,
            'sha256': hashlib.sha256(payload).hexdigest(), 'md5': md5})
    forbidden = re.compile(r'addons/|Steam|MCP|\.gdextension|\.blend$|\.so$|\.dll$|'
                           r'tests/fixtures/(?!s03/)')
    if any(forbidden.search(name) for name in payloads):
        raise RuntimeError('out-of-scope pack member')
    mappings = []
    for row in json.loads((task / 'staged-input.json').read_text()):
        name = row['path']
        if name.endswith('.uid'):
            continue
        remap = name + '.remap'
        if remap not in payloads:
            raise RuntimeError('missing exported remap: ' + name)
        targets = re.findall(r'^path="res://([^\"]+)"', payloads[remap].decode(), re.M)
        if len(targets) != 1 or targets[0] not in payloads:
            raise RuntimeError('invalid/missing remap destination: ' + name)
        mappings.append({'source': name, 'remap': remap, 'payload': targets[0]})
    for name in ['project.binary', '.godot/uid_cache.bin', '.godot/global_script_class_cache.cfg']:
        if name not in payloads:
            raise RuntimeError('required cache/config missing: ' + name)
    classes = payloads['.godot/global_script_class_cache.cfg'].decode()
    if 'Steam' in classes or 'MCP' in classes:
        raise RuntimeError('native/development class leak')
    raw = payloads['.godot/uid_cache.bin']
    count = struct.unpack_from('<I', raw)[0]
    position, uids = 4, []
    for _ in range(count):
        uid, size = struct.unpack_from('<QI', raw, position)
        end = position + 12 + size
        path = raw[position + 12:end].decode()
        uids.append({'uid': uid, 'path': path})
        position = end
    if position != len(raw) or len(set(row['uid'] for row in uids)) != len(uids):
        raise RuntimeError('invalid/duplicate UID cache')
    save(task / 'package-binding.json', {'executable': identity(executable),
        'pck': identity(pack), 'entries': members, 'mappings': mappings,
        'uids': uids, 'class_cache': classes, 'input_revision': json.loads(
            (task / 'preparation.json').read_text())['revision'], 'output_set': actual})


def main():
    """Spend one export attempt only after exact saved-source/template checks, with no import."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--author-project', type=Path, required=True)
    args = parser.parse_args()
    task = args.output.resolve()
    if task.exists() or not task.is_relative_to(Path('/tmp')):
        parser.error('fresh private /tmp output required')
    task.mkdir(mode=0o700)
    record = {'ok': False, 'revision': args.revision, 'imports': 0, 'exports': 0}
    save(task / 'preparation.json', record)
    try:
        if identity(ENGINE) != {'bytes': 151398728, 'sha256': ENGINE_SHA}:
            raise RuntimeError('pinned export engine differs')
        bind_templates(task)
        project = task / 'project'
        project.mkdir()
        names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', args.revision,
            'tests/fixtures/s03'], cwd=ROOT, text=True).splitlines()
        rows = []
        for name in names:
            data = subprocess.check_output(['git', 'show', args.revision + ':' + name], cwd=ROOT)
            if (args.author_project / name).read_bytes() != data:
                raise RuntimeError('saved source differs: ' + name)
            target = project / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            rows.append({'path': name, **identity(target)})
        save(task / 'staged-input.json', rows)
        config = (ROOT / 'project.godot').read_text()
        config = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', config)
        config = config.replace('config/icon="res://icon.svg"\n', '')
        config = config.replace('[application]\n', '[application]\n'
            'run/main_scene="res://tests/fixtures/s03/boot.tscn"\n')
        (project / 'project.godot').write_text(config)
        cache = project / '.godot'
        cache.mkdir()
        # Already-completed owned discovery only; no dependency import or author relaunch.
        text = (args.author_project / '.godot/global_script_class_cache.cfg').read_text()
        classes = [item for item in re.findall(r'\{[^}]*\}', text)
                   if 'res://tests/fixtures/s03/' in item]
        (cache / 'global_script_class_cache.cfg').write_text('list=[' + ', '.join(classes) + ']\n')
        raw = (args.author_project / '.godot/uid_cache.bin').read_bytes()
        count = struct.unpack_from('<I', raw)[0]
        position, kept = 4, []
        for _ in range(count):
            _uid, size = struct.unpack_from('<QI', raw, position)
            end = position + 12 + size
            if raw[position + 12:end].decode() in {'res://' + name for name in names}:
                kept.append(raw[position:end])
            position = end
        if position != len(raw) or len(classes) != 7:
            raise RuntimeError('private dependency discovery differs')
        (cache / 'uid_cache.bin').write_bytes(struct.pack('<I', len(kept)) + b''.join(kept))
        resources = ['res://' + name for name in names if not name.endswith('.uid')]
        preset = ('[preset.0]\nname="S08 lifecycle"\nplatform="Linux"\nrunnable=true\n'
            'export_filter="resources"\nexport_files=PackedStringArray(' +
            ', '.join(json.dumps(name) for name in resources) + ')\n'
            'include_filter=""\nexclude_filter=""\nexport_path=""\n'
            'encrypt_pck=false\nencrypt_directory=false\nscript_export_mode=1\n'
            '[preset.0.options]\ncustom_template/debug=""\ncustom_template/release=' +
            json.dumps(str(task / 'custom_template/release')) + '\n'
            'binary_format/architecture="x86_64"\nbinary_format/embed_pck=false\n'
            'debug/export_console_wrapper=0\ntexture_format/s3tc_bptc=true\n'
            'texture_format/etc2_astc=false\n')
        (project / 'export_presets.cfg').write_text(preset)
        save(task / 'scratch-config.json', {'project.godot': config, 'export_presets.cfg': preset})
        folder = task / 'export-folder'
        folder.mkdir()
        record['exports'] = 1
        save(task / 'preparation.json', record)
        launch(task, 'export', [str(ENGINE), '--headless', '--path', str(project),
            '--export-release', 'S08 lifecycle', str(folder / 'FunThingsS08.x86_64')],
            120, project)
        for row in rows:
            if identity(project / row['path']) != {key: row[key] for key in ['bytes', 'sha256']}:
                raise RuntimeError('export changed saved input: ' + row['path'])
        inspect_pack(task)
        record['ok'] = True
    except Exception as error:
        record['failure'] = repr(error)
        raise
    finally:
        save(task / 'preparation.json', record)


if __name__ == '__main__':
    main()
