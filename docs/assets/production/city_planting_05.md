# city_planting.05 — Ironreach sparse weeds

9 October 2026. **Source/export candidate; independent and engine acceptance pending.**
Producer: assigned Codex specialist. Dispatch/acceptance owner: ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2`; downstream integration is lead-owned.
Workspace `wks_59891ad7a05813e5`, branch `art/register-production-20261009`.
The immutable [commission](commission.md) was read at
`2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`; the current user assignment supersedes
historical concept-only wording. No READY, Godot, gameplay or device claim.

## Brief and original construction

Two static, low, sparse olive-green blade arrangements for selected workshop/fence
margins. Original Blender-authored lenticular blade solids: a nine-blade short tuft
and a spreading group of three irregular five-blade roots. Curved centre lines,
wide shoulders, a shallow blade ridge and tapered drooping tips carry the shape.
There are visible gaps through the spreading group. These are deliberately separate
from the compact rounded crown volumes of shrub `.03`. No copied plant models,
external textures, image-to-mesh service or paid generator was used. Original project
work; reference concepts remain references, not mesh provenance.

Read [planting brief](../city_planting.md), [accepted art direction](../../art-direction.md),
[Ironreach concept](../../concepts/districts-v1/ironreach.md) and
[breakdown](../../concepts/districts-v1/ironreach-assets.md), including the v02 image.
Input hashes and read-only tooling references are in
[reference_inputs.json](city_planting_05-evidence/reference_inputs.json).
Dimensions below are reversible authoring choices consistent with the brief's low
edge dressing, **not measurements extracted from the generated district image**.

## Source, variants and dimensional contract

Source: [city_planting_05.blend](../../../art/source/models/environment/city_planting_05/city_planting_05.blend).
Metres, Metric scale 1. Parent export collection `export_city_planting_05` contains
`variant_short_tuft` and `variant_spreading_clump`. Each variant contains exactly one
identity-transform empty named `city_planting_05_<variant>` and its one mesh child
`<variant>_blades`. Blade islands remain individually editable in the mesh.
Declared root + child selection is rebuilt for every export; studio selection is
never relied upon. Both runtime outputs are explicit:

| Variant | Game GLB | Godot X width × Y height × Z depth (m) | Godot AABB min → max (m) | Blades / triangles |
| --- | --- | --- | --- | --- |
| Short tuft | [short_tuft.glb](../../../art/models/environment/city_planting_05/city_planting_05_short_tuft.glb) | 0.56 × 0.26 × 0.42 | (-0.28, 0, -0.21) → (0.28, 0.26, 0.21) | 9 / 1,170 |
| Spreading clump | [spreading_clump.glb](../../../art/models/environment/city_planting_05/city_planting_05_spreading_clump.glb) | 1.00 × 0.20 × 0.62 | (-0.50, 0, -0.31) → (0.50, 0.20, 0.31) | 15 / 1,950 |

Ground datum and pivot are ground-centred at Y=0 in Godot (Z=0 in Blender).
Rotation and scale are applied; source and exported object/root transforms are
identity. Blender +Y forward / +Z up maps once to Godot -Z forward / +Y up.
Plants need no facing-dependent gameplay. Dimensional acceptance tolerance is
±0.001 m; source and binary numeric checks use the stricter 0.000001 m tolerance.
No ground disc, soil skirt or supporting box is included in either runtime model.
Individual tapered roots contact the flat ground; uneven terrain is untested.

Authoring collection `authoring_reference_excluded` retains an applied-scale
0.035 × 0.035 × **1.000 m** vertical measurement rod, ground, cameras and lights.
The reference is measured in source checks, visible in comparison previews, and
proven absent from both GLBs by exact exported node scope. It is not production art.

### Assembly footprint proposal

Use short tufts as isolated marks, with a nominal 0.70 × 0.60 m allocation; use a
spreading clump in a 1.20 × 0.82 m margin allocation. These allocations include
at least 0.07 m or 0.10 m respectively beyond the authored AABB and are placement
suggestions, not gameplay clearances. For arbitrary yaw, reserve a 0.35 m radius
for the tuft and 0.589 m radius for the clump, plus placement clearance.
Space spreading roots at least 1.20 m centre-to-centre along an unrotated margin
if a visible 0.20 m gap between full footprints is wanted; use broken groups rather
than a continuous hedge or grass carpet. Do not fill gateways, yard centres, walking
routes, vehicle openings or the separate foot bypass. The entire visual footprint,
including overhang, belongs outside those route envelopes. Actual route ownership,
placement and camera/actor acceptance remain downstream. No collider, navigation,
wind, growth, rig, animation, socket, interaction or runtime system is supplied.

## Materials and geometry rationale

Both variants use one mesh, three opaque material primitives, no textures/UVs or
normal maps. Stable slots, in order:

| Slot | sRGB swatch | Roughness | Metallic |
| --- | --- | --- | --- |
| `weed_olive` | #5C6C3D | 0.89 | 0 |
| `weed_olive_light` | #707A48 | 0.88 | 0 |
| `weed_olive_dry` | #7D794C | 0.94 | 0 |

PBR colors are converted to linear values in Blender and exported embedded in each
GLB. No external material dependency or Godot remap is authored. Solid closed blades
use backface culling, not alpha cards. Eleven longitudinal rings, six vertices per
cross-section and a single closed tip provide smooth curvature without dense leaf
texture or tiny serration. Joining blades into one mesh limits unnecessary surfaces;
three palette primitives remain. No invented polygon/performance gate, LOD or
compression policy is claimed. Target-renderer overdraw, draw calls and cost await
measurement; automatic import LOD settings are integrator-owned.

## Evidence and findings

- [Short tuft hero](city_planting_05-evidence/short_tuft_hero.png) and
  [spreading clump hero](city_planting_05-evidence/spreading_clump_hero.png): final
  smooth broad blade silhouettes, sparse gaps and quiet olive variation.
- [Scale comparison hero](city_planting_05-evidence/scale_comparison_hero.png):
  left to right, retained 1 m rod, tuft, spreading clump, unchanged `.03` shrub,
  unchanged Coral Courier. Existing GLBs were imported read-only at **unit scale**;
  hashes, offsets and measured bounds are in
  [preview_checks.json](city_planting_05-evidence/preview_checks.json).
- [Gameplay-camera comparison](city_planting_05-evidence/scale_comparison_gameplay.png):
  Blender perspective, vertical down, fixed zero yaw, 47 m, 42° vertical FOV,
  1280×800. This is a calibrated **Blender reference**, not an engine capture.
  Measured extents are 12.42 × 9.33 px (tuft) and 22.21 × 13.78 px (clump).
  The weeds are deliberately small marks at this distance; broad silhouettes carry
  the detail. The layout is a separated comparison, not an actor movement test.
- [Enlarged overhead silhouettes](city_planting_05-evidence/silhouette_overhead_enlarged.png):
  same comparison with temporary black materials, showing negative spaces versus
  shrub `.03`'s filled lobes. This orthographic enlarged diagnostic is not gameplay.

Previews use CPU Cycles, 32 samples with denoising, AgX, four CPU threads, fixed area
lights and slate ground. All temporary comparison placement/material changes are
in-memory only; the source is not re-saved by preview tooling. No actor/shrub source,
export or material file was changed. Visibility at the project camera and any
close-up material tuning must still be judged in Godot and on target devices.

[Source/export checks](city_planting_05-evidence/source_export_checks.json) verify
pinned tools, declared membership, metre scale, applied transforms, source bounds,
closed/consistently wound edges and positive volume **per blade island**, finite
unit normals and nondegenerate triangulated faces. The minimum final triangle area
is over 0.000007 m². [Binary checks](city_planting_05-evidence/glb_checks.json) independently
decode actual vertex/index buffers, check triangle winding against shading normals,
welded edge pairing, material values, exact runtime scope and Godot-axis bounds.
No cameras, reference fixtures, lights, textures, skins or animation are in the GLBs.
[Saved-source re-export comparison](city_planting_05-evidence/reexport_comparison.json)
passes **byte-for-byte for both variants** in a fresh private Blender process.

### Owned fix cycle and actual diagnostics

The first hero showed angular bends. One owned geometry refinement increased curve
rings from seven to eleven, retaining dimensions and silhouette, and enabled
backface culling on closed blades. Initial source, GLBs, scripts and previews remain
under `city_planting_05-evidence/initial_attempt/`; final evidence is at its parent.
The first binary material assertion also rejected 0.879999995 against literal 0.88;
the corrected check compares each intended value with 1e-6 tolerance. Full failed
and successful logs remain. This was a checker precision defect, not a wrong material.

The requested `/usr/bin/blender5.2.2LTS` path returned ENOENT (exit 127).
`/usr/bin/blender` is the exact verified **5.2.2 LTS / d13f752e3b9c / glTF 5.2.40**
build and was used instead. Blender prints an unavailable optional MeshOptimizer
library diagnostic; exports use uncompressed core glTF and passed all payload checks.
Source saves print an OpenImageIO thumbnail-cache write error outside the writable
workspace; the `.blend` save itself succeeds and is reopened for export/re-export.
The version command reports one 23-byte shutdown allocation. Material `use_nodes`
prints a Blender 6.0 deprecation warning. These diagnostics are retained and not
suppressed; none is presented as an engine acceptance result. The installed
BlenderMCP addon registers during CLI startup; no connector API or shared session
was used. No service or global configuration was changed.

The first command-ledger implementation loaded its array before the long preview;
its completion overwrote four concurrent command receipts. Exact executed argv and
observed exits for those four were restored from terminal results, with missing
UTC start/end explicitly marked. Their complete original diagnostic logs survived.
The runner now writes a per-command receipt and reads the ledger after the command.
The preview bounds helper was also narrowed to visible rendered meshes. An
importer-created `Icosphere` in hidden collection `glTF_not_exported` had polluted
the actor AABB; the first object-level hide filter was insufficient, and the final
collection-aware filter excludes it. Original receipts remain; captures are unchanged.
The unit-scale actor's rendered ground/top are 0.00250 / 1.85665 m.
The first final-audit pass checked its own not-yet-written output link and failed;
that self-link is now validated after report generation. The original assertion log
and audit script are retained. All actual command argv, process environment, exits and substantive diagnostics are
in [commands.json](city_planting_05-evidence/commands.json) and linked raw `.log` files.

## Reproduction and handoff limits

From repository root, use the exact argv in the command ledger with process-local
`ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy`, `-b -noaudio -t 4` and
`--python-exit-code 1`. `author.py` creates the source; open that saved `.blend` with
`export.py` for runtime outputs. `export.py -- <scratch-directory>` re-exports for
comparison. `check_glb.py` audits runtime payloads; `compare.py` performs the strict
byte comparison. `preview.py` opens the saved source and generates only evidence.
`run.py <unique-log-name> <argv...>` retains logs without overwriting prior failures.
Authoring is deterministic geometry construction; the `.blend` container's own
bytes are not claimed deterministic between saves. Saved-source **GLB** bytes are.

[Final audit](city_planting_05-evidence/final_audit.json) records completion and
reference integrity. Authoritative path/byte/SHA256 listing:
[manifest.json](city_planting_05-evidence/manifest.json). It lists source, explicit
runtime outputs, report, tooling and retained evidence; it excludes itself to avoid
self-reference. Reproduction/check scripts are local to this ID. No Git/index,
shared docs, project, prefab, world, other-source, initial-six source or connector
configuration writes were made by this worker.

Source/model and export checks: **passed by producer**. Blender visual inspection:
**completed by producer, not independent acceptance**. Godot import metadata and
saved-resource checks, prefab/inheritance, collision/no-collision behavior, gameplay
camera/movement, multiplayer relevance, device/performance and independent art review:
**pending downstream**. Production source status must not be promoted to READY from
these source-only receipts. Concrete later review fixes remain with this specialist.
