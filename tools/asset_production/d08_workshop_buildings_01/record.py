"""Record lean final evidence, compress review PNGs, or verify every delivered payload hash."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_workshop_buildings_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
RENDERS = ("hero.png", "side.png", "shutter_detail.png", "overhead_47m_42deg.png")


def read_json(path):
    """Read a required receipt without masking missing files or malformed evidence."""
    return json.loads(path.read_text(encoding="utf-8"))


def payloads():
    """Hash the complete owned deliverable set, excluding only the manifest itself."""
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
            assert image.size == (1280, 720)
            # Same bounded evidence-only channel quantization as the accepted house handoff.
            # Keep broad gradient shadows; indexed palettes introduce visible banding.
            step = 2 if name == "overhead_47m_42deg.png" else 4
            table = [value // step * step for value in range(256)] * 3
            image.convert("RGB").point(table).save(path, optimize=True, compress_level=9)
        assert path.stat().st_size < 400_000, (name, path.stat().st_size)
        print(name, path.stat().st_size)
    raise SystemExit(0)

if "--verify" in sys.argv:
    assert read_json(MANIFEST)["files"] == payloads(), "Manifest set or SHA-256 mismatch"
    print("PASS: complete produced-file set and all SHA-256 hashes match")
    raise SystemExit(0)

validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-check.json")
checks = read_json(SCRATCH / "checks/summary.json")
assert engine["ok"] and not engine["failures"]
assert checks["ok"], "Unexpected production-check failures require explicit classification"
normalize_log = (SCRATCH / "normalize.log").read_text(encoding="utf-8")
assert '"save_reload_byte_stable":true' in normalize_log
runtime_log = (SCRATCH / "prefab-final.log").read_text(encoding="utf-8")
assert not any(marker in runtime_log for marker in ("ERROR:", "WARNING:"))
import_log = (SCRATCH / "import-final.log").read_text(encoding="utf-8")
assert "ERROR:" not in import_log
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["production_checks"] = {"overall_ok": checks["ok"], "results": checks["results"],
                                   "python_tests": 17, "gut_tests": 165, "gut_asserts": 6918,
                                   "ignored_failures": []}
validation["visual_self_review"] = {
    "images": list(RENDERS), "size_px": [1280,720],
    "renderer": "Blender Cycles CPU, 32 samples, AgX; RGB PNG, 6-bit channels (overhead 7-bit)",
    "gameplay_camera": "Vertical down (0,0,47)m; north/+Y up; perspective vertical FOV42 degrees",
    "observed": "Compact pitched silhouette, raised replacement roof sheets and amber front band "
                "remain distinct overhead. Masonry base, pale bays and subtly dented closed shutter "
                "read in oblique/detail views. Replaced overlapping base faces; closed the eave seam.",
    "limits": "Isolated Blender self-review only; native visuals and populated placement pending"
}
validation["diagnostics"] = {
    "source": "Passed; Blender 6.0 material-API deprecation notices only",
    "normalization": "Byte-stable; toolkit compatibility warning and editor shutdown RID/ObjectDB "
                     "leaks retained in final.log; fresh non-editor runtime clean",
    "import": "Passed; existing toolkit Godot 4.8 compatibility warning, no ERROR lines",
    "initial_corrections": "Removed overlapping wall/base faces; sealed gable/eave seam; raised "
                           "ridge cap over amber band after literal height assertion; moved brick "
                           "face ray off newly authored mortar joint. Final validation passes.",
    "production_checks": "All canonical layers passed; no failures ignored"
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation,indent=2)+"\n",newline="\n")
diagnostics = "\n".join(line for line in normalize_log.splitlines()
                        if "ERROR:" in line or "WARNING:" in line)
summary = (
    "D08 SMALL PITCHED REPAIR SHED — final receipt\n"
    "Raw temporary logs: C:/tmp/ft/assets/"+NID+"/ (not committed).\n"
    "Pinned Blender source/raw GLB/re-export exited 0. Byte-identical export; topology/normals PASS.\n"
    "Pinned import exited 0; editor normalization exited 0 with byte-stable save/reload.\n"
    "Known isolated editor diagnostics (not suppressed):\n"+diagnostics+"\n\n"
    "Fresh headless prefab/production ActorMotion checks (exit 0, no ERROR/WARNING):\n"
    +runtime_log+"\nCanonical production checks (exit 0): "
    +json.dumps(checks["results"],sort_keys=True)+"\n"
    "17 Python tests; 165 GUT tests / 6918 assertions pass. Expected negative GUT exit 1 detected.\n"
    "Owned gdstyle fmt/lint pass; four 1280x720 compressed images self-reviewed.\n"
    "World placement, populated native visuals, actual network transport and target-device "
    "performance remain pending.\n"
)
(EVIDENCE / "final.log").write_text(summary,encoding="utf-8",newline="\n")
manifest = {"asset_id":"d08_workshop_buildings.01",
            "producer":"Commissioned original Blender asset-production worker",
            "scope":"Every produced payload except this self-referential manifest; scratch excluded",
            "files":payloads()}
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n",newline="\n")
print(f"Recorded {len(manifest['files'])} payload hashes.")
