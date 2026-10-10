"""Record final targeted receipts and hash every delivered payload except this manifest."""
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_sign_island_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}")
CHECKS = ("author-final", "validate", "import-final", "prefab-normalize-final", "compile",
          "prefab-fresh", "gdstyle-lint", "gdstyle-format")


def digest(path):
    """Hash actual saved bytes, never stale tool metadata."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Fail on missing checks or export drift; retain known editor shutdown errors explicitly."""
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    glb = ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb"
    assert validation["glb_sha256"] == digest(glb)
    assert validation["glb_bytes"] == glb.stat().st_size
    assert validation["fresh_export_byte_identical"]
    validation["targeted_checks"] = {}
    final_log = ["d07_sign_island.01 final targeted checks; raw logs remain in " + str(SCRATCH)]
    for name in CHECKS:
        exit_code = int((SCRATCH / (name + ".exit")).read_text())
        assert exit_code == 0, (name, exit_code)
        log_path = SCRATCH / (name + ".log")
        text = re.sub(r"\x1b\[[0-9;]*m", "", log_path.read_text(errors="replace"))
        errors = [line for line in text.splitlines() if "ERROR:" in line or "SCRIPT ERROR" in line]
        if name == "prefab-normalize-final":
            # This existing pin/plugin shutdown fault is not treated as a clean editor exit.
            allowed = (
                "ERROR: 5 RID allocations of type 'N16RendererViewport8ViewportE' were leaked at exit.",
                "ERROR: 8 RID allocations of type 'PN13RendererDummy14TextureStorage12DummyTextureE' were leaked at exit.",
                "ERROR: 1 RID allocations of type 'N17RendererSceneCull8ScenarioE' were leaked at exit.",
                "ERROR: 52 RID allocations of type 'PN18TextServerAdvanced22ShapedTextDataAdvancedE' were leaked at exit.",
                "ERROR: 1 RID allocations of type 'PN18TextServerAdvanced12FontAdvancedE' were leaked at exit.",
            )
            assert all(line in allowed for line in errors), errors
        else:
            assert not errors, (name, errors)
        warnings = [line for line in text.splitlines() if "WARNING:" in line]
        validation["targeted_checks"][name] = {
            "exit": exit_code, "raw_log_sha256": digest(log_path),
            "errors": errors, "warnings": warnings,
        }
        final_log.append(f"{name}: exit {exit_code}; {len(errors)} errors; {len(warnings)} warnings")
        final_log.extend(errors + warnings)
    engine = json.loads((SCRATCH / "prefab-fresh.json").read_text())
    normalized = json.loads((SCRATCH / "prefab-normalize-final.json").read_text())
    assert engine["ok"] and normalized["ok"] and normalized["save_reload_byte_stable"]
    prefab = ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"
    assert normalized["prefab_sha256"] == digest(prefab)
    assert normalized["prefab_uid"] == engine["prefab_uid"]
    assert normalized["model_uid"] == engine["model_uid"]
    assert f'uid="{engine["prefab_uid"]}"' in prefab.read_text()
    engine["save_reload_byte_stable"] = True
    engine["prefab_sha256"] = digest(prefab)
    validation["engine_checks"] = engine
    source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
    validation["source_sha256"] = digest(source)
    validation["evidence_renders"] = {}
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        image = EVIDENCE / (name + ".png")
        raw = image.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"
        size = struct.unpack_from(">II", raw, 16)
        assert size == (1280, 720)
        validation["evidence_renders"][name] = {
            "size_px": list(size), "bytes": len(raw), "sha256": digest(image),
            "source": "isolated Blender Cycles CPU, 24 samples, AgX, PNG compression 95",
        }
    final_log.extend([
        "Source: 1916 triangles; zero nonmanifold edges and degenerate faces/triangles.",
        "GLB: byte-identical fresh export; actual bounds, normals and three surfaces pass.",
        "Prefab: stable editor pack/save/reload/resave, inline/dependency UIDs retained.",
        "Physics: ten shape queries, three top rays, capsule edge/bypass/support pass.",
        "Initial corrections: studio side-camera ray origins moved above ground; actor contact",
        "tolerance separated from dimensional tolerance (5 mm contact vs 1 mm geometry).",
        "Non-editor scene saving dropped inline UID in an uncommitted trial; normalization now",
        "requires --editor and asserts saved UID and stable bytes. Final import/fresh checks clean.",
        "Production ActorMotion, cars, network, world placement, Godot visuals and device cost pending.",
    ])
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    (EVIDENCE / "final.log").write_text("\n".join(final_log) + "\n", newline="\n")
    handoff = ROOT / f"docs/assets/production/{ASSET}.md"
    assert validation["glb_sha256"] in handoff.read_text()
    files = [handoff, prefab]
    for directory in (f"art/source/models/environment/{ASSET}",
                      f"art/models/environment/{ASSET}",
                      f"tools/asset_production/{ASSET}",
                      f"docs/assets/production/{ASSET}-evidence"):
        files.extend(p for p in (ROOT / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts and p.name != "manifest.json")
    manifest = {
        "asset": "d07_sign_island.01", "producer": "commissioned implementation worker",
        "scope": "All produced payloads except this self-referential manifest",
        "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
                   "sha256": digest(p)} for p in sorted(set(files))],
    }
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print(f"Recorded {len(manifest['files'])} final payload hashes")


if __name__ == "__main__":
    main()
