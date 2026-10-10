"""Original depot direction artwork on the shared low panel; no fonts or external images."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_repair_graphics_02"
SIZE = (1440, 390)
VARIANTS = ("depot_right", "depot_right_patched")
OUTPUT = ROOT / f"art/textures/environment/{NID}"
FAMILY_SOURCE = ROOT / "tools/asset_production/d08_repair_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("ironreach_artwork", FAMILY_SOURCE)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
# A private canvas module instance shares the existing Ironreach swatches and stroke letters.
canvas_module = family.canvas_module
canvas_module.SIZE = SIZE
PALETTE = family.PALETTE
canvas_module.GLYPHS["W"] = [[(0, 0), (0.8, 6), (2, 3.5), (3.2, 6), (4, 0)]]


def create_artwork(variant="depot_right"):
    """Keep depot and right arrow invariant; vary only the weathered lower paint finish."""
    if variant not in VARIANTS:
        raise ValueError(variant)
    c = canvas_module.Canvas()
    c.polygon([(16, 16), (1424, 16), (1424, 374), (16, 374)], "amber")
    # Large, sparse chips stay at the perimeter, clear of primary lettering and arrow.
    for points in [
        [(16, 16), (342, 16), (326, 30), (198, 28), (176, 39), (80, 32), (16, 45)],
        [(1397, 16), (1424, 16), (1424, 127), (1409, 117), (1412, 68), (1398, 56)],
        [(16, 291), (41, 283), (38, 316), (56, 323), (46, 346), (16, 346)],
        [(1140, 355), (1234, 352), (1251, 364), (1383, 359), (1424, 366),
         (1424, 374), (1140, 374)],
    ]:
        c.polygon(points, "old_paint")
    c.polygon([(28, 22), (132, 22), (124, 31), (75, 29), (68, 37), (28, 35)], "petrol")
    c.polygon([(1410, 74), (1424, 80), (1424, 108), (1416, 103)], "petrol")
    c.text("DEPOT", 93, 70, 126, "petrol", tracking=1.8, stroke=0.9)
    # Ivory arrow field uses the fascia badge's broad contrast rather than electric light.
    c.polygon([(1009, 48), (1387, 48), (1387, 337), (1009, 337)], "ivory")
    c.polygon([(1054, 153), (1210, 153), (1210, 91), (1341, 192),
               (1210, 294), (1210, 232), (1054, 232)], "petrol")
    c.line([(763, 84), (918, 84)], "cyan", 20)
    c.line([(763, 116), (860, 116)], "cyan", 14)
    # Secondary service copy is optional close-view information, never a route authority.
    c.polygon([(60, 243), (953, 243), (953, 337), (60, 337)], "petrol")
    if variant == "depot_right_patched":
        c.polygon([(54, 232), (967, 237), (962, 348), (61, 353), (68, 300)], "old_paint")
        c.polygon([(79, 254), (936, 251), (943, 329), (74, 333)], "fresh_paint")
        c.text("PARTS THIS WAY", 210, 265, 50, "petrol", tracking=1.85, stroke=0.9)
    else:
        c.text("PARTS THIS WAY", 210, 265, 50, "ivory", tracking=1.85, stroke=0.9)
    return c.finish()


def main():
    """Write two reproducible RGB albedos to runtime paths or an explicit scratch directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        path = args.output_dir / f"{variant}_albedo.png"
        create_artwork(variant).save(path, compress_level=9)
        print(path)


if __name__ == "__main__":
    main()
