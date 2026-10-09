# city_planting.01 — low rectangular planter

2026-10-09. **Source/export complete; engine integration and independent acceptance pending.**
Original Blender author: assigned Codex specialist. Commission/queue/Git owner: ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2`; accepting engine integrator:
`150f00b5-9e62-44d8-b0aa-a456d2a88b8c`. No claim of reviewer acceptance.
Inputs: `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`; original main base
`66400c26a01bf917dfe631af4762c2b444d9c48f`.

## Delivered design and provenance

Original rounded cast-stone trough with slightly tapered broad walls, a softly rolled
pale rim, recessed petrol foot and separate quiet earth insert. No foliage is baked
into this asset: `city_planting.03/.04` remain reusable separate outputs. The
[family brief](../city_planting.md), [production commission](commission.md), accepted
[art direction](../../art-direction.md), register row and inspected
[Signal Row reference](../../concepts/districts-v1/06-signal-row-v03.png) informed
its restrained frontage/path-edge character. Dimensions below are reversible authoring
choices for this commission, not measurements inferred from the concept image.
All geometry and material values were authored here in Blender. No downloaded model,
paid generation, external textures or third-party art dependencies.

[Hero preview](city_planting_01-evidence/hero.png) ·
[Project camera reference](city_planting_01-evidence/project_camera_reference.png)

## Source/output and assembly contract

- Source: `art/source/models/environment/city_planting_01/city_planting_01.blend`.
- Collection: `export_city_planting_01`; root empty: `city_planting_01`.
- Output: `art/models/environment/city_planting_01/city_planting_01.glb` (36,544 bytes).
- Only root and three mesh children export. Studio floor, lights and both cameras
  remain editable in `studio_do_not_export` and are excluded from GLB.
- Godot/glTF AABB: min `(-1.2, 0, -0.45)`, max `(1.2, 0.6, 0.45)` metres;
  dimensions **2.40 × 0.60 × 0.90 m (X/Y/Z)**. Blender dimensions 2.40 × 0.90 × 0.60.
  Ground-centred origin; all exported local translations/rotations zero and scales one.
  Blender +Y front/+Z up maps Godot -Z front/+Y up; body is symmetric.
- Top cavity opening at Godot Y=0.60: 2.085 × 0.585 m rounded rectangle,
  corner radius 0.115 m. Narrow throat at Y=0.56: 2.05 × 0.55 m, radius 0.10 m.
  Solid cavity floor at Y=0.16; empty depth 0.44 m. Rim horizontal land about 0.14 m.
- Separate soil top at Y=0.40: 2.01 × 0.51 m, radius 0.09 m; recessed 0.20 m.
  Reserve central **1.90 × 0.40 m** rectangle for planting roots/assembly, with 0.01 m
  inset tolerance for consumers. Foliage owner may place stems at `(0, 0.40, 0)`;
  spread above rim is their envelope, not planter collision. No attachment socket
  is needed for this static insert interface. Soil can be omitted for an empty planter.
- Envelope/export tolerance: 0.001 m. No off-centre protrusions or separate hardware.
  Collision is not supplied: integrator must choose and test the appropriate solid
  planter envelope without deriving gameplay collision from decoration automatically.

## Density, materials and shading

| Mesh | Vertices | Export triangles | Material slots |
| --- | ---: | ---: | --- |
| `recessed_ground_foot` | 144 | 284 | `planter_recess_petrol` |
| `rounded_cast_trough` | 468 | 932 | `planter_sage_cast_stone`, `planter_pale_stone_rim` |
| `separate_recessed_soil_insert` | 108 | 212 | `planter_quiet_earth` |
| Total | 720 | 1,428 | Four unique materials / four export primitives |

Embedded metallic-roughness materials, metallic zero. sRGB authoring colors:
stone `#97A497` (roughness .76), rim `#BBC2AC` (.70), foot `#304948` (.80),
earth `#3F392C` (.95). Colors are converted to linear for shader inputs.
Smooth perimeter surfaces and applied weighted normals retain broad quiet highlights;
planar caps are flat. Geometry has 8 segments per 90° corner to preserve hero curvature.
Textures, UVs, tangents, rig, animation, destruction and LODs are not applicable to
this small untextured static delivery. No measured performance budget is claimed.
Materials are embedded in source/GLB, so no empty material/texture directories are needed.

## Reproduce and verify

Run from repository root with pinned `/usr/bin/blender` **5.2.2 LTS**, build
`d13f752e3b9c`, bundled glTF exporter **5.2.40**. Exporter asserts all three pins.

```bash
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy /usr/bin/blender -b -noaudio \
  art/source/models/environment/city_planting_01/city_planting_01.blend \
  --python-exit-code 1 --python tools/asset_production/city_planting_01/export.py
python tools/asset_production/city_planting_01/check_glb.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy /usr/bin/blender -b -noaudio \
  art/source/models/environment/city_planting_01/city_planting_01.blend \
  --python-exit-code 1 --python tools/asset_production/city_planting_01/export.py \
  -- /tmp/city_planting_01_reexport.glb
cmp art/models/environment/city_planting_01/city_planting_01.glb /tmp/city_planting_01_reexport.glb
```

`author.py` reconstructs the editable source and renders both previews; routine
re-exports open the saved `.blend` and never regenerate it. Construction is original;
the GLB parser/checker was adapted from the existing immutable city_lights_02 checker.
Exporter selects only declared collection members, uses +Y-up conversion and evaluated
mesh data, and includes normals/materials while excluding cameras, lights, animations,
extras, textures and tangents. Exact settings are retained in the evidence JSON.

## Actual validation and limitations

**PASS:** Three source meshes have zero nonmanifold or inconsistently wound edges,
positive signed volumes, finite coordinates and no zero-area faces. Source transform
and bounds assertions pass. Exported triangle geometry independently passes bounds,
unit normals, nondegenerate triangle and primitive/material-count checks. All exported
nodes have unit transform; studio/cameras/lights/textures/animations are absent.
Saved-source reopen and re-export are **byte-identical**, SHA256
`4a46f752ecba59975a4d01c088477eb25c372714f022d9a59f21ba60a3c12bd7`.
[Source checks](city_planting_01-evidence/source_export_checks.json),
[GLB checks](city_planting_01-evidence/glb_checks.json),
[re-export comparison](city_planting_01-evidence/reexport_comparison.json).

Both rendered previews were inspected. Hero shows a continuous broad rim, open cavity,
subdued materials and a legible recessed foot without leaf/detail noise. The project
reference is Blender Cycles, 1280×800, vertical-down perspective, 47 m height, 42°
vertical FOV, fixed yaw; projection matrix measurement confirms 42.000002°.
The planter occupies roughly 54×20 pixels centrally and retains a rim/soil distinction.
Studio lighting and ground are presentation only. This is **not** an actual runtime
capture, district placement, clearance test or device/readability acceptance.
[Camera measurement](city_planting_01-evidence/camera_checks.json).

All five retained process exits are zero (author, export, GLB check, re-export,
camera check). Raw stdout/stderr logs are preserved without suppression. Authoring
reported an unavailable desktop thumbnail cache write; source save and both PNG writes
succeeded. Exporter reported missing optional MeshOptimizer shared library; the delivered
uncompressed GLB does not use that extension. Blender emitted the `use_nodes` deprecation
notice for Blender 6.0. These environment diagnostics are retained, not presented as
asset failures. No failed geometry/export run or owned corrective cycle occurred.

**Pending with integration:** Godot import and `.import`/UID evidence; linked prefab
save/reopen; material/shading appearance in engine; collider/movement/query tests;
actual runtime-camera and foliage assembly acceptance; independent art review;
performance/device checks and world placement. No shared files, Git/index, prefab or
world scenes were changed. Authoring/export writers are quiescent at handoff.

## Exact owned deliverables

- `docs/assets/production/city_planting_01.md`
- `art/models/environment/city_planting_01/city_planting_01.glb`
- `art/source/models/environment/city_planting_01/city_planting_01.blend`
- `docs/assets/production/city_planting_01-evidence/author.exit`
- `docs/assets/production/city_planting_01-evidence/author.log`
- `docs/assets/production/city_planting_01-evidence/camera_check.exit`
- `docs/assets/production/city_planting_01-evidence/camera_check.log`
- `docs/assets/production/city_planting_01-evidence/camera_checks.json`
- `docs/assets/production/city_planting_01-evidence/export.exit`
- `docs/assets/production/city_planting_01-evidence/export.log`
- `docs/assets/production/city_planting_01-evidence/glb_check.exit`
- `docs/assets/production/city_planting_01-evidence/glb_check.log`
- `docs/assets/production/city_planting_01-evidence/glb_checks.json`
- `docs/assets/production/city_planting_01-evidence/hero.png`
- `docs/assets/production/city_planting_01-evidence/project_camera_reference.png`
- `docs/assets/production/city_planting_01-evidence/reexport.exit`
- `docs/assets/production/city_planting_01-evidence/reexport.log`
- `docs/assets/production/city_planting_01-evidence/reexport_checks.json`
- `docs/assets/production/city_planting_01-evidence/reexport_comparison.json`
- `docs/assets/production/city_planting_01-evidence/source_export_checks.json`
- `tools/asset_production/city_planting_01/author.py`
- `tools/asset_production/city_planting_01/check_glb.py`
- `tools/asset_production/city_planting_01/export.py`
