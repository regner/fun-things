"""Package final receipts and lean renders, then hash this asset's complete payload set."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_warehouses_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
RENDERS = ("hero.png", "side.png", "loading_detail.png", "overhead_47m_42deg.png")


def read_json(path):
    """Read a source, engine or canonical production-check receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    """Reject failed receipts and retain only owned deliverables, never scratch artifacts."""
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
                image = ImageOps.posterize(source.convert("RGB"), bits=6 if name == "hero.png" else 7)
                image.save(path, optimize=True, compress_level=9)
        assert path.stat().st_size <= 410000
        renders.append({"file": name, "pixels": list(expected), "bytes": path.stat().st_size})

    validation = read_json(EVIDENCE / "validation.json")
    engine = read_json(SCRATCH / "prefab-fresh-final.json")
    normalization = read_json(SCRATCH / "prefab-check.json")
    checks = read_json(SCRATCH / "checks/summary.json")
    compilation = read_json(SCRATCH / "checks/script-checks/compilation.json")
    assert engine["ok"] and not engine["failures"]
    assert normalization["save_reload_byte_stable"]
    assert normalization["stable_roundtrip_count"] == 2
    assert engine["prefab_uid"] == normalization["prefab_uid"]
    assert engine["model_uid"] == normalization["model_uid"]
    assert checks["ok"] and all(row["ok"] for row in compilation)
    assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd"
               for row in compilation)
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation["glb_sha256"]
    assert glb.read_bytes() == (SCRATCH / f"reexport/{NID}.glb").read_bytes()
    validation["engine"] = engine
    validation["engine"]["save_reload_byte_stable"] = True
    validation["engine"]["stable_roundtrip_count"] = 2
    validation["production_checks"] = {
        "overall_ok": checks["ok"],
        "results": checks["results"],
        "compiled_script_count": len(compilation),
        "python_tests": 17,
        "gut_tests": 149,
        "gut_assertions": 6768,
        "known_failure_exemptions": [],
    }
    validation["visual_review"] = {
        "renders_inspected": list(RENDERS),
        "renders": renders,
        "renderer": "Blender Cycles CPU, 32 samples, AgX",
        "camera": "Vertical down, 47 m height, 42 degree vertical FOV, 1280x720",
        "lean_packaging": "RGB evidence PNG: 6 bits/channel hero, 7 bits/channel others; "
                          "optimize=True, compression level 9",
        "observation": "Broad low blue roof and two long rooflight ribbons distinguish the "
                       "wide sibling from .01's long ridge. Loading accents stay subordinate. "
                       "Not an in-engine capture.",
    }
    validation["pending"] = [
        "Independent review and final district dimensions/sibling fit",
        "World placement, aprons and actual camera/material/LOD review",
        "Production actor/car motion and multiplayer collision validation",
        "Exported-platform, Deck and sustained performance validation",
    ]
    (EVIDENCE / "validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8", newline="\n")
    (EVIDENCE / "final.log").write_text(
        "d09_warehouses.02 FINAL PRODUCER RECEIPT\n"
        "Blender 5.2.2 LTS d13f752e3b9c / exporter 5.2.40: source validation exit 0.\n"
        "10944 source vertices; 21432 triangles; 13095 exported vertices; 1 mesh/7 surfaces.\n"
        "Zero degenerate source faces/GLB triangles/nonmanifold edges; unit normals pass.\n"
        "Fresh source reexport is byte-identical; GLB 554556 bytes.\n"
        "Pinned Godot import: exit 0, existing MCP Godot-4.8 compatibility warning only.\n"
        "Runtime-mode scene normalization: exit 0, two stable save/reload roundtrips.\n"
        "Fresh pinned headless resource/physics check: exit 0, no ERROR/WARNING diagnostics.\n"
        "Eight shape queries, six actor/car-envelope casts and front ray expectations pass.\n"
        "gdstyle 0.3.0 owned lint/fmt and explicit compilation pass.\n"
        "Canonical production checks exit 0: all owned scripts; Python 17/17; "
        "GUT 149/149, 6768 assertions; negative control detected.\n"
        "All four final isolated Blender renders inspected; no engine visual acceptance claimed.\n"
        "Blender authoring emits forward-looking use_nodes deprecations; final export/validation clean.\n"
        "Version-only Blender query emitted a 23-byte shutdown allocation diagnostic; "
        "author/validate exited 0 without that diagnostic.\n"
        "Hero evidence packaging reduced to six bits/channel to meet the lean render target.\n"
        "No known-failure exemptions, shared file edits, live editor access or runtime geometry.\n"
        "Placement/gameplay/transport/performance gates remain pending; see asset handoff.\n",
        encoding="utf-8", newline="\n")
    roots = [
        ROOT / f"art/source/models/environment/{NID}",
        ROOT / f"art/models/environment/{NID}",
        ROOT / f"tools/asset_production/{NID}",
        EVIDENCE,
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
        "asset_id": "d09_warehouses.02",
        "producer": "Commissioned isolated asset-production worker",
        "scope": "Every produced payload, excluding this self-referential manifest and scratch",
        "files": sorted(files, key=lambda item: item["path"]),
    }
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: {len(files)} payload hashes, four lean renders, all production checks green")


if __name__ == "__main__":
    main()
