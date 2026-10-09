# city_planting.03 — low shrub cluster

9 October 2026. **Source/export complete; integration and independent acceptance pending.**
Producer: assigned city_planting.03 Codex specialist. ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2` owns queue/integration; supplied input baseline
`2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`. No READY or reviewer-acceptance claim.

Original five-mass shrub, with an asymmetric broad centre, lower side crowns and
small front/back shoulders. Smooth quiet jade/sage shading replaces individual
leaves. Tapered lower foliage conceals most of three short woody stems. This is
static decorative planting: no wind, growth, tree, soil, planter or collision is
included. Low height and restrained footprint support street scale; placement must
still keep walking routes and overhead actor sightlines clear.

Inputs read: AGENTS.md, assets/art-direction/family briefs, immutable production
commission, district common contract, Signal Row breakdown, completed planter .01/.02
reports and local export/check approaches. Visually inspected Signal Row v03 and
rectangular-planter hero. Commission overrides the older concept-only wording.
Geometry and colors are original local Blender authorship, with no downloaded art,
textures, paid generators or linked libraries. Export/check/runner patterns adapt
local city_planting_02 scripts read-only. No generated concept is used as mesh data.

## Source and interface

- Editable source: `art/source/models/environment/city_planting_03/city_planting_03.blend`.
- Collection `export_city_planting_03`; root `city_planting_03`.
- Explicit GLB: `art/models/environment/city_planting_03/city_planting_03.glb`.
- Tools: `tools/asset_production/city_planting_03/`.
- Complete evidence: `docs/assets/production/city_planting_03-evidence/`.
- `manifest.json` in that evidence directory enumerates exact producer paths, bytes
  and SHA256 for all deliverables except the manifest itself, including initial failure.

Metres, Metric unit scale 1; all seven export objects have identity local transforms.
Origin is the central planting ground datum. Blender +Y front/+Z up maps to Godot
-Z/+Y. Slight asymmetry around that pivot is deliberate, not an axis correction.

| Measurement in Godot local axes | Metres |
| --- | --- |
| AABB minimum | (-0.543030, 0, -0.356221) |
| AABB maximum | (0.540500, 0.670000, 0.334672) |
| X/Y/Z size | 1.083529 / 0.670000 / 0.690894 |
| Foliage lowest point | 0.035 |
| Conservative whole-shrub horizontal radius | <0.60 |
| Below local Y=0.20, conservative X/Z envelope | 0.92 × 0.36 |

Tolerance 0.001 m for exported bounds. These are reversible authoring refinements,
not dimensions inferred from the district image. No model sockets are necessary.

**Rectangular planter .01:** set shrub pivot to planter-local Godot `(0,0.40,0)`
on its soil. Lower foliage fits the reserved 1.90 × 0.40 m planting rectangle up
to the 0.60 m rim. Triangle-edge intersections with the local 0.20 m rim plane are
checked, including triangulation diagonals; measured below-plane Blender bounds
are (-0.409115,-0.154442,0) to (0.417154,0.166360,0.20).
Two repeated shrubs at X=-0.48/+0.48 m, Y=0.40 m also fit that reserved rectangle;
small crown overlap is intentional. Assembled top height is 1.07 m. Foliage above
the rim overhangs the opening but stays within the planter's outer 0.90 m depth.

**Round planter .02:** one shrub at the common ground pivot fits within radius
0.60 m through the conservative 1.2385 m inscribed clear opening. Crown top is
0.67 m, 0.19 m above the 0.48 m rim. The open ring intentionally has no soil plug;
the studio ground supplies its base. A later raised soil assembly must explicitly
recheck foliage clearance rather than lifting the shrub arbitrarily.

These checks establish model-space compatibility, not prefab collision or runtime
clearance. Foliage stays separate from gameplay collision; no collider suffixes,
physics, navigation or automatic collision generation is supplied.

## Geometry and materials

Six meshes, six export primitives, three unique embedded opaque PBR materials.
Five crown meshes each have 482 vertices / 960 triangles; the combined three-stem
mesh has 72 vertices / 132 triangles. Total **2,482 source vertices / 4,932 triangles**.
Separate overlapping closed crown shells preserve simple editable masses and broad
shading; intentional inter-mass intersections are not a Boolean watertight union.
No modifiers, UVs, textures, tangents, rig, animation, LOD or external material files
are needed for this static color-only delivery. Performance acceptance is pending.

| Mesh slot 0 | sRGB color | Roughness |
| --- | --- | --- |
| `shrub_quiet_jade` — west, centre, front shoulder | #42694A | .87 |
| `shrub_muted_sage` — east, back shoulder | #56774E | .86 |
| `shrub_woody_umber` — three recessed stems | #4C422D | .94 |

Colors are converted to linear shader inputs, metallic zero. Materials currently
export double-sided (Blender default); no leaf cards or transparency are present.
Studio floor/material/cameras/lights are excluded from the GLB.

## Validation and reproduction

Private `/usr/bin/blender` is pinned 5.2.2 LTS, build `d13f752e3b9c`, with glTF
exporter 5.2.40 asserted in author/export scripts. The named alternate path
`/usr/bin/blender5.2.2LTS` is absent; the installed executable is the exact authorized
build. Processes use `-noaudio`, four threads, and only process-local
`ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy`. No live editor or connector was driven.

From repository root:

```bash
python tools/asset_production/city_planting_03/run.py
python tools/asset_production/city_planting_03/manifest.py
```

The runner authors the source and previews, opens the saved source in a new process
for export, independently parses the GLB, reopens the saved source again for scratch
export, compares bytes, and renders read-only planter assembly references. For
routine export without regenerating source:

```bash
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy /usr/bin/blender -b -noaudio -t 4 \
  art/source/models/environment/city_planting_03/city_planting_03.blend \
  --python-exit-code 1 --python tools/asset_production/city_planting_03/export.py
python tools/asset_production/city_planting_03/check_glb.py
```

`commands.json` retains exact process argv, local environment and exits with complete
raw logs. `source_export_checks.json` verifies finite geometry, nondegenerate faces,
consistent manifold edges, positive signed volumes, transforms, bounds, planter
interface and exact export settings. `glb_checks.json` checks actual binary positions,
unit normals, nondegenerate indexed triangles, axis-converted bounds, material/mesh
counts and exact seven-node membership, excluding studio/animation/texture content.
`reexport_comparison.json` confirms saved-source reexport is byte-identical:
**70,556 bytes**, SHA256
`572bb17a248b686df1917181e569b04a3662fbd6994de230dc8b17cd634cb7cd`.

One meaningful owned correction was made. Initial export rejected a crown below the
intended 0.22 m foliage clearance (exit 1); initial hero also exposed too much stem.
The revised lower foliage now forms tapered skirts, with the actual below-rim
profile tested instead of requiring all foliage above the rim. Initial source,
scripts, previews, full author/export logs and process ledger are preserved under
`initial_attempt/`. Final source/export/GLB/reexport checks pass.

Retained environment diagnostics: `Material.use_nodes` future deprecation;
OpenImageIO cannot write an external desktop thumbnail (actual source/PNGs save);
optional MeshOptimizer library is unavailable (uncompressed GLB export passes).
Installed BlenderMCP addon startup/shutdown messages do not indicate connector use.

## Visual evidence and remaining gates

[Hero](city_planting_03-evidence/hero.png) is 1100×800, oblique orthographic 1.8 m
frame. [Native camera](city_planting_03-evidence/project_camera_reference.png) is
1280×800, vertical-down perspective, 47 m height / 42° vertical FOV. The shrub reads
as a quiet cluster about 24 pixels wide; individual stems are not meaningful at
that scale. It remains low and does not create a tree-canopy-sized occluding area.
These observations do not prove actor visibility in actual streets.

[Planter fit](city_planting_03-evidence/planter_fit_studio.png) and
[planter camera](city_planting_03-evidence/planter_fit_project_camera.png) reuse .01/.02
GLBs read-only; no shared asset or prefab was saved. Assembly script asserts actual
camera frame vertical FOV and zero tilt. Rendering uses Cycles 32 samples, AgX,
three broad area lights, neutral slate floor; this is Blender studio evidence.

Godot import/UID metadata, linked prefab and inherited save/reopen, collision,
movement/query/network behavior, actual runtime camera/material/actor visibility,
device performance and clean-context independent technical/art review remain pending.
No project, prefab, world, shared docs, other assets or Git/index writes were made.
All owned authoring/export/render subprocesses are stopped at final handoff.
