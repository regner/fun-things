# city_lights.01 — ordinary street pole

9 October 2026. **Source/export handoff; prefab, independent review and engine acceptance pending.**
Production commissioned by Regner; see [commission](commission.md). Family brief:
[city_lights](../city_lights.md). The earlier concept-only status is superseded by
this explicit production commission, not by an inferred concept approval.

Original model author: commissioned Codex visual/modeling specialist. Lead
150f00b5-9e62-44d8-b0aa-a456d2a88b8c owns Git, Godot import/prefab integration,
review scheduling and shared documentation. ROOT fbd92534-e159-432f-aae7-28072c2bf3b2
owns main integration. No Git or live editor operations performed by this worker.

## Design and dimensions

A quiet tapered petrol pole, flared cast foot, inset service hatch, curved arm,
broad two-part rounded lamp housing and a recessed warm/cool lens. Original Blender
construction; no downloaded geometry, textures, paid services or generated meshes
at runtime. Direction follows Petrol & Coral and the current Crescents district
concept, inspected as a style reference. Exact dimensions are authored choices,
not inferred measurements from a concept image.

- Height: 6.200 m; maximum width: 0.720 m.
- Ground foot: 0.420 m diameter, ground at zero; base flare rises to 0.320 m.
- Pole: 0.270 m lower diameter tapering to 0.132 m at arm junction.
- Lamp housing: 0.720 × 1.360 m plan, with upper canopy reaching 6.200 m.
- Lens: 0.530 × 0.900 m; inset underside near height 5.941 m.
- Godot-axis whole visual AABB: min (-0.360, 0, -1.400),
  max (0.360, 6.200, 0.210) m; size (0.720, 6.200, 1.610) m.
- Numeric acceptance tolerance: ±0.001 m for envelope and ground datum;
  GLB/source coordinate mapping comparison tolerance 0.00001 m.
- Root and mesh pivots: (0,0,0), centered on **ground-contact foot**, not the
  asymmetric lamp overhang. Blender +Y projects toward the road; maps to Godot -Z.
  Blender +Z maps to Godot +Y. Unit scale, applied rotation/scale, metre units.

Suggested integration collision is a simple upright pole envelope, radius 0.21 m,
height 5.45 m; this is a proposal, not an authored collider or gameplay acceptance.
Lamp/arm are overhead visual decoration. Keep the 1.40 m forward overhang away from
upper-level routes and preserve actors/aim lines in actual placement. No lights,
shadow budget, illumination radius or clearance behavior is claimed measured.

## Source, exports and materials

Source: `art/source/models/environment/city_lights_01/city_lights_01.blend`.
Declared collection `export_city_lights_01`; root `CityLights01`, child
`CityLights01_Mesh`. Studio camera, plane and area lights remain outside it.
Source authoring and reexport scripts live in `tools/asset_production/city_lights_01/`.

The collection exports to both:

- `art/models/environment/city_lights_01/city_lights_01_warm.glb`
- `art/models/environment/city_lights_01/city_lights_01_cool.glb`

Same geometry, four material surfaces: `pole_petrol`, `fixture_rim`,
`service_recess`, and `lens_warm` or `lens_cool`. Opaque Principled materials,
flat colors, no texture files or embedded images. Lens emission strength 0.45 is
appearance-only and creates no real light. Warm base linear RGB (0.95,0.69,0.32);
cool (0.46,0.78,0.92). Petrol (0.025,0.075,0.09), metallic 0.45, roughness 0.46.
Full exported PBR values and actual material order are in validation.json.
Godot material remapping and any light nodes remain lead-owned.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
Explicit shared `tools/s01/export_settings.json` options are loaded by the owned
export script: collection filter, GLB, Y-up, normals/UVs, no cameras/lights,
no animations/skins/morphs. Static modifiers are applied before saving; glTF
triangulates mesh faces. All geometry is editable in the saved .blend; the
construction script preserves the parametrized authoring recipe. No rig, animation,
sockets, destruction states, textures or LODs are needed for this static fixture.
No platform performance budget is ratified; repeat-placement profiling remains open.

## Evidence and reproduction

[Hero](city_lights_01-evidence/hero.png), [side](city_lights_01-evidence/side.png),
[underside detail](city_lights_01-evidence/lens_detail.png),
[47 m / 42° overhead](city_lights_01-evidence/overhead_47m_42deg.png).
These are isolated Blender renders, not Godot captures. The overhead image is
1280×800 perspective, vertical-down, with Blender +Y at image top. The small quiet
silhouette is intentional; production camera readability still needs engine review.

Commands from repository root:

```sh
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy blender -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_lights_01/author.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy blender -noaudio --background --factory-startup --threads 2 --python-exit-code 1 --python tools/asset_production/city_lights_01/validate.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy blender -noaudio --background art/source/models/environment/city_lights_01/city_lights_01.blend --threads 2 --python-exit-code 1 --python tools/asset_production/city_lights_01/export.py -- /tmp/city_lights_01_reexport
```

Raw logs retain initial arm/lens overlap correction and the subsequently discovered
78 near-zero-area bevel faces. Regner explicitly authorized one additional cleanup
pass. Coincident bevel vertices are welded at 0.000001 m, collapsed edges dissolved,
and face normals recalculated before weighted normals. Pre-cleanup hero/detail
renders and diagnostics are retained for comparison. The initial runs wrote their
outputs but emitted PipeWire/`pa_write` shutdown diagnostics; their exit status was
not established and they are not counted as successful command exits. The `-noaudio` flag alone still produced shutdown diagnostics. Final validation
and fresh reexport use `ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy` as well as
`-noaudio`; both exited 0 without timeout/termination. No unrelated processes were terminated.

Final source/export geometry: **2,424 triangles, 1,232 Blender vertices, one mesh,
four surfaces; zero degenerate faces and zero nonmanifold edges**. Unit-length
corner normals pass. Both fresh exports are byte-identical to production GLBs.
Post-cleanup visual comparison preserves silhouette, lens inset and base/hatch detail;
the arm junction remains a visible manufactured seam.

Final counts, measured bounds, mesh checks, actual GLB metadata and reproducibility
results are in `city_lights_01-evidence/validation.json`, `reproducibility.json`
and `commands.json`. `manifest.json` lists final owned artifact hashes.

## Remaining acceptance

Lead: import both GLBs with pinned Godot, retain .import identities, make linked
prefab(s), verify transforms/materials/normals/front and lens overrides, author any
intentional collider, save/reopen and inspect the saved scene. Capture actual
47 m/42° gameplay views and test collision/movement/query/multiplayer implications
if collision is added. Profile repeated placements before adding real lights.
Independent art/technical review and production acceptance remain pending. Nothing
in this record marks the register asset ready or authorizes world placement.
