"""Check Dock Thumper source/export freshness and the owned saved asset linkage."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "art/source/models/rocket_launcher"
MODELS = ROOT / "art/models/rocket_launcher"
manifest = json.loads((SOURCE / "source_manifest.json").read_text())
assert (ROOT / "art/source/.gdignore").exists()
assert (SOURCE / manifest["source"]).stat().st_size > 100000
rows = []
fresh = Path(sys.argv[1]) if len(sys.argv) > 1 else None
for name, members in manifest["collections"].items():
    path = MODELS / (name.removeprefix("export_") + ".glb")
    raw = path.read_bytes()
    magic, version, length = struct.unpack("<III", raw[:12])
    assert magic == 0x46546C67 and version == 2 and length == len(raw)
    size, kind = struct.unpack("<II", raw[12:20])
    assert kind == 0x4E4F534A
    gltf = json.loads(raw[20:20+size])
    assert not gltf.get("images") and not gltf.get("textures")
    assert not gltf.get("animations") and not gltf.get("skins")
    assert not gltf.get("extensionsRequired")
    node_names = {node["name"] for node in gltf["nodes"]}
    # Godot sanitizes punctuation on import; the source/export member trail is exact here.
    assert {member["name"] for member in members} <= node_names
    assert all("uri" not in buf for buf in gltf["buffers"])
    assert path.with_suffix(".glb.import").exists()
    if fresh:
        assert raw == (fresh / path.name).read_bytes(), f"Stale output: {path}"
    geometry = [row for row in members if row["type"] == "MESH"]
    mins = [min(row["aabb_godot_min"][i] for row in geometry) for i in range(3)]
    maxs = [max(row["aabb_godot_max"][i] for row in geometry) for i in range(3)]
    rows.append({"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(raw).hexdigest(),
                 "members": len(members), "triangles": sum(row["triangles"] for row in geometry),
                 "aabb_min": mins, "aabb_max": maxs,
                 "sockets": [row for row in members if row["type"] == "EMPTY"]})
for path in list((ROOT / "scenes/prefabs/rocket_launcher").glob("*.tscn")) + list(
        (ROOT / "tests/fixtures/rocket_launcher").glob("*.tscn")):
    text = path.read_text()
    assert 'uid="uid://' in text and "unique_id=" in text
    assert "ArrayMesh" not in text and "PrimitiveMesh" not in text
    assert "Collision" not in text and "RigidBody" not in text
    for reference in re.findall(r'path="res://([^\"]+)"', text):
        assert (ROOT / reference).exists(), reference
result = {"blender": manifest["blender"], "build": manifest["build"],
          "source_sha256": hashlib.sha256((SOURCE / manifest["source"]).read_bytes()).hexdigest(),
          "fresh_byte_comparison": bool(fresh), "outputs": rows}
print(json.dumps(result, indent=2))
