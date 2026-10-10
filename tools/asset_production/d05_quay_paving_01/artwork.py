"""Original quiet double-harbour-line artwork, in metres; no external image/font input."""
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_paving_01"
TEXTURE = ROOT / f"art/textures/environment/{NID}/quay_border_albedo.png"
SIZE = (1280, 192)
WARM_GREY = (166, 167, 158)  # #A6A79E: quieter than the civic ivory lettering.
TEAL = (101, 126, 123)  # #657E7B: desaturated harbour accent, never neon.
PIXELS_PER_METRE = 160
SUPERSAMPLE = 4


def draw_artwork():
    """Draw two broad, parallel tidal lines in an 8 x 1.2 m repeatable border field."""
    scale = PIXELS_PER_METRE * SUPERSAMPLE
    image = Image.new("RGB", tuple(v * SUPERSAMPLE for v in SIZE), WARM_GREY)
    draw = ImageDraw.Draw(image)
    for centre_m in (.38, .82):
        points = []
        for sample in range(SIZE[0] * SUPERSAMPLE + 1):
            x_m = sample / scale
            y_m = centre_m + .08 * math.cos(math.tau * x_m / 4)
            points.append((sample, y_m * scale))
        draw.line(points, fill=TEAL, width=round(.10 * scale), joint="curve")
    image = image.resize(SIZE, Image.Resampling.LANCZOS)
    # Equal endpoint phase and zero tangent: ensure identical discrete seam samples too.
    image.paste(image.crop((0, 0, 1, SIZE[1])), (SIZE[0] - 1, 0))
    return image


def main():
    """Write the single original albedo; source parameters remain editable here."""
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    draw_artwork().save(TEXTURE, compress_level=9)
    print("QUAY_ARTWORK_WRITTEN", TEXTURE)


if __name__ == "__main__":
    main()
