"""Retain lean check evidence and a hash manifest after source/export and engine validation."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_trolley_shelter_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def main():
    """Compact only review images, attach completed suite results, then hash final payloads."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checks", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads((args.checks / "summary.json").read_text(encoding="utf-8"))
    assert summary["ok"], "Production checks must pass before recording the receipt"
    validation_path = EVIDENCE / "validation.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    validation["production_checks"] = summary["results"]
    validation["evidence_renders"] = {}
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            # Drop only two noise-heavy low bits per channel, not rare accent colours.
            # This is idempotent and applies only to evidence, never runtime assets.
            compact = image.convert("RGB").point(lambda value: (value >> 2) << 2)
            compact.save(path, optimize=True, compress_level=9)
            assert image.size == (1280, 720)
        validation["evidence_renders"][name] = {
            "size_px": [1280, 720], "bytes": path.stat().st_size,
            "source": "isolated Blender Cycles render, 6-bit/channel precision review-only PNG",
        }
    validation_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8", newline="\n")
    paths = [ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
    for directory in [f"art/source/models/environment/{ASSET}",
                      f"art/models/environment/{ASSET}",
                      f"tools/asset_production/{ASSET}",
                      f"docs/assets/production/{ASSET}-evidence"]:
        paths.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    manifest = {
        "asset": "d07_trolley_shelter.01",
        "producer": "commissioned implementation specialist",
        "scope": "All delivered files except this self-referential manifest; no external inputs",
        "files": [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                  for path in sorted(set(paths)) if path.name != "manifest.json"],
    }
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Recorded {len(manifest['files'])} payload hashes")


if __name__ == "__main__":
    main()
