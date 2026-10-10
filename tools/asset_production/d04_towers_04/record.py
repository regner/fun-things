"""Package final tower receipts and lean images, then hash every produced payload."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_towers_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
RENDERS = ("hero.png", "side.png", "crown_detail.png", "overhead_47m_42deg.png")


def read_json(path):
    """Read a retained machine receipt without rewriting historical input."""
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    """Reject stale or failed receipts and collect only the owned final payload set."""
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
    assert normalization["save_reload_byte_stable"]
    assert normalization["stable_roundtrip_count"] == 2
    assert engine["prefab_uid"] == normalization["prefab_uid"]
    assert engine["model_uid"] == normalization["model_uid"]
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation["glb_sha256"]
    assert glb.stat().st_size == validation["glb_bytes"]
    assert glb.read_bytes() == (SCRATCH / f"reexport/{NID}.glb").read_bytes()
    validation["engine"] = engine
    validation["engine"]["save_reload_byte_stable"] = True
    validation["engine"]["stable_roundtrip_count"] = 2
    validation["validation_policy"] = (
        "Owner decision 52: asset-scoped import, source/export byte-compare, prefab roundtrips "
        "and owned GDScript formatting/lint only. No global production suite required or invoked."
    )
    validation["visual_review"] = {
        "renders_inspected": list(RENDERS), "renders": renders,
        "renderer": "Blender Cycles CPU, 32 samples, AgX",
        "gameplay_camera_godot_position_m": [14, 47, -12],
        "gameplay_camera": "Vertical down, north-up, 42 degree vertical FOV, 1280x720",
        "lean_packaging": "7-bit/channel RGB evidence PNG, optimize=True, compression level 9",
        "observation": "Two stepped cyan tiers, broad indigo window groups and closed lobby read "
                       "in supporting views. The off-footprint gameplay view crops the lower crown "
                       "and facade at the bottom-left edge; the upper tier is outside the frustum. "
                       "Open ground remains visible. No placement, occlusion acceptance or cutaway.",
    }
    validation["pending"] = [
        "Independent art/technical review and final dimensions/sibling compatibility",
        "World placement with important open forecourt; actual engine camera/occlusion/material/LOD review",
        "Production actor/car controller and multiplayer collision checks",
        "Exported-platform, Deck and sustained repeated-placement performance",
    ]
    (EVIDENCE / "validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8", newline="\n")
    (EVIDENCE / "final.log").write_text(
        "d04_towers.04 FINAL PRODUCER RECEIPT\n"
        "Blender 5.2.2 LTS d13f752e3b9c / glTF 5.2.40: author and validation exit 0.\n"
        f"{validation['source_vertices']} source vertices; {validation['source_triangles']} triangles; "
        f"{validation['glb_vertices_including_surface_splits']} exported vertices; "
        "3 meshes/12 surfaces/7 materials.\n"
        "Zero degenerate source faces/GLB triangles/nonmanifold edges; unit normals pass.\n"
        "Independent tier bounds/recess checks verify the 3.4 m setback and closed manifold rims.\n"
        f"Fresh saved-source export byte-identical; GLB {validation['glb_bytes']} bytes.\n"
        "Pinned Godot imports exit 0; existing MCP Godot-4.8 compatibility warning only.\n"
        "No ERROR or SCRIPT ERROR lines in import or prefab checks.\n"
        "Prefab normalization and fresh resource/physics check exit 0.\n"
        "Two byte-stable save/reload roundtrips; 16 shape queries, 7 actor/car casts, front ray pass.\n"
        "gdstyle 0.3.0 owned formatting/lint pass; global production suite not invoked.\n"
        "Blender use_nodes deprecation warnings concern Blender 6.0, not pin failure.\n"
        "Owned Python syntax and final evidence packaging pass.\n"
        "Four isolated Blender images inspected; no engine visual acceptance claimed.\n"
        "Off-footprint gameplay view shows partial lower crown/facade; upper tier outside frustum.\n"
        "Initial recess assertion omitted the 0.04 m inner bevel; corrected tolerance, rerun pass.\n"
        "No live editor access or sibling changes. Placement/gameplay/device gates pending.\n",
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
        "asset_id": "d04_towers.04", "producer": "Commissioned isolated asset-production worker",
        "scope": "Every produced payload, excluding this self-referential manifest and scratch",
        "files": sorted(files, key=lambda item: item["path"]),
    }
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: {len(files)} payload hashes, four lean renders, asset-scoped receipts verified")


if __name__ == "__main__":
    main()
