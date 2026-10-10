"""Collect final entry-panel receipts and inventory every deliverable with SHA-256."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform

import PIL
from PIL import Image

import author

ROOT = author.ROOT
NID = author.NID
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
OWNED = [
    f"art/textures/environment/{NID}", f"art/materials/environment/{NID}",
    f"scenes/prefabs/environment/{NID}.tscn", f"tools/asset_production/{NID}",
    f"docs/assets/production/{NID}.md", f"docs/assets/production/{NID}-evidence",
]


def entry(path):
    """Hash the final on-disk payload with a portable repository-relative path."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def inventory():
    """Inventory owned payloads only, excluding the manifest and uncommitted Python cache."""
    paths = set()
    for relative in OWNED:
        path = ROOT / relative
        paths.update(path.rglob("*") if path.is_dir() else [path])
    return [entry(p) for p in sorted(paths) if p.is_file() and p != MANIFEST
            and "__pycache__" not in p.parts]


def collect():
    """Join current source, engine and image proofs without accepting stale roundtrip bytes."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    normalized = json.loads((SCRATCH / "normalize.json").read_text())
    runtime = json.loads((SCRATCH / "prefab.json").read_text())
    assert normalized["status"] == runtime["status"] == "PASS"
    assert normalized["stable_roundtrips"] == 2
    for key, path in [
        ("roundtrip_sha256", ROOT / f"scenes/prefabs/environment/{NID}.tscn"),
        ("material_roundtrip_sha256", ROOT / f"art/materials/environment/{NID}/entry_panel.tres"),
    ]:
        assert normalized[key] == [entry(path)["sha256"]]*3
    for key in ("prefab_uid", "material_uid"):
        assert normalized[key] == runtime[key]
    for name in ("import-final", "runtime"):
        text = (SCRATCH / f"{name}.log").read_text(encoding="utf-8")
        assert "ERROR:" not in text and "SCRIPT ERROR:" not in text
        if name == "runtime":
            assert "WARNING:" not in text and "CAMPUS_PREFAB_PASS" in text
    output = io.BytesIO()
    author.create_artwork().save(output, format="PNG", compress_level=9)
    assert output.getvalue() == author.OUTPUT.read_bytes()
    report["engine"] = {"normalization": normalized, "runtime": runtime,
                        "final_import_no_errors": True, "runtime_no_diagnostics": True,
                        "pin": "4.8.dev7.official.c971f93e7"}
    report["artwork"].update({
        "texture": entry(author.OUTPUT), "fresh_png_byte_identical": True,
        "python": platform.python_version(), "pillow": PIL.__version__,
        "source_inputs": [entry(p) for p in (
            author.FAMILY_SOURCE, author.family.LETTERS,
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
    print("ENTRY_PANEL_EVIDENCE_PASS: PNG, final resource hashes, engine receipts and renders")


def main():
    """Collect explicitly, write last, and otherwise verify hashes plus complete file inventory."""
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
    report = {"asset_id": "d01_campus_graphics.02", "algorithm": "SHA-256",
              "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted)"],
              "unchanged_dependencies": dependencies, "files": inventory()}
    if args.write:
        MANIFEST.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == report, "Payload inventory/hash mismatch"
    print(f"ENTRY_PANEL_MANIFEST_PASS: {len(report['files'])} payload files")


if __name__ == "__main__":
    main()
