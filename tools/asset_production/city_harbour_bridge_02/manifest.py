"""Compact review PNGs and hash the complete owned delivery; manifest excludes itself."""
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_harbour_bridge_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
checks = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(f"C:/tmp/ft/assets/{ASSET}/checks")
summary = json.loads((checks / "summary.json").read_text())
assert summary["ok"], "Production checks did not pass"
images = []
for name in ("hero", "side", "detail", "overhead_47m_42deg"):
    path = EVIDENCE / (name + ".png")
    image = Image.open(path)
    assert image.size == (1280, 720)
    # One low bit per channel is removed to trim denoised background entropy,
    # without the visible shadow banding of a global 256-color palette.
    image = ImageOps.posterize(image.convert("RGB"), bits=7)
    image.save(path, optimize=True, compress_level=9)
    images.append({"file": path.name, "size_px": [1280, 720], "bytes": path.stat().st_size})
validation_path = EVIDENCE / "validation.json"
validation = json.loads(validation_path.read_text())
assert validation["godot"]["physics"]["authority_replay_equal"]
assert validation["godot"]["save_reload_byte_stable"]
validation["production_checks"] = summary["results"]
validation["renders"] = images
validation["render_encoding"] = "RGB 7 significant bits per channel, PNG compression 9"
validation_path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
paths = [ROOT / f"docs/assets/production/{ASSET}.md",
         ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                  ROOT / f"art/models/environment/{ASSET}",
                  ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
    paths.extend(p for p in directory.rglob("*") if p.is_file()
                 and p.name != "manifest.json" and "__pycache__" not in p.parts)
manifest = {"asset": "city_harbour_bridge.02", "producer": "commissioned implementation specialist",
            "hash_algorithm": "SHA-256", "self_excluded": True, "files": []}
for path in sorted(set(paths)):
    raw = path.read_bytes()
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print("MANIFEST_PASS", len(manifest["files"]), "payload files")
