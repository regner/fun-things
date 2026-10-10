"""Reexport unchanged shared low panel into scratch, never duplicate carrier geometry."""
from pathlib import Path
import runpy
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend"
DEFAULT = Path("C:/tmp/ft/assets/d01_campus_graphics_02/reexport")


def export_shared(output=DEFAULT):
    """Use the carrier owner's pinned export contract after reopening its saved source."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    argv = sys.argv[:]
    try:
        sys.argv = ["export.py", "--", str(output)]
        runpy.run_path(str(ROOT / "tools/asset_production/city_sign_supports_02/export.py"),
                      run_name="__main__")
    finally:
        sys.argv = argv
    return output / "city_sign_supports_02.glb"


if __name__ == "__main__":
    output = Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else DEFAULT
    export_shared(output)
