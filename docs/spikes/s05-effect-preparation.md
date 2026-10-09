# S05 explosion carrier source preparation

Predeclared 8 October 2026. Sole producer `92400a44-fc12-400a-a0d0-126e7f8f984e`,
GPT-6.1-Sol configured/effective HIGH, workspace `wks_437a9484cd5db686`, accepted
base `122978243dba25b3fb5d8d90fc50ffb1a468ecf5`. Root owns integration and leases.
Scope is one new original Blender blockout/carrier and explicit GLB export. This
is provisional technical source preparation; full S05 and production art remain open.

## Brief and source ownership

The accepted [effect concept](../concepts/p0-04/g-weapons-effects.png) and
[art direction](../art-direction.md#weapons-and-effects) supply broad ivory/amber
flash, coral lobes and gaps. Use one smooth static burst keyframe: a small central
flash and five separated outward lobes, combined into one Blender mesh with three
opaque flat material slots. No dense smoke, sparks, debris, texture, rig, animation,
collision, audio, LOD or new effect family is needed for this preparation.

New source `prototypes/s05_effect/art/source/models/spikes/s05_explosion_carrier.blend`, collection
`export_s05_explosion_carrier`, sole member/export root `ExplosionCarrier`, exports
to `prototypes/s05_effect/art/models/spikes/s05_explosion_carrier.glb`. Existing `art/source/.gdignore`
excludes the source. Material order: `flash_amber`, `burst_coral`, `flash_ivory`.
Original geometry and source-owned colors are authored in Blender by this producer;
no external models, images, libraries, copied meshes or new licensing dependencies.
Textures and UVs are unnecessary for flat opaque colors; no emission/alpha/bloom
claim. No machine-local source dependencies. Catalogue/import/prefab stages remain
pending under the source-only commission, which reserves this new mapping here.

Metres, metric unit scale1, Blender +Z up/+Y front → Godot +Y up/-Z front through
one Y-up export conversion. Origin is the cosmetic emission datum, not a damage
radius. Predeclared static limits: width/depth <=4 m, positive height <=2 m, no
geometry below datum; local identity transforms, six disconnected closed surfaces,
nondegenerate outward triangles, finite coordinates/normals and no modifiers.
Provisional footprint relates only to the unchanged S04 visual1.88×1.54×3.4 m and
four-metre S05 grid; it does not ratify spacing, clearance or range4.1 m. Actual
camera readability remains pending at the S02 provisional vertical perspective,
fixed yaw, height47 m/FOV42°/native1280×800 (50° comparison), under matched lighting.
Static gaps can be checked; drawn target/road visibility and cost cannot.

## Authorized validation and stop boundary

Blender MCP drives the shared live session and is outside this grant. Use only
owned isolated CLI processes on actual accepted Blender5.2.2 LTS/buildd13f752e3b9c,
bundled glTF exporter5.2.40; private temporary config/cache and null audio backend.
Keep exact argv, raw stdout/stderr, exit/termination records and output hashes.
Bootstrap refuses existing source/export. Save the source, export its declared
collection into private scratch, reopen the committed source in another owned
process, inspect geometry/material/dependency invariants, reexport to scratch and
compare GLB bytes. Check GLB accessor bounds, hierarchy/materials, normals, triangle
topology and absence of textures/skins/animations/cameras/lights/compression.
Any failed check is retained. Stop only owned process handles with bounded waits.

No shared Godot/Blender editor, display, service, registry credential, PID inventory,
renderer/project/profile/pin/vendor/Steam/device action. No Godot import, `.import`,
UID/scene/node identities, saved resource roundtrip, screenshot or runtime evidence
is supplied at this stage. Accepted S01/S02/S04/S05/S06 bytes remain unchanged.

The [stopped S02 observation](s02-drawability.md#actual-single-observation-and-restoration)
had three automatic callbacks and nonblank pixels, but can_draw=false,2112×1320 and
suspended input: full positive criteria failed. Do not repeat or repair that route.
An actual changed drawable condition and explicit root grant are required later.
Eight deadline tokens are not eight visible effects or S07 GPU/capacity evidence.

## Source/export results

Saved source117308 bytes, SHA256
`f2f145c7f93906a56b7708823e33c926cab24ee6dec190d3495829364b05deb3`;
GLB27536 bytes, SHA256
`d24e97bdbc5832787f3d781295d8eea40bbcdf0802d1c62f7ef78b6ddfc98647`.
Nine owned Blender CLI children exited0 and were reaped without stop signals.
Source reopening returned an identical geometry/material/dependency receipt and
both fresh exports were byte-identical. [Full evidence](s05-effect-preparation-evidence/README.md)
retains source-authoring/reexport/check scripts, exact commands and raw diagnostics.

The original684-vertex/1344-triangle smooth mesh has six closed, manifold, outward
components; no modifiers, animation or external dependencies. The GLB contains
one identity node, one mesh and three opaque non-emissive, double-sided material
primitives. Double-sided is the exported Blender default, not a measured cost
choice. No image/texture/skin/animation/camera/light/compression is exported. Static
Y-up AABB minimum(-1.736134,0.100000,-1.813600), maximum(1.736134,1.700000,1.529067) m;
size3.472268×1.600000×3.342667 m. Five literal vertical-projection probes fall in
open gaps; six others lie inside the centre/lobes. These are static shape checks,
not camera readability, road/actor visibility, timing or overdraw evidence.

Initial bootstrap attempted a shared extension-cache write, blocked by the read-only
filesystem. Its raw stdout and the material-use_nodes deprecation remain retained.
A later private check sets the installed-help-documented BLENDER_USER_RESOURCES,
CONFIG,EXTENSIONS,SCRIPTS,DATAFILES plus all three XDG roots; no cache warning and
identical source/export bytes. Every export retains the optional missing MeshOptimizer
library diagnostic; compression extensions are absent. Logs are not diagnostic-free.
No source/model was altered to correct the environment, and no shared write succeeded.

Source preparation is ready for scoped independent review. Import, saved Godot
resources, authored presentation and actual draw observations remain pending.

## Accepted main rebase and bounded capability metadata

Root released the fresh review slot and supplied accepted LOCAL main
`0c84f01f2a0c817a5c6851a3a360e193a5f846d8`. Clean candidatec36db17 rebased to
cc719cf before further capability evidence. Actually read the nine-path accepted
1229782→0c84 delta: orchestration skill's prospective6–8 substantive/milestone
cadence, same-instance writer rule, proportional exact-review/retention policy;
TODO's OPEN DOC12/13, accepted stopped S02/S08 discovery, current S05 source-only
ownership and readiness; eighth checkpoint/index and immutable static ledgers.
Preserve all accepted bytes/master task blocks/Parallel/readiness/watermark; only
the existing S05 block has this preparation's additive three-line link. No pending
checkpoint candidate was inspected/adopted, and no full checkpoint is rerun here.

Root additionally authorized only exact pinned Godot `--help`, private XDG/tmp,
five-second cap, without `--editor`, `--path` or a loaded project. Actual call exited0
in0.032s, stderr empty/no private files and owned handle reaped. It documents
debug-server URI, DAP/LSP port overrides and log-file path. Raw help/argv/exit are
retained; no editor/runtime/app/registry or service query occurred. Root provisionally
reserved16650/16670/16015/16016/16017 for this S05 proposal. Actual binding/auth/route/
user-path separation/drawability remain unproved and require a new explicit grant.

## Deferred Godot stage

Before any launch/call/mutation, send root exact resource/node/script/import,
identity/save/reopen/playtest/cleanup operations, isolation evidence, finite budget
and positive/negative criteria. Await explicit grant. One writer is required only
for the same editor/endpoint/source; independently verified worktree editors may
author in parallel. Source-only readiness does not authorize this next stage.

The concrete pending request is [here](s05-effect-preparation-evidence/godot-request.md).
Installed toolkit/server1.0.3 source supports separate project directories, exact
WS pins, explicit token/project paths and private XDG registry. Binary metadata
and the newly authorized actual help document LSP/DAP/debug-server CLI switches.
This is capability metadata evidence;
no independent editor, bridge, port availability, user-path separation, actual
argument behavior or drawability has been exercised. No live connector setting was
changed. In particular, pinning alone does not prevent registry writes: plugin
startup always registers and its unfocused-sleep backup also uses the registry.
The private XDG route is essential. [Source identities](s05-effect-preparation-evidence/isolation-source-receipt.json)
retain exact accepted Git blobs and installed-source/binary hashes, without copying
old histories, inspecting credentials or querying main483496.

Future cosmetics must consume the existing S05 live EventId/current-state fence
and eight120-tick reservations, with finite generation/lifetime cleanup and four
saturation drops in the twelve-event row. Hydration emits no historical effects.
The saved effect hierarchy owns model placement; runtime instantiates saved scenes
and supplies state, never authors children or changes authored model placement.
Damage/lifecycle/replication and accepted car/chain/S04 resources remain immutable.
Actual eight drawn effects, saturation/live-versus-settled-hydrated observations,
Regner policies, final S02/S04 dimensions/contact reruns, admitted-player lifecycle,
full join/journal/reset, S07/Steam/Deck/P0/M1/production acceptance remain open.
