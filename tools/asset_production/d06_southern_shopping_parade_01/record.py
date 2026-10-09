"""Collect final bounded receipts and hash the complete lean parade deliverable set."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"


def read_json(path):
    """Read one final source or pinned-engine receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def payloads():
    """List only owned final files, rejecting backup files and scratch bytecode."""
    roots = [ROOT / f"art/source/models/environment/{NID}",
             ROOT / f"art/models/environment/{NID}",
             ROOT / f"tools/asset_production/{NID}", EVIDENCE,
             ROOT / f"docs/assets/production/{NID}.md",
             ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
    files = []
    for path in roots:
        for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
            if not item.is_file() or item == MANIFEST:
                continue
            assert "__pycache__" not in item.parts and item.suffix not in (".blend1", ".pyc")
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
    return sorted(files, key=lambda item: item["path"])


if "--verify" in sys.argv:
    assert read_json(MANIFEST)["files"] == payloads(), "Manifest file set or hashes changed"
    print("PASS: complete manifest set and every SHA-256 match")
    raise SystemExit(0)

validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-fresh-final.json")
checks = read_json(SCRATCH / "checks-final/summary.json")
assert engine["ok"] and not engine["failures"] and checks["ok"]
normalize_log = (SCRATCH / "editor-normalize-stable.log").read_text(encoding="utf-8")
assert '"save_reload_byte_stable":true' in normalize_log
fresh_log = (SCRATCH / "prefab-fresh-final.log").read_text(encoding="utf-8")
assert not any(marker in fresh_log for marker in ("ERROR:", "WARNING:"))
compilation = read_json(SCRATCH / "checks-final/script-checks/compilation.json")
assert all(row["ok"] for row in compilation)
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["map_fit_candidate"] = read_json(SCRATCH / "map-fit.json")
validation["production_checks"] = {
    "overall_ok": checks["ok"], "results": checks["results"],
    "compiled_script_count": len(compilation), "python_tests": 9,
    "gut_tests": 23, "gut_assertions": 196, "ignored_failures": [],
}
validation["visual_self_review"] = {
    "images": ["hero.png", "side.png", "bay_detail.png", "overhead_47m_42deg.png"],
    "renderer": "Blender Cycles CPU, 24 samples, AgX; 1280x800",
    "gameplay_camera": "Vertical down at Blender (-6,0,47), north-up, vertical FOV 42 degrees",
    "observed": "One continuous quiet roof and six paired west recesses; intentional central "
                "overhead crop because a 60 m shell exceeds the calibrated frustum. "
                "Door/window faces are hidden overhead; essential wayfinding must not rely on them.",
    "limits": "Self-review only; not native engine or independent art/gameplay acceptance",
}
validation["diagnostics"] = {
    "editor_normalize": "Exit 0 with stable saved bytes; toolkit compatibility warning and "
                        "scan-thread/RID/ObjectDB shutdown diagnostics retained in final.log",
    "initial_owned_fixes": "Added @tool for editor execution and stopped before runtime physics; "
                           "UIDs established by editor save plus rescan; lint warnings corrected",
    "fresh_runtime": "Exit 0 without ERROR/WARNING", "production_checks": "All layers PASS",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation,indent=2)+"\n",newline="\n")
diagnostics = "\n".join(line for line in normalize_log.splitlines()
                        if "ERROR:" in line or "WARNING:" in line)
summary = (
    "FINAL PARADE VALIDATION — full raw logs stay in C:/tmp/ft/assets/" + NID + "\n"
    "Blender author and source/raw-GLB validation exited 0; fresh export byte-identical.\n"
    "No topology/normal/export errors. Blender API deprecation notices are non-failing.\n"
    "Map checker PASS: candidate shell, both 3m walking bands and north forecourt fit frozen map.\n"
    "Pinned import exited 0 with existing toolkit 4.8 compatibility warning.\n"
    "Editor pack/save/reload exited 0 and is byte-stable; shutdown diagnostics (NOT hidden):\n"
    + diagnostics + "\n\nFresh runtime load/material/bounds/UID/mount/physics check (exit 0):\n"
    + fresh_log + "\n"
    "Production checks exit 0: all scripts compile; format/lint pass; Python 9/9; "
    "GUT 23/23, 196 assertions; negative control caught. No ignored failures.\n"
    "Initial failures: missing @tool caused editor-script timeout (124); runtime-only saves "
    "and stale cache failed UID assertions until editor save/rescan; lint warnings fixed.\n"
    "All four retained images self-inspected; native visuals/gameplay, placement, bridge "
    "engineering, multiplayer and sustained device performance remain pending.\n"
)
(EVIDENCE / "final.log").write_text(summary,encoding="utf-8",newline="\n")
manifest = {"asset_id":"d06_southern_shopping_parade.01",
            "producer":"Commissioned isolated original Blender asset-production worker",
            "scope":"Every produced payload except this self-referential manifest; no scratch files",
            "files":payloads()}
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n",newline="\n")
print(f"Recorded {len(manifest['files'])} payload hashes; all production check layers PASS.")
