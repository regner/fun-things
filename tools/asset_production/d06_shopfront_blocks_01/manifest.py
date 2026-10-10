"""Inventory final short-row payloads and read-only source/prefab dependencies."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d06_shopfront_blocks_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
MANIFEST = EVIDENCE / "manifest.json"


def describe(path):
    """Record final bytes with a repository-relative stable identity."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


files = [ROOT / f"docs/assets/production/{ASSET}.md"]
for folder in (EVIDENCE, ROOT / f"tools/asset_production/{ASSET}"):
    files.extend(p for p in folder.rglob("*") if p.is_file() and p != MANIFEST
                 and "__pycache__" not in p.parts)
files.extend((ROOT / "scenes/prefabs/environment").glob(ASSET + "*.tscn*"))
validation = json.loads((EVIDENCE / "validation.json").read_text())
dependencies = {ROOT / p.removeprefix("res://") for p in validation["dependencies"]}
dependencies.difference_update(files)
for model in validation["geometry"]["models"]:
    dependencies.add(ROOT / model["source"]["path"])
    dependencies.add(ROOT / (model["glb"]["path"] + ".import"))
report = {"asset_id": "d06_shopfront_blocks.01", "producer": "commissioned implementation worker",
          "self_exclusion": "manifest excludes itself to avoid recursive hashing",
          "files": [describe(p) for p in sorted(set(files))],
          "read_only_dependencies": [describe(p) for p in sorted(dependencies)]}
if "--verify" in sys.argv:
    assert json.loads(MANIFEST.read_text()) == report, "Payload/dependency manifest mismatch"
    print(f"MANIFEST_PASS: {len(files)} payloads; {len(dependencies)} read-only dependencies")
else:
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(f"MANIFEST_WRITTEN: {len(files)} payloads; {len(dependencies)} dependencies")
