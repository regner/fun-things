"""Independent frozen-candidate checks; no shared implementation mutations."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REVIEW = Path(__file__).resolve().parent
SNAPSHOT = Path('/tmp/batch02-review-5e94cc0/snapshot')
REPO = Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production')
CANDIDATE = '5e94cc0ea4155219285db49c64b5728e0882b093'
PARENT = '784dfc33a47f481ee43441c36a0280793e02de77'
BASE = '66400c26a01bf917dfe631af4762c2b444d9c48f'
IDS = ['city_planting_03', 'city_planting_04', 'city_planting_05',
       'city_roof_details_01', 'city_roof_details_02', 'city_shop_fittings_01']


def run(name, argv, cwd=SNAPSHOT, local_env=None, timeout=240):
    """Retain exact invocation and complete separate streams, including empties."""
    env = os.environ.copy()
    env.update(local_env or {})
    receipt = {'argv': [str(x) for x in argv], 'cwd': str(cwd),
               'environment_overrides': local_env or {},
               'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    result = subprocess.run(receipt['argv'], cwd=cwd, env=env, capture_output=True,
                            timeout=timeout)
    (REVIEW / (name + '.stdout')).write_bytes(result.stdout)
    (REVIEW / (name + '.stderr')).write_bytes(result.stderr)
    receipt.update(exit=result.returncode,
                   end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (REVIEW / (name + '.command.json')).write_text(json.dumps(receipt, indent=2)+'\n')
    print(name, result.returncode, flush=True)
    return result


def index(path):
    """Fingerprint actual payload bytes."""
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def scope(path, asset):
    """Derive expected owned set from tree prefixes, independently of manifests."""
    prefixes = [f'art/source/models/environment/{asset}/',
                f'art/models/environment/{asset}/',
                f'art/materials/environment/{asset}/',
                f'art/textures/environment/{asset}/',
                f'tools/asset_production/{asset}/',
                f'docs/assets/production/{asset}-evidence/']
    return path == f'docs/assets/production/{asset}.md' or any(
        path.startswith(p) for p in prefixes)


def static():
    """Compare complete candidate tree, manifests, source-readback and parent retention."""
    tree_result = run('candidate-tree', ['git', 'ls-tree', '-r', '--full-tree', CANDIDATE], REPO)
    tree = {}
    for line in tree_result.stdout.decode().splitlines():
        meta, path = line.split('\t')
        mode, kind, blob = meta.split()
        tree[path] = {'mode': mode, 'kind': kind, 'git_blob': blob}
    parent_result = run('parent-tree', ['git', 'ls-tree', '-r', '--full-tree', PARENT], REPO)
    parent = {}
    for line in parent_result.stdout.decode().splitlines():
        meta, path = line.split('\t')
        parent[path] = meta.split()[2]
    run('delta-parent', ['git', 'diff', '--name-status', PARENT, CANDIDATE], REPO)
    run('delta-original-base', ['git', 'diff', '--name-status', BASE, CANDIDATE], REPO)
    run('candidate-whitespace', ['git', 'diff', '--check', PARENT, CANDIDATE], REPO)
    readback = json.loads((SNAPSHOT/'docs/assets/production/batch_02-evidence/source-readback.json').read_text())
    reports = []
    references = []
    for asset in IDS:
        mp = f'docs/assets/production/{asset}-evidence/manifest.json'
        manifest = json.loads((SNAPSHOT/mp).read_text())
        expected = {p for p in tree if scope(p, asset) and p != mp}
        declared = [row['path'] for row in manifest['files']]
        mismatches = []
        for row in manifest['files']:
            p = SNAPSHOT/row['path']
            actual = index(p) if p.is_file() else None
            if actual != {'bytes': row['bytes'], 'sha256': row['sha256']}:
                mismatches.append({'path': row['path'], 'actual': actual, 'declared': row})
        actual_manifest = index(SNAPSHOT/mp)
        rb = next(r for r in readback if r['id'] == asset)
        report = {'asset': asset, 'actual_tree_count_excluding_manifest': len(expected),
                  'manifest_count': len(declared), 'duplicates': len(declared)-len(set(declared)),
                  'omitted': sorted(expected-set(declared)),
                  'extra': sorted(set(declared)-expected), 'mismatches': mismatches,
                  'source_readback_manifest_hash_matches': actual_manifest['sha256']==rb['manifest_sha256'],
                  'source_readback_count_matches': len(declared)==rb['expected_payload_count'],
                  'parent_owned_paths_changed_or_removed': [p for p in parent if scope(p, asset) and tree.get(p,{}).get('git_blob') != parent[p]]}
        reports.append(report)
        for p in sorted(expected | {mp}):
            references.append({'path': p, **tree[p], **index(SNAPSHOT/p), 'revision': CANDIDATE})
    (REVIEW/'candidate-payload-index.json').write_text(json.dumps(references, indent=2)+'\n')
    (REVIEW/'retention-check.json').write_text(json.dumps(reports, indent=2)+'\n')
    print(json.dumps(reports, indent=2), flush=True)


if __name__ == '__main__':
    static()
    run('blender-pin', ['/usr/bin/blender', '--version'], local_env={
        'ALSOFT_DRIVERS':'null', 'SDL_AUDIODRIVER':'dummy'})
    for asset in IDS:
        run(asset+'-source', ['/usr/bin/blender', '-b', '-noaudio', '-t', '2',
            str(SNAPSHOT/f'art/source/models/environment/{asset}/{asset}.blend'),
            '--python-exit-code', '1', '--python', str(REVIEW/'source_audit.py'),
            '--', asset, str(REVIEW)], local_env={
                'ALSOFT_DRIVERS':'null', 'SDL_AUDIODRIVER':'dummy'}, timeout=300)
    run('binary-audit', [sys.executable, str(REVIEW/'glb_audit.py')])
