"""Package four lean saved-source contact sheets and measured run follow-up evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / 'docs/assets/player_character/evidence/run_5mps'
CLIPS = ('run', 'run_back', 'run_left', 'run_right')
MOTION = 'art/models/characters/shared_humanoid/shared_humanoid_player_motion_v1.glb'


def sha256(path):
    """Fingerprint actual bytes, including the saved-source reexport comparison."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sheets(scratch):
    """Keep native-scale gameplay crops beneath four unaltered close pose renders."""
    font = ImageFont.load_default(size=19)
    small = ImageFont.load_default(size=15)
    for clip in CLIPS:
        sheet = Image.new('RGB', (1280, 720), '#102C37')
        draw = ImageDraw.Draw(sheet)
        draw.text((16, 8), f'CORAL COURIER / {clip} / 5 m/s / 0.667 s cycle / 1x playback', font=font, fill='white')
        for column, (frame, label) in enumerate(((6, 'Touchdown'), (8, 'Support'), (10, 'Lift-off'), (1, 'Flight'))):
            sheet.paste(Image.open(scratch / 'review' / f'{clip}_{frame}.png'), (column * 320, 60))
            draw.text((column * 320 + 16, 38), f'{label} / frame {frame}', font=small, fill='#FFAB96')
        overhead = Image.open(scratch / 'review' / f'{clip}_overhead.png')
        sheet.paste(overhead.crop((0, 290, 1280, 430)), (0, 580))
        draw.rectangle((0, 580, 510, 633), fill='#102C37')
        draw.text((16, 588), '47 m / vertical 42 deg FOV / 1280 x 720 render', font=small, fill='white')
        draw.text((16, 610), 'Native pixel-scale center crop; not enlarged', font=small, fill='white')
        # Drop only the lowest RGB bit to meet the lean PNG budget without resizing.
        ImageOps.posterize(sheet, 7).save(EVIDENCE / f'{clip}.png', compress_level=9, optimize=True)


def unchanged(baseline):
    """Prove the skin, canonical rig, sockets, grips and all pedestrian-owned files stayed intact."""
    paths = subprocess.check_output(['git', 'ls-files', 'art', 'scenes/prefabs/player_character'], cwd=ROOT, text=True).splitlines()
    keep = [p for p in paths if 'pedestrian_worker' in p
            or 'coral_courier' in p
            or Path(p).stem in ('shared_humanoid_v1', 'shared_humanoid_bind_v1')]
    records = {}
    for path in keep:
        original = subprocess.check_output(['git', 'show', f'{baseline}:{path}'], cwd=ROOT)
        assert original == (ROOT / path).read_bytes(), path
        records[path] = sha256(ROOT / path)
    return records


def main():
    """Require successful checks before recording compact evidence and producer hashes."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--scratch', type=Path, required=True)
    parser.add_argument('--checks', type=Path, required=True)
    parser.add_argument('--baseline', required=True)
    args = parser.parse_args()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    sheets(args.scratch)
    validation = json.loads((args.scratch / 'review/source_validation.json').read_text())
    measurements = (args.scratch / 'measure_run.log').read_text()
    validation['presentation'] = json.loads(next(line.removeprefix('RUN_MEASUREMENTS ') for line in measurements.splitlines() if line.startswith('RUN_MEASUREMENTS ')))
    contract_log = (args.scratch / 'asset_check.log').read_text()
    validation['asset_contract_checks'] = json.loads(next(line.removeprefix('PLAYER_ASSET_CHECK ') for line in contract_log.splitlines() if line.startswith('PLAYER_ASSET_CHECK ')))
    assert not validation['asset_contract_checks']['failures']
    validation['production_checks'] = json.loads((args.checks / 'summary.json').read_text())['results']
    assert all(result['ok'] for result in validation['production_checks'].values())
    assert (ROOT / MOTION).read_bytes() == (args.scratch / 'reexport.glb').read_bytes()
    validation['saved_source_reexport'] = {'byte_identical': True, 'sha256': sha256(ROOT / MOTION),
                                          'export_settings_sha256': sha256(ROOT / 'tools/assets/blender/export_settings.json')}
    validation['unchanged_dependencies'] = unchanged(args.baseline)
    validation['tools'] = {'blender': '5.2.2 LTS', 'godot': '4.8.dev7.official.c971f93e7',
                           'render': 'Cycles CPU / 16 samples / PNG compression 95',
                           'sheet_size': [1280, 720], 'sheet_rgb_precision_bits': 7}
    validation['limits'] = ['Asset-only Blender review lighting; not a gameplay/device acceptance capture.',
                            'Stance velocity measured at four baked intervals; no claim of analytic sub-frame IK.',
                            'Live editors untouched; consumers must reload changed resources before saving.']
    (EVIDENCE / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n', newline='\n')
    changed = subprocess.check_output(['git', 'diff', '--name-only', args.baseline], cwd=ROOT, text=True).splitlines()
    new = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    paths = sorted(set(p for p in changed + new if p.startswith(('art/', 'docs/assets/player_character/', 'scenes/prefabs/player_character/', 'tests/unit/actors/', 'tools/assets/characters/coral_courier/'))))
    manifest = {'asset': 'coral_courier_run_5mps', 'baseline': args.baseline,
                'files': {p: sha256(ROOT / p) for p in paths if not p.endswith('/manifest.json')}}
    (EVIDENCE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', newline='\n')
    print('RUN_EVIDENCE', EVIDENCE, len(manifest['files']), 'files hashed')


if __name__ == '__main__':
    main()
