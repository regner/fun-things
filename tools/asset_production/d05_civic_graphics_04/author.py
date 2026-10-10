"""Three original warm Old Quay shop fascias, reusing the civic family's path alphabet."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_04"
OUTPUT = ROOT / f"art/textures/environment/{NID}"
SIZE = (2000, 400)
spec = importlib.util.spec_from_file_location(
    "civic_lettering", ROOT / "tools/asset_production/d05_civic_graphics_03/author.py")
civic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(civic)
LETTERS = civic.LETTERS
PALETTE = dict(civic.PALETTE, plum="#514452")
VARIANTS = {
    "tide_tea": ("TIDE TEA", "TEA AT YOUR OWN PACE", "slate"),
    "quay_pantry": ("QUAY PANTRY", "DAILY GOODS", "plum"),
    "hem_repairs": ("HEM REPAIRS", "A STITCH IN QUAY TIME", "slate"),
}


def create_artwork(variant: str) -> Image.Image:
    """Draw one broad shop identity with a unique trade emblem and a quiet secondary line."""
    title, aside, background = VARIANTS[variant]
    scale = 3
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALETTE[background])
    draw = ImageDraw.Draw(image)

    def stroke(points, width, color):
        """Rasterize continuous original paths with the family's softened terminals."""
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        width = round(width * scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(copy, x, y, height, color):
        """Set broad source-owned capitals without any external font or bitmap alphabet."""
        unit = height / 7
        for letter in copy:
            if letter == " ":
                x += unit * 3.8
                continue
            for path in LETTERS[letter]:
                stroke([(x + u * unit, y + v * unit) for u, v in path], unit * 0.82, color)
            x += unit * 6.1

    # Shared compositional rhythm, but each tenant has its own large trade silhouette.
    if variant == "tide_tea":
        stroke([(117, 167), (267, 167), (256, 255), (236, 277),
                (148, 277), (127, 255), (117, 167)], 13, "ivory")
        stroke([(266, 184), (304, 184), (314, 199), (304, 235), (260, 243)], 12, "ivory")
        stroke([(108, 301), (282, 301)], 12, "amber")
        stroke([(177, 137), (165, 119), (177, 96), (177, 77)], 9, "amber")
        stroke([(222, 137), (210, 119), (222, 96), (222, 77)], 9, "amber")
    elif variant == "quay_pantry":
        stroke([(139, 114), (267, 114), (267, 142), (139, 142), (139, 114)], 13, "amber")
        stroke([(146, 146), (126, 172), (126, 286), (141, 301),
                (264, 301), (279, 286), (279, 172), (260, 146)], 13, "ivory")
        stroke([(149, 210), (255, 210), (255, 260), (149, 260), (149, 210)], 9, "amber")
    else:
        stroke([(130, 112), (274, 112), (274, 137), (130, 137), (130, 112)], 12, "ivory")
        stroke([(148, 140), (148, 267), (258, 267), (258, 140)], 12, "amber")
        for y in (169, 205, 241):
            stroke([(159, y), (248, y-15)], 9, "amber")
        stroke([(130, 272), (274, 272), (274, 297), (130, 297), (130, 272)], 12, "ivory")
        stroke([(279, 239), (316, 273), (318, 308), (301, 326)], 8, "amber")
    stroke([(370, 78), (370, 323)], 4, "amber")
    text(title, 451, 94, 153 if variant == "tide_tea" else 145, "ivory")
    text(aside, 455, 295, 34, "amber")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write deterministic RGB albedos to owned runtime paths or an explicit scratch directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        path = args.output_dir / f"{variant}_albedo.png"
        create_artwork(variant).save(path, compress_level=9)
        print(path)


if __name__ == "__main__":
    main()
