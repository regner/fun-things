"""Original Urgent Eventually Freight fascia; Pillow paths, no external font or imagery."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_01"
OUTPUT = ROOT / f"art/textures/environment/{NID}/warehouse_fascia_albedo.png"
SIZE = (2000, 400)
PALETTE = {"field": "#143344", "amber": "#FFC05A", "ivory": "#F6F1DC", "steel": "#85929D"}
# Original rounded industrial capitals, on a continuous six-unit cap-height grid.
# Paths are design source, not a raster/pixel font or traced commercial typeface.
GLYPHS = {
    "A": [[(0, 6), (0, 2), (1, 0), (3, 0), (4, 2), (4, 6)], [(0, 3.5), (4, 3.5)]],
    "E": [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]],
    "F": [[(0, 6), (0, 0), (4, 0)], [(0, 3), (3, 3)]],
    "G": [[(4, 1), (3, 0), (1, 0), (0, 1), (0, 5), (1, 6), (4, 6), (4, 3), (2, 3)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "I": [[(0, 0), (4, 0)], [(2, 0), (2, 6)], [(0, 6), (4, 6)]],
    "L": [[(0, 0), (0, 6), (4, 6)]],
    "N": [[(0, 6), (0, 0), (4, 6), (4, 0)]],
    "R": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)], [(2, 3), (4, 6)]],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    "U": [[(0, 0), (0, 5), (1, 6), (3, 6), (4, 5), (4, 0)]],
    "V": [[(0, 0), (0, 2), (2, 6), (4, 2), (4, 0)]],
    "Y": [[(0, 0), (2, 3), (4, 0)], [(2, 3), (2, 6)]],
}


def create_artwork() -> Image.Image:
    """Draw one five-to-one fascia with a cargo-clock emblem and two tiers of copy."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALETTE["field"])
    draw = ImageDraw.Draw(image)

    def stroke(points, color, width):
        """Draw smooth monoline paths with rounded junctions and caps."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(copy, x, y, height, color, width):
        """Lay out only the explicit original capital outlines above."""
        unit = height / 6
        for character in copy:
            if character == " ":
                x += 3 * unit
                continue
            for path in GLYPHS[character]:
                stroke([(x + u*unit, y + v*unit) for u, v in path], color, width)
            x += 5.7 * unit

    # A broad amber parcel, interrupted tape and clock hand communicate cargo + delay.
    draw.rounded_rectangle(tuple(v*scale for v in (70, 65, 340, 335)),
                           radius=38*scale, fill=PALETTE["amber"])
    stroke([(205, 65), (205, 122)], "field", 32)
    draw.ellipse(tuple(v*scale for v in (126, 151, 282, 307)), fill=PALETTE["field"])
    stroke([(204, 184), (204, 230), (240, 230)], "amber", 16)
    # Keep large clean gutters between symbol, title and the secondary freight line.
    text("URGENT EVENTUALLY", 420, 75, 88, "ivory", 12)
    text("FREIGHT", 420, 233, 100, "amber", 16)
    # Three grouped steel cargo bars echo a container, not a road/loading marking.
    for x in (1230, 1300, 1370):
        stroke([(x, 245), (x, 324)], "steel", 24)
    stroke([(1470, 282), (1845, 282)], "steel", 14)
    stroke([(1811, 247), (1846, 282), (1811, 317)], "amber", 18)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Save deterministic opaque artwork to its runtime path or an explicit scratch path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(f"FREIGHT_ARTWORK_PASS: {args.output}")


if __name__ == "__main__":
    main()
