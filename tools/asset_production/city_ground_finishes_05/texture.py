"""Original quiet garden soil: broad earthen washes without grit, cracks or mulch specks."""
import argparse
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "city_ground_finishes_05"
OUTPUT = ROOT / f"art/textures/environment/{NID}/quiet_garden_soil_albedo.png"
SIZE = 512
TILE_METRES = 4.0
# Suppress recognizable 4 m landmarks at gameplay height, not the seamless UV interface.
PATCH_CONTRAST = 0.18
BASE_SRGB = (105, 91, 78)
# Metre-scale soft loam variation, not damp hazards, raked rows or individual soil grains.
# Centre U/V, spread U/V, tone. Periodic distances preserve both repeat boundaries.
LOAM_PATCHES = (
    (0.28, 0.38, 0.32, 0.26, -4.0),
    (0.74, 0.66, 0.27, 0.34, 3.5),
    (0.66, 0.10, 0.22, 0.18, 1.5),
)


def create_texture():
    """Draw a seamless RGB tile using unequal, smooth low-contrast earthen patches."""
    image = Image.new("RGB", (SIZE, SIZE))
    pixels = []
    for y in range(SIZE):
        v = y / (SIZE - 1)
        for x in range(SIZE):
            u = x / (SIZE - 1)
            shift = 0.0
            for cx, cy, sx, sy, tone in LOAM_PATCHES:
                dx = math.sin(math.pi * (u - cx)) / (math.pi * sx)
                dy = math.sin(math.pi * (v - cy)) / (math.pi * sy)
                shift += tone * math.exp(-2.0 * (dx * dx + dy * dy))
            shift *= PATCH_CONTRAST
            pixels.append((round(BASE_SRGB[0] + shift),
                           round(BASE_SRGB[1] + shift),
                           round(BASE_SRGB[2] + shift * 0.8)))
    image.putdata(pixels)
    return image


def main():
    """Write the runtime PNG, or an explicit scratch copy for independent comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_texture().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
