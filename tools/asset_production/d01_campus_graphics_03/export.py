"""Delegate scratch-only reexport to the existing low-panel artwork export contract."""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
DEFAULT = Path("C:/tmp/ft/assets/d01_campus_graphics_03/reexport")
SPEC = importlib.util.spec_from_file_location(
    "campus_low_export", ROOT / "tools/asset_production/d01_campus_graphics_02/export.py")
shared = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shared)


def export_shared(output=DEFAULT):
    """Reopen the unchanged Blender carrier and export using its pinned owner contract."""
    return shared.export_shared(output)


if __name__ == "__main__":
    output = Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else DEFAULT
    export_shared(output)
