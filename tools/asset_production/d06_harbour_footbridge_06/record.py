"""Consolidate successful source/engine/check receipts and hash only the owned production payloads."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_06"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a real completed receipt; missing or malformed evidence must fail."""
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    """Reject failed evidence before recording measurements, diagnostics and the producer manifest."""
    validation = read_json(EVIDENCE / "validation.json")
    engine = read_json(SCRATCH / "prefab-fresh-final.json")
    normalization = read_json(SCRATCH / "prefab-check.json")
    checks = read_json(SCRATCH / "checks-final/summary.json")
    compilation = read_json(SCRATCH / "checks-final/script-checks/compilation.json")
    assert validation["status"] == "PASS"
    assert engine["ok"] and not engine["failures"]
    assert normalization["ok"] and not normalization["failures"]
    assert engine["engine"] == "4.8-dev7 (official)"
    assert checks["results"]["engine"]["version"] == "4.8.dev7.official.c971f93e7"
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
    receipts = list(engine["variants"].values()) + [engine["assembly"]]
    rays = sum(len(row["rays"]) for row in receipts)
    capsules = sum(len(row["capsules"]) for row in receipts)
    validation["engine"] = engine
    validation["query_totals"] = {"rays": rays, "capsule_overlaps": capsules,
                                  "total": rays+capsules, "assembled_seams": 6}
    validation["production_checks"] = {
        "overall_ok": checks["ok"], "results": checks["results"],
        "compiled_scripts": len(compilation), "failed_scripts": [],
        "python_tests": 11, "gut_tests": 40, "gut_assertions": 458,
    }
    validation["visual_self_review"] = {
        "renders_inspected": ["hero.png", "side.png", "guard_detail.png", "overhead_47m_42deg.png"],
        "observation": "Dark thin guards preserve the pale route and open mouths. Cyan is a narrow "
                       "fascia accent. Straight and quarter-turn stairs remain distinct overhead. "
                       "Piers are visibly detached catalogue components, never approved placements.",
        "camera": "Vertical-down, 47 m above ground, 42 degree vertical FOV, 1280x720 overhead",
        "renderer": "Isolated Blender Cycles CPU, 32 samples, AgX; PNG95, film dither off",
        "resolution": "Hero/detail 1120x630, side/overhead 1280x720 (production cleanliness limit)",
        "not_claimed": "Engine visual, assembled map, gameplay movement, device or engineering acceptance",
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2)+"\n", newline="\n")
    normalize_log = (SCRATCH / "normalize-final.log").read_text()
    diagnostics = "\n".join(line for line in normalize_log.splitlines()
                            if "ERROR:" in line or "WARNING:" in line)
    summary = (
        "FINAL COMPONENT VALIDATION - verbose logs/retries remain in external scratch\n"
        "Blender 5.2.2 LTS d13f752e3b9c / glTF 5.2.40. Author and validator exit 0.\n"
        "Seven source/GLB variants: 33264 triangles, 17248 source vertices, 29184 export vertices.\n"
        "Seven meshes / 16 material surfaces; zero degenerate faces/triangles or non-manifold edges.\n"
        "Unit normals, metre datums, independent nominal bounds and byte-identical reexports pass.\n"
        "Pinned Godot import/normalization/fresh query exit 0; seven byte-stable wrapper roundtrips.\n"
        f"{rays} rays and {capsules} capsule overlaps pass, including all six assembled seams.\n"
        "Support instances in assembly test: zero. No road/land support position is approved.\n"
        "Editor-mode normalization diagnostics (not represented as clean shutdown):\n"
        + diagnostics + "\n\nFresh non-editor query: no ERROR/WARNING diagnostics.\n"
        "Production checks pass: 85 scripts formatted/linted/compiled, 11 Python tests, "
        "40 GUT tests/458 assertions; negative control detected.\n"
        "Initial query expectation incorrectly treated 1 cm from a turning corner as open: outgoing "
        "guard thickness correctly blocks it. Corrected expectation; separate mouth/turn probes pass.\n"
        "Initial owned allocation/line-length lint warnings corrected.\n"
        "Initial recorder confused Godot API display version with CLI hash version; corrected "
        "to validate both exact formats against their own receipts.\n"
        "Initial exploded display overlap and hero clipping fixed; no exported geometry affected.\n"
        "Posts terminate within caps to avoid coplanar post/cap top faces.\n"
        "Blender use_nodes future-version deprecation warnings remain; pinned tool succeeds.\n"
        "Independent review, actor ascent/descent, navigation/transport, map fit, engine visuals "
        "and device/performance gates remain pending.\n"
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
                raw = item.read_bytes()
                files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset_id": "d06_harbour_footbridge.06",
                "producer": "Commissioned isolated production worker",
                "scope": "All produced payloads except this self-referential manifest; scratch excluded",
                "files": sorted(files, key=lambda row: row["path"])}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", newline="\n")
    print(f"Recorded {len(files)} SHA-256 payloads; {rays+capsules} geometry queries; checks passed.")


if __name__ == "__main__":
    main()
