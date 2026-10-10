"""Package verified podium receipts and lean renders; hash every final produced payload."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_podiums_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
RENDERS = ("hero.png", "side.png", "entry_detail.png", "overhead_47m_42deg.png")


def read_json(path):
    """Read a machine receipt without changing its input."""
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    """Reject stale geometry or failed engine receipts before creating the manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compress-renders", action="store_true")
    args = parser.parse_args()
    renders = []
    for name in RENDERS:
        path = EVIDENCE / name
        with Image.open(path) as source:
            expected = (1280, 720) if name.startswith("overhead") else (1152, 648)
            assert source.size == expected
            if args.compress_renders:
                image = ImageOps.posterize(source.convert("RGB"), bits=7)
                image.save(path, optimize=True, compress_level=9)
        assert path.stat().st_size <= 410000, (name, path.stat().st_size)
        renders.append({"file": name, "pixels": list(expected), "bytes": path.stat().st_size})
    validation = read_json(EVIDENCE / "validation.json")
    engine = read_json(SCRATCH / "prefab-fresh-final.json")
    normalization = read_json(SCRATCH / "prefab-check.json")
    assert engine["ok"] and not engine["failures"]
    assert normalization["ok"] and not normalization["failures"]
    assert normalization["save_reload_byte_stable"]
    assert normalization["stable_roundtrip_count"] == 2
    assert engine["prefab_uid"] == normalization["prefab_uid"]
    assert engine["model_uid"] == normalization["model_uid"]
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation["glb_sha256"]
    assert glb.stat().st_size == validation["glb_bytes"]
    assert glb.read_bytes() == (SCRATCH / f"reexport/{NID}.glb").read_bytes()
    for name in ("import-final.log", "prefab-normalize-final.log", "prefab-fresh-final.log"):
        text = (SCRATCH / name).read_text(encoding="utf-8")
        assert "ERROR" not in text, (name, "Engine diagnostic requires review")
    validation["engine"] = engine
    validation["engine"]["save_reload_byte_stable"] = True
    validation["engine"]["stable_roundtrip_count"] = 2
    validation["visual_review"] = {
        "renders_inspected": list(RENDERS), "renders": renders,
        "renderer": "Blender Cycles CPU, 32 samples, AgX",
        "gameplay_camera_godot_position_m": [0, 47, 0],
        "gameplay_camera": "Vertical down, north-up, 42 degree vertical FOV, 1280x720",
        "lean_packaging": "7-bit/channel RGB, PNG optimize=True, compression level 9",
        "observation": "The stepped slate/blue mass and deep covered entry read in supporting "
                       "views. Overhead preserves the broad front and side roof setbacks, quiet "
                       "upper cap and entry canopy. Magenta lintel is an elevation detail, not "
                       "an overhead wayfinding cue. Initial coplanar lower-roof faces caused "
                       "black render artifacts; vertical separation corrected them before final "
                       "capture. No engine visual or populated-street acceptance claimed.",
    }
    validation["pending"] = [
        "Independent art/technical review and layout confirmation of provisional dimensions",
        "World placement preserving grid corners, inter-site gaps and open forecourts",
        "Actual engine camera/material/normal/LOD review and actor/target visibility",
        "Production controller, multiplayer, packaged build and Deck performance checks",
    ]
    (EVIDENCE / "validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8", newline="\n")
    (EVIDENCE / "final.log").write_text(
        "d04_podiums.02 FINAL PRODUCER RECEIPT\n"
        "Blender 5.2.2 LTS d13f752e3b9c / glTF 5.2.40: author and validator exit 0.\n"
        f"{validation['source_vertices']} source vertices; {validation['source_triangles']} triangles; "
        f"{validation['glb_vertices_including_surface_splits']} exported vertices; 1 mesh/7 surfaces.\n"
        "Zero degenerate source faces/GLB triangles/nonmanifold edges; unit normals pass.\n"
        f"Fresh export byte-identical; {validation['glb_bytes']} GLB bytes.\n"
        "Pinned Godot import, normalization and fresh resource/physics check exit 0; no ERROR lines.\n"
        "Two byte-stable save/reload roundtrips; 18 shape queries, 8 actor/car casts, entry ray pass.\n"
        "Owned gdstyle 0.3.0 formatting and lint pass; global production suite not invoked (decision 52).\n"
        "Four isolated Blender images inspected; lean RGB packaging preserves geometry/framing.\n"
        "Initial lower roof was coplanar with its supporting mass; fixed before final captures.\n"
        "First fresh load preceded the post-normalization UID scan and failed its UID assertion; "
        "post-save pinned import registered the scene, and the fresh check then passed.\n"
        "Initial receipt script had malformed newline escapes; corrected before packaging.\n"
        "Blender use_nodes future-6.0 deprecation warning retained in scratch; full author/validator "
        "processes exited cleanly.\n"
        "No owner's live editor accessed; headless project autoload logs are not live-editor use.\n"
        "Placement, actual controllers/network/device/render review remain pending.\n",
        encoding="utf-8", newline="\n")
    roots = [
        ROOT / f"art/source/models/environment/{NID}",
        ROOT / f"art/models/environment/{NID}",
        ROOT / f"tools/asset_production/{NID}", EVIDENCE,
        ROOT / f"docs/assets/production/{NID}.md",
        ROOT / f"scenes/prefabs/environment/{NID}.tscn",
    ]
    files = []
    for path in roots:
        for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
            if not item.is_file() or item.name == "manifest.json" or "__pycache__" in item.parts:
                continue
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {
        "asset_id": "d04_podiums.02", "producer": "Commissioned isolated asset-production worker",
        "scope": "Every produced payload except this self-referential manifest and scratch",
        "files": sorted(files, key=lambda item: item["path"]),
    }
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: {len(files)} payload hashes, four lean renders, asset-scoped receipts verified")


if __name__ == "__main__":
    main()
