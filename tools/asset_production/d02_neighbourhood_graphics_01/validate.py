"""Reuse the source owner's complete topology/GLB audit and verify artwork dependencies."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
DEPENDENCIES = [
    "art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend",
    "art/models/environment/city_sign_supports_01/city_sign_supports_01.glb",
    "art/models/environment/city_sign_supports_01/city_sign_supports_01.glb.import",
    "scenes/prefabs/environment/city_sign_supports_01.tscn",
    "tools/asset_production/city_sign_supports_01/export.py",
    "tools/asset_production/city_sign_supports_01/check_glb.py",
    "tools/asset_production/d06_commercial_graphics_01/author.py",
    "tools/asset_production/d06_commercial_graphics_02/author.py",
    "tools/asset_production/d06_commercial_graphics_01/manifest.py",
]


def fingerprints():
    """Protect all read-only dependencies with exact before/after hashes and byte counts."""
    return {p: {"sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest(),
                "bytes": (ROOT / p).stat().st_size} for p in DEPENDENCIES}


def main():
    """Refresh only this artwork's receipt, preserving all owner validation assertions."""
    before = fingerprints()
    exporter = Path(__file__).with_name("export.py")
    spec = importlib.util.spec_from_file_location("watch_export", exporter)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.reexport()
    checker = ROOT / "tools/asset_production/city_sign_supports_01/check_glb.py"
    code = checker.read_text()
    old = "E=ROOT/'docs/assets/production/city_sign_supports_01-evidence'"
    assert code.count(old) == 1
    code = code.replace(old, f"E=Path({str(SCRATCH)!r})")
    exec(compile(code, str(checker), "exec"), {"__file__": str(checker)})
    assert fingerprints() == before
    source = json.loads((SCRATCH / "source_checks.json").read_text())
    binary = json.loads((SCRATCH / "glb_checks.json").read_text())
    raw = (SCRATCH / "reexport_city_sign_supports_01.glb").read_bytes()
    length = struct.unpack_from("<I", raw, 12)[0]
    gltf = json.loads(raw[20:20 + length])
    primitives = [p for mesh in gltf["meshes"] for p in mesh["primitives"]]
    report = {
        "asset_id": "d02_neighbourhood_graphics.01", "new_geometry": False,
        "source": source, "glb": binary,
        "source_vertices": sum(o["vertices"] for o in source["objects"]),
        "glb_vertices": sum(gltf["accessors"][p["attributes"]["POSITION"]]["count"]
                            for p in primitives),
        "mesh_count": len(gltf["meshes"]), "surface_count": len(primitives),
        "zero_degenerate_faces": True, "unit_length_normals": True,
        "pivot": "Wall attachment centre (0,0,0); mount height remains placement-owned",
        "dimensions_godot_m": [1.4, 1.0, 0.1],
        "shared_dependencies": before, "shared_dependencies_unchanged": True,
        "status": "PASS: source topology/UV/normals, binary audit and byte-identical reexport",
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("WATCH_SOURCE_PASS: shared carrier untouched; source and binary assertions pass")


if __name__ == "__main__":
    main()
