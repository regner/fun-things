"""Read the saved assembly as the sole placement owner; never build a runtime scene."""
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_trolley_shelter_03"
PREFAB = ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}")
SOURCE = ROOT / "art/source/models/environment/d07_trolley_shelter_02/d07_trolley_shelter_02.blend"


def load_tool(name, path):
    """Import an existing family tool without executing its main or writing a cache."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def placements():
    """Read literal identity-basis placements from the normalized saved trolley instances."""
    text = PREFAB.read_text(encoding="utf-8")
    result = []
    for header, body in re.findall(r"(\[node [^\n]+\])\n([^\[]*)", text):
        if 'parent="Trolleys"' not in header:
            continue
        assert 'instance=ExtResource("1_trolley")' in header
        name = re.search(r'name="([^"]+)"', header).group(1)
        match = re.search(r"transform = Transform3D\(([^)]+)\)", body)
        values = [float(value) for value in match.group(1).split(",")] if match else [
            1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        assert values[:9] == [1, 0, 0, 0, 1, 0, 0, 0, 1], "Unexpected rotation/scale"
        result.append((name, values[9:]))
    assert [name for name, _ in result] == ["Front", "Middle", "Rear"]
    return result
