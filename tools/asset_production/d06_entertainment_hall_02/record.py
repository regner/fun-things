"""Consolidate final external check receipts and hash this asset's lean payloads."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_entertainment_hall_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a completed source or engine receipt without rerunning its checks."""
    return json.loads(path.read_text(encoding="utf-8"))


validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-fresh.json")
normalization = read_json(SCRATCH / "prefab-check.json")
checks = read_json(SCRATCH / "checks/summary.json")
compilation = read_json(SCRATCH / "checks/script-checks/compilation.json")
failed = [row["script"] for row in compilation if not row["ok"]]
assert engine["ok"] and not engine["failures"]
assert normalization["ok"] and normalization["save_reload_byte_stable"]
assert engine["prefab_uid"] == normalization["prefab_uid"]
assert all(path.startswith("tests/fixtures/asset_production/") for path in failed)
assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd" and row["ok"]
           for row in compilation)
assert "no issues found" in (SCRATCH / "checks/script-checks/style.log").read_text()
fresh_log = (SCRATCH / "prefab-fresh.log").read_text()
assert not any(marker in fresh_log for marker in ("ERROR:", "WARNING:"))
formatting = (SCRATCH / "checks/script-checks/formatting.log").read_text()
format_failures = [line for line in formatting.splitlines() if line.startswith("Would reformat:")]
assert len(format_failures) == 3
assert all(any(name in line for name in ("batch_observation.gd", "batch03_author.gd", "inspector.gd"))
           for line in format_failures)
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["engine"]["normalization_diagnostics"] = (
    "Initial editor pass produced no receipt; static-string/thread cleanup errors. "
    "Revised resource-only normalization exits 0 with successful two-save stability, "
    "but editor shutdown RID/ObjectDB leaks remain. Fresh runtime load is diagnostic-free."
)
validation["production_checks"] = {
    "results": checks["results"], "overall_ok": checks["ok"],
    "failed_compilation_paths": failed,
    "formatting_failures": format_failures,
    "owned_gdscript_style_format_compile": "PASS",
    "python_tests": 9, "gut_tests": 9, "gut_assertions": 70,
}
validation["visual_review"] = {
    "renders_inspected": ["hero.png", "side.png", "ring_detail.png", "overhead_47m_42deg.png"],
    "scratch_unlit_comparison_inspected": str(SCRATCH / "unlit_overhead.png"),
    "observation": "Continuous broad magenta shoulder visible around dome; quiet centre, legible unlit silhouette.",
    "renderer": "Blender Cycles CPU, 32 samples, AgX, 1280x800; not game lighting acceptance",
    "camera": "Vertical down, 47 m, 42 degree vertical perspective FOV, north up",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
normalize_log = (SCRATCH / "normalize-final.log").read_text()
diagnostics = "\n".join(line for line in normalize_log.splitlines()
                         if "ERROR:" in line or "WARNING:" in line)
summary = (
    "FINAL RECEIPT — full scratch logs outside checkout\n"
    "Blender 5.2.2 LTS / glTF 5.2.40 author and validator: exit 0.\n"
    "2040 triangles, 1020 source / 1156 GLB vertices, 1 mesh / 2 surfaces.\n"
    "Zero degenerate faces/triangles, zero nonmanifold edges; connected ring/diffuser.\n"
    "Bounds, normals, 8 visible diffuser camera rays and byte-identical reexport PASS.\n"
    "Author renders inspected including scratch emission-zero overhead.\n"
    "Headless import: completed, existing MCP 4.8 compatibility warning only.\n"
    "Initial normalize: no receipt, static-string/thread shutdown errors; exit not captured.\n"
    "Resource-only normalization simplified; revised command exit 0, stable two-save UIDs.\n"
    "Final editor diagnostics retained, not claimed fixed:\n" + diagnostics + "\n\n"
    "Fresh resource load: exit 0, no ERROR/WARNING:\n" + fresh_log + "\n"
    "Owned gdstyle 0.3.0 lint/format and compilation PASS.\n"
    "Production checks exit 1: known unrelated fixture compilation and integration formatting.\n"
    "Python 9/9; GUT 9/9 (70 assertions); negative-control detection PASS.\n"
    "Independent review, world placement/clearance, actual lighting and device performance pending.\n"
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
paths = [ROOT / f"art/source/models/environment/{NID}",
         ROOT / f"art/models/environment/{NID}", ROOT / f"tools/asset_production/{NID}",
         EVIDENCE, ROOT / f"docs/assets/production/{NID}.md",
         ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
files = []
for path in paths:
    for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
        if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
manifest = {
    "asset_id": "d06_entertainment_hall.02",
    "producer": "Commissioned isolated asset-production worker",
    "scope": "Every produced payload except this self-referential manifest; no scratch outputs",
    "files": sorted(files, key=lambda row: row["path"]),
}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"Recorded {len(files)} payload hashes; global failures remain visible.")
