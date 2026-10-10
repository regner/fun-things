"""Initial-only linked access wrapper and terminal/side-connection collision fixture."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_05"
prefab = ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"
fixture = ROOT / f"tools/asset_production/{ASSET}/mating_check.tscn"
assert not prefab.exists() and not fixture.exists(), "Never overwrite normalized scene identities"
prefab.write_text('''[gd_scene load_steps=3 format=3]

[ext_resource type="PackedScene" path="res://art/models/environment/city_boardwalk_05/city_boardwalk_05.glb" id="1_model"]

[sub_resource type="ConvexPolygonShape3D" id="Convex_access"]
points = PackedVector3Array(-1.8, -0.24, 0, 1.8, -0.24, 0, 2.4, -0.24, -3, -2.4, -0.24, -3, -1.8, 0, 0, 1.8, 0, 0, 2.4, 0, -3, -2.4, 0, -3)

[node name="CityBoardwalk05" type="Node3D"]

[node name="Visuals" type="Node3D" parent="."]

[node name="Model" parent="Visuals" instance=ExtResource("1_model")]

[node name="Collision" type="Node3D" parent="."]

[node name="Body" type="StaticBody3D" parent="Collision"]
collision_layer = 1
collision_mask = 0

[node name="Access" type="CollisionShape3D" parent="Collision/Body"]
shape = SubResource("Convex_access")
''', newline="\n")
fixture.write_text('''[gd_scene load_steps=7 format=3]

[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_05.tscn" id="1_access"]
[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_01.tscn" id="2_deck"]
[ext_resource type="Script" path="res://scripts/actors/actor_motion.gd" id="3_motion"]

[sub_resource type="CapsuleShape3D" id="Capsule_actor"]
radius = 0.35
height = 1.8

[sub_resource type="BoxShape3D" id="Box_test_prom"]
size = Vector3(4.8, 0.24, 3)

[sub_resource type="BoxShape3D" id="Box_test_side_prom"]
size = Vector3(3, 0.24, 4.8)

[node name="BoardwalkAccessCheck" type="Node3D"]

[node name="Deck" parent="." instance=ExtResource("2_deck")]
position = Vector3(0, 0, 3)

[node name="Access" parent="." instance=ExtResource("1_access")]

[node name="PromenadeEnvelope" type="StaticBody3D" parent="."]
position = Vector3(0, -0.12, -4.5)
collision_mask = 0

[node name="Floor" type="CollisionShape3D" parent="PromenadeEnvelope"]
shape = SubResource("Box_test_prom")

[node name="SideDeck" parent="." instance=ExtResource("2_deck")]
position = Vector3(12, 0, 0)

[node name="SideAccess" parent="." instance=ExtResource("1_access")]
position = Vector3(13.8, 0, 0)
rotation = Vector3(0, -1.570796326794897, 0)

[node name="SidePromenadeEnvelope" type="StaticBody3D" parent="."]
position = Vector3(18.3, -0.12, 0)
collision_mask = 0

[node name="Floor" type="CollisionShape3D" parent="SidePromenadeEnvelope"]
shape = SubResource("Box_test_side_prom")

[node name="Actor" type="CharacterBody3D" parent="."]
collision_layer = 2
script = ExtResource("3_motion")

[node name="Capsule" type="CollisionShape3D" parent="Actor"]
position = Vector3(0, 0.9, 0)
shape = SubResource("Capsule_actor")
''', newline="\n")
print("INITIAL_PREFAB_AND_FIXTURE_AUTHORED")
