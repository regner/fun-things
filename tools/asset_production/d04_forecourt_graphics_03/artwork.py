"""Original quiet Glassward inset emblem; reproducible Pillow artwork without external imagery."""
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_forecourt_graphics_03"
TEXTURE = ROOT / f"art/textures/environment/{NID}/quiet_inset_emblem_albedo.png"
SIZE = (512, 512)
spec = importlib.util.spec_from_file_location(
    "forecourt_palette", ROOT / "tools/asset_production/d04_forecourt_graphics_01/artwork.py")
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
PALE, SLATE, CYAN = family.PALE, family.SLATE, family.CYAN


def draw():
    """Inset two offset slate appointment corners and a small cyan marker in pale paving."""
    scale = 4
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), PALE)
    canvas = ImageDraw.Draw(image)
    # Squared paving inlays echo the corporate appointment emblem, without signage contrast.
    # Half-open bounds preserve .375m strokes and a generous unmarked perimeter at 64 px/m.
    for left, top, right, bottom in [
        (116, 116, 140, 332), (140, 116, 332, 140),
        (196, 196, 412, 220), (388, 220, 412, 412),
    ]:
        canvas.rectangle((left * scale, top * scale,
                          right * scale - 1, bottom * scale - 1), fill=SLATE)
    # One .75 x .1875m cyan appointment marker; no ring, arrow, copy or magenta.
    canvas.rectangle((280 * scale, 300 * scale, 328 * scale - 1, 312 * scale - 1), fill=CYAN)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write the sole runtime artwork reproducibly at maximum PNG compression."""
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    draw().save(TEXTURE, compress_level=9)
    print("EMBLEM_ARTWORK_WRITTEN", TEXTURE)


if __name__ == "__main__":
    main()
