"""Compact the four evidence images and hash every delivered chimney payload except this manifest."""
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_roof_details_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}")
checks = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRATCH / "checks-final"
summary = json.loads((checks / "summary.json").read_text())
assert summary["ok"], "Canonical checks failed"
images = []
for name in ("hero", "side", "detail", "overhead_47m_42deg"):
    path = EVIDENCE / (name + ".png")
    image = Image.open(path)
    assert image.size == (1280, 720)
    # Evidence-only encoding; runtime materials and geometry remain untouched.
    image = ImageOps.posterize(image.convert("RGB"), bits=6)
    image.save(path, optimize=True, compress_level=9)
    assert path.stat().st_size < 400 * 1024
    images.append({"file": path.name, "resolution_px": [1280, 720], "bytes": path.stat().st_size})

lines = (SCRATCH / "check.log").read_text().splitlines()
assert not any("ERROR:" in line or "WARNING:" in line for line in lines)
assert sum("CITY_ROOF_DETAILS_04_CHECK_PASS" in line for line in lines) == 1
validation_path = EVIDENCE / "validation.json"
validation = json.loads(validation_path.read_text())
assert validation["fresh_reexport_byte_identical"]
assert validation["godot"]["save_reload_byte_stable"]
assert validation["godot"]["static_body_count"] == 0
validation["production_checks"] = summary["results"]
validation["renders"] = images
validation["render_encoding"] = "RGB six significant bits per channel; PNG compression 9"
validation["diagnostics"] = {
    "blender": "Material/World.use_nodes deprecation notices; all final jobs exit 0",
    "version_probe": "One 0.000023 MB unfreed allocation from Blender --version",
    "initial_source_check": "Apron bevel exceeded 1 mm dimension tolerance; reduced to 2 mm and revalidated",
    "visual_iteration": "Widened hero framing; replaced protruding square flue floor with contained round floor",
    "headless_import": "Pass; existing MCP plugin compatibility warning for Godot 4.8",
    "headless_editor_normalization": "Assertions pass; renderer/text RID and ObjectDB shutdown leaks",
    "standalone_asset_check": "Pass with no error/warning diagnostics",
    "initial_canonical_checks": "Owned 101-character line rejected; shortened literal precision and reran",
    "final_canonical_checks": "All pass without exemptions, including intentional failing-test detection",
}
validation_path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
paths = [ROOT / f"docs/assets/production/{ASSET}.md"]
paths.extend((ROOT / "scenes/prefabs/environment").glob(ASSET + "*.tscn*"))
for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                  ROOT / f"art/models/environment/{ASSET}",
                  ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
    paths.extend(p for p in directory.rglob("*") if p.is_file()
                 and p.name != "manifest.json" and "__pycache__" not in p.parts)
manifest = {"asset": "city_roof_details.04", "producer": "commissioned implementation specialist",
            "hash_algorithm": "SHA-256", "self_excluded": True, "files": []}
for path in sorted(set(paths)):
    raw = path.read_bytes()
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print("MANIFEST_PASS", len(manifest["files"]), "payload files")
