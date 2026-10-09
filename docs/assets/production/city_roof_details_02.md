# city_roof_details.02 — compact mechanical-plant enclosure

9 October 2026. **Original editable source and explicit GLB delivered; independent
acceptance and engine stages pending.** Produced by assigned specialist
`1cfcd098-b913-488f-aa0a-80181e160534`, verified `gpt-6-astra` / effective **medium**
([receipt](city_roof_details_02-evidence/runtime_receipt.json)). ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2` owns dispatch/integration, workspace
`wks_59891ad7a05813e5`, branch `art/register-production-20261009`.
The [commission](commission.md), dispatched at `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`,
and direct assignment supersede historical concept-only restrictions.

A low, broad dark enclosure with a smooth shouldered cover, six formed louvers in
two sparse intake panels, a fixed service panel/latch, and a continuous folded
flashing/raised curb. All visible geometry is original Blender-authored editable
mesh; no external model, texture, paid generation or borrowed production mesh.
Static decoration only; no foliage, roof access, traversal, fan, smoke, simulation,
rig, clips, sockets or collision. Closed manufactured components intentionally overlap;
they are not an engineering ventilation simulation or unified collision solid.

## Sources, references and reproduction

- [Editable Blender source](../../../art/source/models/environment/city_roof_details_02/city_roof_details_02.blend).
- [Explicit game GLB](../../../art/models/environment/city_roof_details_02/city_roof_details_02.glb).
- Export collection `export_city_roof_details_02`, root `city_roof_details_02`.
- [Owned author/export/audit/preview tools](../../../tools/asset_production/city_roof_details_02/).
- [Exact expected path/bytes/SHA256 manifest](city_roof_details_02-evidence/manifest.json),
  excluding itself and integrator-owned `.import` sidecars.

Read AGENTS.md, assets workflow, art direction, roof family brief, district common
contract, approved identities, Glassward/Ironreach/Northpoint concepts. Visually
inspected the accepted roof-shape sheet and Glassward v01: broad quiet roofs and
sparse subordinate equipment. [Input hashes](city_roof_details_02-evidence/input_references.json)
retain references and reused tool provenance. Numerical dimensions below are reversible
production proposals, never measured from concept images. Read-only `.01` helper,
export/check/preview methods were adapted into owned scripts; no dependency on `.01`
source, export or unfinished work. Project-owned `shop.glb` is temporary scale context.

From the workspace root:

```sh
python tools/asset_production/city_roof_details_02/run.py
python tools/asset_production/city_roof_details_02/manifest.py
```

Runner saves source, audits/exports, parses GLB independently, reopens saved source in
a fresh Blender process, reexports, compares bytes and renders five previews. Re-running
overwrites final logs/previews, leaving `initial_failure/` intact. Private installed
`/usr/bin/blender` is verified **5.2.2 LTS / d13f752e3b9c / glTF 5.2.40**; requested
`/usr/bin/blender5.2.2LTS` is absent (retained exit 127). All jobs use process-local
`ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy`, `-b -noaudio -t 4`; no global configuration
or shared live editor was used. Exact commands and exits are in
[commands.json](city_roof_details_02-evidence/commands.json).

## Metres, axes and mounting interface

Metric unit scale 1; export members have zero location/rotation and unit scale,
with applied bevels/transforms. Root is centred on the roof-contact footprint at
Blender Z=0. Service-panel face is Blender +Y; single exporter conversion maps it
to Godot -Z, with +Z up → +Y up. No corrective root scale/rotation is needed.
`authoring_excluded` retains an actual measured 1 × 1 × 1 m reference, hidden from
render and absent from GLB.

| Measurement/interface | Metres |
| --- | --- |
| Godot width X / height Y / depth Z | 3.20 / 1.55 / 2.20 |
| Godot AABB min → max | (-1.60, 0, -1.10) → (1.60, 1.55, 1.10) |
| Flashing outside edge thickness | 0.030 |
| Base inner opening / corner radius | 2.68 × 1.68 / 0.11 |
| Raised curb maximum height | 0.270 |
| Main body maximum footprint | 2.90 × 1.90 |
| Rain cover maximum footprint | 2.98 × 1.98 |
| Front / rear blade width | 1.58 / 2.24 |
| Blade vertical pitch / profile height | 0.240 / 0.095 |
| Service panel width / height | 0.61 / 0.78 |
| Proposed level supporting roof patch | ≥3.30 × 2.30 |
| Source/export dimensional tolerance | ±0.001 |
| Proposed contact flatness tolerance | ±0.002 |

Root sits on a level roof, with no roof cut required. Base flashing contains every
part's horizontal extent. Initial placement proposal: retain 0.50 m from its envelope
to roof edges/parapets; this is a visual margin, not traversal/safety acceptance.
Pitched roofs require a separately owned level adapter. Sparse reuse, not every roof.
Actual mounting/material response remains the integrator's gate.

## Geometry and materials

Nine meshes / ten nodes / nine material primitives, **3,132 source vertices and
6,180 GLB triangles**, 22 closed component solids. Each has positive signed volume;
zero nonmanifold or inconsistent edges. No LOD is supplied; these counts are not a
ratified device/performance budget. Every mesh uses slot 0:

| Mesh | Triangles | Material suffix (`roof_plant_`) |
| --- | ---: | --- |
| flashing_and_curb | 576 | folded_metal |
| formed_enclosure_body | 356 | dark_petrol |
| swept_rain_cover | 428 | folded_metal |
| intake_shadow_panels | 376 | shadow |
| intake_frames | 1,504 | dark_petrol |
| six_formed_louvers | 2,376 | dark_petrol |
| service_panel_gasket | 188 | shadow |
| service_panel | 188 | dark_petrol |
| service_latch | 188 | folded_metal |

Three embedded opaque single-sided PBR materials: dark petrol `#273F43`, metallic
.28/roughness .52; folded metal `#314D50`, .30/.55; shadow `#172B30`, .05/.78.
sRGB is converted to linear. No textures, UV requirement, normal maps, emission or
alpha effects. No external material files are needed for this flat-color source;
Godot remapping remains later integration work.

## Evidence and outcomes

[Source audit](city_roof_details_02-evidence/source_export_checks.json) checks exact
membership, metric units, applied transforms, finite coordinates, nonzero polygon
areas, manifold/contiguous edges, per-component positive volume, reference exclusion
and bounds. [Independent GLB parser](city_roof_details_02-evidence/glb_checks.json)
checks actual position/normal/index payloads, nondegenerate triangles, unit normals,
face-winding/normal agreement, triangle count, axis-converted bounds, node/material
counts, opaque single-sided surfaces and absence of studio, images, animation and lights.

[Saved-source reexport](city_roof_details_02-evidence/reexport_comparison.json) is byte
identical: **116,664 bytes**, SHA256
`18d0ede1099abed3b84b1a8d0f983441aa53f7b0d99e9893b4d4ff430ba24b35`.
Author/export/parser/reexport/preview final commands all exit 0.

[Hero](city_roof_details_02-evidence/hero.png),
[service/louver detail](city_roof_details_02-evidence/louver_detail.png),
[project camera](city_roof_details_02-evidence/project_camera_roof_context.png),
[dark-roof study](city_roof_details_02-evidence/project_camera_dark_roof_study.png),
and [unchanged shop comparison](city_roof_details_02-evidence/unchanged_shop_scale_comparison.png)
retain Blender-only appearance evidence. Hero shows broad smooth shoulders, purposeful
service interfaces and a clear mounting skirt. At the calibrated vertical camera,
the enclosure is approximately 90 pixels wide against a roughly 505-pixel roof;
side interfaces mostly disappear, as expected. Building outline remains stronger.

[Preview receipt](city_roof_details_02-evidence/preview_checks.json): 1280×800 vertical-down
perspective, north-up, 42° vertical FOV, world camera height 47 m, 10 m shop roof
(37 m roof-relative camera height). Unchanged shop is 18 × 15 × 10 m, unit scale,
bytes hashed before/after; only temporary translation is applied. Enclosure footprint
is **2.61%** of roof area and height **15.5%** of building height. Dark-roof study alone
uses a temporary material override. Cycles CPU, four threads, 32 samples, denoise,
AgX; exact cameras/lighting in preview script. No assembly was saved as world placement.

## One fix cycle, retained diagnostics and remaining gates

Initial source audit failed on zero-area faces where opposing bevels met across thin
panels. The [complete failed source/logs/tools/face coordinates](city_roof_details_02-evidence/initial_failure/)
are retained. One fix limits box bevel width to 40% of its smallest dimension;
no checks were weakened. All affected source/export/visual checks reran. See
[fix record](city_roof_details_02-evidence/fix_record.json).

Raw logs retain all diagnostics: future Blender 6.0 `use_nodes` deprecations; denied
external desktop-thumbnail write (source save/reopen succeeds); unavailable optional
MeshOptimizer library (uncompressed GLB validates); version-only shutdown reports
one 0.000023 MB unfreed allocation. Installed BlenderMCP registers/unregisters at
startup, but no shared connector was called. These are distinguished from the owned
geometry defect, which was corrected; errors were not suppressed.

All owned jobs have exited; no owned writer/editor remains. Shared project, prefab,
world, index and frozen six-asset candidate files were not written. Producer artifact
checks are complete; **Godot import/sidecars, linked prefab, save/reopen, mounting,
collision/query/runtime, device/performance, district acceptance and independent
technical/art acceptance remain pending**. No READY claim. Available for concrete
review findings within the assigned paths.
