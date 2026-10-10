"""Original Glassward low directory art; reuse family glyphs and the existing PIL canvas."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_corporate_graphics_02"
SIZE = (1440, 390)
OUTPUT = ROOT / f"art/textures/environment/{NID}/directory_albedo.png"


def load_tool(name, relative):
    """Load an isolated tool module without editing its shared palette or source file."""
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


family = load_tool("glassward_letters", "tools/asset_production/d04_corporate_graphics_01/artwork.py")
canvas = load_tool("directory_canvas", "tools/asset_production/d06_commercial_graphics_02/author.py")
PALETTE = family.PALETTE
canvas.SIZE = SIZE
canvas.PALETTE = dict(PALETTE, petrol=PALETTE["field"])
# I/Y complete DIRECTORY, retaining the same continuous 4x6 capital construction.
canvas.GLYPHS = dict(family.GLYPHS, I=canvas.GLYPHS["I"], Y=canvas.GLYPHS["Y"])
COPY = ("DIRECTORY", "A", "TOMORROW", "B", "LATER")


def create_artwork():
    """Separate two fictional office entries with generous dark margins and no route arrows."""
    c = canvas.Canvas()
    # The exact two offset appointment corners echo the delivered facade identity.
    c.line([(86, 239), (86, 81), (244, 81)], "cyan", 16)
    c.line([(147, 142), (305, 142), (305, 300)], "cyan", 16)
    c.line([(205, 226), (246, 226)], "magenta", 14)
    c.text("DIRECTORY", 399, 65, 42, "cyan", tracking=1.6, stroke=.58)
    c.text("A", 399, 160, 66, "cyan", stroke=.58)
    c.text("TOMORROW", 513, 160, 66, "ivory", tracking=1.6, stroke=.58)
    c.line([(399, 252), (1334, 252)], "cyan", 2)
    c.text("B", 399, 282, 58, "cyan", stroke=.58)
    c.text("LATER", 513, 282, 58, "ivory", tracking=1.6, stroke=.58)
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
