"""Run the existing drum audit read-only, redirecting its evidence and reexport to this ID."""
import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
OWNER = ROOT / "tools/asset_production/d06_poster_drum_01/validate.py"
DEPENDENCIES = [
    "art/source/models/environment/d06_poster_drum_01/d06_poster_drum_01.blend",
    "art/models/environment/d06_poster_drum_01/d06_poster_drum_01.glb",
    "art/models/environment/d06_poster_drum_01/d06_poster_drum_01.glb.import",
    "scenes/prefabs/environment/d06_poster_drum_01.tscn",
    "tools/asset_production/d06_poster_drum_01/validate.py",
    "tools/asset_production/d06_poster_drum_01/export.py",
    "tools/asset_production/d06_commercial_graphics_01/author.py",
    "tools/asset_production/d06_commercial_graphics_02/author.py",
    "tools/asset_production/d06_commercial_graphics_01/manifest.py",
]


def dependency_hashes():
    """Record all reused hardware and art-tool dependencies without modifying them."""
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in DEPENDENCIES}


def main():
    """Keep the owner's validation assertions intact and change only its output destinations."""
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    before = dependency_hashes()
    # The existing audit is a top-level script, not a parameterized callable. Redirect
    # exactly its two output assignments in memory; __file__ still locates its exporter.
    code = OWNER.read_text()
    redirects = {
        'EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"':
            f'EVIDENCE = Path({str(SCRATCH)!r})',
        'SCRATCH = Path("C:/tmp/ft/assets") / NID / "reexport"':
            f'SCRATCH = Path({str(SCRATCH / "reexport")!r})',
    }
    for old, new in redirects.items():
        assert code.count(old) == 1, "Shared audit output API changed; inspect before updating"
        code = code.replace(old, new)
    exec(compile(code, str(OWNER), "exec"), {"__file__": str(OWNER), "__name__": "__main__"})
    assert dependency_hashes() == before
    # Independently verify that the real saved loop UVs place the repeated panels at
    # front and rear, and that their vertical image orientation is upright.
    mesh = bpy.data.objects["D06PosterDrum01_Body"].data
    samples = {"rear": 0, "front": 0, "bottom": 0, "top": 0}
    for face in mesh.polygons:
        if face.material_index != 1:
            continue
        for index in face.loop_indices:
            u, v = mesh.uv_layers.active.data[index].uv
            point = mesh.vertices[mesh.loops[index].vertex_index].co
            if abs(u) < 1e-6 or abs(u - 1) < 1e-6:
                assert abs(point.x) < 1e-6 and abs(point.y + 0.397) < 1e-6
                samples["rear"] += 1
            if abs(u - 0.5) < 1e-6:
                assert abs(point.x) < 1e-6 and abs(point.y - 0.397) < 1e-6
                samples["front"] += 1
            assert abs(point.z - (0.24 if v == 0 else 1.28)) < 1e-6
            assert v in (0, 1)
            samples["bottom" if v == 0 else "top"] += 1
    assert samples == {"rear": 4, "front": 4, "bottom": 128, "top": 128}
    report = json.loads((SCRATCH / "validation.json").read_text())
    report.update({
        "asset_id": "d06_commercial_graphics.03", "new_geometry": False,
        "shared_dependencies_unchanged": True, "shared_dependency_sha256": before,
        "source_audit": "Unmodified owner assertions; only output destinations redirected",
        "independent_wrap_uv_orientation_samples": samples,
        "texture_dimensions": [2400, 1000], "variants": ["last_call", "small_prices"],
        "status": "PASS: bounded source/export audit; independent review pending",
    })
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("POSTER_WRAP_SOURCE_PASS: shared source unchanged; exact GLB reexport")


if __name__ == "__main__":
    main()
