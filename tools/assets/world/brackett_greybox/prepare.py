#!/usr/bin/env python3
"""One-time offline greybox authoring input; saved Godot sectors own runtime placement.

Requires Shapely 2.2.0. Never runs as part of the game or regenerates edited sectors.
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random

from shapely import constrained_delaunay_triangles
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'art/source/models/brackett_greybox'
REFERENCE = ROOT / 'docs/concepts/world-v1/stage-04-streets'
spec = importlib.util.spec_from_file_location('streets', REFERENCE / 'draw_plan.py')
streets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(streets)

# Width/east, depth/south, total height in metres. Deliberate neutral placeholders.
TYPES = {
    1: [('campus_hall', 28, 18, 12), ('campus_classroom', 20, 14, 9), ('campus_annex', 14, 12, 6)],
    2: [('house', 10, 12, 6), ('semi', 14, 12, 7), ('terrace', 20, 11, 8)],
    3: [('apartment', 24, 15, 16), ('apartment_slab', 32, 14, 21), ('apartment_small', 18, 16, 13)],
    4: [('tower_high', 30, 28, 90), ('tower_mid', 28, 26, 68), ('office', 24, 22, 42)],
    5: [('quay_house', 12, 15, 9), ('quay_row', 20, 12, 12), ('quay_hall', 26, 18, 14)],
    6: [('shop', 18, 15, 10), ('entertainment_hall', 30, 23, 15), ('shop_row', 26, 14, 13)],
    7: [('retail_large', 65, 38, 10), ('retail_box', 45, 30, 8), ('retail_small', 28, 22, 7)],
    8: [('workshop', 30, 20, 8), ('repair_shed', 22, 16, 7), ('workshop_large', 40, 24, 10)],
    9: [('warehouse', 65, 28, 12), ('warehouse_small', 42, 24, 10), ('dock_shed', 28, 20, 8)],
}


def polygons(geometry):
    """Yield only nonempty polygon members after clipping/union operations."""
    if geometry.geom_type == 'Polygon':
        if geometry.area > .001:
            yield geometry
    elif hasattr(geometry, 'geoms'):
        for part in geometry.geoms:
            yield from polygons(part)


def triangles(geometry):
    """Constrained triangulation preserves harbour holes and exact clipped edges."""
    result = []
    for poly in polygons(geometry):
        for triangle in constrained_delaunay_triangles(poly).geoms:
            result.append([[round(x, 5), round(y, 5)] for x, y in list(triangle.exterior.coords)[:3]])
    return result


def main():
    """Freeze concept geometry, solve clear plots, and write reviewable authoring input."""
    SOURCE.mkdir(parents=True, exist_ok=True)
    assert not (SOURCE/'authoring_plan.json').exists(), 'Bootstrap only: preserve the frozen placement IDs'
    routes = streets.roads()
    land = Polygon(streets.LAND).difference(Polygon(streets.WATER))
    bridge_route = next(r for r in routes if r['name'] == 'Harbour bridge')
    bridge = LineString(bridge_route['points']).buffer(8.5, cap_style='flat')
    surface = land.union(bridge)
    carriage, corridors = [], []
    for road in routes:
        width, corridor, *_ = streets.TYPES[road['kind']]
        line = LineString(road['points'])
        carriage.append(line.buffer(width / 2, quad_segs=6))
        corridors.append(line.buffer(corridor / 2, quad_segs=6))
        if road['dead']:
            radius = 15 if road['kind'] == 'freight' else 10
            carriage.append(Point(road['points'][-1]).buffer(radius, quad_segs=12))
            corridors.append(Point(road['points'][-1]).buffer(radius + 2, quad_segs=12))
    road_area = unary_union(carriage).intersection(surface)
    corridor_area = unary_union(corridors).intersection(surface)
    foot = unary_union([LineString(p).buffer(1, quad_segs=4) for p in streets.foot_links(routes)])
    walk_area = corridor_area.union(foot).difference(road_area).intersection(surface)
    field = box(210, 127, 308, 180)
    buildable = land.buffer(-5).difference(corridor_area.buffer(2.5)).difference(foot.buffer(2.5)).difference(field.buffer(5))
    districts = streets.BOUNDARIES
    district_polys = {d['id']: Polygon(d['points']) for d in districts}
    road_lines = [LineString(r['points']) for r in routes]
    rng = random.Random(9042026)
    candidates = [(x + rng.uniform(-3, 3), y + rng.uniform(-3, 3))
                  for y in range(55, 660, 8) for x in range(65, 1205, 8)]
    # Large sites first; small west plots get an independent fine grain. Stable frozen IDs
    # are assigned below and must be retained during replacement, not regenerated in game.
    placements, occupied, counts = [], [], {}
    for district in [9, 7, 4, 3, 8, 1, 6, 5, 2]:
        candidates.sort(key=lambda p: (min(l.distance(Point(p)) for l in road_lines), p[1], p[0]))
        local_count = 0
        for x, z in candidates:
            point = Point(x, z)
            if not buildable.contains(point) or not district_polys[district].covers(point):
                continue
            near = min(road_lines, key=lambda line: line.distance(point))
            along = near.project(point)
            a, b = near.interpolate(max(0, along - 1)), near.interpolate(min(near.length, along + 1))
            angle = math.degrees(math.atan2(b.y - a.y, b.x - a.x))
            if district in (3, 4, 6, 7):
                angle = 0
            choices = TYPES[district][local_count % 3:] + TYPES[district][:local_count % 3]
            for asset, width, depth, height in choices:
                footprint = translate(rotate(box(-width/2, -depth/2, width/2, depth/2), angle), x, z)
                gap = 5 if district in (7, 9) else 3 if district == 4 else 2
                clearance = footprint.buffer(gap, join_style='mitre')
                if not buildable.covers(footprint) or not district_polys[district].covers(footprint):
                    continue
                if any(clearance.intersects(other) for other in occupied):
                    continue
                local_count += 1
                world_id = f'brackett/district_{district:02d}/building_{local_count:04d}'
                placements.append(dict(world_id=world_id, district_id=district, asset_id=asset,
                                       position=[round(x-630, 4), 0, round(z-355, 4)],
                                       yaw_degrees=round(-angle, 4), map_center=[x, z]))
                occupied.append(footprint)
                break
        counts[district] = local_count
    sectors = []
    for row in range(3):
        for column in range(4):
            tile = box(40 + column*300, 35 + row*220, 340 + column*300, 255 + row*220)
            ground = surface.intersection(tile)
            if ground.area < 1:
                continue
            sector_id = f'ground_{column:02d}_{row:02d}'
            parts = {name: triangles(shape.intersection(tile)) for name, shape in [
                ('land', surface), ('road', road_area), ('walk', walk_area), ('field', field)]}
            sectors.append(dict(asset_id=sector_id, parts=parts))
    inputs = ['draw_plan.py', '01-city-road-block-plan.svg', 'district-editor/brackett-districts.json']
    hashes = {str(REFERENCE.relative_to(ROOT) / name): hashlib.sha256((REFERENCE/name).read_bytes()).hexdigest() for name in inputs}
    source_macro = REFERENCE.parent / 'stage-02-city-structure/draw_maps.py'
    hashes[str(source_macro.relative_to(ROOT))] = hashlib.sha256(source_macro.read_bytes()).hexdigest()
    kit = [dict(asset_id=a, district_id=d, width=w, depth=z, height=h)
           for d, values in TYPES.items() for a, w, z, h in values]
    result = dict(schema=1, reference_hashes=hashes, map_origin_godot=[-630, 0, -355],
                  districts=districts, routes=routes, kit=kit, placements=placements, sectors=sectors,
                  summary=dict(road_count=len(routes), building_count=len(placements),
                               buildings_by_district=counts, ground_area_m2=surface.area,
                               road_area_m2=road_area.area, corridor_area_m2=corridor_area.area,
                               harbour_open_below_bridge=True, land_bounds=list(land.bounds)))
    (SOURCE/'authoring_plan.json').write_text(json.dumps(result, separators=(',', ':'))+'\n')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
