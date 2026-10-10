"""Collect bounded final receipts and hash every owned deliverable, excluding this manifest."""
import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_harbour_hall_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a retained validation receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def diagnostics(path):
    """Keep warnings and errors visible even when a tool exited zero."""
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if re.search(r"(?:ERROR:|WARNING:|SCRIPT ERROR:)", line)]


validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-fresh-final.json")
second = read_json(SCRATCH / "prefab-second-process.json")
normalization = read_json(SCRATCH / "prefab-check.json")
checks = read_json(SCRATCH / "checks/summary.json")
compilation = read_json(SCRATCH / "checks/script-checks/compilation.json")
assert engine["ok"] and not engine["failures"]
assert engine == second, "Separate-process mounting checks differ"
assert normalization["two_scene_save_reload_byte_stable"]
assert engine["resource_uids"] == normalization["resource_uids"]
assert checks["ok"] and all(row["ok"] for row in checks["results"].values())
assert all(row["ok"] for row in compilation)
assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd" for row in compilation)
assert not diagnostics(SCRATCH / "prefab-fresh-final.log")
assert not diagnostics(SCRATCH / "prefab-second-process.log")
import_diagnostics = diagnostics(SCRATCH / "import-final.log")
assert all("WARNING: [MCP] Godot 4.8 detected" in line for line in import_diagnostics)
normalization_diagnostics = diagnostics(SCRATCH / "prefab-normalize-final.log")
validation["engine"] = engine
validation["engine"]["two_scene_save_reload_byte_stable"] = True
validation["engine"]["second_fresh_process_exact_match"] = True
validation["engine"]["normalization_diagnostics"] = normalization_diagnostics
validation["engine"]["final_import_diagnostics"] = import_diagnostics
python_log = (SCRATCH / "checks/python-tests.log").read_text(encoding="utf-8")
python_count = int(re.search(r"Ran (\d+) tests", python_log)[1])
gut_xml = ET.parse(SCRATCH / "checks/gut-results.xml").getroot()
gut_count = sum(1 for _ in gut_xml.iter("testcase"))
gut_log = (SCRATCH / "checks/gut.log").read_text(encoding="utf-8")
gut_assertions = int(re.search(r"Asserts\s+(\d+)", gut_log)[1])
validation["production_checks"] = {
    "overall_ok": checks["ok"],
    "results": checks["results"],
    "compiled_script_count": len(compilation),
    "failed_compilation_paths": [row["script"] for row in compilation if not row["ok"]],
    "owned_script_style_compile_and_format": "PASS",
    "python_tests": python_count,
    "gut_tests": gut_count,
    "gut_assertions": gut_assertions,
    "known_failure_exemptions": [],
}
renders = []
for name in ("hero", "side", "mount_detail", "overhead_47m_42deg"):
    path = EVIDENCE / f"{name}.png"
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack_from(">II", data, 16)
    assert width <= 1280 and height <= 720
    assert len(data) <= 400 * 1024
    renders.append({"file": path.name, "width": width, "height": height, "bytes": len(data)})
validation["visual_review"] = {
    "renders_inspected": renders,
    "observation": "Quiet chamfered teal hood and warm edge fit the hall. Mounted detail shows "
                   "the central entrance with no posts; overhead reveals a restrained entrance tab "
                   "beyond the roof. Side render floor horizon removed; detail resolution reduced "
                   "to keep lean evidence. Occlusion of directly-under-canopy actors is untested.",
    "renderer": "Blender Cycles CPU, 32 samples, AgX; not Godot visual acceptance",
    "gameplay_camera": "Vertical down, 47 m above ground, 42 degree vertical FOV, 1280x720",
    "png": "RGB8, compression 95, dither disabled; no image post-processing",
    "sibling_dependency": "d05_harbour_hall_01 source read-only in mounted evidence; not re-exported",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
summary = (
    "FINAL BOUNDED VALIDATION — d05_harbour_hall.02 / Entry canopy\n"
    "Blender 5.2.2 LTS / exporter 5.2.40: author-final and validate-final exit 0.\n"
    "792 source vertices; 1,556 triangles; 871 split GLB vertices; one mesh/three surfaces.\n"
    "Zero degenerate faces/triangles and non-manifold source edges; unit normals PASS.\n"
    "GLB 40,368 bytes; fresh saved-source export byte-identical.\n"
    "Initial relative Blender script argument resolved only as tools/ and exited 1.\n"
    "Absolute worktree script path corrected invocation; no unchanged retry.\n"
    "Initial gdstyle local-variable warning fixed by named UID inspection helper.\n"
    "Detail reduced to 1152x648; side floor horizon removed; final four PNGs inspected.\n"
    "Headless normalization exit 0; two owned scenes stable on second save.\n"
    "Normalization retains pinned editor shutdown diagnostics (not a clean-log claim):\n"
    + "\n".join(normalization_diagnostics) + "\n\n"
    "Final pinned worktree import exit 0; diagnostic:\n"
    + "\n".join(import_diagnostics) + "\n\n"
    "Two fresh runtime processes exit 0, diagnostic-free, exact JSON agreement.\n"
    "Checks: imported bounds/identity/materials, linked hall/canopy, 0.06 m lintel gap,\n"
    "3.5 m landing clearance, two standing-capsule queries and unchanged front wall ray.\n"
    + (SCRATCH / "prefab-fresh-final.log").read_text(encoding="utf-8") + "\n"
    f"Canonical production checks exit 0: {len(compilation)} scripts compile; style/format PASS; "
    f"Python {python_count}/{python_count}; GUT {gut_count}/{gut_count}, {gut_assertions} assertions.\n"
    "Negative control correctly detects intentional exit 1. No exemptions.\n"
    "Pending: independent review, gameplay camera/occlusion, placement, car/multiplayer,\n"
    "packaged build, Godot lighting/LOD, sustained target-device performance.\n"
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
paths = [
    ROOT / f"art/source/models/environment/{NID}",
    ROOT / f"art/models/environment/{NID}",
    ROOT / f"tools/asset_production/{NID}",
    EVIDENCE,
    ROOT / f"docs/assets/production/{NID}.md",
    *sorted((ROOT / "scenes/prefabs/environment").glob(f"{NID}*.tscn")),
]
files = []
for path in paths:
    for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
        if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
manifest = {
    "asset_id": "d05_harbour_hall.02",
    "producer": "Commissioned isolated asset-production worker",
    "scope": "Every produced deliverable except this self-referential manifest; no scratch files",
    "files": sorted(files, key=lambda item: item["path"]),
}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"Recorded {len(files)} payload hashes; source, engine and canonical checks PASS.")
