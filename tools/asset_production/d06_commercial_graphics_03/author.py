"""Draw two seamless Signal Row poster wraps with original paths and family lettering."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_03"
SIZE = (2400, 1000)
VARIANTS = ("last_call", "small_prices")
OUTPUT = ROOT / f"art/textures/environment/{NID}"
spec = importlib.util.spec_from_file_location(
    "signal_row_canvas", ROOT / "tools/asset_production/d06_commercial_graphics_02/author.py")
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
# Reuse the existing smooth-path implementation, palette and original letter skeletons.
family.SIZE = (1200, 1000)
family.GLYPHS["M"] = [[(0, 6), (0, 0), (2, 3), (4, 0), (4, 6)]]
PALETTE = family.PALETTE


def centered_text(canvas, copy, y, height, color):
    """Centre the actual letter extents, leaving ample wraparound quiet space."""
    unit = height / 6
    advance = sum(3.4 if letter == " " else 5.5 for letter in copy[:-1]) + 4
    canvas.text(copy, (1200 - advance * unit) / 2, y, height, color)


def create_artwork(variant):
    """Repeat front/back identity with the rear UV seam crossing continuous artwork."""
    canvas = family.Canvas()
    if variant == "last_call":
        # One broad angular burst, deliberately unlike the hall ring or shop motifs.
        canvas.polygon([(200, 90), (620, 90), (525, 244), (940, 206),
                        (715, 398), (974, 530), (492, 560), (590, 395),
                        (219, 429), (390, 273)], "magenta")
        canvas.line([(483, 207), (684, 207)], "ivory", 32)
        canvas.line([(474, 595), (725, 595)], "cyan", 24)
        centered_text(canvas, "LAST CALL", 674, 99, "ivory")
        centered_text(canvas, "FIRST REGRET", 848, 64, "cyan")
    elif variant == "small_prices":
        # Two wide rectangular ticket silhouettes, with notches rather than tag points.
        for left, top, right, bottom in [(232, 105, 1025, 302), (175, 348, 968, 566)]:
            canvas.polygon([(left, top), (right, top), (right, bottom), (left, bottom)], "cyan")
            for x in (left, right):
                middle = (top + bottom) / 2
                canvas.ellipse((x-38, middle-38, x+38, middle+38), "petrol")
        canvas.line([(402, 201), (781, 201)], "petrol", 38)
        canvas.line([(357, 454), (620, 454)], "petrol", 38)
        canvas.line([(475, 610), (725, 610)], "magenta", 24)
        centered_text(canvas, "SMALL PRICES", 686, 77, "ivory")
        centered_text(canvas, "BIG STORIES", 850, 66, "magenta")
    else:
        raise ValueError(f"Unknown wrap: {variant}")
    tile = canvas.finish()
    image = Image.new("RGB", SIZE)
    image.paste(tile, (0, 0))
    image.paste(tile, (1200, 0))
    # Panel centres now land at U=0/1 (rear seam) and U=.5 (front), not on the flanks.
    return ImageChops.offset(image, 600, 0)


def main():
    """Write both reproducible opaque albedo textures or reproduce them in scratch."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        path = args.output_dir / f"{variant}_albedo.png"
        create_artwork(variant).save(path, optimize=False, compress_level=9)
        print(path)


if __name__ == "__main__":
    main()
