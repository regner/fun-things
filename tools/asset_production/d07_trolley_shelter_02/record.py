"""Compact review-only PNGs, retain suite receipts and hash the final trolley payloads."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_trolley_shelter_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def main():
    """Record completed checks; exclude caches and this self-referential manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checks", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads((args.checks / "summary.json").read_text(encoding="utf-8"))
    assert summary["ok"], "Production checks must pass"
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text(encoding="utf-8"))
    assert validation["source_export_status"] == "passed" and validation["godot"]
    validation["production_checks"] = summary["results"]
    validation["evidence_renders"] = {}
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        image_path = EVIDENCE / f"{name}.png"
        with Image.open(image_path) as image:
            assert image.size == (1280, 720)
            # Match the sibling's idempotent 6-bit/channel evidence compaction.
            image.convert("RGB").point(lambda value: (value >> 2) << 2).save(
                image_path, optimize=True, compress_level=9)
        validation["evidence_renders"][name] = {
            "size_px": [1280, 720], "bytes": image_path.stat().st_size,
            "source": "isolated Blender Cycles; 6-bit/channel review PNG, no runtime textures",
        }
    path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8", newline="\n")
    paths = [ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
    for directory in (f"art/source/models/environment/{ASSET}",
                      f"art/models/environment/{ASSET}",
                      f"tools/asset_production/{ASSET}",
                      f"docs/assets/production/{ASSET}-evidence"):
        paths.extend(p for p in (ROOT / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts and p.name != "manifest.json")
    manifest = {
        "asset": "d07_trolley_shelter.02",
        "producer": "commissioned implementation specialist",
        "scope": "Every delivered payload except this self-referential manifest",
        "reused_tool_dependencies": [
            "tools/assets/blender/export_settings.json",
            "tools/asset_production/d07_trolley_shelter_01/author.py",
            "tools/asset_production/d07_trolley_shelter_01/validate.py",
        ],
        "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(paths))],
    }
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Recorded {len(manifest['files'])} final payload hashes")


if __name__ == "__main__":
    main()
