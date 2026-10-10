"""Initial text authoring only: linked edge wrappers and unchanged sibling mating fixtures."""
from math import cos, radians, sin
from pathlib import Path

from design import ASSET, VARIANTS, segments, station

ROOT = Path(__file__).resolve().parents[3]
PREFABS = ROOT / "scenes/prefabs/environment"
TOOLS = ROOT / f"tools/asset_production/{ASSET}"


def number(value):
    """Serialize stable collision/placement coordinates without negative-zero noise."""
    return f"{0 if abs(value) < 1e-9 else value:.9f}".rstrip("0").rstrip(".") or "0"


def quad(a, b, c, d):
    """Convert Blender CCW quads into Godot clockwise triangle coordinates."""
    return [v for x, y, z in (a, c, b, a, d, c) for v in (x, z, -y)]


def collision(variant):
    """Author a closed thin static ribbon, not a convex hull spanning the inside of a bend."""
    count = segments(variant)
    result = []
    for i in range(count):
        # Boundary-to-outboard order differs between the inner and outer edges.
        u, v = (0, .1) if variant[3] == 1 else (.1, 0)
        plan = [station(variant, i / count, u, 0),
                station(variant, (i + 1) / count, u, 0),
                station(variant, (i + 1) / count, v, 0),
                station(variant, i / count, v, 0)]
        bottom = [(x, y, -.24) for x, y, _z in plan]
        result += quad(*plan) + quad(*reversed(bottom))
        for a, b in ((0, 1), (2, 3)):
            result += quad(bottom[a], bottom[b], plan[b], plan[a])
        if i == 0:
            result += quad(bottom[3], bottom[0], plan[0], plan[3])
        if i == count - 1:
            result += quad(bottom[1], bottom[2], plan[2], plan[1])
    return ", ".join(number(v) for v in result)


def write_new(path, text):
    """Never overwrite normalized scene/dependency identities during reproduction."""
    if path.exists():
        raise SystemExit(f"Refusing to replace existing scene identities: {path}")
    path.write_text(text, newline="\n")


for variant in VARIANTS:
    suffix, angle, _radius, _sign, length = variant
    name = ASSET + suffix
    shape = (f'[sub_resource type="ConcavePolygonShape3D" id="Edge_profile"]\n'
             f'data = PackedVector3Array({collision(variant)})' if angle else
             f'[sub_resource type="BoxShape3D" id="Edge_profile"]\n'
             f'size = Vector3(0.1, 0.24, {length})')
    position = '' if angle else 'position = Vector3(0.05, -0.12, 0)\n'
    write_new(PREFABS / (name + ".tscn"), f'''[gd_scene load_steps=3 format=3]

[ext_resource type="PackedScene" path="res://art/models/environment/{ASSET}/{name}.glb" id="1_model"]

{shape}

[node name="{name}" type="Node3D"]

[node name="Visuals" type="Node3D" parent="."]

[node name="Model" parent="Visuals" instance=ExtResource("1_model")]

[node name="Collision" type="Node3D" parent="."]

[node name="Body" type="StaticBody3D" parent="Collision"]
collision_mask = 0

[node name="Edge" type="CollisionShape3D" parent="Collision/Body"]
{position}shape = SubResource("Edge_profile")
''')

fixture = ['[gd_scene load_steps=15 format=3]', '']
for index, variant in enumerate(VARIANTS):
    fixture.append(f'[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/{ASSET}{variant[0]}.tscn" id="edge_{index}"]')
for index, suffix in enumerate(("", "_45", "_22p5")):
    fixture.append(f'[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_02{suffix}.tscn" id="bend_{index}"]')
fixture += ['[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_01.tscn" id="straight"]',
            '[ext_resource type="Script" path="res://scripts/actors/actor_motion.gd" id="motion"]', '',
            '[sub_resource type="CapsuleShape3D" id="Actor_capsule"]',
            'radius = 0.35', 'height = 1.8', '',
            '[node name="EdgeMatingCheck" type="Node3D"]']


def instance(name, resource, x, z, yaw=0):
    """Save explicit prefab placement; runtime checks never construct visual node hierarchies."""
    fixture.extend(['', f'[node name="{name}" parent="." instance=ExtResource("{resource}")]',
                    f'position = Vector3({number(x)}, 0, {number(z)})',
                    f'rotation = Vector3(0, {number(yaw)}, 0)'])


def dressed_straight(name, x, z, yaw):
    """Keep the full 3.6 m timber lane clear by fitting both trim strips outboard."""
    instance(name, "straight", x, z, yaw)
    for side in (-1, 1):
        instance(name + ("Left" if side < 0 else "Right"), "edge_0",
                 x + side * 1.8 * cos(yaw), z - side * 1.8 * sin(yaw),
                 yaw + (3.141592653589793 if side < 0 else 0))


for index, degrees in enumerate((90, 45, 22.5)):
    offset, angle = index * 20, radians(degrees)
    instance(f"Bend{index}", f"bend_{index}", offset, 0)
    instance(f"Outer{index}", f"edge_{2 + index * 2}", offset, 0)
    instance(f"Inner{index}", f"edge_{3 + index * 2}", offset, 0)
    dressed_straight(f"Entry{index}", offset, 3, 0)
    dressed_straight(f"Exit{index}", offset + 6 * (1 - cos(angle)) + 3 * sin(angle),
                     -6 * sin(angle) - 3 * cos(angle), -angle)
dressed_straight("TerminalDeck", 60, 0, 0)
instance("TerminalCap", "edge_1", 60, -3, radians(90))
fixture += ['', '[node name="Actor" type="CharacterBody3D" parent="."]',
            'position = Vector3(0, 0.001, 2)', 'collision_layer = 2',
            'script = ExtResource("motion")', '',
            '[node name="Capsule" type="CollisionShape3D" parent="Actor"]',
            'position = Vector3(0, 0.9, 0)', 'shape = SubResource("Actor_capsule")', '']
write_new(TOOLS / "mating_check.tscn", "\n".join(fixture))
print("AUTHORED_EIGHT_WRAPPERS_AND_SAVED_MATING_FIXTURE")
