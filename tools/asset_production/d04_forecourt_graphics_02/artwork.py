"""Original Glassward entry-axis motif; deterministic Pillow source without external imagery."""
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_forecourt_graphics_02"
TEXTURE = ROOT / f"art/textures/environment/{NID}/entry_axis_motif_albedo.png"
SIZE = (512, 1024)
# One spelling of the family palette; the earlier band remains read-only.
spec = importlib.util.spec_from_file_location(
    "forecourt_palette", ROOT / "tools/asset_production/d04_forecourt_graphics_01/artwork.py")
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
PALE, SLATE, CYAN = family.PALE, family.SLATE, family.CYAN


def draw():
    """Paint two open-ended axis brackets and one small north-end cyan inset at 64 px/m."""
    scale = 4
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALE)
    canvas = ImageDraw.Draw(image)
    # Half-open pixel bounds give 0.5m wide, 12m long slate strokes and broad blank margins.
    for left, top, right, bottom in [
        (96, 128, 128, 896), (384, 128, 416, 896),
        (128, 128, 208, 160), (304, 128, 384, 160),
    ]:
        canvas.rectangle((left * scale, top * scale,
                          right * scale - 1, bottom * scale - 1), fill=SLATE)
    # A single 1.5 x .1875m dash terminates the axis, not a repeated route or arrow.
    canvas.rectangle((208 * scale, 218 * scale, 304 * scale - 1, 230 * scale - 1), fill=CYAN)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write the sole runtime artwork reproducibly at maximum PNG compression."""
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    draw().save(TEXTURE, compress_level=9)
    print("AXIS_ARTWORK_WRITTEN", TEXTURE)


if __name__ == "__main__":
    main()
