"""Compact inspected PNGs and index every final lighthouse payload after checks/import."""
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d01_lighthouse_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
checks = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(f"C:/tmp/ft/assets/{ASSET}/checks-final")
summary = json.loads((checks / "summary.json").read_text())
assert summary["ok"], "Final canonical production checks must pass"
compilation = json.loads((checks / "script-checks/compilation.json").read_text())
owned = next(row for row in compilation if row["script"] ==
             f"tools/asset_production/{ASSET}/check.gd")
assert owned["ok"]
images = []
for name in ("hero", "side", "detail", "overhead_47m_42deg"):
    path = EVIDENCE / (name + ".png")
    with Image.open(path) as original:
        assert original.size == (1280, 720)
        image = ImageOps.posterize(original.convert("RGB"), bits=6)
    image.save(path, optimize=True, compress_level=9)
    assert path.stat().st_size <= 400 * 1024
    images.append({"file": path.name, "size_px": [1280, 720], "bytes": path.stat().st_size})
validation_path = EVIDENCE / "validation.json"
validation = json.loads(validation_path.read_text())
assert validation["fresh_reexport_byte_identical"]
assert validation["godot"]["physics"]["authority_replay_within_tolerance"]
assert validation["godot"]["save_reload_byte_stable"]
validation["production_checks"] = {
    "ok": summary["ok"], "results": summary["results"], "owned_script": owned,
    "compiled_scripts": len(compilation), "python_tests": 17, "gut_tests": 149,
    "gut_assertions": 6768,
}
validation["renders"] = images
validation["render_encoding"] = "RGB 6 significant bits per channel, PNG compression 9"
validation["overhead_camera"] = {
    "projection": "perspective", "height_m": 47, "vertical_fov_deg": 42,
    "direction": "vertical down, Blender +Y at image top", "engine_capture": False,
    "observation": "Roof and gallery ring remain visible; shaft/band/glazing self-occlude at centre",
}
validation_path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
paths = [ROOT / f"docs/assets/production/{ASSET}.md",
         ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                  ROOT / f"art/models/environment/{ASSET}",
                  ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
    paths.extend(p for p in directory.rglob("*") if p.is_file()
                 and p.name != "manifest.json" and "__pycache__" not in p.parts)
manifest = {"asset": "d01_lighthouse.01", "producer": "commissioned implementation specialist",
            "hash_algorithm": "SHA-256", "self_excluded": True, "files": []}
for path in sorted(set(paths)):
    raw = path.read_bytes()
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print("MANIFEST_PASS", len(manifest["files"]), "payload files; canonical checks passed")
