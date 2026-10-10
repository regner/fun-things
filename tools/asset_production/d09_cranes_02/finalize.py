"""Compact crane renders and hash the final delivery after source/engine validation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_cranes_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def main():
    """Publish lean evidence; never turn a failed production check into a pass."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compress-renders", action="store_true")
    parser.add_argument("--checks", type=Path, default=Path(f"C:/tmp/ft/assets/{ASSET}/checks"))
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
    gut = ET.parse(args.checks / "gut-results.xml").getroot()
    python_log = (args.checks / "python-tests.log").read_text()
    python_count = int(re.search(r"Ran (\d+) tests", python_log).group(1))
    validation["production_checks"] = {
        "ok": checks["ok"], "results": checks["results"], "python_tests": python_count,
        "gut_tests": int(gut.attrib["tests"]),
        "gut_assertions": sum(int(case.attrib["assertions"]) for case in gut.iter("testcase")),
    }
    validation["renders"] = renders
    validation["render_encoding"] = "RGB, 6 significant bits/channel; PNG compression 9"
    validation["overhead_camera"] = {
        "renderer": "Blender Cycles CPU, 32 samples, AgX; isolated studio",
        "blender_position_m": [0, 6.7, 47], "rotation_radians": [0, 0, 0],
        "vertical_fov_degrees": 42, "north_up": True,
        "pair_comparison": {
            "larger_blender_translation_m": [-12, 0, 0],
            "smaller_blender_translation_m": [12, 0, 0],
            "rotation_radians_both": [0, 0, 0], "scale_both": [1, 1, 1],
            "base_centres_separation_m": 24, "clear_ground_apron_between_plinths_m": 19,
            "status": "Isolated illustrative pair; not measured district placement acceptance",
        },
    }
    validation["diagnostics"] = [
        "Blender 5.2.2 emits forward-looking Material/World.use_nodes deprecation notices.",
        "Headless import emits the existing MCP toolkit 4.8-vs-tested-4.7 warning.",
        "Production checks use explicit mise-pinned Godot/gdstyle paths and UTF-8, following "
        "the larger sibling's recorded Windows shim workaround; all layers pass.",
        "The four final renders were visually inspected. Overhead was changed from the "
        "single crane to an equal-camera pair comparison using the unchanged larger source.",
    ]
    validation["pending"] = [
        "Independent art/technical acceptance", "Actual engine-camera appearance and occlusion",
        "Whole-city pair readability and actor-centred boom occlusion",
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
    dependencies = []
    for relative in (
        "tools/asset_production/d09_cranes_01/author.py",
        "art/source/models/environment/d09_cranes_01/d09_cranes_01.blend",
        "tools/assets/blender/export_settings.json",
    ):
        dependencies.append({"path": relative,
                             "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()})
    manifest = {"asset": "d09_cranes.02", "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": entries,
                "read_only_reproduction_dependencies": dependencies}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(entries), "payload files")


if __name__ == "__main__":
    main()
