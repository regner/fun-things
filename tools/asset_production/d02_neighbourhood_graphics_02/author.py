"""Original parking-request artwork sharing the Crescents' quiet palette and path lettering."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_02"
OUTPUT = ROOT / f"art/textures/environment/{NID}/parking_request_albedo.png"
FAMILY = ROOT / "tools/asset_production/d02_neighbourhood_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("crescents_notice_art", FAMILY)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
SIZE, PALETTE = family.SIZE, family.PALETTE


def create_artwork():
    """Place one modest car inside one bay, with an overly attentive neighbour's request."""
    c = family.shared.Canvas()
    c.line([(55, 55), (1165, 55), (1165, 765), (55, 765), (55, 55)], "plum", 8)
    c.text("PLEASE USE", 475, 180, 57, "blue", tracking=1.35, stroke=0.63)
    c.text("ONE", 475, 290, 105, "plum", tracking=1.35, stroke=0.66)
    c.text("SPACE", 475, 422, 105, "plum", tracking=1.35, stroke=0.66)
    # Two quiet bay edges enclose a single compact car: request, not a prohibition symbol.
    c.line([(139, 179), (139, 485), (397, 485), (397, 179)], "blue", 12)
    c.polygon([(210, 208), (326, 208), (347, 253), (347, 422), (326, 449),
               (210, 449), (189, 422), (189, 253)], "plum")
    c.polygon([(213, 248), (323, 248), (331, 296), (205, 296)], "ivory")
    c.polygon([(205, 380), (331, 380), (320, 408), (216, 408)], "ivory")
    c.line([(181, 315), (191, 315)], "plum", 13)
    c.line([(345, 315), (355, 315)], "plum", 13)
    c.line([(130, 571), (1090, 571)], "blue", 5)
    c.text("WE ARE COUNTING", 156, 638, 68, "plum", tracking=1.45, stroke=0.68)
    return c.finish()


def main():
    """Write a reproducible RGB PNG without external fonts or raster sources."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
