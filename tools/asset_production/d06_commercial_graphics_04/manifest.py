"""Write or verify this asset's exact payload using the existing family inventory helper."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_04"
MANIFEST = ROOT / f"docs/assets/production/{NID}-evidence/manifest.json"
spec = importlib.util.spec_from_file_location(
    "family_manifest", ROOT / "tools/asset_production/d06_commercial_graphics_01/manifest.py")
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
# Reuse the inventory/hash routine without calling the hall's writing entrypoint.
family.MANIFEST = MANIFEST
family.OWNED = [
    f"art/textures/environment/{NID}",
    f"art/materials/environment/{NID}",
    f"tools/asset_production/{NID}",
    f"docs/assets/production/{NID}.md",
    f"docs/assets/production/{NID}-evidence",
    f"scenes/prefabs/environment/{NID}.tscn",
]


def main():
    """Only --write may refresh the producer manifest; default mode checks every hash."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = {
        "asset_id": "d06_commercial_graphics.04", "algorithm": "SHA-256",
        "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted cache)"],
        "files": family.inventory(),
    }
    if args.write:
        MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == report, "Manifest inventory or hashes differ"
    print(f"PASSAGE_MANIFEST_PASS: {len(report['files'])} payload files")


if __name__ == "__main__":
    main()
