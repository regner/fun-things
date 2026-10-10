"""Original Old Quay civic fascia: reproducible paths, no font or image dependencies."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_01"
OUTPUT = ROOT / f"art/textures/environment/{NID}/hall_fascia_albedo.png"
SIZE = (2000, 400)
PALETTE = {"slate": "#344953", "ivory": "#F6F1DC", "amber": "#E9B96E"}
# Original broad civic capitals. The softened octagonal bowls avoid a pixel-grid style.
LETTERS = {
    "A": [[(0, 7), (0, 2), (1.4, 0), (2.6, 0), (4, 2), (4, 7)],
          [(0, 4), (4, 4)]],
    "C": [[(4, 1), (3, 0), (1, 0), (0, 1), (0, 6), (1, 7), (3, 7), (4, 6)]],
    "E": [[(4, 0), (0, 0), (0, 7), (4, 7)], [(0, 3.5), (3.4, 3.5)]],
    "F": [[(0, 7), (0, 0), (4, 0)], [(0, 3.5), (3.4, 3.5)]],
    "I": [[(0.6, 0), (3.4, 0)], [(2, 0), (2, 7)], [(0.6, 7), (3.4, 7)]],
    "M": [[(0, 7), (0, 0), (2, 3.2), (4, 0), (4, 7)]],
    "N": [[(0, 7), (0, 0), (4, 7), (4, 0)]],
    "O": [[(1, 0), (3, 0), (4, 1), (4, 6), (3, 7), (1, 7), (0, 6),
           (0, 1), (1, 0)]],
    "P": [[(0, 7), (0, 0), (3, 0), (4, 1), (4, 2.5), (3, 3.5), (0, 3.5)]],
    "R": [[(0, 7), (0, 0), (3, 0), (4, 1), (4, 2.5), (3, 3.5), (0, 3.5)],
          [(2, 3.5), (4, 7)]],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 7)]],
    "Y": [[(0, 0), (2, 3.4), (4, 0)], [(2, 3.4), (2, 7)]],
}


def create_artwork() -> Image.Image:
    """Draw an original civic seal and the brief's candidate bureaucratic title."""
    supersample = 3
    image = Image.new("RGB", (SIZE[0] * supersample, SIZE[1] * supersample), PALETTE["slate"])
    draw = ImageDraw.Draw(image)

    def stroke(points, width, color):
        """Rasterize continuous civic lettering paths with softly rounded joins."""
        points = [(round(x * supersample), round(y * supersample)) for x, y in points]
        width = round(width * supersample)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(copy, x, y, height, color):
        """Set the commissioned copy in source-owned vector capitals, without a font file."""
        unit = height / 7
        for letter in copy:
            if letter == " ":
                x += unit * 3.8
                continue
            for path in LETTERS[letter]:
                stroke([(x + u * unit, y + v * unit) for u, v in path], unit * 0.82, color)
            x += unit * 6.1

    # Municipal seal: a broad hall pediment and three piers over two calm harbour lines.
    stroke([(174, 63), (240, 63), (312, 135), (312, 265), (240, 337),
            (174, 337), (102, 265), (102, 135), (174, 63)], 10, "amber")
    stroke([(148, 154), (207, 115), (266, 154), (148, 154)], 11, "ivory")
    for x in (160, 207, 254):
        stroke([(x, 177), (x, 231)], 14, "ivory")
    stroke([(145, 245), (269, 245)], 12, "ivory")
    stroke([(158, 278), (188, 278), (208, 287), (228, 278), (256, 278)], 8, "amber")
    stroke([(179, 306), (207, 312), (236, 306)], 7, "amber")
    text("OFFICE OF", 420, 78, 54, "amber")
    text("TEMPORARY PERMANENCE", 420, 194, 84, "ivory")
    stroke([(420, 333), (1868, 333)], 5, "amber")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write deterministic RGB albedo to the owned runtime path or an explicit scratch path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
