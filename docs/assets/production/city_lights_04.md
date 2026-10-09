# city_lights.04 — wall light

9 October 2026. Source/export handoff; independent review and engine/prefab acceptance pending.
Commission: [raw request and ownership](commission.md). Producer: commissioned Codex
visual/model specialist, working only on city_lights.04. Lead
`150f00b5-9e62-44d8-b0aa-a456d2a88b8c` owns imports, prefabs, shared records and Git;
ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2` now directly owns queue/dispatch and receives the sole final handoff; technical integration waits for ROOT assignment. Input baseline
`2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`. No independent acceptance is claimed.

## Appearance and provenance

Original oval wall lantern: broad domed petrol canopy, dark seal, recessed continuous
warm/cool diffuser, layered lower shield, a smooth rising cast bracket and two quiet
backplate fasteners. It carries city_lights.02's shallow cap/diffuser/shield language
onto a wall, with city_lights.01's curved support vocabulary. Neither source was edited
or copied. No downloaded meshes, texture assets, generative services or external
libraries were used. Geometry and flat-color materials were authored in Blender for
this commission; no third-party attribution is required.

References actually inspected: [family brief](../city_lights.md),
[Petrol & Coral](../../art-direction.md), city_lights.01 hero and city_lights.02 head
detail, [Old Quay v03](../../concepts/districts-v1/05-old-quay-v03.png),
[Glassward v01](../../concepts/districts-v1/04-glassward-v01.png), both districts'
exact map extracts and layout/identity records. Warm frontage accents and cool
corporate variants guide appearance. No dimensions were inferred from image pixels,
and no district placement, polygon, road surface or building was changed.

## Interface and measured dimensions

These are authorized reversible modeling choices, not gameplay-approved dimensions.
Envelope tolerance is ±0.001 m. All source objects have applied translation, rotation
and scale, identity root and metre units. Blender +Y is outward/front and +Z is up;
glTF conversion maps them once to Godot -Z/+Y.

| Property | Metres |
| --- | --- |
| Complete Godot X/Y/Z size | 0.640 / 0.535 / 0.710 |
| Godot-axis AABB minimum | (-0.320, -0.230, -0.710) |
| Godot-axis AABB maximum | (0.320, 0.305, 0.000) |
| Oval head plan | 0.640 wide × 0.500 deep |
| Head plan centre, Godot | (0, height varies, -0.460) |
| Backplate | 0.200 wide × 0.460 high × 0.056 deep |
| Backplate fastener centres, Godot | (0, ±0.171, -0.057) |
| Bracket diameter | 0.072 at wall, tapering to 0.062 at head |

Root `CityLights04` is the **attachment anchor**, at the centre of the rear mounting
plane, not a ground pivot. Place root on the facade plane; local Godot Z=0 is the rear
contact plane and all visible geometry projects toward -Z. No geometry penetrates
behind that plane. Yaw the prefab so -Z points away from the wall; do not compensate
with scale or an export-axis rotation. The backplate/gasket rear plane is Blender Y=0.

A provisional anchor height of 2.80 m puts the complete visual bottom at 2.57 m and
head top at 3.105 m. This height is only a placement example; lead must validate
clearance, door/canopy overlap, sightlines and actual route use. Maximum projection
is 0.71 m; the head rear edge is 0.21 m from the wall. No mounting socket, collider,
real light, rig, animation, damage state or dynamic behavior is supplied.

## Source and outputs

- Source: `art/source/models/environment/city_lights_04/city_lights_04.blend`, covered
  by existing `art/source/.gdignore`.
- Export collection: `export_city_lights_04`; root: `CityLights04`.
- Warm: `art/models/environment/city_lights_04/city_lights_04_warm.glb`.
- Cool: `art/models/environment/city_lights_04/city_lights_04_cool.glb`.
- Owned tools: `tools/asset_production/city_lights_04/{author,export,check_glb,run}.py`.

Nine named editable mesh members parented to root: `mounting_backplate`,
`mounting_gasket`, `mount_fastener_lower`, `mount_fastener_upper`, `curved_cast_arm`,
`lower_shield`, `broad_recessed_diffuser`, `canopy_seal`, `broad_oval_canopy`.
The explicit member allowlist is checked before export. Source studio wall, metre
reference, camera and lights are excluded; actual payload node names are checked.
Saved source defaults to warm; the cool material is retained using a fake user.
Reexport switches only the diffuser material and restores the original assignment.

Toolchain: `/usr/bin/blender` **5.2.2 LTS**, build `d13f752e3b9c`; bundled glTF
**5.2.40**, both asserted by the export tool. `-noaudio` support is retained in
`tool_help.log`. GLB with selection allowlist, Y-up, normals, embedded PBR materials;
no UVs/tangents/textures, cameras, lights, extras, skins, morphs or animations.
Modifiers are already applied to the editable source meshes. Full settings and
member-to-slot mapping: [source checks](city_lights_04-evidence/source_checks.json).

## Materials and geometry

Each mesh uses slot 0. Petrol metal: backplate, bracket, lower shield and canopy.
Dark recess: gasket, two fasteners and canopy seal. Lens material: diffuser only.
Three used materials per variant, nine mesh primitives and **4,388 triangles**.
Broad oval parts use 64 circumferential segments; bracket uses 21 × 16 rings.
No explicit LOD is provided; repeated-placement cost and importer LOD stay pending.

| Material suffix (`city_lights_04_`) | sRGB | Metallic | Roughness | Emission strength |
| --- | --- | --- | --- | --- |
| `petrol_metal` | #193F46 | 0.55 | 0.38 | 0 |
| `recess_dark` | #0D1D22 | 0.30 | 0.42 | 0 |
| `lens_warm` | #FFDCA3 | 0 | 0.55 | 0.45 |
| `lens_cool` | #ACDEEF | 0 | 0.55 | 0.45 |

sRGB colors are converted to linear shader inputs. Opaque materials; no texture
files, alpha blending or transmission. Emission is fixture appearance only and
creates no exported real light. Godot material remapping, bloom and any real light
budget are lead-owned. Material JSON values are retained in the payload report.

## Validation and previews

Source checks: exact declared membership, identity transforms, no pending modifiers,
finite positions/normals, positive volume per component, closed manifold edges and
nondegenerate source faces/triangles. Independent GLB decoding checks actual position
and normal buffers, finite unit normals, triangle areas, bounds, exact hierarchy,
material names, and absence of studio/animation/image/light content. These checks
validate source and export, not Godot import or gameplay.

[Warm hero](city_lights_04-evidence/hero_warm.png),
[cool hero](city_lights_04-evidence/hero_cool.png),
[underside/attachment detail](city_lights_04-evidence/detail_underside.png),
[vertical-down close view](city_lights_04-evidence/vertical_down_detail.png),
[47 m/42° scale view](city_lights_04-evidence/vertical_down_47m_42deg.png).
These are isolated Blender Cycles/AgX renders, 32 samples, CPU four threads;
hero/detail 1000×900, scale view 1280×800. Studio light transforms, colors and energies
are in `author.py`. The scale view uses vertical 42° FOV, camera 44.2 m above the
attachment anchor (equivalent to 47 m above ground with a 2.8 m mounting height),
straight down, Blender +Y at image top. Wall is omitted in overhead renders to show
footprint without studio-wall occlusion. No actor, city lighting or engine view is
represented. At this scale the canopy is intentionally small and the lens is hidden
from directly above; the wall light is not an actor-identification cue.

One concrete visual fix cycle: initial underside view showed the bracket end cap
peeking through the shield. The terminal point moved from Z=0.095 to 0.125 m and its
preceding control point from 0.084 to 0.105 m, burying the cap in the head. Detail
framing was widened. Initial source, outputs and authoring script are retained in
`initial_visual_failure.zip`; initial images/checks/logs are retained separately.

Full subprocess argv, PIDs, elapsed time and exit statuses:
[execution](city_lights_04-evidence/execution.json). The first run completed all writes
but stalled at audio teardown despite `-noaudio`; its owned process required SIGINT
then SIGKILL and returned -9. This is not an exit-zero success. The corrected run uses
process-local `ALSOFT_DRIVERS=null`; no global audio or connector configuration changed.
The corrected build and saved-source reexport both exited **0** without termination.
The independently decoded final GLBs passed; both fresh saved-source exports were
**byte-identical** to their delivered counterparts. Final hero, underside, cool and
vertical-down views were visually inspected: the bracket cap is now enclosed, broad
shading is continuous and the warm/cool diffuser remains distinct. All owned writers
are stopped. Logs also record a blocked thumbnail-cache write, Blender 6.0 API deprecation notices,
and unavailable optional MeshOptimizer library. Compression was not requested.

## Reproduction and remaining gates

From repository root, run via `python tools/asset_production/city_lights_04/run.py LABEL`
followed by the command to retain argv, logs and exit status. Reexport existing sources
rather than rebuilding when validating an artist-edited source:

```sh
env ALSOFT_DRIVERS=null /usr/bin/blender -noaudio --background --factory-startup --threads 2 art/source/models/environment/city_lights_04/city_lights_04.blend --python-exit-code 1 --python tools/asset_production/city_lights_04/export.py -- docs/assets/production/city_lights_04-evidence/reexport
python tools/asset_production/city_lights_04/check_glb.py docs/assets/production/city_lights_04-evidence/reexport
```

[Payload report](city_lights_04-evidence/glb_checks.json),
[reproducibility](city_lights_04-evidence/reproducibility.json) and
[producer paths/bytes/SHA256 manifest](city_lights_04-evidence/manifest.json) identify
the actual files tested. Scratch reexports are evidence, not runtime dependencies.

Lead remaining gates: pinned Godot import and import-sidecar/UID validation; linked
warm/cool prefab integration; material and normal inspection; import AABB/front/anchor
checks; saved/inherited scene save/reopen; actual vertical-down camera views with an
actor; independent art/technical review; placement and any collision/query/movement/
multiplayer checks; repeated-instance draw cost, real-light budget and Deck LCD/OLED
readability/performance. No gameplay, engine, performance or production-ready claim
is made. No Git, shared docs, prefab, project, world or live connector was mutated.
