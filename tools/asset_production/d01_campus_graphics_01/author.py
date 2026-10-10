"""Draw the original Northpoint campus-map face; no external fonts or images."""
import argparse
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_campus_graphics_01"
SIZE = (1640, 1040)
OUTPUT = ROOT / f"art/textures/environment/{NID}/campus_map_albedo.png"
# Reuse the project's original continuous letter skeletons, not a bundled system font.
LETTERS = ROOT / "tools/asset_production/d06_commercial_graphics_02/author.py"
spec = importlib.util.spec_from_file_location("project_sign_letters", LETTERS)
letters = importlib.util.module_from_spec(spec)
spec.loader.exec_module(letters)
GLYPHS = dict(letters.GLYPHS)
GLYPHS.update({
    "M": [[(0, 6), (0, 0), (2, 3), (4, 0), (4, 6)]],
    "K": [[(0, 0), (0, 6)], [(4, 0), (0, 3), (4, 6)]],
    "W": [[(0, 0), (0.6, 6), (2, 3.5), (3.4, 6), (4, 0)]],
    "V": [[(0, 0), (2, 6), (4, 0)]],
    "Q": letters.GLYPHS["O"] + [[(2.6, 4.6), (4.4, 6.6)]],
    "/": [[(0, 6), (4, 0)]],
})
PALETTE = {
    "slate": "#233F4A", "mint": "#A3DCC5", "ivory": "#F6F1DC",
    "amber": "#FFC05A", "coral": "#FF725D", "field": "#557B70",
    "quiet": "#385660",
}
BOUNDARY = ROOT / "docs/concepts/world-v1/stage-04-streets/district-editor/brackett-districts.json"


class Canvas:
    """Draw smooth sign graphics at triple resolution with one final downsample."""

    def __init__(self):
        """Start an opaque slate field with generous unprinted margins."""
        self.image = Image.new("RGB", (SIZE[0] * 3, SIZE[1] * 3), PALETTE["slate"])
        self.draw = ImageDraw.Draw(self.image)

    def polygon(self, points, color):
        """Fill a deliberately broad silhouette in final-pixel coordinates."""
        self.draw.polygon([(round(x * 3), round(y * 3)) for x, y in points],
                          fill=PALETTE[color])

    def ellipse(self, bounds, color):
        """Draw a continuous ellipse, independent of raster glyphs."""
        self.draw.ellipse(tuple(round(v * 3) for v in bounds), fill=PALETTE[color])

    def line(self, points, color, width):
        """Draw a rounded continuous stroke, including round end caps."""
        scaled = [(round(x * 3), round(y * 3)) for x, y in points]
        w = round(width * 3)
        self.draw.line(scaled, fill=PALETTE[color], width=w, joint="curve")
        r = w / 2
        for x, y in scaled:
            self.draw.ellipse((x-r, y-r, x+r, y+r), fill=PALETTE[color])

    def text(self, copy, x, y, height, color, tracking=1.5, stroke=0.72):
        """Draw the project-owned original letter paths at a uniform cap height."""
        unit = height / 6
        for letter in copy:
            if letter == " ":
                x += unit * 3.4
                continue
            for path in GLYPHS[letter]:
                self.line([(x + u * unit, y + v * unit) for u, v in path],
                          color, unit * stroke)
            x += unit * (4 + tracking)

    def badge(self, label, x, y):
        """Mark an illustrative destination with a large warm letter disc."""
        self.ellipse((x-25, y-25, x+25, y+25), "amber")
        self.text(label, x-8, y-12, 24, "slate", stroke=0.9)

    def finish(self):
        """Filter the authored paths once into the runtime RGB texture."""
        return self.image.resize(SIZE, Image.Resampling.LANCZOS)


def crest(canvas, x, y, size):
    """Draw Northpoint's original open-book/point crest, reusable by campus siblings."""
    def points(values):
        """Map the emblem's normalized coordinates into the chosen printed size."""
        return [(x + u * size, y + v * size) for u, v in values]
    canvas.polygon(points([(0, .30), (.43, .43), (.43, .95), (0, .82)]), "mint")
    canvas.polygon(points([(.57, .43), (1, .30), (1, .82), (.57, .95)]), "mint")
    canvas.polygon(points([(.50, 0), (.69, .29), (.50, .23), (.31, .29)]), "amber")


def create_artwork():
    """Compose a district-outline diagram, bold keyed destinations and provisional copy."""
    c = Canvas()
    c.text("NORTHPOINT", 70, 65, 90, "mint", tracking=1.4)
    c.text("INSTITUTE OF ALMOST KNOWING", 72, 193, 33, "ivory")
    crest(c, 1390, 63, 150)
    c.line([(65, 267), (1575, 267)], "mint", 6)
    c.text("CAMPUS MAP", 72, 300, 28, "amber")
    c.text("PLACES TO KNOW", 1060, 300, 28, "mint")

    # Preserve the owner's district boundary shape; internal glyphs are illustrative,
    # not a second road/placement dataset or a claim of navigable campus routes.
    points = next(d["points"] for d in json.loads(BOUNDARY.read_text())["districts"]
                  if d["id"] == 1)
    outline = [(265 + (x-55)*1.6, 355 + (y-45)*1.6) for x, y in points]
    c.polygon(outline, "quiet")
    c.line(outline + [outline[0]], "mint", 5)
    # North mark is orientation only, never a player-position marker.
    c.text("N", 870, 371, 30, "ivory")
    c.polygon([(880, 424), (862, 461), (880, 452), (898, 461)], "ivory")
    # Track in the inner northeast; hall southwest of it; lighthouse northwest.
    c.ellipse((529, 433, 685, 550), "mint")
    c.ellipse((545, 449, 669, 534), "field")
    c.line([(607, 452), (607, 531)], "mint", 3)
    c.line([(550, 493), (664, 493)], "mint", 3)
    c.line([(545, 561), (568, 579), (645, 579), (669, 561)], "ivory", 13)
    c.badge("B", 640, 607)
    # Open U-court reads as architecture rather than a generic filled rectangle.
    c.polygon([(395, 582), (425, 582), (425, 650), (487, 650), (487, 582),
               (517, 582), (517, 680), (395, 680)], "mint")
    c.polygon([(438, 650), (474, 650), (474, 692), (438, 692)], "ivory")
    c.badge("A", 363, 627)
    # Lighthouse stripe / beacon; a quiet detached landmark, not a new shoreline.
    c.polygon([(383, 474), (407, 474), (414, 530), (376, 530)], "ivory")
    c.polygon([(381, 493), (409, 493), (411, 507), (379, 507)], "coral")
    c.polygon([(375, 469), (395, 457), (415, 469)], "amber")
    c.badge("D", 349, 490)
    # Low teaching wings in the smaller southern plots.
    c.polygon([(380, 738), (420, 738), (420, 795), (380, 795)], "mint")
    c.polygon([(438, 741), (478, 741), (478, 763), (438, 763)], "ivory")
    c.badge("C", 335, 772)
    # Deliberately no 'you are here', scale bar, or invented road topology.
    c.line([(998, 359), (998, 899)], "quiet", 4)
    for label, title, subtitle, y in [
        ("A", "MAIN HALL", "ALMOST CERTAIN", 400),
        ("B", "SPORTS FIELD", "ROOM TO THINK", 539),
        ("C", "TEACHING WINGS", "FURTHER QUESTIONS", 678),
        ("D", "LIGHTHOUSE", "A BRIGHT IDEA", 817),
    ]:
        c.badge(label, 1080, y+15)
        c.text(title, 1132, y, 31, "ivory", tracking=1.2)
        c.text(subtitle, 1132, y+54, 20, "mint", tracking=1.1)
    c.line([(65, 949), (1575, 949)], "mint", 4)
    c.text("ILLUSTRATIVE / NOT TO SCALE", 72, 978, 22, "ivory")
    c.text("QUESTIONS WELCOME", 1185, 978, 22, "amber", tracking=1.2)
    return c.finish()


def main():
    """Save the deterministic opaque artwork, optionally into scratch for byte comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
