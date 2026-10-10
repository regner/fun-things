"""Write or verify the complete producer inventory, excluding only this manifest itself."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "city_ground_finishes_02"
MANIFEST = ROOT / f"docs/assets/production/{NID}-evidence/manifest.json"
OWNED = [
    f"art/source/models/environment/{NID}",
    f"art/models/environment/{NID}",
    f"art/materials/environment/{NID}",
    f"art/textures/environment/{NID}",
    f"tools/asset_production/{NID}",
    f"docs/assets/production/{NID}.md",
    f"docs/assets/production/{NID}-evidence",
    f"scenes/prefabs/environment/{NID}.tscn",
]


def inventory():
    """Hash every delivered source, resource, tool, test and evidence file."""
    files = set()
    for relative in OWNED:
        path = ROOT / relative
        assert path.exists(), relative
        files.update(path.rglob("*") if path.is_dir() else [path])
    return [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(files) if path.is_file() and path != MANIFEST
            and "__pycache__" not in path.parts]


def main():
    """Write explicitly with --write; default mode rejects missing, extra or stale payloads."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = {"asset_id": "city_ground_finishes.02", "algorithm": "SHA-256",
              "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted cache)"],
              "files": inventory()}
    if args.write:
        MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == report, "Inventory or hashes differ"
    print(f"CONCRETE_MANIFEST_PASS: {len(report['files'])} payload files")


if __name__ == "__main__":
    main()
