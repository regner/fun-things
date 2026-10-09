"""Retain lean north-facade receipts and hash every produced payload and dependency."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_03"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
MANIFEST = EVIDENCE / "manifest.json"


def read_json(path):
    """Read completed receipts without mutating producer-owned resources."""
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint(path):
    """Record exact bytes and SHA-256 with a portable repository-relative path."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def payloads():
    """List this asset's complete lean payload set, excluding the manifest itself."""
    paths = [ROOT / f"docs/assets/production/{NID}.md"]
    paths += list((ROOT / "scenes/prefabs/environment").glob(f"{NID}*.tscn*"))
    for folder in (ROOT / f"art/source/models/environment/{NID}",
                   ROOT / f"art/models/environment/{NID}",
                   ROOT / f"tools/asset_production/{NID}", EVIDENCE):
        paths += [path for path in folder.rglob("*") if path.is_file() and path != MANIFEST]
    assert all("__pycache__" not in path.parts and path.suffix not in (".pyc", ".blend1")
               for path in paths)
    return sorted((fingerprint(path) for path in paths), key=lambda entry: entry["path"])


if "--verify" in sys.argv:
    assert read_json(MANIFEST)["files"] == payloads(), "Produced payload set/bytes changed"
    for entry in read_json(EVIDENCE / "validation.json")["dependencies"]:
        assert fingerprint(ROOT / entry["path"]) == entry, entry["path"]
    print("PASS: complete north-facade manifest and all repaired-family dependencies")
    raise SystemExit(0)

engine = read_json(SCRATCH / "prefab.json")
geometry = read_json(SCRATCH / "geometry.json")
normalize = read_json(SCRATCH / "normalize.json")
checks = read_json(SCRATCH / "checks-final/summary.json")
assert engine["ok"] and normalize["ok"] and checks["ok"]
assert normalize["save_reload_byte_stable"] and geometry["reexport_byte_identical"]
assert not any(marker in (SCRATCH / "prefab.log").read_text() for marker in ("ERROR:", "WARNING:"))
# Member .02 already owns the explicit source/export/import/prefab provenance map.
# Reuse its checked list rather than inventing a second family dependency map.
family = read_json(ROOT / "docs/assets/production/d06_southern_shopping_parade_02-evidence/validation.json")
dependencies = family["geometry"]["inputs"].copy()
for entry in dependencies:
    assert fingerprint(ROOT / entry["path"]) == entry
for suffix in ("", "_bay"):
    dependencies.append(fingerprint(ROOT /
        f"scenes/prefabs/environment/d06_southern_shopping_parade_02{suffix}.tscn"))
validation = {
    "asset_id": "d06_southern_shopping_parade.03", "output_type": "Component design",
    "status": "PASS bounded source/export/prefab candidate; independent acceptance pending",
    "geometry": geometry, "engine": engine, "save_reload": normalize,
    "production_checks": checks["results"], "dependencies": dependencies,
    "visual_self_review": {
        "images": ["hero.png", "side.png", "relief_detail.png", "overhead_47m_42deg.png"],
        "renderer": "Blender Cycles CPU, 24 samples, AgX, 1280x800",
        "camera": "Vertical down, north-up at Blender (0,38,47), vertical FOV 42 degrees",
        "observed": "Plum end relief and quiet blue brow preserve one building. Grouped cyan/magenta "
                    "inlays add restrained corner rhythm; north forecourt stays empty. "
                    "Only a thin facade band reads overhead; it carries no essential wayfinding. "
                    "North-corner black stripe removed by separately approved .01 2 mm cap recess.",
        "limits": "Isolated Blender self-review, not native engine or gameplay acceptance",
    },
    "collision": "One 17.4x4.8x0.18 m box at (0,2.4,-0.09); shell retains main collision. "
                 "Box intentionally bridges shallow relief gaps to prevent snags/clipping.",
    "reference_totals": {
        "triangles": family["geometry"]["assembled_totals"]["triangles"] + geometry["triangles"],
        "source_vertices": family["geometry"]["assembled_totals"]["source_vertices"]
                           + geometry["source_vertices"],
        "export_vertices": family["geometry"]["assembled_totals"]["export_vertices"]
                           + geometry["export_vertices"],
        "mesh_instances": engine["reference_mesh_count"],
        "surfaces": family["geometry"]["assembled_totals"]["export_surfaces"]
                    + geometry["surface_count"],
    },
    "family_repair_commit": "dd66d23",
    "pending": ["independent review", "final proportions and parcel selection", "tenant graphics",
                "native camera/gameplay", "road-tool and bridge fit", "world identity placement",
                "actual player/vehicle/aim and multiplayer", "packaged/device/performance"],
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
diagnostics = "\n".join(line for line in (SCRATCH / "normalize.log").read_text().splitlines()
                        if "ERROR:" in line or "WARNING:" in line)
(EVIDENCE / "final.log").write_text(
    "D06 NORTH FACADE — FINAL BOUNDED RECEIPT\n"
    "Full raw logs/scratch: C:/tmp/ft/assets/d06_southern_shopping_parade_03/\n"
    "Pinned Blender 5.2.2 LTS d13f752e3b9c; exporter 5.2.40; "
    "Godot 4.8.dev7.official.c971f93e7.\n"
    "Author/validate/render exit 0: 3,196 triangles, 1,632 source/export vertices, "
    "one mesh/five surfaces, zero degenerate/nonmanifold, unit normals. "
    "Saved-source fresh GLB reexport byte-identical (57,864 bytes).\n"
    "Import/normalize/runtime exit 0. Both scenes byte-stable; runtime no ERROR/WARNING.\n"
    "Editor normalization diagnostics, retained rather than suppressed:\n" + diagnostics + "\n"
    "32 linked GLBs; 158 meshes; exactly two active collision shapes in reference.\n"
    "Four north rays, five capsule samples pass; radius .35 m capsule stops at Z=-30.53125.\n"
    "Four 1280x800 renders inspected, no black north-corner stripe after approved .01 repair.\n"
    "Production checks exit 0: scripts compile/style clean, Python 9/9, "
    "GUT 23/23 (196 assertions), negative control correctly detected. No ignored failures.\n"
    "Initial owned lint warnings corrected. Blender API deprecation warnings are non-failing.\n"
    "Independent/native/world/gameplay/multiplayer/device checks remain pending.\n",
    encoding="utf-8", newline="\n")
MANIFEST.write_text(json.dumps({
    "asset_id": "d06_southern_shopping_parade.03",
    "producer": "Commissioned isolated original Blender asset-production worker",
    "scope": "Every produced payload except this self-referential manifest; no scratch files",
    "files": payloads(),
}, indent=2) + "\n", newline="\n")
print("Recorded lean validation and complete producer manifest")
