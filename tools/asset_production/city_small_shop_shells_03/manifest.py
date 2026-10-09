"""Hash only this asset's final deliverables; never include scratch or unrelated lane files."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_small_shop_shells_03"
MANIFEST = ROOT / f"docs/assets/production/{ASSET}-evidence/manifest.json"


def describe(path):
    """Record one payload's repository-relative identity, bytes and SHA-256."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


paths = []
for folder in (f"art/source/models/environment/{ASSET}", f"art/models/environment/{ASSET}",
               f"docs/assets/production/{ASSET}-evidence", f"tools/asset_production/{ASSET}"):
    paths.extend(path for path in (ROOT / folder).rglob("*")
                 if path.is_file() and path != MANIFEST and "__pycache__" not in path.parts)
paths.append(ROOT / f"docs/assets/production/{ASSET}.md")
paths.extend((ROOT / "scenes/prefabs/environment").glob(ASSET + "*.tscn*"))
files = [describe(path) for path in sorted(set(paths))]
dependencies = []
for folder, stem in (("city_shop_fittings_01", "city_shop_fittings_01"),
                     ("city_shop_fittings_02", "city_shop_fittings_02"),
                     ("city_shop_fittings_03", "city_shop_fittings_03_single"),
                     ("city_shop_fittings_05", "city_shop_fittings_05"),
                     ("city_shop_fittings_06", "city_shop_fittings_06_single")):
    dependencies.extend([
        describe(ROOT / f"art/models/environment/{folder}/{stem}.glb"),
        describe(ROOT / f"scenes/prefabs/environment/{stem}.tscn"),
    ])
report = {"asset_id": "city_small_shop_shells.03", "producer": "commissioned implementation worker",
          "self_exclusion": "manifest.json excludes itself to avoid recursive hashing",
          "files": files, "read_only_dependencies": dependencies}
if "--verify" in sys.argv:
    assert json.loads(MANIFEST.read_text()) == report, "Manifest payload or dependency mismatch"
    print(f"MANIFEST_PASS: {len(files)} produced files, {len(dependencies)} read-only dependencies")
else:
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(f"MANIFEST_WRITTEN: {len(files)} produced files")
