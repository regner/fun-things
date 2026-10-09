# city_lights.02 — short pedestrian fixture

9 October 2026. **Source/export complete; prefab, independent review and engine acceptance pending.**
Production commission: [commission](commission.md), user specialist task and lead adoption at
`2a0fe4f`. This supersedes the family brief's historical concept-only restriction for this
member. Producer: commissioned Codex modeling specialist. Technical integration/review owner:
lead `150f00b5-9e62-44d8-b0aa-a456d2a88b8c`; overall integration ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2`. No acceptance by another reviewer is claimed.

## Design and measured contract

Original smooth stylized pedestrian lantern for districts 01–08. A shallow, rounded
0.72 m canopy shelters a broad continuous diffuser, layered lower shield and tapered neck.
The quiet tapered pole terminates in a flared casting; a small dark service cover marks
front. Petrol metal and warm/cool lenses follow [city lights](../city_lights.md),
[Petrol & Coral](../../art-direction.md) and the inspected
[Crescents v02](../../concepts/districts-v1/02-the-crescents-v02.png) district reference.
Dimensions are deliberate production choices, not measurements inferred from concept pixels.

| Property | Contract |
| --- | --- |
| Godot dimensions X/Y/Z | 0.720 / 3.000 / 0.720 m; ±0.001 m export tolerance |
| Godot-axis AABB min | (-0.360, 0.000, -0.360) m |
| Godot-axis AABB max | (0.360, 3.000, 0.360) m |
| Origin | Ground-centred (0,0,0), centred under pole and complete footprint |
| Base | 0.270 m maximum diameter, 0.340 m casting height |
| Pole | 0.124 m lower diameter tapering to 0.094 m upper diameter |
| Canopy | 0.720 m diameter; top at 3.000 m |
| Head clearance | Broad head starts at 2.630 m; canopy overhang 0.360 m radius |
| Front/up | Blender +Y/+Z → glTF/Godot -Z/+Y; service cover on front |
| Transform | Metric scale 1; static rotation/scale applied; export root identity |

Recorded bounds are measured from both source vertices and decoded GLB positions with node
translations. Float deviation is about 1.4e-8 m. This is an export-axis check, not a Godot
import observation. No collider, socket, rig, animation, destruction state or gameplay
behavior is supplied. Lead must decide collision separately and verify walk clearance.

## Sources, outputs and reproducibility

- Editable source: `art/source/models/environment/city_lights_02/city_lights_02.blend`.
- Declared collection: `export_city_lights_02`; root: `city_lights_02`.
- Warm output: `art/models/environment/city_lights_02/city_lights_02.glb`.
- Cool output: `art/models/environment/city_lights_02/city_lights_02_cool.glb`.
- Construction: `tools/asset_production/city_lights_02/author.py`.
- Saved-source reexport: `tools/asset_production/city_lights_02/export.py`.
- Independent payload checks: `tools/asset_production/city_lights_02/check_glb.py`.

Source default is warm; both lens materials are retained in the source with fake users.
Reexport switches only the diffuser's material, exports each variant, then restores warm.
The source remains editable separate named closed components. No linked libraries, external
textures, downloaded meshes, network generators or paid APIs were used. Original geometry
and palette materials were authored by Codex in Blender for this commission; no third-party
asset attribution is needed. District images were visual references only.

Pinned tool observed: `/usr/bin/blender`, **5.2.2 LTS**, build `d13f752e3b9c`;
glTF exporter **5.2.40**. Collection members are explicitly selected by the export script;
Y-up conversion is applied once. Export includes evaluated mesh normals/materials, excludes
cameras/lights/animation/extras/UV/tangents. Exact options, source members, hashes and counts:
[source checks](city_lights_02-evidence/source_export_checks.json).
Studio camera, lighting and floor remain outside export collection. The authoring script
also specifies reproducible detail-camera and cool-variant render settings.

```bash
blender --background --factory-startup --threads 6 --python tools/asset_production/city_lights_02/author.py
blender -noaudio --background --factory-startup --threads 2 art/source/models/environment/city_lights_02/city_lights_02.blend --python tools/asset_production/city_lights_02/export.py
python tools/asset_production/city_lights_02/check_glb.py
```

Use the reexport command for existing sources; construction deliberately rebuilds this
asset and is not the normal update workflow. No Git/index/shared docs/prefab/world files
were changed by this specialist.

## Materials and geometry

Each variant has eight mesh components, eight primitives and three used materials.
Each component uses slot 0; only `broad_recessed_diffuser` changes between variants.
`crown_seal` and `front_service_panel` use recess dark; all other parts use petrol metal.

| Stable material | sRGB reference | Metallic / roughness | Emission strength |
| --- | --- | --- | --- |
| `city_lights_02_petrol_metal` | #193F46 | 0.55 / 0.38 | 0 |
| `city_lights_02_recess_dark` | #0D1D22 | 0.30 / 0.38 | 0 |
| `city_lights_02_lens_warm` | #FFDCA3 | 0 / 0.55 | 0.45 |
| `city_lights_02_lens_cool` | #ACDEEF | 0 / 0.55 | 0.45 |

Opaque PBR, embedded glTF materials, no alpha/texture dependencies. Colors are converted
from sRGB to linear in the authoring code. Lens emission is a conservative appearance
input, not measured lighting. No real lights are exported. Lead owns any Godot material
remap and final emission/bloom tuning.

3,616 exported triangles per variant. Radial parts use 32 segments for base/pole and 48
for the head, preserving smooth silhouettes and broad bevel highlights. No explicit LOD
is supplied: lead should evaluate Godot import LOD and repeated-placement draw cost.
Eight surfaces are disclosed; no performance acceptance is implied.

## Evidence and remaining acceptance

Actual isolated Cycles renders, visually inspected by producer:

- [Warm three-quarter](city_lights_02-evidence/warm_three_quarter.png)
- [Cool three-quarter](city_lights_02-evidence/cool_three_quarter.png)
- [Head detail](city_lights_02-evidence/head_detail.png)

Views show a broad legible lantern, smooth continuous shading, distinct cap/diffuser/shield
and quiet tapered pole. Studio views do not establish gameplay-camera readability.

Source checks passed: closed manifold components, positive signed volumes, nonzero-area
faces, unit scale/applied rotation and dimensional tolerance. GLB checks passed: exact
axis bounds, identity scale/rotation, 3,616 nondegenerate triangles, unit normals, expected
materials and no studio/camera/light/image/animation payload. Both fresh saved-source
reexports were **byte-identical** to initial exports; see
[comparison](city_lights_02-evidence/reexport_comparison.json) and
[payload report](city_lights_02-evidence/glb_checks.json).

One ordinary fix cycle was used: initial service-cover bevel produced a degenerate face;
bevel reduced from 0.012 to 0.003 m. Failed source and complete initial diagnostics are
retained (failed source compressed as `initial_failed_source.blend.gz` to avoid engine import). Blender completed source/export/render work but stalled on audio teardown with
`pa_write() failed ... Operation not permitted`; only owned CLI sessions were interrupted
after completion. Final process exit was 130, not a clean exit. `-noaudio` did not eliminate
this teardown behavior. Logs also retain a blocked user-cache thumbnail write, PipeWire connection failure and Blender 6.0 material API deprecation warning; the source file and renders were written successfully. Artifact checks and byte comparison passed independently; do not
report the Blender process as exit-zero. Full commands, exits and logs are in
[execution record](city_lights_02-evidence/execution.json). All owned writers are stopped.

Lead remaining gates: import both GLBs with pinned Godot; preserve generated `.import`
sidecars and UIDs; create a linked prefab at `scenes/prefabs/environment/city_lights_02.tscn`;
verify import AABB, normals, front/service cover, root scale and lens variants; save/reopen
prefab (including inherited variant if used); inspect at 47 m/42° vertical-down perspective
1280×800 with an actor; check head sightlines, route/collision clearance and repeated-instance
cost. No unmeasured real lights should be added. Obtain independent art/technical review.
Prefab, collision/gameplay/network, engine visuals and performance are all pending.

Import sidecars appeared from a separate importer during work; this specialist did not author
or modify them and makes no engine acceptance claim from their presence. The evidence
manifest lists producer files only; the lead owns sidecar validation.
