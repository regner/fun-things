"""Original sign-island layout using the delivered Broadlot capital paths and palette."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_graphics_02"
OUTPUT = ROOT / f"art/textures/environment/{NID}/sign_island_face_albedo.png"
SIZE = (1920, 920)
# The earlier fascia owns the family letterforms; reuse rather than fork them.
FAMILY_RECIPE = ROOT / "tools/asset_production/d07_retail_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("broadlot_fascia", FAMILY_RECIPE)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)


def create_artwork() -> Image.Image:
    """Compose one quiet directory identity with the same nearly-closed shopping bag."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), family.PALETTE["petrol"])
    draw = ImageDraw.Draw(image)

    def stroke(points, width, color):
        """Rasterize rounded path joins at three-times final resolution."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=family.PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=family.PALETTE[color])

    def text(copy, x, y, height, color, weight):
        """Set the existing original capitals without any external font dependency."""
        unit = height / 7
        for letter in copy:
            if letter == " ":
                x += unit * 3.2
                continue
            for path in family.LETTERS[letter]:
                stroke([(x + u * unit, y + v * unit) for u, v in path], unit * weight, color)
            x += unit * 5.9

    # The bag, missing upper-right corner and single lime ticket echo the fascia.
    stroke([(508, 425), (508, 727), (144, 727), (144, 399), (374, 399)], 54, "coral")
    stroke([(238, 399), (238, 341), (264, 293), (334, 293), (362, 341), (362, 399)],
           38, "coral")
    stroke([(460, 303), (514, 303)], 36, "lime")
    text("EVERYTHING YOU", 690, 183, 84, "ivory", .75)
    text("NEARLY", 690, 363, 164, "coral", .83)
    text("NEEDED", 690, 592, 164, "coral", .83)
    stroke([(690, 823), (1710, 823)], 6, "ivory")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write deterministic RGB albedo to the owned output or a supplied scratch path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
