"""Independent imported-geometry, body-footprint, route and minimap expectations."""
import argparse
import json
import math
from pathlib import Path


def rectangle(row):
    lo, size = row['minimum'], row['size']
    return (lo[0], lo[2], lo[0] + size[0], lo[2] + size[2])


def contains(rect, x, z, tolerance=.001):
    a, b, c, d = rect
    return a - tolerance <= x <= c + tolerance and b - tolerance <= z <= d + tolerance


def distance(point, start, end):
    x, z = point
    a, b = start[0], start[2]
    dx, dz = end[0] - a, end[2] - b
    length = dx * dx + dz * dz
    t = max(0., min(1., ((x - a) * dx + (z - b) * dz) / length)) if length else 0.
    return math.hypot(x - a - t * dx, z - b - t * dz)


def footprint(x, z, yaw, width=1.8, length=3.4):
    # Independent rectangle edge sampling uses the accepted collider, never handling formulas.
    right = (math.cos(yaw), -math.sin(yaw))
    forward = (-math.sin(yaw), -math.cos(yaw))
    points = []
    for i in range(35):
        for lateral in [-width / 2, width / 2]:
            longitudinal = -length / 2 + length * i / 34
            points.append((x + right[0] * lateral + forward[0] * longitudinal,
                           z + right[1] * lateral + forward[1] * longitudinal))
    for i in range(19):
        for longitudinal in [-length / 2, length / 2]:
            lateral = -width / 2 + width * i / 18
            points.append((x + right[0] * lateral + forward[0] * longitudinal,
                           z + right[1] * lateral + forward[1] * longitudinal))
    return points


def analyze(result):
    roads = [rectangle(row) for row in result['geometry'] if row['name'].startswith('Road')]
    walks = [rectangle(row) for row in result['geometry'] if row['name'].startswith('Walk')]
    # Marked crossing's declared 3 m band is checked independently of graph construction.
    walks.append((-4.5, 5., 4.5, 8.))
    failures = list(result['failures'])
    metrics = {}
    for name, rows in result['trajectories'].items():
        previous = None
        max_step = max_error = 0.
        outside = contacts = seams = 0
        for row in rows:
            x, _, z = row['position']
            if previous:
                max_step = max(max_step, math.dist(row['position'], previous['position']))
                seams += (x >= 0) != (previous['position'][0] >= 0)
            previous = row
            route = result['routes'][name]
            max_error = max(max_error, min(distance((x, z), a, b)
                                          for a, b in zip(route, route[1:])))
            contacts += len(row['contacts'])
            if name == 'foot':
                points = [(x + .38 * math.cos(i * math.tau / 32),
                           z + .38 * math.sin(i * math.tau / 32)) for i in range(32)]
                outside += sum(not any(contains(r, *p) for r in walks) for p in points)
            else:
                outside += sum(not any(contains(r, *p) for r in roads)
                               for p in footprint(x, z, row['yaw']))
        metrics[name] = {'ticks': len(rows), 'seconds': sum(r['delta'] for r in rows),
                         'last_pose': rows[-1] if rows else None,
                         'max_step_m': max_step, 'max_route_error_m': max_error,
                         'footprint_samples_outside': outside, 'contacts': contacts,
                         'seam_crossings': seams}
        if not rows or contacts or outside or seams != 1 or max_step > .15 or max_error > 1.:
            failures.append(name + ' geometry/continuity/contact/seam expectation')
    shared = {road['id']: road for road in result['roads']}
    west, east = shared['s06/road/west_link'], shared['s06/road/east_link']
    map_error = math.dist(west['points'][-1], east['points'][0])
    map_bounds = (west['points'][0][0], east['points'][-1][0])
    visual_bounds = (min(r[0] for r in roads), max(r[2] for r in roads))
    extents_error = max(abs(a - b) for a, b in zip(map_bounds, visual_bounds))
    if map_error > .01 or extents_error > .01 or any(road['width_m'] != 9 for road in shared.values()):
        failures.append('minimap seam/geometry extents/width expectation')
    # Sensitivity checks retain actual poses and test larger envelopes, without changing S04.
    sensitivity = {}
    for width, length in [(2., 3.8), (2.2, 4.8)]:
        count = 0
        for name in ['east_to_north', 'west_to_south']:
            for row in result['trajectories'][name]:
                x, _, z = row['position']
                count += sum(not any(contains(r, *p) for r in roads)
                             for p in footprint(x, z, row['yaw'], width, length))
        sensitivity[f'{width}x{length}'] = {'outside_edge_samples': count,
            'scope': 'geometric sensitivity on actual baseline poses; no changed-body physics proof'}
    return {'failures': failures, 'metrics': metrics, 'minimap': {
        'seam_error_m': map_error, 'seam_error_px_at_3px_per_m': map_error * 3,
        'geometry_extents_error_m': extents_error}, 'sensitivity': sensitivity,
        'sampling': 'every actual physics tick; rectangle edges <=0.1m; not analytic continuous sweep',
        'camera_ground_view_m': {str(fov): [2 * 47 * math.tan(math.radians(fov / 2)) * 1.6,
            2 * 47 * math.tan(math.radians(fov / 2))] for fov in [42, 50]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = analyze(json.loads(args.result.read_text()))
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return bool(report['failures'])


if __name__ == '__main__':
    raise SystemExit(main())
