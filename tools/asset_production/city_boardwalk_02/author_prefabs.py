"""Author saved linked wrappers and a mating fixture; Godot normalizes new scene identities."""
from math import cos, radians, sin
from pathlib import Path

from design import ASSET, DEPTH, RADIUS, VARIANTS, WIDTH, point

ROOT = Path(__file__).resolve().parents[3]
PREFABS = ROOT / "scenes/prefabs/environment"
TOOLS = ROOT / f"tools/asset_production/{ASSET}"


def number(value):
    """Keep collision coordinates deterministic without negative-zero noise."""
    return f"{0 if abs(value) < 1e-9 else value:.9f}".rstrip("0").rstrip(".") or "0"


def triangle(a, b, c):
    """Convert Blender CCW points to Godot's clockwise face winding and Y-up axes."""
    return [v for x, y, z in (a, c, b) for v in (x, z, -y)]


def quad(a, b, c, d):
    """Triangulate one continuous surface without introducing internal walls."""
    return triangle(a, b, c) + triangle(a, c, d)


def collision(degrees, count):
    """Return a closed static annular slab: flat top, bottom and perimeter only."""
    data = []
    angle = radians(degrees)
    inner, outer = RADIUS - WIDTH / 2, RADIUS + WIDTH / 2
    for i in range(count):
        a, b = angle * i / count, angle * (i + 1) / count
        plan = [point(inner, a), point(inner, b), point(outer, b), point(outer, a)]
        bottom = [(x, y, -DEPTH) for x, y, _z in plan]
        data += quad(*plan)
        data += quad(*reversed(bottom))
        # Only the inner/outer boundaries, not the joins between radial cells.
        for u, v in ((0, 1), (2, 3)):
            data += quad(bottom[u], bottom[v], plan[v], plan[u])
        if i == 0:
            data += quad(bottom[3], bottom[0], plan[0], plan[3])
        if i == count - 1:
            data += quad(bottom[1], bottom[2], plan[2], plan[1])
    return ", ".join(number(v) for v in data)


for suffix, degrees, count in VARIANTS:
    name = ASSET + suffix
    path = PREFABS / (name + ".tscn")
    if path.exists():
        raise SystemExit(f"Refusing to replace normalized scene identities: {path}")
    path.write_text(f'''[gd_scene load_steps=3 format=3]

[ext_resource type="PackedScene" path="res://art/models/environment/{ASSET}/{name}.glb" id="1_model"]

[sub_resource type="ConcavePolygonShape3D" id="Deck_profile"]
data = PackedVector3Array({collision(degrees, count)})

[node name="{name}" type="Node3D"]

[node name="Visuals" type="Node3D" parent="."]

[node name="Model" parent="Visuals" instance=ExtResource("1_model")]

[node name="Collision" type="Node3D" parent="."]

[node name="Body" type="StaticBody3D" parent="Collision"]
collision_mask = 0

[node name="Deck" type="CollisionShape3D" parent="Collision/Body"]
shape = SubResource("Deck_profile")
''', newline="\n")

fixture = ['[gd_scene load_steps=7 format=3]', '',
           '[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_01.tscn" id="1_straight"]',
           '[ext_resource type="Script" path="res://scripts/actors/actor_motion.gd" id="2_motion"]']
for index, (suffix, _degrees, _count) in enumerate(VARIANTS):
    fixture.append(f'[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/{ASSET}{suffix}.tscn" id="bend_{index}"]')
fixture += ['', '[sub_resource type="CapsuleShape3D" id="Actor_capsule"]',
            'radius = 0.35', 'height = 1.8', '',
            '[node name="BendWalkCheck" type="Node3D"]']
for index, (suffix, degrees, _count) in enumerate(VARIANTS):
    offset = 20 * index
    angle = radians(degrees)
    end = point(RADIUS, angle)
    x, z = offset + end[0] + 3 * sin(angle), -end[1] - 3 * cos(angle)
    # Explicit saved placement, never runtime-authored geometry or node composition.
    fixture += ['', f'[node name="Bend{index}" parent="." instance=ExtResource("bend_{index}")]',
                f'position = Vector3({offset}, 0, 0)', '',
                f'[node name="Entry{index}" parent="." instance=ExtResource("1_straight")]',
                f'position = Vector3({offset}, 0, 3)', '',
                f'[node name="Exit{index}" parent="." instance=ExtResource("1_straight")]',
                f'position = Vector3({number(x)}, 0, {number(z)})',
                f'rotation = Vector3(0, {number(-angle)}, 0)']
fixture += ['', '[node name="Actor" type="CharacterBody3D" parent="."]',
            'position = Vector3(0, 0.001, 2)', 'collision_layer = 2',
            'script = ExtResource("2_motion")', '',
            '[node name="Capsule" type="CollisionShape3D" parent="Actor"]',
            'position = Vector3(0, 0.9, 0)', 'shape = SubResource("Actor_capsule")', '']
path = TOOLS / "walk_check.tscn"
if path.exists():
    raise SystemExit(f"Refusing to replace normalized fixture identities: {path}")
path.write_text("\n".join(fixture), newline="\n")
print("AUTHORED_THREE_PREFABS_AND_MATING_FIXTURE")
