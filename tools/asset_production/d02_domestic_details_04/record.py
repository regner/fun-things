"""Finalize lean evidence and verify every produced payload against its SHA-256 manifest."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_domestic_details_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
RENDERS = ("hero.png", "side.png", "detail.png", "overhead_47m_42deg.png")


def payloads():
    """Hash the complete owned payload set, excluding the self-referential manifest."""
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
            # Evidence-only six-bit RGB channels: no indexed-palette shadow banding.
            image.convert("RGB").point([v // 4 * 4 for v in range(256)] * 3).save(
                path, optimize=True, compress_level=9)
        assert path.stat().st_size < 400_000
        print(name, path.stat().st_size)
    raise SystemExit(0)

if "--verify" in sys.argv:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["files"] == payloads(), "Produced file set or bytes changed"
    print(f"PASS: complete expected set and all {len(manifest['files'])} payload SHA-256 hashes")
    raise SystemExit(0)

validation = json.loads((EVIDENCE / "validation.json").read_text(encoding="utf-8"))
engine = json.loads((SCRATCH / "prefab-check.json").read_text(encoding="utf-8"))
assert engine["ok"] and not engine["failures"]
normalize = (SCRATCH / "normalize-editor.log").read_text(encoding="utf-8")
runtime = (SCRATCH / "prefab-final.log").read_text(encoding="utf-8")
import_log = (SCRATCH / "import-final.log").read_text(encoding="utf-8")
assert '"save_reload_byte_stable":true' in normalize
assert "ERROR:" not in import_log and "SCRIPT ERROR:" not in import_log
assert "ERROR:" not in runtime and "WARNING:" not in runtime
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["visual_self_review"] = {
    "images": list(RENDERS), "size_px": [1280, 720],
    "renderer": "Blender Cycles CPU, 32 samples, AgX, six-bit RGB PNG",
    "gameplay_camera": "Vertical down (0,0,47)m; Blender +Y north/up; vertical FOV42 degrees",
    "observations": "Quiet sloped sage roof, ivory fascia and two slate wall brackets read as a "
                    "small domestic canopy in close views. The roof is approximately 43 pixels "
                    "wide overhead; brackets are not visible or used as gameplay information. "
                    "Final fascia corners and flashing are attached and free of black overlap artifacts.",
    "limits": "Isolated Blender self-review, not native gameplay or placed route acceptance"
}
validation["diagnostics"] = {
    "source": "Passed; Blender 6.0 use_nodes deprecation notices only",
    "import": "Passed without ERROR/SCRIPT ERROR; existing MCP 4.8 compatibility warning only",
    "normalization": "Passed stable save/reload with UIDs. Headless editor shutdown emitted existing "
                     "scan-aborted/RID/ObjectDB diagnostics; exact lines retained in final.log.",
    "fresh_runtime": "Passed with no ERROR/WARNING lines",
    "initial_corrections": "Coplanar roof/fascia and fascia corner faces showed black render "
                           "artifacts. Insets remove coplanarity; the flashing is deepened into "
                           "the roof and mounting plates extended to its underside. Final views "
                           "were rerendered and inspected after these source corrections."

}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n",
                                        encoding="utf-8", newline="\n")
normalization_diagnostics = "\n".join(line for line in normalize.splitlines()
                                     if "ERROR:" in line or "WARNING:" in line)
import_diagnostics = "\n".join(line for line in import_log.splitlines() if "WARNING:" in line)
summary = (
    "D02 porch canopy: final evidence receipt\n"
    "Source, binary GLB topology/normals/bounds and fresh byte-identical reexport: PASS (exit 0).\n"
    "Pinned headless import: PASS (exit 0), no ERROR/SCRIPT ERROR lines. Diagnostics:\n"
    + import_diagnostics + "\n"
    "Headless editor normalize/load/save: PASS (exit 0); stable second save, registered UIDs.\n"
    "Editor-only shutdown diagnostics (not hidden; absent from fresh runtime):\n"
    + normalization_diagnostics + "\n"
    "Fresh runtime prefab/ActorMotion/car clear-passage checks: PASS (exit 0):\n"
    + runtime + "\n"
    "Pinned gdstyle fmt --check: 1 file already formatted; strict lint: 1 file, no issues.\n"
    "Four renders manually inspected after correction/compression. No production_checks.py run.\n"
    "No world placement, real network transport, native visuals or device/performance acceptance.\n"
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
MANIFEST.write_text(json.dumps({
    "asset_id": "d02_domestic_details.04",
    "producer": "Commissioned original Blender asset-production worker",
    "scope": "Every produced payload except this manifest itself; scratch/review artifacts excluded",
    "files": payloads()
}, indent=2) + "\n", encoding="utf-8", newline="\n")
print("Recorded final validation, concise log and complete producer manifest")
