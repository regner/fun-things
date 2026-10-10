"""Original Terrace Ward stepping artwork; no downloaded art or external font dependency."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_court_graphics_02"
SIZE = (512, 1024)
SUPERSAMPLE = 4
SPAN_M = (3.0, 6.0)
# Centres in Blender XY: number one starts at the south end and ascends north.
CELLS = [(0, -2.25), (0, -1.35), (-.5, -.45), (.5, -.45),
         (0, .45), (-.5, 1.35), (.5, 1.35), (0, 2.25)]
COLORS = {"teal": "#587D7C", "ivory": "#CECDB8", "coral": "#B98377"}
# Original rounded monoline glyph paths in a unit box, not a third-party font.
DIGITS = {
    1: [[(.2, .22), (.5, 0), (.5, 1)], [(.2, 1), (.8, 1)]],
    2: [[(0, .18), (.12, .04), (.35, 0), (.7, .02), (.9, .15), (1, .32),
         (.9, .48), (.65, .63), (.2, .85), (0, 1), (1, 1)]],
    3: [[(0, .07), (.3, 0), (.65, .02), (.9, .14), (1, .3), (.85, .44),
         (.5, .5), (.85, .56), (1, .72), (.95, .86), (.7, .98), (.3, 1), (0, .93)]],
    4: [[(.75, 1), (.75, 0), (0, .65), (1, .65)]],
    5: [[(.95, 0), (.1, 0), (.05, .48), (.5, .43), (.82, .5), (1, .66),
         (.97, .83), (.75, .97), (.35, 1), (0, .9)]],
    6: [[(.9, .03), (.6, 0), (.25, .15), (.05, .43), (0, .75), (.13, .94),
         (.45, 1), (.78, .97), (1, .8), (.95, .61), (.72, .5), (.3, .5), (.05, .65)]],
    7: [[(0, 0), (1, 0), (.4, 1)]],
    8: [[(.5, .5), (.15, .4), (0, .23), (.1, .07), (.35, 0), (.7, .02),
         (.95, .15), (1, .3), (.85, .43), (.5, .5), (.15, .6), (0, .78),
         (.12, .94), (.4, 1), (.75, .97), (1, .83), (.95, .66), (.8, .57), (.5, .5)]],
}


def cell_outline(cx, cy, inset=0):
    """Return an eight-corner footprint in metres, counterclockwise in Blender XY."""
    x, y, bevel = .45 - inset, .4 - inset, .08
    return [(cx - x + bevel, cy - y), (cx + x - bevel, cy - y),
            (cx + x, cy - y + bevel), (cx + x, cy + y - bevel),
            (cx + x - bevel, cy + y), (cx - x + bevel, cy + y),
            (cx - x, cy + y - bevel), (cx - x, cy - y + bevel)]


def draw_artwork(path):
    """Draw eight separate painted cells; unused atlas pixels are never ground geometry."""
    width, height = (value * SUPERSAMPLE for value in SIZE)
    image = Image.new("RGB", (width, height), COLORS["ivory"])
    draw = ImageDraw.Draw(image)

    def pixel(x, y):
        """Map Blender north/+Y to image top, matching the carrier's plan UVs."""
        return ((x / SPAN_M[0] + .5) * width, (.5 - y / SPAN_M[1]) * height)

    for number, (cx, cy) in enumerate(CELLS, 1):
        fill = COLORS["coral" if number in (3, 4) else "teal"]
        draw.polygon([pixel(x, y) for x, y in cell_outline(cx, cy, .065)], fill=fill)
        # Hand-drawn strokes have rounded joins/caps and no segmented-display styling.
        stroke = .055
        for path_points in DIGITS[number]:
            points = [(cx + (x - .5) * .25, cy + (.5 - y) * .38)
                      for x, y in path_points]
            draw.line([pixel(x, y) for x, y in points], fill=COLORS["ivory"],
                      width=round(stroke * width / SPAN_M[0]), joint="curve")
            for x, y in points:
                a, b = pixel(x - stroke / 2, y + stroke / 2)
                c, d = pixel(x + stroke / 2, y - stroke / 2)
                draw.ellipse((a, b, c, d), fill=COLORS["ivory"])
    image = image.resize(SIZE, Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, compress_level=9, optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT /
                        f"art/textures/environment/{NID}/play_steps_albedo.png")
    draw_artwork(parser.parse_args().output)
