"""Original Old Quay civic notices, sharing the hall's palette and source-owned capitals."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_02"
OUTPUT = ROOT / f"art/textures/environment/{NID}/noticeboard_albedo.png"
SIZE = (1640, 1040)
SOURCE = ROOT / "tools/asset_production/d05_civic_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("hall_lettering", SOURCE)
hall = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hall)
PALETTE = hall.PALETTE
# Extend the original civic alphabet, without changing the earlier hall's recipe.
LETTERS = dict(hall.LETTERS, **{
    "B": [[(0, 7), (0, 0), (3, 0), (4, 1), (4, 2.5), (3, 3.5), (0, 3.5)],
          [(3, 3.5), (4, 4.5), (4, 6), (3, 7), (0, 7)]],
    "D": [[(0, 7), (0, 0), (2.5, 0), (4, 1.5), (4, 5.5), (2.5, 7), (0, 7)]],
    "G": [[(4, 1), (3, 0), (1, 0), (0, 1), (0, 6), (1, 7), (3, 7), (4, 6),
           (4, 3.5), (2.4, 3.5)]],
    "H": [[(0, 0), (0, 7)], [(4, 0), (4, 7)], [(0, 3.5), (4, 3.5)]],
    "L": [[(0, 0), (0, 7), (4, 7)]],
    "Q": [[(1, 0), (3, 0), (4, 1), (4, 5.5), (2.5, 7), (1, 7), (0, 6),
           (0, 1), (1, 0)], [(2.4, 5), (4.5, 7.5)]],
    "S": [[(4, 1), (3, 0), (1, 0), (0, 1), (0, 2.5), (1, 3.5), (3, 3.5),
           (4, 4.5), (4, 6), (3, 7), (1, 7), (0, 6)]],
    "U": [[(0, 0), (0, 6), (1, 7), (3, 7), (4, 6), (4, 0)]],
})


def create_artwork() -> Image.Image:
    """Lay out one large municipal notice and two secondary cards within the safe rectangle."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALETTE["slate"])
    draw = ImageDraw.Draw(image)

    def stroke(points, width, color):
        """Rasterize continuous vector strokes with the hall's softly rounded terminals."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(copy, x, y, height, color):
        """Set provisional fictional copy in the shared hand-authored civic alphabet."""
        unit = height / 7
        for letter in copy:
            if letter == " ":
                x += unit * 3.8
                continue
            for path in LETTERS[letter]:
                stroke([(x + u * unit, y + v * unit) for u, v in path], unit * 0.82, color)
            x += unit * 6.1

    def card(bounds, color):
        """Use quiet flat paper fields, not simulated dirt, microprint or extra geometry."""
        draw.rounded_rectangle(tuple(round(v * scale) for v in bounds), radius=8 * scale,
                               fill=PALETTE[color])

    # The municipal pediment and harbour line echo the hall without a second emblem asset.
    stroke([(86, 128), (145, 88), (204, 128), (86, 128)], 10, "amber")
    for x in (100, 145, 190):
        stroke([(x, 149), (x, 202)], 12, "ivory")
    stroke([(84, 219), (206, 219)], 10, "ivory")
    stroke([(93, 246), (126, 246), (146, 254), (166, 246), (197, 246)], 7, "amber")
    text("OLD QUAY", 268, 83, 42, "amber")
    text("PUBLIC NOTICES", 268, 166, 77, "ivory")
    stroke([(80, 289), (1560, 289)], 5, "amber")

    card((80, 335, 963, 916), "ivory")
    card((1004, 335, 1560, 602), "amber")
    stroke([(1004, 642), (1560, 642), (1560, 916), (1004, 916), (1004, 642)], 5, "amber")
    text("TEMPORARY", 145, 395, 77, "slate")
    text("NOTICE", 145, 507, 104, "slate")
    stroke([(144, 657), (892, 657)], 4, "amber")
    # A single hourglass is the large secondary read; no actual schedule or quest is implied.
    stroke([(165, 701), (250, 701)], 8, "slate")
    stroke([(171, 713), (241, 805), (171, 805), (241, 713)], 6, "slate")
    stroke([(165, 817), (250, 817)], 8, "slate")
    text("UNTIL FURTHER", 301, 725, 37, "slate")
    text("NOTICE", 301, 793, 44, "slate")
    text("QUAY MEETING", 1048, 378, 42, "slate")
    stroke([(1048, 462), (1514, 462)], 4, "slate")
    text("AGENDA TO COME", 1048, 512, 30, "slate")
    text("LOST TIME", 1048, 690, 48, "ivory")
    stroke([(1048, 779), (1514, 779)], 4, "amber")
    text("PLEASE ENQUIRE", 1048, 834, 31, "amber")
    text("OFFICE OF TEMPORARY PERMANENCE", 80, 967, 25, "amber")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write deterministic opaque sRGB albedo to the owned path or explicit scratch output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
