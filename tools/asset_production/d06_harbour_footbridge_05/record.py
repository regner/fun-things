"""Consolidate successful measurements and retain a lean SHA-256 producer inventory."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_05"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a completed numerical receipt without substituting missing evidence."""
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    """Reject failed receipts, append measured engine/check outcomes, then hash all owned payloads."""
    validation = read_json(EVIDENCE / "validation.json")
    engine = read_json(SCRATCH / "prefab-fresh-final.json")
    normalization = read_json(SCRATCH / "prefab-check.json")
    checks = read_json(SCRATCH / "checks-final/summary.json")
    compilation = read_json(SCRATCH / "checks-final/script-checks/compilation.json")
    assert validation["status"] == "PASS"
    assert engine["ok"] and not engine["failures"]
    assert normalization["ok"] and not normalization["failures"]
    assert checks["ok"] and all(row["ok"] for row in checks["results"].values())
    assert all(row["ok"] for row in compilation)
    assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd" for row in compilation)
    fresh_log = (SCRATCH / "prefab-fresh-final.log").read_text()
    assert not any(marker in fresh_log for marker in ("ERROR:", "WARNING:"))
    for variant, source in validation["variants"].items():
        assert source["fresh_reexport_byte_identical"]
        glb = ROOT / f"art/models/environment/{NID}/{NID}_{variant}.glb"
        assert hashlib.sha256(glb.read_bytes()).hexdigest() == source["glb_sha256"]
        normal = normalization["variants"][variant]
        assert normal["save_reload_byte_stable"]
        for key in ("tscn_uid", "glb_uid"):
            assert normal[key] == engine["variants"][variant][key]
        engine["variants"][variant]["save_reload_byte_stable"] = True
    validation["engine"] = engine
    validation["production_checks"] = {
        "overall_ok": checks["ok"], "results": checks["results"],
        "compiled_scripts": len(compilation), "failed_scripts": [],
        "python_tests": 11, "gut_tests": 40, "gut_assertions": 458,
    }
    validation["visual_self_review"] = {
        "renders_inspected": ["hero.png", "side.png", "landing_detail.png", "overhead_47m_42deg.png"],
        "observation": "Straight and left/right quarter-turn routes, tread rhythm and clear landings read "
                       "overhead. Pale/slender family language preserved. No guards/supports claimed.",
        "camera": "Vertical-down, 47 m above ground, FOV 42 degrees, 1280x720; comparison offsets only",
        "renderer": "Isolated Blender Cycles CPU, 32 samples, AgX; PNG95, film dithering disabled",
        "not_claimed": "In-engine visual, movement, assembled-map or device acceptance",
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    normalize_log = (SCRATCH / "normalize-final.log").read_text()
    diagnostics = "\n".join(line for line in normalize_log.splitlines()
                            if "ERROR:" in line or "WARNING:" in line)
    summary = (
        "FINAL COMPONENT VALIDATION - verbose logs/retries retained in external scratch\n"
        "Blender 5.2.2 LTS d13f752e3b9c, glTF exporter 5.2.40. Author/validator exit 0.\n"
        "Per variant: 1908 triangles, 964 source vertices, 1728 exported vertices, 1 mesh/3 surfaces.\n"
        "Zero degenerate faces/triangles and non-manifold edges; unit normals; byte-identical reexports.\n"
        "Pinned Godot import, normalization and fresh load/query exit 0; all three wrappers byte-stable.\n"
        "69 geometry queries pass; two slopes per variant measure 28.24066 degrees.\n"
        "Source sockets and complete public transforms match; actual spans .02/.03/.04 mate flush.\n"
        "Editor-mode normalization shutdown diagnostics (not represented as clean):\n"
        + diagnostics + "\n\nFresh non-editor check: no ERROR/WARNING diagnostics.\n"
        "Production checks pass: 84 scripts formatted/linted/compiled, 11 Python tests, "
        "40 GUT tests/458 assertions; diagnostic negative control detected.\n"
        "Initial reversed quarter-turn public socket bases fixed in saved wrappers and authoring recipe.\n"
        "Initial lint warnings fixed; initial shell validator-writing syntax failure wrote no artifact.\n"
        "Blender use_nodes future-version deprecation warnings remain; pinned version succeeds.\n"
        "Version-only Blender probe reported one 23-byte unfreed block; asset author/validator did not.\n"
        "Hero camera revised to expose treads; studio horizon removed; film dither disabled for lean PNGs.\n"
        "Current player FLOATING mode and no gravity/floor following prevent traversal acceptance.\n"
        "Player lane owns that integration. Rails/supports remain .06-owned. No gameplay changes.\n"
        "Independent review, world fit, gameplay/transport, engine visual and device/performance pending.\n"
    )
    (EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
    paths = [ROOT / f"art/source/models/environment/{NID}",
             ROOT / f"art/models/environment/{NID}", ROOT / f"tools/asset_production/{NID}",
             ROOT / f"docs/assets/production/{NID}.md", EVIDENCE]
    paths.extend(sorted((ROOT / "scenes/prefabs/environment").glob(f"{NID}*.tscn")))
    files = []
    for path in paths:
        for item in sorted(path.rglob("*")) if path.is_dir() else [path]:
            if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
                data = item.read_bytes()
                files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                              "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {
        "asset_id": "d06_harbour_footbridge.05", "producer": "Commissioned isolated production worker",
        "scope": "All produced payloads except this self-referential manifest; no scratch outputs",
        "files": sorted(files, key=lambda row: row["path"]),
    }
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print(f"Recorded {len(files)} SHA-256 payloads; source/engine/canonical checks passed.")


if __name__ == "__main__":
    main()
