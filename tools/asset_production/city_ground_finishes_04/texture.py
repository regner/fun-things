"""Original short-grass albedo: soft interlocking growth patches, never blade/grit noise."""
import argparse
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "city_ground_finishes_04"
OUTPUT = ROOT / f"art/textures/environment/{NID}/short_grass_albedo.png"
SIZE = 512
TILE_METRES = 4.0
# Suppress recognizable 4 m landmarks at gameplay height, not the seamless UV interface.
PATCH_CONTRAST = 0.18
BASE_SRGB = (81, 117, 91)
# Unequal metre-scale growth patches; their amplitude must not reveal the repeat grid.
# Centre U/V, spread U/V, tone. The palest patch is slightly warmer, not neon green.
GROWTH_PATCHES = (
    (0.18, 0.30, 0.27, 0.19, -4.0),
    (0.64, 0.71, 0.30, 0.24, 4.5),
    (0.83, 0.17, 0.16, 0.28, 2.0),
)


def create_texture():
    """Draw one periodic RGB tile from smooth broad forms with no stochastic detail."""
    image = Image.new("RGB", (SIZE, SIZE))
    pixels = []
    for y in range(SIZE):
        v = y / (SIZE - 1)
        for x in range(SIZE):
            u = x / (SIZE - 1)
            shift = 0.7 * math.cos(math.tau * (u - v))
            for cx, cy, sx, sy, tone in GROWTH_PATCHES:
                dx = math.sin(math.pi * (u - cx)) / (math.pi * sx)
                dy = math.sin(math.pi * (v - cy)) / (math.pi * sy)
                shift += tone * math.exp(-2.0 * (dx * dx + dy * dy))
            shift *= PATCH_CONTRAST
            pixels.append((round(BASE_SRGB[0] + shift),
                           round(BASE_SRGB[1] + shift),
                           round(BASE_SRGB[2] + shift * 0.65)))
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
