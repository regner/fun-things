"""Draw one original rightward passage face using Signal Row's original path lettering."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_04"
SIZE = (1220, 820)
OUTPUT = ROOT / f"art/textures/environment/{NID}/passage_albedo.png"
spec = importlib.util.spec_from_file_location(
    "signal_row_canvas", ROOT / "tools/asset_production/d06_commercial_graphics_02/author.py")
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
# Adapt only the in-memory canvas size; the shared path/palette source stays unchanged.
family.SIZE = SIZE
PALETTE = family.PALETTE


def create_artwork():
    """Make the open doorway and broad right arrow primary; copy remains supplemental."""
    canvas = family.Canvas()
    # Open doorway: a clear negative-space opening, with one inward-swung leaf.
    canvas.line([(155, 537), (155, 139), (450, 139), (450, 537)], "cyan", 48)
    canvas.polygon([(179, 163), (329, 209), (329, 485), (179, 523)], "cyan")
    canvas.ellipse((288, 343, 308, 363), "petrol")
    # A single unambiguous direction, with enough gap from the doorway to read separately.
    canvas.polygon([(526, 294), (856, 294), (856, 182), (1090, 350),
                    (856, 518), (856, 406), (526, 406)], "ivory")
    canvas.line([(139, 573), (466, 573)], "magenta", 28)
    canvas.text("PASSAGE", 263, 650, 110, "ivory", tracking=1.65)
    return canvas.finish()


def main():
    """Write the deterministic opaque texture, optionally to an external scratch path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_artwork().save(args.output, optimize=False, compress_level=9)
    print(args.output)


if __name__ == "__main__":
    main()
