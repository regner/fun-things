"""Validate the terminal assembly using the source kit's topology/export checks without editing it."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_04"
KIT = "city_quay_furniture_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence/validation.json"


def load_tool(path):
    """Load an existing asset tool without executing its production-writing entrypoint."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def main():
    """Record actual source/export counts and independent assembled envelope expectations."""
    source = ROOT / f"art/source/models/environment/{KIT}/{KIT}.blend"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    exporter = load_tool(Path(__file__).with_name("export.py"))
    exporter.main()
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    validator = load_tool(ROOT / f"tools/asset_production/{KIT}/validate.py")
    # Only the reexport lookup is redirected; all kit-owned numerical expectations stay intact.
    validator.SCRATCH = exporter.SCRATCH
    components = {name: validator.check_component(name) for name in exporter.COMPONENTS}
    minimum = [min(c["godot_bounds_min_m"][i] for c in components.values()) for i in range(3)]
    maximum = [max(c["godot_bounds_max_m"][i] for c in components.values()) for i in range(3)]
    assert all(abs(a - b) < .001 for a, b in zip(minimum, [-.16, 0, -.16]))
    assert all(abs(a - b) < .001 for a, b in zip(maximum, [.535, 1.06, .16]))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    report = {
        "asset": "city_barriers.04", "output_type": "Assembly reference",
        "blender": bpy.app.version_string, "blender_build": bpy.app.build_hash.decode(),
        "exporter": "5.2.40", "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": source_hash, "source_unchanged": True, "new_meshes": 0,
        "dimensions_provisional": True, "bounds_tolerance_m": .001,
        "components": components,
        "assembly": {"bounds_min_m": minimum, "bounds_max_m": maximum,
                     "size_m": [maximum[i] - minimum[i] for i in range(3)],
                     "ground_post_pivot_m": [0, 0, 0]},
    }
    for key in ("source_vertices", "triangles", "export_vertices", "mesh_count", "surface_count"):
        report["assembly"][key] = sum(c[key] for c in components.values())
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("CITY_BARRIERS_04_SOURCE_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
