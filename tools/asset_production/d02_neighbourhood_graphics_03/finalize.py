"""Shared finalize entrypoint for the corner-shop fascia artwork."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from family_tools import load_tool


def main():
    """Run the existing shared implementation against this asset's owned outputs."""
    return load_tool("finalize.py")["main"]()


if __name__ == "__main__":
    main()
