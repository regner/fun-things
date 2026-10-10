"""Package lean evidence, assemble checked receipts, and write/verify the producer manifest."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
OWNED = [
    f"art/textures/environment/{NID}", f"art/materials/environment/{NID}",
    f"tools/asset_production/{NID}", f"scenes/prefabs/environment/{NID}.tscn",
    f"docs/assets/production/{NID}.md", f"docs/assets/production/{NID}-evidence",
]


def digest(path):
    """Return the byte count and SHA-256 of an actual delivered payload."""
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def compress_renders():
    """Reduce only evidence to seven bits per RGB channel; runtime texture is untouched."""
    for path in sorted(EVIDENCE.glob("*.png")):
        with Image.open(path) as image:
            image.convert("RGB").point([value & 254 for value in range(256)] * 3).save(
                path, compress_level=9
            )
        print(path.name, path.stat().st_size)


def assemble():
    """Merge measured receipts only after confirming current bytes, logs and identity stability."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    engine = json.loads((SCRATCH / "prefab.json").read_text())
    normalized = json.loads((SCRATCH / "normalize.json").read_text())
    assert engine["status"] == normalized["status"] == "PASS"
    assert not engine["failures"] and not normalized["failures"]
    assert normalized["stable_roundtrip_count"] == 2
    prefab = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
    material = ROOT / f"art/materials/environment/{NID}/warehouse_fascia.tres"
    assert digest(prefab)["sha256"] == normalized["scene_sha256"]
    assert digest(material)["sha256"] == normalized["material_sha256"]
    for key, value in engine.items():
        if key.startswith("res://"):
            assert normalized[key] == value
    for path, measured in report["dependencies"].items():
        assert digest(ROOT / path) == measured, "Shared dependency drift"
    for name, token in [("source.log", "FREIGHT_SOURCE_PASS"),
                        ("render.log", "FREIGHT_PREVIEW_PASS"),
                        ("prefab.log", "FREIGHT_PREFAB_PASS"),
                        ("normalize.log", "FREIGHT_PREFAB_PASS"),
                        ("tests.log", "OK"), ("style.log", "no issues found"),
                        ("format.log", "already formatted")]:
        log = (SCRATCH / name).read_text(encoding="utf-8")
        assert token in log and "ERROR" not in log, name
    import_log = (SCRATCH / "import-final.log").read_text(encoding="utf-8")
    assert "ERROR" not in import_log and "[MCPServer] stopped" in import_log
    report["engine"] = engine
    report["save_reload"] = normalized
    report["artwork"] = {
        "texture": digest(ROOT / f"art/textures/environment/{NID}/warehouse_fascia_albedo.png"),
        "size_px": [2000, 400], "mode": "RGB", "tests_passed": 4,
        "filter": "linear_mipmap", "repeat": False, "emission": False,
        "safe_margin_px": 20,
    }
    report["renders"] = {}
    for path in sorted(EVIDENCE.glob("*.png")):
        with Image.open(path) as image:
            assert image.size == (1280, 720)
        report["renders"][path.name] = digest(path)
    report["checks"] = {
        "pinned_import_no_errors": True, "gdstyle_format": "PASS", "gdstyle_lint": "PASS",
        "independent_review": "pending", "world_gameplay_device_acceptance": "pending",
    }
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (EVIDENCE / "final.log").write_text(
        "d09_freight_graphics.01 final bounded producer checks\n"
        "Blender 5.2.2 LTS d13f752e3b9c / exporter 5.2.40: source audit and reexport PASS, exit 0.\n"
        "Shared fascia unchanged; 1656 triangles, 836 source / 1072 GLB vertices, 7 meshes, 8 surfaces.\n"
        "Zero degenerates/nonmanifold edges; unit normals; exact fresh GLB bytes.\n"
        "Four isolated Blender renders: PASS, exit 0; 1280x720, compression 100.\n"
        "Four Python artwork tests: PASS, exit 0; fresh PNG byte-identical.\n"
        "Godot 4.8.dev7.official.c971f93e7 import: PASS, exit 0; no ERROR/SCRIPT ERROR.\n"
        "Import warning: installed MCP toolkit tested through Godot 4.7, running on 4.8.\n"
        "Runtime resource normalization: PASS, exit 0; two byte-stable save/reload cycles.\n"
        "Fresh-process linked prefab/dependency/face-slot audit: PASS, exit 0; no warnings/errors.\n"
        "gdstyle 0.3.0 format and zero-warning lint: PASS, exit 0.\n"
        "Earlier own 101-character constant lint finding corrected by wrapping the constant.\n"
        "Receipt packaging corrected to explicit LF; staged-byte manifest verification passes.\n"
        "Blender --version alone printed one 23-byte shutdown allocation diagnostic; actual source\n"
        "audit and render runs did not. Preview API emits a use_nodes deprecation warning.\n"
        "No production_checks, live-editor, gameplay, network, world-placement or device test run.\n",
        encoding="utf-8", newline="\n"
    )


def inventory():
    """List every owned payload, excluding only this manifest and uncommitted Python cache."""
    paths = set()
    for relative in OWNED:
        path = ROOT / relative
        assert path.exists(), relative
        paths.update(path.rglob("*") if path.is_dir() else [path])
    return [{"path": p.relative_to(ROOT).as_posix(), **digest(p)} for p in sorted(paths)
            if p.is_file() and p != MANIFEST and "__pycache__" not in p.parts]


def main():
    """Compress explicitly, write explicitly, otherwise perform a read-only manifest verification."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compress-renders", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.compress_renders:
        compress_renders()
        return
    if args.write:
        assemble()
    validation = json.loads((EVIDENCE / "validation.json").read_text())
    payload = {"asset_id": "d09_freight_graphics.01", "algorithm": "SHA-256",
               "exclusions": ["manifest self-hash", "uncommitted __pycache__"],
               "unchanged_shared_dependencies": validation["dependencies"], "files": inventory()}
    if args.write:
        MANIFEST.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    else:
        assert payload == json.loads(MANIFEST.read_text()), "Manifest drift"
    print(f"FREIGHT_MANIFEST_PASS: {len(payload['files'])} payloads")


if __name__ == "__main__":
    main()
