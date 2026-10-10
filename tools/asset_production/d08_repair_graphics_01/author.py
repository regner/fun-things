"""Original Ironreach repair artwork; reuse project-owned path letters, no external font."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_repair_graphics_01"
SIZE = (1220, 820)
VARIANTS = ("fixed_enough", "fixed_enough_patched")
OUTPUT = ROOT / f"art/textures/environment/{NID}"
CANVAS_SOURCE = ROOT / "tools/asset_production/d06_commercial_graphics_02/author.py"
spec = importlib.util.spec_from_file_location("project_path_canvas", CANVAS_SOURCE)
canvas_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canvas_module)
# These are local module instances, not edits to the Signal Row palette or recipe.
PALETTE = {
    "petrol": "#263F43", "amber": "#DCAE66", "ivory": "#E9DFC1",
    "cyan": "#78ACA9", "old_paint": "#B6A77E", "fresh_paint": "#DCCDA5",
}
canvas_module.SIZE = SIZE
canvas_module.PALETTE = PALETTE
canvas_module.GLYPHS["X"] = [[(0, 0), (4, 6)], [(4, 0), (0, 6)]]


def create_artwork(variant="fixed_enough"):
    """Keep the large spanner and two-line shop name clear of deliberate edge wear."""
    if variant not in VARIANTS:
        raise ValueError(variant)
    c = canvas_module.Canvas()
    c.polygon([(24, 24), (1196, 24), (1196, 796), (24, 796)], "amber")
    # Sparse old paint at edges: broad authored shapes, not randomized grime/noise.
    for points in [
        [(24, 24), (281, 24), (272, 40), (173, 43), (170, 58), (73, 51), (24, 67)],
        [(1171, 180), (1196, 174), (1196, 387), (1180, 380), (1185, 293), (1169, 280)],
        [(24, 464), (48, 477), (43, 526), (61, 541), (50, 571), (24, 566)],
        [(965, 773), (1060, 765), (1078, 782), (1196, 774), (1196, 796), (965, 796)],
    ]:
        c.polygon(points, "old_paint")
    for points in [
        [(38, 29), (121, 29), (111, 38), (71, 36), (67, 47), (38, 44)],
        [(1182, 209), (1196, 204), (1196, 251), (1187, 244)],
        [(30, 510), (40, 518), (35, 545), (24, 548), (24, 514)],
    ]:
        c.polygon(points, "petrol")
    # Ivory service badge, one unmistakable diagonal open-ended spanner.
    c.polygon([(92, 194), (230, 114), (367, 194), (367, 390),
               (230, 470), (92, 390)], "ivory")
    c.line([(166, 390), (279, 240)], "petrol", 46)
    c.ellipse((137, 356, 194, 414), "petrol")
    c.ellipse((153, 372, 178, 397), "ivory")
    c.polygon([(240, 257), (230, 211), (251, 171), (273, 162),
               (266, 211), (302, 234), (341, 210), (338, 242),
               (303, 272), (264, 276)], "petrol")
    c.text("FIXED", 453, 147, 112, "petrol", tracking=1.65, stroke=0.9)
    c.text("ENOUGH", 453, 337, 112, "petrol", tracking=1.65, stroke=0.9)
    c.line([(452, 507), (1128, 507)], "petrol", 9)
    c.line([(102, 516), (227, 516)], "cyan", 22)
    c.line([(102, 548), (183, 548)], "cyan", 16)
    # Small original copy is a close-view joke, not a gameplay information contract.
    c.polygon([(69, 595), (1151, 595), (1151, 742), (69, 742)], "petrol")
    if variant == "fixed_enough_patched":
        # A second hand-painted patch changes finish, never hardware or sign content.
        c.polygon([(386, 575), (1166, 583), (1158, 754), (393, 765),
                   (404, 687), (388, 648)], "old_paint")
        c.polygon([(411, 602), (1139, 609), (1136, 735), (414, 742)], "fresh_paint")
        c.text("NOISES", 111, 623, 39, "ivory", tracking=1.8, stroke=0.9)
        c.text("COST EXTRA", 455, 640, 48, "petrol", tracking=1.9, stroke=0.9)
    else:
        c.text("NOISES COST EXTRA", 145, 642, 52, "ivory", tracking=1.8, stroke=0.9)
    return c.finish()


def main():
    """Write both deterministic weathered albedo variants to runtime or scratch."""
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
