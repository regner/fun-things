"""Compact evidence PNGs and hash the complete roof-access delivery after final engine import."""
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_roof_details_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}")
checks = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRATCH / "checks-utf8"
summary = json.loads((checks / "summary.json").read_text())
assert summary["ok"], "Production checks did not pass"
images = []
for name in ("hero", "side", "detail", "overhead_47m_42deg"):
    path = EVIDENCE / (name + ".png")
    image = Image.open(path)
    assert image.size == (1280, 720)
    # Compact evidence-only encoding; no runtime texture or asset shading is changed.
    image = ImageOps.posterize(image.convert("RGB"), bits=6)
    image.save(path, optimize=True, compress_level=9)
    assert path.stat().st_size <= 420 * 1024
    images.append({"file": path.name, "size_px": [1280, 720], "bytes": path.stat().st_size})

receipts = []
for filename in ("check.log", "check-second-process.log"):
    lines = (SCRATCH / filename).read_text().splitlines()
    assert not any("ERROR:" in line or "WARNING:" in line for line in lines)
    matches = [line.split("_CHECK_PASS ", 1)[1] for line in lines if "_CHECK_PASS " in line]
    assert len(matches) == 1
    receipts.append(json.loads(matches[0]))
assert receipts[0] == receipts[1], "Separate-process physics receipts differ"
validation_path = EVIDENCE / "validation.json"
validation = json.loads(validation_path.read_text())
assert validation["fresh_reexport_byte_identical"]
assert validation["godot"]["physics"]["authority_replay_equal"]
assert validation["godot"]["save_reload_byte_stable"]
assert validation["overhead_camera"]["reference_modified"] is False
validation["godot"]["separate_process_results_equal"] = True
validation["godot"]["standalone_process_count"] = 2
validation["production_checks"] = summary["results"]
validation["renders"] = images
validation["render_encoding"] = "RGB 6 significant bits per channel, PNG compression 9"
validation["diagnostics"] = {
    "blender": "Material/World.use_nodes deprecation notices; successful source/export/render exits",
    "version_probe": "Blender --version emitted one 0.000023 MB unfreed allocation",
    "headless_import": "Passed; existing MCP plugin warning about Godot 4.8",
    "headless_editor_normalization": "Save/reload assertions passed; editor/plugin shutdown RID/ObjectDB leaks",
    "standalone_asset_checks": "Two processes passed without error/warning diagnostics",
    "first_production_attempt": "Windows cp1252 subprocess decoding failed before engine verification",
    "evidence_size_gate": "Initial 7-bit hero exceeded the 420 KiB cap; final 6-bit PNGs pass",
    "canonical_production_checks": "Passed after PYTHONUTF8=1 and explicit mise-resolved executables; no exemptions",
}
validation_path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
paths = [ROOT / f"docs/assets/production/{ASSET}.md",
         ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                  ROOT / f"art/models/environment/{ASSET}",
                  ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
    paths.extend(p for p in directory.rglob("*") if p.is_file()
                 and p.name != "manifest.json" and "__pycache__" not in p.parts)
manifest = {"asset": "city_roof_details.03", "producer": "commissioned implementation specialist",
            "hash_algorithm": "SHA-256", "self_excluded": True, "files": []}
for path in sorted(set(paths)):
    raw = path.read_bytes()
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print("MANIFEST_PASS", len(manifest["files"]), "payload files")
