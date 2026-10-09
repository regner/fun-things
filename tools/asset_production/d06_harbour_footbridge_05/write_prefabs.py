"""Author new linked wrappers as text; preserve existing files/IDs on later source rebuilds."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_05"


def vector(values):
    """Serialize explicit metre coordinates without hidden import corrections."""
    return ", ".join(f"{value:.9g}" for value in values)


def main():
    """Create missing wrapper files only; the pinned headless checker normalizes their identities."""
    for variant in ("main", "south", "quay"):
        suffix = "" if variant == "main" else "_" + variant
        target = ROOT / f"scenes/prefabs/environment/{NID}{suffix}.tscn"
        if target.exists():
            print("Preserving", target)
            continue
        sections = [("Upper", (-1.6, 1.6, -3.2, 0), 5.5, 5.5, "z"),
                    ("Flight1", (-1.6, 1.6, -8.32, -3.2), 2.75, 5.5, "z"),
                    ("Mid", (-1.6, 1.6, -11.52, -8.32), 2.75, 2.75, "z")]
        if variant == "main":
            sections += [("Flight2", (-1.6, 1.6, -16.64, -11.52), 0, 2.75, "z"),
                         ("Apron", (-1.6, 1.6, -19.84, -16.64), 0, 0, "z")]
            end, basis = (0, 0, -19.84), (1, 0, 0, 0, 1, 0, 0, 0, 1)
        elif variant == "south":
            sections += [("Flight2", (1.6, 6.72, -11.52, -8.32), 2.75, 0, "x"),
                         ("Apron", (6.72, 9.92, -11.52, -8.32), 0, 0, "x")]
            end, basis = (9.92, 0, -9.92), (0, 0, -1, 0, 1, 0, 1, 0, 0)
        else:
            sections += [("Flight2", (-6.72, -1.6, -11.52, -8.32), 0, 2.75, "x"),
                         ("Apron", (-9.92, -6.72, -11.52, -8.32), 0, 0, "x")]
            end, basis = (-9.92, 0, -9.92), (0, 0, 1, 0, 1, 0, -1, 0, 0)
        text = '[gd_scene format=3]\n\n'
        text += (f'[ext_resource type="PackedScene" path="res://art/models/environment/{NID}/'
                 f'{NID}_{variant}.glb" id="1_model"]\n\n')
        nodes = []
        for name, (xmin, xmax, zmin, zmax), start, end_height, axis in sections:
            if start == end_height:
                text += f'[sub_resource type="BoxShape3D" id="Shape_{name}"]\n'
                text += f'size = Vector3({vector((xmax-xmin, 0.35, zmax-zmin))})\n\n'
                centre = ((xmin+xmax)/2, start-0.175, (zmin+zmax)/2)
            else:
                points = []
                for depth in (0, -0.35):
                    for x, z in ((xmin, zmin), (xmax, zmin), (xmax, zmax), (xmin, zmax)):
                        top = (start if (z == zmin if axis == "z" else x == xmin)
                               else end_height)
                        points.extend((x, top+depth, z))
                text += f'[sub_resource type="ConvexPolygonShape3D" id="Shape_{name}"]\n'
                text += f'points = PackedVector3Array({vector(points)})\n\n'
                centre = (0, 0, 0)
            nodes.append(f'[node name="{name}" type="CollisionShape3D" parent="Collision/Body"]\n'
                         f'position = Vector3({vector(centre)})\nshape = SubResource("Shape_{name}")\n\n')
        text += (f'[node name="{NID}_{variant}" type="Node3D"]\n\n'
                 '[node name="Visuals" type="Node3D" parent="."]\n\n'
                 '[node name="Model" parent="Visuals" instance=ExtResource("1_model")]\n\n'
                 '[node name="Collision" type="Node3D" parent="."]\n\n'
                 '[node name="Body" type="StaticBody3D" parent="Collision"]\n'
                 'collision_layer = 1\ncollision_mask = 0\n\n')
        text += "".join(nodes)
        text += ('[node name="Sockets" type="Node3D" parent="."]\n\n'
                 '[node name="Incoming" type="Marker3D" parent="Sockets"]\n'
                 'transform = Transform3D(-1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 5.5, 0)\n\n'
                 '[node name="Ground" type="Marker3D" parent="Sockets"]\n'
                 f'transform = Transform3D({vector(basis + end)})\n')
        target.write_text(text, newline="\n")
        print("Created", target)


if __name__ == "__main__":
    main()
