"""Export both committed sources to scratch; verify or install only validated outputs."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ('s01_static', 's01_rig')
spec = importlib.util.spec_from_file_location('checks', ROOT / 'tools/check.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='replace validated GLBs; preserve .import files')
    parser.add_argument('--logs', type=Path, default=ROOT / 'builds/s01-export')
    args = parser.parse_args()
    args.logs.mkdir(parents=True, exist_ok=True)
    binary = os.environ.get('BLENDER_BIN') or shutil.which('blender')
    assert binary, 'Blender unavailable'
    with tempfile.TemporaryDirectory(prefix='s01-export-') as scratch:
        outputs = []
        evidence = {}
        for asset in ASSETS:
            source = ROOT / f'art/source/models/spikes/{asset}.blend'
            output = Path(scratch) / (asset + '.glb')
            env = os.environ.copy()
            env['ALSOFT_DRIVERS'] = 'null'
            env['XDG_CACHE_HOME'] = scratch
            log = args.logs / (asset + '.log')
            with log.open('w') as stream:
                result = subprocess.run([binary, '-b', '--factory-startup', str(source),
                                         '--python-exit-code', '1', '--python',
                                         str(ROOT / 'tools/s01/export.py'), '--', str(output)],
                                        env=env, stdout=stream, stderr=subprocess.STDOUT,
                                        timeout=60, check=False)
            text = log.read_text()
            assert result.returncode == 0 and 'S01_EXPORT ' + asset in text, (log, text)
            model = checks.glb(output)
            assert not model.get('images') and not model.get('textures')
            assert not model.get('extensionsUsed'), 'unexpected compression or extensions'
            expected = ['death', 'idle', 'run', 'walk'] if asset == 's01_rig' else []
            assert sorted(a['name'] for a in model.get('animations', [])) == expected
            target = ROOT / f'art/models/spikes/{asset}.glb'
            if not args.install:
                assert output.read_bytes() == target.read_bytes(), 'stale GLB: ' + asset
            evidence[asset] = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                               'export_sha256': hashlib.sha256(output.read_bytes()).hexdigest()}
            outputs.append((output, target))
        if args.install:
            for output, target in outputs:
                shutil.copyfile(output, target)
        (args.logs / 'fingerprints.json').write_text(json.dumps(evidence, indent=2) + '\n')
        print('PASS both sources exported; ' + ('installed' if args.install else 'byte-identical'))


if __name__ == '__main__':
    main()
