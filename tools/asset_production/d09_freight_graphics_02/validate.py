"""Reuse storage-owned source validators with scratch receipts; audit both outward UV faces."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_02"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def fingerprint(path):
    """Measure immutable shared dependencies before and after validation."""
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Call each carrier's validator without writing any carrier-owned artifact."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    dependencies = [ROOT / "tools/assets/blender/export_settings.json",
                    ROOT / "tools/asset_production/d09_freight_graphics_01/author.py"]
    for number in (1, 2):
        carrier = f"d09_storage_{number:02d}"
        dependencies.extend([
            ROOT / f"art/source/models/environment/{carrier}/{carrier}.blend",
            ROOT / f"art/models/environment/{carrier}/{carrier}.glb",
            ROOT / f"art/models/environment/{carrier}/{carrier}.glb.import",
            ROOT / f"scenes/prefabs/environment/{carrier}.tscn",
            ROOT / f"tools/asset_production/{carrier}/validate.py",
            ROOT / f"tools/asset_production/{carrier}/export.py",
        ])
    before = {p.relative_to(ROOT).as_posix(): fingerprint(p) for p in dependencies}
    reports = {}
    for number, variant, length in [(1, "long", 12), (2, "short", 6)]:
        carrier = f"d09_storage_{number:02d}"
        script = ROOT / f"tools/asset_production/{carrier}/validate.py"
        spec = importlib.util.spec_from_file_location(carrier + "_validator", script)
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        validator.EVIDENCE = SCRATCH / f"{carrier}_source.json"
        validator.SCRATCH = SCRATCH / f"{carrier}_reexport"
        validator.main()
        report = json.loads(validator.EVIDENCE.read_text())
        raw = validator.EXPORT.read_bytes()
        json_length = struct.unpack_from("<I", raw, 12)[0]
        document = json.loads(raw[20:20+json_length])
        binary = raw[28+json_length:]
        face = document["meshes"][0]["primitives"][3]
        positions = validator.accessor(document, binary, face["attributes"]["POSITION"])
        normals = validator.accessor(document, binary, face["attributes"]["NORMAL"])
        uvs = validator.accessor(document, binary, face["attributes"]["TEXCOORD_0"])
        centre_z = -length / 2 + 1.35
        for position, normal, uv in zip(positions, normals, uvs):
            x, y, z = position
            side = 1 if x > 0 else -1
            assert abs(x - side*1.23) < 1e-5
            # The unchanged carrier uses weighted corner normals, slightly rounded at edges.
            assert normal[0]*side > .99, "Shading normals must face outward"
            assert abs(y - (2.19 - uv[1]*.46)) < 1e-5, "Upright GLB V"
            assert abs(z - (centre_z - side*(uv[0]-.5)*1.4)) < 1e-5, "Outside L-to-R U"
        indices = [i[0] for i in validator.accessor(document, binary, face["indices"])]
        for offset in range(0, len(indices), 3):
            a, b, c = [Vector(positions[i]) for i in indices[offset:offset+3]]
            geometric_normal = (b-a).cross(c-a).normalized()
            assert abs(geometric_normal.x - (1 if a.x > 0 else -1)) < 1e-5
        report["artwork_face_audit"] = {
            "dimensions_m": [1.4, .46], "centres_godot_m": [[-1.23, 1.96, centre_z],
                                                               [1.23, 1.96, centre_z]],
            "outward_normals": ["-X", "+X"], "upright_outside_left_to_right_uv": True,
            "face_surface": 3, "face_triangles": 4,
        }
        reports[variant] = report
    assert before == {p.relative_to(ROOT).as_posix(): fingerprint(p) for p in dependencies}
    output = {"asset_id": "d09_freight_graphics.02", "status": "PASS",
              "new_geometry": False, "shared_dependencies_unchanged": True,
              "dependencies": before, "carriers": reports,
              "blender": bpy.app.version_string, "exporter": "5.2.40"}
    (EVIDENCE / "validation.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print("CONTAINER_SOURCE_PASS: both source audits, fresh byte-identical exports, outward face UVs")


if __name__ == "__main__":
    main()
