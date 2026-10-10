"""Original Glassward entry wordmark art; reuse family glyphs and the existing PIL canvas."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_corporate_graphics_03"
SIZE = (2000, 400)
OUTPUT = ROOT / f"art/textures/environment/{NID}/entry_wordmark_albedo.png"


def load_tool(name, relative):
    """Load an isolated tool module without editing its shared palette or source file."""
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


family = load_tool("glassward_letters", "tools/asset_production/d04_corporate_graphics_01/artwork.py")
canvas = load_tool("wordmark_canvas", "tools/asset_production/d06_commercial_graphics_02/author.py")
PALETTE = family.PALETTE
canvas.SIZE = SIZE
canvas.PALETTE = dict(PALETTE, petrol=PALETTE["field"])
canvas.GLYPHS = dict(family.GLYPHS)
COPY = "TOMORROW"


def create_artwork():
    """Give the fictional entry one word and the family's open appointment-corner emblem."""
    c = canvas.Canvas()
    c.line([(104, 256), (104, 104), (256, 104)], "cyan", 20)
    c.line([(165, 165), (317, 165), (317, 317)], "cyan", 20)
    c.line([(220, 246), (266, 246)], "magenta", 16)
    c.text(COPY, 472, 117, 166, "ivory", tracking=1.6, stroke=.58)
    return c.finish()


def main():
    """Write the deterministic RGB albedo, or reproduce it at an explicit scratch path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
