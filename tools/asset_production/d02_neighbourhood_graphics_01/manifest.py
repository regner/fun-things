"""Use the existing exact-payload inventory implementation for this artwork's owned paths."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_01"
SHARED = ROOT / "tools/asset_production/d06_commercial_graphics_01/manifest.py"
spec = importlib.util.spec_from_file_location("project_asset_manifest", SHARED)
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
shared.MANIFEST = ROOT / f"docs/assets/production/{NID}-evidence/manifest.json"
shared.OWNED = [
    f"art/textures/environment/{NID}", f"art/materials/environment/{NID}",
    f"scenes/prefabs/environment/{NID}.tscn", f"tools/asset_production/{NID}",
    f"docs/assets/production/{NID}.md", f"docs/assets/production/{NID}-evidence",
]


def main():
    """Regenerate only explicitly; default verifies the complete final payload inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = {
        "asset_id": "d02_neighbourhood_graphics.01", "algorithm": "SHA-256",
        "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted cache)"],
        "files": shared.inventory(),
    }
    if args.write:
        shared.MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    else:
        assert json.loads(shared.MANIFEST.read_text()) == report, "Stale payload manifest"
    print(f"WATCH_MANIFEST_PASS: {len(report['files'])} payloads")


if __name__ == "__main__":
    main()
