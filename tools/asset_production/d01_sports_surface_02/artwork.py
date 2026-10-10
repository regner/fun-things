"""Original quiet field graphics: reproducible Pillow strokes, no fonts or borrowed artwork."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
TEXTURE = ROOT / 'art/textures/environment/d01_sports_surface_02/field_lines_albedo.png'
SIZE = (2048, 1024)
SUPERSAMPLE = 4
STROKE_M = .18


def artwork():
    """Draw a 50 x 24 m non-regulation field in a transparent 52 x 26 m UV atlas."""
    scale = SIZE[0] * SUPERSAMPLE / 52
    alpha = Image.new('L', (SIZE[0] * SUPERSAMPLE, SIZE[1] * SUPERSAMPLE), 0)
    draw = ImageDraw.Draw(alpha)
    width = round(STROKE_M * scale)

    def point(x, z):
        """Map Godot east/south metres to atlas pixel coordinates."""
        return (round((x + 26) * scale), round((z + 13) * scale))

    def line(points):
        """Keep strokes centred on their documented metre-space paths."""
        draw.line([point(*p) for p in points], fill=255, width=width, joint='curve')

    line([(-25, -12), (25, -12), (25, 12), (-25, 12), (-25, -12)])
    line([(0, -12), (0, 12)])
    for sign in (-1, 1):
        line([(sign * 25, -6), (sign * 19, -6), (sign * 19, 6), (sign * 25, 6)])
        line([(sign * 25, -3), (sign * 23, -3), (sign * 23, 3), (sign * 25, 3)])
    # Pillow ellipse outlines run inside their box: expand half a stroke to centre the ring.
    radius = 3.5 + STROKE_M / 2
    draw.ellipse([point(-radius, -radius), point(radius, radius)], outline=255, width=width)
    draw.ellipse([point(-.15, -.15), point(.15, .15)], fill=255)
    alpha = alpha.resize(SIZE, Image.Resampling.LANCZOS)
    result = Image.new('RGBA', SIZE, (246, 241, 220, 0))
    result.putalpha(alpha)
    return result


def main():
    """Write the sole committed sRGB/straight-alpha image deterministically."""
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    artwork().save(TEXTURE, compress_level=9)
    print('FIELD_ARTWORK_WRITTEN', TEXTURE)


if __name__ == '__main__':
    main()
