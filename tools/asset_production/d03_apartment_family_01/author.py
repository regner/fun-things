"""Author the saved L reference from existing apartment prefabs; never generate meshes."""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_01"
PREFIX = "d03_apartment_family_"
placements = []


def place(name, suffix, position, yaw=0):
    """Record a rigid prefab instance at its documented family datum."""
    placements.append((name, suffix, position, yaw))


# The compact elbow stays low. Only a straight-run bay rises by one storey.
for level in range(2):
    place(f"CornerL{level}", "06_outside", (0, 3.2 * level, 0))
for name, x, z, yaw, height, entry in [
    ("EastA", 9, 0, 0, 2, True),
    ("EastB", 15, 0, 0, 3, False),
    ("EastC", 21, 0, 0, 2, False),
    ("SouthA", 0, 9, 90, 2, False),
    ("SouthB", 0, 15, 90, 2, True),
]:
    for level in range(height):
        # East entry faces the court; rotation preserves the symmetric core interface.
        facing = (180 if name == "EastA" else -90) if entry and level == 0 else yaw
        place(f"{name}L{level}", "08" if entry and level == 0 else "05",
              (x, level * 3.2, z), facing)
    place(f"{name}Roof", "10_straight", (x, (height - 1) * 3.2, z), yaw)
place("CornerRoof", "10_outside", (0, 3.2, 0))
for name, position, yaw in [("EastEnd", (24.12, 0, 0), 0),
                             ("SouthEnd", (0, 0, 18.12), -90)]:
    x, _, z = position
    for level in range(2):
        place(f"{name}L{level}", "07", (x, level * 3.2, z), yaw)
    place(f"{name}Roof", "10_end", (x, 3.2, z), yaw)
# Each .11 already contains its upper wall and terminal roof cap.
place("RiseWest", "11", (11.88, 3.2, 0), 180)
place("FallEast", "11", (18.12, 3.2, 0))
place("EastBalconyLower", "09", (15, 0, -6))
place("EastBalconyUpper", "09", (15, 3.2, -6))
place("SouthCourtBalcony", "09", (6, 0, 9), -90)

resources = sorted({item[1] for item in placements})
lines = ['[gd_scene format=3]', '']
for suffix in resources:
    lines.append('[ext_resource type="PackedScene" '
                 f'path="res://scenes/prefabs/environment/{PREFIX}{suffix}.tscn" '
                 f'id="{suffix}"]')
lines += ['', '[node name="D03ApartmentFamily01" type="Node3D"]', '']
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
