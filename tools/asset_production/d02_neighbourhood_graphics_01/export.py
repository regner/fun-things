"""Reexport unchanged shared panel to scratch; artwork creates no duplicate geometry."""
import importlib.util
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path("C:/tmp/ft/assets/d02_neighbourhood_graphics_01")
OWNER = ROOT / "tools/asset_production/city_sign_supports_01/export.py"
SOURCE = ROOT / "art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend"


def reexport():
    """Invoke the carrier owner's validated export contract without writing its owned paths."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    spec = importlib.util.spec_from_file_location("panel_export", OWNER)
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    output = SCRATCH / "reexport_city_sign_supports_01.glb"
    owner.perform(output, SCRATCH / "source_checks.json")
    committed = ROOT / "art/models/environment/city_sign_supports_01/city_sign_supports_01.glb"
    assert output.read_bytes() == committed.read_bytes(), "Shared carrier reexport differs"
    return output


if __name__ == "__main__":
    reexport()
