# Fun Things — foundations through the first playable milestone

This list contains remaining work. Remove completed tasks with their resolving
changes; retain evidence in dated decision, spike and review records. Assign a
named worker and budget when starting a task. Partial proofs leave their unmet
criteria open; prototypes require a deliberate productionization decision.

Use [repository guidance](AGENTS.md), [development](docs/development.md),
[assets](docs/assets.md), [multiplayer](docs/multiplayer.md), the
[scene draft](docs/scene-structure.md) and [API draft](docs/api-contracts.md) as
contracts. Keep revised contracts there rather than duplicating them here.
Completed foundation and documentation evidence is navigable through the
[dated checkpoint index](docs/reviews/plan-checkpoints.md) and task prerequisites below.

## Product requirements and scope to settle

The [ratified brief](docs/design.md), [accepted art direction](docs/art-direction.md)
and [city brief](docs/world-layout.md) own scope and gameplay policies. Preserve:

- Playful stylized top-down 3D with GTA2 turn/forward/back controls and a fixed-yaw,
  vertically downward perspective camera; control-model changes need a product decision.
- One exterior district of roughly six connected blocks; custom art, two car
  silhouettes, pedestrians/traffic without modeled occupants, pistol/SMG/rocket
  launcher, vehicle entry/driving/exit, car chains, road minimap, effects and audio.
- Standalone shared authoritative rules and 1–4-player listen-server sessions;
  host loss ends the match. ENet local/LAN works without Steam; Steam friends use
  actual gameplay transport across networks without port forwarding. Choose one
  transport before host/join and retain it until teardown.
- Windows/Linux desktop and Steam Deck LCD/OLED; native 1280×800 and 60 FPS on both
  Deck models, built-in controls and Gaming Mode. Renderer, exact engine/templates,
  frame pacing and simulation/memory/network/load budgets await proof and ratification.
- Existing AppID 5294580, Windows/Linux depots 5294581/5294582 and intended private
  `fun-things` beta branch; live setup/access is S03-S/S08 work, preserving VCS delivery.
- All visible 3D, including blockouts and mesh VFX, comes from committed Blender
  sources and explicit linked GLB exports. Saved scenes own composition/placement;
  no primitive/CSG/generated draw meshes, embedded model copies or runtime city rebuilding.
  Collision/navigation/occluders, shaders/particles, debug overlays and 2D UI/map
  drawing remain separate concerns under the asset contract.

Missions, police/wanted systems, interiors, passengers, detailed civilian simulation,
building destruction, procedural cities, persistent worlds, host migration,
production matchmaking and public store launch remain deferred scope. Additional
stores/platforms receive capability/adapter contracts before selected integrations.

## Phase zero — foundations

### Contracts to validate with spikes

Spikes refine the [ownership](docs/architecture.md), scene, API and source contracts.
[S01 pipeline evidence](docs/spikes/s01.md) and [S03 ENet evidence](docs/spikes/s03.md)
are bounded prerequisites, not production art/gameplay or Steam/Deck acceptance.
The [asset workflow](docs/assets.md), [handoff template](docs/templates/asset-handoff.md)
and [catalogue](docs/asset-catalogue.md) own source/export/prefab handoffs.

### Deferred orchestration configuration

- [ ] **P0-PROFILES — Create Paseo profiles from observed session requirements (configuration DEFERRED).**
  Owner: workflow worker; orchestrator coordinates readiness/review.
  Needs: [reviewed proposal](docs/workflows/p0-profiles-proposal.md),
  [session evidence](docs/workflows/p0-profiles-evidence.md),
  [independent review](docs/workflows/p0-profiles-review.md) and
  [latest dated assessment](docs/reviews/plan-check-2026-10-08-08.md#profile-assessment).
  Remaining: reconcile historical pending S03-R/lease prose and exact proposed notes
  with accepted scope and current routing/lease/retention requirements. Preserve
  original dated samples; supply a dated supplement and independently checked notes
  before authorized configuration. Do not manufacture a specialist session for readiness.
  Review actual task categories, model/effort, capability/permission needs and repeated
  friction against supported provider capabilities. Keep a small demonstrated set,
  with intended use, exclusions and tradeoffs; validate lead/specialist routing separately.
  Follow the [model policy](.agents/skills/paseo-orchestrator/SKILL.md#model-policy-workers-subagents-and-reviewers):
  Sol6.1 medium/high leads; Luna6 high only for very simple delegated work/review;
  Astra only for necessary bounded visual/spatial/modeling specialist subagents with
  explicit question/output/validation/budget. No automatic ultra/broad-access default.
  Done when: a later checkpoint records readiness; exact notes/provider/model/effort/
  mode/features receive independent review; then-authorized configuration and safe
  representative launches prove routing/capabilities, approval boundaries and no
  silent fallback. Record limits, final inventory and next revisit. Configuration
  and launches remain deferred, outside P0-GATE.
  Revisit at full checkpoints (normally 6–8 substantive integrated workstreams or
  milestone transition), meaningful supported routing/capability/permission drift,
  and before configuration. Docs/retention/reviewfix/lifecycle alone do not advance
  cadence; no per-workstream model inventory or extra coordinator/specialist required.

### Documentation checkpoint follow-ups

Completed DOC work stays in its dated records. Use the
[checkpoint index](docs/reviews/plan-checkpoints.md),
[DOC12 stopped S02 discovery](docs/reviews/p0-doc12.md) and
[DOC13 stopped S08 discovery](docs/reviews/p0-doc13.md) before relying on reconciled
records at P0-GATE; these completions do not reopen or close technical proofs.

## Phase-zero technical spikes

Each spike uses `docs/spikes/<id>.md` for question/hypothesis, alternatives, minimum
fixture, tool versions, predeclared criteria, measurements/logs/captures, decision,
limitations and resulting doc/TODO changes. Normally propose 1–2 focused days per
experiment before work; if inconclusive, name the next bounded question and its M1
impact. Save editor mutations before playtests; preserve unsaved work. No full
feature expansion, repeated unchanged experiment or silent contract/pin change.

- [ ] **S02 — GTA2-style foot controls, camera and aiming.**
  Owner: controls/camera proof worker; Regner ratifies feel/product choices.
  Needs: ratified brief, accepted art/city direction, [S01 pipeline](docs/spikes/s01.md),
  [reviewed desktop fixture](docs/spikes/s02.md) and early S08 before handheld acceptance.
  Remaining: usable interactive drawability, native focus-loss/physical-key playtests,
  human feel and camera/control/aim ratification. The
  [accepted stopped drawability record](docs/spikes/s02-drawability.md) failed full
  drawable/viewport/focus criteria; resume only after a genuinely changed authorized
  surface/output condition and explicit ROOT grant, reusing the fixture.
  Evaluate height/FOV/framing, fixed yaw, rooftops/obstruction and targets below/near/
  above camera height; walk/turn/aim/shoot around the corner/alley and focus loss.
  Refine held-weapon silhouettes/aim readability with actual-camera captures/paintovers;
  S04 repeats this while driving. Start with GTA2 controls; alternatives need a product decision.
  Done when: camera/control contract, actor/collision/aim envelope and playtest feel
  targets are evidenced and ratified, including Deck controls/native 1280×800 readability.
  Deck cases remain deferred without hardware; desktop views do not prove them.
  No finished animation or production weapon system required.

- [ ] **S03-S — Steam integration, friend connection and transport proof.**
  Owner: Steam compatibility/proof worker; Regner owns Steamworks/tester access.
  Needs: [S03 boundary](docs/spikes/s03.md), existing-app brief,
  [preparation](docs/spikes/s03-s.md) and
  [accepted stopped compatibility probe](docs/spikes/s03-s-compatibility.md).
  [Accepted upstream evidence](docs/spikes/s03-s-upstream-peer-evidence.md) assesses
  three immutable peers; none meets the unchanged streams/bounds/lifecycle.
  [Valve API/interface proposal](docs/spikes/s03-s-valve-api-interface.md) maps public
  APIs and specifies a narrow native boundary; it selects no integration or pin.
  Remaining: separately commission exact SDK/native/Godot applicability, bounded
  ownership/receipt and correlated callback retirement before implementation, or
  keep Steam unavailable. Preserve four streams/modes/limits and admission ownership;
  no five-lane workaround, reliable fallback or assumed drain. Actual Steam testing
  is postponed; the live prerequisites/proof below remain deferred, not waived.
  Before live proof, verify app type/release state, distinct authorized testers/package
  entitlement, depot OS/package inclusion and launch settings; confirm/create the
  intended private branch and record its install/access route. No new app required.
  Two-account/separate-machine/network testing remains deferred until access exists.
  Done when: initialize the existing app, create/join a friend lobby and exchange
  the same admitted baseline/intent through a real Steam peer across networks without
  port forwarding. Retain relay/connection diagnostics, native API/export compatibility,
  transfer modes/channels/limits and cleanup after cancellation; settle integration/
  SDK/native pins and private access recipe. Lobby success or ENet via a lobby cannot
  satisfy gameplay transport. Full invite races/gameplay belong to M1-A/D.

- [ ] **S03-R — Networked on-foot responsiveness.**
  Owner: foot-response proof worker; Regner ratifies feel; ROOT assigns fixture lease.
  Needs: [S02 desktop handoff](docs/spikes/s02.md#reviewed-desktop-handoff),
  [S03 boundary](docs/spikes/s03.md) and
  [accepted bounded ENet result](docs/spikes/s03-r.md).
  Remaining: measure predeclared owned visible movement/camera/aim response and
  remote presentation continuity on a drawable two-process fixture under latency/loss,
  with human feel review. Distinguish physics latency, drawn response, stationary
  convergence and prediction correction; headless timing cannot close acceptance.
  If warranted, commission a separate bounded shared-rule prediction trial. Predeclare
  newest-held intent per host tick versus numbered steps/acknowledgements, repeated
  values/supersession, contact restoration, history/overflow/resync and replay side-effect
  exclusion. Actual S02 movement remains the sole rule owner; one acknowledged sequence
  is not necessarily one simulation step. Require matching-tick correction and adverse convergence.
  Done when: foot interpolation/prediction/reconciliation decision, limits and evidence
  meet S02 human feel/target choices through ENet and actual S03-S Steam transport;
  include physical keys/native focus and reference-device acceptance. Provisional
  desktop work can proceed and affected cases rerun after S02 choices. Foot prediction
  is independent of cars; original S02/S03 resources stay immutable. Required for M1-A2.

- [ ] **S04 — Arcade car physics and network response.**
  Owner: car-response proof worker; Regner ratifies handling/dimensions/controls.
  Needs: [S02 envelope](docs/spikes/s02.md), [S03 boundary](docs/spikes/s03.md),
  [accepted desktop body/ENet result](docs/spikes/s04.md),
  [source handoff](docs/assets/s04_kit.md) and [body/seat contract](docs/spikes/s04-contracts.md).
  Remaining: drawable owned car response/camera/target/roof evidence, physical input/
  native focus/handling review, final dimensions/turning/recovery and independent
  car prediction decision. CharacterBody3D is a technical candidate, not a ratified
  product choice. Use the Blender fixture and rerun affected rows after S02 choices.
  Compare simple body/control approaches on a track with fast steering/sliding/braking,
  wall contact and host/client latency/loss through ENet and Steam; VehicleBody3D only
  if useful. Do not assume cross-peer physics determinism.
  If prediction is warranted, predeclare host-tick/held-intent/contact/history/correction
  and replay side-effect expectations before a bounded local-step trial; substantial
  replay scope needs a separate commission. Use [S03-R lessons](docs/spikes/s03-r.md#unavailable-graphical-evidence-and-stop-boundary)
  without inheriting foot prediction. Physics timing is not drawn latency or feel.
  Done when: handling/body/recovery, car prediction, dimensions/turning and seat/control
  contracts are evidenced and ratified, with S02 feel/targets, Steam and LCD/OLED gates.
  Confirm no seated firing/reloading in feel review; specify the full seat race/
  disconnect/exit matrix for M1-B1, passive replica physics and physics-phase pose
  capture. Verify seated resync preserves player/seat/equipment while reauthorizing input.
  Separately bounded desktop preparation can precede full S02/S03-R closure; drawable
  work needs a changed-condition grant, not identical retries or renderer repair.

- [ ] **S05 — Authoritative explosion-chain feasibility.**
  Owner: damage/chain proof worker; Regner ratifies blast/occupant/wreck policies.
  Needs: [S03 boundary](docs/spikes/s03.md), [S04 technical kit](docs/spikes/s04.md#bounded-recommendation-and-next-question),
  [accepted partial chain evidence](docs/spikes/s05.md) and
  [fixture contract](docs/spikes/s05-contracts.md).
  Remaining: exercise the accepted [saved presentation](docs/spikes/s05-saved-presentation.md)
  in eight cosmetic slots with drawn receipts. The [bounded observation](docs/spikes/s05-render-observation.md)
  adds a saved observation camera and natural expiry/ENet evidence, but its two
  graphical groups produced no workload PNGs (final group: two startup callbacks,
  can_draw=false). The single [disabled-VSync image card](docs/spikes/s05-vsync-image-observation.md)
  also FAILed: runner-owned endpoint-binding proof stopped before live/late launch;
  host interrupted, no callbacks/PNG/effective-VSync receipt. Its attempt is consumed;
  no retry follows. Drawn saturation/fallback, readability/cost and live-versus-hydrated
  presentation need a separately authorized protected drawable condition.
  [Source preparation](docs/spikes/s05-effect-preparation.md)
  and node visibility/token reservations do not prove drawn effects.
  Ratify range/obstruction/falloff, delay/order, occupant outcome and wreck/collision
  lifetime; rerun affected spacing/contact rows after final S04/S02 dimensions.
  Preserve the bounded host-owned damage/event-ID/per-tick/queue/effect contract,
  duplicate ShotId rejection after cache retirement, near/far/duplicate/wreck hydration
  cases and 12-car burst: chain work completes despite eight cosmetic slots, with
  queue/work peaks and off-camera outcomes retained.
  Done when: remaining presentation and policy/dimension evidence settles full S05.
  Settled hydration is not during-chain journal proof; occupant sentinel is not an
  admitted player. Full joining/reset/races and sustained capacity belong to M1-B3/B4/D
  and S07. Full S04 feel/dimensions do not block scoped preparation, but the technical
  kit cannot ratify blast spacing/production clearance. Original S02/S03/S04 stay immutable.

- [ ] **S06 — Shared city topology, navigation and minimap.**
  Owner: topology proof worker; Regner ratifies layout/readability/feel.
  Needs: [S01 pipeline](docs/spikes/s01.md), [S02 envelope](docs/spikes/s02.md),
  [S04 geometry](docs/assets/s04_kit.md#measured-technical-geometry), city brief and
  [accepted partial two-sector result](docs/spikes/s06.md)/[contract](docs/spikes/s06-contracts.md).
  Remaining: actual drawn camera/layout/crossing/minimap readability and Regner
  decisions; affected actual body/contact/legal-turn/seam/map/exit reruns after final
  S02/S04 choices. Geometric sensitivity is not changed-body physics or user approval.
  Preserve one saved placement owner: topology references geometry/transforms and
  owns connectivity. Settle sidewalk graph/navmesh and car lane graph/curve representation,
  stable IDs/layers, host AI/controller APIs and explicit bake/update/stale-data rejection.
  Done when: the saved two-sector intersection supports actual sidewalk/crossing and
  legal car routes with aligned road-map seams under final envelopes and readable views.
  Specified bounded blockage/contested-junction/stuck/wreck recovery still needs actual
  M1-C3 integration/checks. Partial saved topology satisfies S07's technical dependency;
  it proves neither production traffic nor renderer/streaming/map maximum.

- [ ] **S07 — Map capacity, top-down culling and growth headroom.**
  Owner: Sol-led capacity-spike worker; Regner ratifies scope/budgets.
  Needs: [research/method](docs/spikes/s07.md), S01 pipeline, reviewed provisional
  S02 camera/controller, actual S02/S04 bodies, partial S06 saved seam/topology and
  relevant S05 chain/effect load. [Static inventory/run cards](docs/spikes/s07-run-cards.md)
  and the [simulation-only sustained saved-reload route driver](docs/spikes/s07-sustained-driver.md)
  supply technical preparation; representative capacity measurements remain unexecuted.
  Primary T still needs named hardware/build/telemetry and authorized real drawability;
  its driver receipt is not graphical calibration. S05 comparator reset/draw gates remain open. Stand-ins cannot certify missing
  gameplay, presentation or residency costs; tokens are not drawable effects.
  Use the [static fixture inventory and concrete run cards](docs/spikes/s07-run-cards.md) to prepare the baseline and growth experiment.
  Minimum remaining experiment: controlled saved imported two-sector baseline,
  six-block reference load and one bounded growth axis at named extent/density/
  variety/population/camera/views. Use graphical host/client, four separated views,
  rapid driving/seams, bursts/off-camera outcomes; retain CPU/GPU/physics percentiles,
  pacing, render/content/resident costs, loading/traversal/lifecycle, AI/query/navigation/
  network costs and last passing/first failing axis.
  Diagnose limits before choosing the simplest culling/LOD/texture/sector organization
  or no change. Unloading/streaming/pooling/batching require measured need and lifecycle
  proof. Saved authored visible 3D stays Blender/GLB-linked; growth does not expand M1.
  Done when: accepted capacity/identity table, headroom/limiting axis, target gaps,
  scene/asset recommendations, reproducible profiling/escalation guide, selected decision
  and bounded owned follow-ups update canonical guides/TODO together.
  LCD/OLED and real Steam cases remain deferred; desktop hardware results cannot select
  Deck budgets/renderer or certify native 1280×800/60 FPS. S06 owns topology, S08 exact
  exports, M1-D3 integrated targets; feel/engine-input/P0/production gates stay open.

- [ ] **S08 — First-target export and service compatibility.**
  Owner: export/service proof worker; Regner owns device/access evidence.
  Needs: [target/pin brief](docs/design.md), S01/S03 evidence, S03-S and
  [desktop preparation](docs/spikes/s08.md), [saved entrypoint/assets](docs/spikes/s08-standard-editor-release.md#bounded-addon-free-outcomes-and-exported-enet-stop)
  and [lifecycle diagnosis](docs/spikes/s08-release-lifecycle.md).
  Remaining desktop work: clean release native-cache teardown and the original saved
  S08 main's full exported ENet proof. New minimal S03 release evidence completes
  held/resync health70, authority/expiry, replication and observed traffic, but strict
  diagnostics fail on two host/six client `tree_exited` errors. The historical
  [saved-main stall](docs/spikes/s08-exported-enet-handoff.md#first-changed-condition-set-handoff-positive-runtime-stop)
  was not reproduced; no causal gameplay fix is established. Under a new scoped grant,
  localize actual release cache registration/comparison and the original entrypoint's
  first stalled boundary/close reason. Bound/unbound callable spelling alone is not
  an identity defect: Godot keys the base comparator. Preserve unconditional release
  mutation, health70/admission/recovery and traffic expectations; require error-free
  bounded teardown. No identical retry, error suppression or inferred diagnosis.
  Preserve original [release observation failure](docs/spikes/s08-linux-observation.md#actual-stopped-observation),
  [private authoring STOP](docs/spikes/s08-release-entrypoint.md#actual-private-authoring-stop)
  and authoring-shutdown diagnostics. Static PCK membership is not runtime resolution;
  release mutations need explicit execution and independent assertions, not debug asserts.
  Any further immutable S03 change needs a scoped ROOT grant and exact review.
  First device proof: exported Gaming Mode input/native-extension initialization,
  exact templates and candidate engine for the dev7 controller regression. Record
  OS/client/driver/power versions; choose engine/template pair from evidence and update
  pins/docs together before S02 handheld acceptance. Desktop Mode cannot close this.
  Done when: imported fixture exports on each selected OS; ENet works without Steam
  installed/running and Steam works between authorized accounts. Check native dependencies,
  exclusions, app/depot/launch settings and test-account install/launch through the
  selected private branch/build while preserving VCS delivery; IDs/recipes are not live proof.
  Require LCD/OLED built-in controls, native 1280×800 readability/60 FPS, Gaming Mode,
  offline and suspend/resume. Prefer native Linux; prove/document any Proton fallback.
  Settle supported-target matrix, export recipe and capability/failure behavior.
  Devices and multi-account Steam remain deferred until available; desktop preparation
  cannot ratify engine choice or close target gates. Full gameplay is M1-D4.

- [ ] **P0-GATE — Review the foundation evidence and revise the milestone plan.**
  Owner: foundation review worker/implementers; Regner ratifies product decisions.
  Needs: ratified brief, ownership/scene/API drafts, accepted art/city briefs;
  [minimum tooling](docs/spikes/s03.md#integration-validation),
  [GDScript](docs/reviews/p0-06.md)/[art review](docs/reviews/p0-07.md) evidence,
  [asset workflow decision](docs/decisions/p0-05-asset-workflow.md), S01/S03 evidence,
  S02, S03-R/S03-S and S04–S08, plus reconciled guides/dated DOC records above.
  S07 must supply capacity envelope, limiting axes and organization/diagnostic decisions;
  research alone leaves representative/target gaps open. Steam feasibility and tester
  access require actual evidence; ENet cannot close Steam.
  Done when: critical design/feasibility assumptions for M1 are resolved; Regner ratifies
  scope/art/layout/camera/controls against concepts/spikes; implementers settle contracts
  and budgets. Record decisions in `docs/decisions/`, update canonical guides/TODO and
  identify prototypes to discard or deliberately productionize. Review skills/minimum
  checks work. Failed proofs require a specific follow-up or deliberate scope revision;
  production acceptance is not a phase-zero requirement.

## First milestone — implementation

All M1 tasks follow P0-GATE. Gameplay can initially use accepted Blender fixture
imports while final assets are produced; final acceptance requires the ratified
custom art/content. Add production tests with each rule/lifecycle change. Art
families proceed from their relevant approved contracts alongside M1-A/B, without
waiting for unrelated gameplay systems.

### M1-A — Playable session and player foundation

Owner roles: session/gameplay implementer (A1/A2), UI/audio implementer (A3),
independent validation worker (A-GATE).

- [ ] **M1-A1 — Production session service and main-menu flow.**
  Needs: [S03 evidence](docs/spikes/s03.md), S03-S/S08 decisions.
  Build both providers, Steam lobby/invite adapter and Host/Join/Settings/Quit
  scenes with loading/readiness/roster, actionable errors, cancel, leave and retry.
  Include Standalone entry and in-match leave/settings/host-reset requests, following
  the ratified brief; only host/standalone may reset, including when dead.
  Offer local-network and Steam friend sessions; route manual endpoints, friend/
  overlay invites and launch requests through the same join/cancel lifecycle.
  Done when: baseline/admission/compatibility and bounded teardown are correct;
  unreachable/full/incompatible games, unavailable Steam and host loss return to a
  usable menu. ENet remains available without Steam; close stale peers/lobbies from
  canceled callbacks, including invites received while loading or in a match.

- [ ] **M1-A2 — Player simulation, input, camera and replication.**
  Needs: M1-A1 and S02/S03-R decisions.
  Implement the chosen foot controls/aim, collision, one local rig, remote
  interpolation and foot prediction if required. Keep rules shared across offline,
  authoritative simulation and permitted replay. Add safe spawn/death/respawn lifecycle.
  Done when: distinct players move/aim independently; input expiry/focus loss work;
  convergence meets the selected envelope. Standalone play uses the same rules.
  Match owns a reset coordinator: preserve admitted peers, restore initial player
  state and rehydrate before input; reject old-match commands and preserve saved
  placement. Extend this same transition with each later dynamic gameplay owner.

- [ ] **M1-A3 — Settings, audio buses and persistence.**
  Needs: P0 API decisions; can run alongside M1-A1/A2.
  Implement Master/Music/SFX levels and mute, defaults, validated local load/save,
  live preview and settings access from menu/in-game UI. Apply settings at startup.
  Done when: values survive restart, invalid/missing data recovers, controls work on
  selected input devices and changing audio does not pause or mutate shared gameplay.

- [ ] **M1-A-GATE — Verify the multiplayer shell in real builds.**
  Needs: M1-A1 through M1-A3.
  Two exported processes independently walk/collide, late-join and leave/rejoin with
  one rig each; cancel/retry and host-loss/error flows clean up. Validate selected
  offline mode, host/standalone reset with admitted peers retained, audio persistence
  and latency response. Review logs and owned-script
  checks; retain evidence before extending the shell.
  Run the shared lifecycle through both providers: ENet with Steam unavailable and
  Steam with distinct accounts/networks, using friend joining/invites. Inspect the
  real Steam traffic route; lobby success alone is insufficient.

### M1-B — Arcade vehicles, weapons and destruction

Owner roles: vehicle implementer (B1), combat implementer (B2/B3),
presentation/audio implementer (B4); Regner ratifies feel.

- [ ] **M1-B1 — Vehicle gameplay and authoritative driver transitions.**
  Needs: M1-A-GATE and S04 decision.
  Implement chosen handling, throttle/reverse/brake/steering/handbrake, contacts,
  stuck/rollover recovery and selected car replication/prediction.
  Done when: players enter/drive/exit; simultaneous claims, blocked exits, death,
  disconnect and car destruction follow the seat contract. NPC-to-player control
  transfer has one authoritative simulation owner; player input ownership never
  grants client physics authority. Preserve the ratified parked-car policy after
  abandonment; resuming traffic AI requires a recorded product change.

- [ ] **M1-B2 — Weapons, health, damage and respawn.**
  Needs: M1-A-GATE and combat/API decisions; can run alongside M1-B1.
  Build the ratified weapon list with stable definitions, equip/fire/reload/ammo
  rules, authoritative hitscan/projectile outcomes, pedestrian/player/car damage,
  and coherent death/respawn state. HUD consumes owned state.
  Done when: weapon behavior is distinct and readable; rates/ownership are validated,
  stale commands cannot fire after transitions and late joins hydrate current state.

- [ ] **M1-B3 — Car explosions, wrecks and chain reactions.**
  Needs: M1-B1, M1-B2 and S05 decision.
  Implement threshold damage, bounded exactly-once blast propagation, chosen
  obstruction/falloff/delay, occupant outcomes, wreck collision and cleanup.
  Done when: clustered cars chain and distant/protected cars follow the blast policy;
  no cycles/duplicate damage; collision/lifecycle completes before dependent state
  is published. Offscreen chains work; joining during/after one receives correct
  wreck/health state without replaying historical explosions. Register combat,
  seats, rockets, chains and wreck cleanup with the existing Match reset transition;
  reset while driving/firing restores initial dynamic state and clears old work.

- [ ] **M1-B4 — Shooting/explosion feedback and vertical-slice review.**
  Needs: M1-B2/B3 event contracts; effects/audio can develop alongside those tasks.
  Add muzzle flash, impact/tracer/projectile feedback, explosions/smoke/sparks and
  bounded cosmetic debris using Blender mesh carriers where meshes are needed.
  Source/license sound for weapons, hits, explosions, engine/tires, footsteps, UI
  and music/ambience; retain originals, edits and notices. Mix buses and bound voices.
  Done when: both players can walk, shoot, enter/drive/exit and cause visible chains;
  replay/duplicate packets do not repeat effects or sounds. Effects preserve aim,
  road/minimap readability and chosen performance limits.

### M1-C — Custom city, population and minimap

Owner roles: asset-family authors (C1), world assembler (C2), AI implementer (C3),
UI/minimap implementer (C4), following the [asset handoffs](docs/assets.md).

- [ ] **M1-C1 — Produce the ratified custom art families.**
  Needs: P0-GATE; pipeline/style/camera/dimensions for each family.
  Produce reusable building types/landmark, roads/junctions/sidewalks, props,
  player/pedestrian rig and animations, car variants/wrecks, weapons and VFX carriers.
  Refine the accepted concept shapes and overhead weapon presentation with S02/S04
  camera evidence; source handoffs include final gameplay-camera views/paintovers.
  Use the documented handoffs and art review for each accepted prefab.
  Done when: the content catalogue links concepts, `.blend`, exports, import settings,
  reusable scenes and previews; reexport/save/reload preserves ancestry/placement.
  Families can run in parallel with distinct source/prefab ownership and M1-A/B.

- [ ] **M1-C2 — Assemble the authored district in saved sectors.**
  Needs: accepted M1-C1 road/building/prop subsets, S06 topology and
  S07 documented capacity/organization decisions (see [brief](docs/spikes/s07.md)).
  Instance individual building scenes repeatedly; compose the ratified district,
  loops/sidewalks/intersections/alleys/landmark, stunt/chain space, safe spawns and
  boundaries. Implement selected culling configuration and rebuild derived data.
  Done when: placement survives reexport/reopen, actor/vehicle/camera clearance is
  proven, sector seams connect and actual gameplay-camera views remain readable.
  Record actual density/asset variety/residency against S07 assumptions; expanded
  experimental layouts are not production scope.

- [ ] **M1-C3 — Host-owned pedestrians and traffic.**
  Needs: M1-A2, M1-B1/B2, S06 decision and an accepted M1-C2 route fixture.
  Use actor/vehicle command APIs for wandering/fleeing pedestrians and lane-following
  cars; add bounded spawn/replenishment, crossing/junction/blocked-route/stuck policies,
  damage/death and wreck avoidance. Cars need no visible occupants.
  Done when: pedestrians stay on sidewalks except sanctioned crossings; cars make
  legal road turns and recover from obstruction; NPC-to-player vehicle transfer,
  sector routes, distant players, late joins and offscreen gameplay remain coherent.
  Population reset restores initial descriptors under Match, clears old AI/replenishment
  work and stays within caps without rewriting city placement.

- [ ] **M1-C4 — Road minimap and local HUD integration.**
  Needs: S06 topology contract and M1-A2; final alignment uses M1-C2.
  Draw roads from the selected city data with the local controlled-entity
  position/orientation marker; additional markers require a product decision.
  Define map scale, rotation, bounds and sector data lifetime.
  Done when: intersections/seams match world roads at both walking/driving speeds,
  late-join/map load works, markers track the local controlled entity and HUD state
  comes from gameplay owners. No separately maintained minimap street layout.

### M1-D — Integration, fun tuning and private review builds

Owner roles: validation/tooling worker (D1/D3), gameplay/review workers with Regner
(D2), release worker with Regner for access (D4); Regner owns M1-GATE approval.

- [ ] **M1-D1 — Complete production validation tooling and CI.**
  Needs: [foundation tooling evidence](docs/spikes/s03.md#integration-validation); grows alongside production implementations.
  Extend style/compiler/resource/source checks to all owned code/assets; add the
  preserving formatter wrapper if needed, meaningful gameplay tests, production
  network scenarios and local/CI parity. Exclude vendor addon rules and retain logs.
  Done when: checks fail on actual contract violations, including unused scripts,
  and run reproducibly without broad diagnostic suppression or implementation-copy tests.

- [ ] **M1-D2 — Integrated playtests, reviews and feel tuning.**
  Needs: M1-B4 and M1-C1 through M1-C4 accepted content/behavior.
  Use both review skills; test several players, camera transitions, aim, collisions,
  rapid driving/slides, readable spectacle, exploration routes, menu/focus/controller
  flows and audio mix. Record player feedback and specific changes.
  Done when: the agreed arcade feel criteria are met in windowed play; the district
  supports varied traversal and playful chain/stunt situations; review findings and
  gameplay defects are fixed or explicitly scoped out by the user.

- [ ] **M1-D3 — Capacity, adverse-network and performance acceptance.**
  Use [S07 methodology/results](docs/spikes/s07.md) for content identities, distinct
  capacity axes and diagnostic baselines; repeat with actual production content.
  Needs: integrated M1-A/B/C behavior and M1-D1 runner.
  Test selected player/population capacity, far-apart views, sustained traffic and
  effect/chain bursts on named hardware. Measure frame/physics times, draw calls,
  memory, bandwidth, queue/replay work and response/correction behavior.
  Exercise delay/jitter/loss/duplicates/stale identities, slow admission, host stalls,
  invalid intent, seat/lifecycle races, reset while driving/firing or joining, and
  changing collision through production APIs. Verify retained peers, new revision
  hydration, cleared history/effects/queues and unchanged authored placement.
  Run shared gameplay scenarios through both ENet and Steam; verify each provider's
  transfer modes/channels, payload limits and observed behavior independently.
  Done when: ratified budgets/convergence hold, limits stay bounded, authoritative
  state survives adverse delivery and real-process logs contain no new errors.
  Culling never disables required simulation; additional optimization needs evidence.

- [ ] **M1-D4 — Export and deliver private milestone review builds.**
  Needs: M1-D1 through M1-D3 and S08 target recipe.
  Clean-import/save/reload representative inherited assets; export with exact
  templates, packaged build/protocol/content identity and intended exclusions.
  Exclude authoring sources, tests, captures and development MCP tooling.
  Done when: each selected target/transport passes packaged launch/render/input/audio/
  settings/network checks and the promised external-network route. Record versions,
  hardware, results and unavailable evidence; retain builds, logs and known limits.
  Deliver the Steam build on the existing app's `fun-things` private beta branch
  and verified access route;
  verify friends can install/update, launch, invite/join and play across networks.
  Record build/depot/branch IDs and retain a rollback build. ENet remains usable for
  local testing. Public store launch/certification remains a separate later task.

- [ ] **M1-GATE — User review of the first playable milestone.**
  Needs: M1-D4.
  Done when: the ratified capacity can host/join a custom Blender-authored district,
  explore on foot/in cars, use the agreed weapons, encounter sidewalk pedestrians
  and road traffic, and cause car explosion chains; roads appear on the minimap;
  shooting/explosion feedback is readable; audio settings persist; menus/failures/
  leave/retry and host/standalone reset work. Require the agreed feel, performance
  and multiplayer evidence,
  ENet local testing and Steam friend playtesting on the existing app, plus the
  selected offline/target promises. Current docs describe shipped behavior.

## Parallel work and dependency checkpoints

| Ready or stage | Parallel work | Gates |
| --- | --- | --- |
| Ready bounded preparation | S03-S [public API/interface record](docs/spikes/s03-s-valve-api-interface.md), then separately commissioned native prerequisites; S07 primary T hardware/build/telemetry preparation using the saved-reload driver; S08 release-cache/entrypoint diagnosis; P0-PROFILES dated-notes reconciliation | Named owners/budgets and scoped grants; S07 graphical T still needs authorized drawability; pending output is not accepted evidence |
| Drawable fixtures | Remaining S02/S03-R/S04 response/focus/readability/feel; S05 effects; S06 camera/map readability | Changed authorized surface/lease; final dimensions and Regner ratification; no identical stopped retry |
| Representative loads | S07 capacity/culling experiments; S08 exact exports | Actual content/effects/drawability and named hardware; Deck and multi-account Steam remain deferred |
| Production after P0-GATE | M1-A shell/settings and M1-C1 approved art families; then B1/B2 and accepted sector subsets | B3 needs vehicles/damage; C3 needs routes/actors/control transfer; D/GATE need integrated evidence |

ROOT coordinates task-block overlaps and review slots at saved rebases. Give separate
workstreams distinct fixture/prefab/sector ownership; never share a scene/source writer.
Parallel work preserves save/reload, source review and gameplay ownership contracts.

## Primary references for spike questions

Verify behavior against the exact pinned engine; task evidence records retain researched sources.

- [Godot 3D imports](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html).
- [High-level multiplayer](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html).
- [Steam networking/relay](https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay),
  [lobbies](https://partner.steamgames.com/doc/features/multiplayer/matchmaking) and
  [private testing](https://partner.steamgames.com/doc/store/testing).
- [VehicleBody3D](https://docs.godotengine.org/en/stable/classes/class_vehiclebody3d.html).
- [NavigationAgents](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationagents.html).
- [S07 capability/method brief](docs/spikes/s07.md) and
  [occlusion culling](https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html).
