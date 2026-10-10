"""Finalize lean evidence and hash every delivered payload except the manifest itself."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_parking_furniture_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}")


def main():
    """Retain completed checks and compact lossless PNGs of seven-bit RGB render evidence."""
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as source:
            assert source.size == (1280, 720)
            image = ImageOps.posterize(source.convert("RGB"), bits=7)
        image.save(path, optimize=True, compress_level=9)
        renders.append({"file": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["physics"]["low_ray_blocked"]
    summary = json.loads((SCRATCH / "checks/summary.json").read_text())
    assert summary["ok"], "Do not publish a passing record for failed production checks"
    compilation = json.loads((SCRATCH / "checks/script-checks/compilation.json").read_text())
    own_script = f"tools/asset_production/{ASSET}/check.gd"
    assert any(row["script"] == own_script and row["ok"] for row in compilation)
    validation["production_checks"] = {
        "ok": summary["ok"], "results": summary["results"],
        "scripts_compiled": len(compilation), "owned_check_explicitly_compiled": True,
    }
    validation["renders"] = renders
    validation["render_encoding"] = "RGB, 7 significant bits per channel; PNG compression 9"
    validation["render_camera"] = {
        "projection": "perspective", "height_m": 47, "vertical_fov_degrees": 42,
        "orientation": "vertical down, Blender +Y at image top", "engine": "Blender Cycles CPU",
    }
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
    manifest = {
        "asset": "city_parking_furniture.01",
        "producer": "commissioned implementation specialist, lane/a-parking",
        "hash_algorithm": "SHA-256", "self_excluded": True, "files": payload,
    }
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(payload), "payload files", renders)


if __name__ == "__main__":
    main()
