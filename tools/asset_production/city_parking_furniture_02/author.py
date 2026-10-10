"""Recompose Broadlot's original P / ZONE A design for the existing 48:13 low panel."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "city_parking_furniture_02"
OUTPUT = ROOT / f"art/textures/environment/{NID}/parking_zone_low_albedo.png"
SIZE = (1440, 390)
RECIPE = ROOT / "tools/asset_production/d07_retail_graphics_03/author.py"
spec = importlib.util.spec_from_file_location("broadlot_parking", RECIPE)
parking = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parking)
PALETTE = parking.family.PALETTE


def create_artwork() -> Image.Image:
    """Set the existing parking symbol and capitals horizontally, without raster distortion."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALETTE["petrol"])
    draw = ImageDraw.Draw(image)

    def stroke(points, width, color):
        """Use the sibling's rounded path treatment at three-times resolution."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(copy, x, y, height, color, weight):
        """Reuse the exact family capital paths and isotropic letter scaling."""
        unit = height / 7
        for letter in copy:
            paths = parking.ZONE_Z if letter == "Z" else parking.family.LETTERS[letter]
            for path in paths:
                stroke([(x + u * unit, y + v * unit) for u, v in path], unit * weight, color)
            x += unit * 5.9

    # The parking glyph is the existing original path at uniform 0.46 scale.
    path = [(160, 647), (160, 185), (336, 185), (414, 247), (414, 349),
            (336, 411), (160, 411)]
    stroke([(115 + (x-160)*.46, 88 + (y-185)*.46) for x, y in path], 66*.46, "coral")
    text("ZONE", 360, 107, 151, "ivory", .75)
    text("A", 968, 81, 222, "coral", .83)
    stroke([(1266, 193), (1320, 193)], 18, "lime")
    stroke([(360, 320), (1100, 320)], 5, "ivory")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write the deterministic owned albedo or a caller-selected scratch export."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
