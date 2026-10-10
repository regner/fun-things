"""Original Terrace Ward multi-notice artwork; rounded paths, no external fonts or images."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_community_graphics_01"
SIZE = (1640, 1040)
OUTPUT = ROOT / f"art/textures/environment/{NID}/community_board_albedo.png"
PALETTE = {"ivory": "#CECDB8", "paper": "#E6E1CC", "teal": "#587D7C",
           "ink": "#294B50", "coral": "#B98377", "pale": "#C5D0C3"}
# Original continuous monoline capitals, six-unit cap height. Coordinates are editable
# design source, not a downloaded/traced font or a raster grid rendered as square pixels.
GLYPHS = {
    "A": [[(0,6),(0,2),(1,0),(3,0),(4,2),(4,6)],[(0,3.5),(4,3.5)]],
    "C": [[(4,1),(3,0),(1,0),(0,1),(0,5),(1,6),(3,6),(4,5)]],
    "D": [[(0,0),(2,0),(4,2),(4,4),(2,6),(0,6),(0,0)]],
    "E": [[(4,0),(0,0),(0,6),(4,6)],[(0,3),(3,3)]],
    "H": [[(0,0),(0,6)],[(4,0),(4,6)],[(0,3),(4,3)]],
    "I": [[(0,0),(4,0)],[(2,0),(2,6)],[(0,6),(4,6)]],
    "K": [[(0,0),(0,6)],[(4,0),(0,3),(4,6)]],
    "L": [[(0,0),(0,6),(4,6)]],
    "M": [[(0,6),(0,0),(2,3),(4,0),(4,6)]],
    "N": [[(0,6),(0,0),(4,6),(4,0)]],
    "O": [[(1,0),(3,0),(4,1),(4,5),(3,6),(1,6),(0,5),(0,1),(1,0)]],
    "P": [[(0,6),(0,0),(3,0),(4,1),(4,2),(3,3),(0,3)]],
    "R": [[(0,6),(0,0),(3,0),(4,1),(4,2),(3,3),(0,3)],[(2,3),(4,6)]],
    "S": [[(4,1),(3,0),(1,0),(0,1),(0,2),(1,3),(3,3),(4,4),(4,5),(3,6),(1,6),(0,5)]],
    "T": [[(0,0),(4,0)],[(2,0),(2,6)]],
    "U": [[(0,0),(0,5),(1,6),(3,6),(4,5),(4,0)]],
    "V": [[(0,0),(0,2),(2,6),(4,2),(4,0)]],
    "W": [[(0,0),(0,6),(2,3),(4,6),(4,0)]],
    "Y": [[(0,0),(2,3),(4,0)],[(2,3),(2,6)]],
    ".": [[(2,6),(2,6)]],
}
COPY = ["SHARED SPACE.", "INDIVIDUAL OPINIONS.", "COURT CHAT", "ALL WELCOME",
        "LAUNDRY", "SHARE THE LINE.", "NOT THE SOCKS.", "TAKE A SEAT", "LEAVE ROOM."]


def create_artwork():
    """Compose a quiet civic header, one meeting card and two domestic courtesy notices."""
    scale = 3
    image = Image.new("RGB", (SIZE[0]*scale, SIZE[1]*scale), PALETTE["ivory"])
    draw = ImageDraw.Draw(image)

    def box(bounds, color, radius=0):
        """Draw flat printed paper fields, never extra carrier geometry."""
        draw.rounded_rectangle(tuple(round(v*scale) for v in bounds), radius=radius*scale,
                               fill=PALETTE[color])

    def stroke(points, color, width):
        """Keep smooth rounded monoline junctions and ends at final texture resolution."""
        points = [(round(x*scale), round(y*scale)) for x, y in points]
        width = round(width*scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        r = width/2
        for x, y in points:
            draw.ellipse((x-r,y-r,x+r,y+r), fill=PALETTE[color])

    def text(copy, x, y, height, color, width):
        """Place the original path capitals inside the inherited safe-copy rectangle."""
        unit = height/6
        for character in copy:
            if character == " ":
                x += 3*unit
                continue
            for path in GLYPHS[character]:
                stroke([(x+u*unit,y+v*unit) for u,v in path], color, width)
            x += 5.7*unit

    box((0,0,1640,320), "teal")
    # Two overlapping conversation bubbles, no commercial badge or directional arrow.
    box((85,78,260,185), "ivory", 27)
    draw.polygon([(v[0]*scale,v[1]*scale) for v in [(114,175),(114,216),(156,175)]],
                 fill=PALETTE["ivory"])
    box((182,155,315,242), "coral", 24)
    draw.polygon([(v[0]*scale,v[1]*scale) for v in [(281,229),(281,265),(247,229)]],
                 fill=PALETTE["coral"])
    text(COPY[0], 385, 91, 88, "paper", 12)
    text(COPY[1], 390, 232, 42, "paper", 6)
    # Generous flat gutters and three broad notices, rather than a dense paper collage.
    box((60,378,710,980), "paper", 16)
    box((60,378,710,414), "coral", 10)
    text(COPY[2], 108, 468, 64, "ink", 9)
    text(COPY[3], 108, 570, 46, "ink", 6)
    # Three neighbours over a shared underline: a large calm community icon.
    for x,y in [(243,744),(389,704),(534,744)]:
        box((x-31,y-31,x+31,y+31), "teal", 31)
        stroke([(x-48,y+104),(x-48,y+76),(x-30,y+56),(x+30,y+56),
                (x+48,y+76),(x+48,y+104)], "teal", 16)
    stroke([(271,910),(507,910)], "coral", 14)
    box((762,378,1580,716), "pale", 16)
    text(COPY[4], 807, 429, 62, "ink", 9)
    text(COPY[5], 807, 554, 40, "ink", 6)
    text(COPY[6], 807, 626, 40, "ink", 6)
    # A broad textile icon; no raised pegs, tiny notices or faux handwritten noise.
    stroke([(1372,437),(1524,437)], "ink", 8)
    box((1410,423,1488,515), "coral", 8)
    box((762,764,1580,980), "paper", 16)
    text(COPY[7], 807, 812, 49, "ink", 7)
    text(COPY[8], 807, 906, 35, "ink", 5)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write a deterministic opaque 41:26 PNG, or a scratch reproduction on request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print("COMMUNITY_ARTWORK_PASS:", args.output)


if __name__ == "__main__":
    main()
