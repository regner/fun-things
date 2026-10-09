# Task-specific requirements

Open acceptance omitted from the concise [task list](../../TODO.md). Spike records and
canonical guides own their technical detail; this index carries only task-specific
qualification and enough outcome detail for dispatch.

## Foundations

[Owner instruction 12](../reviews/owner-decisions-2026-10-08.md) authorizes S09–S16
and the audit-derived tasks in
[section 4 of the readiness audit](../reviews/p0-readiness-audit-2026-10-08.md).
Their quantitative criteria are orchestrator proposals derived from the current product
budgets, not ratified values; the owner reviews them at P0-GATE.

- **P0-TOOLING:** Completed. The [baseline repair](../spikes/p0-tooling.md) made the
  canonical script check green, established complete Python discovery, selected the
  cross-platform `python` spelling, ignored GodotSteam temporary imports and stripped the
  MCP autoload from compile mirrors. Linux execution remains a production-CI follow-up.
- **P0-TOOLING-2:** Completed. The [runner-safety follow-up](../spikes/p0-tooling-2.md)
  added exact 60 FPS guards, withdrew unsafe uncapped modes, moved contention sampling
  outside timed cases, centralized measurement identity and added incremental log reads.
- **P0-PROFILES:** Retained for later Paseo review. It is non-blocking and outside P0-GATE;
  do not configure or install profiles now.
- **S01-W:** Completed. The [Windows supplement](../spikes/s01-w.md) used Blender 5.2.2
  LTS / glTF exporter 5.2.40 and reproduced both committed S01 GLBs byte-for-byte.
- **S02:** The [implemented controls](../spikes/s02-controls.md) use the ratified 47 m,
  north-up 42° camera, normalized 5 m/s world-relative WASD, mouse-ground facing,
  left-click fire and no cutaway. Physical Alt-Tab, control/aim feel and roof/weapon
  readability remain human checks in the [gate packet](../reviews/p0-gate-packet-2026-10-09.md).
- **S03-S:** Completed as an abstraction review. The
  [ENet-first result](../spikes/s03-s-abstraction-review.md) specifies provider IDs,
  optional directories, opaque connection generations, four logical streams and safe
  close/reuse. Actual Steam implementation/testing remains deferred beyond M1.
- **S03-R:** Technical response and expiry work is complete. [S03-L](../spikes/s03-l.md)
  applies exact decision-age telemetry and a fresh adverse run passes the unchanged 250 ms
  rule. Physical feel and drawable remote continuity remain human/production checks.
- **S03-L:** Completed diagnosis. Corrected passing evidence still shows a contended
  direct-loopback p95 of 317 ms, so prediction/S12 carry a provisional 350 ms p95 Windows
  authoritative-loop allowance until quiet Windows and later Linux evidence replace it.
- **S03-P:** Completed bounded implementation. [Foot prediction](../spikes/s03-prediction.md)
  shares S02 motion/collision rules, restores authority and replays bounded side-effect-free
  history. Selected predicted physics p95 is 19–29 ms and drawn p95 39 ms, all contended.
  P0-GATE must approve the dated three-frame pending-lag/oldest-valid queue revision.
- **S04:** The technical car body and [standalone drive scene](../spikes/s04-drive-scene.md)
  are complete. Owner handling feedback/F12 tuning remains open. Cars cannot fire; exit
  requires speed below 0.5 m/s; disconnect coasts. Driver-death behavior needs a separate
  owner decision.
- **S04-P:** Completed bounded implementation. [Car prediction](../spikes/s04-prediction.md)
  shares drive/body rules and bounds replay/history, stopped exit and disconnect coast.
  Normal passes; the post-rebase adverse correction p95 of 0.576 m misses the 0.5 m target,
  so production still needs clean adverse and moving-contact acceptance.
- **S04-T:** Completed bounded mechanism. The [transition fixture](../spikes/s04-t.md)
  proves authoritative seat races, `EXIT_MOVING`, blocked retention, AI release, disconnect
  coast and prediction-domain transfer under normal/adverse profiles. Production must
  address the retained 6.999 m adverse moving-traffic correction, real clearance and full
  death/destruction/reset races.
- **S05:** Bounded chain logic and uncapped fixture presentation are complete. The
  [chain record](../spikes/s05.md) completes 12 explosions/144 visits; the
  [presentation supplement](../spikes/s05-uncapped-effects.md) draws 12 and drops zero.
  Production M1-B3/B4 retains in-flight hydration, real occupants, wreck/contact/reset,
  final-body and lifetime-owned pool work.
- **S06:** The accepted prototype scale/top-right map position and
  [two-sector topology](../spikes/s06.md) are complete foundation inputs. Whole-UI and
  minimap size/look review, final-body reruns and production contested recovery remain open.
- **S07:** Completed planning guidance. The
  [environment envelope](../spikes/s07-environment-scale.md) passed 6/24/96 shared
  grey-blocks and historically crashed at 384. S08-C later loaded current no-cutaway 384
  content. Neither result is a product ceiling, production-art proof or Deck measurement.
- **S08:** Stay on Godot 4.8-dev7 and retain the ENet bandwidth workaround/offline upstream
  review. Windows original-main DEBUG/RELEASE passed. Linux original-main and Linux-only
  diagnostics remain a non-blocking follow-up; M1 still targets Windows/Linux desktop.
- **S08-X:** Completed configuration and Windows smoke. [S08-X](../spikes/s08-x.md) adds
  the real main scene and four desktop presets, verifies addon-free packages and launches
  Windows release with Steam absent. Linux packages were built on Windows; the recorded
  Linux Vulkan launch checklist remains unexecuted. GodotSteam keep/remove awaits owner review.
- **S08-C:** Completed bounded triage. [Current no-cutaway 192/288/384 scenes](../spikes/s08-c-stability.md)
  instantiated; the historical access violation did not reproduce and its cause remains
  unknown. Safe workstation GPU evidence is capped frame intervals plus RenderingServer
  timings. Owner approval is needed to replace the old uncapped design instruction.
- **S09:** Completed foundation prototype. [Traffic evidence](../spikes/s09.md) covers
  24/32 controllers for three ten-minute seeds, bounded recovery and zero sampled overlap/
  gridlock. The 24-car aggregate p95/p99 is 1.165/1.690 ms, a **contended upper bound**.
  Actual bodies, final routes, replenishment and intersection policy remain M1/owner work.
- **S10:** Completed comparison, with a negative production-readiness result. The
  [64-pedestrian evidence](../spikes/s10.md) favors graph kinematics, but normal/flee graph
  p95 medians are 2.654/3.658 ms (**contended**) against the proposed 1 ms share, and
  overlap/stuck quality is unacceptable. P0-GATE decides a follow-up spike versus explicit
  carry into M1-C3; quiet timing cannot erase the behavior findings.
- **S11:** Completed codec/bandwidth direction. [S11](../spikes/s11.md) keeps 1,196-byte
  movement payloads; worst measured host output is 55.16 KiB/s against 256 KiB/s and join
  wire bytes are about 3.2 KiB against 1 MiB. Production baseline/input remain unmeasured,
  and remote drawable smoothness/extrapolation policy is open.
- **S12:** Completed decision prototype. [S12](../spikes/s12.md) recommends 250 ms
  target-only rewind: normal median agreement reaches 89.3% for pedestrians and 62.5% for
  fast cars, while adverse fast-car agreement remains 44.8%. Owner must ratify the rewind
  fairness bound and combat/impact defaults; clients never claim damage.
- **S13:** Completed technical path. [S13](../spikes/s13.md) proves one linked rig with four
  clips/three palettes at 68 live plus 16 dead and presentation-only throttling from 68 to
  30 active mixers. All timing is contended; production art/readability and quiet/Linux
  checks remain M1 work.
- **S14:** Completed automated audio/settings foundation. [S14](../spikes/s14.md) enforces
  exact 8 engine/8 explosion/6 weapon voice caps and settings roundtrip on Dummy/WASAPI.
  Human listening, final assets/licences and attributable sustained audio profiling remain.
- **S15:** Completed technical cost comparison. [S15](../spikes/s15.md) retains all 12/24
  explosion roots; contended 24-full frame p95 is 18.445 ms median. `amount_ratio` did not
  prove a cost reduction. Owner must approve full/reduced/minimum non-dropping tiers.
- **S16:** Completed. The [M1 production plan](m1-production-plan.md) maps owners, fixture
  promotion, tests, ordered work and risks. P0-GATE reviews rather than reopens the plan.
- **S17:** Completed integrated measurement, with a budget miss. The
  [production-schedule comparison](../spikes/s17.md) is 2.394/4.582/6.286 ms
  median/p95/p99 (**contended**), missing the proposed 4 ms p95 before omitted real body,
  prediction and socket costs. Quiet evidence, owner budget allocation and optimization are
  required before treating the host architecture as within budget.
- **Quiet re-measurement:** The quiet record was still in progress while the
  [P0-GATE packet](../reviews/p0-gate-packet-2026-10-09.md) was drafted. Fill every `TODO(QUIET-*)` from the committed record; do not infer values.
- **P0-GATE:** Review the integrated records above against the owner decisions. Record the
  quiet-performance disposition, human checks and one-line owner decisions listed in the
  [gate packet](../reviews/p0-gate-packet-2026-10-09.md#owner-decisions-needed). Linux-only
  S08 confirmation and P0-PROFILES remain non-blocking unless the owner changes scope.

## Checkpoint follow-up

Completed discovery reconciliation: [P0-DOC14 record](../reviews/p0-doc14.md).

## First milestone

- **M1-A1:** Deliver standalone/ENet sessions and Steam-adapter-capable boundaries;
  menu flows must handle cancel, stale/failure/host loss and cleanup. Only host/standalone
  can reset. Steam friend sessions are owner-deferred beyond M1.
- **M1-A2:** Share rules offline/authority/permitted prediction; handle focus/expiry,
  respawn and reset rehydration before input while rejecting stale-match commands.
- **M1-A3:** Persist validated audio settings with defaults/recovery and live preview;
  device settings cannot mutate shared gameplay.
- **M1-A-GATE:** Validate two exported ENet processes, settings and lifecycle/reset/error
  flows with Steam absent. Actual Steam gameplay transport is owner-deferred beyond M1.
- **M1-B1:** Implement vehicle handling and authoritative driver transitions; resolve
  claim/exit/death/disconnect/destruction races and preserve parked-car policy.
- **M1-B2:** Implement the ratified weapons and authoritative damage/death state; reject
  stale fire commands and hydrate late joiners.
- **M1-B3:** Bound/deduplicate chains and complete wreck/collision lifecycle; late join
  and reset restore current state without replaying old effects/work.
- **M1-B4:** Add readable bounded effects and licensed/source-tracked audio; review the
  walk/shoot/drive/chain slice for duplicate feedback, aim/map readability and cost.
- **M1-C1:** Produce ratified buildings, roads/props, character rigs, cars/wrecks, weapons
  and VFX. Preserve Blender-linked sources, catalogue/ancestry and reexport/reload.
- **M1-C2:** Start with approved M1-C1 road/building/prop subsets; don't wait for unrelated
  art families. Use S06 topology and S07 environment-envelope guidance to compose saved
  sectors, routes, play space, spawns and boundaries; preserve placement and prove
  seams/clearance/readability.
- **M1-C3:** Implement bounded host-owned pedestrians/traffic, legal routes, crossing and
  blocked/stuck recovery, NPC transfer, late joins and reset without moving city content.
- **M1-C4:** After M1-A2 and the S06 contract (covered by P0-GATE), build the road map
  from shared city data and local entity marker; align with M1-C2 when the district is ready.
  Check walking/driving/late-join seams and read HUD values from gameplay owners.
- **M1-D1:** Build reproducible local/CI checks that catch owned code/resource/gameplay
  violations, including unused scripts, without broad suppression or copied formulas.
- **M1-D2:** Playtest desktop keyboard/mouse multiplayer feel, camera/aim, driving,
  spectacle, exploration, menus/focus and audio; fix findings or have the user scope
  them out. Gamepad/controller playtesting is owner-deferred.
- **M1-D3:** On named Windows/Linux hardware, verify ratified performance/capacity and
  bounded adverse-network lifecycle through real ENet processes/APIs; measure frame/
  physics, draw, memory, bandwidth, queues and response. Culling cannot stop required
  simulation and optimization needs evidence. Steam transport testing is owner-deferred.
- **M1-D4:** Export Windows/Linux targets with exact templates/identity/exclusions and
  verify launch, keyboard/mouse input, audio and ENet routes. Retain results/rollback.
  Steam private-branch delivery and Deck/gamepad checks are owner-deferred.
- **M1-GATE:** User reviews the ratified playable district, gameplay/population/minimap,
  readable feedback, audio/settings, menu/lifecycle/reset, ENet multiplayer, desktop feel,
  Windows/Linux targets and delivery. Deferred Steam, Deck and gamepad evidence does not
  block M1.

### Owner-deferred follow-up after M1

- Implement and test actual Steam friend sessions, authorized-account gameplay transport,
  external routes, install/update/invite flows and private-branch delivery while preserving
  ENet/offline availability and the abstraction contracts reviewed in S03-S.
- Implement and review gamepad/controller gameplay and menu flow, then validate native
  1280×800 LCD/OLED Deck Gaming Mode, 60 FPS, hosting/joining, suspend and Steam delivery.
