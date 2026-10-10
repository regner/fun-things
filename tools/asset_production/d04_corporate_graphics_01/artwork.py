"""Original Glassward corporate panel: explicit vector lettering, no external fonts."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_corporate_graphics_01"
OUTPUT = ROOT / f"art/textures/environment/{NID}/tomorrow_albedo.png"
SIZE = (1608, 1128)
PALETTE = {"field": "#15263D", "cyan": "#57D9E5", "ivory": "#F6F1DC", "magenta": "#EB62B7"}
# Original continuous-outline capitals on a 4 x 6 drafting grid; not a bitmap font.
GLYPHS = {
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    "O": [[(1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0)]],
    "M": [[(0, 6), (0, 0), (2, 3), (4, 0), (4, 6)]],
    "R": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)], [(2, 3), (4, 6)]],
    "W": [[(0, 0), (0, 6), (2, 3), (4, 6), (4, 0)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "A": [[(0, 6), (0, 2), (2, 0), (4, 2), (4, 6)], [(0, 3.5), (4, 3.5)]],
    "S": [[(4, 0), (1, 0), (0, 1), (0, 2), (1, 3), (3, 3), (4, 4), (4, 5), (3, 6), (0, 6)]],
    "B": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)],
          [(3, 3), (4, 4), (4, 5), (3, 6), (0, 6)]],
    "E": [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]],
    "N": [[(0, 6), (0, 0), (4, 6), (4, 0)]],
    "C": [[(4, 0), (1, 0), (0, 1), (0, 5), (1, 6), (4, 6)]],
    "D": [[(0, 6), (0, 0), (2, 0), (4, 2), (4, 4), (2, 6), (0, 6)]],
    "U": [[(0, 0), (0, 5), (1, 6), (3, 6), (4, 5), (4, 0)]],
    "L": [[(0, 0), (0, 6), (4, 6)]],
}


def create_artwork():
    """Draw generous original typography and an offset appointment emblem at 3x."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALETTE["field"])
    draw = ImageDraw.Draw(image)

    def stroke(points, color, width):
        """Render antialiased continuous strokes with rounded joins and caps."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        r = width / 2
        for x, y in points:
            draw.ellipse((x-r, y-r, x+r, y+r), fill=PALETTE[color])

    def text(copy, x, y, height, color):
        """Place original letter skeletons with a deliberately spacious corporate rhythm."""
        unit = height / 6
        for letter in copy:
            if letter == " ":
                x += unit * 3.0
                continue
            for path in GLYPHS[letter]:
                stroke([(x+u*unit, y+v*unit) for u, v in path], color, unit * .58)
            x += unit * 5.6

    # Three broad open corners form a rescheduled calendar, not a real company logo.
    stroke([(135, 346), (135, 138), (347, 138)], "cyan", 32)
    stroke([(221, 218), (433, 218), (433, 428)], "cyan", 32)
    stroke([(296, 330), (366, 330)], "magenta", 32)
    stroke([(550, 288), (1448, 288)], "cyan", 5)
    text("TOMORROW", 136, 535, 148, "ivory")
    text("HAS BEEN", 139, 751, 56, "cyan")
    text("RESCHEDULED", 138, 900, 126, "ivory")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write the deterministic opaque albedo to the delivery or requested scratch path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
