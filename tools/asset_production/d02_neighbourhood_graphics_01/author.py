"""Original quiet residential watch artwork, using existing project-owned path lettering."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_01"
SIZE = (1220, 820)
PALETTE = {"ivory": "#F6F1DC", "plum": "#635168", "blue": "#526D86"}
OUTPUT = ROOT / f"art/textures/environment/{NID}/watch_notice_albedo.png"
SHARED = ROOT / "tools/asset_production/d06_commercial_graphics_02/author.py"
spec = importlib.util.spec_from_file_location("project_path_canvas", SHARED)
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
# Reuse the original project strokes/canvas, not Signal Row's commercial palette/layout.
shared.SIZE = SIZE
shared.PALETTE = {**PALETTE, "petrol": PALETTE["ivory"]}
shared.GLYPHS.update({
    "M": [[(0, 6), (0, 0), (2, 2.6), (4, 0), (4, 6)]],
    "W": [[(0, 0), (0.7, 6), (2, 3.5), (3.3, 6), (4, 0)]],
})


def create_artwork():
    """Build a curtain-window emblem and two-level joke within the carrier safe rectangle."""
    c = shared.Canvas()
    # A restrained single rule, broad whitespace and muted inks distinguish domestic notices.
    c.line([(55, 55), (1165, 55), (1165, 765), (55, 765), (55, 55)], "plum", 8)
    c.text("NEIGHBOURHOOD", 469, 182, 45, "blue", tracking=1.35, stroke=0.63)
    c.text("WATCH", 471, 296, 129, "plum", tracking=1.35, stroke=0.66)
    # Original four-pane window: drawn curtains part just enough to suggest nosy neighbours.
    c.polygon([(136, 173), (394, 173), (394, 472), (136, 472)], "blue")
    c.polygon([(154, 194), (376, 194), (376, 450), (154, 450)], "ivory")
    c.line([(265, 194), (265, 450)], "blue", 11)
    c.line([(154, 319), (376, 319)], "blue", 11)
    c.polygon([(156, 196), (244, 196), (217, 290), (191, 332), (213, 446),
               (156, 446)], "plum")
    c.polygon([(374, 196), (286, 196), (313, 290), (339, 332), (317, 446),
               (374, 446)], "plum")
    c.line([(120, 477), (410, 477)], "blue", 17)
    # The punchline is larger than secondary copy, with no pretend seals or real branding.
    c.line([(130, 542), (1090, 542)], "blue", 5)
    c.text("MOSTLY CURTAINS", 151, 620, 70, "plum", tracking=1.45, stroke=0.68)
    return c.finish()


def main():
    """Write one deterministic RGB PNG; optional scratch output supports byte comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
