# Six-asset engine integration candidate

Source candidate: `390377dc6530e101eddcbf38b2946a1b235137c7`, original base
`66400c26a01bf917dfe631af4762c2b444d9c48f`. Scope: city_lights.01/.02/.04,
city_sign_supports.01 and city_planting.01/.02. Source bytes remain unchanged.
ROOT owns queue/review/world integration. This is a technical candidate, not a READY verdict.

## Saved deliverables and contracts

Nine linked Godot prefabs under `scenes/prefabs/environment/` include warm/cool variants
for all three lights. They retain imported `Visuals/Model` instances at identity transforms;
there are no embedded render meshes or runtime-authored prefab hierarchies.
The final editor inspection records imported mesh ancestry, aggregate bounds and UID
registration. All nine prefab and three inherited fixture save/close/reopen/resave
roundtrips preserved exact bytes. Original four light prefab UIDs and node IDs are preserved;
Godot normalized redundant imported-node `type` declarations in the pedestrian wrappers.

| Asset | Godot bounds / pivot | Collision decision |
| --- | --- | --- |
| Street pole | (-.36,0,-1.40) → (.36,6.20,.21), ground foot | Existing saved pole cylinder, radius .21 m / height 5.45 m; overhead arm decoration |
| Pedestrian light | (-.36,0,-.36) → (.36,3,.36), ground foot | Existing saved pole cylinder, radius .135 m / height 2.63 m; cap decoration |
| Wall light | (-.32,-.23,-.71) → (.32,.305,0), wall anchor | Visual-only mounted hardware; facade owns blocking wall |
| Wall panel | (-.7,-.5,-.1) → (.7,.5,0), wall plane | Visual-only carrier; facade owns blocking wall |
| Rectangular planter | (-1.2,0,-.45) → (1.2,.6,.45), ground centre | Separate saved 2.4 × .6 × .9 m box envelope |
| Round planter | (-.9,0,-.9) → (.9,.48,.9), ground centre | Sixteen saved convex ring prisms; .62 m clear inscribed radius retained |

Collision layers are static-world layer 1 / mask 0, separate from imported visuals.
The wall test mounts anchors at facade Z=-6, yaw π: both lamps at Y=2.8 m,
panel at Y=1.6 m. Panel top 2.1 m leaves .47 m below lamp backplate bottom.
These are inspection placements, not accepted city placement. No road tooling changed.
Panel UV0/sign_face material remains a future artwork interface; blank carrier rendering
and essential overhead wall-copy readability are not artwork/wayfinding acceptance.

## Actual validation

`batch_01-evidence/validation-summary.json` asserts all independent reviewer source-scope
hashes and all reviewer-indexed artifact bytes/hashes, nine measured engine bounds within
.001 m, linked ancestry, registered dependency identities, twelve stable roundtrips,
and actual public physics results. Raw requests/results/logs are retained in `transport/`.
Pinned gdstyle 0.3.0 reports zero warnings on both affected integration GDScripts;
script API compilation receipts have `valid=true`. Node transport now rejects empty
owned inspector receipts, because protocol success alone previously hid failed assertions.

Saved `batch_01_camera.tscn` uses the accepted Courier/preview fixture, vertical 47 m,
42° perspective, fixed north-up yaw, native 1280×800. `gameplay.png` is an actual engine
capture. Seven actor-capsule overlap expectations pass, including solid poles/planter/ring,
clear round centre/walkway/below-wall clearance. `S02ActorMotion.step` moved the saved
radius .38 m / height 1.8 m actor for 120 physics ticks per case: planter stop at
Z=3.83007 m and clear bypass at X=3 m ending Z=-4.00000 m. Initial X=2 bypass hit an
existing pedestrian pole; that fixture failure and correction remain raw evidence.
`mounting-close.png` captures the saved close camera and warm/cool facade mounts.
Camera capture is idle Courier presentation; combat/aim, populated-city occlusion and
separate-process authoritative/predicted movement are not accepted by these checks.

`batch_01_repeat.tscn` adds eight saved copies of each of the six designs (48 instances).
Desktop Forward+ / Vulkan, GTX 1070; same camera/lighting, capped 60 Hz preview.
Last-60-frame median render submissions: baseline 256 draw calls / 35,916 primitives;
repetition 439 / 153,096. Process/physics monitor timings and 300-query batch times are
raw observations, not GPU-frame/device/load budgets. No Deck/exported-platform or network
performance claim. The detached wall-fixture rows in this sample are cost fixtures, not
valid mounted world placements.

## Source calibration and independent review

Source reviewer `88d917ff-a9d8-4faa-b276-007c50bd4f05` reviewed the exact source candidate.
Full quiescent review pack is retained under `docs/reviews/asset-production/batch_01/`;
verdict pending G1, no P1/P2 source defect. G2 integrator-generated rectangular-planter
retention provenance was accepted. No speculative neck remodelling was performed.

`calibration/` retains a separate editable comparison scene, 1600×1000 render,
measurements and argv/exits. Blender 5.2.2 LTS, build/hash in measurements; five unchanged
source export collections are instanced with translation only, zero rotation/unit scale,
beside verified 1×1×1 m cubes. Original object matrices, metre units and source bounds
are recorded; all source hashes match the frozen candidate before/after. No source save
or export rewrite occurred. Isolated audio-disabled Blender exited 0 in about 20 s.
This supplies G1 evidence; the same reviewer must disposition it and the final engine delta.

## Diagnostics and safe resume

Private editor PID 195352, project/cwd this worktree; editor 22650, runtime 22651,
LSP 22652. `transport/launch.json` records binary and argv. Guarded
`tools/asset_production/integration/editor_client.mjs` verifies PID/cwd/cmdline and reads
only the private token. Live state `/tmp/asset-register-production-editor/`; no connector
configuration or shared live editor was changed. Runtime stopped; editor saved/no unsaved
scenes, inspector scene active. Blender calibration process finished. ROOT source writers
outside this batch remain untouched; worktree dirtiness is not wholesale staged.

Initial missing cache registrations/imports and unsupported ResourceUID.update_cache probe
are retained. A saved-state private restart with pinned headless import exited 0;
existing authored UIDs remained intact, and current runtimes show no UID fallback warnings.
The editor scene/save/play transport produces Godot progress-dialog/message-queue errors;
raw full logs retain them, successful saved-state inspections do not erase those errors.
Earlier unfocused_sleep constructor, importer stale-child/port notices and producer audio
shutdown diagnostics remain classified historical/tooling diagnostics, not silently fixed.

Resume a named editor request file with:
`node tools/asset_production/integration/editor_client.mjs /tmp/asset-register-production-editor/REQUEST.json`
Use `--runtime` only after a named game.start; preserve state and ownership checks.
Recheck committed receipts with `python3 tools/asset_production/integration/verify_batch.py`.
Remaining gates: same-reviewer exact-engine-candidate/G1 disposition, relevant network
collision behavior, combat/aim/populated-city placement, artwork content and device/export
performance. No unfinished placement, TODO or whole-register readiness is marked accepted.
