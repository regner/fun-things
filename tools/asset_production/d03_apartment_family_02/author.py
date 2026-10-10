"""Author the saved open-U reference from existing apartment prefabs; never generate meshes."""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_02"
PREFIX = "d03_apartment_family_"
placements = []


def place(name, suffix, position, yaw=0):
    """Record a rigid prefab instance at its documented family datum."""
    placements.append((name, suffix, position, yaw))


# Low elbows connect three runs; the shorter east arm leaves a side walking link.
for name, x, yaw in [("WestCorner", 0, 0), ("EastCorner", 30, -90)]:
    for level in range(2):
        place(f"{name}L{level}", "06_outside", (x, 3.2 * level, 0), yaw)
    place(f"{name}Roof", "10_outside", (x, 3.2, 0), yaw)
for name, x, z, yaw, height, entry_yaw in [
    ("NorthA", 9, 0, 0, 2, 180),
    ("NorthB", 15, 0, 0, 3, None),
    ("NorthC", 21, 0, 0, 2, None),
    ("WestA", 0, 9, 90, 2, None),
    ("WestB", 0, 15, 90, 2, -90),
    ("EastA", 30, 9, 90, 2, 90),
]:
    for level in range(height):
        entry = entry_yaw is not None and level == 0
        place(f"{name}L{level}", "08" if entry else "05",
              (x, level * 3.2, z), entry_yaw if entry else yaw)
    place(f"{name}Roof", "10_straight", (x, (height - 1) * 3.2, z), yaw)
for name, x, z in [("WestEnd", 0, 18.12), ("EastEnd", 30, 12.12)]:
    for level in range(2):
        place(f"{name}L{level}", "07", (x, level * 3.2, z), -90)
    place(f"{name}Roof", "10_end", (x, 3.2, z), -90)
# Complete .11 includes its upper wall/end cap; no duplicate closure at the rise.
place("RiseWest", "11", (11.88, 3.2, 0), 180)
place("FallEast", "11", (18.12, 3.2, 0))
place("NorthCourtBalconyLower", "09", (15, 0, 6), 180)
place("NorthCourtBalconyUpper", "09", (15, 3.2, 6), 180)
place("WestCourtBalcony", "09", (6, 0, 9), -90)

resources = sorted({item[1] for item in placements})
lines = ['[gd_scene format=3]', '']
for suffix in resources:
    lines.append('[ext_resource type="PackedScene" '
                 f'path="res://scenes/prefabs/environment/{PREFIX}{suffix}.tscn" '
                 f'id="{suffix}"]')
lines += ['', '[node name="D03ApartmentFamily02" type="Node3D"]', '']
for name, suffix, (x, y, z), yaw in placements:
    cosine = round(math.cos(math.radians(yaw)), 8)
    sine = round(math.sin(math.radians(yaw)), 8)
    lines += [f'[node name="{name}" parent="." instance=ExtResource("{suffix}")]',
              f'transform = Transform3D({cosine:g}, 0, {sine:g}, 0, 1, 0, '
              f'{-sine:g}, 0, {cosine:g}, {x:g}, {y:g}, {z:g})', '']
path = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
if path.exists():
    raise SystemExit("Refusing to overwrite saved identities; edit the saved scene intentionally.")
path.write_text('\n'.join(lines), newline='\n')
print(f"Authored {len(placements)} existing prefab instances: {path}")
