"""Author the saved short-infill reference from existing apartment prefabs; never generate meshes."""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_03"
PREFIX = "d03_apartment_family_"
placements = []


def place(name, suffix, position, yaw=0):
    """Record a rigid prefab instance at its documented family datum."""
    placements.append((name, suffix, position, yaw))


# Three unscaled bays form a short, low infill rather than another long apartment bar.
for name, x in [("WestBay", -6), ("EntryBay", 0), ("EastBay", 6)]:
    for level in range(2):
        place(f"{name}L{level}", "08" if x == 0 and level == 0 else "05",
              (x, 3.2 * level, 0))
    place(f"{name}Roof", "10_straight", (x, 3.2, 0))
for name, x, yaw in [("WestEnd", -9.12, 180), ("EastEnd", 9.12, 0)]:
    for level in range(2):
        place(f"{name}L{level}", "07", (x, 3.2 * level, 0), yaw)
    place(f"{name}Roof", "10_end", (x, 3.2, 0), yaw)
place("EastFrontBalcony", "09", (6, 0, -6))

resources = sorted({item[1] for item in placements})
lines = ['[gd_scene format=3]', '']
for suffix in resources:
    lines.append('[ext_resource type="PackedScene" '
                 f'path="res://scenes/prefabs/environment/{PREFIX}{suffix}.tscn" '
                 f'id="{suffix}"]')
lines += ['', '[node name="D03ApartmentFamily03" type="Node3D"]', '']
for name, suffix, (x, y, z), yaw in placements:
    cosine = round(math.cos(math.radians(yaw)), 8)
    sine = round(math.sin(math.radians(yaw)), 8)
    lines += [f'[node name="{name}" parent="." instance=ExtResource("{suffix}")]',
              f'transform = Transform3D({cosine:g}, 0, {-sine:g}, 0, 1, 0, '
              f'{sine:g}, 0, {cosine:g}, {x:g}, {y:g}, {z:g})', '']
path = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
if path.exists():
    raise SystemExit("Refusing to overwrite saved identities; edit the saved scene intentionally.")
path.write_text('\n'.join(lines), newline='\n')
print(f"Authored {len(placements)} existing prefab instances: {path}")
