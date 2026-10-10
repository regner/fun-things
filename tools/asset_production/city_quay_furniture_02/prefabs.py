"""Author new linked rail wrappers as text; Godot check.gd owns normalization and UID saves.

Existing scenes are never overwritten, preserving accepted node/resource identities.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_quay_furniture_02"
MOUNTS = {"quay": (.30, .30), "deck": (.22, .34), "landward": (.32, .32)}
# Godot coordinates: corner turns from east toward north (-Z).
POSTS = {"straight": [(-1.5, 0), (1.5, 0)],
         "corner": [(-.75, .75), (.691421356, .691421356), (.75, -.75)],
         "end": [(0, 0)], "post": []}


def name_for(form, mount):
    """Use the unsuffixed prefab as the default standalone quay straight run."""
    return ASSET if (form, mount) == ("straight", "quay") else f"{ASSET}_{form}_{mount}"


def main():
    """Save twelve complete wrappers with one simple body and no copied render geometry."""
    for mount, (width, depth) in MOUNTS.items():
        for form in POSTS:
            name = name_for(form, mount)
            path = ROOT / f"scenes/prefabs/environment/{name}.tscn"
            if path.exists():
                continue
            model = "post_" + mount if form == "post" else form
            lines = ["[gd_scene format=3]", "",
                     f'[ext_resource type="PackedScene" path="res://art/models/environment/{ASSET}/{ASSET}_{model}.glb" id="1_model"]']
            if form != "post":
                lines += [f'[ext_resource type="PackedScene" path="res://art/models/environment/{ASSET}/{ASSET}_post_{mount}.glb" id="2_post"]']
            if form == "straight":
                boxes = [((3 + width, 1.06, depth), (0, .53, 0))]
            elif form == "corner":
                boxes = [((1.5 + width, 1.06, depth), (0, .53, .75)),
                         ((width, 1.06, 1.5 + depth), (.75, .53, 0))]
            elif form == "end":
                boxes = [((.535 + width / 2, 1.06, depth), ((.535 - width / 2) / 2, .53, 0))]
            else:
                boxes = [((width, 1.06, depth), (0, .53, 0))]
            for index, (size, _position) in enumerate(boxes):
                lines += ["", f'[sub_resource type="BoxShape3D" id="Box_{index}"]',
                          "size = Vector3(%s, %s, %s)" % size]
            lines += ["", f'[node name="{name}" type="Node3D"]', "",
                      '[node name="Visuals" type="Node3D" parent="."]', "",
                      '[node name="Model" parent="Visuals" instance=ExtResource("1_model")]']
            for index, (x, z) in enumerate(POSTS[form]):
                lines += ["", f'[node name="Post{index}" parent="Visuals" instance=ExtResource("2_post")]',
                          f"position = Vector3({x}, 0, {z})"]
            lines += ["", '[node name="Collision" type="Node3D" parent="."]', "",
                      '[node name="RailBody" type="StaticBody3D" parent="Collision"]',
                      'collision_mask = 0']
            for index, (_size, position) in enumerate(boxes):
                lines += ["", f'[node name="Shape{index}" type="CollisionShape3D" parent="Collision/RailBody"]',
                          "position = Vector3(%s, %s, %s)" % position,
                          f'shape = SubResource("Box_{index}")']
            path.write_text("\n".join(lines) + "\n", newline="\n")
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
