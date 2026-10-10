"""Shared preview entrypoint for the corner-shop fascia artwork."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from family_tools import load_tool


if __name__ == "__main__":
    load_tool("preview.py")
