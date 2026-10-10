"""Compact review images and hash every owned delivery payload, excluding the manifest itself."""
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
checks = Path(sys.argv[1])
summary = json.loads((checks / "summary.json").read_text())
assert summary["results"]["owned_scripts"]["ok"], "Owned scripts must pass"
# A manifest establishes integrity, not acceptance of unrelated test failures.
images = []
for name in ("hero", "side", "detail", "overhead_47m_42deg"):
    path = EVIDENCE / (name + ".png")
    image = Image.open(path)
    expected_size = {"hero": (1152, 648), "detail": (1024, 576)}.get(name, (1280, 720))
    assert image.size == expected_size
    # Match the straight member's lean evidence encoding; runtime assets are untouched.
    image = ImageOps.posterize(image.convert("RGB"), bits=7)
    image.save(path, optimize=True, compress_level=9)
    images.append({"file": path.name, "size_px": list(image.size), "bytes": path.stat().st_size})
validation_path = EVIDENCE / "validation.json"
validation = json.loads(validation_path.read_text())
assert validation["godot"]["physics"]["authority_replay_equal"]
assert validation["godot"]["save_reload_byte_stable"]
validation["production_checks"] = summary["results"]
validation["production_checks_overall_passed"] = summary["ok"]
validation["renders"] = images
validation["render_encoding"] = "RGB 7 significant bits per channel, PNG compression 9"
validation_path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
paths = [ROOT / f"docs/assets/production/{ASSET}.md"]
paths.extend((ROOT / "scenes/prefabs/environment").glob(ASSET + "*.tscn"))
for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                  ROOT / f"art/models/environment/{ASSET}",
                  ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
    paths.extend(p for p in directory.rglob("*") if p.is_file()
                 and p.name != "manifest.json" and "__pycache__" not in p.parts)
manifest = {"asset": "city_boardwalk.02", "producer": "commissioned implementation specialist",
            "hash_algorithm": "SHA-256", "self_excluded": True, "files": []}
for path in sorted(set(paths)):
    raw = path.read_bytes()
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print("MANIFEST_PASS", len(manifest["files"]), "payload files")
for image in images:
    print(image)
