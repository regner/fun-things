# city_roof_details.01 — broad roof vent

Produced 9 October 2026 for ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2`, workspace
`wks_59891ad7a05813e5`, branch `art/register-production-20261009`. Original production
source/export delivered; independent technical/art acceptance and all engine gates
remain **pending**. The [commission](commission.md) at
`2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661` and direct assignment supersede the old
concept-only status. Producer is this assigned per-asset Codex specialist; ROOT owns
acceptance/integration. No other asset, shared scene, index or project file was edited.

A low formed-metal rain cowl with a smooth broad crown, two rounded end cheeks,
six curved downturned louvers and a folded roof flashing/curb. Louvers are actual
separated closed solids over a recessed dark baffle, not a grille texture or a cube
fixture. The quiet silhouette and three widely spaced blades on each side preserve
building dominance. Decorative static appearance only: no roof access, traversal,
smoke, fan, light, simulation, sockets, rig or clips. Components overlap intentionally
as an assembled prop; this is not a unified watertight engineering duct or collider.

## References and original provenance

Read repository AGENTS.md, docs/assets.md, docs/art-direction.md, the family brief
[city_roof_details](../city_roof_details.md), district common contract and the
Broadlot, Ironreach, Glassward and Signal Row roof context/breakdowns. Visually
inspected `07-broadlot-v01.png` and `08-ironreach-v02.png`: sparse small service
fittings on broad quiet roofs, while steps/sawtooth/building outlines dominate.
The historical raster dimensions were not used as measurements. This record makes
reversible asset-specific production dimensions under the direct commission.

All vent geometry was originally authored in private Blender by this worker through
`author.py`; no external models, libraries, textures, image generation or paid tools.
Project-owned concept images supply style only. Existing city_planting.02 exporter,
GLB parser and runner were read and adapted inside the owned tool directory; no
shared exporter was changed. The unchanged project-owned `shop.glb` supplies measured
scale context only, without a production building claim or new copied runtime asset.

## Source, export and interface

- Editable source: `art/source/models/environment/city_roof_details_01/city_roof_details_01.blend`.
- Named collection: `export_city_roof_details_01`; root: `city_roof_details_01`.
- Explicit output: `art/models/environment/city_roof_details_01/city_roof_details_01.glb`.
- Author/export/check/preview/runner: `tools/asset_production/city_roof_details_01/`.
- Authoring collection `authoring_excluded` retains a measured 1 × 1 × 1 m reference
  cube. It is hidden from render and explicitly excluded from the exported selection.

Metric unit scale 1. Every export member has zero location/rotation and unit scale;
all mesh transforms are applied. Base-centred origin is the roof contact datum:
Blender Z=0 → Godot Y=0. Blender +Y front/+Z up converts once through exporter Y-up
to Godot -Z front/+Y up. The two louver sides are symmetric, so either long side can
face the street; no corrective integration rotation or scale is required.

| Interface or measurement | Metres / contract |
| --- | --- |
| Godot width X / height Y / depth Z | 2.60 / 0.76 / 1.60 |
| Godot AABB minimum → maximum | (-1.30, 0, -0.80) → (1.30, 0.76, 0.80) |
| Roof attachment datum | Y=0, flat annular underside of flashing |
| Maximum cowl footprint | 2.48 × 1.48; below flashing envelope |
| Cowl underside / maximum crown height | 0.565 / 0.760 |
| Raised curb outer footprint near its top | 2.24 × 1.24, easing to 2.18 × 1.18 |
| Curb top | 0.270 |
| Flashing outside edge thickness | 0.025 |
| Base inner opening | 2.02 × 1.02, 0.08 corner radius; visual assembly only |
| Louver solid width / nominal vertical pitch | 1.97 / 0.105 |
| Louver nominal profile envelope height | 0.087; 0.018 gap between blade envelopes |
| Recommended level supporting roof patch | at least 2.70 × 1.70, 0.05 surrounding margin |
| Numerical source/export dimension tolerance | ±0.001 |
| Proposed roof contact flatness tolerance | ±0.002 across contact band; not engine-tested |

Place the root on a level roof surface and retain unit scale. No roof cut is needed;
the roof remains below the dark baffle. A pitched roof needs an independently owned
level adapter: this asset supplies no arbitrary pitch correction. Leave at least
0.50 m from the flashing envelope to roof edges/parapets as an initial visual placement
rule, not a route or safety clearance. Do not populate every roof. Mounting, actual
roof material response and placement suitability await the building integrator.

## Meshes and materials

Five meshes, six exported nodes including the root, 1,788 authored vertices and
3,536 exported triangles. Eleven disconnected closed component solids, each positive
signed volume, with zero nonmanifold or inconsistently wound edges. No negative
scales, live modifiers, cameras, lights, animations, textures or stray reference nodes
in GLB. Rounded profiles and small applied three-segment edge bevels provide the
smooth form; weighted normals preserve broad faces. Five material primitives in GLB;
no LOD is supplied for this small static prop and no measured performance budget is claimed.

| Mesh | Triangles | Slot 0 |
| --- | ---: | --- |
| flashing_and_curb | 576 | roof_vent_folded_metal |
| formed_rain_cowl | 500 | roof_vent_dark_petrol |
| two_formed_end_cheeks | 376 | roof_vent_dark_petrol |
| recessed_throat_baffle | 188 | roof_vent_shadow |
| six_broad_curved_louvers | 1,896 | roof_vent_dark_petrol |

Embedded opaque single-sided PBR materials: dark petrol `#273F43` (metallic .28,
roughness .52), folded metal `#314D50` (.30/.55), shadow `#172B30` (.05/.78).
sRGB swatches are converted to linear values. No emission, alpha effects or normal
maps. Solid colors need no exported UVs/tangents; no separate material/texture files
or engine remaps were created. Any later shared material remap is integrator-owned.

## Reproduction and evidence

Run from the workspace: `python tools/asset_production/city_roof_details_01/run.py`.
The runner authors the source, reopens it to audit/export, parses GLB independently,
reopens again to scratch-export and byte-compares, then renders source-only previews.
It overwrites current owned outputs/logs; retained `initial_failure/` is immutable
historical diagnostic evidence. [commands.json](city_roof_details_01-evidence/commands.json)
contains exact argv, cwd, process-local environment, exit codes and raw log paths.
Four CPU threads, `-noaudio`, `ALSOFT_DRIVERS=null`, `SDL_AUDIODRIVER=dummy`.
The named `/usr/bin/blender5.2.2LTS` is absent (127); `/usr/bin/blender` is verified as
Blender 5.2.2 LTS build `d13f752e3b9c`; author/export assert glTF exporter 5.2.40.
No shared live editor or connector was used; no global configuration was changed.

[Source/export audit](city_roof_details_01-evidence/source_export_checks.json) checks
finite coordinates, nonzero face areas, consistent manifold edges, each component's
positive signed volume, identity transforms, expected members and metre bounds.
[GLB audit](city_roof_details_01-evidence/glb_checks.json) independently checks actual
positions/indices, finite unit normals, face-winding/normal agreement, nondegenerate
triangles, axis-converted AABB, exact node set, mesh/material counts, opaque single-sided
materials and absence of studio/light/animation/texture content. These are artifact
checks, not Godot import acceptance.

[Reexport comparison](city_roof_details_01-evidence/reexport_comparison.json) records
fresh-process export from the saved source, byte-identical at **68,384 bytes**,
SHA256 `3b868ceda54173b273618bcce39ff3da4c0ac5fb3ad3eb951dd3e504ff504d52`.
The [producer manifest](city_roof_details_01-evidence/manifest.json) is the exact
expected path/byte/SHA256 set, including this report, tools, binary outputs, previews
and all failure evidence; it excludes only itself and integrator-created files.

### Visual and unchanged scale comparison

[Hero](city_roof_details_01-evidence/hero.png) and
[louver detail](city_roof_details_01-evidence/louver_detail.png): 1200×900 perspective
studio views, Cycles CPU 32 samples/denoise, AgX, broad area lighting, slate floor.
The cowl remains smooth, the three openings on the visible side read as a sparse
horizontal rhythm, and the soft raised flashing forms a contained base interface.

[Project-camera comparison](city_roof_details_01-evidence/project_camera_roof_context.png):
1280×800, straight-down north-up perspective, 42° vertical FOV, world camera height
47 m and roof at 10 m (37 m roof-relative height). Unchanged neutral greybox shop
geometry/materials are imported read-only and translated for this temporary Blender
assembly. The existing asset remains **18 × 15 × 10 m** with unit scale; its bytes
are hashed before/after. Vent offset on the roof is Blender (3,2,0).
The 4.16 m² vent footprint occupies **1.54%** of the 270 m² roof; its height is
**7.6%** of the building height. At this camera it reads as a quiet roughly 74-pixel
wide fitting within a roughly 505-pixel wide roof. Individual side louvers are
intentionally subordinate/mostly hidden in the vertical view.

[Dark-roof color study](city_roof_details_01-evidence/project_camera_dark_roof_study.png)
uses the same geometry/camera with a temporary slate material override; it is clearly
separate from the unchanged comparison, not a modified source or accepted building.
[Oblique scale comparison](city_roof_details_01-evidence/unchanged_shop_scale_comparison.png)
retains the original shop materials and shows relative height. The
[preview receipt](city_roof_details_01-evidence/preview_checks.json) records cameras,
reference hashes/measurements, lighting, render settings and temporary transforms.
These are Blender previews, not linked prefabs, saved world placement or runtime captures.

### One owned fix cycle and complete diagnostics

Initial source geometry passed; the first GLB material assertion failed because
Blender's default exported all three closed-solid materials as double-sided.
`initial_failure/` retains original command receipts, full logs, failed GLB,
material JSON, original tool text and original previews. The one fix sets
`use_backface_culling=True`; no geometry was changed. The final GLB check and
saved-source reexport pass. Camera metadata was also made explicit and the separate
dark-roof color study was added. See [fix record](city_roof_details_01-evidence/fix_record.json).

Raw logs retain the future Blender 6.0 `use_nodes` deprecation, an OpenImageIO failure
to write a desktop thumbnail outside the writable workspace, and the optional
MeshOptimizer library warning. The source saves/reopens and uncompressed GLB export
validates; neither thumbnail nor compression is used in the deliverable. BlenderMCP
registers/unregisters as an installed startup addon; no shared connector commands
were issued. No errors are suppressed or interpreted as engine acceptance.

All owned jobs exited; no owned live editor/background writer remains. Producer checks
and source/export delivery are complete. Engine import and sidecars, linked prefab,
save/reopen, actual mounting/collision/query/runtime checks, district readability,
Deck/device/performance and independent acceptance remain later gates. No commission
completion or whole-city readiness is claimed.
