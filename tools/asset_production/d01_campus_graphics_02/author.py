"""Draw the original Northpoint entry face using the committed campus family language."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_campus_graphics_02"
SIZE = (1440, 390)
OUTPUT = ROOT / f"art/textures/environment/{NID}/entry_panel_albedo.png"
FAMILY_SOURCE = ROOT / "tools/asset_production/d01_campus_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("campus_family", FAMILY_SOURCE)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
PALETTE = family.PALETTE


class Canvas(family.Canvas):
    """Use the existing campus vector paths on the low panel's exact 48:13 domain."""

    def __init__(self):
        """Start a fully opaque field at triple resolution for smooth continuous paths."""
        self.image = Image.new("RGB", (SIZE[0]*3, SIZE[1]*3), PALETTE["slate"])
        self.draw = ImageDraw.Draw(self.image)

    def finish(self):
        """Downsample once to the carrier's 1000-pixels-per-metre artwork domain."""
        return self.image.resize(SIZE, Image.Resampling.LANCZOS)


def create_artwork():
    """Set the institution first, with a broad crest and quiet district/entry labels."""
    c = Canvas()
    family.crest(c, 68, 62, 168)
    c.text("ENTRY", 93, 297, 27, "amber", tracking=1.4)
    c.line([(285, 53), (285, 337)], "quiet", 5)
    c.text("INSTITUTE OF", 340, 60, 55, "ivory", tracking=1.5)
    c.text("ALMOST KNOWING", 340, 157, 77, "mint", tracking=1.25, stroke=0.78)
    c.line([(338, 275), (1370, 275)], "quiet", 4)
    c.text("NORTHPOINT", 341, 310, 26, "mint", tracking=1.4)
    c.text("QUESTIONS WELCOME", 1000, 313, 23, "amber", tracking=1.1)
    return c.finish()


def main():
    """Write the deterministic runtime PNG or a scratch reproduction."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
