"""Original Glassward broad paving band; deterministic Pillow source, no external imagery."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_forecourt_graphics_01"
TEXTURE = ROOT / f"art/textures/environment/{NID}/broad_paving_band_albedo.png"
SIZE = (1536, 256)
# Ground stays pale and neutral; cyan matches the corporate family exactly.
PALE = "#C5CBCA"
SLATE = "#85929D"
CYAN = "#57D9E5"


def draw():
    """Paint a 24 x 4 m strip at 64 px/m, without joints, arrows, text or an emblem."""
    scale = 4
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALE)
    canvas = ImageDraw.Draw(image)
    # Half-open rectangles preserve exact authored metre dimensions after supersampling.
    canvas.rectangle((0, 80 * scale, SIZE[0] * scale - 1, 176 * scale - 1), fill=SLATE)
    # One quiet 1.5 x .1875 m inset, 1.5 m from the east end; no continuous neon edge.
    canvas.rectangle((1344 * scale, 122 * scale, 1440 * scale - 1, 134 * scale - 1), fill=CYAN)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write the sole runtime artwork reproducibly at maximum PNG compression."""
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    draw().save(TEXTURE, compress_level=9)
    print("BAND_ARTWORK_WRITTEN", TEXTURE)


if __name__ == "__main__":
    main()
