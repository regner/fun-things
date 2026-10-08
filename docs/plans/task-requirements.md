# Task-specific requirements

Open acceptance omitted from the concise [task list](../../TODO.md). Spike records and
canonical guides own their technical detail; this index carries only task-specific
qualification and enough outcome detail for dispatch.

## Foundations

- **P0-PROFILES:** Keep this as a Paseo profiles task for later review. It is
  non-blocking and outside P0-GATE; do not configure or install profiles now.
- **S02:** Implement the ratified 47 m, north-up 42° camera and replace tank turning
  with normalized screen/world-relative WASD movement at 5 m/s, instant start/stop,
  mouse-ground facing each physics tick and left-click fire. Remove building cutaway;
  keep held weapon silhouettes. Revalidate focus and control/aim/feel on desktop;
  gamepad and Deck work are deferred.
- **S03-S:** The initial game uses ENet only. Review session and transport APIs for
  a later Steam adapter covering friend joins, lobby identity mapping, reliable and
  unreliable lanes, and connection lifecycle. Steam-specific implementation and tests
  are deferred.
- **S03-R:** Implement required local-character prediction with shared movement rules,
  replay limited to permitted local simulation, no replay side effects and authoritative
  corrections winning. Then close drawn owned/remote response and desktop feel. Historical
  response p95s measured under the S08 ENet defect remain history, not acceptance.
- **S04:** Add a standalone drive scene for handling review. Cars cannot fire; exit
  succeeds only below 0.5 m/s and otherwise returns `EXIT_MOVING`; a disconnected
  driver's car coasts without braking. Local-driver prediction is required under the
  same replay/correction rules as S03-R. Rerun affected cases after S02 choices.
- **S05:** Remove the on-screen explosion cap: every explosion receives its effect.
  Start from 100 car HP, 100 blast damage, 4.1 m radius, no falloff or obstruction,
  0.1 s chain delay, 5 s wreck duration and friendly fire/self-damage always on.
  Remeasure effect cost and update saturation evidence without dropped presentations;
  settled hydration is not in-flight proof.
- **S06:** The grey-block 9 m roads, 4 m sidewalks and 48 m extent are accepted.
  The minimap's top-right position is accepted; its size and look are not. Commission
  and iterate whole-UI mockups, then revalidate layout/crossing/minimap readability.
  Partial topology is not production traffic or recovery evidence.
- **S07:** Reframe this as a visual/graphical environment-scaling investigation, not
  a requirement or capacity gate. Build saved city variants of increasing block counts
  (for example 6, 24, 96 and 384; stop early at a limit) from existing grey-block sectors
  and building prefabs. Measure load time, RAM/VRAM, node/static-collider counts and
  60-capped frame time along a 42° camera route. Report a cost-versus-block envelope,
  caveating shared grey-block assets versus production-art variety and no Deck result.
  Network, AI and population are out of scope; budgets are guidance only. Do not repeat
  the accepted sustained primary-T driver.
- **S08:** Stay on Godot 4.8-dev7. Keep the S03Transport workaround for the upstream
  ENet bandwidth defect and retain the offline upstream review; do not file the proposed
  issue yet. Windows is the current development platform. Linux original-main and
  Linux-only release-diagnostic confirmation remain follow-up for a Linux machine and
  do not block proceeding. M1 targets Windows/Linux desktop; Deck is later.
- **P0-GATE:** Review foundation evidence against the 8 October owner decisions.
  Do not reopen the ratified camera/control, vehicle, explosion, layout, ENet or target
  choices without a new owner decision. S07 budgets are guidance, Linux S08 confirmation
  is follow-up, and P0-PROFILES is not a prerequisite. Record other unresolved items.

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
