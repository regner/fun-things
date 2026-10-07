Independent S02 art / camera / spatial review — 7 October 2026

**Verdict: request two bounded corrections before accepting the desktop fixture handoff.** No P0/P1 finding. Source/export/import ancestry and the reproduced camera evidence are technically accepted within this spike. The overlapping target placement and aliased-key cancellation are rejected as implemented. Whole S02, subjective art/feel selection, early S08 and production acceptance remain pending.

Reviewer: this independent Codex art-review session, using `.agents/skills/art-review/SKILL.md`; no inherited producer conversation, no subdelegation, no fixes or commits. Producer: S02 Codex workstream. Handoff stage: Blender blockout → linked prefab → saved corner placement / desktop exploration, not production assets.

Exact reviewed candidate: **8d5c8d7caf62ef54cc1e90ce7c050e0780eb8d32** on `s02-desktop-camera-controls`.
Exact comparison base: **eb8e9d5c9f92ea95f582603aada6f05ff6b2415e**.
Worktree: `/home/regner/.paseo/worktrees/0u71f39f/s02-desktop-camera-controls`.
HEAD remained exact and the worktree remained clean. At final verification the moving `refs/heads/main` resolved to **62e080000077f5d5b5551883b940aad0f4e2fde0**, rather than the supplied base. This review stayed pinned to the supplied base; it does not review that later main revision or a future rebased candidate.

**1. P2 — The blocked target is embedded in the tall building, contaminating the target/obstruction fixture.**

Location: `tests/fixtures/s02/corner.tscn:51–53`, `TargetBlocked`; related `TallTower` placement at lines 40–42 and `tall_prefab.tscn`'s 8×60×8 solid box.

Observed geometry: TallTower is centred at (10,0,-12), so its solid footprint is X=[6,14], Z=[-16,-8]. TargetBlocked is centred exactly at (6,0,-12). Its 0.38 m radius capsule penetrates the tower by 0.38 m, and its visible 0.75 m wide body also straddles the wall. An independent engine `intersect_shape` using the target's actual saved shape/transform and World mask returned `TallTower/Collision/Body`. This is an actual physics query, not solely a bounds inference. The reproduced alley/tower captures show the resulting partial coral/amber sliver at the tower's west wall.

Impact: the hidden-target case mixes perspective occlusion with an invalid occupied target placement. It cannot cleanly establish visibility or blocked-to-clear aiming around a corner for an actor-sized target in free space. The existing blocked ray does hit EastCorner first, so this does **not** invalidate the observed world-ray blocking or muzzle protection results; it invalidates this placement as representative target/readability evidence. The asset/scene contracts require deliberate collision envelopes and meaningful movement/query checks; this overlap is not documented as an intentional penetration test.

Minimal fix / owner: S02 world-fixture integrator should move TargetBlocked fully outside solid world collision while retaining a deliberately blocked view from the south. Adjust the corresponding firing poses/expectations if necessary; preserve its world ID, linked prefab and tower heights. Add a World-overlap assertion for target placements. Do not solve this by changing the tower collision or hiding the target mesh.

Retest: fresh import; no solid-world overlap for both targets (allow the intended ground contact); blocked shot from the south; move around the relevant corner to obtain a clear hit; matching native 1280×800 captures showing the target before/after obstruction. Retain query outcomes separately from images.

Evidence: `/tmp/s02-art-review-extra-8d5c8d7/probe.json` (`target_blocked_world_overlaps`), `probe.gd`, `probe.log`, `independent_tower_edge.png`, and `captures/alley_42.png`.

**2. P2 — Releasing either alternate binding cancels an action whose other key remains held.**

Location: `tests/fixtures/s02/desktop_input.gd:31–38`, especially `_held.erase(action)` at line 36; `project.godot` binds W/Up, S/Down, A/Left and D/Right in pairs.

Reproduction through real viewport input routing: focus the collector, press physical W, press physical Up, then release Up while W remains pressed. `sample().move` changes from 1.0 to 0.0. The independent graphical run retained both samples. The collector stores only action state and erases it on any bound key's release; subsequent OS key-repeat echoes are deliberately ignored, so the still-held W does not restore movement until pressed again. The same cause applies to the other paired movement/turn bindings.

Impact: supported keyboard inputs can stop movement/turn unexpectedly when a tester overlaps the advertised alternatives. This is a concrete desktop-control defect, separate from subjective GTA2 tuning or unsupported handheld input.

Minimal fix / owner: S02 input owner should aggregate held physical bindings per action, clearing all held bindings on suspension/focus transitions and continuing to reject stale echoes. Keep device handling outside motion simulation; do not replace facing-relative controls or weaken focus cancellation.

Retest: overlapping aliases in both release orders for forward/back/left/right, actual motion/turn continuation while one alias remains held, neutralization after the last release, and the existing focus/menu/native minimize regression. The supplied test checks W and focus, but not simultaneous aliases.

Evidence: `/tmp/s02-art-review-extra-8d5c8d7/probe.json` (`alias_both_pressed.move=1.0`, `alias_w_still_held.move=0.0`), `probe.gd`, `probe.log`.

**Independent visual and source observations**

Read AGENTS, TODO S02/S08 and preparation/deferral context, ratified `docs/design.md`, accepted art direction/world layout, asset/source/prefab/scene/API/development contracts, S01 record and fixture contracts, and the S02 handoff. Inspected the complete 149-path base-to-candidate change inventory, added source/scripts/scenes/settings/contracts, structured evidence and diagnostic logs. The baseline S01 source, exports, fixtures and tools are unchanged. TODO changes are additive three-line desktop evidence notes; the existing preparation/access limits and acceptance gates survive the supplied-base comparison.

Visually inspected the actual accepted concept PNGs: `i-perspective-high-rise.png`, `e-cars-people-study-v2.png`, `f-roof-shapes.png`, `g-weapons-effects.png`, `j-high-rise-families.png`. Compared all seven current S02 PNGs at their actual native dimensions. The isolated independent capture run reproduced **all seven byte-for-byte**, including 42°/50° start/alley views, tower-edge cutaway, between-towers, and held weapons. These are real Forward+ renders, not reconstructed illustrations. Also retained an independently driven start view, tower-edge view and a diagnostic oblique overview. That overview deliberately changes only the temporary runtime camera and is **not** an alternative gameplay camera proposal.

The saved gameplay camera is perspective, vertically downward, fixed world yaw, height 47 m, near 0.1/far 160 m; inherited wide variant is 50°, base is 42°. The 6/46/60 m buildings exercise below/near/above-camera height. Perspective facade expansion and near-camera clipping are present rather than being evaded by lowering towers or tilting the gameplay camera. At 42° the actor remains very small (recorded shoulder span about 17.139 px, versus 14.109 px at 50°). The supplied projection measurements reproduce, and no aspect-ratio-only device claim is made.

The local marker and ivory arm separate the player from the ground in the checked states. The tower-edge disc restores the held pose but creates a conspicuous circular boundary. Large cobalt facade areas dominate the right side of that view; tower shadows are extensive. These are visual judgments and useful refinement inputs, **not ratified tuning or additional blocking defects**. The fixture reasonably demonstrates broad bevelled blockout masses, not the accepted roof-family inventory, facade detail, shared humanoid rig or production city composition. A 4 m physics passage is traversable; the 0.1 m roof overhang on each side is decorative and intentionally narrower in projected appearance.

Weapon study: launcher length is the clearest distinction; pistol and SMG are difficult to identify at native scale, and much of the common silhouette is the extended arm/shadow. The accepted side-profile sheet does not prove overhead recognition. The study also places the SMG over the pale strip while the other two stand over dark ground, so a controlled next comparison should use matched backgrounds and headings. Keep the documented bounded geometry/contrast refinement pending under S02/M1-C1; do not require a finished weapon/animation system for this spike. Cutaway shape, marker, 42° choice, turn rate and 5/3 m/s speeds all remain unratified subjective choices.

Provenance was checked in both directions: saved placed instances → reusable wrappers/actor/studies → nine linked GLBs and importer sidecars → declared collections/members in one committed `.blend`. Reverse resource searches found the documented consumers; corner_wide inherits only the owned camera FOV. No editable imported-child override, copied vertex array, runtime-authored static hierarchy or Godot-generated render primitive was found in S02. Source `.gdignore` remains present. Collision is explicit saved Godot shape data, separate from imported render meshes.

Blender MCP independently returned “Could not connect to Blender.” Isolated Blender CLI opened the committed source without saving it and exported to `/tmp`. Observed Blender 5.2.2 LTS, build d13f752e3b9c, Metric scale 1, nine export collections, 59 objects, no linked libraries or images. All inspected object scales/rotations are applied, no modifiers remain, mesh polygons are triangulated and smooth. Declared members match actual source objects. Byte-identical nine-output reexport establishes freshness more strongly than file existence. Original Codex authorship is documented in the handoff/bootstrap trail; no external asset dependency was found.

Independent imported bounds and socket measurements (Godot +Y up / -Z forward; identity model roots):

| Asset | Imported AABB minimum; size, metres | Contract observation |
| --- | --- | --- |
| actor | (-0.375,0,-0.6); (0.915,1.8,0.8) | 0.75 m jacket plus asymmetric right arm; feet at datum |
| ground | (-32,-0.2,-32); (64,0.215,64) | Road top Y=0; decorative strip actually rises 0.015 m |
| low / near / tall | (-4.1,0,-4.1); (8.2,6/46/60,8.2) | Roof overhang distinct from 8 m solid mass |
| target | (-0.375,0,-0.2); (0.75,1.8,0.4) | Separate 0.38 m radius / 1.8 m capsule |
| pistol | (-0.09,-0.09,-0.42); (0.18,0.205,0.42) | Full bounds include sight; handoff body dimensions are smaller |
| SMG | (-0.14,-0.12,-0.72); (0.28,0.265,1.02) | Includes rear stock and sight |
| launcher | (-0.24,-0.21,-1.1); (0.48,0.42,1.21) | Includes rear bell |

`socket_grip` imports at (0.43,1.2,-0.6), identity basis. Weapon muzzle markers import at local (0,0,-0.42/-0.72/-1.1), identity basis. Saved actor weapon mount and physics-local pistol muzzle (0.43,1.2,-1.02) match the source. No corrective wrapper scale/rotation conceals an axis error. The handoff's “flush” walk strip description is approximate: the actual 15 mm visual elevation has no separate collider. This does not establish curb/step handling.

Imported palette/material slots remain source-linked, with local per-building shader materials instead of shared-resource mutation. The cutaway changes rendering only; shape/mask/placement checks and post-cutaway physics outcomes agree. There are no textures, normal maps, alpha VFX, rigs or clips to certify in S02. Default per-asset automatic LOD/shadow-mesh settings are retained, with no global compression change; transitions/cost are unmeasured. No triangle/texture budget is invented here.

**Checks actually executed and retained evidence**

Exact engine: `/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`, reporting `4.8.dev7.official.c971f93e7`.
Exact gdstyle: `/home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle`.
Graphical runs report Forward+, Vulkan 1.4.312, NVIDIA GeForce GTX 1070, 1280×800 on the Linux desktop. This is not a performance measurement or packaged target proof.

| Command / check | Actual result and evidence |
| --- | --- |
| `python3 tools/script_checks.py --godot <exact> --gdstyle <exact> --output /tmp/s02-art-review-checks-host-8d5c8d7` | Exit 0. Pinned format/lint pass; fresh compiler import passes; 21/21 separate owned-script compilations pass, including unused/editor scripts. Manifest, setup, per-script stdout/engine logs retained in that directory. |
| `python3 tools/s02/run.py --godot <exact> --output /tmp/s02-art-review-outcomes-host-8d5c8d7` | Exit 0. Import, outcome checks and persisted hashes pass; no runtime warning/error. `summary.json`, `outcomes.log`, `identities.json`, `import.log`. Temporary profile omits development autoload/editor plugins. |
| `python3 tools/s02/reexport.py --output /tmp/s02-art-review-blender-8d5c8d7` | Exit 0. Nine byte-identical GLBs; no embedded images/extensions. Source/output fingerprints and complete Blender log retained. |
| Isolated `blender --background <committed source> --python /tmp/s02-art-review-extra-8d5c8d7/source_audit.py` with private config/cache | Exit 0. No source save. `source.json`, `source.log` retain measured objects/transforms/materials/bounds. |
| `python3 /tmp/s02-art-review-extra-8d5c8d7/run_graphical.py` | Exit 0; each child exit 0. Original capture script, original focus runner, and independent probe in isolated copied project. `graphical-results.json`, `captures.log`, `focus.log`, `probe.log`, PNGs and `probe.json`. |
| `GODOT_BIN=<exact> python3 tools/s01/clean_import.py --logs /tmp/s02-art-review-s01-8d5c8d7` | Exit 0. S01 clean asset import/resources pass, 56 persisted files unchanged; all seven focused negative probes reject their intended corruption. Actual failure logs inspected; missing-source probe is in `s01-run.log`. |
| Recovered live editor's installed toolkit: `node /tmp/s02-art-review-extra-8d5c8d7/editor_socket.mjs --roundtrip` | Exit 0. Open/save/close/reopen/save/close for actor, ground/low/near/tall/target prefabs, weapon_studies, corner, corner_wide and focus_runner. No unsaved changes discarded. `editor-roundtrip.log`, `editor-socket.json`, before/after hashes: no persisted differences. |
| Candidate evidence binding | All 60 files in `validated-files.json`, all 10 source/export fingerprints and the 11-scene roundtrip fingerprints matched current candidate files. All seven reproduced PNGs byte-identical. |
| Diff/cleanliness | HEAD exact; clean tracked/untracked status. `git diff --check` on owned source/docs outside evidence succeeds. Full diff check reports whitespace/blank-EOF in raw retained engine logs only; retained in `diff-check.log`, not treated as gameplay defects. |

Meaningful behavior independently re-executed through production APIs: 5 m forward and 3 m reverse in one second; 90° turn without strafe and subsequent facing-relative movement; wall stop at (6,0.001,0.38021); passage and northeast corner traversal ending about (3,0.001,-9); clear target ray; world-blocked ray; centre-to-muzzle near-wall prevention; bounded held firing; nonfinite movement neutralization; routed physical W/Space and focus/menu cancellation. Independent two-second reverse/turn stepping kept camera basis fixed; after 0.6 seconds idle, follow-anchor error was about 0.000203 m. These are algorithmic motion/follow observations, not human comfort or latency acceptance.

The native focus runner observed held movement/fire, real minimize/focus loss, stopped at (0,0.001,3.499997) with two shots, restored native focus and stayed neutral. Its result was `failures: [], os_focus_loss: true`. Held key events are injected, not physical human presses. This proves the bounded minimize notification path only, not Alt-Tab with physical keys, general OS lifecycle behavior or suspend/resume.

Initial restricted runs are retained separately: `/tmp/s02-art-review-checks-8d5c8d7` and `/tmp/s02-art-review-outcomes-8d5c8d7`. Their runners exited 1 because editor import logged `_sock == -1`, `ERR_CANT_CREATE` and null-image diagnostics in the restricted environment; all 21 individual compile results and runtime outcomes nevertheless passed. Normal specific escalation for host sockets/display made the fresh reruns clean. No blanket diagnostic suppression was used.

Blender reexport retains the exact known optional MeshOptimizer-library error; generated GLBs were independently rejected if stale or containing extensions/images and passed. Shared editor recovery logged the existing toolkit warning that 4.8 is newer than its tested 4.7 version. Recovered roundtrip produced no new script/error diagnostics. Historical candidate logs contain earlier authoring/focus failures and are not reclassified as successful runs. Full-project plugin/export compatibility is not inferred from isolated profile checks.

**Technical acceptance boundaries**

| Scope | Status |
| --- | --- |
| Source provenance, fresh explicit exports, imported axes/bounds/sockets, linked reusable ancestry | **Accepted — technical spike only**, within measured sources/consumers. |
| Saved composition, IDs/UID dependency agreement, inherited camera override and live save/reopen | **Accepted — technical spike only**; no tracked save diff. |
| Actual vertical fixed-yaw perspective captures, below/near/above-camera fixture, desktop comparison evidence | **Accepted as reproducible evidence**, not accepted camera tuning or whole-district obstruction solution. |
| Existing wall/passage/corner movement, clear/blocked/muzzle query outcomes, automated minimize cancellation | **Accepted within the executed cases**; no multiplayer or human-input equivalence claim. |
| TargetBlocked placement / representative target-readability handoff | **Rejected pending finding 1 correction/retest.** |
| Simultaneous supported keyboard aliases | **Rejected pending finding 2 correction/retest.** |
| Native-scale held-weapon recognition, local marker/cutaway appearance, camera/turn/speed feel | **Pending S02 / Regner selection**. One bounded 1–2 day follow-up should compare matched held views and human corner/aim/reverse/focus notes. |
| Full S02 completion; driving/camera transfer; world seams/routes/spawns/boundaries | **Pending S02/S04/S06**. This flat corner has no gravity, curbs/slopes, vehicles, district limits, derived navigation or minimap. |
| Performance, culling/LOD transitions, Mobile comparison, load/overdraw and input-to-visible p95 | **Pending S07/S08 and integrated validation**; no measured cost or FPS acceptance. |
| LCD and OLED Deck native 1280×800/60 FPS, built-in controls, Gaming Mode, hosting/joining and suspend/resume; early engine/input decision | **Required and UNPROVEN; deferred under the existing no-device record.** Desktop size/rendering cannot accept these. No devices/accounts requested or acquired. |
| Windows/Linux packaged exports, full plugin/native compatibility, live Steam route | **Pending existing S03-S/S08 owners**, with the multi-account access limit preserved. |
| Animation/rig/death bounds, vehicles, damage/combat, mesh VFX, texture/normal-map workflows, network collision transitions | **Not applicable to this bounded implementation**, with future product acceptance still pending its owning tasks. No networking added or required for this review. |
| P0-GATE and production art/gameplay acceptance | **Pending, unchanged.** No gate waiver, target reduction or whole-S02 removal. |

Input, motion, aim query and presentation have separate owners; the fixture coordinates their calls. No network authority claim is introduced. Future authoritative/predicted implementations still need equivalent rules and their own real-process evidence. Screenshots certify none of traversal, latency, performance, load or Deck input.

**Final shared state / process cleanup**

Initial toolkit read confirmed this worktree, only `res://tests/fixtures/s02/editor_harness.tscn` open, and no unsaved scenes. Later the originally reported PID 146968 was absent; its existing log ended with orderly MCP stop/deregistration. The cause of that exit is not established by this review. The stalled exposed-tool roundtrip was cancelled and hashes confirmed no persisted changes. No unrelated process was killed.

Restored the exact pinned shared editor on this project/harness as PID **167101**. The exposed MCP connector remained disconnected after recovery, so a temporary Node client authenticated to the installed toolkit's own localhost WebSocket; it used the same scene/save handlers, without changing vendor code, pins, configuration or exposing the session token. Final recorded `editor_state()` reports exactly this worktree, only the harness open, `unsaved: PackedStringArray()`. All inspection tabs were saved and closed. No game is running; all verification Godot/Blender children and temporary socket clients exited. Final host process inventory contains only that replacement shared editor, intentionally left saved and quiescent for the lease handback.

Final tracked diff: none. No edits or commits made. Durable report: `/tmp/s02-art-review-8d5c8d7.md`; supplementary evidence paths above remain under `/tmp`.
