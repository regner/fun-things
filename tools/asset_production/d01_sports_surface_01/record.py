"""Consolidate final receipts and hash all owned delivery payloads after checks and docs."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_sports_surface_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def read_json(path):
    """Load an actual completed check receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def diagnostics(name):
    """Retain diagnostic lines without conflating a zero exit with an error-free log."""
    return [line for line in (SCRATCH / f"{name}.log").read_text(encoding="utf-8").splitlines()
            if re.search(r"(?:ERROR:|SCRIPT ERROR:|WARNING:)", line)]


def main():
    """Verify receipt agreement, capture lean evidence and write the manifest last."""
    validation = read_json(EVIDENCE / "validation.json")
    artwork = read_json(SCRATCH / "artwork-check.json")
    engine = read_json(SCRATCH / "prefab-check.json")
    first = read_json(SCRATCH / "prefab-first-process.json")
    roundtrip = read_json(SCRATCH / "roundtrip.json")
    assert engine == first and engine["ok"] and not engine["failures"]
    assert roundtrip["ok"] and roundtrip["roundtrip_1_byte_stable"]
    assert roundtrip["roundtrip_2_byte_stable"]
    for key in engine:
        if key.endswith("_uid"):
            assert engine[key] == roundtrip[key]
    assert artwork["ok"] and artwork["byte_identical_reproduction"]
    assert validation["fresh_reexport_byte_identical"]
    assert artwork["png_sha256"] == validation["texture_sha256"]
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    assert glb.stat().st_size == validation["glb_bytes"]
    assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation["glb_sha256"]
    for name in ("import-final", "prefab-check", "prefab-second-process"):
        assert not [line for line in diagnostics(name) if "ERROR:" in line], name
    normalization_diagnostics = diagnostics("roundtrip")
    errors = [line for line in normalization_diagnostics if "ERROR:" in line]
    assert all("RID allocations of type" in line and "leaked at exit" in line for line in errors)
    assert "1 file already formatted" in (SCRATCH / "format.log").read_text(encoding="utf-8")
    assert "no issues found" in (SCRATCH / "style.log").read_text(encoding="utf-8")
    handoff = (ROOT / f"docs/assets/production/{NID}.md").read_text(encoding="utf-8")
    assert validation["glb_sha256"] in handoff and artwork["png_sha256"] in handoff
    assert f'{validation["glb_bytes"]:,}' in handoff and f'{artwork["png_bytes"]:,}' in handoff
    # Check every handoff hash against these final payload receipts, not historical values.
    assert set(re.findall(r"\b[0-9a-f]{64}\b", handoff)) == {
        validation["glb_sha256"], artwork["png_sha256"]}
    renders = []
    for name in ("hero", "side", "finish_detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        raw = path.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack_from(">II", raw, 16)
        assert (width, height) == (1280, 720)
        assert len(raw) < 400 * 1024
        renders.append({"file": path.name, "size": [width, height], "bytes": len(raw)})
    validation["artwork"] = artwork
    validation["engine"] = engine
    validation["roundtrip"] = roundtrip
    validation["second_runtime_process_exact_match"] = True
    validation["checks"] = {
        "final_import_error_lines": [], "runtime_error_lines": [],
        "gdstyle_format": "PASS", "gdstyle_lint": "PASS: zero warnings",
        "python_compile": "PASS", "production_checks_run": False,
        "headless_editor_normalization_exit": 0,
        "headless_editor_normalization_diagnostics": normalization_diagnostics,
        "normalization_disposition": "Byte-stable scene/material passes and matching UIDs; "
            "plugin version warning, scan abort and RID/ObjectDB shutdown leaks remain. "
            "Not a clean editor-log claim.",
    }
    validation["visual_review"] = {
        "renders_inspected": renders,
        "observation": "Quiet warm oval, six continuous lanes, one south finish and six readable "
            "numbers. Smooth curves and large open infield; no extra equipment or field geometry.",
        "renderer": "Isolated Blender Cycles CPU, 24 samples, AgX, RGB8 PNG compression 95",
        "camera": {"blender_position": [9, -18, 47], "rotation_radians": [0, 0, 0],
                   "vertical_fov_degrees": 42, "projection": "perspective",
                   "framing": "South finish/curve crop, not the entire 80 x 45 m oval"},
        "studio_ground": "Unexported plain quiet-green context only, not a delivered field",
        "godot_visual_acceptance": False,
    }
    validation["remaining_acceptance"] = [
        "Independent technical/art review and provisional dimensions/lane-count acceptance",
        "Saved world plot/terrain/perimeter placement and actual foot/car contacts",
        "Populated Godot lighting, moving-camera mip/depth/actor-contrast review",
        "LOD, packaging, world multiplayer integration and sustained Deck/performance checks",
    ]
    (EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    log = (
        "FINAL ASSET RECEIPT: d01_sports_surface.01\n"
        "Original Blender geometry + Pillow 12.3.0 artwork. No external fonts/models/images.\n"
        "Blender author and validator: exit 0, 5.2.2 LTS / exporter 5.2.40.\n"
        "516 source/export vertices, 516 triangles, one mesh, one surface.\n"
        "Zero degenerate faces/triangles; unit upward normals; identity transforms and UVs pass.\n"
        "516 justified boundary edges in two closed 258-edge loops; zero other non-manifold edges.\n"
        "Fresh saved-source GLB and original PIL PNG reproduction: byte-identical.\n"
        "Seven boundary pixel runs, six numeral regions, south-only finish, quiet fill: PASS.\n"
        "Four 1280x720 evidence renders inspected, all below 400 KiB.\n"
        "Python syntax compilation and final owned GDScript format/zero-warning lint: exit 0.\n"
        "Initial lint annotation syntax corrected to the pinned gdstyle ignore directive.\n"
        "Initial Pillow getdata deprecation removed before final artwork check.\n"
        "Initial checker compared CLI version text with Engine display string; corrected to\n"
        "check display version and c971f93e7 commit separately. No asset defect concealed.\n"
        "Headless editor normalization: exit 0; two byte-stable prefab/material roundtrips.\n"
        "Registered scene/material/model UIDs match both fresh runtime checks.\n"
        "Final headless import: exit 0, no ERROR/SCRIPT ERROR lines.\n"
        "Two fresh runtime checks: exit 0, no ERROR/SCRIPT ERROR lines, identical receipts.\n"
        "Prefab retains identity Visuals/Model, external material, no copied mesh or collision.\n"
        "No production_checks.py; no live owner session, world placement or gameplay modification.\n"
        "Editor shutdown diagnostics retained below; not a clean editor-log claim.\n\n"
        + "\n".join(normalization_diagnostics) + "\n\n"
        + (SCRATCH / "format.log").read_text(encoding="utf-8")
        + (SCRATCH / "style.log").read_text(encoding="utf-8")
    )
    (EVIDENCE / "final.log").write_text(log, encoding="utf-8", newline="\n")
    paths = [ROOT / f"art/{category}/environment/{NID}" for category in (
        "source/models", "models", "textures", "materials")]
    paths.extend([ROOT / f"tools/asset_production/{NID}", EVIDENCE,
                  ROOT / f"docs/assets/production/{NID}.md",
                  ROOT / f"scenes/prefabs/environment/{NID}.tscn"])
    files = []
    for path in paths:
        for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
            if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
                raw = item.read_bytes()
                files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset_id": "d01_sports_surface.01",
                "producer": "Commissioned isolated asset-production worker on lane/a-d01",
                "scope": "Every delivery payload except this self-referential manifest; no scratch",
                "files": sorted(files, key=lambda item: item["path"])}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print(f"TRACK_RECORD_PASS: {len(files)} final payload hashes; receipt/doc hashes agree")


if __name__ == "__main__":
    main()
