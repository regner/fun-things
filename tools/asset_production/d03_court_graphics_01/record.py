"""Consolidate completed motif checks and hash final delivery files, never scratch outputs."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_court_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read completed validator receipts rather than inventing outcomes."""
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    """Hash exact final bytes for source/export/document agreement."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Require passed checks, consolidate lean evidence, then generate the manifest last."""
    validation = read_json(EVIDENCE / "validation.json")
    artwork = read_json(SCRATCH / "artwork-check.json")
    engine = read_json(SCRATCH / "prefab-check.json")
    roundtrip = read_json(SCRATCH / "roundtrip.json")
    assert engine == read_json(SCRATCH / "prefab-first-process.json")
    assert engine["serialized_dependency_uids"]
    assert engine["ok"] and roundtrip["ok"] and artwork["ok"]
    assert all(roundtrip[f"roundtrip_{index}_byte_stable"] for index in (1, 2))
    assert artwork["byte_identical_reproduction"] and validation["fresh_reexport_byte_identical"]
    assert artwork["png_sha256"] == validation["texture_sha256"]
    source = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    texture = ROOT / f"art/textures/environment/{NID}/communal_circle_albedo.png"
    for path, size, digest in [(source, validation["source_bytes"], validation["source_sha256"]),
                               (glb, validation["glb_bytes"], validation["glb_sha256"]),
                               (texture, artwork["png_bytes"], artwork["png_sha256"])]:
        assert path.stat().st_size == size and sha(path) == digest
    for dependency in validation["studio_dependencies"]:
        assert sha(ROOT / dependency["path"]) == dependency["sha256"]
    scene = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
    material = ROOT / f"art/materials/environment/{NID}/communal_circle.tres"
    assert sha(scene) == roundtrip["prefab_sha256"]
    assert sha(material) == roundtrip["material_sha256"]
    warnings = []
    for name in ("import-final", "roundtrip", "prefab-check", "prefab-second-process"):
        text = (SCRATCH / f"{name}.log").read_text(encoding="utf-8")
        assert "ERROR" not in text, name
        warnings += [line for line in text.splitlines() if "WARNING" in line]
    assert "1 file already formatted" in (SCRATCH / "format.log").read_text(encoding="utf-8")
    assert "no issues found" in (SCRATCH / "style.log").read_text(encoding="utf-8")
    assert "PYTHON_COMPILE_PASS" in (SCRATCH / "python-check.log").read_text(encoding="utf-8")
    handoff = ROOT / f"docs/assets/production/{NID}.md"
    text = handoff.read_text(encoding="utf-8")
    assert set(re.findall(r"\b[0-9a-f]{64}\b", text)) == {
        validation["source_sha256"], validation["glb_sha256"], artwork["png_sha256"]}
    for size in (validation["source_bytes"], validation["glb_bytes"], artwork["png_bytes"]):
        assert f"{size:,}" in text
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        raw = path.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"
        dimensions = struct.unpack_from(">II", raw, 16)
        assert dimensions == (1280, 720) and len(raw) < 400 * 1024
        renders.append({"file": path.name, "dimensions": dimensions, "bytes": len(raw)})
    validation.update({
        "artwork": artwork, "engine": engine, "roundtrip": roundtrip,
        "second_fresh_runtime_receipt_identical": True,
        "checks": {"final_import_error_lines": [], "runtime_error_lines": [],
                   "warnings": warnings, "gdstyle_format": "PASS",
                   "gdstyle_lint": "PASS: zero warnings", "python_compile": "PASS",
                   "production_checks_run": False},
        "visual_self_review": {
            "renders_inspected": renders, "renderer": "Blender Cycles CPU, 24 samples, AgX",
            "encoding": "RGB8 PNG compression 95; no quantization or overlays",
            "overhead": {"position_blender_m": [0, 0, 47], "vertical_fov_degrees": 42,
                         "projection": "perspective", "north_up": True},
            "context": "Two unchanged linked city_seating_01 benches and three unchanged linked "
                       "Coral Courier source-pose figures; studio only, not runtime asset contents.",
            "observation": "The approximately 280-pixel circle remains complete and recognizable "
                           "despite local bench/person occlusion. Coral marks one quiet corner; "
                           "the centre stays open. Side/detail show flush broad inlays, not a curb.",
            "godot_gameplay_visual_acceptance": False},
        "remaining_acceptance": ["Independent technical/art review and provisional size approval",
                                 "Saved placement over continuous collision-bearing ground",
                                 "Godot populated lighting, moving-camera mip/depth/actor review",
                                 "Packaged builds, LOD and sustained device/performance checks"],
    })
    (EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")
    log = (
        "REVIEW ROUND 1: existing dependency UIDs serialized; no new identities.\n"
        "Saved header/dependency/node checks and two supplemented roundtrips pass.\n"
        "Missing and mismatched UID negative tests exit 1 as expected.\n"
        "Source/re-export, artwork, import/runtime, Python and gdstyle checks rerun.\n"
        "Visual inputs unchanged; original reviewed renders retained, not rerendered.\n"
        "The production author/render observations below are retained historical evidence.\n\n"
        "FINAL CHECKS: d03_court_graphics.01\n"
        "Original Pillow artwork and Blender annular carrier; no downloaded geometry/fonts/art.\n"
        "Pinned Blender author and validator exited 0. Saved-source re-export byte-identical.\n"
        "256 vertices/triangles, one mesh/surface, zero degenerates, upward unit normals.\n"
        "256 justified boundary edges in two closed loops; no other non-manifold edges.\n"
        "1024x1024 RGB artwork; fresh PNG identical, 53 independent region samples pass.\n"
        "Four 1280x720 isolated renders inspected, each below 400 KiB.\n"
        "Pinned headless normalization: two byte-stable scene/material passes, UIDs retained.\n"
        "Final import and two fresh runtime checks exited 0; no ERROR/SCRIPT ERROR lines.\n"
        "Runtime receipts identical; linked model, external material, mips, no collision.\n"
        "Python compile, gdstyle format and zero-warning lint pass.\n"
        "Initial lint found one overlong constant; split before final checks. A later format\n"
        "check requested one wrap; pinned formatter applied, final check passes.\n"
        "Blender author emitted pinned use_nodes future-removal deprecation warnings.\n"
        "No production_checks.py, live-owner editor access, world or gameplay changes.\n"
        "Final import warning (existing toolkit version advisory; not an asset failure):\n"
        + "\n".join(warnings) + "\n"
    )
    (EVIDENCE / "checks.log").write_text(log, encoding="utf-8", newline="\n")
    roots = [ROOT / f"art/{category}/environment/{NID}" for category in
             ("source/models", "models", "textures", "materials")]
    roots += [ROOT / f"tools/asset_production/{NID}", EVIDENCE, handoff, scene]
    files = []
    for root in roots:
        for path in sorted(root.rglob("*")) if root.is_dir() else [root]:
            if not path.is_file() or path.name == "manifest.json" or "__pycache__" in path.parts:
                continue
            raw = path.read_bytes()
            if path.suffix in (".py", ".gd", ".tscn", ".tres", ".import", ".md", ".json", ".uid", ".log"):
                assert b"\r\n" not in raw, path
            files.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset_id": "d03_court_graphics.01",
                "producer": "Commissioned isolated worker on lane/a-d03g",
                "scope": "Every produced file except self; studio dependencies unchanged",
                "files": sorted(files, key=lambda item: item["path"])}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                             encoding="utf-8", newline="\n")
    print(f"MOTIF_RECORD_PASS: {len(files)} final payload hashes; document/receipts agree")


if __name__ == "__main__":
    main()
