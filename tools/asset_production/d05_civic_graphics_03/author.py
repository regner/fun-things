"""Original quay directions on the shared low panel, in the delivered civic graphic grammar."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_03"
OUTPUT = ROOT / f"art/textures/environment/{NID}/direction_panel_albedo.png"
SIZE = (1440, 390)
SOURCE = ROOT / "tools/asset_production/d05_civic_graphics_02/author.py"
spec = importlib.util.spec_from_file_location("civic_lettering", SOURCE)
civic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(civic)
PALETTE = civic.PALETTE
LETTERS = dict(civic.LETTERS, **{
    "V": [[(0, 0), (2, 7), (4, 0)]],
    "W": [[(0, 0), (0.7, 7), (2, 4), (3.3, 7), (4, 0)]],
})


def create_artwork() -> Image.Image:
    """Compose three broad route fields; copy and arrow bearings remain placement proposals."""
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALETTE["slate"])
    draw = ImageDraw.Draw(image)

    def stroke(points, width, color):
        """Keep the siblings' continuous paths and softened terminals, not grid lettering."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(copy, x, y, height, color):
        """Draw original family capitals without a third-party font or raster dependency."""
        unit = height / 7
        for letter in copy:
            if letter == " ":
                x += unit * 3.8
                continue
            for path in LETTERS[letter]:
                stroke([(x + u * unit, y + v * unit) for u, v in path], unit * 0.82, color)
            x += unit * 6.1

    def arrow(points):
        """Use filled, broad direction silhouettes with no outlined micro-detail."""
        draw.polygon([(x * scale, y * scale) for x, y in points], fill=PALETTE["amber"])

    text("OLD QUAY", 62, 52, 30, "amber")
    text("ONWARD EVENTUALLY", 979, 55, 23, "amber")
    stroke([(60, 111), (1380, 111)], 4, "amber")
    for x in (470, 930):
        stroke([(x, 149), (x, 323)], 3, "amber")
    # The panel is a decorative directional proposal, never the route graph owner.
    arrow([(186, 200), (241, 151), (241, 183), (322, 183),
           (322, 217), (241, 217), (241, 249)])
    arrow([(700, 148), (749, 203), (717, 203), (717, 245),
           (683, 245), (683, 203), (651, 203)])
    arrow([(1224, 200), (1169, 151), (1169, 183), (1088, 183),
           (1088, 217), (1169, 217), (1169, 249)])
    text("QUAY", 166, 281, 57, "ivory")
    text("HALL", 607, 281, 57, "ivory")
    text("SIGNAL ROW", 983, 289, 43, "ivory")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write deterministic opaque albedo to the owned runtime path or an explicit scratch file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
