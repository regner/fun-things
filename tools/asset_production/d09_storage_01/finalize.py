"""Compact isolated renders and hash the final container delivery, after all checks."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_storage_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def main():
    """Retain lean reproducibility evidence without manufacturing test outcomes."""
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
    glb = ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb"
    assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation["glb_sha256"]
    assert glb.stat().st_size == validation["glb_bytes"]
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["stable_roundtrips"] == 2
    assert validation["godot"]["physics"]["authority_replay_equal"]
    validation["renders"] = renders
    validation["render_encoding"] = "Evidence only: RGB 6 significant bits/channel, PNG compression 9"
    validation["overhead_camera"] = {
        "renderer": "Isolated Blender Cycles CPU, 32 samples, AgX",
        "blender_position_m": [0, 0, 47], "rotation_radians": [0, 0, 0],
        "vertical_fov_degrees": 42, "north_up": True,
        "scope": "Isolated asset appearance, not engine/district-camera acceptance",
    }
    validation["pending"] = [
        "Independent art/technical review",
        "World placement, apron clearances and camera occlusion in context",
        "Actual vehicle driving and multiplayer transport/admission/prediction",
        "Engine-camera, LOD transition, packaged-platform and Deck performance checks",
    ]
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    files = [ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
    for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                      ROOT / f"art/models/environment/{ASSET}",
                      ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        files.extend(p for p in directory.rglob("*") if p.is_file()
                     and p.name != "manifest.json" and "__pycache__" not in p.parts)
    entries = []
    for file in sorted(set(files)):
        raw = file.read_bytes()
        entries.append({"path": file.relative_to(ROOT).as_posix(), "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
    settings = "tools/assets/blender/export_settings.json"
    manifest = {
        "asset": "d09_storage.01", "producer": "commissioned implementation specialist",
        "hash_algorithm": "SHA-256", "self_excluded": True, "files": entries,
        "read_only_reproduction_dependencies": [{"path": settings,
            "sha256": hashlib.sha256((ROOT / settings).read_bytes()).hexdigest()}],
    }
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(entries), "payload files")


if __name__ == "__main__":
    main()
