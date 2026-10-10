"""Original sparse civic corner inlay; the border sibling owns the shared paving palette."""
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_paving_02"
TEXTURE = ROOT / f"art/textures/environment/{NID}/civic_inset_albedo.png"
SIZE = (960, 960)
PIXELS_PER_METRE = 160
SUPERSAMPLE = 4
# Import palette only; never run or overwrite the sibling's artwork.
spec = importlib.util.spec_from_file_location(
    "quay_palette", ROOT / "tools/asset_production/d05_quay_paving_01/artwork.py")
palette = importlib.util.module_from_spec(spec)
spec.loader.exec_module(palette)


def draw_artwork():
    """Draw four rounded corner brackets, leaving two-metre openings on all four sides."""
    scale = PIXELS_PER_METRE * SUPERSAMPLE
    image = Image.new("RGB", tuple(v * SUPERSAMPLE for v in SIZE), palette.WARM_GREY)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(tuple(v * scale for v in (.5, .5, 5.5, 5.5)),
                           radius=.45 * scale, outline=palette.TEAL, width=round(.18 * scale))
    # Broad breaks prevent the inset from reading as an enclosed court or a route barrier.
    for box in [(2, 0, 4, 6), (0, 2, 6, 4)]:
        draw.rectangle(tuple(v * scale for v in box), fill=palette.WARM_GREY)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write the original square albedo; no font, external art or generated image input."""
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    draw_artwork().save(TEXTURE, compress_level=9)
    print("QUAY_ARTWORK_WRITTEN", TEXTURE)


if __name__ == "__main__":
    main()
