#!/usr/bin/env python3
"""Author the saved S13 crowd composition; runtime only configures presentation state."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "tests/fixtures/s13/crowd.tscn"


def instance(name, parent, index, position, visible, dead=False):
    """Serialize one linked character instance with saved placement and palette choice."""
    palette = ["2_ivory", "3_coral", "4_cobalt"][index % 3]
    lines = [
        f'[node name="{name}" parent="{parent}" instance=ExtResource("1_character")]',
        f"position = Vector3({position[0]:.3f}, 0, {position[1]:.3f})",
        f"rotation = Vector3(0, {(index % 8) * 0.392699:.6f}, 0)",
        f'palette_material = ExtResource("{palette}")',
    ]
    if not visible:
        lines.append("benchmark_visible = false")
    if dead:
        lines.append("start_at_death_final = true")
    return "\n".join(lines) + "\n"


def main():
    """Write 68 live placements (~30 in-frustum) and 16 visible corpse placements."""
    central = [((column - 2.5) * 5.3, (row - 2.0) * 5.2)
               for row in range(5) for column in range(6)]
    outside = []
    for row in range(10):
        outside.append((-39.0, -27.0 + row * 6.0))
        outside.append((39.0, -27.0 + row * 6.0))
    for column in range(9):
        outside.append((-28.0 + column * 7.0, -27.0))
        outside.append((-28.0 + column * 7.0, 27.0))
    live_positions = central + outside
    if len(live_positions) != 68:
        raise RuntimeError("live placement count changed")
    dead_positions = [((-3.75 + (index % 8)) * 4.4, -15.0 + (index // 8) * 30.0)
                      for index in range(16)]
    header = '''[gd_scene format=3 uid="uid://dkxl1syi8j63v"]\n\n[ext_resource type="PackedScene" uid="uid://c0nx7h52ncu3s" path="res://tests/fixtures/s13/character.tscn" id="1_character"]\n[ext_resource type="Material" uid="uid://cpn5btw27n5po" path="res://art/materials/s13_ivory.tres" id="2_ivory"]\n[ext_resource type="Material" uid="uid://ifrqwtgl6wbu" path="res://art/materials/s13_coral.tres" id="3_coral"]\n[ext_resource type="Material" uid="uid://c5avi4m8s2fj3" path="res://art/materials/s13_cobalt.tres" id="4_cobalt"]\n[ext_resource type="Script" uid="uid://cfusvfgwkjmkt" path="res://tests/fixtures/s13/benchmark.gd" id="5_benchmark"]\n\n[sub_resource type="Environment" id="Environment_s13"]\nbackground_mode = 1\nbackground_color = Color(0.0705882, 0.211765, 0.27451, 1)\nambient_light_source = 3\nambient_light_color = Color(1, 1, 1, 1)\nambient_light_energy = 0.7\n\n[node name="S13Crowd" type="Node3D"]\nscript = ExtResource("5_benchmark")\n\n[node name="Live" type="Node3D" parent="."]\n\n'''
    content = header
    for index, position in enumerate(live_positions):
        content += instance(f"Live{index:02d}", "Live", index, position, index < 30)
        content += "\n"
    content += '[node name="Dead" type="Node3D" parent="."]\n\n'
    for index, position in enumerate(dead_positions):
        content += instance(f"Dead{index:02d}", "Dead", index, position, False, True)
        content += "\n"
    content += '''[node name="Camera" type="Camera3D" parent="."]\ntransform = Transform3D(1, 0, 0, 0, -4.371139e-08, 1, 0, -1, -4.371139e-08, 0, 47, 0)\ncurrent = true\nfov = 42.0\nnear = 0.1\nfar = 160.0\n\n[node name="Sun" type="DirectionalLight3D" parent="."]\ntransform = Transform3D(0.8660254, 0.43301272, -0.24999999, 0, 0.49999997, 0.86602545, 0.5, -0.75, 0.43301266, 0, 0, 0)\nlight_energy = 1.2\nshadow_enabled = true\n\n[node name="Environment" type="WorldEnvironment" parent="."]\nenvironment = SubResource("Environment_s13")\n'''
    TARGET.write_text(content, newline="\n")
    print(f"S13_FIXTURE {TARGET} live=68 visible_live=30 dead=16")


if __name__ == "__main__":
    main()
