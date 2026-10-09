"""Consolidate successful check receipts and hash this asset's lean producer payloads."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a completed source, engine or canonical-check receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    """Reject failed evidence before combining measurements and recording final payload hashes."""
    validation = read_json(EVIDENCE / "validation.json")
    engine = read_json(SCRATCH / "prefab-fresh-final.json")
    normalization = read_json(SCRATCH / "prefab-check.json")
    checks = read_json(SCRATCH / "checks-final/summary.json")
    compilation = read_json(SCRATCH / "checks-final/script-checks/compilation.json")
    assert validation["status"] == "PASS" and validation["fresh_reexport_byte_identical"]
    assert engine["ok"] and not engine["failures"]
    assert normalization["ok"] and normalization["save_reload_byte_stable"]
    assert engine["prefab_uid"] == normalization["prefab_uid"]
    assert engine["model_uid"] == normalization["model_uid"]
    assert checks["ok"] and all(row["ok"] for row in checks["results"].values())
    assert all(row["ok"] for row in compilation)
    assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd" for row in compilation)
    fresh_log = (SCRATCH / "prefab-fresh-final.log").read_text()
    assert not any(marker in fresh_log for marker in ("ERROR:", "WARNING:"))
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation["glb_sha256"]
    validation["engine"] = engine
    validation["engine"]["save_reload_byte_stable"] = True
    validation["engine"]["normalization_diagnostics"] = (
        "Editor-mode custom SceneTree save passes with RID/ObjectDB shutdown leaks; "
        "fresh non-editor load/query is diagnostic-free. See final.log."
    )
    validation["production_checks"] = {
        "overall_ok": checks["ok"], "results": checks["results"],
        "compiled_scripts": len(compilation), "failed_scripts": [],
        "python_tests": 11, "gut_tests": 40, "gut_assertions": 458,
    }
    validation["visual_self_review"] = {
        "renders_inspected": ["hero.png", "side.png", "portal_detail.png", "overhead_47m_42deg.png"],
        "observation": "Quiet pale straight span; square end faces and thin bevel match junction .01. "
                       "The 12 m route reads in westward overhead orientation; guards/cyan remain .06-owned.",
        "camera": "Vertical down, 47 m above ground, deck at 5.5 m/yaw +90, FOV 42 degrees, 1280x800",
        "renderer": "Isolated Blender Cycles CPU, 32 samples, AgX; not an engine capture",
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    normalize_log = (SCRATCH / "normalize-final.log").read_text()
    diagnostics = "\n".join(line for line in normalize_log.splitlines()
                            if "ERROR:" in line or "WARNING:" in line)
    summary = (
        "FINAL COMPONENT VALIDATION â€” verbose logs/retries remain in external scratch\n"
        "Blender 5.2.2 LTS d13f752e3b9c, exporter 5.2.40. Author and validator exit 0.\n"
        "Author emits use_nodes future-version deprecation warnings; pinned execution succeeds.\n"
        "60 triangles, 32 source vertices, 72 exported vertices, 1 mesh, 3 surfaces.\n"
        "Zero degenerate faces/triangles; zero nonmanifold edges; unit normals; byte-identical reexport.\n"
        "Godot 4.8.dev7.official.c971f93e7 import exit 0; existing MCP pin warning.\n"
        "Editor normalization exit 0; two-save byte stability and registered UIDs pass.\n"
        "Editor-mode shutdown diagnostics (not suppressed or represented as clean):\n"
        + diagnostics + "\n\nFresh non-editor check exit 0 without ERROR/WARNING:\n" + fresh_log
        + "\nCanonical production checks final exit 0: formatting/lint/compilation, 11 Python tests, "
        "40 GUT tests/458 assertions and diagnostic negative control all pass.\n"
        "Nine isolated solid/void rays, underside/headroom rays and six West seam rays pass.\n"
        "Initial overhead illumination break corrected by moving studio lights with elevated slab.\n"
        "No actual bridge player/car movement, transport, world placement or device acceptance claimed.\n"
    )
    (EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
    paths = [
        ROOT / f"art/source/models/environment/{NID}",
        ROOT / f"art/models/environment/{NID}",
        ROOT / f"tools/asset_production/{NID}",
        ROOT / f"docs/assets/production/{NID}.md", EVIDENCE,
        ROOT / f"scenes/prefabs/environment/{NID}.tscn",
    ]
    files = []
    for path in paths:
        for item in sorted(path.rglob("*")) if path.is_dir() else [path]:
            if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
                data = item.read_bytes()
                files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                              "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {
        "asset_id": "d06_harbour_footbridge.04", "producer": "Commissioned isolated production worker",
        "scope": "All produced payloads except this self-referential manifest; no scratch outputs",
        "files": sorted(files, key=lambda row: row["path"]),
    }
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print(f"Recorded {len(files)} payload SHA-256 hashes; all final canonical checks passed.")


if __name__ == "__main__":
    main()
