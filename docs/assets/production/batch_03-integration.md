# Batch03 bounded engine candidate

Seven started IDs only: city_shop_fittings.02/.03/.05/.06/.07/.08 and city_small_shop_shells.01. Original commission base `66400c26a01bf917dfe631af4762c2b444d9c48f`; original source candidate `028775618c4493ca672646e6e37fdc3c83e0e313`, parent accepted bounded Batch02 engine `10ddb64d16e6cb2f137923a31d3ca14991468f7d`. Corrected source/review-retention checkpoint `4f11c54d4abf4aa77813a1cf8bcf885fd040b7c9` is the immediate engine-delta base. This report, exact artifact index and engine changes are committed together; final hash is supplied in the handoff.

No new register IDs were started. ROOT owns pause/queue/review. Sources delivered; engine checks delivered; SAME-reviewer final disposition pending. Full world placement, transport/authority and sustained target-device acceptance remain downstream. No blanket READY or TODO completion is claimed.

## Source retention and corrections

All 594 current producer payload bytes/SHA256 match all seven actual manifests, including the released list-form fascia manifest. F1 fascia source correction has all five materials backface-culling enabled; source and raw GLB claims are retained in additive `f1_culling` evidence. F2 leaf correction retains envelopes/materials/UV/glazing/pulls and actual single/double mating evidence; its additive `fix_f2` pack remains unchanged. Corrections are submitted, not independently accepted by this integrator. Original rejected bytes and evidence remain in immutable `02877561` history and initial reviewer pack. Five other producer sets remain unchanged. Old shell source scratch copies remain historically exact; corrected fits are represented by current linked engine instances, not by rewriting the shell evidence.

The complete Batch03 initial review pack (105 indexed payloads + index) and exact Batch02 final pack (89 indexed payloads + two metadata files) passed one readback before retention. Godot subsequently generated an additional `resource_query_audit.gd.uid` for the Batch02 review script; it is retained explicitly as importer metadata, not a new reviewer payload or acceptance transfer. `review-retention-readback.json` records index hashes and observed counts. Producer and importer ownership remain distinct; import sidecars are integrated separately from producer manifests.

## Saved linked prefabs and collision

Nine variants: fascia; single/double surround; display bay; single/double closed leaves; upper window; blade sign; narrow shell. All prefabs instance their actual GLB under `Visuals/Model` at identity, preserving metres, pivots, Blender +Y/+Z → Godot -Z/+Y orientation, original model resources/material slots and UIDs. No embedded replacement meshes/material overrides, copied fitting mesh or runtime-authored hierarchy. Actual imported bounds match the initial independent literal expectations within 0.001m; all imported materials are opaque and back-culling. Fascia slot0 `fascia_artwork_face` and the two independent blade slot0 artwork materials survive import. Blank copy is deliberate; this does not accept essential wayfinding or tenant artwork.

Static closed leaves have exact body-envelope box collision; pulls/trim do not inflate solid volume. Display panes have two thin opaque-pane collision boxes. Shell collision follows separate wall spans, true entrance/window voids, sides/rear and roof slab. Collision is layer1/mask0, separated from visuals. Decorative fascia, casing, upper fitting, canopy and blade sign add no collision; buildings/closed panes/leaves own blocking. Canopy/sign lowest extents clear the1.8m actor. No door opening/state/replication mechanic is invented.

15 saved scenes (nine prefabs, frontage/upper-wall/camera/close/repeat/process fixtures) pass the final save-close-reopen byte-stability check; 25 authored scene/import identities resolve through the actual pinned cache and match saved sidecars. Initial serialization changed11 newly authored scene files; the original hash receipt and failure are retained. One stabilization pass compared complete saved snapshots and verified unchanged scene bytes/IDs. These new identities had no previously accepted engine candidate. No existing accepted Batch01/02 resource identities changed.

## Actual assembly and placement checks

The saved frontage uses actual shell GLB markers for single surround, single leaf, display window, canopy and fascia. Every measured marker-to-instance translation error is0m, axes aligned/unit scale. Measured window→canopy gap0.0999999046m, canopy→fascia gap0.1599998474m. Blade mounts at the flat right pier `(3,3.45,-7)` with all bracket backing at the wall datum; its bottom is2.870000124m, giving1.070000124m clearance over the1.8m actor. It does not overlap the other fitting installation envelopes.

The upper window cannot fit this one-storey shell: its required upper-floor opening is absent and its top6.25m exceeds the5.05m shell. A clearly labelled, original Blender-authored technical four-piece wall provides the real4.680×1.480m through-hole instead; it is a comparison fixture, not another district asset or an accepted shell extension. All260 actual imported rear window vertices fit the actual imported wall opening, with measured minimum jamb/head/bottom gap0.0199818611m and rear clearance0.120000362m. Uncut-shell mounting is explicitly not accepted. Fixture source is retained under ignored `art/source/models/spikes/batch_03_upper_wall`; game scene links only its explicit GLB. `fixture-provenance.json` records the unchanged source relocation and hashes.

The native1280×800 straight-down47m/FOV42deg north-up camera includes the accepted Courier at unscaled frontage distance, plus single/double and upper mounting comparisons. Native `gameplay.png`, `frontage-close.png`, `repetition.png` were inspected. Roofs dominate the overhead view; door/display/fascia copy is not essential overhead readable information. The close view verifies coherent frontage, blank art faces, door/surround placement and independent blade/upper forms. Whole-city placement/combat occlusion remain unaccepted.

## Physical APIs and separate processes

At the original review, the native fixture used S02 motion/query owners: closed single leaf stops at Z=-6.950526714 m, shell wall at -7.380214691 m and display pane at -7.414394379 m. The clear side reaches Z≈0 m; the route below canopy/sign reaches X=6.000000954 m. Its aim query identifies `Frontage/Door/Collision/Body`. Rays excluding the closed fitting bodies confirm shell entrance and display rear voids are structurally clear.

The 9 October cleaned-project reconciliation moved the fixture to
`tests/assets/asset_production/` and replaced archived S02 classes with test-only
accepted-envelope clearance and line-of-sight probes. Current headless observation and
separate-process replay preserve all six retained movement positions, the door aim hit,
structural void results, assembly gaps and upper-window fit values. Headless query timings
differ and are not graphical cost evidence.

Two fresh isolated pinned physics processes, PIDs259301/259300, replay six actual movement cases: single closed leaf, wall, pane, side clear, and both double leaves. Both exit0 with empty stderr and identical positions/query hits. This is bounded command replay in separate physics worlds, not multiplayer transport/admission/prediction authority proof. No authoritative simulation or world/network setting was modified.

## Proportionate cost observation

Godot4.8-dev7 c971f93e7, native Forward+/Vulkan GTX1070. Baseline includes10 production model instances plus the technical wall/Courier/ground; repeat adds three saved complete frontages,21 linked model instances.120 samples each; medians of final60:358→635 draw calls,31,812→78,012 primitives, process0.000152→0.0001525s, physics0.000377→0.0004005s; reported video memory92,159,872 bytes both.300-ray batches250/264 microseconds. This is a short desktop/scenario observation, not a budget or sustained target-device/GPU claim. Native launch argv, renderer/hardware logs, counters and query receipts are retained.

## Tool failures and safe handoff

Targeted refresh did not import new blade/shell directories. Targeted reimport helper returned an empty receipt; full scan then timed out. A saved private-editor restart exposed the actual Configure Blender Importer dialog plus toolkit welcome. Private configuration only now points to a retained wrapper around verified `/usr/bin/blender5.2.2LTS`, with process-local `ALSOFT_DRIVERS=null`, `SDL_AUDIODRIVER=dummy`, `-noaudio`. No connector/global audio/vendor code/project setting was changed. The unused reimport helper was removed after retention of its raw request.

Other retained failures: revised manifest list/dict schema mismatch; nonexistent editor.get_context method; console-handler diagnostic contract error; minimized/black editor screenshots; GLB-only toolkit scene.instantiate rejection (resolved using linked TSCN wrapper); embedded physical screenshot449×281 despite larger virtual content rectangle (resolved with standalone native `--resolution1280x800`, not bitmap resizing); initial new-scene serialization drift; initial style warnings plus corrections. Original argv/exits/raw requests/results and source failures are retained. Known unfocused-sleep constructor/progress-dialog/registry diagnostics remain unfiltered. Source operations are not judged merely by transport success.

Final validator and pinned gdstyle exit0. All source and owned integration writers quiescent; all owned native and separate-process runtimes stopped. Detached native launch OS exits were not collected: `quit(0)` requests and stopped-PID checks are retained, not falsely described as observed native exit0. The waiting separate-process checks have actual exit0 receipts.

Private editor nowPID254275 (prior195352), exact workspace/project and pin, editor22650/runtime22651/LSP22652. Inspector active/saved; no unsaved scenes. Guarded transport `tools/asset_production/integration/editor_client.mjs` and current `/tmp/asset-register-production-editor/launch.json` retain process/endpoint ownership checks. Raw final context/process closure documents safe lease transfer to SAME reviewer `ac61aff0`; ROOT assigns full ID. Resume only after lease verification. No queue/register/progress/TODO/main/push/merge/archive changes.
