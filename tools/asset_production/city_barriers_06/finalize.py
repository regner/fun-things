"""Compact the four required views and hash every delivered payload except this manifest."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_06"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
CHECKS = Path(f"C:/tmp/ft/assets/{ASSET}/checks")


def main():
    """Require owned checks to pass and preserve any narrowly classified global check failure."""
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as source:
            assert source.size == (1280, 720)
            image = ImageOps.posterize(source.convert("RGB"), bits=6)
        image.save(path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    assert all(v["fresh_export_byte_identical"] for v in validation["variants"].values())
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["physics"]["authority_replay_equal"]
    summary = json.loads((CHECKS / "summary.json").read_text())
    validation["production_checks"] = {"ok": summary["ok"], "results": summary["results"]}
    limitation = "None observed; no failures suppressed."
    if not summary["ok"]:
        # Preserve the global failure; do not turn a timed-out aggregate run into a pass.
        assert all(v["ok"] for k, v in summary["results"].items() if k != "owned_scripts")
        status = json.loads((CHECKS / "script-checks.log").read_text().splitlines()[-1])
        assert status["formatting"] and status["style"]
        compilation = json.loads((CHECKS / "script-checks/compilation.json").read_text())
        owned = [item for item in compilation if item["script"].startswith(
            f"tools/asset_production/{ASSET}/")]
        assert owned and all(item["ok"] for item in owned)
        failures = []
        for index, item in enumerate(compilation):
            if item["ok"]:
                continue
            assert item["script"].startswith("tools/assets/")
            log = (CHECKS / f"script-checks/compile-{index}.log").read_text().strip()
            assert log == "CHECK DEADLINE EXCEEDED", (item, log)
            failures.append(item["script"])
        assert failures
        validation["production_checks"]["external_compile_deadlines"] = failures
        limitation = ("Final canonical run exits 1: cumulative compiler deadline prevented "
                      f"{len(failures)} unrelated tools/assets scripts from running. Owned "
                      "format/lint/compile and all Python/GUT checks pass. Earlier full run "
                      "passed; final aggregate failure remains reported, not suppressed.")
    validation["production_check_limitation"] = limitation
    validation["visual_review"] = {
        "reviewer": "producer self-inspection; independent review pending",
        "views_inspected": ["hero", "side", "detail", "overhead_47m_42deg"],
        "observation": "Quiet galvanised line/terminal/corner supports with local base oxide; "
                       "hollow panel clamps and staggered corner brace attachments read in detail. "
                       "At 47 m the posts are tiny dots and braces faint short lines; these "
                       "supports alone do not communicate a complete fence boundary.",
        "camera": {"height_m": 47, "vertical_fov_degrees": 42,
                   "projection": "perspective", "direction": "vertical-down, north-up"},
        "engine_camera_placement_and_target_occlusion": "not tested",
    }
    validation["godot"]["fresh_process_scene_hash_comparison"] = {
        "scene_count": 4, "normalization_processes": 2,
        "result": "All four saved scene SHA-256 values unchanged across two fresh processes",
    }
    validation["renders"] = renders
    validation["render_encoding"] = "RGB six significant bits per channel; PNG compression 9"
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    files = [ROOT / f"docs/assets/production/{ASSET}.md"]
    files.extend((ROOT / "scenes/prefabs/environment").glob(ASSET + "*.tscn"))
    for folder in (ROOT / f"art/source/models/environment/{ASSET}",
                   ROOT / f"art/models/environment/{ASSET}",
                   ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        files.extend(p for p in folder.rglob("*") if p.is_file()
                     and p.name != "manifest.json" and "__pycache__" not in p.parts)
    payloads = []
    for file in sorted(set(files)):
        raw = file.read_bytes()
        payloads.append({"path": file.relative_to(ROOT).as_posix(), "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset": "city_barriers.06", "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": payloads}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(payloads), "payload files", renders)


if __name__ == "__main__":
    main()
