"""Independent literal outcomes and accepted source-derived footprint checks for every traversal."""
import argparse
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/s06'))
from analyze import contains, distance, footprint, rectangle

SIGNATURE = 'eaec39bbde6bd39e0b9c6c5c005f6285be49881faeb3a2cbfa02363014ff1604'
BASELINE = ROOT / 'docs/spikes/s06-evidence/s06-host-final/s06-result.json'
STARTS = {'foot': ([-20, .001, 6.5], -math.pi/2),
          'east_to_north': ([-20, 0, 2.25], -math.pi/2),
          'west_to_south': ([20, 0, -2.25], math.pi/2)}
ENDS = {'foot': ([20, .001, 6.5], -math.pi/2),
        'east_to_north': ([2.25, 0, -20], 0),
        'west_to_south': ([-2.25, 0, 20], math.pi)}


def angle_error(a, b):
    """Compare literal headings with signed wrap independent of shared driving rules."""
    return abs((a - b + math.pi) % math.tau - math.pi)


def analyze(project):
    """Check every actual pose and full interval without treating an empty route as success."""
    baseline = json.loads(BASELINE.read_text())
    roads = [rectangle(g) for g in baseline['geometry'] if g['name'].startswith('Road')]
    walks = [rectangle(g) for g in baseline['geometry'] if g['name'].startswith('Walk')]
    walks.append((-4.5, 5., 4.5, 8.))
    result = json.loads((project / 'result.json').read_text())
    records = [json.loads(line) for line in (project / 'traversals.jsonl').read_text().splitlines()]
    failures = list(result['failures'])
    metrics, counts = [], dict.fromkeys(STARTS, 0)
    previous_retired = 0.
    for ordinal, record in enumerate(records, 1):
        name = record['case']
        counts[name] += 1
        issues = []
        start, yaw = STARTS[name]
        end, exit_yaw = ENDS[name]
        if name != list(STARTS)[(ordinal - 1) % 3] or record['ordinal'] != ordinal:
            issues.append('declared route order')
        if record['route_ordinal'] != counts[name] or record['signature'] != SIGNATURE:
            issues.append('route ordinal/content identity')
        if math.dist(record['start']['position'], start) > .001 or angle_error(record['start']['yaw'], yaw) > .001:
            issues.append('saved start/yaw')
        if math.dist(record['end']['position'], end) > .5 or angle_error(record['end']['yaw'], exit_yaw) > math.radians(10):
            issues.append('real destination/exit direction')
        if record['start']['velocity'] != [0, 0, 0] or record['end']['velocity'] != [0, 0, 0]:
            issues.append('neutral start/stop velocity')
        if record['admission'] != 'OK' or record['timed_out'] or not all(record[k] for k in
                ['stopped_before_notification', 'freed', 'commands_cancelled']):
            issues.append('admission/timeout/cancellation/retirement')
        phases = [previous_retired, record['load_start_seconds'], record['traversal_start_seconds'],
                  record['traversal_end_seconds'], record['retired_seconds']]
        if phases != sorted(phases):
            issues.append('lifetime phase order')
        previous_retired = record['retired_seconds']
        rows = record['samples']
        prior = start
        seams = contacts = outside = 0
        max_step = max_error = 0.
        for tick, row in enumerate(rows, 1):
            position = row['position']
            x, _, z = position
            max_step = max(max_step, math.dist(prior, position))
            seams += (prior[0] >= 0) != (x >= 0)
            prior = position
            contacts += len(row['contacts'])
            if row['tick'] != tick or not 0 < row['delta'] <= .05:
                issues.append('tick/delta progression')
            route = record['route']
            max_error = max(max_error, min(distance((x,z), a,b) for a,b in zip(route, route[1:])))
            points = ([(x + .38 * math.cos(i * math.tau / 32), z + .38 * math.sin(i * math.tau / 32))
                       for i in range(32)] if name == 'foot' else footprint(x,z,row['yaw']))
            outside += sum(not any(contains(r, *p) for r in (walks if name == 'foot' else roads)) for p in points)
        seconds = sum(row['delta'] for row in rows)
        if not rows or len(rows) >= (1200 if name == 'foot' else 1800):
            issues.append('nonempty completed bounded route')
        if seams != 1 or contacts or outside or max_step > .15 or max_error > 1:
            issues.append('continuity/seam/solid contact/legal footprint')
        if rows and math.dist(rows[-1]['position'], record['end']['position']) > .001:
            issues.append('notification/end sample equality')
        metrics.append({'ordinal': ordinal, 'case': name, 'ticks': len(rows), 'simulation_seconds': seconds,
                        'seams': seams, 'contacts': contacts, 'outside_footprint_samples': outside,
                        'max_step_m': max_step, 'max_route_error_m': max_error, 'failures': issues})
        failures.extend(f'{ordinal}/{name}: {issue}' for issue in issues)
    if counts != result['counts'] or len(records) != result['traversals'] or min(counts.values()) < 2:
        failures.append('complete receipt set and repetition minimum')
    if result['elapsed_wall_seconds'] < result['requested_wall_seconds'] or not result['headless']:
        failures.append('actual interval/headless scope')
    if abs(sum(m['simulation_seconds'] for m in metrics) - result['traversal_simulation_seconds']) > .001:
        failures.append('independent simulation total')
    return {'failures': failures, 'counts': counts, 'metrics': metrics,
            'scope': 'every actual tick; accepted source-derived footprints, not continuous swept-volume or graphical capacity',
            'baseline_geometry': str(BASELINE.relative_to(ROOT))}


def main():
    """Write complete independent metrics and use failure status, not only engine exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = analyze(args.project)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'counts': result['counts'], 'failures': result['failures']}))
    return bool(result['failures'])


if __name__ == '__main__':
    raise SystemExit(main())
