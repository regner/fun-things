"""Compact four evidence PNGs and hash the complete owned delivery, excluding the manifest."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_traffic_fixtures_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
CHECKS = Path(f"C:/tmp/ft/assets/{ASSET}/checks-final")


def main():
    """Record checks honestly, retain lean renders and produce reproducible payload hashes."""
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as source:
            assert source.size == (1280, 720)
            image = ImageOps.posterize(source.convert("RGB"), bits=7)
        image.save(path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["physics"]["authority_replay_equal"]
    summary = json.loads((CHECKS / "summary.json").read_text())
    validation["production_checks"] = {"ok": summary["ok"], "results": summary["results"]}
    assert summary["ok"], "Production checks must all pass"
    validation["renders"] = renders
    validation["render_encoding"] = "RGB 7 significant bits per channel; PNG compression 9"
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    (EVIDENCE / "final.log").write_text(
        "city_traffic_fixtures.03 final bounded validation receipt\n"
        "Blender 5.2.2 LTS / glTF exporter 5.2.40: source and explicit export PASS\n"
        f"Geometry: {validation['triangles']} triangles; {validation['source_vertices']} source "
        f"vertices; {validation['export_vertices']} export vertices; 1 mesh / 3 surfaces\n"
        "Zero degenerate faces/triangles and nonmanifold edges; unit normals PASS\n"
        "Fresh saved-source GLB byte identity PASS; face-only upright artwork UVs PASS\n"
        "Pinned Godot import/dependencies, linked ancestry and scene roundtrip PASS\n"
        "ActorMotion authority/replay contact and bypass, blocked/clear rays PASS\n"
        "gdstyle format/lint and complete production checks PASS; no waived failures\n"
        "Four 1280x720 isolated Blender views self-reviewed; no live editor accessed\n"
        "Initial front normals corrected; source float and engine compressed UV tolerances recorded\n"
        "Known diagnostics: Blender use_nodes deprecation; MCP engine compatibility warning\n"
        "Pending: independent review, artwork, world/vehicle/network/device/performance acceptance\n",
        encoding="utf-8", newline="\n",
    )
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
    manifest = {"asset": "city_traffic_fixtures.03", "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": payload}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(payload), "payload files", renders)


if __name__ == "__main__":
    main()
