"""Reexport the saved source, without recreating geometry; compare every explicit GLB."""
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[5]
SOURCE = Path(__file__).with_name("weapon_effects_a.blend")
KINDS = ("muzzle_drop", "fire_lobe", "smoke_puff", "spark", "chip", "trail_puff")


def main():
    """Export to caller-supplied scratch storage and fail if source and delivery differ."""
    assert bpy.app.version_string == "5.2.2 LTS"
    assert Path(bpy.data.filepath).resolve() == SOURCE.resolve()
    output = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    assert not output.is_relative_to(ROOT / "art/models")
    output.mkdir(parents=True, exist_ok=True)
    preset = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
    records = []
    for kind in KINDS:
        name = "weapon_effects_a_" + kind
        target = output / (name + ".glb")
        bpy.ops.export_scene.gltf(**dict(
            preset, collection="export_" + name, export_animations=False, filepath=str(target)))
        reference = ROOT / "art/models/effects/weapon_effects" / target.name
        assert target.read_bytes() == reference.read_bytes(), name + " is stale"
        records.append({"file": target.name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    receipt = {"blender": bpy.app.version_string, "source_sha256": hashlib.sha256(
        SOURCE.read_bytes()).hexdigest(), "byte_identical_exports": records}
    (output / "reexport.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("WEAPON_EFFECTS_REEXPORT_PASS", len(records))


if __name__ == "__main__":
    main()
