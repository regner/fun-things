"""Initial-only saved prefab and bounded mating/contact fixture; preserve existing scene IDs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_04"
prefab = ROOT / f"scenes/prefabs/environment/{ASSET}.tscn"
fixture = ROOT / f"tools/asset_production/{ASSET}/mating_check.tscn"
assert not prefab.exists() and not fixture.exists(), "Never overwrite normalized scene identities"
prefab.write_text('''[gd_scene load_steps=4 format=3]

[ext_resource type="PackedScene" path="res://art/models/environment/city_boardwalk_04/city_boardwalk_04.glb" id="1_model"]

[sub_resource type="BoxShape3D" id="Box_post"]
size = Vector3(0.5, 1.68, 0.56)

[sub_resource type="BoxShape3D" id="Box_head"]
size = Vector3(3.36, 0.32, 0.48)

[node name="CityBoardwalk04" type="Node3D"]

[node name="Visuals" type="Node3D" parent="."]

[node name="Model" parent="Visuals" instance=ExtResource("1_model")]

[node name="Collision" type="Node3D" parent="."]

[node name="Body" type="StaticBody3D" parent="Collision"]
collision_layer = 1
collision_mask = 0

[node name="LeftPost" type="CollisionShape3D" parent="Collision/Body"]
position = Vector3(-1.38, 0.84, 0)
shape = SubResource("Box_post")

[node name="RightPost" type="CollisionShape3D" parent="Collision/Body"]
position = Vector3(1.38, 0.84, 0)
shape = SubResource("Box_post")

[node name="Crosshead" type="CollisionShape3D" parent="Collision/Body"]
position = Vector3(0, 1.84, 0)
shape = SubResource("Box_head")
''', newline="\n")
fixture.write_text('''[gd_scene load_steps=8 format=3]

[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_04.tscn" id="1_support"]
[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_01.tscn" id="2_deck"]
[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_03.tscn" id="3_fascia"]
[ext_resource type="Script" path="res://scripts/actors/actor_motion.gd" id="4_motion"]
[ext_resource type="PackedScene" path="res://scenes/prefabs/environment/city_boardwalk_02_45.tscn" id="5_bend"]

[sub_resource type="CapsuleShape3D" id="Capsule_actor"]
radius = 0.35
height = 1.8

[sub_resource type="BoxShape3D" id="Box_test_floor"]
size = Vector3(8, 0.24, 8)

[node name="BoardwalkSupportCheck" type="Node3D"]

[node name="Deck" parent="." instance=ExtResource("2_deck")]
position = Vector3(0, 2.24, 0)

[node name="SupportA" parent="." instance=ExtResource("1_support")]
position = Vector3(0, 0, -1.5)

[node name="SupportB" parent="." instance=ExtResource("1_support")]
position = Vector3(0, 0, 1.5)

[node name="RightFascia" parent="." instance=ExtResource("3_fascia")]
position = Vector3(1.8, 2.24, 0)

[node name="LeftFascia" parent="." instance=ExtResource("3_fascia")]
position = Vector3(-1.8, 2.24, 0)
rotation = Vector3(0, 3.141592653589793, 0)

[node name="ContactSupport" parent="." instance=ExtResource("1_support")]
position = Vector3(12, 0, 0)

[node name="ContactFloor" type="StaticBody3D" parent="."]
position = Vector3(12, -0.12, 0)
collision_layer = 1
collision_mask = 0

[node name="Floor" type="CollisionShape3D" parent="ContactFloor"]
shape = SubResource("Box_test_floor")

[node name="Bend" parent="." instance=ExtResource("5_bend")]
position = Vector3(24, 2.24, 0)

[node name="BendSupport" parent="." instance=ExtResource("1_support")]
position = Vector3(24.456723, 0, -2.296101)
rotation = Vector3(0, -0.392699081698724, 0)

[node name="Actor" type="CharacterBody3D" parent="."]
collision_layer = 2
script = ExtResource("4_motion")

[node name="Capsule" type="CollisionShape3D" parent="Actor"]
position = Vector3(0, 0.9, 0)
shape = SubResource("Capsule_actor")
''', newline="\n")
print("INITIAL_PREFAB_AND_FIXTURE_AUTHORED")
