"""Original quiet service concrete; broad curing washes, without grit or crack noise."""
import argparse
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "city_ground_finishes_02"
OUTPUT = ROOT / f"art/textures/environment/{NID}/service_concrete_albedo.png"
SIZE = 512
TILE_METRES = 4.0
BASE_SRGB = (139, 146, 144)
# Centre U/V, spread U/V and tone: two broad, low-contrast curing patches per repeat.
CURING_PATCHES = ((0.29, 0.35, 0.21, 0.28, -4.5), (0.73, 0.79, 0.29, 0.18, 3.0))


def create_texture():
    """Draw a seamless 4 m concrete field using only smooth metre-scale tonal forms."""
    image = Image.new("RGB", (SIZE, SIZE))
    pixels = []
    for y in range(SIZE):
        v = y / (SIZE - 1)
        for x in range(SIZE):
            u = x / (SIZE - 1)
            shift = 0.65 * math.cos(math.tau * (u + v))
            for cx, cy, sx, sy, tone in CURING_PATCHES:
                # Wrapped smooth distances have no hard seam or clipped patch boundary.
                dx = math.sin(math.pi * (u - cx)) / (math.pi * sx)
                dy = math.sin(math.pi * (v - cy)) / (math.pi * sy)
                shift += tone * math.exp(-2.0 * (dx * dx + dy * dy))
            pixels.append(tuple(round(channel + shift) for channel in BASE_SRGB))
    image.putdata(pixels)
    return image


def main():
    """Write the runtime PNG or a scratch copy for deterministic comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_texture().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
