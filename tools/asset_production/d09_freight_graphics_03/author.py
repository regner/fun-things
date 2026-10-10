"""Original loading-location artwork on existing wall and low sign hardware; no external fonts."""
import argparse
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_03"
SPEC = importlib.util.spec_from_file_location(
    "freight_container_art", ROOT / "tools/asset_production/d09_freight_graphics_02/author.py"
)
FAMILY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FAMILY)
PALETTE = FAMILY.PALETTE
GLYPHS = {**FAMILY.GLYPHS,
    "O": FAMILY.GLYPHS["0"],
    "D": [[(0, 0), (2.5, 0), (4, 1.5), (4, 4.5), (2.5, 6), (0, 6), (0, 0)]],
}
SIZES = {"wall": (1220, 820), "low": (1440, 390)}


def create_artwork(variant: str) -> Image.Image:
    """Lay out location 04 at each carrier's native aspect, with generous quiet margins."""
    scale = 3
    size = SIZES[variant]
    image = Image.new("RGB", (size[0]*scale, size[1]*scale), PALETTE["field"])
    draw = ImageDraw.Draw(image)

    def stroke(points, color, width):
        """Draw original rounded industrial paths at supersampled resolution."""
        points = [(round(x*scale), round(y*scale)) for x, y in points]
        width = round(width*scale)
        draw.line(points, fill=PALETTE[color], width=width, joint="curve")
        for x, y in points:
            r = width / 2
            draw.ellipse((x-r, y-r, x+r, y+r), fill=PALETTE[color])

    def text(copy, x, y, height, color, width):
        """Typeset the sibling family's explicit outlines without a font dependency."""
        unit = height / 6
        for character in copy:
            if character == " ":
                x += 3*unit
                continue
            for path in GLYPHS[character]:
                stroke([(x+u*unit, y+v*unit) for u, v in path], color, width)
            x += 5.7*unit

    def parcel(x, y, size):
        """Retain the same parcel-clock proportions as the earlier freight graphics."""
        draw.rounded_rectangle(tuple(v*scale for v in (x, y, x+size, y+size)),
                               radius=round(size*.14*scale), fill=PALETTE["amber"])
        stroke([(x+size*.5, y), (x+size*.5, y+size*.21)], "field", size*.118)
        draw.ellipse(tuple(v*scale for v in (x+size*.21, y+size*.33,
                                            x+size*.79, y+size*.91)), fill=PALETTE["field"])
        stroke([(x+size*.5, y+size*.445), (x+size*.5, y+size*.62),
                (x+size*.635, y+size*.62)], "amber", size*.062)

    if variant == "wall":
        text("LOADING", 108, 100, 128, "amber", 19)
        parcel(95, 330, 300)
        text("04", 540, 315, 330, "ivory", 43)
        text("FREIGHT", 104, 706, 40, "steel", 8)
        for x in (1010, 1050, 1090):
            stroke([(x, 702), (x, 744)], "steel", 14)
    else:
        parcel(58, 60, 260)
        text("FREIGHT", 408, 61, 42, "amber", 8)
        text("LOAD 04", 408, 159, 154, "ivory", 22)
        for x in (1216, 1260, 1304):
            stroke([(x, 60), (x, 103)], "steel", 14)
    return image.resize(size, Image.Resampling.LANCZOS)


def main():
    """Save both deterministic opaque PNGs to runtime paths or an explicit scratch folder."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / f"art/textures/environment/{NID}")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in SIZES:
        path = args.output_dir / f"loading_{variant}_albedo.png"
        create_artwork(variant).save(path, compress_level=9)
        print(f"LOADING_ARTWORK_PASS: {path}")


if __name__ == "__main__":
    main()
