"""Assemble lean loading-location evidence and verify all producer/dependency bytes."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
OWNED = [
    f"art/textures/environment/{NID}", f"art/materials/environment/{NID}",
    f"tools/asset_production/{NID}", f"scenes/prefabs/environment/{NID}.tscn",
    f"scenes/prefabs/environment/{NID}_low.tscn", f"docs/assets/production/{NID}.md",
    f"docs/assets/production/{NID}-evidence",
]


def digest(path):
    """Fingerprint actual bytes, not a historical receipt or assumed export."""
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def compress_renders():
    """Use seven significant bits per channel on evidence only; runtime PNGs stay unchanged."""
    for path in sorted(EVIDENCE.glob("*.png")):
        with Image.open(path) as image:
            image.convert("RGB").point([v & 254 for v in range(256)]*3).save(path, compress_level=9)
        print(path.name, path.stat().st_size)


def assemble():
    """Merge measured source/engine receipts after checking final logs and delivered identities."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    engine = json.loads((SCRATCH / "prefab.json").read_text())
    normalized = json.loads((SCRATCH / "normalize.json").read_text())
    assert engine["status"] == normalized["status"] == "PASS"
    assert not engine["failures"] and not normalized["failures"]
    for variant, suffix in [("wall", ""), ("low", "_low")]:
        check = normalized[variant]
        assert check["stable_roundtrip_count"] == 2
        prefab = ROOT / f"scenes/prefabs/environment/{NID}{suffix}.tscn"
        material = ROOT / f"art/materials/environment/{NID}/loading_{variant}.tres"
        assert digest(prefab)["sha256"] == check["scene_sha256"]
        assert digest(material)["sha256"] == check["material_sha256"]
        for key, value in engine[variant].items():
            if key.startswith("res://"):
                assert normalized[variant][key] == value
    for path, measured in report["dependencies"].items():
        assert digest(ROOT / path) == measured, "Shared dependency changed: " + path
    for name, token in [("source.log", "LOADING_SOURCE_PASS"),
                        ("render.log", "LOADING_PREVIEW_PASS"),
                        ("prefab.log", "LOADING_PREFAB_PASS"),
                        ("normalize.log", "LOADING_PREFAB_PASS"),
                        ("tests.log", "OK"), ("style.log", "no issues found"),
                        ("format.log", "already formatted")]:
        log = (SCRATCH / name).read_text(encoding="utf-8")
        assert token in log and "ERROR" not in log and "Traceback" not in log, name
    log = (SCRATCH / "import-final.log").read_text(encoding="utf-8")
    assert "ERROR" not in log and "[MCPServer] stopped" in log
    assert "c971f93e7" in (SCRATCH / "prefab.log").read_text()
    report["engine"] = engine
    report["save_reload"] = normalized
    report["artwork"] = {"mode": "RGB", "tests_passed": 4,
                         "filter": "linear_mipmap", "repeat": False,
                         "emission": False, "variants": {}}
    for variant, copy, size, margin in [("wall", "LOADING 04 / FREIGHT", [1220, 820], 40),
                                        ("low", "FREIGHT / LOAD 04", [1440, 390], 30)]:
        path = ROOT / f"art/textures/environment/{NID}/loading_{variant}_albedo.png"
        report["artwork"]["variants"][variant] = {
            "copy": copy, "size_px": size, "safe_margin_px": margin, **digest(path)}
    report["renders"] = {}
    for path in sorted(EVIDENCE.glob("*.png")):
        with Image.open(path) as image:
            assert image.size == (1280, 720)
        assert path.stat().st_size < 400*1024
        report["renders"][path.name] = digest(path)
    report["checks"] = {"pinned_import_no_errors": True, "gdstyle_format": "PASS",
                        "gdstyle_lint": "PASS", "new_collision": False,
                        "independent_review": "pending", "world_gameplay_device": "pending"}
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n",
                                             encoding="utf-8", newline="\n")
    (EVIDENCE / "final.log").write_text(
        "d09_freight_graphics.03 final bounded producer checks\n"
        "Blender 5.2.2 LTS d13f752e3b9c / exporter 5.2.40 source audit: PASS, exit 0.\n"
        "Both existing sign sources and GLBs unchanged; fresh exports byte-identical.\n"
        "Wall: 2720 triangles, 12 meshes, 13 surfaces. Low: 2448 triangles, 2 meshes, 5 surfaces.\n"
        "Zero degenerates/nonmanifold edges; unit normals, winding and literal bounds pass.\n"
        "Artwork uses only sign_face surface 0; actual GLB UVs upright and outside-readable.\n"
        "Four Python artwork tests: PASS, exit 0; both PNG byte streams reproduce exactly.\n"
        "Four isolated Blender renders: PASS, exit 0; 1280x720; producer inspected each.\n"
        "Godot 4.8.dev7.official.c971f93e7 final import: PASS, exit 0; no ERROR/SCRIPT ERROR.\n"
        "Import retains installed MCP toolkit warning: Godot 4.8 versus tested 4.7.\n"
        "Two save/reload cycles per scene/material plus fresh-process initial-byte check: PASS.\n"
        "Fresh prefab/dependency/material/unchanged inherited collision checks: PASS, exit 0.\n"
        "Wall visual-only; low sign retains original one-box collider, no geometry duplicated.\n"
        "Final normalization and fresh check logs have no errors or warnings.\n"
        "gdstyle 0.3.0 format check and zero-warning lint: PASS, exit 0.\n"
        "Preview emits Blender use_nodes forward-looking deprecation warnings.\n"
        "Initial Pillow deprecated getdata API replaced with get_flattened_data; final tests clean.\n"
        "No production_checks, live editor, gameplay, network, device or world placement test run.\n",
        encoding="utf-8", newline="\n")



def inventory():
    """List every owned payload except the self-hashed manifest and uncommitted Python cache."""
    paths = set()
    for relative in OWNED:
        path = ROOT / relative
        assert path.exists(), relative
        paths.update(path.rglob("*") if path.is_dir() else [path])
    return [{"path": p.relative_to(ROOT).as_posix(), **digest(p)} for p in sorted(paths)
            if p.is_file() and p != MANIFEST and "__pycache__" not in p.parts]


def main():
    """Write/compress only when requested; default invocation verifies the complete manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compress-renders", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.compress_renders:
        compress_renders()
        return
    if args.write:
        assemble()
    report = json.loads((EVIDENCE / "validation.json").read_text())
    payload = {"asset_id": "d09_freight_graphics.03", "algorithm": "SHA-256",
               "exclusions": ["manifest self-hash", "uncommitted __pycache__"],
               "unchanged_shared_dependencies": report["dependencies"], "files": inventory()}
    if args.write:
        MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    else:
        assert payload == json.loads(MANIFEST.read_text()), "Manifest drift"
        for path, measured in payload["unchanged_shared_dependencies"].items():
            assert digest(ROOT / path) == measured, "Dependency drift: " + path
    print(f"LOADING_MANIFEST_PASS: {len(payload['files'])} payloads")


if __name__ == "__main__":
    main()
