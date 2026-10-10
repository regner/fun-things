"""Validate unchanged source/export and fitted instances; no sibling payload is written."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
import assembly

CONTACT_TOLERANCE_M = 0.000001


def wheel_contact_only(vertices_a, vertices_b, triangles, mesh, first, second):
    """Accept only touching rubber sidewalls separated by a common X plane within 1 micrometre."""
    if any(mesh.loop_triangles[index].material_index != 2 for index in (first, second)):
        return False
    a = [vertices_a[index] for index in triangles[first]]
    b = [vertices_b[index] for index in triangles[second]]
    # A wheel sidewall is tangent, not penetrating: one triangle stays in each halfspace.
    x_separated = (max(v.x for v in a) <= min(v.x for v in b) + CONTACT_TOLERANCE_M
                   or max(v.x for v in b) <= min(v.x for v in a) + CONTACT_TOLERANCE_M)
    on_wheels = all(0 <= v.z <= .191 and abs(abs(v.x) - .25) < .005 for v in a + b)
    return x_separated and on_wheels


def main():
    """Reuse the component validator, then measure each actual saved assembly placement."""
    assembly.EVIDENCE.mkdir(parents=True, exist_ok=True)
    assembly.SCRATCH.mkdir(parents=True, exist_ok=True)
    component = assembly.load_tool("trolley_validate",
        "tools/asset_production/d07_trolley_shelter_02/validate.py")
    component.EVIDENCE = assembly.SCRATCH / "dependency-validation.json"
    component.SCRATCH = assembly.SCRATCH / "reexport"
    component.main()
    dependency = json.loads(component.EVIDENCE.read_text())
    obj = bpy.data.objects["D07TrolleyShelter02_Mesh"]
    mesh = obj.data
    mesh.calc_loop_triangles()
    triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
    copies = []
    for name, (x, y, z) in assembly.placements():
        vertices = [obj.matrix_world @ vertex.co + Vector((x, -z, y)) for vertex in mesh.vertices]
        tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0)
        copies.append((name, vertices, tree))
    all_vertices = [vertex for _, vertices, _ in copies for vertex in vertices]
    low = [min(vertex[i] for vertex in all_vertices) for i in range(3)]
    high = [max(vertex[i] for vertex in all_vertices) for i in range(3)]
    godot_min = [low[0], low[2], -high[1]]
    godot_max = [high[0], high[2], -low[1]]
    assert all(abs(a - b) < .001 for a, b in zip(godot_min + godot_max,
        [-.34, 0, -1.245, .34, 1.08, 1.245]))
    pair_checks = []
    for i, (name_a, vertices_a, tree_a) in enumerate(copies):
        for name_b, vertices_b, tree_b in copies[i + 1:]:
            contacts = tree_a.overlap(tree_b)
            unintended = [(a, b) for a, b in contacts if not wheel_contact_only(
                vertices_a, vertices_b, triangles, mesh, a, b)]
            assert not unintended, (name_a, name_b, unintended[:5])
            pair_checks.append({"instances": [name_a, name_b],
                "bvh_triangle_pairs": len(contacts), "tangent_rubber_sidewall_pairs": len(contacts),
                "unintended_crossing_pairs": 0})
    report = {
        "asset": "d07_trolley_shelter.03", "output_type": "Assembly reference",
        "source_export_status": "passed", "dependency_validation": dependency,
        "placements_godot_m": dict(assembly.placements()), "pivot_m": [0, 0, 0],
        "godot_bounds_min_m": godot_min, "godot_bounds_max_m": godot_max,
        "dimensions_m": [.68, 1.08, 2.49], "pitch_m": .72, "instance_count": 3,
        "unique_meshes": 1, "mesh_instances": 3, "surfaces_per_instance": 4,
        "triangles_all_instances": 3 * dependency["triangles"],
        "source_vertices_all_instances": 3 * dependency["source_vertices"],
        "export_vertices_all_instances": 3 * dependency["export_vertices"],
        "new_meshes_or_exports": 0, "pair_checks": pair_checks,
        "contact_tolerance_m": CONTACT_TOLERANCE_M,
        "fit_note": "Shallow nesting; adjacent rubber sidewalls touch at X +/-0.25m. "
                    "No crossing beyond 1 micrometre halfspace tolerance; no scale/geometry edits.",
    }
    (assembly.EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("D07_TROLLEY_SHELTER_03_SOURCE_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
