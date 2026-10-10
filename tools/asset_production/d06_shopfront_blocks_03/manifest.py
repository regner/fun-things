"""Inventory final chamfered-corner payloads and unchanged shared fitting dependencies."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d06_shopfront_blocks_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
MANIFEST = EVIDENCE / "manifest.json"


def describe(path):
    """Record final bytes with a repository-relative stable identity."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


files = [ROOT / f"docs/assets/production/{ASSET}.md"]
for folder in (EVIDENCE, ROOT / f"tools/asset_production/{ASSET}",
               ROOT / f"art/source/models/environment/{ASSET}",
               ROOT / f"art/models/environment/{ASSET}"):
    files.extend(p for p in folder.rglob("*") if p.is_file() and p != MANIFEST
                 and "__pycache__" not in p.parts)
files.extend((ROOT / "scenes/prefabs/environment").glob(ASSET + "*.tscn*"))
validation = json.loads((EVIDENCE / "validation.json").read_text())
dependencies = {ROOT / p.removeprefix("res://") for p in validation["dependencies"]}
for model in validation["model_instances"]:
    path = ROOT / model["path"].removeprefix("res://")
    dependencies.add(Path(str(path) + ".import"))
    owner = path.parent.name
    dependencies.add(ROOT / f"art/source/models/environment/{owner}/{owner}.blend")
dependencies.add(ROOT / "tools/assets/blender/export_settings.json")
dependencies.difference_update(files)
report = {"asset_id": "d06_shopfront_blocks.03", "producer": "commissioned implementation worker",
          "self_exclusion": "manifest excludes itself to avoid recursive hashing",
          "files": [describe(p) for p in sorted(set(files))],
          "read_only_dependencies": [describe(p) for p in sorted(dependencies)]}
if "--verify" in sys.argv:
    assert json.loads(MANIFEST.read_text()) == report, "Payload/dependency manifest mismatch"
    print(f"MANIFEST_PASS: {len(files)} payloads; {len(dependencies)} read-only dependencies")
else:
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(f"MANIFEST_WRITTEN: {len(files)} payloads; {len(dependencies)} dependencies")
