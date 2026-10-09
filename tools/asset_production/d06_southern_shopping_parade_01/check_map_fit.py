"""Measure a non-placed candidate against the frozen district polygon and road triangles.

Uses Shapely, already used by the repository's greybox authoring tools. This does
not author placement, migrate saved identities or certify current road-tool clearance.
"""
import hashlib
import json
from pathlib import Path

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_01"
PLAN = ROOT / "art/source/models/brackett_greybox/authoring_plan.json"
plan = json.loads(PLAN.read_text())
district = Polygon(next(row["points"] for row in plan["districts"] if row["id"] == 6))
roads = unary_union([Polygon(triangle) for sector in plan["sectors"]
                     for triangle in sector["parts"].get("road", [])])
# Concept-map axes: +X east, +Y south. Candidate root map centre (528,499), yaw zero.
# West band reserves 1.20 m fitting volume before a 3 m independent walking band.
envelopes = {
    "visual_shell": box(518.955,468.965,537.040,529.035),
    "west_walk_3m_beyond_fitting_reservation": box(514.8,469,517.8,529),
    "east_walk_3m": box(537.04,469,540.04,529),
    "north_forecourt_18m_by_9_965m": box(519,459,537,468.965),
}
measurements = {}
for name, polygon in envelopes.items():
    assert district.covers(polygon), name
    overlap = polygon.intersection(roads).area
    assert overlap == 0, (name, overlap)
    measurements[name] = {
        "map_bounds_m": list(polygon.bounds), "inside_district": True,
        "carriageway_overlap_m2": overlap,
        "minimum_distance_to_frozen_carriageway_m": polygon.distance(roads),
    }
report = {
    "status": "PASS candidate-only frozen-map checks; NOT placement or movement acceptance",
    "source": str(PLAN.relative_to(ROOT)).replace("\\", "/"),
    "source_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
    "candidate_map_centre_east_south_m": [528,499],
    "candidate_godot_root_m": [-102,0,144], "candidate_yaw_degrees": 0,
    "measurements": measurements,
    "affected_existing_ids_unchanged": [f"brackett/district_06/building_{i}"
                                         for i in ("0001","0008","0005")],
    "limits": "Frozen greybox carriageway only, not current road-tool surfaces, sidewalks, "
              "bridge landing engineering, fitted frontages, navigation or actor/vehicle sweeps. "
              "No map, scene, identity, road or boundary was modified.",
}
output = Path(f"C:/tmp/ft/assets/{NID}/map-fit.json")
output.write_text(json.dumps(report,indent=2)+"\n",newline="\n")
print(json.dumps(report,indent=2))
