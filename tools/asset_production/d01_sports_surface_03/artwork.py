"""Original non-regulation campus court; reproducible Pillow artwork without fonts."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
TEXTURE = ROOT / 'art/textures/environment/d01_sports_surface_03/small_court_albedo.png'
SIZE = (1792, 1024)
SUPERSAMPLE = 4
STROKE_M = .16
IVORY = '#F6F1DC'
FIELD_GREEN = '#326556'
APRON_GREEN = '#294E49'


def artwork():
    """Draw a quiet 24 x 12 m racket-court motif on a 28 x 16 m matte-green atlas."""
    scale = 64 * SUPERSAMPLE
    image = Image.new('RGB', (SIZE[0] * SUPERSAMPLE, SIZE[1] * SUPERSAMPLE), APRON_GREEN)
    draw = ImageDraw.Draw(image)
    width = round(STROKE_M * scale)

    def point(x, z):
        """Map Godot east/south metres to pixel coordinates."""
        return (round((x + 14) * scale), round((z + 8) * scale))

    def line(points):
        """Centre the broad painted lines on documented metre-space coordinates."""
        draw.line([point(*p) for p in points], fill=IVORY, width=width, joint='curve')

    draw.rectangle([point(-12, -6), point(12, 6)], fill=FIELD_GREEN)
    line([(-12, -6), (12, -6), (12, 6), (-12, 6), (-12, -6)])
    for z in (-4.5, 4.5):
        line([(-12, z), (12, z)])
    for x in (-6, 6):
        line([(x, -4.5), (x, 4.5)])
    line([(-6, 0), (6, 0)])
    # A painted transverse divider, not a net or a physical barrier.
    line([(0, -6), (0, 6)])
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    """Write the sole committed opaque sRGB atlas deterministically."""
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    artwork().save(TEXTURE, compress_level=9)
    print('COURT_ARTWORK_WRITTEN', TEXTURE)


if __name__ == '__main__':
    main()
