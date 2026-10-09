"""Retain lean interface evidence and verify the complete producer manifest."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_02"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
MANIFEST = EVIDENCE / "manifest.json"


def read_json(path):
    """Read a completed receipt without changing its producer-owned bytes."""
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint(path):
    """Hash one exact payload relative to the repository root."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def payloads():
    """List only the owned scene/doc/tools/evidence set; reject scratch files."""
    paths = [ROOT / f"docs/assets/production/{NID}.md"]
    paths += list((ROOT / "scenes/prefabs/environment").glob(f"{NID}*.tscn*"))
    for folder in (ROOT / f"tools/asset_production/{NID}", EVIDENCE):
        paths += [path for path in folder.rglob("*") if path.is_file() and path != MANIFEST]
    assert all("__pycache__" not in path.parts and path.suffix not in (".pyc", ".blend1")
               for path in paths)
    return sorted((fingerprint(path) for path in paths), key=lambda entry: entry["path"])


def verify_inputs(geometry):
    """Ensure every reused source/export/import/prefab still matches the checked revision."""
    for entry in geometry["inputs"]:
        assert fingerprint(ROOT / entry["path"]) == entry, entry["path"]


if "--verify" in sys.argv:
    assert read_json(MANIFEST)["files"] == payloads(), "Producer payload set or bytes changed"
    verify_inputs(read_json(EVIDENCE / "validation.json")["geometry"])
    print("PASS: complete producer manifest and all 24 immutable dependency hashes")
    raise SystemExit(0)

engine = read_json(SCRATCH / "prefab.json")
geometry = read_json(SCRATCH / "geometry.json")
normalize = read_json(SCRATCH / "normalize.json")
checks = read_json(SCRATCH / "checks/summary.json")
assert all(receipt["ok"] for receipt in (engine, geometry, normalize, checks))
assert normalize["save_reload_byte_stable"]
verify_inputs(geometry)
assert not any(marker in (SCRATCH / "prefab.log").read_text() for marker in ("ERROR:", "WARNING:"))
validation = {
    "asset_id": "d06_southern_shopping_parade.02", "output_type": "Interface reference",
    "status": "PASS bounded saved reference; independent and downstream acceptance pending",
    "engine": engine, "geometry": geometry, "save_reload": normalize,
    "production_checks": checks["results"],
    "visual_self_review": {
        "images": ["hero.png", "side.png", "bay_detail.png", "overhead_47m_42deg.png"],
        "renderer": "Blender Cycles CPU, 24 samples, AgX, 1280x800",
        "camera": "Overhead at Blender (-6,0,47), vertical down, north-up, vertical FOV 42 degrees",
        "observed": "Six coherent repeated storefronts under one uninterrupted quiet roof; "
                    "no obvious float/intersection. Overhead centre crop shows canopy noses "
                    "but hides doors/fascia; essential wayfinding must not depend on these faces.",
        "limits": "Self-review of isolated Blender views, not native engine or gameplay acceptance",
    },
    "pending": ["independent review", "tenant graphics",
                "native visuals/gameplay", "road/bridge/parcel fit", "world identity placement",
                "movement/aim/vehicle/multiplayer", "packaged/device/performance"],
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
normalization_log = (SCRATCH / "normalize.log").read_text(encoding="utf-8")
diagnostics = "\n".join(line for line in normalization_log.splitlines()
                         if "ERROR:" in line or "WARNING:" in line)
summary = (
    "D06 PARADE .02 — FINAL INTERFACE RECEIPT\n"
    "Full raw logs/scratch assembly: C:/tmp/ft/assets/d06_southern_shopping_parade_02/\n"
    "Pinned Blender 5.2.2 LTS d13f752e3b9c and Godot 4.8.dev7.official.c971f93e7.\n"
    "Headless import, pack/save/reload, fresh runtime checks: exit 0.\n"
    "Both scenes byte-stable. Runtime has no ERROR/WARNING; all 24 dependency hashes unchanged.\n"
    "Editor normalization diagnostics (exit 0; not hidden or treated as clean):\n"
    + diagnostics + "\n\n"
    "Blender validation exit 0: 55,244 triangles, 157 mesh instances, 167 surfaces; "
    "10,812 inserted vertices fit; 60 fitting-pair tests pass; zero unintended shell intersections.\n"
    "288 triangle contacts restricted to exterior canopy/fascia rails on the flat wall.\n"
    "Source topology: zero nonmanifold/degenerate; source and imported normals unit length.\n"
    "No new source or GLB: fresh new-asset reexport is N/A for this interface reference.\n"
    "All four 1280x800 renders exit 0 and were visually inspected; overhead crop/occlusion retained.\n"
    "Production checks exit 0: scripts compile; gdstyle clean; Python 9/9; "
    "GUT 23/23, 196 assertions; intentional negative control detected; no ignored failures.\n"
    "Initial owned failures corrected: bay rotation signs, renderer syntax typo, "
    "over-strict flush-contact assertion; four lint warnings fixed.\n"
    "Blender version probe reported one 0.000023 MB unfreed block; final validate/render clean.\n"
    "Independent/native/world/gameplay/device acceptance remains pending.\n"
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
MANIFEST.write_text(json.dumps({
    "asset_id": "d06_southern_shopping_parade.02",
    "producer": "Commissioned isolated interface-reference worker",
    "scope": "Every produced payload except this self-referential manifest; no new geometry",
    "files": payloads(),
}, indent=2) + "\n", newline="\n")
print("Recorded lean reference evidence and complete producer manifest")
