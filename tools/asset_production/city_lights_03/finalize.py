"""Compact evidence and hash the complete owned delivery after the final pinned import."""
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_lights_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}")


def main():
    """Retain lean PNGs and precise check limitations; exclude only the manifest itself."""
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as source:
            assert source.size == (1280, 720)
            image = ImageOps.posterize(source.convert("RGB"), bits=7)
        image.save(path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["physics"]["authority_replay_equal"]
    summary = json.loads((SCRATCH / "checks/summary.json").read_text())
    compilation = json.loads((SCRATCH / "checks/script-checks/compilation.json").read_text())
    script_log = (SCRATCH / "checks/script-checks.log").read_text()
    script_result = json.loads(script_log.splitlines()[-1])
    python_log = (SCRATCH / "checks/python-tests.log").read_text()
    gut_log = (SCRATCH / "checks/gut.log").read_text()
    assert summary["results"]["python_tests"]["ok"] and summary["results"]["gut_tests"]["ok"]
    assert all(row["ok"] for row in compilation)
    assert script_result["formatting"] and script_result["style"]
    limitation = None
    if not summary["ok"]:
        import_log = (SCRATCH / "checks/script-checks/compiler-import.log").read_text(
            encoding="utf-8", errors="replace")
        assert "CHECK DEADLINE EXCEEDED" in import_log
        limitation = ("Overall exit 1: cold compiler-mirror import exceeded the shared tool's "
                      "30-second deadline. All per-script compiles and style checks passed; "
                      "subsequent GUT import, Python and GUT tests passed. No failure suppressed.")
    validation["production_checks"] = {
        "ok": summary["ok"], "results": summary["results"],
        "scripts_compiled": len(compilation), "scripts_failed": [],
        "formatting": script_result["formatting"], "lint": script_result["style"],
        "python_tests_passed": int(re.search(r"Ran (\d+) tests", python_log)[1]),
        "gut_tests_passed": int(re.search(r"Passing Tests\s+(\d+)", gut_log)[1]),
        "gut_assertions_passed": int(re.search(r"Asserts\s+(\d+)", gut_log)[1]),
        "limitation": limitation,
    }
    validation["renders"] = renders
    validation["render_encoding"] = "RGB, 7 significant bits/channel, PNG compression 9"
    validation["camera"] = {"type": "Blender perspective, vertical-down north-up",
                            "height_m": 47, "vertical_fov_degrees": 42,
                            "viewport_px": [1280, 720], "engine_capture": False}
    validation["remaining_acceptance"] = [
        "Independent asset review", "World placement and populated-camera occlusion",
        "Vehicle driving contacts", "Real multiplayer transport/prediction",
        "Deck/exported-build and repeated-placement performance", "Real lighting budgets",
    ]
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    files = [ROOT / f"docs/assets/production/{ASSET}.md"]
    files.extend((ROOT / "scenes/prefabs/environment").glob(f"{ASSET}*.tscn*"))
    for folder in (ROOT / f"art/source/models/environment/{ASSET}",
                   ROOT / f"art/models/environment/{ASSET}",
                   ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        files.extend(path for path in folder.rglob("*") if path.is_file()
                     and path.name != "manifest.json" and "__pycache__" not in path.parts)
    payload = []
    for path in sorted(set(files)):
        raw = path.read_bytes()
        payload.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset_id": "city_lights.03", "producer": "commissioned Codex specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": payload}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(payload), "payload files", renders)


if __name__ == "__main__":
    main()
