"""Consolidate completed checks and hash only the final community-board delivery."""
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_community_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read completed receipts rather than manufacturing test outcomes."""
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint(path):
    """Fingerprint exact final artifact bytes."""
    raw = path.read_bytes()
    return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}


def main():
    """Require passed checks, preserve dependency provenance and generate the manifest last."""
    validation = read_json(EVIDENCE / "validation.json")
    artwork = read_json(SCRATCH / "artwork-check.json")
    engine = read_json(SCRATCH / "prefab-check.json")
    roundtrip = read_json(SCRATCH / "roundtrip.json")
    assert engine == read_json(SCRATCH / "prefab-first-process.json")
    assert engine["serialized_dependency_uids"]
    assert engine["ok"] and roundtrip["ok"] and artwork["ok"]
    assert roundtrip["fresh_process_initial_byte_stable"]
    assert all(roundtrip[f"roundtrip_{i}_byte_stable"] for i in (1,2))
    assert validation["fresh_reexport_byte_identical"] and artwork["byte_identical_reproduction"]
    for path, receipt in validation["dependencies"].items():
        assert fingerprint(ROOT / path) == receipt
    texture = ROOT / f"art/textures/environment/{NID}/community_board_albedo.png"
    assert fingerprint(texture) == {"bytes":artwork["png_bytes"],"sha256":artwork["png_sha256"]}
    prefab = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
    material = ROOT / f"art/materials/environment/{NID}/community_board.tres"
    assert fingerprint(prefab)["sha256"] == roundtrip["prefab_sha256"]
    assert fingerprint(material)["sha256"] == roundtrip["material_sha256"]
    warnings = []
    for name in ("import-final","roundtrip","prefab-check","prefab-second-process"):
        text = (SCRATCH / f"{name}.log").read_text(encoding="utf-8")
        assert "ERROR" not in text, name
        warnings += [line for line in text.splitlines() if "WARNING" in line]
    assert "1 file already formatted" in (SCRATCH / "format.log").read_text()
    assert "no issues found" in (SCRATCH / "style.log").read_text()
    assert "PYTHON_COMPILE_PASS" in (SCRATCH / "python-check.log").read_text()
    renders = []
    for name in ("hero","side","detail","overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280,720) and image.mode == "RGB"
        assert path.stat().st_size < 400*1024
        renders.append({"file":path.name,"dimensions":[1280,720],**fingerprint(path)})
    handoff = ROOT / f"docs/assets/production/{NID}.md"
    text = handoff.read_text(encoding="utf-8")
    carrier_glb = validation["dependencies"][
        "art/models/environment/city_sign_supports_03/city_sign_supports_03.glb"]
    assert set(re.findall(r"\b[0-9a-f]{64}\b",text)) == {
        artwork["png_sha256"],carrier_glb["sha256"]}
    assert f'{artwork["png_bytes"]:,}' in text and f'{carrier_glb["bytes"]:,}' in text
    sibling_doc = ROOT / "docs/assets/production/city_sign_supports_03.md"
    sibling_manifest = ROOT / "docs/assets/production/city_sign_supports_03-evidence/manifest.json"
    entry = next(v for v in read_json(sibling_manifest)["files"]
                 if v["path"] == sibling_doc.relative_to(ROOT).as_posix())
    assert {key:entry[key] for key in ("bytes","sha256")} == fingerprint(sibling_doc)
    validation.update({
        "artwork":artwork,"engine":engine,"roundtrip":roundtrip,
        "second_fresh_runtime_receipt_identical":True,
        "checks":{"final_import_error_lines":[],"runtime_error_lines":[],"warnings":warnings,
                  "gdstyle_format":"PASS","gdstyle_lint":"PASS: zero warnings",
                  "python_compile":"PASS","production_checks_run":False},
        "visual_self_review":{
            "renders_inspected":renders,"renderer":"Blender Cycles CPU, 32 samples, AgX",
            "encoding":"RGB8 PNG compression 95, no dithering or post-quantization",
            "overhead":{"position_blender_m":[0,0,47],"vertical_fov_degrees":42,
                        "projection":"perspective","north_up":True},
            "observation":"Header, three separated notice fields and community/laundry icons read "
                          "upright in hero/detail; subdued teal, ivory and coral stay civic rather "
                          "than commercial. Side framing was widened to retain cap and feet. "
                          "Overhead shows only the approximately 40-pixel cap strip: the vertical "
                          "face is edge-on, so copy must not carry essential navigation.",
            "godot_gameplay_visual_acceptance":False},
        "remaining_acceptance":["Independent technical/art review and copy approval",
                                "Saved court-edge placement, populated visibility and movement",
                                "Godot lighting, moving-camera mips and actual camera views",
                                "Packaged builds, repeated-placement cost and device performance"],
    })
    (EVIDENCE / "validation.json").write_text(
        json.dumps(validation,indent=2)+"\n",encoding="utf-8",newline="\n")
    log = (
        "REVIEW ROUND 1: existing dependency UIDs serialized; no new identities.\n"
        "Saved header/dependency/node checks and two supplemented roundtrips pass.\n"
        "Missing and mismatched UID negative tests exit 1 as expected.\n"
        "Source/re-export, artwork, import/runtime, Python and gdstyle checks rerun.\n"
        "Visual inputs unchanged; original reviewed renders retained, not rerendered.\n"
        "The production author/render observations below are retained historical evidence.\n\n"
        "FINAL CHECKS: d03_community_graphics.01\n"
        "Original Pillow artwork: five tests pass; byte-identical PNG reproduction.\n"
        "Pinned Blender validator and previews exited 0; reused carrier never saved.\n"
        "Reused geometry: 2636 triangles, 1340 source / 1711 GLB vertices, 2 meshes / 5 surfaces.\n"
        "Zero degenerates/nonmanifold edges; unit normals, literal AABB and upright face UVs pass.\n"
        "Fresh carrier export via its original export contract is byte-identical.\n"
        "Four 1280x720 isolated renders inspected, each under 400 KiB.\n"
        "Two byte-stable scene/material roundtrips and fresh-process initial stability pass.\n"
        "Final pinned import and two fresh runtime checks exited 0 with no ERROR lines.\n"
        "Exactly one face override, unchanged inherited meshes/collider, full RGB8 mip chain.\n"
        "Python compile, gdstyle format and zero-warning lint pass.\n"
        "Initial checks caught default no-mip import and automatic compression policy; owned\n"
        "texture sidecar was corrected and reimported. No suppression or carrier import edit.\n"
        "Initial lint found one overlong texture constant; wrapped before final checks.\n"
        "Initial exact-color glyph occupancy missed antialiased thin ink; occupancy now counts\n"
        "near-ink pixels within 12 RGB levels, retaining the >400-pixel independent threshold.\n"
        "Initial side crop clipped the cap; widened framing and rerendered before final evidence.\n"
        "Finalizer caught Windows-default CRLF in generated evidence; writers now force LF.\n"
        "Blender emits its pinned use_nodes future-removal warning; final artwork tests are clean.\n"
        "No production_checks.py, live editor access, new geometry or gameplay changes.\n"
        "Final engine warnings:\n" + "\n".join(warnings) + "\n"
    )
    (EVIDENCE / "checks.log").write_text(log,encoding="utf-8",newline="\n")
    roots = [ROOT / f"art/{category}/environment/{NID}" for category in ("materials","textures")]
    roots += [ROOT / f"tools/asset_production/{NID}",EVIDENCE,handoff,prefab,
              sibling_doc,sibling_manifest]
    files = []
    for root in roots:
        for path in sorted(root.rglob("*")) if root.is_dir() else [root]:
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path == EVIDENCE / "manifest.json":
                continue
            if path.suffix != ".png":
                assert b"\r\n" not in path.read_bytes(), path
            files.append({"path":path.relative_to(ROOT).as_posix(),**fingerprint(path)})
    manifest = {"asset_id":"d03_community_graphics.01","producer":"worker on lane/a-d03g",
                "scope":"Every produced file except self, plus authorized carrier status reconciliation",
                "files":sorted(files,key=lambda v:v["path"])}
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"COMMUNITY_RECORD_PASS: {len(files)} payloads; document, receipts and dependencies agree")


if __name__ == "__main__":
    main()
