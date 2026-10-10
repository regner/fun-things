"""Reuse the existing notice export contract with parking-notice output paths."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from family_tools import load_tool


def reexport():
    """Reexport the unchanged accepted panel to this notice's scratch directory."""
    return load_tool("export.py")["reexport"]()


if __name__ == "__main__":
    reexport()
