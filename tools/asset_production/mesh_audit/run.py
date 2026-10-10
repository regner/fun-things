"""Audit every exported GLB and saved prefab; writes JSON only outside the checkout.

Run: python -m tools.asset_production.mesh_audit.run --output C:/tmp/ft/mesh-audit/run-01
Exit 0: complete (findings may exist); 1: selected gate failed; 2: incomplete/error.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

# Bound numerical-library threads before importing numpy in each spawned worker.
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

from .audit import analyze, gate_failures, policy_reason
from .geometry import ANGLE_DEGREES, OVERLAP_SQUARE_METRES, PLANE_METRES
from .glb import Glb
from .prefab import Prefabs

ROOT = Path(__file__).resolve().parents[3]
GATE_CHECKS = ('z_fighting_pairs', 'sealed', 'bottoms', 'elevated_undersides', 'unseen_sampled',
               'inside_closed_island', 'duplicate_vertices', 'loose_vertices', 'zero_area')


def digest(path):
    """Fingerprint read-only inputs and output receipts for independent reproduction."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_asset(task):
    """Isolate per-asset failures so the final JSON exposes incomplete inventory explicitly."""
    root, relative, policy, thresholds = task
    try:
        glb = Glb(Path(root) / relative)
        result = analyze(glb.parts(), keep_reason=policy_reason(relative, policy),
                         dynamic=glb.dynamic or relative.split('/')[2] in
                         ('characters', 'vehicles', 'weapons', 'effects'),
                         **thresholds)
        for group in result['groups']:
            group['source'] = relative
        return {'path': relative, 'sha256': glb.sha256, **result}
    except Exception as error:
        return {'path': relative, 'error': f'{type(error).__name__}: {error}'}


def execute(root, output, assets, prefab_paths, policy, jobs, thresholds):
    """Run all selected inputs and retain detailed per-primitive faces, not only totals."""
    report = {'schema_version': 1, 'thresholds': thresholds, 'assets': [], 'prefabs': [], 'errors': []}
    tasks = [(str(root), p.relative_to(root).as_posix(), policy, thresholds) for p in assets]
    start = time.monotonic()
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        for index, row in enumerate(pool.map(audit_asset, tasks)):
            if 'error' in row:
                report['errors'].append(row)
            else:
                report['assets'].append(row)
            (output / f'asset-{index:03}.json').write_text(json.dumps(row), encoding='utf-8')
            print(f"asset {index+1}/{len(tasks)} {row['path']} "
                  f"{row.get('error', row.get('summary'))}", flush=True)
    resolver = Prefabs(root)
    for index, path in enumerate(prefab_paths):
        relative = path.relative_to(root).as_posix()
        try:
            parts = resolver.parts(path)
            instances = sorted(set(p.instance for p in parts))
            # Repeated copies of the same GLB are also composite geometry.
            result = analyze(parts, cross_instance=True, **thresholds) if len(instances) > 1 else {
                'summary': {'z_fighting_pairs': 0}, 'groups': [], 'pairs': []}
            for group in result['groups']:
                group['source'] = Path(group['source']).relative_to(root).as_posix()
            report['prefabs'].append({'path': relative, 'sha256': digest(path),
                                      'instances': instances, 'composite': len(instances) > 1, **result})
        except Exception as error:
            report['errors'].append({'path': relative, 'error': f'{type(error).__name__}: {error}'})
        print(f'prefab {index+1}/{len(prefab_paths)} {relative}', flush=True)
    dependencies = set(assets) | resolver.dependencies
    report['inputs'] = {p.relative_to(root).as_posix(): digest(p) for p in sorted(dependencies)}
    report['input_manifest_sha256'] = hashlib.sha256(
        json.dumps(report['inputs'], sort_keys=True).encode()).hexdigest()
    report['elapsed_seconds_contended'] = round(time.monotonic()-start, 2)
    return report


def main(argv=None):
    """Expose deterministic thresholds and opt-in strict gating without changing production art."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--asset', action='append', help='root-relative GLB path; repeatable')
    parser.add_argument('--no-prefabs', action='store_true')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--policy', type=Path, default=Path(__file__).with_name('policy.json'))
    parser.add_argument('--plane-metres', type=float, default=PLANE_METRES)
    parser.add_argument('--angle-degrees', type=float, default=ANGLE_DEGREES)
    parser.add_argument('--overlap-m2', type=float, default=OVERLAP_SQUARE_METRES)
    parser.add_argument('--fail-on', action='append', choices=GATE_CHECKS, default=[])
    args = parser.parse_args(argv)
    root, output = args.root.resolve(), args.output.resolve()
    if output.is_relative_to(root) or output.is_relative_to(ROOT):
        parser.error('output must be outside the checkout')
    if output.exists() and any(output.iterdir()):
        parser.error('output must be a fresh empty directory')
    if args.jobs < 1 or args.jobs > 8:
        parser.error('--jobs must be 1..8')
    if not (0 < args.plane_metres <= .02 and 0 < args.angle_degrees <= 5 and
            0 < args.overlap_m2 and math.isfinite(args.overlap_m2)):
        parser.error('thresholds must be finite positive values in the documented bounds')
    assets = [root / p for p in args.asset] if args.asset else sorted(root.glob('art/models/**/*.glb'))
    assets = sorted(set(p.resolve() for p in assets))
    if not assets or any(not p.is_relative_to(root/'art/models') or p.suffix != '.glb' for p in assets):
        parser.error('select one or more GLBs under art/models')
    prefabs = [] if args.no_prefabs else sorted(root.glob('scenes/prefabs/**/*.tscn'))
    output.mkdir(parents=True, exist_ok=True)
    thresholds = {'plane': args.plane_metres, 'angle': args.angle_degrees, 'overlap': args.overlap_m2}
    policy = json.loads(args.policy.read_text(encoding='utf-8'))
    tool_hashes = {p.name: digest(p) for p in sorted(Path(__file__).parent.glob('*.py'))}
    report = execute(root, output, assets, prefabs, policy, args.jobs, thresholds)
    report['policy'] = policy
    report['tool_sha256'] = tool_hashes
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True,
                              text=True, timeout=10, check=False)
    report['source_revision'] = revision.stdout.strip()
    report['complete'] = not report['errors']
    report['gate_failures'] = gate_failures(report, args.fail_on)
    report['gate_passed'] = report['complete'] and not report['gate_failures']
    (output/'audit.json').write_text(json.dumps(report, separators=(',', ':'))+'\n', encoding='utf-8')
    print(json.dumps({'complete': report['complete'], 'assets': len(report['assets']),
                      'prefabs': len(report['prefabs']), 'errors': report['errors'],
                      'gate_failures': report['gate_failures']}, indent=2))
    return 2 if report['errors'] else int(bool(report['gate_failures']))


if __name__ == '__main__':
    sys.exit(main())
