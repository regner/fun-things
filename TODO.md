# Fun Things — foundations through the first playable milestone

Planning baseline: 7 October 2026. The project has engine/style configuration and
the Godot MCP Toolkit, but no gameplay, main scene, custom models, or gameplay tests.
This is an active work list; nothing below is claimed to be implemented.

Phase zero establishes decisions, documentation, review skills, reproducible checks,
and small technical proofs. M1 builds the playable game using those results. A spike
closes with evidence and changes to documentation **and this plan**, not just code.

Use [repository guidance](AGENTS.md), [development](docs/development.md),
[assets](docs/assets.md), and [multiplayer](docs/multiplayer.md) as working contracts.
Assign an owner and experiment budget when taking a task. Remove completed tasks
and commit their removal together with the resolving changes; retain evidence in
decision/spike records and replace downstream prerequisite references with those records. Keep unresolved
findings as specific tasks. Do not silently turn prototypes into production systems.

## Product requirements and scope to settle

The required experience is a playful, irreverent city sandbox: top-down 3D with
GTA2-style camera and controls, quick readable action, forgiving arcade cars,
weapons, pedestrians, traffic, player vehicle entry/driving/exit, and car explosions
that can trigger nearby cars. Traffic does not need modeled people inside cars.
M1 includes custom art, a road minimap, shooting/explosion effects, host/join menus,
and audio settings. Multiplayer/store/platform dependencies need focused APIs.
**Confirmed:** M1 supports ENet for local/loopback/LAN testing and Steam for friends
playtesting over the internet, using the existing Steam app. Both use the same
session/gameplay contracts. Steam is required for that path; ENet works without it.
**Confirmed in P0-01 review:** Steam Deck LCD at native 1280×800 is the performance
baseline, with 60 FPS on LCD and OLED; graphics should be stylized, not realistic.
Deck controls and Gaming Mode validation are required. The user designated VCS's
existing AppID 5294580 and Windows/Linux depots 5294581/5294582 for this project.
The intended private Steam beta branch is `fun-things`. Live setup/access is
deferred to S03-S/S08; the current engine pin awaits the early Deck input proof.

Every visible 3D model comes from Blender, including blockouts, spike fixtures,
and mesh-based VFX. Commit sources and explicit GLB exports; scenes instance the
imports. No primitive/CSG draw meshes, copied embedded model data, generated render
meshes, or runtime rebuilding of the authored city. Collision shapes, navigation
and occluder data, shaders/particle behavior, debug overlays, and 2D UI/minimap
drawing are separate concerns. Import processing retains the Blender source link.

The [ratified P0-01 brief](docs/design.md) owns product scope, gameplay policies
and the provisional validation envelope. The table below summarizes scope;
P0-04/spikes still settle detailed art/layout, tuning, toolchain and measured budgets.

| Area | Ratified first-milestone scope / remaining proof |
| --- | --- |
| Session | 1–4 players; authoritative listen server; host loss ends the match cleanly |
| Targets | Steam Deck LCD/OLED and Windows/Linux desktop; choose renderer and verify exact-engine exports/Gaming Mode |
| Connection | Required ENet local host/join and Steam friend lobby/invite joining; integration choice is a spike decision |
| Offline | Standalone sandbox using the same authoritative gameplay rules |
| City | One exterior district, roughly six connected blocks; loops, alleys, plaza, stunt/chain-reaction space |
| Weapons | Pistol, SMG, rocket launcher: distinct fire rates/range and hitscan/projectile behavior |
| Population | Simple wandering/fleeing pedestrians; lane-following cars; bounded replenishment |
| Art | Two car silhouettes; shared pedestrian rig/variants; reusable building, road, sidewalk and prop kit |
| Presentation | Readable stylized forms, restrained detail, playful signage, fixed daytime lighting |
| Menus/audio | Host, Join, Settings, Quit; Master/Music/SFX levels and mute, saved locally |
| Performance | Confirmed 60 FPS on Steam Deck LCD/OLED at native 1280×800; ratify frame pacing, simulation/memory/network and load budgets |

The Steam integration package/version remains to be selected. Prove actual Steam
gameplay transport and relay behavior; lobby success alone cannot satisfy friend
playtesting. Record the existing AppID and tester access/build route during phase
zero; no new Steam app is needed. Additional stores/platforms get capabilities and
adapter contracts now, and real integrations when selected. Record unsupported
targets honestly. A session selects ENet or Steam before host/join and keeps that
transport until teardown.

Defer missions, police/wanted systems, interiors, passengers, detailed civilian
simulation, building destruction, procedural cities, persistent worlds, host
migration, and production matchmaking unless a scope decision explicitly adds them.

## Phase zero — foundations

P0-01 was ratified on 7 October 2026; evidence and review decisions live in
[the product brief](docs/design.md). The user approved scope with budgets provisional,
explicitly deferred unknown live Steamworks setup to its proofs, and left the engine
choice open for early S08 Deck evidence. These deferrals are owned below; completed
scope work is removed from this active list.

- [ ] **P0-02 — Draft ownership, scene and API contracts.**
  Needs: [ratified brief](docs/design.md).
  Output: `docs/architecture.md`, `docs/scene-structure.md`, `docs/api-contracts.md`,
  and updates to existing guides. Define state owners, command/replication/presentation
  boundaries, signatures/data shapes, units, stable identities, lifecycle, errors,
  cancellation and contract tests. Use the scene/API starting points below.
  Done when: each rule/replicated field has one owner; external provider types stay
  at adapters; planned contracts have no contradictory guidance. Drafts are refined
  by spike decisions at P0-GATE. Keep APIs narrow and avoid speculative managers.
  Define both ENet and Steam transport providers plus a separate Steam lobby/invite
  adapter; map Steam account/lobby IDs and ENet peer IDs to fresh session identities.

- [ ] **P0-03 — Add only the tooling needed for reproducible foundation proofs.**
  Needs: [ratified brief](docs/design.md) and the first owned spike scripts/resources.
  Output: working style/lint and explicit all-owned-script compilation tasks,
  focused resource/source-link checks, and a bounded two-process runner. Preserve
  repository comment/spacing rules with manual review until a preserving wrapper exists.
  Runner uses production-facing APIs, distinct user/log directories, configurable
  ports, readiness/results, deadlines, retained logs, and stops only its own children.
  Done when: the spike fixtures can be rerun and failures produce useful evidence.
  Do not present import alone as compilation. CI and broader coverage grow in M1-D1.

- [ ] **P0-04 — Explore concepts and choose art direction and city layout.**
  Needs: [ratified brief](docs/design.md); concept exploration can run alongside
  contract/tooling drafts.
  Output: `docs/art-direction.md`, `docs/world-layout.md`, two small concept directions,
  gameplay-camera paintovers, silhouette sheets for buildings/cars/people/weapons,
  a VFX palette/keyframe, and an overhead road/sidewalk/sector plan.
  Explore chunky stylized forms, quieter streets with strong gameplay accents,
  clear rooftops/landmarks and humorous details. Design continuous sidewalks,
  readable intersections, alternate driving loops, safe spawns and world boundaries.
  Done when: the user chooses a direction and city brief with concept evidence;
  provisional dimensions are labeled for refinement from S02/S04/S06 at P0-GATE.
  GTA references guide feel; original designs supply the assets.

- [ ] **P0-05 — Specify the concept-to-asset-to-world workflow.**
  Needs: P0-02 and P0-04 drafts.
  Output: expand [assets](docs/assets.md) with handoff records, source/export layout,
  meters/axes/origins, export collections, sockets, rigs, animation names, materials,
  texture conventions, collision envelopes, LOD/bounds, catalogue and reexport rules.
  Keep `.blend` sources in a `.gdignore` authoring directory, outside runtime exports.
  Done when: every handoff below names an owner, acceptance evidence and rejection
  path; a changed source updates its outputs and affected placed prefabs together.
  S01 chooses the pinned Blender version/settings and proves the workflow.

- [ ] **P0-06 — Create a project GDScript review skill.**
  Needs: P0-02; use P0-03 checks and spike fixtures as they become available.
  Output: `.agents/skills/gdscript-review/SKILL.md`, linked to canonical guidance.
  Review owner/callers/serialized data, single rules, authority/admission, lifecycle,
  replay effects, bounded work, public/Inspector compatibility, style, simplicity,
  and independent outcome tests. Report severity, location, evidence, impact and fix.
  Done when: frontmatter/links validate and an independent dry run on an isolated
  deliberately flawed fixture finds meaningful issues; missing checks are reported.

- [ ] **P0-07 — Create a project art review skill.**
  Needs: P0-04 and P0-05 drafts; use S01/S02 artifacts for the dry run.
  Output: `.agents/skills/art-review/SKILL.md`, linked to art/source/scene contracts.
  Review concept/style consistency, Blender provenance and import ancestry,
  gameplay-camera readability, scale/pivots/sockets/rigs, materials, collision/routes,
  VFX bounds/overdraw, LOD/culling and measured performance.
  Done when: frontmatter/links validate and an isolated flawed asset/prefab receives
  useful evidence-based findings. Screenshots alone do not certify movement or load.

### Scene structure to validate in P0-02/S01/S06

Names are illustrative; settle concrete paths/contracts before production.

```text
Boot + process-lifetime session/settings/optional platform services
├── MainMenu / Settings (separate reusable UI scenes)
└── Match (authoritative match state and lifecycle)
    ├── CityRoot (saved district scenes)
    │   └── Sector scenes (saved composition and placement)
    │       ├── Building/Road/Sidewalk/Prop prefab instances
    │       │   ├── Visuals (linked Blender model import)
    │       │   ├── Deliberate collision
    │       │   └── Sockets / relevant components
    │       └── Spawn/route anchors + navigation/topology/occluder references
    ├── RuntimeEntities (player, vehicle, pedestrian scenes)
    ├── RuntimeEffects (bounded cosmetic instances)
    └── LocalRig (this process's input, camera, HUD and minimap)
```

Each building type has its own reusable scene; repeated buildings remain instances.
Districts/sectors own authored transforms; a match never reconstructs their layout.
Actor prefabs own simulation state and imported visuals; remote presentation does
not read local input or decide gameplay. Document required node paths, sockets,
stable world/entity IDs, inherited overrides and multiplayer-ready setup before `_ready`.
Start with fully loaded sector scenes; streaming needs measured justification.
One integrator owns each shared world scene; parallel contributors own distinct files.

### API boundaries to draft, then settle with spikes

| Boundary | Owner and contract to define |
| --- | --- |
| Session | Host/join/cancel/leave, states/roster/readiness, operation IDs, timeouts and normalized failure events |
| Transport provider | ENet and Steam peer creation/closure, connection correlation, capability/channel/limit reporting; both real providers plus fake contract fixture |
| Platform services | Steam availability, friend lobby create/join/leave and invites/launch requests into the common join flow; unavailable capability results for ENet/offline builds |
| Local settings/storage | Validated settings, defaults, load/save failure handling, persistent audio controls; platform storage behind its provider if later required |
| Actor and vehicle commands | Typed, ticked intent from local input/AI/network; shared simulation rules; no device polling in movement |
| Vehicle interaction | Authoritative seat claim/exit, driver identity/control transfer, blocked exit and lifecycle policy |
| Weapons/damage/explosions | Definition IDs, equip/fire validation, authoritative outcomes, health/death, bounded blast work and event deduplication |
| City/navigation/map | Stable road/sector IDs, authored links, spawn/route queries, bake revisions and derived minimap data |
| Presentation | State/event consumers for camera/HUD/audio/VFX; distinguish baseline hydration from new live events |

Keep store/native SDK types, addresses, transport handles and callbacks at adapters.
Map session identities to transport peer IDs at the boundary. Document authority,
session/entity generations, state revisions and compatibility where needed. Gameplay
may use Godot physics and high-level RPCs; these APIs do not require a second RPC
framework or an abstraction around every engine call. Test provider replacement and
absence. Steam discovery/invites and Steam gameplay transport have separate owners;
lobby membership does not grant gameplay admission. ENet startup has no Steam
dependency. Additional store integrations follow selected requirements.

### Asset handoffs to document and prove

1. **Brief:** gameplay purpose, dimensions/clearance, camera scale, style, variants,
   collision and sockets. A reviewer accepts the brief before detailed work.
2. **Concept:** silhouettes and gameplay-camera view; select a design and record
   provenance before Blender production. Concept images are references, not models.
3. **Blender blockout:** real dimensions/pivots, applied transforms and export scope;
   use a linked import to test camera, turning and collision envelopes.
4. **Asset production:** model/rig/animations/materials/textures and justified LODs;
   review against the chosen direction and technical envelope.
5. **Export/import:** explicit GLB, pinned tools/settings, source catalogue entry,
   scale/axes/normals/bounds/sockets checks, preserved `.import` and resource identities.
6. **Prefab:** wrap the imported instance with intentional collision/components;
   art and gameplay review from fixed gameplay and overview cameras.
7. **Placement:** world integrator instances accepted prefabs in saved sectors;
   refresh derived route/navigation/minimap/occluder data, save/reopen, playtest and
   profile. Rejected handoffs return to the owner with concrete findings.

## Phase-zero technical spikes

Each spike gets a short `docs/spikes/<id>.md`: question/hypothesis, alternatives,
minimum fixture, tool versions, proposed effort cap, experiment, measurements/logs/
captures, decision, limitations, production acceptance cases and resulting doc/TODO
changes. Start with a proposed **1–2 focused days per experiment**, adjusted before
work; this is an effort cap, not a delivery promise. If inconclusive, record the
next bounded question and whether it blocks M1. Do not expand into full feature
implementation. Save editor mutations before playtests; preserve unsaved work.

- [ ] **S01 — Blender/import/prefab/scene roundtrip.**
  Needs: [ratified brief](docs/design.md), P0-02 and P0-05 drafts; minimal P0-03 checks.
  Question: which pinned Blender/GLB/import settings preserve our source/scene contract?
  Minimum: one static prefab and one rigged fixture, repeated instances and one
  inherited variant; reexport, clean import, save/reopen and inspect identity/overrides.
  Decision: tool/settings pin and accepted source/prefab workflow. Evidence includes
  scale/axes/pivots/sockets, no copied model data, no lost authored transforms or
  unresolved dependencies, and revised asset/scene contracts.

- [ ] **S02 — GTA2-style foot controls, camera and aiming.**
  Needs: [ratified brief](docs/design.md), P0-04 draft and tiny Blender fixture;
  S01 settings can refine it.
  Question: which height/tilt/projection and control/aim choices deliver the desired feel?
  Minimum: walk/turn/aim/shoot in one corner/alley fixture; evaluate fixed camera yaw,
  rooftops/obstruction, target readability, input focus loss and selected device support.
  Include Deck controls and 1280×800 readability; early S08 resolves the engine input
  blocker before handheld evidence can be accepted.
  Start with GTA2 turn/forward/back controls; an alternative needs a deliberate
  product decision. Decision: camera/control contract, actor/collision/aim envelope,
  playtest evidence and feel targets. No finished animation or weapon system required.

- [ ] **S03 — ENet session/authority API proof.**
  Needs: [ratified brief](docs/design.md), P0-02 drafts and minimum P0-03 runner.
  Question: does the narrow provider/service boundary support the intended lifecycle?
  Minimum: two real ENet processes host/join, apply a tiny baseline before admission,
  cancel/retry, reject one stale/invalid intent, and exchange a fake provider.
  Inspect asynchronous cleanup and one local rig per player, with Steam unavailable.
  Decision: topology, common identity/admission/cancellation contract,
  replication writer and budget approach. Full error/adversarial suites belong in M1.

- [ ] **S03-S — Steam integration, friend connection and transport proof.**
  Needs: S03 boundary/fixture and [existing-app record](docs/design.md).
  Owner: Codex (proof/setup record), Regner (Steamworks access).
  Before the network proof, verify app type/release state, distinct authorized
  testers/package entitlement, depot OS/package inclusion and launch settings;
  confirm/create the intended `fun-things` private branch and record its access route.
  Live setup is unknown and was explicitly deferred from P0-01 by the user.
  Compatibility/access research can run alongside S03; no new app is required.
  Question: which pinned integration works with our exact Godot engine and supports
  Steam lobbies/invites plus actual gameplay traffic across friends' networks?
  Minimum: initialize the existing app, create/join one friend lobby and exchange
  the same tiny admitted baseline/intent via a real Steam multiplayer peer, using
  distinct authorized accounts on separate machines/networks without port forwarding.
  Inspect connection/relay diagnostics, native API/export compatibility, transfer
  modes/channels/limits and cleanup after one canceled attempt. Keep the fixture small.
  Decision: integration/SDK/native-library pins, account/peer mapping, lifecycle and
  proven networking route, plus private install/access recipe. Record failures as
  blockers; ENet exchanged through a lobby is not the required Steam transport.
  Full invitation races and gameplay acceptance belong in M1-A/D.

- [ ] **S03-R — Networked on-foot responsiveness.**
  Needs: S02, S03 and S03-S; ENet measurements can start before the Steam proof.
  Question: does the actual foot controller meet the feel target over the selected network envelope?
  Minimum: two processes walking/turning/aiming under representative latency/loss,
  repeated through ENet and Steam;
  measure local response and correction behavior. Try minimal shared-rule prediction
  only if needed. Decision: foot interpolation/prediction/reconciliation requirements,
  limits and evidence; independent of the vehicle prediction choice. Required for M1-A2.

- [ ] **S04 — Arcade car physics and network response.**
  Needs: S02 and S03; finish with S03-S evidence. Use a Blender car fixture.
  Question: which simple body/control approach gives fun handling and tractable replication?
  Minimum: compare a small kinematic/custom dynamic candidate on one track, fast
  steering/sliding/braking and a wall contact; repeat host/client under latency/loss
  through ENet and Steam before settling the responsiveness decision.
  Compare VehicleBody3D only if useful. Do not assume cross-peer physics determinism.
  Decision: body/handling/recovery approach, car prediction needs, dimensions/turning
  envelope and seat/control contract. Specify the full seat race/disconnect/exit
  matrix for M1-B1 rather than building it here.

- [ ] **S05 — Authoritative explosion-chain feasibility.**
  Needs: S03 and a minimal S04 vehicle/damage fixture.
  Question: how do we order and bound damage/chain events without duplicate outcomes?
  Minimum: three cars, near/far spacing, one duplicate event and wreck-state hydration.
  Estimate peak work and choose blast range/obstruction, chain delay/order, occupant
  outcome, wreck/collision lifetime and live-versus-historical presentation behavior.
  Decision: host-owned damage/explosion contract, event IDs and per-tick/queue/effect
  bounds. Full joining races and sustained capacity loads belong in M1-B3/M1-D.

- [ ] **S06 — Shared city topology, navigation and minimap.**
  Needs: S01, S02, S04 dimensions and P0-04 district draft.
  Question: which authored representation supports lanes, sidewalks, seams and road-map drawing?
  Minimum: one intersection split across two saved sectors; one person takes a
  sidewalk/crossing route, one car makes a legal turn, and minimap roads align at
  the seam. Compare sidewalk graph/navmesh choices and lane graph/curves for cars.
  Validate stale derived data. Scene placement owns geometry/transforms; topology
  references it and owns connectivity, avoiding an independent layout writer.
  Decision: representation, stable IDs/layers, host AI/controller APIs and bake/update
  workflow. Specify bounded blockage/junction/stuck/wreck recovery for M1-C3.

- [ ] **S07 — Top-down culling and representative load.**
  Needs: S01, S02 camera, S06 sector fixture and preliminary S05 effect load.
  Question: which culling/LOD/sector choices help from our actual camera without visual errors?
  Minimum: repeated imported fixtures and simple moving stand-ins at proposed load;
  camera movement/fast driving, distant player views and an explosion-effect burst.
  Compare frustum/LOD/visibility ranges and occlusion benefit/cost; inspect bounds,
  roof visibility, seams/pop-in, shadows and transparent overdraw.
  Compare Mobile and Forward Plus on the LCD Deck baseline, including graphical
  listen-server load; the required 60 FPS guides art/effect choices.
  Decision: selected configuration, measured budgets and sector sizing. Separate
  rendering visibility, AI scheduling, network relevance and streaming; off-camera
  authoritative gameplay continues correctly. Streaming/batching require evidence.

- [ ] **S08 — First-target export and service compatibility.**
  Needs: [ratified target/pin record](docs/design.md) for early input/template checks;
  S01, S03 and S03-S for the complete proof. Owner: Codex (proof), Regner (device access).
  Early input evidence settles the engine decision deliberately left open in P0-01.
  First: minimal exported Deck Gaming Mode input/native-extension initialization
  test, exact templates and candidate engine choice for the dev7 controller regression.
  Obtain LCD/OLED Deck access and record installed OS/client/driver/power versions;
  choose the exact engine/template pair from the proof and update the pins/docs together.
  Do this before S02 handheld validation; Desktop Mode alone cannot close it.
  Question: can the exact toolchain package the selected model/renderer/service path?
  Minimum: one imported fixture exported on each selected OS, an ENet connection
  without Steam installed/running, and a Steam connection between authorized accounts.
  Check templates/native dependencies, intended export exclusions and Steam app/
  depot/launch settings. Reuse S03-S network evidence where applicable; prove the
  private test package can be installed/launched through Steam by a test account.
  Verify the selected `fun-things` branch/build and preserve existing VCS delivery;
  repo IDs/recipes do not prove live setup or account access.
  Include Deck LCD/OLED built-in controls, native 1280×800 readability, offline and
  suspend/resume outcomes. Prefer native Linux; document/prove any Proton fallback.
  Decision: supported-target matrix, export recipe and capability/failure behavior.
  Record missing hardware/access as unresolved evidence; full gameplay acceptance is M1-D4.

- [ ] **P0-GATE — Review the foundation evidence and revise the milestone plan.**
  Needs: [ratified brief](docs/design.md), P0-02 through P0-07, S01 through S08
  including S03-R and S03-S.
  Done when: critical design/feasibility assumptions required to begin M1 are resolved;
  the user ratifies scope, chosen art/layout and camera/control choices against
  concepts/spike evidence; implementers settle API/scene/source contracts and budgets.
  Record decisions in `docs/decisions/`, update canonical guides and this TODO, and
  identify prototype code to discard or deliberately productionize. Review skills
  and minimum checks work. A failed proof means a specific follow-up or deliberate
  scope revision; production acceptance is not a phase-zero requirement.
  Steam transport/integration feasibility and tester access are required evidence;
  successful ENet tests cannot close an unresolved Steam proof.

## First milestone — implementation

All M1 tasks follow P0-GATE. Gameplay can initially use accepted Blender fixture
imports while final assets are produced; final acceptance requires the ratified
custom art/content. Add production tests with each rule/lifecycle change. Art
families proceed from their relevant approved contracts alongside M1-A/B, without
waiting for unrelated gameplay systems.

### M1-A — Playable session and player foundation

- [ ] **M1-A1 — Production session service and main-menu flow.**
  Needs: S03/S03-S/S08 decisions.
  Build both providers, Steam lobby/invite adapter and Host/Join/Settings/Quit
  scenes with loading/readiness/roster, actionable errors, cancel, leave and retry.
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
  convergence meets the selected envelope. Selected offline play uses the same rules.

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
  offline mode, audio persistence and latency response. Review logs and owned-script
  checks; retain evidence before extending the shell.
  Run the shared lifecycle through both providers: ENet with Steam unavailable and
  Steam with distinct accounts/networks, using friend joining/invites. Inspect the
  real Steam traffic route; lobby success alone is insufficient.

### M1-B — Arcade vehicles, weapons and destruction

- [ ] **M1-B1 — Vehicle gameplay and authoritative driver transitions.**
  Needs: M1-A-GATE and S04 decision.
  Implement chosen handling, throttle/reverse/brake/steering/handbrake, contacts,
  stuck/rollover recovery and selected car replication/prediction.
  Done when: players enter/drive/exit; simultaneous claims, blocked exits, death,
  disconnect and car destruction follow the seat contract. NPC-to-player control
  transfer has one authoritative simulation owner; player input ownership never
  grants client physics authority. Verify return-to-traffic policy if selected.

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
  wreck/health state without replaying historical explosions.

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

- [ ] **M1-C1 — Produce the ratified custom art families.**
  Needs: P0-GATE; pipeline/style/camera/dimensions for each family.
  Produce reusable building types/landmark, roads/junctions/sidewalks, props,
  player/pedestrian rig and animations, car variants/wrecks, weapons and VFX carriers.
  Use the documented handoffs and art review for each accepted prefab.
  Done when: the content catalogue links concepts, `.blend`, exports, import settings,
  reusable scenes and previews; reexport/save/reload preserves ancestry/placement.
  Families can run in parallel with distinct source/prefab ownership and M1-A/B.

- [ ] **M1-C2 — Assemble the authored district in saved sectors.**
  Needs: accepted M1-C1 road/building/prop subsets and S06/S07 decisions.
  Instance individual building scenes repeatedly; compose the ratified district,
  loops/sidewalks/intersections/alleys/landmark, stunt/chain space, safe spawns and
  boundaries. Implement selected culling configuration and rebuild derived data.
  Done when: placement survives reexport/reopen, actor/vehicle/camera clearance is
  proven, sector seams connect and actual gameplay-camera views remain readable.

- [ ] **M1-C3 — Host-owned pedestrians and traffic.**
  Needs: M1-A2, M1-B1/B2, S06 decision and an accepted M1-C2 route fixture.
  Use actor/vehicle command APIs for wandering/fleeing pedestrians and lane-following
  cars; add bounded spawn/replenishment, crossing/junction/blocked-route/stuck policies,
  damage/death and wreck avoidance. Cars need no visible occupants.
  Done when: pedestrians stay on sidewalks except sanctioned crossings; cars make
  legal road turns and recover from obstruction; NPC-to-player vehicle transfer,
  sector routes, distant players, late joins and offscreen gameplay remain coherent.

- [ ] **M1-C4 — Road minimap and local HUD integration.**
  Needs: S06 topology contract and M1-A2; final alignment uses M1-C2.
  Draw roads from the selected city data, with player position/orientation and useful
  agreed markers. Define map scale, rotation, bounds and sector data lifetime.
  Done when: intersections/seams match world roads at both walking/driving speeds,
  late-join/map load works, markers track the local controlled entity and HUD state
  comes from gameplay owners. No separately maintained minimap street layout.

### M1-D — Integration, fun tuning and private review builds

- [ ] **M1-D1 — Complete production validation tooling and CI.**
  Needs: P0-03; grows alongside production implementations.
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
  Needs: integrated M1-A/B/C behavior and M1-D1 runner.
  Test selected player/population capacity, far-apart views, sustained traffic and
  effect/chain bursts on named hardware. Measure frame/physics times, draw calls,
  memory, bandwidth, queue/replay work and response/correction behavior.
  Exercise delay/jitter/loss/duplicates/stale identities, slow admission, host stalls,
  invalid intent, seat/lifecycle races and changing collision through production APIs.
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
  leave/retry work. Require the agreed feel, performance and multiplayer evidence,
  ENet local testing and Steam friend playtesting on the existing app, plus the
  selected offline/target promises. Current docs describe shipped behavior.

## Parallel work and dependency checkpoints

| When | Work that can run together | Must wait |
| --- | --- | --- |
| Initial foundation | Ratified brief, contract drafts, concept exploration, tool inventory | Chosen style/layout and measured scope revisions need user ratification and evidence |
| Tiny fixtures available | S01 pipeline, S02 camera, S03 session; review skill drafts | All visible fixtures must have Blender sources; only minimum harness required |
| ENet boundary available | S03-S Steam proof, S04 car candidates, S08 packaging work | Existing-app/tester access and native compatibility must be established early |
| Both providers available | Finish S03-R foot response and S04 network response; S08 exports | Both transports need evidence; foot/vehicle prediction are separate decisions |
| Vehicle envelope available | S05 chain proof and S06 intersection/seam | S06 uses pipeline plus real actor/turning dimensions |
| City/effect fixtures available | S07 culling, finish S08, skill dry runs and doc reconciliation | P0-GATE resolves critical assumptions before production |
| M1 begins | M1-A shell/settings, M1-C1 art families | Each art class uses its approved style/pipeline/envelope |
| Shell accepted | M1-B1 vehicles and M1-B2 weapons; static sector assembly | M1-B3 needs both vehicle and damage ownership |
| Routes/actors accepted | NPCs, minimap, final asset integration and growing CI | Population needs actual movement, roads and control transfer |
| Integrated district accepted | Feel/reviews and network/performance work | Final builds/user acceptance require all selected evidence |

Do not let multiple agents edit one shared scene/source at once. Give independent
workstreams separate fixture/prefab/sector files and explicit handoffs. Parallelism
does not bypass editor save/reload, source review or gameplay ownership contracts.

## Primary references for spike questions

Stable docs guide research; verify APIs and behavior against the exact pinned engine.

- [Godot 3D import formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html): GLB/import workflow for S01.
- [Godot high-level multiplayer](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html): transport/RPC constraints for S03/S08.
- [Steam networking/relay](https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay): actual Steam gameplay route for S03-S.
- [Steam lobbies](https://partner.steamgames.com/doc/features/multiplayer/matchmaking): friend discovery/join lifecycle, separate from gameplay transport.
- [Testing on Steam](https://partner.steamgames.com/doc/store/testing): existing-app tester access, private branches and installation checks for S03-S/S08/M1-D4.
- [VehicleBody3D](https://docs.godotengine.org/en/stable/classes/class_vehiclebody3d.html): known limitations to consider when choosing S04 candidates.
- [NavigationAgents](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationagents.html): path following and avoidance questions for S06.
- [Occlusion culling](https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html): camera-dependent opportunities and CPU cost to measure in S07.
