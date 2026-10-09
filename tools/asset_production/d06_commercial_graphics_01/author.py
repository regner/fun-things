"""Author original hall artwork with drawn letterforms, no external fonts or images."""
from pathlib import Path
import argparse
import math

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_01"
OUTPUT = ROOT / f"art/textures/environment/{NID}/hall_title_albedo.png"
SIZE = (2000, 400)
PALETTE = {
    "petrol": "#102C3C", "magenta": "#F54BBA", "cyan": "#45DFE5", "ivory": "#F6F1DC"
}
# Original monoline capital skeletons on a continuous 4-by-6 design grid.
# Curved letters are sampled paths, not pixel-grid glyphs or a third-party font.
GLYPHS = {
    "A": [[(0, 6), (0, 2), (1, 0), (3, 0), (4, 2), (4, 6)], [(0, 3.5), (4, 3.5)]],
    "F": [[(0, 6), (0, 0), (4, 0)], [(0, 3), (3.2, 3)]],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    "E": [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3.2, 3)]],
    "R": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)],
          [(2, 3), (4, 6)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "U": [[(0, 0), (0, 5), (1, 6), (3, 6), (4, 5), (4, 0)]],
    "S": [[(4, 0), (1, 0), (0, 1), (0, 2), (1, 3), (3, 3), (4, 4),
           (4, 5), (3, 6), (0, 6)]],
    "L": [[(0, 0), (0, 6), (4, 6)]],
    "P": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)]],
    "N": [[(0, 6), (0, 0), (4, 6), (4, 0)]],
    "D": [[(0, 6), (0, 0), (2, 0), (4, 1.5), (4, 4.5), (2, 6), (0, 6)]],
    "C": [[(4, 0), (1, 0), (0, 1), (0, 5), (1, 6), (4, 6)]],
    "I": [[(2, 0), (2, 6)]],
    "Y": [[(0, 0), (2, 3), (4, 0)], [(2, 3), (2, 6)]],
    ".": [[(2, 6), (2, 6.01)]],
}
GLYPHS["O"] = [[(2 + 2 * math.cos(t * math.tau / 64),
                 3 + 3 * math.sin(t * math.tau / 64)) for t in range(65)]]


def create_artwork() -> Image.Image:
    """Draw the final 5:1 face at 3x resolution, then filter once for smooth edges."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALETTE["petrol"])
    draw = ImageDraw.Draw(image)

    def line(points, color, width):
        """Draw a continuous rounded stroke in final-pixel coordinates."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(copy, x, y, height, color, tracking=1.5, stroke=0.65):
        """Place the explicitly defined original letter paths at a uniform cap height."""
        unit = height / 6
        for letter in copy:
            if letter == " ":
                x += unit * 3.4
                continue
            for path in GLYPHS[letter]:
                line([(x + u * unit, y + v * unit) for u, v in path], color, unit * stroke)
            x += unit * (4 + tracking)

    # A split orbit with two large gaps remains recognisable without title text.
    for start, stop, color in [(25, 155, "cyan"), (205, 335, "magenta")]:
        points = [(216 + 127 * math.cos(math.radians(t)),
                   200 + 127 * math.sin(math.radians(t))) for t in range(start, stop + 1)]
        line(points, color, 52)
    line([(205, 202), (243, 162)], "ivory", 23)
    line([(205, 202), (180, 189)], "ivory", 23)
    # Quiet field around the large title avoids a dense all-neon rectangle.
    text("AFTER HOURS", 444, 79, 138, "ivory", tracking=1.65, stroke=0.72)
    line([(440, 266), (1850, 266)], "cyan", 5)
    text("HALL", 444, 304, 43, "magenta", tracking=2.0, stroke=0.85)
    text("OPEN LATE. DECISIONS EARLY.", 768, 308, 31, "ivory", tracking=1.45)
    # The two short bars balance the emblem, staying inside the 2.94 x .54 safe area.
    line([(1902, 87), (1902, 183)], "magenta", 22)
    line([(1902, 215), (1902, 311)], "cyan", 22)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write one opaque, deterministic PNG to the runtime path or scratch output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, optimize=False, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
