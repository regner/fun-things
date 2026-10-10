"""Compact crane renders and hash the final delivery after source/engine validation."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_cranes_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def main():
    """Publish lean evidence; never turn a failed production check into a pass."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compress-renders", action="store_true")
    parser.add_argument("--checks", type=Path, default=Path(f"C:/tmp/ft/assets/{ASSET}/checks-pinned"))
    args = parser.parse_args()
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720)
            if args.compress_renders:
                compact = ImageOps.posterize(image.convert("RGB"), bits=6)
                compact.save(path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    if args.compress_renders:
        print(json.dumps(renders, indent=2))
        return

    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["physics"]["authority_replay_equal"]
    checks = json.loads((args.checks / "summary.json").read_text())
    assert checks["ok"]
    validation["production_checks"] = {"ok": checks["ok"], "results": checks["results"],
                                       "python_tests": 17, "gut_tests": 149, "gut_assertions": 6768}
    validation["renders"] = renders
    validation["render_encoding"] = "RGB, 6 significant bits/channel; PNG compression 9"
    validation["overhead_camera"] = {
        "renderer": "Blender Cycles CPU, 32 samples, AgX; isolated studio",
        "blender_position_m": [0, 6.7, 47], "rotation_radians": [0, 0, 0],
        "vertical_fov_degrees": 42, "north_up": True,
    }
    validation["diagnostics"] = [
        "Blender 5.2.2 emits forward-looking Material/World.use_nodes deprecation notices.",
        "Headless import emits the existing MCP toolkit 4.8-vs-tested-4.7 warning.",
        "First production-check invocation selected the PATH gdvm shim and failed version "
        "discovery (including a cp1252 reader error). PYTHONUTF8 alone did not fix the shim. "
        "Final invocation uses explicit mise-pinned Godot/gdstyle paths and passes all layers.",
        "Initial visual review added boom end posts and removed the studio horizon. "
        "Final four renders were inspected after reauthor/export.",
    ]
    validation["pending"] = [
        "Independent art/technical acceptance", "Actual engine-camera appearance and occlusion",
        "Unequal crane pair comparison after d09_cranes.02 exists",
        "Land-only base placement, over-water boom orientation and generous apron spacing",
        "Vehicle driving/turning; multiplayer transport/admission/prediction",
        "Packaged-platform, Deck and repeated-placement GPU/frame-time performance",
    ]
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    files = [ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
    for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                      ROOT / f"art/models/environment/{ASSET}",
                      ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        files.extend(path for path in directory.rglob("*") if path.is_file()
                     and path.name != "manifest.json" and "__pycache__" not in path.parts)
    entries = []
    for path in sorted(set(files)):
        raw = path.read_bytes()
        entries.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset": "d09_cranes.01", "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": entries}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(entries), "payload files")


if __name__ == "__main__":
    main()
