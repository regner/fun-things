"""Original, seamless plain-plaza paving; no downloaded imagery or noise textures."""
import argparse
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "city_ground_finishes_01"
OUTPUT = ROOT / f"art/textures/environment/{NID}/plain_plaza_paving_albedo.png"
SIZE = 512
TILE_METRES = 4.0


def create_texture():
    """Draw four broad 2 m slabs with soft, low-contrast 16 mm joints in a 4 m tile."""
    image = Image.new("RGB", (SIZE, SIZE))
    pixels = []
    for y in range(SIZE):
        v = (y + 0.5) / SIZE
        for x in range(SIZE):
            u = (x + 0.5) / SIZE
            # Periodic broad tone only: no grit, cracks, flecks, or normal-map sparkle.
            broad = 1.2 * math.cos(math.tau * u) * math.cos(math.tau * v)
            slab = 1.5 * math.sin(math.tau * u) * math.sin(math.tau * v)
            distance = min(u % 0.5, 0.5 - u % 0.5, v % 0.5, 0.5 - v % 0.5)
            joint = 1.0 - min(1.0, max(0.0, (distance * TILE_METRES - 0.008) / 0.008))
            shift = (broad + slab) * (1.0 - joint) - joint * 8.0
            pixels.append(tuple(round(channel + shift) for channel in (133, 146, 157)))
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
