"""Write or verify the exact hall-title payload manifest, excluding only itself/cache."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_01"
MANIFEST = ROOT / f"docs/assets/production/{NID}-evidence/manifest.json"
OWNED = [
    f"art/textures/environment/{NID}",
    f"art/materials/environment/{NID}",
    f"scenes/prefabs/environment/{NID}.tscn",
    f"tools/asset_production/{NID}",
    f"docs/assets/production/{NID}.md",
    f"docs/assets/production/{NID}-evidence",
]


def inventory():
    """List hashes for all delivered files, including import metadata and tests."""
    files = set()
    for relative in OWNED:
        path = ROOT / relative
        files.update(path.rglob("*") if path.is_dir() else [path])
    return [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(files) if path.is_file() and path != MANIFEST
            and "__pycache__" not in path.parts]


def main():
    """Generate explicitly with --write; otherwise reject stale or missing payloads."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = {"asset_id": "d06_commercial_graphics.01", "algorithm": "SHA-256",
              "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted cache)"],
              "files": inventory()}
    if args.write:
        MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == report, "Manifest inventory or hashes differ"
    print(f"HALL_MANIFEST_PASS: {len(report['files'])} payload files")


if __name__ == "__main__":
    main()
