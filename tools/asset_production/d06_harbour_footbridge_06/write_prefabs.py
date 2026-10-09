"""Create missing linked wrappers with deliberate collision, then let pinned Godot normalize them."""
from pathlib import Path
from layout import NID, VARIANTS, edges, guard_prism, prefab_suffix

ROOT = Path(__file__).resolve().parents[3]


def vector(values):
    """Serialize explicit metre coordinates without hidden model corrections."""
    return ", ".join(f"{value:.9g}" for value in values)


def main():
    """Write only missing wrappers so rerunning authoring preserves normalized UIDs/node identities."""
    for variant in VARIANTS:
        path = ROOT / f"scenes/prefabs/environment/{NID}{prefab_suffix(variant)}.tscn"
        if path.exists():
            print("Preserving", path)
            continue
        text = '[gd_scene format=3]\n\n'
        text += (f'[ext_resource type="PackedScene" path="res://art/models/environment/{NID}/'
                 f'{NID}_{variant}.glb" id="1_model"]\n\n')
        nodes = []
        if variant.startswith("support"):
            height = 5.15 if variant == "support_tall" else 2.4
            boxes = [("Foot", (0, 0.1, 0), (1.2, 0.2, 1.2)),
                     ("Collar", (0, 0.275, 0), (0.85, 0.15, 0.85)),
                     ("Pier", (0, (height+0.05)/2, 0), (0.65, height-0.65, 0.65)),
                     ("Head", (0, height-0.15, 0), (2.4, 0.3, 0.7))]
            for name, centre, size in boxes:
                text += (f'[sub_resource type="BoxShape3D" id="Shape_{name}"]\n'
                         f'size = Vector3({vector(size)})\n\n')
                nodes.append((name, centre))
        else:
            for index, (a, b, height) in enumerate(edges(variant)):
                name = f"Guard{index:02d}"
                points = [value for p in guard_prism(a, b, -0.15, height) for value in p]
                text += (f'[sub_resource type="ConvexPolygonShape3D" id="Shape_{name}"]\n'
                         'margin = 0.005\n'
                         f'points = PackedVector3Array({vector(points)})\n\n')
                nodes.append((name, (0, 0, 0)))
        text += (f'[node name="{NID}_{variant}" type="Node3D"]\n\n'
                 '[node name="Visuals" type="Node3D" parent="."]\n\n'
                 '[node name="Model" parent="Visuals" instance=ExtResource("1_model")]\n\n'
                 '[node name="Collision" type="Node3D" parent="."]\n\n'
                 '[node name="Body" type="StaticBody3D" parent="Collision"]\n'
                 'collision_layer = 1\ncollision_mask = 0\n\n')
        for name, centre in nodes:
            text += (f'[node name="{name}" type="CollisionShape3D" parent="Collision/Body"]\n'
                     f'position = Vector3({vector(centre)})\nshape = SubResource("Shape_{name}")\n\n')
        path.write_text(text, newline="\n")
        print("Created", path)


if __name__ == "__main__":
    main()
