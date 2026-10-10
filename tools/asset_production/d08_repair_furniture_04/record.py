"""Finalize lean evidence and producer hashes; use --verify to audit without changing files."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d08_repair_furniture_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}")
MANIFEST = EVIDENCE / "manifest.json"
RENDERS = ("hero.png", "side.png", "detail.png", "overhead_47m_42deg.png")


def payloads():
    """Collect every owned delivery file except this self-referential manifest."""
    roots = [ROOT / f"art/source/models/environment/{ASSET}",
             ROOT / f"art/models/environment/{ASSET}",
             ROOT / f"tools/asset_production/{ASSET}", EVIDENCE,
             ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
    files = []
    for root in roots:
        assert root.exists(), root
        for path in sorted(root.rglob("*")) if root.is_dir() else [root]:
            if not path.is_file() or path == MANIFEST:
                continue
            assert "__pycache__" not in path.parts and path.suffix not in (".blend1", ".pyc")
            raw = path.read_bytes()
            files.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()})
    return sorted(files, key=lambda item: item["path"])


if "--compress-renders" in sys.argv:
    from PIL import Image, ImageOps
    for name in RENDERS:
        path = EVIDENCE / name
        with Image.open(path) as image:
            assert image.size == (1280, 720)
            bits = 7 if name == "overhead_47m_42deg.png" else 6
            ImageOps.posterize(image.convert("RGB"), bits=bits).save(
                path, optimize=True, compress_level=9)
        assert path.stat().st_size < 400_000, (name, path.stat().st_size)
        print(name, path.stat().st_size)
    raise SystemExit(0)

if "--verify" in sys.argv:
    assert json.loads(MANIFEST.read_text())["files"] == payloads(), "Manifest set/hash mismatch"
    print("PASS: complete produced-file set and SHA-256 hashes match")
    raise SystemExit(0)

validation_path = EVIDENCE / "validation.json"
validation = json.loads(validation_path.read_text())
engine = json.loads((SCRATCH / "prefab-check.json").read_text())
assert validation["fresh_reexport_byte_identical"] and engine["ok"] and not engine["failures"]
normalize_log = (SCRATCH / "normalize-editor.log").read_text()
assert '"save_reload_byte_stable":true' in normalize_log
runtime_log = (SCRATCH / "prefab-final.log").read_text()
assert not any(marker in runtime_log for marker in ("ERROR:", "WARNING:"))
import_log = (SCRATCH / "import-final.log").read_text()
assert "ERROR:" not in import_log
style_log = (SCRATCH / "style-final.log").read_text(encoding="utf-8").replace("✓", "PASS")
assert "no issues found" in style_log and "already formatted" in style_log
validation["godot"] = engine
validation["godot"]["save_reload_byte_stable"] = True
validation["renders"] = [{"file": name, "size_px": [1280, 720],
                         "bytes": (EVIDENCE / name).stat().st_size} for name in RENDERS]
validation["visual_self_review"] = {
    "renderer": "Isolated Blender Cycles CPU, 32 samples, AgX",
    "encoding": "RGB with 6 significant bits per channel (overhead 7); PNG compression 9",
    "camera": "Vertical down (0,0,47)m, Blender +Y north-up, perspective vertical FOV42 degrees",
    "observed": "Broad steel worktop, rear stop, fixed feet, two closed drawers and one lower "
                "bin read in close views, with localized wear. At 47m the quiet pale "
                "worktop rectangle and thin rear edge dominate. Drawers, feet, storage "
                "and abrasion are not claimed readable overhead.",
    "scope": "Self-review of Blender evidence, not native engine/world/device visual acceptance"
}
validation["diagnostics"] = {
    "source": "Pinned Blender passes; material API deprecation notices only",
    "editor": "Known toolkit compatibility warning, aborted scan and shutdown RID/ObjectDB "
              "leaks; successful normalization assertions, diagnostics retained in final.log",
    "import": "Exit 0; no ERROR/SCRIPT ERROR lines; existing toolkit compatibility warning",
    "runtime": "Exit 0; no ERROR/WARNING lines; all resource and physics assertions pass",
    "production_checks": "Not run, per owner decision 52"
}
validation_path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
diagnostics = "\n".join(line for line in normalize_log.splitlines()
                        if "ERROR:" in line or "WARNING:" in line)
summary = (
    "D08 COMPACT WORKBENCH - final bounded validation\n"
    "Raw logs/scratch: C:/tmp/ft/assets/d08_repair_furniture_04/ (not committed).\n"
    "Pinned Blender author, reexport, validator and four-view renderer: exit 0.\n"
    "Saved source/raw GLB topology, dimensions, normals and byte-identity checks pass.\n"
    "Pinned import: exit 0, no ERROR/SCRIPT ERROR lines.\n"
    "Headless editor load/pack/save/reload/save: exit 0, byte-stable normalized wrapper.\n"
    "Initial runtime-only UID omission fixed by editor roundtrip, not by hand-authored UID.\n"
    "Known headless editor shutdown diagnostics (not suppressed):\n" + diagnostics + "\n\n"
    "Fresh headless runtime load/resource/physics: exit 0, no ERROR/WARNING lines.\n"
    + runtime_log + "\nOwned GDScript checks:\n" + style_log + "\n"
    "Four 1280x720 renders inspected. Whole-world placement, native visuals, network transport "
    "and target-device performance remain pending. No production_checks.py run (decision 52).\n"
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
manifest = {"asset_id": "d08_repair_furniture.04",
            "producer": "Commissioned original Blender asset-production worker",
            "scope": "All produced payloads except this manifest; scratch excluded",
            "files": payloads()}
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print("Recorded", len(manifest["files"]), "payload SHA-256 hashes")
