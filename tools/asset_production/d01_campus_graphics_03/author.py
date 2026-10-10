"""Original left/ahead/right campus route faces on the existing low sign support."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_campus_graphics_03"
VARIANTS = ("left", "ahead", "right")
SIZE = (1440, 390)
FAMILY_SOURCE = ROOT / "tools/asset_production/d01_campus_graphics_02/author.py"
spec = importlib.util.spec_from_file_location("campus_low_panel", FAMILY_SOURCE)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
Canvas, PALETTE = family.Canvas, family.PALETTE
OUTPUT_DIR = ROOT / f"art/textures/environment/{NID}"


def create_artwork(variant):
    """Keep a large solid arrow primary and the linked campus identity secondary."""
    if variant not in VARIANTS:
        raise ValueError(variant)
    c = Canvas()
    # One broad arrow skeleton, rotated in image space only: lettering never mirrors.
    arrow = [(-132, -43), (12, -43), (12, -108), (142, 0),
             (12, 108), (12, 43), (-132, 43)]
    if variant == "left":
        arrow = [(-x, y) for x, y in arrow]
    elif variant == "ahead":
        arrow = [(y, -x) for x, y in arrow]
    c.polygon([(235+x, 195+y) for x, y in arrow], "mint")
    c.line([(430, 54), (430, 336)], "quiet", 5)
    c.text("CAMPUS ROUTE", 490, 73, 70, "ivory", tracking=1.15)
    c.text("NORTHPOINT", 492, 200, 38, "mint", tracking=1.4)
    c.text("INSTITUTE OF ALMOST KNOWING", 492, 303, 23, "amber", tracking=1.05)
    family.family.crest(c, 1240, 180, 126)
    return c.finish()


def main():
    """Write three independently placeable opaque PNGs or reproduce them into scratch."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        path = args.output_dir / f"route_{variant}_albedo.png"
        create_artwork(variant).save(path, compress_level=9)
        print(path)


if __name__ == "__main__":
    main()
