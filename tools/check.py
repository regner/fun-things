"""Minimum P0-03 checks for S01. Vendor addons and ignored trees stay excluded."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
VENDORS = {'addons/godot_mcp_toolkit', 'addons/godotsteam'}


def owned_files(root=ROOT):
    for directory, dirs, files in os.walk(root):
        current = Path(directory)
        if '.gdignore' in files:
            dirs[:] = []
            continue
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and
                         str((current / d).relative_to(root)) not in VENDORS and
                         d not in ('builds', '__pycache__'))
        for name in sorted(files):
            yield current / name


def run(command, log, env, timeout=60):
    with log.open('w') as output:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=output,
                                stderr=subprocess.STDOUT, timeout=timeout, check=False)
    contents = log.read_text(errors='replace')
    if result.returncode or re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|WARNING:)', contents):
        raise RuntimeError(f'{log}: exit {result.returncode}\n{contents}')
    print(f'PASS {log.name}')
    return contents


def glb(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<III', data)
    assert magic == 0x46546C67 and version == 2 and length == len(data), path
    size, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4E4F534A, path
    return json.loads(data[20:20+size])


def source_links(root):
    assert (root / 'art/source/.gdignore').is_file()
    for name in ('s01_static', 's01_rig'):
        source = root / f'art/source/models/spikes/{name}.blend'
        # Blender supports uncompressed, gzip and Zstandard source files.
        assert source.read_bytes().startswith((b'BLENDER', b'\x1f\x8b', b'\x28\xb5\x2f\xfd')), source
        export = root / f'art/models/spikes/{name}.glb'
        assert export.with_suffix('.glb.import').is_file(), export
        model = glb(export)
        assert not model.get('images') and not model.get('textures'), export
        assert all('uri' not in b for b in model['buffers']), export
        if name == 's01_rig':
            assert sorted(a['name'] for a in model['animations']) == ['death','idle','run','walk']
            assert len(model['skins']) == 1 and len(model['skins'][0]['joints']) == 2
        else:
            assert not model.get('animations') and not model.get('skins')
    assert (root / 'art/source/textures/spikes/s01_palette.png').read_bytes() == (
        root / 'art/textures/spikes/s01_palette.png').read_bytes(), 'stale runtime texture'
    identities = {}
    for path in owned_files(root):
        if path.suffix in ('.tscn', '.tres'):
            text = path.read_text()
            assert not re.search(r'type="(?:ArrayMesh|\w*Mesh|CSG\w*)"', text), path
            assert not re.search(r'"(?:vertices|_surfaces)"', text), path
            for target in re.findall(r'path="(res://[^"]+)"', text):
                assert (root / target[6:]).is_file(), (path, target)
        if path.suffix in ('.tscn', '.tres', '.import', '.uid'):
            text = path.read_text()
            uid = text.strip() if path.suffix == '.uid' else next(iter(
                re.findall(r'(?:^uid=|^\[gd_.*?uid=)"(uid://[^"]+)"', text, re.M)), None)
            if uid:
                assert uid not in identities, (uid, identities.get(uid), path)
                identities[uid] = path
    print('PASS source/export links, no copied mesh data, external files and unique resource UIDs')


def godot_binary(env):
    binary = env.get('GODOT_BIN') or shutil.which('godot')
    assert binary, 'Godot unavailable: run via mise or set GODOT_BIN'
    config = tomllib.loads((ROOT / 'mise.toml').read_text())
    pin = config['tools']['github:godotengine/godot-builds']['version'].replace('-', '.')
    version = subprocess.check_output([binary, '--version'], env=env, text=True).strip()
    assert version.startswith(pin + '.'), (pin, version)
    print('Godot', version)
    return binary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=('style', 'scripts', 'resources'))
    parser.add_argument('--logs', type=Path, default=ROOT / 'builds/checks')
    args = parser.parse_args()
    args.logs.mkdir(parents=True, exist_ok=True)
    scripts = [str(p.relative_to(ROOT)) for p in owned_files() if p.suffix == '.gd']
    assert scripts, 'no owned scripts discovered'
    env = os.environ.copy()
    with tempfile.TemporaryDirectory(prefix='s01-user-') as user:
        for key in ('XDG_DATA_HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME'):
            env[key] = user + '/' + key.lower()
        if args.check == 'style':
            binary = os.environ.get('GDSTYLE_BIN') or shutil.which('gdstyle')
            assert binary, 'gdstyle unavailable: run via mise or set GDSTYLE_BIN'
            pin = (ROOT / '.gdstyle-version').read_text().strip()
            assert pin in subprocess.check_output([binary, '--version'], text=True)
            run([binary, 'check', '--no-color', '--max-warnings', '0', *scripts],
                args.logs / 'style.log', env)
            return
        binary = godot_binary(env)
        if args.check == 'scripts':
            errors = []
            for script in scripts:
                try:
                    run([binary, '--headless', '--path', str(ROOT), '--check-only', '--script', script],
                        args.logs / (script.replace('/', '_') + '.log'), env)
                except RuntimeError as error:
                    errors.append(str(error))
            if errors:
                raise RuntimeError('\n'.join(errors))
            print(f'PASS explicitly compiled {len(scripts)} owned scripts (including unused scripts)')
        else:
            source_links(ROOT)
            contents = run([binary, '--headless', '--path', str(ROOT), '--script',
                            'tests/fixtures/s01/check_s01.gd'], args.logs / 'resources.log', env)
            assert 'S01_RESULT checks complete; failures=0' in contents, 'missing result marker'


if __name__ == '__main__':
    main()
