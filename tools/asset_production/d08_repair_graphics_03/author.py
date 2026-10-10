"""Original Ironreach service-warning faces using the family's project-owned path canvas."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_repair_graphics_03"
SIZE = (1220, 820)
VARIANTS = ("service_warning", "service_warning_patched")
OUTPUT = ROOT / f"art/textures/environment/{NID}"
FAMILY_SOURCE = ROOT / "tools/asset_production/d08_repair_graphics_01/author.py"
spec = importlib.util.spec_from_file_location("ironreach_path_art", FAMILY_SOURCE)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
canvas_module = family.canvas_module
PALETTE = family.PALETTE
# Local module instances only: no mutation of the earlier sibling's recipe or files.
canvas_module.GLYPHS.update({
    "M": [[(0, 6), (0, 0), (2, 3), (4, 0), (4, 6)]],
    "V": [[(0, 0), (2, 6), (4, 0)]],
})


def create_artwork(variant="service_warning"):
    """Keep a bold warning triangle and service-area copy clear of sparse edge wear."""
    if variant not in VARIANTS:
        raise ValueError(variant)
    c = canvas_module.Canvas()
    c.polygon([(24, 24), (1196, 24), (1196, 796), (24, 796)], "amber")
    # Old edge paint is a few deliberate broad shapes, not noisy random surface damage.
    for points in [
        [(24, 24), (220, 24), (216, 42), (124, 38), (112, 54), (24, 62)],
        [(916, 24), (1196, 24), (1196, 68), (1150, 61), (1137, 44), (920, 47)],
        [(24, 378), (43, 386), (38, 426), (61, 442), (49, 474), (24, 466)],
        [(1171, 557), (1196, 548), (1196, 682), (1183, 675), (1188, 624), (1169, 608)],
        [(855, 778), (958, 763), (991, 780), (1118, 774), (1127, 796), (855, 796)],
    ]:
        c.polygon(points, "old_paint")
    for points in [
        [(40, 29), (113, 29), (105, 40), (64, 39), (58, 48), (40, 45)],
        [(1176, 34), (1196, 34), (1196, 52), (1184, 46)],
        [(25, 411), (39, 418), (34, 448), (24, 445)],
    ]:
        c.polygon(points, "petrol")
    # Inset triangle, generous empty space and an unmistakable separated dot/bar.
    c.polygon([(230, 123), (400, 448), (60, 448)], "petrol")
    c.polygon([(230, 174), (354, 420), (106, 420)], "ivory")
    c.line([(230, 252), (230, 335)], "petrol", 29)
    c.ellipse((214, 363, 246, 395), "petrol")
    c.text("SERVICE", 468, 166, 103, "petrol", tracking=1.65, stroke=0.9)
    c.text("AREA", 468, 338, 112, "petrol", tracking=1.65, stroke=0.9)
    c.line([(460, 507), (1133, 507)], "petrol", 9)
    c.line([(110, 511), (237, 511)], "cyan", 22)
    c.line([(110, 544), (194, 544)], "cyan", 16)
    c.polygon([(69, 595), (1151, 595), (1151, 742), (69, 742)], "petrol")
    if variant == "service_warning_patched":
        # Repaint changes the lower finish only; the warning and wording stay intact.
        c.polygon([(102, 581), (1117, 590), (1129, 679), (1115, 755),
                   (109, 765), (119, 698), (99, 651)], "old_paint")
        c.polygon([(126, 610), (1091, 617), (1100, 731), (128, 741)], "fresh_paint")
    color = "petrol" if variant.endswith("_patched") else "ivory"
    c.text("MIND THE FIXES", 242, 646, 52, color, tracking=1.8, stroke=0.9)
    return c.finish()


def main():
    """Write both reproducible opaque albedo PNGs to runtime or an explicit scratch path."""
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
