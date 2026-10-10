"""Compact four evidence PNGs and hash the complete owned delivery, excluding the manifest."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
CHECKS = Path(f"C:/tmp/ft/assets/{ASSET}/checks")


def main():
    """Record checks honestly, retain lean renders and produce reproducible payload hashes."""
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as source:
            assert source.size == (1280, 720)
            image = ImageOps.posterize(source.convert("RGB"), bits=7)
        image.save(path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["physics"]["authority_replay_equal"]
    summary = json.loads((CHECKS / "summary.json").read_text())
    validation["production_checks"] = {"ok": summary["ok"], "results": summary["results"]}
    assert summary["ok"], "Review canonical check failures before finalizing this delivery"
    validation["production_check_limitation"] = "None observed in this run; no failures suppressed."
    validation["visual_review"] = {
        "reviewer": "producer self-inspection; independent review pending",
        "views_inspected": ["hero", "side", "detail", "overhead_47m_42deg"],
        "observation": "Low pale separator, dark shoe and two restrained upper amber bands; "
                       "about 48 x 11 pixels in the calibrated overhead view.",
        "camera": {"height_m": 47, "vertical_fov_degrees": 42,
                   "projection": "perspective", "direction": "vertical-down, north-up"},
        "engine_camera_placement_and_target_occlusion": "not tested",
    }
    validation["renders"] = renders
    validation["render_encoding"] = "RGB 7 significant bits per channel; PNG compression 9"
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    files = [ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
    for folder in (ROOT / f"art/source/models/environment/{ASSET}",
                   ROOT / f"art/models/environment/{ASSET}",
                   ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        files.extend(p for p in folder.rglob("*") if p.is_file()
                     and p.name != "manifest.json" and "__pycache__" not in p.parts)
    payload = []
    for file in sorted(set(files)):
        raw = file.read_bytes()
        payload.append({"path": file.relative_to(ROOT).as_posix(), "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset": "city_barriers.03", "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": payload}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(payload), "payload files", renders)


if __name__ == "__main__":
    main()
