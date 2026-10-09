# city_planting.02 — round planter / tree surround

Produced 9 October 2026 by the assigned city_planting.02 specialist. Source/export
production is commissioned by ROOT fbd92534-e159-432f-aae7-28072c2bf3b2; ROOT owns
queue and integration. Independent art/technical acceptance remains pending.

Original editable Blender geometry: a continuous turned cast-stone ring with a
broad softly rolled lip, slightly tapered wall, and separate recessed annular foot.
The centre is open through to the ground, suitable for a reusable tree or planting
asset at the same ground datum. No tree, shrub, soil plug or trunk is baked in.
The ring is a designed closed radial profile, not an unmodified primitive.

## References and design refinement

Read AGENTS.md, docs/assets.md, docs/art-direction.md, docs/assets/city_planting.md,
production/commission.md, district brief-contract and Signal Row asset breakdown.
Visually inspected `docs/concepts/districts-v1/06-signal-row-v03.png` and the available
`city_planting_01-evidence/hero.png`; inspected its author/export/check scripts read-only.
The existing rectangular planter's sage stone, pale rolled rim and recessed petrol
base establish the family language. This source is self-contained and does not link
to the rectangular source or depend on its completion. Shape/dimensions below are
reversible production refinements, not measurements inferred from concept imagery.
Original geometry authored locally in Blender; no external assets, paid generation,
textures, linked libraries or third-party models.

## Source and output contract

- Source: `art/source/models/environment/city_planting_02/city_planting_02.blend`.
- Collection: `export_city_planting_02`; root empty: `city_planting_02`.
- Members: `cast_stone_open_surround`, `recessed_annular_foot`.
- Output: `art/models/environment/city_planting_02/city_planting_02.glb`.
- Author/export/check/runner: `tools/asset_production/city_planting_02/`.
- No prefab, collision, placement or import metadata authored by this worker.

Metres, scale_length 1, all export object locations/rotations zero and scales one.
Ground-centred origin `(0,0,0)`; Blender +Y front/+Z up exports to Godot -Z/+Y.
Rotational symmetry makes horizontal front visually interchangeable.

| Measurement | Metres |
| --- | --- |
| Godot X/Y/Z size | 1.80 / 0.48 / 1.80 |
| Godot bounds min → max | (-0.90, 0, -0.90) → (0.90, 0.48, 0.90) |
| Clear core, conservative nominal diameter | 1.24 |
| Polygonal clear core inscribed diameter | 1.2385 (64 sides) |
| Inner lip diameter at Y 0.44 | 1.352 |
| Broad flat rim radial band at Y 0.48 | radius 0.715–0.860 |
| Foot outer diameter | 1.64 |
| Ground planting datum | Y 0 |

Keep a separate plant/root-base footprint within radius 0.60 m for at least 19 mm
radial tolerance through the narrowest faceted opening. A tree can stand on ground
through the open ring; a raised soil surface, if desired, belongs to the planting
assembly. No compatibility claim is made for unfinished tree/shrub outputs. Ring
is not a solid disc: integration must choose deliberate collision appropriate to
intended access and avoid silently filling the central opening.

Material slots: body mesh slot 0 `planter_sage_cast_stone` (#97A497, roughness .76),
slot 1 `planter_pale_stone_rim` (#BBC2AC, .70); foot slot 0 `planter_recess_petrol`
(#304948, .80). Opaque nonmetallic flat PBR, sRGB swatches converted to linear.
No UVs/maps required. Studio material, cameras and lights excluded from export.
No rigs, animations or sockets needed; plant interface is the documented datum and
clear volume. 64 radial segments preserve the smooth hero silhouette; 3,456 triangles,
two meshes and three materials. No LOD/performance budget is claimed.

## Evidence and validation

Evidence directory: `docs/assets/production/city_planting_02-evidence/`.
`commands.json` retains exact job argv, environment, exit status and raw log paths;
`version.log` records the binary. The supplied `/usr/bin/blender5.2.2LTS` path was
absent (exit 127); `/usr/bin/blender` is the exact pinned Blender 5.2.2 LTS build
`d13f752e3b9c`, with glTF exporter 5.2.40 asserted inside author/export scripts.
Private CLI processes use `-noaudio`, process-local ALSOFT_DRIVERS=null and
SDL_AUDIODRIVER=dummy, with four CPU render threads. No live connector was used.

`hero.png`: 1100×800 oblique orthographic studio view, 2.85 m frame.
`project_camera_reference.png`: 1280×800 vertical perspective, 47 m height,
42° vertical FOV, centred asset at native reference scale. These are Blender studio
previews, not engine/runtime acceptance. Studio uses Cycles 32 samples, AgX,
three broad area lights and neutral slate floor; no plant masks the cavity.

`source_export_checks.json` records bounds, topology counts, positive signed
volumes, manifold/consistent edges, nonzero face areas, finite coordinates and
identity object transforms. It also checks the clear core and records exact export
settings. `glb_checks.json` independently parses exported positions, normals,
indices/materials and checks axis-converted bounds, unit normals, nondegenerate
triangles, expected mesh/material counts and studio/animation/texture exclusion.
`reexport_checks.json` and `reexport_comparison.json` record reopening the saved
source and exporting again in a fresh process, with byte-for-byte comparison.
`manifest.json` records the exact expected deliverable set, byte counts and SHA256
fingerprints (excluding itself).

Engine import/material response, prefab and inherited save/reopen, collision,
movement/query/network checks, runtime camera visuals, device performance and
independent acceptance are integration-stage responsibilities, all pending.

Observed results: all five recorded version/author/export/GLB-check/reexport jobs
exited 0. Saved-source reexport is byte-identical: GLB 68,156 bytes, SHA256
`20eb2d5e44bd57ea6b01c15c177d9e561f775ab808170379da52b926258baa34`.
Both meshes have zero nonmanifold/inconsistently wound edges and positive signed
volume; 1,728 authored vertices / 3,456 exported triangles. No degenerate exported
triangles. Manual preview inspection confirms a continuous broad rim, smooth walls,
clear open cavity and family palette. At the native project camera the ring is
about 40 pixels wide and remains distinguishable; this is a studio observation,
not proof of planted or in-district gameplay readability.

Raw diagnostics retained without suppression: author logs a future Blender 6.0
`Material.use_nodes` deprecation and an OpenImageIO failure writing a desktop
thumbnail outside the workspace. The actual .blend and PNGs saved and reopened.
Both export logs report the optional MeshOptimizer library unavailable; uncompressed
GLB export completes and validates without that extension. The installed BlenderMCP
addon registers/unregisters during CLI startup; no connector commands were sent.
No geometry fix cycle was needed. All owned subprocesses have exited; no owned
background writer or live editor session remains.
