"""Compress review images, collect final receipts, or verify the exact producer manifest."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_house_family_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
RENDERS = ("hero.png", "side.png", "entrance_detail.png", "overhead_47m_42deg.png")


def read_json(path):
    """Read a UTF-8 validation receipt without hiding absent or malformed inputs."""
    return json.loads(path.read_text(encoding="utf-8"))


def payloads():
    """Enumerate every owned final payload except the self-referential manifest itself."""
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
            # Discard only low colour bits; a 256-colour palette visibly banded the soft shadows.
            # Geometry, framing and dimensions are unchanged; this is evidence-only compression.
            step = 2 if name == "overhead_47m_42deg.png" else 4
            table = [value // step * step for value in range(256)] * 3
            image.convert("RGB").point(table).save(path, optimize=True, compress_level=9)
        assert path.stat().st_size < 400_000, (name, path.stat().st_size)
        print(name, path.stat().st_size)
    raise SystemExit(0)

if "--verify" in sys.argv:
    assert read_json(MANIFEST)["files"] == payloads(), "Manifest expected set or SHA-256 changed"
    print("PASS: complete produced-file set and all SHA-256 hashes match")
    raise SystemExit(0)

validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-check.json")
checks = read_json(SCRATCH / "checks/summary.json")
assert engine["ok"] and not engine["failures"]
assert checks["ok"], "Classify unexpected production-check failures before recording success"
normalize_log = (SCRATCH / "normalize.log").read_text(encoding="utf-8")
assert '"save_reload_byte_stable":true' in normalize_log
runtime_log = (SCRATCH / "prefab-final.log").read_text(encoding="utf-8")
assert not any(marker in runtime_log for marker in ("ERROR:", "WARNING:"))
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["production_checks"] = {"overall_ok": checks["ok"], "results": checks["results"],
                                   "commands": checks["commands"],
                                   "ignored_failures": []}
validation["visual_self_review"] = {
    "images": list(RENDERS), "size_px": [1280,720],
    "renderer": "Blender Cycles CPU, 32 samples, AgX; RGB PNG, 6-bit channels (overhead 7-bit)",
    "gameplay_camera": "Vertical down (0,0,47)m; north/+Y up; perspective vertical FOV42 degrees",
    "observed": "A broad cross-frontage ridge and shorter, lower recessed end roof read "
                "overhead, unlike the detached hip and paired front-gable siblings. "
                "Three warm grade-level doors and quiet glazing read in detail. "
                "Floor courses terminate beside facade piers rather than intersecting them.",
    "limits": "Isolated Blender self-review only; native visuals and city placement remain pending"
}
validation["diagnostics"] = {
    "source": "Passed; Blender 6.0 API deprecation notices only",
    "normalization": "Passed stable save/reload; existing toolkit compatibility warning plus "
                     "scan-aborted/RID/ObjectDB shutdown diagnostics retained in final.log",
    "fresh_runtime": "Passed without ERROR/WARNING",
    "initial_corrections": "Split front floor courses beside the party-wall piers and extended "
                           "end courses to their wall corners after render inspection. "
                           "Default PATH engine lookup failed with Windows cp1252 decoding; "
                           "explicit mise-resolved executable paths passed the complete rerun.",
    "production_checks": "All layers passed, no failures ignored"
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation,indent=2)+"\n",newline="\n")
diagnostics = "\n".join(line for line in normalize_log.splitlines()
                        if "ERROR:" in line or "WARNING:" in line)
summary = (
    "D02 SHORT TERRACE — concise final receipt; raw scratch logs: C:/tmp/ft/assets/"+NID+"\n"
    "Blender source/raw buffers/reexport PASS; GLB byte-identical; topology/normals PASS.\n"
    "Pinned headless import PASS. Editor-only save/reload byte-stable. Known editor diagnostics:\n"
    + diagnostics + "\n\nFresh headless prefab/production ActorMotion checks (exit 0):\n"
    + runtime_log + "\nProduction checks: " + json.dumps(checks["results"],sort_keys=True) + "\n"
    "Four compressed images visually self-reviewed. No world placement, real-process networking, "
    "native visual or target-device performance acceptance claimed.\n"
)
(EVIDENCE / "final.log").write_text(summary,encoding="utf-8",newline="\n")
manifest = {"asset_id":"d02_house_family.03",
            "producer":"Commissioned original Blender asset-production worker",
            "scope":"Every produced payload except this self-referential manifest; scratch excluded",
            "files":payloads()}
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n",newline="\n")
print(f"Recorded {len(manifest['files'])} payload hashes.")
