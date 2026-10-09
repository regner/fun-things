"""Measure saved source geometry, markers and authored export members in Blender."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

source = Path(__file__).resolve().parent
record = json.loads((source / "source_manifest.json").read_text())
for name in record["collections"]:
    rows = []
    for obj in bpy.data.collections[name].all_objects:
        row = {"name": obj.name, "type": obj.type,
               "location_blender": list(obj.location), "scale": list(obj.scale)}
        if obj.type == "MESH":
            vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
            mapped = [(v.x, v.z, -v.y) for v in vertices]
            row["aabb_godot_min"] = [min(v[i] for v in mapped) for i in range(3)]
            row["aabb_godot_max"] = [max(v[i] for v in mapped) for i in range(3)]
            row["triangles"] = len(obj.data.polygons)
            row["material"] = obj.data.materials[0].name
        else:
            v = obj.matrix_world.translation
            row["position_godot"] = [v.x, v.z, -v.y]
            row["basis_godot"] = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            if "contact_normal_blender" in obj:
                n = obj["contact_normal_blender"]
                row["contact_normal_godot"] = [n[0], n[2], -n[1]]
        rows.append(row)
    record["collections"][name] = rows
(source / "source_manifest.json").write_text(json.dumps(record, indent=2) + "\n")
print("DOCK_THUMPER_SOURCE_MEASURED", bpy.data.filepath)
