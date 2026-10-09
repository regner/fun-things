# Batch 02 engine candidate

Source candidate: `5e94cc0ea4155219285db49c64b5728e0882b093`, parent `784dfc33a47f481ee43441c36a0280793e02de77`. This report and integration evidence are committed together; final engine hash is supplied in the handoff. Six records, eight imported variants: planting03 shrub, planting04 compact/broad trees, planting05 tuft/clump, roof01 vent, roof02 enclosure, shop01 canopy. Production sources remain byte-identical to the frozen candidate. No world placement acceptance is claimed.

## Saved assets and checks

Eight editor-authored prefabs instance the corresponding imported GLB under `Visuals/Model` at identity, preserving original pivots, metres and Blender +Y/+Z to Godot -Z/+Y axes. Import sidecars and authored scene UIDs are retained. Inspection confirms source-backed mesh resources, no material overrides or embedded replacement geometry, opaque imported materials, source bounds within 0.001m, and 21 registered dependency/scene identities. All eight prefabs and five inherited test fixtures passed save/close/reopen with byte-identical saved files.

Only tree trunks have authored static collision: cylinder radius 0.22m, height 1.6m, base on ground, layer1/mask0. Crowns, shrub, weed, roof details and canopy are decorative; enclosing buildings and planting containers own applicable collision. Decorative canopy volume is not a solid obstruction. This avoids invented foliage, opening or roof access mechanics.

At the original review, native S02 movement/aim APIs verified trunk contacts in an isolated saved fixture, clear bypass and canopy passage. Two real separate pinned engine processes (227633/227634, exit0, empty stderr) replayed the same commands with identical outcomes: both tree contacts stop at Z2.60025811m; clear route reaches Z-4.00000095m; aim query identifies the broad trunk. This is separate-process physics equivalence, not multiplayer transport/admission/prediction proof. The native planted fixture separately stops actors at Z3.27734089m against surrounding planters; its original overly high threshold failure and bounded corrected ring-specific expectation are retained.

The 9 October cleaned-project reconciliation moved the fixture to
`tests/assets/asset_production/` and replaced archived S02 classes with test-only
accepted-envelope clearance and line-of-sight probes. Current headless observation and
separate-process replay preserve the retained trunk stops (Z=2.600258112 m), clear route
(Z=-4.000000954 m), planted stops (Z=3.277340889 m), broad-trunk aim hit, overlap outcomes
and mounting margins. Headless query timings differ and are not graphical cost evidence.

## Visual and placement evidence

`batch_02_camera.tscn` renders a native 1280x800 vertical47m/FOV42deg view with the accepted Courier and source-backed actor references 2.6m in front of each tree, in pistol-hold pose. Native `gameplay.png`, `mounting-close.png`, `roof-close.png` and `repetition.png` were visually inspected. Chosen spacing preserves actor visibility; direct under-crown occlusion remains a placement consideration. Roof fixtures rest on the unchanged shop roof at Y10m, with edge margins 4.70m/4.40m and zero plane error. Canopy wall datum error is under 0.000001m; lowest Y2.58m provides 0.78m headroom above the 1.8m capsule. Tree/surround ground datum errors are zero. These are saved comparison fixtures, not accepted whole-city placements.

Reviewer C1 is addressed by the separate Blender-authored `calibration/tree-roof-metre-front-up-comparison.blend` and PNG: unchanged compact/broad tree and both roof source collections beside measured one-metre cubes and visible +Y FRONT/+Z UP arrows. `tree-roof-measurements.json` records pin, source/GLB hashes, measured source bounds, translation-only instances, unit scale, axes and reference dimensions. The earlier shrub/tree comparison and its initial failure are retained. Frozen production source bytes are not edited or reexported. The same independent reviewer must disposition this evidence at the final exact candidate.

## Bounded desktop cost

Godot4.8-dev7 c971f93e7, native Forward+/Vulkan GTX1070, 120 samples per scenario, medians over final60. Baseline three Courier visuals: 274 draw calls, 65,952 primitives; repeated fixture adds32 saved instances (four of each output): 444 calls, 170,856 primitives. Process medians 0.000206/0.000215s, physics 0.0011325/0.0004515s, reported video memory 93,696,064 bytes both. A batch of300 production queries measured195/227 microseconds. Default imports generate LODs. This short desktop observation establishes actual counts and query execution, not sustained device/GPU performance acceptance; detached roof/canopy copies in repetition fixture are cost comparisons only.

## Retention, diagnostics and disposition

335 producer payload hashes/bytes and six manifests retained without source edits. The initial independent review pack is retained in place, with one readback receipt:120 artifact-index-listed payloads plus the index and expected-set metadata,122 paths total. No actionable source/export defects were reported; initial disposition was pending C1. Integration evidence includes raw requests/results, command argv/exits, script compilation/style results, initial class-name, physics-threshold, stale-method and missing-PIL failures plus corrections. Known pinned `unfocused_sleep` constructor diagnostics remain visible in the editor log delta; no vendor diagnostics were patched or broadly suppressed. Final validation and pinned gdstyle exit0.

Source/export delivered; bounded engine integration/checks delivered; independent final review pending. Full-world placement, combat occlusion, network transport/authority and sustained target-device checks remain downstream. No generic READY claim.

Private editor PID195352, exact production project and pinned executable, editor22650/runtime22651/LSP22652; guarded client verifies PID/cwd/argv before local authenticated transport. Runtime stopped, inspector scene saved, no unsaved scenes. Private configuration remains under `/tmp/asset-register-production-editor`; resume via `node tools/asset_production/integration/editor_client.mjs <requests.json>` (owned endpoint only), after verifying current PID and lease. Final context receipt is retained. No other editor/config/project or queue/register/progress mutation occurred.
