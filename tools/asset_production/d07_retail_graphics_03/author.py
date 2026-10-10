"""Original Broadlot parking-zone artwork, sharing the delivered family capital paths."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_graphics_03"
OUTPUT = ROOT / f"art/textures/environment/{NID}/parking_zone_albedo.png"
SIZE = (1220, 820)
FAMILY_RECIPE = ROOT / "tools/asset_production/d07_retail_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("broadlot_fascia", FAMILY_RECIPE)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
# Only the new zone-label Z is local; all existing letters retain their original owner.
ZONE_Z = [[(0, 0), (4, 0), (0, 7), (4, 7)]]


def create_artwork() -> Image.Image:
    """Compose a broad parking P, quiet zone identifier and one restrained lime ticket."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), family.PALETTE["petrol"])
    draw = ImageDraw.Draw(image)

    def stroke(points, width, color):
        """Rasterize original paths with smooth rounded joins at three-times resolution."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=family.PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=family.PALETTE[color])

    def text(copy, x, y, height, color, weight):
        """Set the shared condensed capitals without external font dependencies."""
        unit = height / 7
        for letter in copy:
            paths = ZONE_Z if letter == "Z" else family.LETTERS[letter]
            for path in paths:
                stroke([(x + u * unit, y + v * unit) for u, v in path], unit * weight, color)
            x += unit * 5.9

    # The generous open counter keeps P distinct from a filled tile at close range.
    stroke([(160, 647), (160, 185), (336, 185), (414, 247), (414, 349),
            (336, 411), (160, 411)], 66, "coral")
    text("ZONE", 594, 176, 125, "ivory", .75)
    text("A", 738, 408, 239, "coral", .83)
    # Echo the siblings' single lime ticket without suggesting a road-direction arrow.
    stroke([(1014, 370), (1052, 370)], 22, "lime")
    stroke([(594, 704), (1084, 704)], 5, "ivory")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write deterministic opaque RGB albedo to the owned output or a scratch path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
