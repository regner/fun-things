"""Collect final evidence or write/verify the exact campus-map producer manifest."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform

import PIL
from PIL import Image

import author

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_campus_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
OWNED = [
    f"art/textures/environment/{NID}", f"art/materials/environment/{NID}",
    f"scenes/prefabs/environment/{NID}.tscn", f"tools/asset_production/{NID}",
    f"docs/assets/production/{NID}.md", f"docs/assets/production/{NID}-evidence",
]


def entry(path):
    """Hash an actual final artifact, using portable repository-relative paths."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def inventory():
    """Inventory all produced payloads, excluding this manifest and uncommitted bytecode."""
    paths = set()
    for relative in OWNED:
        path = ROOT / relative
        paths.update(path.rglob("*") if path.is_dir() else [path])
    return [entry(p) for p in sorted(paths) if p.is_file() and p != MANIFEST
            and "__pycache__" not in p.parts]


def collect():
    """Merge fresh engine evidence only when current saved bytes match the roundtrip receipts."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    normalized = json.loads((SCRATCH / "normalize.json").read_text())
    runtime = json.loads((SCRATCH / "prefab.json").read_text())
    assert normalized["status"] == runtime["status"] == "PASS"
    assert normalized["stable_roundtrips"] == 2
    prefab = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
    material = ROOT / f"art/materials/environment/{NID}/campus_map.tres"
    assert normalized["roundtrip_sha256"] == [entry(prefab)["sha256"]]*3
    assert normalized["material_roundtrip_sha256"] == [entry(material)["sha256"]]*3
    assert runtime["prefab_uid"] == normalized["prefab_uid"]
    assert runtime["material_uid"] == normalized["material_uid"]
    import_log = (SCRATCH / "import-final.log").read_text(encoding="utf-8")
    runtime_log = (SCRATCH / "runtime.log").read_text(encoding="utf-8")
    assert "ERROR:" not in import_log and "SCRIPT ERROR:" not in import_log
    assert "ERROR:" not in runtime_log and "WARNING:" not in runtime_log
    output = io.BytesIO()
    author.create_artwork().save(output, format="PNG", compress_level=9)
    assert output.getvalue() == author.OUTPUT.read_bytes()
    report["engine"] = {"normalization": normalized, "runtime": runtime,
                        "final_import_no_errors": True, "runtime_no_diagnostics": True}
    report["artwork"].update({
        "texture": entry(author.OUTPUT), "fresh_png_byte_identical": True,
        "python": platform.python_version(), "pillow": PIL.__version__,
        "source_inputs": [entry(p) for p in (
            author.BOUNDARY, author.LETTERS,
            ROOT / "tools/asset_production/d06_commercial_graphics_01/author.py")],
    })
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720) and image.mode == "RGB"
        assert path.stat().st_size < 400_000
        renders.append(entry(path))
    report["renders"] = renders
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    print("CAMPUS_EVIDENCE_PASS: final resource hashes, PNG reproduction, engine receipts, renders")


def main():
    """Explicitly collect or write; default behavior verifies the complete final manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.collect:
        collect()
        return
    validation = json.loads((EVIDENCE / "validation.json").read_text())
    dependencies = validation["dependencies"] + validation["artwork"]["source_inputs"]
    assert dependencies == [entry(ROOT / item["path"]) for item in dependencies]
    report = {"asset_id": "d01_campus_graphics.01", "algorithm": "SHA-256",
              "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted)"],
              "unchanged_dependencies": dependencies, "files": inventory()}
    if args.write:
        MANIFEST.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == report, "Payload inventory/hash mismatch"
    print(f"CAMPUS_MANIFEST_PASS: {len(report['files'])} payload files")


if __name__ == "__main__":
    main()
