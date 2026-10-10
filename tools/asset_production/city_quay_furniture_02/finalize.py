"""Compress rail review renders or record final validation and payload SHA-256 hashes."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_quay_furniture_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def main():
    """Publish lean, independently verifiable receipts only after all required checks pass."""
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
                ImageOps.posterize(source.convert("RGB"), bits=7).save(
                    path, optimize=True, compress_level=9)
        renders.append({"file": path.name, "pixels": [1280, 720], "bytes": path.stat().st_size})
    if args.compress_renders:
        print(json.dumps(renders, indent=2))
        return
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text())
    assert all(item["fresh_export_byte_identical"] for item in validation["components"].values())
    assert validation["godot"]["save_reload_byte_stable"]
    assert len(validation["godot"]["prefabs"]) == 12
    assert all(item["physics"]["authority_replay_equal"]
               for item in validation["godot"]["prefabs"].values())
    assert validation["godot"]["access_opening"]["authority_replay_equal"]
    summary = json.loads((args.checks / "summary.json").read_text())
    assert summary["ok"], "Never publish passing production checks over a failure"
    validation["production_checks"] = {"ok": True, "results": summary["results"]}
    validation["renders"] = renders
    validation["render_settings"] = {
        "renderer": "Blender Cycles CPU", "samples": 32, "view_transform": "AgX",
        "encoding": "RGB, 7 significant bits/channel, PNG compression 9",
        "overhead": {"height_m": 47, "vertical_fov_degrees": 42,
                     "projection": "perspective", "orientation": "vertical-down; Blender +Y image-up"},
        "self_review": "All four final images inspected; no engine visual acceptance claimed",
    }
    validation["diagnostics"] = [
        "Initial test measured only one imported parent transform; fixed to traverse all ancestors. "
        "No model or placement was altered for the failed aggregate bounds assertion.",
        "Initial exact contact comparison rejected sub-micrometre floating-point differences. "
        "Final check allows 0.00001 m numeric tolerance and at most 0.03 m precontact gap; "
        "no production motion or collision changed.",
        "The new inherited opening fixture needed a post-normalization import to register its "
        "new scene UID for a fresh process. That import and subsequent fresh check passed.",
        "The first side render was crowded and had an orthographic near-plane ground crop. "
        "Final side isolates the straight rail and raises the studio camera; detail isolates mounts.",
        "Pinned Blender emits future-6.0 use_nodes deprecation notices. Pinned project import "
        "emits the existing MCP toolkit 4.8-versus-tested-4.7 warning. No suppression added.",
    ]
    validation["pending"] = [
        "Independent technical/art review", "Approval of provisional mounts/dimensions and connector fits",
        "Actual engine lighting/gameplay-camera review", "World route/shore/loading placement",
        "Vehicle collision/turning", "Real multiplayer transport/admission/prediction",
        "Packaged builds, repeated-placement performance and Deck profiling",
    ]
    path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
    files = [ROOT / f"docs/assets/production/{ASSET}.md"]
    files += list((ROOT / "scenes/prefabs/environment").glob(ASSET + "*.tscn"))
    for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                      ROOT / f"art/models/environment/{ASSET}",
                      ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        files += [p for p in directory.rglob("*") if p.is_file()
                  and p.name != "manifest.json" and "__pycache__" not in p.parts]
    payload = [{"path": file.relative_to(ROOT).as_posix(), "bytes": file.stat().st_size,
                "sha256": hashlib.sha256(file.read_bytes()).hexdigest()} for file in sorted(set(files))]
    manifest = {"asset": "city_quay_furniture.02", "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": payload}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(payload), "payload files")


if __name__ == "__main__":
    main()
