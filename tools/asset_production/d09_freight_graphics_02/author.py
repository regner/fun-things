"""Original container IDs using the freight family's original capital paths and palette."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_02"
SIZE = (1400, 460)
VARIANTS = {"long": "UE 240", "short": "UE 481"}
SPEC = importlib.util.spec_from_file_location(
    "freight_family_art", ROOT / "tools/asset_production/d09_freight_graphics_01/author.py"
)
FAMILY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FAMILY)
PALETTE = FAMILY.PALETTE
# Extend, never alter, the sibling's original industrial-capital vocabulary.
GLYPHS = {**FAMILY.GLYPHS,
    "0": [[(1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0)]],
    "1": [[(0, 1), (2, 0), (2, 6)], [(0, 6), (4, 6)]],
    "2": [[(0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (0, 6), (4, 6)]],
    "4": [[(3, 6), (3, 0), (0, 4), (4, 4)]],
    "8": [[(1, 0), (3, 0), (4, 1), (4, 2), (3, 3), (1, 3), (0, 2), (0, 1), (1, 0)],
          [(1, 3), (0, 4), (0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3)]],
}


def create_artwork(variant: str) -> Image.Image:
    """Draw an upright, opaque 1.4 x 0.46 m face; IDs are fictional visual copy only."""
    scale = 3
    image = Image.new("RGB", (SIZE[0]*scale, SIZE[1]*scale), PALETTE["field"])
    draw = ImageDraw.Draw(image)

    def stroke(points, color, width):
        """Keep the family's rounded monoline construction and supersampling."""
        points = [(round(x*scale), round(y*scale)) for x, y in points]
        width = round(width*scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        for x, y in points:
            r = width / 2
            draw.ellipse((x-r, y-r, x+r, y+r), fill=PALETTE[color])

    def text(copy, x, y, height, color, width):
        """Place explicit original vector outlines, with no external font dependency."""
        unit = height / 6
        for character in copy:
            if character == " ":
                x += 3*unit
                continue
            for path in GLYPHS[character]:
                stroke([(x+u*unit, y+v*unit) for u, v in path], color, width)
            x += 5.7*unit

    # Parcel-clock: same family silhouette, centred within its own quiet left cluster.
    draw.rounded_rectangle(tuple(v*scale for v in (60, 70, 350, 360)),
                           radius=40*scale, fill=PALETTE["amber"])
    stroke([(205, 70), (205, 129)], "field", 34)
    draw.ellipse(tuple(v*scale for v in (121, 166, 289, 334)), fill=PALETTE["field"])
    stroke([(205, 199), (205, 250), (244, 250)], "amber", 18)
    text("FREIGHT", 450, 70, 54, "amber", 10)
    text(VARIANTS[variant], 450, 182, 176, "ivory", 23)
    # Compact steel cargo-bar group, not a barcode, road marking or encoded identity.
    for x in (1212, 1254, 1296):
        stroke([(x, 76), (x, 123)], "steel", 15)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Save both deterministic artwork variants to runtime or explicit scratch output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / f"art/textures/environment/{NID}")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        path = args.output_dir / f"container_id_{variant}_albedo.png"
        create_artwork(variant).save(path, compress_level=9)
        print(f"CONTAINER_ARTWORK_PASS: {path}")


if __name__ == "__main__":
    main()
