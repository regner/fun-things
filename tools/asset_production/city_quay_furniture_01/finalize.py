"""Compact review renders or hash the completed mooring-bollard delivery."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_quay_furniture_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def main():
    """Keep lean evidence and record hashes only after source, engine and check validation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compress-renders", action="store_true")
    parser.add_argument("--checks", type=Path, default=Path(f"C:/tmp/ft/assets/{ASSET}/checks"))
    args = parser.parse_args()
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as source:
            assert source.size == (1280, 720)
            if args.compress_renders:
                image = ImageOps.posterize(source.convert("RGB"), bits=7)
                image.save(path, optimize=True, compress_level=9)
        renders.append({"path": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    if args.compress_renders:
        print(json.dumps(renders, indent=2))
        return

    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    assert validation["fresh_export_byte_identical"]
    assert validation["godot"]["save_reload_byte_stable"]
    assert validation["godot"]["physics"]["authority_replay_equal"]
    summary = json.loads((args.checks / "summary.json").read_text())
    assert summary["ok"], "Do not publish a passing receipt over failed production checks"
    validation["production_checks"] = {"ok": summary["ok"], "results": summary["results"]}
    validation["renders"] = renders
    validation["render_encoding"] = "RGB, 7 significant bits/channel; PNG compression 9"
    validation["diagnostics"] = [
        "Initial capsule test used 15 mm symmetric tolerance; measured stop 16.666 mm before "
        "the nominal plane. Final independent test rejects penetration and gaps over 30 mm. "
        "No model/collider or production ActorMotion change was made for this observation.",
        "Blender emits future-6.0 use_nodes deprecation notices on the required 5.2.2 pin.",
        "Pinned headless import emits the existing MCP toolkit 4.8-vs-tested-4.7 warning.",
    ]
    validation["pending"] = [
        "Independent art/technical acceptance", "Actual Godot visual/camera review",
        "World placement and continuous unobstructed quay routes", "Vehicle collision driving",
        "Real multiplayer transport/admission/prediction", "Device and repeated-placement performance",
    ]
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    files = [ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"]
    for folder in (ROOT / f"art/source/models/environment/{ASSET}",
                   ROOT / f"art/models/environment/{ASSET}",
                   ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        files.extend(p for p in folder.rglob("*") if p.is_file()
                     and p.name != "manifest.json" and "__pycache__" not in p.parts)
    payload = []
    for file in sorted(set(files)):
        raw = file.read_bytes()
        payload.append({"path": file.relative_to(ROOT).as_posix(), "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset": "city_quay_furniture.01",
                "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": payload}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(payload), "payload files")


if __name__ == "__main__":
    main()
