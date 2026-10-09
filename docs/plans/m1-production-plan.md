# M1 production plan — owner-review proposal

8 October 2026. This is a production architecture, test and backlog proposal for the
P0-GATE review. It does not claim that production gameplay exists or that an open
foundation criterion passed. The [product brief](../design.md),
[ownership map](../architecture.md), [API contracts](../api-contracts.md),
[scene contracts](../scene-structure.md) and [multiplayer guide](../multiplayer.md)
remain the detailed sources for rules that are not changed below.

The owner's 8 October decisions supersede older text where they conflict:

- M1 ships ENet only. Keep a narrow session/transport seam for a later Steam adapter,
  but Steam features, packaging and acceptance are not M1 work.
- M1 targets Windows and Linux desktop. Steam Deck is a later target, not an M1 gate.
- On foot, WASD moves in fixed north-up world/screen axes and the mouse controls
  facing. The camera FOV is 42 degrees. Local foot and car control use prediction.
- No firing from cars. Exit requires speed below 0.5 m/s. A disconnected driver's
  car coasts to a stop.
- Every accepted explosion receives a visible effect. Presentation may reduce effect
  complexity under load, but it may not drop an explosion.
- S07 supplies environment-scale planning guidance, not a production capacity gate.

P0-GATE should reconcile the older Steam, Deck, tank-control, cutaway and eight-effect
wording in the canonical records. Production must not implement those superseded
requirements merely because the dated drafts still contain them.

## 1. Production shape

### 1.1 Directory and dependency layout

Create directories only with their first real resource. Production code must not
import from `tests/fixtures/`; fixtures may import production APIs in order to remain
regression tests.

```text
res://
  scenes/
    boot/                 boot.tscn: process-lifetime composition
    ui/                   menu, status, settings, HUD and reusable widgets
    match/                match.tscn and match-owned coordinators
    world/                district and saved sectors
    prefabs/              buildings, roads, sidewalks and props
    entities/             player, pedestrian, vehicle and projectile scenes
    local/                local_rig.tscn: input, prediction, camera and HUD
    effects/              authored reusable effect scenes
  scripts/
    session/              SessionService and ENet transport
    match/                tick, lifecycle, reset and spawn reservations
    replication/          codecs, admission, state application and interpolation
    actors/               shared actor motion and player lifecycle
    vehicles/             shared drive rules, motion and interaction
    combat/               weapons, damage, projectiles and explosions
    population/           population owner, traffic and pedestrian controllers
    world/                CityData queries and bake validation
    local/                input, prediction/reconciliation and presentation
    settings/             LocalSettings
    ui/                    view controllers; no gameplay decisions
    audio/                 voice policy and state-driven emitters
  resources/
    actors/ vehicles/ weapons/ damage/ population/ world/
  art/
    source/                committed Blender sources under .gdignore
    models/ textures/ materials/ audio/
  tests/
    unit/                  GUT tests of production APIs and pure rules
    fixtures/              saved spike and integration fixtures
  tools/                   checks and external-process runners
```

The source directories follow the state owner, not arbitrary technical layers. For
example, the explosion queue and chain policy stay in `combat/`; replication reads
committed explosion state but does not decide damage.

### 1.2 Autoload and main-scene policy

Use no project autoload initially. The saved `/root/Boot` main scene owns the
process-lifetime `Session`, `Settings`, optional future `Platform` boundary and
replaceable `View`. This preserves the architecture draft while avoiding hidden
global state. Add an autoload only when a demonstrated process-lifetime need cannot
remain under Boot, and record its teardown/test contract first.

The main flow is:

```text
Boot
  -> MainMenu
  -> Session starting/connecting (or standalone preparation)
  -> Match loading and local world readiness
  -> baseline/handoff where networking is used
  -> active Match
  -> bounded closing/cleanup
  -> MainMenu with a useful result or error
```

Standalone enters the same Match initialization and authority paths without a fake
peer. Hosting creates an ENet peer through `ENetTransport`; joining parses an
adapter-owned endpoint before Session accepts the operation. Match is attached only
under `Boot/View`, and the menu is restored only after producers, peer callbacks,
entities, prediction and presentation histories are closed.

### 1.3 Module boundaries and sole owners

The following maps production modules to the canonical ownership table. A row may
start as one script or scene component; it is not a requirement to create a manager
class for every noun.

| Module | Sole decisions/writes | Inputs and consumers |
| --- | --- | --- |
| Boot | Current view and process-service lifetime | Coordinates Session, Settings and menu/Match replacement |
| SessionService | Operation, phase, provider selection, roster and peer mapping | UI requests operations; Match observes admitted participants |
| ENetTransport | ENet peer creation, endpoint parsing, capability facts and close | Session only; applies the pinned-engine bandwidth workaround before exposing a server peer |
| Match | Session/match identity, fixed tick, dynamic identity, reset and teardown order | Calls owner APIs in explicit physics order; Replication reads committed results |
| Replication | Wire validation, codecs, baseline/journal/handoff, revisions, receipts and replica install | Never computes movement, damage, seats, health or population outcomes |
| CityData | Authored topology identity, map data, route and shared clearance queries | Population, lifecycle, interactions and minimap consume one representation |
| SpawnReservations | Atomic dynamic spawn/exit reservations | PlayerLifecycle and Population reserve before body insertion |
| ActorMotion | Foot pose, velocity and facing rule | Local input, host remote input and pedestrian controller submit typed commands |
| PlayerLifecycle | Death, three-second respawn, safe-spawn result and controlled entity | Coordinates Health, WeaponState and VehicleInteraction before publication |
| VehicleMotion | Car pose, velocity, handling/contact state and coast-to-stop policy | Player prediction, authority and traffic all call the same drive step |
| VehicleInteraction | Seat, enter/exit, control revision and transfer transactions | Enforces stopped exit and no partial transition |
| WeaponState | Selection, magazine, reload/cooldown and ShotId allocation | Local UI reads; DamageResolver receives accepted shots |
| Health | Health value, revision and damage deduplication | Lifecycle owners consume lethal outcomes |
| DamageResolver | Hitscan/projectile verdict, attribution and friendly/self damage | Host physics only; clients never submit hits or damage |
| Explosions | Blast queue, chain order, terminal car transition and wreck retention | Presentation consumes every committed live explosion event |
| Population | Global slots, replenishment and pedestrian/car lifecycle | Creates through Match; AI emits motion commands rather than poses |
| TrafficController | Lane route, gap/intersection, blockage and stuck state | Emits the standard `DriveCommand`; never writes VehicleMotion |
| PedestrianController | Wander, crossing and flee state | Emits the standard foot command; never writes ActorMotion/Health |
| LocalRig/Input | Device state, focus release and intent sequence | No gameplay outcomes; swaps foot/car command collector on binding |
| LocalRig prediction | Owned foot/car history and permitted replay | Calls shared motion steps only; authoritative corrections always win |
| EntityPresentation | Remote interpolation and local visual correction | Moves presentation anchors, never physics or authoritative transforms |
| RuntimeEffects | VFX/audio instance lifetime and EventId deduplication | Cannot suppress an explosion event or mutate gameplay |
| HUD/minimap/menu | Display and local interaction | Reads owners; does not derive health, ammo, routes or authority |
| LocalSettings | Audio schema, validation, preview and atomic local save | Audio/UI only; never replicated |

Parents call these public APIs and subscribe to child signals; reusable children do
not climb the tree to find siblings. Saved scenes own node composition, UI layout,
collision and authored placement. Runtime code instantiates saved scenes and supplies
identity/state.

## 2. Shared simulation, prediction and replication

### 2.1 One rule path for standalone, host and replay

Every movement rule has a typed command and state transition independent of device
collection or networking:

```text
FootCommand {sequence, move_xz, aim_yaw, fire_held}
ActorMotion.step(command, fixed_delta, AUTHORITY | REPLAY)

DriveCommand {sequence, throttle, steer, brake, handbrake}
VehicleMotion.step(command, fixed_delta, AUTHORITY | REPLAY)
```

Foot movement normalizes diagonals, travels at 5 m/s, starts/stops immediately and
sets facing to the aim yaw. Input obtains the yaw from the mouse/camera ground-plane
intersection; simulation never reads mouse coordinates. Vehicle AI and players use
the same drive step and tuning resource.

Standalone and the host-local player submit trusted local intent through the same
validator used after sender mapping for remote intent. Only the command source
differs. AI receives a host-owned source. Delta is always the host fixed step;
clients cannot grant elapsed simulation time.

`REPLAY` permits only motion/contact state needed by that body. It suppresses firing,
damage, interaction, seat changes, population, audio and live effects. Motion code
must not signal gameplay side effects directly. Tests compare authority and replay
from the same initial state and command stream.

### 2.2 Local prediction for foot and car

Prediction is required for both local foot and local driving:

1. The local rig samples and numbers commands on physics ticks, predicts one shared
   motion step and stores the command plus complete replay state in a bounded history.
2. The host validates newest-held frames, simulates at most one fixed step per body
   per tick and acknowledges only consumed or explicitly superseded sequences.
3. An authoritative snapshot restores pose, velocity and motion-specific state at
   its tick. The client drops acknowledged history and replays remaining permitted
   commands in sequence.
4. Small display error is smoothed on `PresentationAnchor`; the gameplay body is
   immediately authoritative plus replay. Large error, changed generation/life/
   control/collision revision, overflow, reset or teardown snaps and clears history.
5. Collision revision must be installed before replay that depends on it. Historical
   world rollback is outside M1; contacts with changing remote bodies can correct.

Foot and vehicle history/state types stay separate because their contact and handling
state differ. The reconciliation scheduler can be shared, but it must not erase that
difference or assume one input packet equals one host tick. Cap replay work per
physics callback; overflow closes input and requests the existing bounded resync
rather than causing a long frame.

Remote entities do not predict. They interpolate snapshots behind the host timeline,
with a bounded extrapolation fallback followed by authoritative convergence.

### 2.3 Replication layers

Use one explicit production Replication writer rather than combining custom RPCs
with `MultiplayerSynchronizer` writers for the same fields:

- reliable session control: handshake, roster, admission and resync requests;
- reliable match state: baseline chunks, durable transactions, action results and
  live events with required revisions;
- unreliable ordered held intent;
- unreliable ordered movement snapshots.

The production codec uses fixed primitive schemas and bounded `PackedByteArray`
payloads where measurement justifies them. It must reject type, size, count and
nonfinite values before mutation. Sender identity comes from the RPC sender mapping,
not payload identity.

Admission retains the immutable baseline plus bounded journal and handoff described
in the API contract. Install lifecycle/collision, seat/control, health/equipment and
then poses. Enable local input only after the current admission grant and matching
fresh movement. Hydration creates current presentation without historical audio or
VFX. Per-entity freshness and periodic refresh prevent one lost entity subset from
remaining stale. Reliable lifecycle remains the sole writer of death, wreck, seat,
health and equipment; movement cannot resurrect or overwrite it.

The production baseline contains the full capped population and temporary durable
state. S11 must measure its encoded and wire sizes against the 1 MiB target and the
four-player bandwidth budgets before the codec is frozen.

### 2.4 Population and AI

Population is a Match child and host-only simulation owner. It maintains global caps
of 64 live pedestrians and 32 live cars (24 traffic and 8 parked/available, with
occupied cars counted), plus bounded retained dead/wreck state. Replenishment:

- uses CityData candidates and Match spawn reservations;
- rejects candidates in any admitted player's view or clearance envelope;
- performs bounded candidates and work per tick;
- never deletes an occupied, in-chain or otherwise required entity to make room;
- restores caps gradually and records spawn failure rather than looping.

Traffic routes on the directed lane graph and emits ordinary drive commands. A car
has exactly one controller: traffic, admitted driver, or neutral/coast. Player exit,
death or disconnect does not resume traffic AI. Pedestrians route on sidewalk and
crossing data, and their wander/flee controllers emit ordinary foot commands. Render
visibility never suspends authoritative AI, health, timers or collision.

S09 and S10 establish algorithms and measured host budget shares; S11 establishes
replication. M1-C3 productionizes accepted results rather than importing a complete
spike fixture.

### 2.5 Combat, presentation, UI and audio

WeaponState validates fire rate, magazine, reload, rocket cooldown, alive/unseated
state and gameplay capacity before allocating ShotId. DamageResolver owns hitscan,
projectile and attribution. S12 selects host-current-state versus bounded rewind;
client-claimed hits are not acceptable authority. Rockets are host gameplay entities
with cosmetic client flight and a reliable impact/expiry result.

Explosions reserves authoritative work before accepting it, marks a car terminal
once, orders jobs by due tick/EventId, completes occupant/seat/health/collision state
and then publishes. Every published explosion creates an effect instance from a
saved scene. Under load, the effect owner may select a cheaper authored variant or
reduce emission counts; it may not drop the effect or any gameplay work.

Presentation reads committed state/events. HUD values come directly from Health,
WeaponState, PlayerLifecycle and VehicleInteraction. The minimap draws CityData's
road polylines, not a second street layout. UI mockups may change saved composition
but not ownership. Audio uses state/event-driven emitters with category voice limits,
priorities and ducking; uncapped visual explosions do not imply unbounded audio
voices. LocalSettings alone persists master/music/SFX values.

## 3. Fixture promotion plan

Fixtures stay runnable and keep their historical evidence. Promotion means porting
a reviewed rule behind a production API, then changing or adding fixture coverage
to exercise that production API. Production code never depends on spike paths.

| Spike | Production disposition | Regression disposition |
| --- | --- | --- |
| S01 asset roundtrip | Port the explicit Blender→GLB→linked-wrapper workflow and resource checks. Do not promote the blockout models as production art. | Keep source/reexport/identity fixture and negative probes. |
| S02 foot/camera | Port the revised world-relative movement rule, command type, collision envelope candidate and 42° camera composition. Rewrite device input as production LocalRig. Remove cutaway behavior. Art and diagnostic aim overlay are not production. | Keep corner movement/collision/aim and Windows draw/focus cases, updated narrowly for WASD/mouse-facing. |
| S03 session | Rewrite the fixture service as typed production Session/Replication modules while preserving fixed endpoints, correlated operations, admission, per-entity freshness and clean teardown. Its JSON/marker codec is not promoted. | Keep the tiny two-process fixture as an independent protocol regression; add tests against production shell APIs. |
| S03-R foot response | Do not promote authority-only fixture networking or old tank commands. Implement the required shared-rule prediction in production using post-S02 commands. | Keep adverse proxy, pose-fence and drawn-response regressions; label historical confounded numbers. |
| S03-S Steam | Promote only backend-neutral operation/transport boundaries from the reviewed abstraction. Do not ship Steam code, addon initialization or Steam acceptance in M1. | Keep source research as design evidence; no M1 runtime test. |
| S04 car | Port accepted drive-rule math and CharacterBody adapter after owner drive-scene tuning. Rewrite prediction and network binding. Build full VehicleInteraction; the seated-resync fixture codec is not that system. | Keep body/passive/pose-fence tests and the standalone feel scene. Add production seat matrix tests. |
| S05 chains | Port ShotId retirement, reserved bounded jobs, ordering and movement/lifecycle separation. Replace sentinel occupant and fixed rows with production PlayerLifecycle/VehicleInteraction/entities. Apply the uncapped-effect decision. | Keep three-car, twelve-car, pressure, duplicate, late-hydration and drawn-effect tests. |
| S06 topology | Port graph/curve/map representation, stable IDs, bounds, stale-bake rejection and editor bake workflow into CityData. Production sectors are newly authored M1 content. | Keep crossing/turn/seam/map/stale-content fixture and rerun after final body dimensions. |
| S07 environment | Promote no gameplay code. Adopt measured block-scale guidance for sector granularity and art planning only. | Keep generated city variants and capped runner as performance diagnostics. It is not a release gate. |
| S08 export/ENet | Port the ENet bandwidth workaround into ENetTransport and reusable export-runner safety patterns. Do not promote fixture main scenes. | Keep Windows release/debug original-main matrix; add Linux CI smoke and exported production-shell checks. |
| S09 traffic (planned) | After acceptance, port the selected lane follower, gap/intersection and stuck state as TrafficController calling production VehicleMotion. Avoid AI-only physics. | Keep seeded 10-minute 24/32-car loops, obstacle/wreck and budget regressions. |
| S10 pedestrians (planned) | Port selected wander/cross/flee state and bounded scheduling as PedestrianController. Final rig comes from S13. | Keep seeded 64-agent normal/flee/crossing/cost cases and both compared motion options. |
| S11 population net (planned) | Port the measured codec, update schedule and interpolation only after bandwidth/baseline evidence. Integrate with production Replication rather than forking S03. | Keep full-cap synthetic rail population and real-process normal/adverse tests. |
| S12 combat (planned) | Port the selected host hit-registration policy, bounded history if selected, and starting definitions into Combat owners. Rewrite simple rail actors around production APIs. | Keep profile/target-speed verdict agreement, ShotId, ammo/rate and rocket-offset regressions. |
| S13 characters (planned) | Treat the Blender rig/blockout as a technical candidate. Promote source/rig/animation setup only after art and readability review; create production variants through linked assets. | Keep 68-live/16-dead crowd cost and animation-throttling comparison. |
| S14 audio (planned) | Port LocalSettings and an accepted voice policy. Placeholder generated sounds remain test assets unless explicitly approved for production. | Keep save/corrupt/recovery, voice-cap and storm tests; add owner listening checklist results separately. |
| S15 VFX (planned) | Port or rebuild accepted saved effect scenes under production art review. Preserve every-explosion visibility with authored quality degradation, never dropping. | Keep 12/24 explosions, shooters/rockets and capped graphical cost cases. |

A fixture may preload a production script/resource for a public-API test. If that
would make its historical evidence ambiguous, add a new production regression and
leave the historical fixture unchanged.

## 4. Production test strategy

### 4.1 Godot unit framework decision

Current Godot projects commonly use:

1. **GUT** — a Godot 4 GDScript test addon with assertions, doubles, parameterized
   tests, command-line execution and machine-readable output. It is mature and has
   a small test authoring surface. Sources: [GUT repository](https://github.com/bitwes/Gut)
   and [command-line guide](https://gut.readthedocs.io/en/latest/Command-Line.html).
2. **gdUnit4** — a Godot 4 test addon with GDScript/C# support, discovery, parameterized
   tests and reports. It has a richer IDE/test-runner integration and therefore a
   larger plugin surface to pin and verify. Sources:
   [gdUnit4 repository](https://github.com/MikeSchulze/gdUnit4) and
   [documentation](https://mikeschulze.github.io/gdUnit4/).
3. **A minimal in-repository runner** — no vendor dependency and complete control,
   but the project would own discovery, assertions, filtering, failure locations,
   async cleanup and CI reports. Existing spike probes demonstrate outcomes, but
   they are not a maintainable general unit framework.

**Proposal: use GUT for production GDScript unit/component tests.** It supplies the
needed assertion/reporting features without making us maintain a framework, while
the existing Python runners remain better for real processes and evidence. M1-D1
pins one reviewed GUT revision, checks it against Godot 4.8-dev7 on Windows/Linux,
keeps it test-only and excludes its third-party scripts from project-owned style
rules without suppressing production diagnostics. Do not enable it as a runtime
autoload or export it in release builds.

Godot's command-line and headless behavior remain engine-owned; see the official
[command-line tutorial](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html).
Tests must still inspect logs because Godot can emit diagnostics with exit status 0.

### 4.2 Test layers

| Layer | Scope and examples | Required trigger |
| --- | --- | --- |
| Python unit | Runner parsing, process ownership, codecs implemented in Python, evidence analysis | Every tools change; all CI jobs |
| GUT unit | Validators, revisions, command normalization, damage ordering, route/spawn selection, settings schema | Every production rule change |
| Headless component | Saved scene plus public APIs: collision, seat transaction, respawn, chain, CityData, AI | Affected subsystem on Windows and Linux where deterministic |
| Headless gameplay | Standalone saved Match: walk/aim/fire, drive/exit, death/respawn, population, reset | Per merge after those systems exist |
| Real-process network | Exported or project host/client, admission, authority, prediction, loss/jitter/stalls, host loss | Session/replication changes; nightly full profiles |
| Drawn/windowed | Actual frame receipts and selected PNGs for camera, HUD, minimap, VFX and animation | Presentation changes on Windows; bounded Linux graphical job where available |
| Manual review | Physical controls/focus, feel, readability, listening and menu navigation | M1-D2 and before gates/build delivery |
| Performance | Named hardware, exact content/build, raw samples, repeated capped runs | Scheduled/baseline comparisons and M1-D3 |
| Export | PCK membership, launch, input/audio/network, missing dependency and clean teardown | Both target OSes before A-GATE and D4 |

Unit expectations use externally visible outcomes, not copied implementation
formulas. Every production bug fix adds the lowest practical regression plus any
higher-level case needed to protect the contract.

### 4.3 Network suite

Python owns multi-process orchestration because it can allocate ports and private
`APPDATA`/`LOCALAPPDATA`/XDG roots, capture stdout/engine logs, enforce deadlines and
stop only its children. Cases drive normal production entry points, not test-only
parallel simulation.

Required suites are:

- shell: standalone, host/join, cancel/retry, incompatible/full/unreachable, host
  loss and leave/rejoin;
- admission: connected input rejected, bounded baseline/journal/handoff, duplicate
  readiness/acks, slow/overflow join and rollback;
- prediction: local foot and car response, matching-tick restore/replay, overflow,
  collision/life/control invalidation and no replay effects;
- lifecycle: seat races, blocked/moving exit, driver death/disconnect, destruction,
  respawn, late join and reset while driving/firing/joining;
- population: full cap, lifecycle churn and current-state hydration;
- delivery: normal/adverse delay, jitter, loss, interruption and host stall, plus
  malformed/rate/queue bounds;
- bandwidth: actual transport bytes in worst ten-second windows and separate join
  bytes at host plus three clients.

Use the ENet server bandwidth workaround in every production and fixture adapter
until a fixed engine is deliberately selected. Unreliable traffic remains lossy;
tests require bounded recovery, not delivery of each send.

### 4.4 CI split

**Every pull request, Windows and Linux:** pinned engine/gdstyle identity, formatting
and lint, explicit compile of every owned script, Python unit tests, GUT unit tests,
resource/UID/source-link checks and a short standalone headless smoke. All output
uses fresh external directories and is uploaded on failure.

**Every pull request, one primary OS after the shell exists:** bounded two-process
ENet baseline and session cleanup. Run on both OSes for changes under `session/`,
`replication/`, export configuration or platform-sensitive code.

**Nightly or manually dispatched:** full normal/adverse profiles, population-cap
bandwidth, lifecycle matrix, longer AI seeds and export launch smoke. Windows owns
the routine drawn 1280×800 checks because current evidence establishes drawability;
Linux owns native release/ENet confirmation and a bounded graphical smoke when the
runner supports it.

**Not ordinary hosted CI:** subjective feel/listening, ten-minute integrated capacity,
GPU comparisons and delivery-signing/private publication. These run on named local
hardware with retained raw data. CI must never claim Deck or Steam acceptance.

### 4.5 Performance regression policy

Keep tiny deterministic timing checks out of correctness pass/fail unless they catch
an algorithmic bound. Hardware timings use an exact exported build, content manifest,
renderer, power state and concurrent Godot-process/CPU-load record. Run at least
three repeats; report median and worst. A contended run is an upper bound.

Track frame p50/p95/p99, render CPU/GPU, host simulation p95/p99 including AI/chains,
working set, draw calls, active counts, encode/decode time and wire bandwidth. Compare
against the ratified design budgets without silently changing content or quality.
S07's city-size curve informs authored scope; M1-D3 still validates the integrated
six-block milestone.

## 5. Ordered M1 backlog

Sizes are dispatch units, not calendar promises: **S** is one narrow owner/API with
focused tests, **M** spans several collaborators or one real-process matrix, and
**L** is an integration outcome that must be split into its listed children before
implementation. A lane owns distinct files; one integrator owns shared Boot, Match,
district and project/export settings.

| Order / task | Size | Depends on | Parallel lane and acceptance |
| --- | --- | --- | --- |
| 1. **M1-D1.1 — establish production checks**: pin GUT, add test-only config, release exclusions and CI scripts | M | P0-GATE | Tooling lane. Windows/Linux exact pins; owned scripts compile; Python/GUT smoke and diagnostic-negative pass; no addon in export manifest. |
| 2. **M1-A1.1 — compose Boot and session state machine**: saved Boot/menu/status scenes, typed operations, standalone path and fake correlated provider | M | P0-GATE | Session/UI lane. One completion per accepted operation; busy/cancel/close/retry and late callback cleanup tested. |
| 3. **M1-A3.1 — LocalSettings and settings UI** | S | P0-GATE, D1.1 test seam | Settings/UI lane, separate from Boot file owner. Defaults, validation, corrupt recovery, live preview, atomic-save failure and restart pass. |
| 4. **M1-C1.1 — road/building/prop starter subset** | M | P0-GATE art approval | Art lane. Source-linked Blender/GLB families, provenance, collision and reexport/reload identities pass; enough for first production sector. |
| 5. **M1-A1.2 — ENet transport and menu host/join flow** | M | A1.1 | Session lane. Workaround before peer publication; standalone and ENet without Steam; bounded full/incompatible/unreachable/host-loss cleanup in real processes. |
| 6. **M1-A2.1 — production foot command and ActorMotion** | M | D1.1, ratified S02 control update | Actor lane. Standalone/authority/replay equivalence, collision/aim, focus neutral and malformed command tests. |
| 7. **M1-A2.2 — identity, baseline and durable replication core** | L | A1.2, A2.1 | Replication lane, split codec/admission/state-apply commits. Current state before input, bounded transfer/journal, stale revisions and subset recovery pass. |
| 8. **M1-A2.3 — local foot prediction and remote interpolation** | M | A2.1, A2.2 | Local/replication lane. Normal/adverse correction, history bounds, life/control/collision invalidation and replay side-effect exclusion pass. |
| 9. **M1-A2.4 — player lifecycle, safe respawn and match reset** | M | A2.2, C2.1 spawn anchors | Match lane. Three-second respawn, bounded blocked search/retry and reset rehydration retain admitted peers with no old work. |
| 10. **M1-C4.1 — HUD/minimap shell** | M | A2.2, production CityData from C2.1 | UI lane. Reads owner state, shared roads align, controlled marker rebind/late join works at supported resolutions. |
| 11. **M1-A3.2 — production audio buses and voice policy** | M | A3.1, accepted S14 evidence | Audio lane. Persistent settings, category limits, state-driven emitters and clean teardown; owner listening review remains explicit. |
| 12. **M1-A-GATE — exported multiplayer shell** | L | A1.2, A2.3, A2.4, A3.2 | Integration. Two Windows and two Linux processes cover settings, join/admission, movement/prediction, respawn/reset, errors and host loss; no Steam criterion. |
| 13. **M1-B1.1 — production vehicle motion and tuning** | M | A-GATE, owner drive-scene values | Vehicle lane. Same rules for standalone/host/replay/AI; local prediction corrects boundedly; wall/brake/reverse/handbrake cases pass. |
| 14. **M1-B1.2 — VehicleInteraction transaction matrix** | M | B1.1, A2.4 | Match/vehicle lane. Same-tick claims, stopped/blocked exit, death/disconnect coast, reset/resync/destruction and revision fences pass. |
| 15. **M1-B2.1 — WeaponState and hitscan** | M | A-GATE, S12 decision | Combat lane. Pistol/SMG rate/ammo/reload/equip/no-seated-fire, ShotId duplicates and host verdict pass normal/adverse tests. |
| 16. **M1-B2.2 — rockets, Health and player/pedestrian death** | M | B2.1, A2.4 | Combat/lifecycle lane. Capacity/cooldown, impact/expiry, friendly/self damage, full-loadout respawn and hydration pass. |
| 17. **M1-B3.1 — explosions, wrecks and chains** | M | B1.2, B2.2 | Combat lane. Three/12-car outcomes, bounded work, occupied destruction, collision fence, retention, late join and reset pass off-camera. |
| 18. **M1-B4.1 — combat VFX/audio/HUD feedback** | M | B3.1, accepted S14/S15 evidence | Presentation lane. Every explosion visible, duplicates suppressed, cheaper quality fallback measured, readable weapon/rocket feedback and bounded audio. |
| 19. **M1-C1.2 — character, vehicle, weapon and effect production assets** | L | Accepted S13/S15 technical evidence and owner art review | Parallel asset lanes by family. Linked sources, rigs/clips/sockets/collision/provenance and target-camera readability pass before integration. |
| 20. **M1-C2.1 — saved production district and CityData bake** | L | C1.1; later consumes approved C1.2 subsets | Sole world integrator. Six blocks, two loops, alley, landmark and stunt area; seam/route/clearance/map/stale-bake/source identity checks pass. |
| 21. **M1-C3.1 — traffic controller and car population** | M | B1.2, C2.1, accepted S09 | Population lane. 24 traffic/32 total cap, lanes/turns, obstacle/wreck recovery, abandoned cars parked and bounded unseen replenishment pass seeded runs. |
| 22. **M1-C3.2 — pedestrian controller and population** | M | B2.2, C2.1, accepted S10, C1.2 rig | Population lane. 64 cap, sidewalk/crossing, flee, damage/death/16 retention and bounded unseen replenishment pass seeded runs. |
| 23. **M1-C3.3 — population replication and capacity profile** | L | C3.1, C3.2, accepted S11 codec | Replication integrator. Full current join, lifecycle reliability, smoothing, baseline and all four-player bandwidth budgets pass. |
| 24. **M1-D1.2 — complete production validation/CI** | M | All owner APIs stable enough | Tooling lane. Contract/resource/export discovery includes every production path and catches unused/broken scripts without broad suppression. |
| 25. **M1-D2 — integrated playtest and tuning** | L | B4.1, C3.3, C4.1 | Integration/owner review. Walk/aim/shoot/drive/chain/explore, menus/focus, audio and readability findings are fixed or explicitly scoped out. |
| 26. **M1-D3 — integrated capacity and adverse delivery** | L | D1.2, D2 | Performance/network lane. Named Windows/Linux hardware, host+3 clients, six-block caps/bursts/lifecycle; ratified frame/sim/memory/bandwidth/recovery budgets with raw evidence. |
| 27. **M1-D4 — private review builds** | M | D2, D3 | Release lane. Exact Windows/Linux exports, identity/exclusions, clean launch/input/audio/ENet, retained hashes/results/rollback and VCS delivery; no Steam upload. |
| 28. **M1-GATE — owner review** | — | D4 | Owner accepts the playable district or records bounded follow-ups/scope changes. |

C1.1 can proceed beside the session shell and settings. C2.1 begins as soon as its
approved road/building subset exists rather than waiting for characters/audio/VFX.
Actor, replication and world integrators must agree on APIs before parallel file
work; they do not concurrently edit Boot, Match or district scenes.

### First five starts

1. Start **D1.1** so all subsequent code lands with one unit/CI path.
2. Start **A1.1** in parallel, owning Boot/Session composition.
3. Start **A3.1** in a separate settings scene/script lane.
4. Start **C1.1** in separate source/prefab files with one world integrator designated.
5. Start **A1.2** immediately after A1.1 freezes the provider seam; it is the first
   dependent continuation, while the other three lanes continue.

Do not start production replication by copying the S03 fixture before A1.1/A1.2 and
the production identity types are reviewed. Do not start C3 population by replacing
missing S09–S11 evidence with dummy behavior.

## 6. Risk register and owner-review questions

| Risk | Consequence | Mitigation / owner question |
| --- | --- | --- |
| Canonical requirements still name Steam/Deck and rejected controls/effect cap | Teams implement or gate against superseded scope | P0-GATE records one dated reconciliation. **Owner:** confirm this plan's ENet-only, desktop-only M1 wording is the governing milestone scope. |
| Prediction against CharacterBody contacts is approximate | Visible corrections, divergent foot/car behavior or replay side effects | Separate motion replay state, revision fences and adverse tests before gameplay integration. Snap/resync on overflow; no historical-world rollback claim. |
| Vehicle handling remains subjective | B1 foundations may be rebuilt after integration | Owner runs the standalone S04 drive scene and ratifies tuning/body dimensions before B1.1 freezes definitions. |
| Hitscan policy is unsettled | High-latency disagreement or exploit surface | S12 compares host-current and bounded rewind. **Owner:** approve the recommended policy and maximum rewind before B2.1. |
| “Every explosion visible” has no accepted quality-degradation rule | 12/24 effects may violate frame budget or produce unreadable output | S15 measures authored full/cheap variants. **Owner:** confirm reducing particles/lighting while retaining one visible effect per explosion is allowed. |
| Production art differs greatly from grey-block evidence | Memory, draw and animation costs arrive late | C1 delivers source-linked subsets early; repeat representative capped tests as each family lands. S07 is planning guidance, not a pass. |
| AI spikes may meet correctness but consume too much of the 4 ms host budget | Integrated host misses simulation target | S09/S10 propose measured shares; C3 runs both together before content lock and reduces bounded update frequency only with correctness evidence. |
| Full population codec misses bandwidth/join targets | Late replication rewrite | S11 measures full caps before A2 codec freeze where possible; retain replaceable motion, per-entity refresh and immutable durable ownership. |
| GUT or its editor plugin conflicts with pinned dev engine/addons | CI instability or exported test code | D1.1 pins and proves headless CLI on both OSes, keeps plugin disabled at runtime and verifies export exclusion. No broad warning suppression. |
| Shared scenes become parallel merge hotspots | Lost authored placement/identity or accidental multiple writers | Assign one Boot, Match and district integrator. Parallel lanes contribute saved prefabs/public APIs and hand off for placement. |
| Linux release diagnostics or dev-engine regressions recur | One target cannot pass clean export | Run Linux export smoke at A-GATE, retain exact logs, and escalate an engine-pin decision rather than suppress diagnostics. |
| No Deck acceptance in M1 | Later handheld work may require renderer/input/UI changes | Keep 1280×800 and controller-friendly composition in design, but label it unverified. Deck becomes a separately planned post-M1 target. |
| Schedule pressure encourages making large tasks monolithic | Review and regression gaps | Split every L row at its named owner seams before dispatch; gate integration on public-API tests rather than completion prose. |

Additional owner review at P0-GATE:

1. Ratify the final vehicle body dimensions and S04 drive tuning when the feel scene
   result is available.
2. Ratify S12 weapon damage, fire rate, magazine/reload, rocket cooldown and hit
   registration defaults before B2.
3. Select the production art subsets that unblock C1.1/C2.1; later families must not
   block initial sector assembly.
4. Confirm that Windows/Linux desktop budget evidence on named available hardware is
   sufficient for M1 review while Deck remains explicitly untested.
5. Approve adding the pinned test-only GUT dependency under D1.1.

## 7. Suggested task-record reconciliation

Do not edit the task index until the owner reviews this proposal. Suggested concise
changes for `docs/plans/task-requirements.md` are:

- **M1-A1/A-GATE:** ENet and standalone only for M1; prove the backend-neutral seam,
  but move real Steam gameplay/install criteria to a later milestone.
- **M1-A2:** explicitly require local foot prediction with world-relative WASD and
  mouse-facing, plus authoritative correction/replay side-effect fences.
- **M1-B1:** explicitly require local car prediction, stopped-only exit below 0.5 m/s,
  no firing from cars and coast-on-disconnect.
- **M1-B3/B4:** every committed explosion receives a visible effect; quality may
  degrade under measured load, but dropping effects is not an accepted fallback.
- **M1-D3/D4:** M1 target exports are Windows and Linux desktop. Remove Deck and
  Steam from M1 acceptance and retain them as later target/transport work.
- **S07/C2:** use the environment cost-versus-block envelope as city-planning guidance,
  not a population/network/capacity gate.

Suggested TODO refinement: keep the existing M1-A..D outcome bullets concise and
link this plan for the ordered child tasks and acceptance checks rather than copying
this table into `TODO.md`.
