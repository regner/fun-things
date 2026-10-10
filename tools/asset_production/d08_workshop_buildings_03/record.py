"""Record lean evidence, compress review PNGs, or verify all produced payload hashes."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_workshop_buildings_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
RENDERS = ("hero.png", "side.png", "frontage_detail.png", "overhead_47m_42deg.png")


def read_json(path):
    """Require an existing, well-formed evidence receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def payloads():
    """Hash all owned deliverables except this self-referential manifest."""
    roots = [ROOT / f"art/source/models/environment/{NID}",
             ROOT / f"art/models/environment/{NID}",
             ROOT / f"tools/asset_production/{NID}", EVIDENCE,
             ROOT / f"docs/assets/production/{NID}.md",
             ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
    files = []
    for path in roots:
        assert path.exists(), path
        for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
            if not item.is_file() or item == MANIFEST:
                continue
            assert "__pycache__" not in item.parts and item.suffix not in (".blend1", ".pyc")
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
    return sorted(files, key=lambda item: item["path"])


if "--compress-renders" in sys.argv:
    from PIL import Image
    for name in RENDERS:
        path = EVIDENCE / name
        with Image.open(path) as image:
            target_size = (1280, 720) if name == "overhead_47m_42deg.png" else (1152, 648)
            assert image.size in ((1280, 720), target_size)
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            # Evidence-only channel quantization preserves geometry and material definitions.
            step = 2 if name == "overhead_47m_42deg.png" else 4
            table = [value // step * step for value in range(256)] * 3
            image.convert("RGB").point(table).save(path, optimize=True, compress_level=9)
        assert path.stat().st_size < 410 * 1024, (name, path.stat().st_size)
        print(name, path.stat().st_size)
    raise SystemExit(0)

if "--verify" in sys.argv:
    assert read_json(MANIFEST)["files"] == payloads(), "Manifest set or SHA-256 mismatch"
    print("PASS: complete produced-file set and all SHA-256 hashes match")
    raise SystemExit(0)

validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-check.json")
assert engine["ok"] and not engine["failures"]
normalize_log = (SCRATCH / "normalize.log").read_text(encoding="utf-8")
assert '"save_reload_byte_stable":true' in normalize_log
runtime_log = (SCRATCH / "prefab-final.log").read_text(encoding="utf-8")
assert not any(marker in runtime_log for marker in ("ERROR:", "WARNING:"))
import_log = (SCRATCH / "import-final.log").read_text(encoding="utf-8")
assert "ERROR:" not in import_log and "SCRIPT ERROR" not in import_log
style_log = (SCRATCH / "style-final.log").read_text(encoding="utf-8")
assert "no issues found" in style_log and "already formatted" in style_log
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["checks"] = {
    "pinned_import_no_errors": True, "prefab_runtime_no_errors_or_warnings": True,
    "owned_gdstyle_format_and_lint": True,
    "production_checks": "Not run, per owner decision 52 for unplaced assets"
}
validation["visual_self_review"] = {
    "images": list(RENDERS), "oblique_size_px": [1152,648], "overhead_size_px": [1280,720],
    "renderer": "Blender Cycles CPU, 32 samples, AgX; RGB PNG, 6-bit channels (overhead 7-bit)",
    "gameplay_camera": "Vertical down (0,0,47)m; north/+Y up; perspective vertical FOV42 degrees",
    "observed": "Two unequal pitches, four broad repair sheets, dark valley and one amber front "
                "band read overhead. Three dented closed shutters, a lower side roof and quiet "
                "five-bay flank distinguish this depot from both siblings. Brick base, localized "
                "wear and pale datums preserve the family vocabulary.",
    "limits": "Isolated Blender self-review only; native visuals and populated placement pending"
}
validation["diagnostics"] = {
    "source": "Passed; Blender 6.0 material-API deprecation notices only",
    "normalization": "Byte-stable; toolkit compatibility warning, aborted scan and editor "
                     "shutdown RID/ObjectDB leaks retained in final.log; non-editor runtime clean",
    "import": "Passed; existing toolkit Godot 4.8 compatibility warning, no ERROR/SCRIPT ERROR",
    "initial_corrections": "One extra GDScript blank line fixed by formatter. Non-editor save "
                           "did not supply resource UIDs; headless editor supplied stable UIDs. "
                           "Initial evidence recorder syntax error fixed before receipts were written."
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2)+"\n", newline="\n")
diagnostics = "\n".join(line for line in normalize_log.splitlines()
                        if "ERROR:" in line or "WARNING:" in line)
summary = (
    "D08 LARGER DEPOT - final receipt\n"
    f"Raw temporary logs: C:/tmp/ft/assets/{NID}/ (not committed).\n"
    "Pinned Blender source/raw GLB/re-export exited 0; byte-identical, topology/normals PASS.\n"
    "Pinned import exited 0, no ERROR/SCRIPT ERROR; editor normalization exited 0, stable saves.\n"
    "Known isolated editor diagnostics (not suppressed):\n" + diagnostics + "\n\n"
    "Fresh headless prefab/production ActorMotion checks (exit 0, no ERROR/WARNING):\n"
    + runtime_log + "\nOwned pinned gdstyle formatting/lint (exit 0):\n" + style_log + "\n"
    "No production_checks.py run, per owner decision 52.\n"
    "Four compressed images self-reviewed (1152x648 obliques, 1280x720 overhead).\n"
    "Placement, populated native visuals, network transport and target-device checks pending.\n"
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
manifest = {"asset_id": "d08_workshop_buildings.03",
            "producer": "Commissioned original Blender asset-production worker",
            "scope": "Every produced payload except this self-referential manifest; scratch excluded",
            "files": payloads()}
MANIFEST.write_text(json.dumps(manifest, indent=2)+"\n", newline="\n")
print(f"Recorded {len(manifest['files'])} payload hashes.")
