"""Compact crate evidence and hash all final payloads, after the final import/check receipts."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_storage_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
DEPENDENCIES = [
    "tools/assets/blender/export_settings.json",
    "tools/asset_production/d09_storage_01/author.py",
    "tools/asset_production/d09_storage_03/validate.py",
    "tools/asset_production/d09_storage_03/check.gd",
]


def entry(path):
    """Describe one final payload without relying on earlier receipts or machine-local paths."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Check receipt consistency and produce a self-excluding manifest of the completed asset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compress-renders", action="store_true")
    args = parser.parse_args()
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720)
            if args.compress_renders:
                ImageOps.posterize(image.convert("RGB"), bits=6).save(
                    path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    if args.compress_renders:
        print(json.dumps(renders, indent=2))
        return

    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    glb = entry(ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb")
    assert glb["sha256"] == validation["glb_sha256"]
    assert glb["bytes"] == validation["glb_bytes"]
    handoff = (ROOT / f"docs/assets/production/{ASSET}.md").read_text(encoding="utf-8")
    assert validation["glb_sha256"] in handoff, "Refresh handoff from final export receipt"
    assert f"{int(validation['glb_bytes']):,} bytes" in handoff, "Stale handoff GLB size"
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["stable_roundtrips"] == 2
    assert validation["godot"]["fresh_process_roundtrip_byte_stable"]
    assert validation["godot"]["physics"]["authority_replay_equal"]
    validation["renders"] = renders
    validation["render_encoding"] = "Evidence only: RGB 6 significant bits/channel, PNG compression 9"
    validation["overhead_camera"] = {
        "renderer": "Isolated Blender Cycles CPU, 32 samples, AgX",
        "blender_position_m": [0, 0, 47], "rotation_radians": [0, 0, 0],
        "vertical_fov_degrees": 42, "north_up": True,
        "trio_center_blender_m": [-3, 0, 0], "pair_center_blender_m": [3, 0, 0],
        "scope": "Isolated asset arrangements only, not approved district placement",
    }
    validation["pending"] = [
        "Independent art/technical review",
        "World placement, actual engine-camera and actor/target occlusion checks",
        "Actual vehicle driving, network transport/admission/prediction and collision lifecycle",
        "LOD transitions, repeat-placement profiling, packaged-platform and Deck checks",
    ]
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    files = [ROOT / f"docs/assets/production/{ASSET}.md"]
    files.extend((ROOT / "scenes/prefabs/environment").glob(f"{ASSET}*.tscn*"))
    for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                      ROOT / f"art/models/environment/{ASSET}",
                      ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        files.extend(p for p in directory.rglob("*") if p.is_file()
                     and p.name != "manifest.json" and "__pycache__" not in p.parts)
    manifest = {
        "asset": "d09_storage.04", "producer": "commissioned implementation specialist",
        "hash_algorithm": "SHA-256", "self_excluded": True,
        "files": [entry(file) for file in sorted(set(files))],
        "read_only_reproduction_dependencies": [entry(ROOT / p) for p in DEPENDENCIES],
    }
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(manifest["files"]), "payload files")


if __name__ == "__main__":
    main()
