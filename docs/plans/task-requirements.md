# Task-specific requirements

Open acceptance omitted from the concise [task list](../../TODO.md). Spike records and
canonical guides own their technical detail; this index carries only task-specific
qualification and enough outcome detail for dispatch.

## Foundations

- **P0-PROFILES:** Create a small independently reviewed profile set using the existing
  [proposal](../workflows/p0-profiles-proposal.md), [evidence](../workflows/p0-profiles-evidence.md)
  and [review](../workflows/p0-profiles-review.md) for readiness. Configuration stays
  deferred/outside P0-GATE until separately authorized. Then verify exact supported
  settings/readback and representative launches/effective boundaries; do not install now.
  Reconcile historical Codex modes/features and stale pending/lease/revisit notes with
  ROOT's 8 October 15:53Z zero-profile/pi inventory and accepted pi Sol HIGH/Luna HIGH
  sessions. Those Codex fields are not a pi launch recipe; notes confer no permissions.
- **S02:** Settle desktop camera/control/aim and feel. Resume stopped drawability only
  with a changed authorized condition and explicit grant; Deck needs native evidence.
- **S03-S:** Public API/interface research is accepted; native integration/testing is
  deferred, not accepted. Eventual proof is admitted gameplay traffic over actual Steam,
  not lobby success or ENet through a lobby; testing waits for authorized access.
- **S03-R:** Close drawn owned/remote response and feel; any separately commissioned
  prediction must share simulation rules and exclude replay side effects. Historical
  response p95s were measured under the ENet bandwidth defect found in S08; re-measure
  (Linux and the target platform) before using them for feel decisions. Windows drawn
  technical response now exists (post-fix p95 123/273/379 ms physics); feel stays open.
- **S04:** Ratify car handling, dimensions, recovery, seat/control and prediction choices;
  rerun affected cases after S02 choices. Historical response figures are confounded by
  the S08 ENet defect. Post-fix Windows drawn runs pass all profiles (p95 90/277/386 ms).
- **S05:** Disabled-VSync image attempt failed at endpoint-binding proof before live/late
  launch; no workload PNG/VSync evidence or image-review credit. Attempt consumed; no
  retry. Remaining full acceptance includes drawn eight-slot saturation and live-versus-
  hydrated presentation, policy ratification and affected final-dimension checks.
  Cosmetic capacity cannot limit chains; settled hydration is not in-flight proof.
- **S06:** Ratify drawn layout/crossing/minimap against final body envelopes; partial
  topology is not production traffic, recovery or capacity evidence.
- **S07:** Sustained primary-T driver is accepted (57 traversals over 600 declared
  seconds); do not reopen or repeat it. It proves no graphical calibration/capacity.
  Graphical T and capacity remain open: named hardware/build, telemetry, authorized
  drawability, two-sector and six-block loads, four views, bursts and one bounded growth
  axis; record costs, limiting axis/headroom and decisions. Desktop does not certify Deck.
  [Source-only representative preparation](../spikes/s07-representative-preparation.md)
  records the pre-P0 mapping, individually commissionable slices and unexecuted proposal.
  Remaining prerequisites: Regner's representation/count/diversity/final-envelope/budget
  decisions; saved six-block content/bakes, real population/player/car/combat lifecycle,
  four-rig codecs/journal/reset driver and named graphical telemetry. Comparator also
  needs genuine trial-reset and eight-effect draw receipts. No M1 completion mandate
  or proxy/empty-load acceptance; T is technical, R/G remain blocked, not waived.
- **S08:** The original-main 20 ms held/resync stall is explained and fixed: the
  pinned `ENetMultiplayerPeer.create_server` passes its channel count as incoming
  bandwidth, so client unreliable held input was throttled away. With the
  S03Transport workaround, the exported saved S08 main passes the full matrix in
  Windows RELEASE and DEBUG with zero diagnostics ([Windows record](
  ../spikes/s08-windows-observation.md)). Remaining: a Linux re-run of the original main;
  the Linux-only release `tree_exited` diagnostics (consistent with open upstream PR
  #123998), which need an engine fix/pin decision, not `.bind` spelling or suppression;
  export delivery/target compatibility; ENet with Steam uninstalled/stopped and
  optional-service failure; Deck/Gaming Mode; graphical/input. Steam/device testing
  is deferred until access. Historical card/records: [source-first diagnosis](
  ../spikes/s08-source-diagnosis.md) and [lifecycle](../spikes/s08-release-lifecycle.md).
- **P0-GATE:** Review foundations and ratify product scope, art/layout/camera/control,
  implementation contracts and budgets. Partial research/proofs are not acceptance;
  record unresolved items or explicit scope decisions. P0-PROFILES is not a prerequisite.

## Checkpoint follow-up

Completed discovery reconciliation: [P0-DOC14 record](../reviews/p0-doc14.md).

## First milestone

- **M1-A1:** Deliver standalone/ENet and selected Steam friend sessions; menu flows must
  handle cancel, stale/failure/host loss and cleanup. Only host/standalone can reset.
- **M1-A2:** Share rules offline/authority/permitted prediction; handle focus/expiry,
  respawn and reset rehydration before input while rejecting stale-match commands.
- **M1-A3:** Persist validated audio settings with defaults/recovery and live preview;
  device settings cannot mutate shared gameplay.
- **M1-A-GATE:** Validate two exported processes, settings and lifecycle/reset/error flows;
  test ENet without Steam and Steam gameplay transport between authorized accounts.
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
  art families. Use S06 topology/S07 capacity decisions to compose saved sectors, routes,
  play space, spawns and boundaries; preserve placement and prove seams/clearance/readability.
- **M1-C3:** Implement bounded host-owned pedestrians/traffic, legal routes, crossing and
  blocked/stuck recovery, NPC transfer, late joins and reset without moving city content.
- **M1-C4:** After M1-A2 and the S06 contract (covered by P0-GATE), build the road map
  from shared city data and local entity marker; align with M1-C2 when the district is ready.
  Check walking/driving/late-join seams and read HUD values from gameplay owners.
- **M1-D1:** Build reproducible local/CI checks that catch owned code/resource/gameplay
  violations, including unused scripts, without broad suppression or copied formulas.
- **M1-D2:** Playtest multiplayer feel, camera/aim, driving, spectacle, exploration,
  menus/focus/controller and audio; fix findings or have the user scope them out.
- **M1-D3:** On named hardware, verify ratified performance/capacity and bounded adverse-
  network lifecycle through real processes/APIs; measure frame/physics, draw, memory,
  bandwidth, queues and response. Test ENet/Steam independently; culling cannot stop
  required simulation and optimization needs evidence.
- **M1-D4:** Export selected targets with exact templates/identity/exclusions and verify
  launch/input/audio/network/external routes. Retain results/rollback, preserve VCS
  delivery and use the existing private Steam branch when authorized.
- **M1-GATE:** User reviews the ratified playable district, gameplay/population/minimap,
  readable feedback, audio/settings, menu/lifecycle/reset, multiplayer, feel, targets and
  delivery. ENet and Steam friend playtesting are distinct; unavailable evidence stays open.
