"""Compress only review PNGs and fingerprint the complete final producer set."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "vehicle_wrecks_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def fingerprint(path):
    """Return an exact payload identity without including the self-referential manifest."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Require matching validation receipts and emit a manifest after all other writes."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    assert report["fresh_reexport_byte_identical"] and report["engine"]["status"] == "PASS"
    for key in ("source", "export", "live_source", "live_export"):
        actual = fingerprint(ROOT / report[key]["path"])
        assert actual == report[key], (key, actual, report[key])
    prefab = ROOT / f"scenes/prefabs/city_cars/{ASSET}.tscn"
    assert fingerprint(prefab)["sha256"] == report["engine"]["prefab_sha256"]
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / (name + ".png")
        with Image.open(path) as source:
            assert source.size == (1280, 720)
            image = ImageOps.posterize(source.convert("RGB"), bits=6)
        image.save(path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
        assert path.stat().st_size < 410000, (path, path.stat().st_size)
    report["renders"] = renders
    report["render_notes"] = "Isolated Cycles CPU, 32 samples, AgX; review PNGs RGB6/deflate9 only"
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    roots = [ROOT / f"art/source/models/vehicles/{ASSET}", ROOT / f"art/models/vehicles/{ASSET}",
             ROOT / f"tools/asset_production/{ASSET}", EVIDENCE]
    files = [p for directory in roots for p in directory.rglob("*")
             if p.is_file() and p.name != "manifest.json" and "__pycache__" not in p.parts]
    files += [prefab, ROOT / f"docs/assets/production/{ASSET}.md"]
    manifest = {"asset": "vehicle_wrecks.01", "producer": "commissioned implementation specialist",
                "scope": "Owned source/export/prefab/tools/handoff/evidence; manifest excludes itself",
                "files": [fingerprint(p) for p in sorted(files)]}
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("MANIFEST", len(files), "payloads; all source/export/prefab receipt hashes agree")
    for render in renders:
        print("RENDER", render)


if __name__ == "__main__":
    main()
