"""Draw three original Signal Row fascia graphics; no fonts or external images."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_02"
SIZE = (2000, 400)
VARIANTS = ("loose_change", "second_helping", "side_b")
OUTPUT = ROOT / f"art/textures/environment/{NID}"
# Keep the family's existing original letter skeletons and exact palette as one source.
FAMILY_SOURCE = ROOT / "tools/asset_production/d06_commercial_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("signal_row_letters", FAMILY_SOURCE)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
PALETTE = family.PALETTE
GLYPHS = dict(family.GLYPHS)
GLYPHS.update({
    "G": [[(4, 0), (1, 0), (0, 1), (0, 5), (1, 6), (4, 6), (4, 3), (2.3, 3)]],
    "B": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)],
          [(3, 3), (4, 4), (4, 5), (3, 6), (0, 6)]],
})


class Canvas:
    """Supersample smooth filled shapes and the family's rounded original strokes."""

    def __init__(self):
        """Start an opaque petrol face with a three-times working resolution."""
        self.scale = 3
        self.image = Image.new("RGB", (SIZE[0] * 3, SIZE[1] * 3), PALETTE["petrol"])
        self.draw = ImageDraw.Draw(self.image)

    def polygon(self, points, color):
        """Fill a broad graphic mass using final-pixel coordinates."""
        self.draw.polygon([(x * 3, y * 3) for x, y in points], fill=PALETTE[color])

    def ellipse(self, bounds, color):
        """Draw a continuous circular or elliptical shape, never a pixel glyph."""
        self.draw.ellipse(tuple(v * 3 for v in bounds), fill=PALETTE[color])

    def line(self, points, color, width):
        """Use the hall artwork's rounded-path treatment for shared lettering."""
        scaled = [(round(x * 3), round(y * 3)) for x, y in points]
        width = round(width * 3)
        self.draw.line(scaled, fill=PALETTE[color], width=width, joint="curve")
        radius = width / 2
        for x, y in scaled:
            self.draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=PALETTE[color])

    def text(self, copy, x, y, height, color, tracking=1.5, stroke=0.72):
        """Draw explicitly authored letter skeletons, without an external font."""
        unit = height / 6
        for letter in copy:
            if letter == " ":
                x += unit * 3.4
                continue
            for path in GLYPHS[letter]:
                self.line([(x + u * unit, y + v * unit) for u, v in path], color, unit * stroke)
            x += unit * (4 + tracking)

    def finish(self):
        """Filter the authored paths once into the runtime RGB texture."""
        return self.image.resize(SIZE, Image.Resampling.LANCZOS)


def create_artwork(variant):
    """Give each tenant a distinct colour mass, not a text-dependent identity."""
    canvas = Canvas()
    if variant == "loose_change":
        # Large asymmetric tag occupies the left half; a quiet right half carries copy.
        canvas.polygon([(45, 40), (665, 40), (860, 200), (665, 360), (45, 360)], "magenta")
        canvas.ellipse((654, 161, 732, 239), "petrol")
        canvas.line([(140, 135), (485, 135)], "ivory", 26)
        canvas.line([(140, 225), (390, 225)], "ivory", 26)
        canvas.text("LOOSE", 977, 76, 90, "ivory", tracking=1.65)
        canvas.text("CHANGE", 977, 226, 90, "ivory", tracking=1.65)
        canvas.line([(1776, 73), (1880, 73)], "cyan", 22)
        canvas.line([(1776, 99), (1828, 99)], "cyan", 22)
    elif variant == "second_helping":
        # Cyan flood field and a dark bowl invert the other two tenants' value structure.
        canvas.polygon([(24, 24), (1976, 24), (1976, 376), (24, 376)], "cyan")
        canvas.ellipse((93, 89, 789, 355), "petrol")
        canvas.polygon([(80, 40), (805, 40), (805, 203), (80, 203)], "cyan")
        canvas.line([(107, 204), (776, 204)], "petrol", 27)
        canvas.line([(294, 353), (584, 353)], "petrol", 20)
        for x in (267, 441, 615):
            canvas.line([(x, 151), (x-17, 124), (x+17, 95), (x, 68)], "petrol", 24)
        canvas.text("SECOND", 928, 73, 88, "petrol")
        canvas.text("HELPING", 928, 235, 88, "petrol")
    elif variant == "side_b":
        # One filled ivory disc plus a separated magenta right block; not the hall's ring.
        canvas.ellipse((80, 40, 400, 360), "ivory")
        canvas.ellipse((185, 145, 295, 255), "cyan")
        canvas.ellipse((222, 182, 258, 218), "petrol")
        canvas.polygon([(1040, 35), (1975, 35), (1975, 365), (1040, 365)], "magenta")
        canvas.text("SIDE B", 1150, 120, 146, "petrol", tracking=1.4)
        canvas.line([(522, 162), (822, 162)], "ivory", 26)
        canvas.line([(522, 239), (727, 239)], "ivory", 26)
    else:
        raise ValueError(f"Unknown tenant: {variant}")
    return canvas.finish()


def main():
    """Write all three deterministic runtime PNGs, or reproduce them in scratch."""
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
