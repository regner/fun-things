"""Re-export the reused blank carrier into scratch, using its owner's export contract."""
from pathlib import Path
import runpy
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
CARRIER = "city_sign_supports_03"
SCRATCH = Path("C:/tmp/ft/assets/d03_community_graphics_01/reexport")


def main():
    """Freshly open immutable source and delegate to its exact pinned collection exporter."""
    output = Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else SCRATCH
    # The artwork reuses hardware: never overwrite its production GLB or author a duplicate.
    assert ROOT.resolve() not in output.resolve().parents, "Use an external scratch directory"
    bpy.ops.wm.open_mainfile(filepath=str(
        ROOT / f"art/source/models/environment/{CARRIER}/{CARRIER}.blend"))
    sys.argv = ["export.py", "--", str(output)]
    runpy.run_path(str(ROOT / f"tools/asset_production/{CARRIER}/export.py"), run_name="__main__")


if __name__ == "__main__":
    main()
