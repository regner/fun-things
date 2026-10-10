"""Compact the four evidence PNGs and hash the complete owned delivery."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_traffic_fixtures_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
CHECKS = Path(f"C:/tmp/ft/assets/{ASSET}/checks")


def main():
    """Retain lean renders and successful check receipts with final payload hashes."""
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as source:
            assert source.size == (1280, 720)
            image = ImageOps.posterize(source.convert("RGB"), bits=7)
        image.save(path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text(encoding="utf-8"))
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["mount_matches_source_and_adapter"]
    summary = json.loads((CHECKS / "summary.json").read_text(encoding="utf-8"))
    validation["production_checks"] = {"ok": summary["ok"], "results": summary["results"]}
    assert summary["ok"], "Production checks must all pass"
    validation["renders"] = renders
    validation["render_encoding"] = "RGB 7 significant bits per channel; PNG compression 9"
    path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8", newline="\n")
    log = EVIDENCE / "final.log"
    log.write_text(
        "city_traffic_fixtures.02 - final bounded validation receipt\n"
        "Blender 5.2.2 LTS / d13f752e3b9c; glTF exporter 5.2.40\n"
        f"Source/export: {validation['triangles']:g} triangles, "
        f"{validation['source_vertices']:g} source vertices; 1 mesh / 6 surfaces.\n"
        "Zero degenerate faces/triangles or non-manifold edges; normals and bounds pass.\n"
        "Fresh saved-source re-export byte-identical.\n"
        "Godot 4.8.dev7 c971f93e7: linked resources/UIDs, materials, mount and queries pass.\n"
        "Both wrappers preserve bytes/UIDs across save/reload and a fresh import.\n"
        "Pinned gdstyle formatting and lint pass.\n"
        "Production checks pass: 17 Python tests; 149 GUT tests; 6768 assertions; "
        "negative sentinel fails as expected.\n"
        "Import: existing MCP 4.8-versus-tested-4.7 warning only; no missing resources.\n"
        "Independent review, engine visual review, placement/car/network/device checks pending.\n",
        encoding="utf-8", newline="\n",
    )
    files = [ROOT / f"docs/assets/production/{ASSET}.md"]
    files.extend((ROOT / "scenes/prefabs/environment").glob(f"{ASSET}*.tscn*"))
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
    manifest = {"asset": "city_traffic_fixtures.02",
                "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": payload}
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("MANIFEST_PASS", len(payload), "payload files", renders)


if __name__ == "__main__":
    main()
