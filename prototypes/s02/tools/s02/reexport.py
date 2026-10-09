"""Require byte-identical explicit exports from the committed S02 Blender source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import struct
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or Path(tempfile.mkdtemp(prefix='s02-reexport-'))
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(XDG_CACHE_HOME=str(output / 'cache'),
               BLENDER_USER_CONFIG=str(output / 'config'), ALSOFT_DRIVERS='null')
    with (output / 'blender.log').open('w') as log:
        result = subprocess.run(['blender', '--background',
            str(ROOT / 'art/source/models/spikes/s02_kit.blend'), '--python',
            str(ROOT / 'tools/s02/export.py'), '--', str(output / 'exports')],
            env=env, stdout=log, stderr=subprocess.STDOUT, timeout=90)
    assert result.returncode == 0
    log = (output / 'blender.log').read_text()
    known = 'ERROR MeshOptimizer is not available because library could not be found at /usr/lib/blender/5.2/scripts/addons_core/io_scene_gltf2/libbf_intern_meshopt_bridge.so'
    unexpected = [line for line in log.splitlines() if ('ERROR' in line or 'Traceback' in line) and line != known]
    assert not unexpected, unexpected
    hashes = {}
    members = json.loads((ROOT / 'tools/s02/export_members.json').read_text())
    for collection in members:
        name = collection.removeprefix('export_') + '.glb'
        original = ROOT / 'art/models/spikes' / name
        assert original.read_bytes() == (output / 'exports' / name).read_bytes(), name
        data = original.read_bytes()
        length = struct.unpack_from('<I', data, 12)[0]
        gltf = json.loads(data[20:20 + length])
        assert not gltf.get('extensionsUsed'), name
        assert not gltf.get('images'), name
        hashes[str(original.relative_to(ROOT))] = hashlib.sha256(original.read_bytes()).hexdigest()
    source = ROOT / 'art/source/models/spikes/s02_kit.blend'
    hashes[str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
    (output / 'fingerprints.json').write_text(json.dumps(hashes, indent=2) + '\n')
    print('S02 byte-identical exports:', len(members), output)


if __name__ == '__main__':
    main()
