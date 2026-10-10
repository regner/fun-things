"""Original oval lane artwork; deterministic PIL paths, no fonts or downloaded content."""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_sports_surface_01"
OUTPUT = ROOT / f"art/textures/environment/{NID}/oval_track_albedo.png"
SIZE = (4096, 2304)
TRACK = "#AB735F"
PAINT = "#F6F1DC"
# Original continuous-stroke numerals on a 0..1 design cell, not external font glyphs.
NUMERALS = {
    1: [[(.2, .75), (.5, 1), (.5, 0)], [(.15, 0), (.85, 0)]],
    2: [[(0, .8), (.2, 1), (.8, 1), (1, .8), (1, .65), (0, 0), (1, 0)]],
    3: [[(0, 1), (.8, 1), (1, .8), (.8, .5), (.3, .5)],
        [(.8, .5), (1, .25), (.8, 0), (0, 0)]],
    4: [[(.75, 0), (.75, 1), (0, .3), (1, .3)]],
    5: [[(1, 1), (0, 1), (0, .55), (.8, .55), (1, .35), (1, .2), (.8, 0), (0, 0)]],
    6: [[(1, 1), (.2, 1), (0, .8), (0, .2), (.2, 0), (.8, 0), (1, .2),
         (1, .4), (.8, .55), (0, .55)]],
}


def create_artwork():
    """Paint equal-scale plan UVs: U east; image rows south; 51.2 pixels per metre."""
    supersample = 2
    image = Image.new("RGB", (SIZE[0] * supersample, SIZE[1] * supersample), TRACK)
    draw = ImageDraw.Draw(image)
    density = SIZE[0] / 80 * supersample

    def stroke(points, width):
        """Rasterize metre-space paths with smooth, continuous joins."""
        pixels = [((x + 40) * density, (22.5 - y) * density) for x, y in points]
        draw.line(pixels, fill=PAINT, width=round(width * density), joint="curve")

    # Seven nested stadium outlines: six visually even lanes and narrow edge margins.
    for lane in range(7):
        radius = 16.02 + lane * 1.06
        points = []
        for centre, start in [(17.5, -90), (-17.5, 90)]:
            points.extend((centre + radius * math.cos(math.radians(start + step / 4)),
                           radius * math.sin(math.radians(start + step / 4)))
                          for step in range(721))
        stroke(points + [points[0]], .14)
    # A single quiet finish bar, not chequerboards, logos or regulation stagger marks.
    stroke([(9, -16.02), (9, -22.38)], .24)
    for lane in range(1, 7):
        centre_y = -(16.02 + (lane - .5) * 1.06)
        for path in NUMERALS[lane]:
            stroke([(6.9 + x * .48, centre_y + (y - .5) * .68) for x, y in path], .105)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write the runtime PNG, or a scratch reproduction for byte comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(f"ARTWORK_PASS {args.output}")


if __name__ == "__main__":
    main()
