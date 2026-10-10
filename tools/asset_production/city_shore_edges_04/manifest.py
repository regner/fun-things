"""Compact the four inspected renders and index every owned production payload."""
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_shore_edges_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
checks = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(f"C:/tmp/ft/assets/{ASSET}/checks")
summary = json.loads((checks / "summary.json").read_text())
compilation = json.loads((checks / "script-checks/compilation.json").read_text())
owned = next(row for row in compilation if row["script"] ==
             f"tools/asset_production/{ASSET}/check.gd")
followup_path = checks.parent / "compilation-followup.json"
followup = json.loads(followup_path.read_text()) if followup_path.exists() else []
for row in followup:
    assert row["sha256"] == hashlib.sha256((ROOT / row["script"]).read_bytes()).hexdigest()
assert all(any(f["script"] == row["script"] and f["ok"] for f in followup)
           for row in compilation if not row["ok"]), "Unresolved compilation failure"
owned_followup = next((row for row in followup if row["script"] == owned["script"]), {})
assert owned["ok"] or owned_followup.get("ok"), "Owned script must compile explicitly"
images = []
for name in ("hero", "side", "detail", "overhead_47m_42deg"):
    path = EVIDENCE / (name + ".png")
    image = Image.open(path)
    assert image.size == (1280, 720)
    # Studio output dither is disabled in Blender; preserve every rendered RGB value.
    image = image.convert("RGB")
    image.save(path, optimize=True, compress_level=9)
    assert path.stat().st_size <= 400 * 1024
    images.append({"file": path.name, "size_px": [1280, 720], "bytes": path.stat().st_size})
validation_path = EVIDENCE / "validation.json"
validation = json.loads(validation_path.read_text())
assert all(v["fresh_reexport_byte_identical"] for v in validation["variants"].values())
assert validation["godot"]["physics"]["authority_replay_within_tolerance"]
assert validation["godot"]["save_reload_byte_stable"]
validation["production_checks"] = {
    "ok": summary["ok"], "results": summary["results"], "owned_script": owned,
    "compilation_failures": [row for row in compilation if not row["ok"]],
    "individual_compilation_followup": followup,
    "note": "Canonical result preserved; per-script 180s follow-ups are separate evidence",
}
validation["renders"] = images
validation["render_encoding"] = "RGB 8 bits per channel, PNG compression 9; Blender output dither disabled"
validation["overhead_camera"] = {
    "projection": "perspective", "height_m": 47, "vertical_fov_deg": 42,
    "direction": "vertical down, Blender +Y at image top", "engine_capture": False,
}
validation_path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
paths = [ROOT / f"docs/assets/production/{ASSET}.md"]
paths.extend((ROOT / "scenes/prefabs/environment").glob(ASSET + "_*.tscn"))
for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                  ROOT / f"art/models/environment/{ASSET}",
                  ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
    paths.extend(p for p in directory.rglob("*") if p.is_file()
                 and p.name != "manifest.json" and "__pycache__" not in p.parts)
manifest = {"asset": "city_shore_edges.04", "producer": "commissioned implementation specialist",
            "hash_algorithm": "SHA-256", "self_excluded": True, "files": []}
for path in sorted(set(paths)):
    raw = path.read_bytes()
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print("MANIFEST_PASS", len(manifest["files"]), "payload files; canonical checks:", summary["ok"])
