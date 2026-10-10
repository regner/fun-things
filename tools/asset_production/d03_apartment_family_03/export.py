"""Re-export existing dependencies to scratch; an assembly has no flattened GLB of its own."""
import json
from pathlib import Path
import runpy
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path("C:/tmp/ft/assets/d03_apartment_family_03")
assert bpy.app.version_string == "5.2.2 LTS"
models = json.loads((SCRATCH / "prefab-check.json").read_text())["models"]
for sibling in sorted({Path(item["path"]).parent.name for item in models}):
    source = ROOT / f"art/source/models/environment/{sibling}/{sibling}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    script = ROOT / f"tools/asset_production/{sibling}/export.py"
    sys.argv = [str(script), "--", str(SCRATCH / "reexport" / sibling)]
    runpy.run_path(str(script), run_name="__main__")
print("PASS: dependency collections exported to scratch using their original shared-contract exporters")
