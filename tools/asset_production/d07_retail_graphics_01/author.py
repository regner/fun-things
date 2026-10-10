"""Original Broadlot fascia artwork: drawn paths only, no external font or image."""
from pathlib import Path
import argparse

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_graphics_01"
OUTPUT = ROOT / f"art/textures/environment/{NID}/retail_fascia_albedo.png"
SIZE = (2000, 400)
PALETTE = {"petrol": "#102C3C", "coral": "#FF725D", "lime": "#B8DC6F", "ivory": "#F6F1DC"}
# Original condensed rounded capitals, continuous coordinates rather than bitmap glyphs.
LETTERS = {
    "E": [[(4, 0), (0, 0), (0, 7), (4, 7)], [(0, 3.4), (3.4, 3.4)]],
    "V": [[(0, 0), (2, 7), (4, 0)]],
    "R": [[(0, 7), (0, 0), (2.8, 0), (4, 1), (4, 2.6), (2.8, 3.6), (0, 3.6)],
          [(2, 3.6), (4.2, 7)]],
    "Y": [[(0, 0), (2, 3.3), (4, 0)], [(2, 3.3), (2, 7)]],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 7)]],
    "H": [[(0, 0), (0, 7)], [(4, 0), (4, 7)], [(0, 3.4), (4, 3.4)]],
    "I": [[(2, 0), (2, 7)]],
    "N": [[(0, 7), (0, 0), (4, 7), (4, 0)]],
    "G": [[(4, 1), (3, 0), (1, 0), (0, 1.3), (0, 5.7), (1, 7), (4, 7),
           (4, 3.8), (2.4, 3.8)]],
    "O": [[(1, 0), (3, 0), (4, 1.3), (4, 5.7), (3, 7), (1, 7),
           (0, 5.7), (0, 1.3), (1, 0)]],
    "U": [[(0, 0), (0, 5.7), (1, 7), (3, 7), (4, 5.7), (4, 0)]],
    "A": [[(0, 7), (0, 2), (1.5, 0), (2.5, 0), (4, 2), (4, 7)],
          [(0, 4), (4, 4)]],
    "L": [[(0, 0), (0, 7), (4, 7)]],
    "D": [[(0, 7), (0, 0), (2.5, 0), (4, 1.7), (4, 5.3), (2.5, 7), (0, 7)]],
}


def create_artwork() -> Image.Image:
    """Draw the icon and two-level candidate copy with a generous quiet perimeter."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALETTE["petrol"])
    draw = ImageDraw.Draw(image)

    def stroke(points, width, color):
        """Draw smooth rounded original paths at supersampled resolution."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(copy, x, y, height, color, weight):
        """Set the custom capitals at one consistent cap height without font dependencies."""
        unit = height / 7
        for letter in copy:
            if letter == " ":
                x += unit * 3.2
                continue
            for path in LETTERS[letter]:
                stroke([(x + u * unit, y + v * unit) for u, v in path], unit * weight, color)
            x += unit * 5.9

    # An almost-closed shopping bag: the missing upper-right corner is the visual joke.
    stroke([(274, 152), (274, 303), (92, 303), (92, 139), (207, 139)], 27, "coral")
    stroke([(139, 139), (139, 110), (152, 86), (187, 86), (201, 110), (201, 139)],
           19, "coral")
    # One restrained lime ticket, not an arrow or parking/traffic instruction.
    stroke([(250, 91), (277, 91)], 18, "lime")
    text("EVERYTHING YOU", 392, 73, 58, "ivory", 0.75)
    text("NEARLY NEEDED", 392, 187, 112, "coral", 0.83)
    stroke([(392, 340), (1840, 340)], 4, "ivory")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write deterministic opaque RGB artwork to the owned runtime or a scratch path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
