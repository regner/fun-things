"""Write or verify this asset's exact payload inventory using the existing manifest helper."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_repair_graphics_03"
MANIFEST = ROOT / f"docs/assets/production/{NID}-evidence/manifest.json"


def main():
    """Hash every produced payload except the manifest itself and ignored Python caches."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    path = ROOT / "tools/asset_production/d06_commercial_graphics_01/manifest.py"
    spec = importlib.util.spec_from_file_location("project_manifest_inventory", path)
    inventory = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventory)
    inventory.MANIFEST = MANIFEST
    inventory.OWNED = [
        f"art/textures/environment/{NID}", f"art/materials/environment/{NID}",
        f"tools/asset_production/{NID}", f"docs/assets/production/{NID}.md",
        f"docs/assets/production/{NID}-evidence",
        f"scenes/prefabs/environment/{NID}.tscn",
        f"scenes/prefabs/environment/{NID}_patched.tscn",
    ]
    report = {
        "asset_id": "d08_repair_graphics.03", "algorithm": "SHA-256",
        "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted cache)"],
        "files": inventory.inventory(),
    }
    validation = json.loads((MANIFEST.parent / "validation.json").read_text())
    report["shared_dependency_sha256"] = validation["shared_dependency_sha256"]
    for relative, expected in validation["shared_dependency_sha256"].items():
        assert inventory.hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    for appearance in validation["godot_normalization"]["variants"]:
        for kind in ("prefab", "material"):
            payload = ROOT / appearance[kind].removeprefix("res://")
            assert inventory.hashlib.sha256(payload.read_bytes()).hexdigest() == appearance[
                f"{kind}_sha256"]
    if args.write:
        MANIFEST.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == report, "Payload inventory or hashes changed"
    print(f"WARNING_MANIFEST_PASS: {len(report['files'])} payloads; shared and roundtrip hashes match")


if __name__ == "__main__":
    main()
