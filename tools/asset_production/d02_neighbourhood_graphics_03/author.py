"""Original corner-shop fascia art in the Crescents' quiet domestic graphic family."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_03"
OUTPUT = ROOT / f"art/textures/environment/{NID}/corner_cupboard_albedo.png"
FAMILY = ROOT / "tools/asset_production/d02_neighbourhood_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("crescents_graphics", FAMILY)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
SIZE = (2000, 400)
PALETTE = family.PALETTE
family.shared.SIZE = SIZE
family.shared.GLYPHS["K"] = [[(0, 0), (0, 6)], [(4, 0), (0, 3), (4, 6)]]


def create_artwork():
    """Draw groceries and neighbourly copy, leaving a quiet ivory safe-crop margin."""
    c = family.shared.Canvas()
    c.line([(32, 32), (1968, 32), (1968, 368), (32, 368), (32, 32)], "plum", 4)
    # One shopping bag with broad bottle and loaf shapes, not an official or real brand mark.
    c.polygon([(143, 162), (143, 111), (152, 111), (152, 84), (181, 84),
               (181, 111), (193, 111), (193, 162)], "blue")
    c.ellipse((224, 86, 297, 223), "plum")
    c.line([(238, 111), (258, 127)], "ivory", 7)
    c.line([(242, 141), (266, 160)], "ivory", 7)
    c.polygon([(111, 168), (319, 168), (300, 311), (130, 311)], "plum")
    c.line([(175, 184), (175, 157), (188, 140), (224, 140), (238, 157), (238, 184)],
           "ivory", 10)
    c.line([(150, 273), (280, 273)], "ivory", 8)
    c.text("CORNER CUPBOARD", 421, 85, 108, "plum", tracking=1.45, stroke=0.65)
    c.line([(417, 242), (1856, 242)], "blue", 4)
    c.text("MILK. BREAD. LOCAL OPINIONS.", 424, 285, 39, "blue", tracking=1.55, stroke=0.67)
    return c.finish()


def main():
    """Write a deterministic RGB PNG; the optional output path supports scratch comparisons."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
