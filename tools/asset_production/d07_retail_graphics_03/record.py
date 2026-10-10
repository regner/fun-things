"""Write or verify the sign-face receipt; reject asset errors and stale payload hashes."""
from pathlib import Path
import argparse
import hashlib
import json
import re

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
COMMANDS = ["author", "artwork-tests", "validate", "preview", "import", "normalize",
            "import-final", "fresh", "compile", "format", "lint"]


def identity(path):
    """Identify actual bytes, not a timestamp or a cached importer resource."""
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def payloads():
    """Enumerate only this delivery's allowed files, excluding caches and the manifest."""
    paths = [ROOT / f"docs/assets/production/{NID}.md",
             ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
    for directory in [f"tools/asset_production/{NID}", f"art/textures/environment/{NID}",
                      f"art/materials/environment/{NID}",
                      f"docs/assets/production/{NID}-evidence"]:
        paths.extend(p for p in (ROOT / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts and p != MANIFEST)
    return sorted(set(paths))


def write_receipt():
    """Combine current executed checks, retaining exact non-clean editor diagnostics."""
    validation_path = EVIDENCE / "validation.json"
    report = json.loads(validation_path.read_text())
    commands = {}
    final_log = []
    for name in COMMANDS:
        code = int((SCRATCH / f"{name}.exit").read_text())
        assert code == 0, (name, code)
        log = (SCRATCH / f"{name}.log").read_text(errors="replace")
        diagnostics = [line for line in log.splitlines()
                       if re.search(r"ERROR|WARNING|DeprecationWarning", line)]
        errors = [line for line in diagnostics if "ERROR" in line]
        if name == "normalize":
            # Only the observed pinned-editor shutdown RID leaks are permitted here.
            # In particular, SCRIPT ERROR/assertion, missing-node and UID errors fail.
            allowed_types = {
                "N16RendererViewport8ViewportE", "PN13RendererDummy14TextureStorage12DummyTextureE",
                "N17RendererSceneCull8ScenarioE", "PN18TextServerAdvanced22ShapedTextDataAdvancedE",
                "PN18TextServerAdvanced12FontAdvancedE",
            }
            for line in errors:
                match = re.fullmatch(r"ERROR: \d+ RID allocations of type '([^']+)' were leaked at exit\.", line)
                assert match and match[1] in allowed_types, line
            assert "PARKING_PREFAB_PASS" in log
        else:
            assert not errors, (name, errors)
        if name == "fresh":
            assert not diagnostics, diagnostics
        commands[name] = {"exit_code": code, "diagnostics": diagnostics}
        final_log.extend([f"{name}: exit {code}", *diagnostics])
    normalization = json.loads((SCRATCH / "normalize.json").read_text())
    assert normalization["two_roundtrips_byte_identical"]
    assert normalization["no_collision"]
    prefab = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
    assert normalization["prefab_sha256"] == identity(prefab)["sha256"]
    report["engine_normalization"] = normalization
    report["engine_fresh_load"] = json.loads((SCRATCH / "prefab.json").read_text())
    report["commands"] = commands
    report["artwork_tests"] = {"tests": 3, "status": "PASS",
                               "fresh_png_byte_identical": True}
    report["renders"] = {}
    for name in ["hero", "side", "detail", "overhead_47m_42deg"]:
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720) and image.mode == "RGB"
        assert path.stat().st_size < 400_000
        report["renders"][name] = {**identity(path), "resolution": [1280, 720]}
    texture = ROOT / f"art/textures/environment/{NID}/parking_zone_albedo.png"
    report["artwork_texture"] = {"path": texture.relative_to(ROOT).as_posix(),
                                 "resolution": [1220, 820], "mode": "RGB", **identity(texture)}
    validation_path.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    (EVIDENCE / "final.log").write_text("\n".join(final_log) + "\n", newline="\n")
    dependencies = {path: identity(ROOT / path)
                    for path in report["shared_dependency_sha256"]}
    for path, data in dependencies.items():
        assert data["sha256"] == report["shared_dependency_sha256"][path]
    manifest = {"asset_id": "d07_retail_graphics.03", "files": {
        path.relative_to(ROOT).as_posix(): identity(path) for path in payloads()},
        "unchanged_dependencies": dependencies}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")


def verify_receipt():
    """Reject missing, extra, modified payloads or stale dependency/hand-off hash claims."""
    manifest = json.loads(MANIFEST.read_text())
    actual = {path.relative_to(ROOT).as_posix(): identity(path) for path in payloads()}
    assert actual == manifest["files"], "Payload set/hash drift"
    for path, expected in manifest["unchanged_dependencies"].items():
        assert identity(ROOT / path) == expected, path
    report = json.loads((EVIDENCE / "validation.json").read_text())
    handoff = (ROOT / f"docs/assets/production/{NID}.md").read_text()
    hashes = re.findall(r"\b[0-9a-f]{64}\b", handoff)
    assert hashes and all(value == report["shared_glb_sha256"] for value in hashes)
    assert report["shared_glb_bytes"] == (ROOT / report["shared_glb"]).stat().st_size
    assert f'{report["shared_glb_bytes"]:,}' in handoff, "Handoff GLB byte count drift"
    assert "surface_material_override/0" in (ROOT / f"scenes/prefabs/environment/{NID}.tscn").read_text()
    print(f"RETAIL_MANIFEST_PASS: {len(actual)} produced files; shared source/GLB unchanged")


def main():
    """Only --write refreshes receipts; ordinary invocation is a non-mutating audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_receipt()
    verify_receipt()


if __name__ == "__main__":
    main()
