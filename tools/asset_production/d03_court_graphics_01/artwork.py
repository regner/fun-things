"""Draw the original Terrace Ward shared-circle paving artwork without fonts or external art."""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_court_graphics_01"
SIZE = 1024
SUPERSAMPLE = 4
SPAN_M = 14.0
COLORS = {
    "stone": "#9BA8A2", "teal": "#587D7C", "joint": "#889C97",
    "ivory": "#CECDB8", "panel": "#A7B0A5", "coral": "#B98377",
}


def draw_artwork(path):
    """Paint an opaque plan atlas; only the Blender annulus consumes its pixels."""
    size = SIZE * SUPERSAMPLE
    image = Image.new("RGB", (size, size), COLORS["stone"])
    draw = ImageDraw.Draw(image)

    def band(inner, outer, start, end, color):
        """Fill an exact radial strip; angles run clockwise from east in image space."""
        steps = max(2, math.ceil((end - start) * 3))
        angles = [math.radians(start + (end - start) * i / steps) for i in range(steps + 1)]
        points = [(size / 2 + math.cos(a) * r * size / SPAN_M,
                   size / 2 + math.sin(a) * r * size / SPAN_M)
                  for r, arc in ((outer, angles), (inner, reversed(angles))) for a in arc]
        draw.polygon(points, fill=COLORS[color])

    band(6.60, 7.05, 0, 360, "teal")
    band(4.35, 4.56, 0, 360, "teal")
    band(6.38, 6.53, 0, 360, "ivory")
    # Twelve broad pavers, not fine texture noise; two adjacent coral pieces make one shared corner.
    band(4.78, 6.23, 0, 360, "joint")
    for index in range(12):
        color = "coral" if index in (3, 4) else ("panel" if index % 2 == 0 else "stone")
        band(4.82, 6.19, index * 30 + .5, (index + 1) * 30 - .5, color)
    image = image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, compress_level=9, optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT /
                        f"art/textures/environment/{NID}/communal_circle_albedo.png")
    draw_artwork(parser.parse_args().output)
