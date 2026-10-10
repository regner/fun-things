# M1 production plan

8 October 2026; gate disposition updated 9 October 2026. This production architecture, test and
backlog plan passed P0-GATE under owner decision 27, and M1 production has started. It does not
claim that production gameplay is complete. The [product brief](../design.md),
[ownership map](../architecture.md), [API contracts](../api-contracts.md),
[scene contracts](../scene-structure.md) and [multiplayer guide](../multiplayer.md)
remain the detailed sources for rules that are not changed below.

**Whole-city replan, 9 October 2026.** The owner dropped the six-block M1 area in favour of
the whole Brackett island and parallel asset tracks
([parallel art production](../workflows/parallel-art-production.md)), asking to “get us to
playable game as fast as possible”. The [Brackett greybox](../assets/brackett_greybox.md) and
the first player, pedestrian, car, weapon and weapon-effect assets are delivered (section 5.5).
M1-D1.1 production checks and M1-A1.1 Boot/session are integrated. Owner decisions 33–44 adopt
TheDuckCow's Road Generator as a conditional pilot with no bake step: roads generate live in
the editor and at level load, and gameplay road data derives at load (decisions 40–41). See
the [road-tool evaluation record](../spikes/road-tool.md); its explicit-bake production
breakdown is superseded on `main` by decisions 40–44 and this plan's RT rows, and RT-01 lands
the rewritten record. Decision 35 records the orchestrator as the current gameplay integration
owner, pending owner confirmation. Decision 39 moved spike fixtures into the reference-only
[`prototypes/`](../../prototypes/README.md) archive. Section 5 is the current ordered
backlog; it replaces the 8 October ordering and every six-block acceptance.

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

P0-GATE reconciled older Steam, Deck, tank-control, cutaway and eight-effect wording;
production must not implement superseded requirements merely because dated drafts retain
them. **Historical scope note:** owner instruction 12 originally made unfinished S02–S08,
S03-P/S04-P, S09–S17 and audit G tasks gate dependencies. Owner decision 14 narrowed that
scope to the integrated S17 quiet record and refreshed packet; owner decision 27 records the
9 October 2026 pass. Remaining human checks and subsystem choices belong to their M1 consumers.

## 1. Production shape

### 1.1 Directory and dependency layout

Create directories only with their first real resource. Production code must not
import from `tests/` or the `.gdignore`d `prototypes/` archive. Archived spike fixtures are
reference-only and not runnable in the project (decision 39); production regressions are
written against production APIs under `tests/unit/` or as runner cases in `tools/`.
Delivered asset wrappers currently live under `scenes/prefabs/<family>/` and
`scenes/effects/`; asset checks live under `tests/assets/` (section 5.5).

```text
res://
  scenes/
    boot/                 boot.tscn: process-lifetime composition
    ui/                   menu, status, settings, HUD and reusable widgets
    match/                match.tscn and match-owned coordinators
    world/                Brackett city, district and ground sectors
    prefabs/              buildings, props, road fixtures and delivered asset wrappers
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
    world/                CityData queries and load-time road-data validation
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
    assets/                delivered-asset resource checks and previews
    diagnostic/            intentional-failure checks for the test runner
  tools/                   checks and external-process runners
  addons/                  pinned GUT (test-only); Road Generator after RT-01 (runtime)
  prototypes/              reference-only spike archive under .gdignore
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
| CityData | World/content identity, load-time road-data derivation (decision 41), map data, route and shared clearance queries | Population, lifecycle, interactions and minimap consume one representation |
| SpawnReservations | Atomic dynamic spawn/exit reservations | PlayerLifecycle and Population reserve before body insertion |
| ActorMotion | Foot pose, velocity and facing rule | Local input, host remote input and pedestrian controller submit typed commands |
| PlayerLifecycle | Death, three-second respawn, safe-spawn result and controlled entity | Coordinates Health, WeaponState and VehicleInteraction before publication |
| VehicleMotion | Car pose, velocity, handling/contact state and coast-to-stop policy | Player prediction, authority and traffic all call the same drive step |
| VehicleInteraction | Seat, enter/exit, control revision and transfer transactions | Enforces host-confirmed entry, stopped exit and no partial transition |
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
FootCommand {sequence, client_tick, move_xz, aim_yaw, fire_held}
ActorMotion.step(command, fixed_delta, AUTHORITY | REPLAY)

DriveCommand {sequence, client_tick, throttle, steer, brake, handbrake}
VehicleMotion.step(command, fixed_delta, AUTHORITY | REPLAY)
```

Foot movement normalizes diagonals, travels at 5 m/s, starts/stops immediately and
sets facing to the aim yaw. Input obtains the yaw from the mouse/camera ground-plane
intersection; simulation never reads mouse coordinates. `client_tick` remains the
canonical diagnostic/replay-ordering field; it never grants elapsed host time.
Vehicle AI and players use the same drive step and tuning resource.

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
occupied cars counted), plus bounded retained dead/wreck state. Where these live entities
are placed across the whole island is an open owner question; section 5.3 recommends
relevance-based placement around players under the same global caps. Replenishment:

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

S09 and S10 establish algorithms and measured timing reports; decision 22 makes their
old subsystem shares reporting only, not acceptance gates. S11 establishes replication.
M1-C3 productionizes accepted results rather than importing a complete spike fixture.

### 2.5 Combat, presentation, UI and audio

WeaponState validates fire rate, magazine, reload, rocket cooldown, alive/unseated
state and gameplay capacity before allocating ShotId. DamageResolver owns hitscan,
projectile and attribution. Decisions 18/21 select host-current-time verdicts and accept
S12's combat values as playtest-tuned M1 starting values; client-claimed hits are not
acceptable authority. Rockets are host gameplay entities with cosmetic client flight
and a reliable impact/expiry result.

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

Decision 39 moved the spike fixtures into the reference-only `prototypes/` archive; they
are no longer runnable in the project and keep their historical evidence there. Promotion
means porting a reviewed rule behind a production API and writing new production coverage
for it. In the regression column below, “keep” now means: keep the archived fixture as
reference and recreate the named case against production APIs when its consumer lands.
Production code never depends on archived spike paths.

| Spike | Production disposition | Regression disposition |
| --- | --- | --- |
| S01 asset roundtrip | Port the explicit Blender→GLB→linked-wrapper workflow and resource checks. Do not promote the blockout models as production art. | Keep source/reexport/identity fixture and negative probes. |
| S02 foot/camera | Port the revised world-relative movement rule, command type, collision envelope candidate and 42° camera composition. Rewrite device input as production LocalRig. Remove cutaway behavior. Art and diagnostic aim overlay are not production. | Keep corner movement/collision/aim and Windows draw/focus cases, updated narrowly for WASD/mouse-facing. |
| S03 session | Rewrite the fixture service as typed production Session/Replication modules while preserving fixed endpoints, correlated operations, admission, per-entity freshness and clean teardown. Its JSON/marker codec is not promoted. | Keep the tiny two-process fixture as an independent protocol regression; add tests against production shell APIs. |
| S03-R foot response / S03-P foot prediction | Do not promote authority-only S03-R fixture networking or old tank commands. M1-A2.3 integrates the completed S03-P shared-rule restore/replay evidence using post-S02 commands. | Keep S03-R adverse proxy, pose-fence and drawn-response regressions plus S03-P correction/replay regressions; label historical confounded numbers. |
| S03-S Steam | Promote only backend-neutral operation/transport boundaries from the reviewed abstraction. Do not ship Steam code, addon initialization or Steam acceptance in M1. | Keep source research as design evidence; no M1 runtime test. |
| S04 car | Port accepted drive-rule math and CharacterBody adapter, starting from decision 30's handling. Rewrite prediction and network binding. Build full VehicleInteraction; the seated-resync fixture codec is not that system. | Keep body/passive/pose-fence cases. The archived drive scene is replaced by a production standalone drive/tuning entry in M1-B1.1. Add production seat matrix tests. |
| S05 chains | Port ShotId retirement, reserved bounded jobs, ordering and movement/lifecycle separation. Replace sentinel occupant and fixed rows with production PlayerLifecycle/VehicleInteraction/entities. Replace the fixture's finite 12 saved slots with a lifetime-owned production pool that instances saved effect scenes without dropping events. | Keep three-car, twelve-car, pressure, duplicate, late-hydration and accepted 12-drawn/zero-drop tests. |
| S06 topology | Port graph/curve/map representation, stable IDs, bounds and stale-content rejection into CityData. Decision 41 replaces the editor bake with load-time derivation from the live road network (RT-05). | Keep crossing/turn/seam/map/stale-content fixture and rerun after final body dimensions. |
| S07 environment | Promote no gameplay code. Use 96 blocks as the last passing shared-grey-block desktop observation and 384 as the first crashing row, not as a product ceiling. M1-C2.1 measures the actual whole-island Brackett greybox instead (section 5.3). | Keep generated city variants and capped runner as performance diagnostics. It is guidance, not a release gate. |
| S08 export/ENet | Port the ENet bandwidth workaround into ENetTransport and reusable export-runner safety patterns. Do not promote fixture main scenes. | Keep Windows release/debug original-main matrix; add Linux CI smoke and exported production-shell checks. |
| S09 traffic (planned) | After acceptance, port the selected lane follower, gap/intersection and stuck state as TrafficController calling production VehicleMotion. Avoid AI-only physics. | Keep seeded 10-minute 24/32-car loops, obstacle/wreck and budget regressions. |
| S10 pedestrians (planned) | Port selected wander/cross/flee state and bounded scheduling as PedestrianController. Final rig comes from S13. | Keep seeded 64-agent normal/flee/crossing/cost cases and both compared motion options. |
| S11 population net (planned) | Port the measured codec, update schedule and interpolation only after bandwidth/baseline evidence. Integrate with production Replication rather than forking S03. | Keep full-cap synthetic rail population and real-process normal/adverse tests. |
| S12 combat (planned) | Port the selected host hit-registration policy, bounded history if selected, and starting definitions into Combat owners. Rewrite simple rail actors around production APIs. | Keep profile/target-speed verdict agreement, ShotId, ammo/rate and rocket-offset regressions. |
| S13 characters (planned) | Treat the Blender rig/blockout as a technical candidate. Promote source/rig/animation setup only after art and readability review; create production variants through linked assets. | Keep 68-live/16-dead crowd cost and animation-throttling comparison. |
| S14 audio (planned) | Port the accepted voice policy with default bus levels; defer LocalSettings/settings UI to M1-D5. Placeholder generated sounds remain test assets unless explicitly approved for production. | Keep save/corrupt/recovery, voice-cap and storm tests; add owner listening checklist results separately. |
| S15 VFX (planned) | Port or rebuild accepted saved effect scenes under production art review. Preserve every-explosion visibility with authored quality degradation, never dropping. | Keep 12/24 explosions, shooters/rockets and capped graphical cost cases. |

A fixture may preload a production script/resource for a public-API test. If that
would make its historical evidence ambiguous, add a new production regression and
leave the historical fixture unchanged.

### 3.1 Art production throughput estimate

This is a planning range, not a delivery promise. One **focused artist-day** means a
source edit plus explicit export, linked wrapper/collision or rig setup, source record,
reexport check and one review correction on the established pipeline. It excludes
waiting for owner feedback and unrelated engine/tool repairs. Before using the range,
S01-W must establish the exact Windows Blender result and the owner must select a
production quality bar.

| Deliverable package | Starting scope | Estimated focused artist-days |
| --- | --- | ---: |
| District starter subset | Road/sidewalk kit, two building families and two prop/sign families, sufficient to start C2.1 | 10–16 |
| Remaining district kit | Four building/landmark families and four prop/sign families | 12–20 |
| Vehicles | Two silhouettes, color variants and corresponding wreck states | 8–12 |
| Shared people | Player/pedestrian rig, readable variants and idle/walk/run/death clips | 10–15 |
| Weapons and held presentation | Pistol, SMG, launcher, mounts/muzzles and variants | 4–7 |
| Production VFX art | Muzzle/impact/tracer/rocket and full/cheap explosion families | 6–10 |

The subtotal is **50–80 focused artist-days**. Reserve about 20% (10–16 days) for
cross-family camera readability, collision/socket correction, source reexports and
world-integration review, giving **60–96 focused artist-days** for the visible M1 kit.
Audio sourcing/editing is tracked separately under S14/A3.2. Two genuinely independent
asset lanes could improve wall-clock throughput, but shared character, material and
world integration plus owner review prevent assuming a linear 2× speedup.

The starter subset is intentionally first: at roughly 10–16 artist-days it unlocks
C2.1 while the remaining families continue in parallel. Record actual throughput for
the first two accepted families and reforecast C1.2; do not respond to a slower rate
by dropping source, identity or review checks.

**Whole-city status, 9 October 2026.** This estimate predates the whole-city replan and is
historical. The parallel tracks delivered first-pass vehicles, shared people, weapons and
weapon VFX (section 5.5). Road/sidewalk surfaces now come from the road tool under
decision 42, so only road fixtures (signals, street lights, prefab intersection pieces)
remain Blender work. District building/prop families wait for the owner-run M1-C0 asset
lists. Reforecast from the delivered tracks' actual throughput, not from this table.

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
working set, draw calls, active counts, encode/decode time and wire bandwidth. Use the
safe capped method settled by S08-C; do not repeat the uncapped runs that removed the
GPU device. The audit's [owner question 2](../reviews/p0-readiness-audit-2026-10-08.md#5-owner-questions)
historically noted that deferring Deck left no ratified desktop frame target. Owner
decision 15 now sets capped 60 FPS with frame p95 <= 16.7 ms and p99 <= 20 ms on the
named RTX 4070 Laptop Windows reference and a Linux machine when available. The target
remains tunable during M1; do not silently change content or quality to claim it.
S07's city-size curve informs authored scope: its repeated grey-block rows passed at
6, 24 and 96 blocks, while 384 crashed before a result. The fit (about 0.79 MiB working
set and 138 expanded nodes per repeated-content block) is planning guidance with large
production-art caveats, not a supported-size promise. M1-C2.1 records the whole-island
Brackett greybox baseline and M1-D3 validates the integrated whole-island milestone.

## 5. Foundation entry criteria and ordered M1 backlog

The audit found risks that should produce evidence before their production consumers,
not be rediscovered inside M1. These IDs are external foundation dependencies in the
backlog below; all of them are complete as foundation tasks:

| Foundation task | Required result | Hard consumers in this plan |
| --- | --- | --- |
| **P0-TOOLING** | Green canonical style/compile command, complete Python test discovery, cross-platform Python invocation and MCP-free compile mirror; GodotSteam artifact handling is obsolete after addon removal | M1-D1.1 (done) and every later CI claim |
| **S03-L** | Per-stage Windows baseline latency/pacing diagnosis and a disposition of the S03-R expiry boundary | M1-A2.3 and M1-B2.1/S12 interpretation |
| **S08-X** | Both target exports, a Windows launch, committed main-scene/preset decisions, pinned template identity, GodotSteam-removal/package-rejection proof, and a Linux launch checklist; Linux launch acceptance remains at M1-A-GATE | M1-A1.1 (done), M1-A-GATE, RT-11, M1-D3 and M1-D4 |
| **S08-C** | Bounded 384-block crash/cutaway diagnosis and a safe capped GPU measurement method | M1-C2.1 capacity baseline, RT-10 and M1-D3 |
| **S01-W** | Exact Windows Blender version and byte or semantic reexport result | M1-C1.1–C1.3 |
| **S03-P** | Bounded shared-rule foot prediction/reconciliation evidence after S02 controls and S03-L | M1-A2.3 |
| **S04-P** | Bounded shared-rule car prediction/reconciliation evidence after S03-L | M1-B1.1 |
| **S04-T** | Two-process predicted foot↔car evidence, racing claims, moving/blocked exit, AI release and disconnect coast; decision 23 retains predicted entry only as a later option | M1-B1.2 and M1-D2 |
| **S17** | Integrated full-cap host-tick composition after S09–S12, including S11 encode for three clients | M1-A2.2 codec freeze, M1-C3 and M1-D3 |

S11's accepted full-cap codec, baseline and wire-budget evidence is independently a
**hard** M1-A2.2 dependency. S17 does not substitute for it. **Historical scope note:**
the 8 October audit reconciliation made unfinished S02–S08, S03-P/S04-P, S09–S17 and
G1–G7 P0 dependencies. Owner decision 14 narrowed that scope, and decision 27 passed P0-GATE.

### 5.1 Fastest path to a playable multiplayer slice

The owner's goal is a playable game as fast as possible, built in parallel. The backlog is
therefore organized as four playable checkpoints in the existing Brackett greybox, each
built on the accepted host-authority, prediction and replication contracts. Each checkpoint
is reviewable by playing it; none waits for production district art.

| Checkpoint | Playable outcome | Completing rows |
| --- | --- | --- |
| **P1 — walk together** | Boot → menu → host/join over ENet → the Coral Courier walks the whole Brackett greybox with the 47 m / 42° north-up camera, local prediction, smooth remote players, respawn/reset and a HUD shell; exported Windows/Linux processes | 1–9 |
| **P2 — drive together** | The three delivered cars park at authored anchors and drive with decision 30 handling; host-confirmed entry (decision 23), stopped exit, coast on disconnect/driver death | 11–12 |
| **P3 — fight together** | Pistol, SMG and Dock Thumper with decision 18 host-current-time verdicts and decision 21 values; delivered muzzle/hit/trail/explosion effects; Health, death, chains and wrecks | 12a–14, 18–19 |
| **P4 — living city** | Road-tool roads replace the greybox road strokes; traffic and pedestrians use load-time graphs; road minimap from the same data | 3a, 20–34 |

Decision 14's first production work runs from the start beside P1: M1-C3.0 builds the pedestrian
behavior/budget core against synthetic navigation graphs, and M1-D3.0 instruments and tracks the
host budget as each simulation row lands. The road tool (rows 20–30) and content tracks (rows
12a, 15–17, 35) also run in parallel with P1–P3 from the start. P1–P3 do not depend on the road
tool: the greybox already provides a flat ground collider under its road and walk strokes, so
walking and driving need no road-tool output; C2.1 must still prove that traversal, which the
greybox handoff did not test. Only traffic, pedestrians and the minimap need road-derived data,
and they must not invent a second interim road layout (decision 33).

Two dependency changes from the 8 October ordering are deliberate. First, vehicles and weapons
now depend on the shell's production rows (A2.3/A2.4) rather than on the exported M1-A-GATE, so
P2/P3 work can overlap the export and Linux checks. D2 depends on M1-A-GATE, so D3, D4 and
M1-GATE cannot pass without it; an A-GATE finding is fixed in the owning row. Second, the
six-block C1.1 → C2.1 art-first chain is replaced: C2.1 now integrates the delivered greybox for
play and C2.2 replaces greybox districts with production art later.

### 5.2 Ordered backlog

Sizes are dispatch units, not calendar promises: **S** is one narrow owner/API with
focused tests, **M** spans several collaborators or one real-process matrix, and
**L** is an integration outcome that must be split into its listed children before
implementation. A lane owns distinct files; one integrator owns shared Boot, Match,
world scenes/CityData and project/export settings. Under decision 35 the orchestrator is
that integration owner (pending owner confirmation) and assigns the Boot/Match and world
integrator lanes. Order numbers guarantee that every row depends only on an earlier row,
an accepted foundation result or a named owner input; they are not a schedule, and the
checkpoint/track column shows what can run in parallel.

| Order / task | Size | Depends on | Checkpoint / lane and acceptance |
| --- | --- | --- | --- |
| — **M1-D1.1 — production checks** | M | accepted P0-TOOLING | **Done** (`a9e234b`–`2626d0e`): pinned test-only GUT 9.7.1, `tools/production_checks.py`, Windows/Linux CI entry and export exclusion; [record](../spikes/m1-d1-1.md). Linux CI execution remains unobserved. |
| — **M1-A1.1 — Boot and session state machine** | M | accepted S08-X | **Done** (`731bf8c`–`cf9a54d`): saved Boot/menu/status, typed operations, standalone path and test-only fake provider; [evidence](../spikes/m1-a1-1-evidence/README.md). |
| 1. **M1-A1.2 — ENet transport and menu host/join flow** | M | A1.1 | P1, session lane. Workaround before peer publication; standalone and ENet without Steam; bounded full/incompatible/unreachable/host-loss cleanup in real processes. |
| 2. **M1-C2.1 — Brackett greybox play world** | M | A1.1, D1.1, accepted S08-C | P1, sole world integrator. Match loads the saved [`city.tscn`](../../scenes/world/brackett_greybox/city.tscn) (never the review preview); CityData publishes a world/content identity that admission checks (`CONTENT_INVALID` on mismatch); provisional player-spawn and parked-car anchors are saved markers (owner question 5); S02 foot and S04 car envelopes cross ground-sector seams, bridge and building edges without snags; record the whole-island capacity baseline (section 5.3). No road topology: RT-05 owns it. |
| 3. **M1-A2.1 — production foot command and ActorMotion** | M | D1.1, accepted S02 control update | P1, actor lane. Standalone/authority/replay equivalence, `client_tick`, collision/aim, focus neutral and malformed command tests. |
| 3a. **M1-C3.0 — pedestrian core behavior and budget** | M | D1.1, accepted S10, accepted S17, decisions 14, 22 and 32 | Decision 14 first production work, population lane. Host-only pedestrian core with compact typed state, a reusable spatial grid, staggered 10 Hz decisions over 60 Hz motion, wander/cross/flee states and a finite crossing reservation API (decision 32) with capped wait, queue length and overlap duration. It consumes an **injected navigation interface** (nodes, sidewalk links, crossings, conflict sets): synthetic test graphs now, RT-07/CityData graphs later through C3.2. The S06 topology fixtures are archived in `prototypes/` and not loadable, so tests build their own graphs. Before scaling, the lane records numeric behavior acceptance thresholds on S10's metric definitions (sampled overlap pairs and continuous overlap duration, stuck identities below 0.25 m displacement, crossing wait and queue age, flee reaction) and passes them on seeded 64-agent normal/flee runs. Timings are reported through D3.0 as reporting only (decision 22), never as a gate. It emits the standard foot command; binding to ActorMotion bodies happens in C3.2. |
| 3b. **M1-D3.0 — host-budget instrumentation and tracking** | S, ongoing | D1.1, accepted S17 | Decision 14 first production work, performance lane. Add production host-tick timing (S17's section brackets: total plus per-subsystem reports) and a repeatable capped tracking run reporting median/p95/p99 against decision 22's soft ~4 ms total p95 at the current tunable population settings. It starts with the first simulation rows (A2.1, C3.0); every later simulation row (A2.2, B1.1, B2.x, B3.1, C3.x) adds its section and reports the tracked total when it lands, and the trend is checked at least at each checkpoint P1–P4. Subsystem timings are reports only; when the total is threatened, optimize the largest contributor, pedestrians first. D3 keeps final integrated acceptance. |
| 4. **M1-A2.5 — player presentation and local camera** | M | A2.1, C2.1 | P1, actor/local lane. LocalRig's saved 47 m / 42° north-up camera follows the controlled body; [`coral_courier.tscn`](../../scenes/prefabs/player_character/coral_courier.tscn) mounts under `PresentationAnchor`; lower-body clips follow velocity relative to facing through `play_layered`, with idle/death; stride matches 5 m/s; presentation never writes motion. **First playable: standalone walking across Brackett from Boot.** |
| 5. **M1-A2.2 — identity, measured codec, baseline and durable replication core** | L | A1.2, A2.1, accepted S11 codec/baseline evidence, accepted S17 composition | P1, replication lane, split codec/admission/state-apply commits. Freeze only the measured codec; current state before input, bounded transfer/journal, stale revisions and subset recovery pass. |
| 6. **M1-A2.3 — local foot prediction and remote interpolation** | M | A2.1, A2.2, A2.5, accepted S03-L, accepted S03-P | P1, local/replication lane. Decision 19 queue and watermark; decision 20 tunable ~100–150 ms extrapolate→hold→blend; normal/adverse correction, history bounds, life/control/collision invalidation and replay side-effect exclusion; S03-R drawable continuity reviewed with remote Coral Courier players. |
| 7. **M1-A2.4 — player lifecycle, safe respawn and match reset** | M | A2.2, C2.1 | P1, Match lane. Three-second respawn at C2.1 anchors through SpawnReservations, bounded blocked search/retry and reset rehydration retain admitted peers with no old work. |
| 8. **M1-C4.1 — HUD shell** | S | A2.2, A2.5 | P1, UI lane. Saved HUD scene reads session, player and lifecycle owners at supported resolutions; B rows add health/ammo/vehicle values from their owners. The minimap is C4.2. |
| 9. **M1-A-GATE — exported multiplayer shell** | L | D1.1, A1.2, A2.3, A2.4, C2.1, C4.1, accepted S08-X | **P1 complete.** Two Windows and two Linux exported processes cover join/admission, walking/prediction in Brackett, respawn/reset, errors and host loss with Steam absent; run the S08 Linux checklist. |
| 10. **M1-A3.2 — production audio buses and voice policy** | M | D1.1, accepted S14 evidence | Parallel audio lane. Default bus levels, category limits, state-driven emitters and clean teardown; listening waits for real assets and settings land in D5. |
| 11. **M1-B1.1 — production vehicle motion, prediction and tuning** | M | A2.3, C2.1, accepted S03-L, accepted S04-P, decision 30 values | P2, vehicle lane. The standalone drive-rule port may start after D1.1. One VehicleMotion step for standalone/host/replay/AI from a decision 30 tuning resource; body envelopes for the three [delivered cars](#55-delivered-asset-inputs) under `PresentationAnchor`; wheel spin/steer presentation from motion state; local car prediction with bounded corrections, including the clean adverse and moving-contact acceptance S04-P left open (0.576 m adverse p95 against 0.5 m); wall/brake/reverse/handbrake cases; a production standalone drive/tuning entry replaces the archived S04 drive scene (decision 5). |
| 12. **M1-B1.2 — VehicleInteraction transaction matrix** | M | B1.1, A2.4, accepted S04-T | **P2 complete**, Match/vehicle lane. Decision 23 host-confirmed entry with ~0.3 s presentation (door hinges, entry sockets), acceptance-only control/camera/HUD transfer and snap-free rejection; <0.5 m/s exit at the authored 1.5 m offset plus clearance; same-tick claims, decision 16 driver death, disconnect coast, reset/resync/destruction and revision fences; parked cars at C2.1 anchors. |
| 12a. **M1-C1.2a — hitscan tracer effect** | S + art | Delivered weapon effects A family, decision 18 | Content track; the first C1.2 item, owned by the weapon-effects lead. The delivered family has muzzle, hit, rocket-trail and explosion scenes but no hitscan tracer, and reusing the continuous rocket trail is not approved. Add a presentation-only saved tracer scene under `scenes/effects/weapon_effects/` on the family's `effect.gd` API, with Blender-sourced draw meshes, documented lifetime and culling bounds, and every-event allocation. Acceptance includes an owner art-review checkpoint of the tracer look from the gameplay camera. |
| 13. **M1-B2.1 — WeaponState and hitscan** | M | A2.3, A2.4, A2.5, C1.2a, accepted S03-L, accepted S12 decisions | P3, combat lane. Pistol/SMG wrappers at `Sockets/WeaponMount` via `select_grip`; held/walk/run/fire/reload clips; queries from the unsmoothed body pose plus authored muzzle offset; decision 18 immediate cosmetic muzzle flash **and hitscan tracer** on the shooter (C1.2a tracer scene), with impact/hit effect and damage only on host confirmation; decision 21 rate/ammo/reload/equip/no-seated-fire, ShotId duplicates and decision 18 verdicts pass normal/adverse tests. |
| 14. **M1-B2.2 — rockets, Health and player death** | M | B2.1, A2.4 | P3, combat/lifecycle lane. Dock Thumper launcher and visible rocket; trail retained after impact through `stop_emission()`/`finished`; decision 21 health/rocket values, capacity/cooldown, impact/expiry, friendly/self damage, death clip, full-loadout respawn and hydration. Pedestrian death joins in C3.2. |
| 15. **M1-C1.1 — district asset lists and first building/prop families** | M | Owner-reported integrated M1-C0 and its per-district asset lists, accepted S01-W | Content track. Do not dispatch from this orchestration before decision 24's owner-run world concept work integrates. Source-linked Blender/GLB families with provenance, collision and reexport/reload identities, replacing greybox types without changing `world_id`s. |
| 16. **M1-C1.2 — character, vehicle, weapon and effect follow-up assets** | L | Delivered handoffs (section 5.5), C1.2a, owner art review | Content track, parallel lanes by family. The hitscan tracer is split out as C1.2a. Car wreck states (consumed by B3.1, owner question 6), the scoped car art pass, more pedestrian silhouettes/palettes, approved VFX tiers. The bus/truck stay out of M1 unless their concepts and envelopes are approved. |
| 17. **M1-C1.3 — road fixture art** | M | Decisions 42–44, greybox road classes in the [greybox handoff](../assets/brackett_greybox.md), accepted S01-W | Content track. Blender-authored signal, street light and common 3/4-way prefab intersection pieces with connectors and sockets; greybox-grade first, production look after M1-C0. |
| 18. **M1-B3.1 — explosions, wrecks and chains** | M | B1.2, B2.2; C1.2 wreck art for final visuals | P3, combat lane. Every committed explosion allocates its own `weapon_effects_a_explosion.tscn` instance; three/12-car outcomes, bounded work, occupied destruction, collision fence, retention, in-flight late join and reset pass off-camera. |
| 19. **M1-B4.1 — combat VFX/audio/HUD feedback** | M | B3.1, C4.1, accepted S14/S15 evidence | **P3 complete**, presentation lane. Every explosion visible, duplicates suppressed by EventId, measured trail bounds at rocket speed, cheaper quality fallback measured, readable weapon/rocket feedback and bounded audio. |
| 20. **RT-01 — Road Generator release hardening and vendor** | M | Decision 40 | Road track. Implemented on `lane/rt-01` (0.9.4, unmodified vendor) and accepted, but **held for the owner's hands-on editor trial**; not on `main`. Its no-bake production breakdown lands with it; until then the [road-tool evaluation record](../spikes/road-tool.md) (its explicit-bake production breakdown is superseded on `main` by decisions 40–44 and this plan's RT rows; RT-01 lands the rewritten record) still shows the superseded proposal. |
| 21. **RT-02 — road preset, identity and revision adapter** | M | RT-01, C2.1 | Road track, world integrator. Five Brackett presets seeded from the greybox's 50 routes, stable road/section/point/junction IDs, source revision ownership, drift rejection and connection validation without a duplicate spline. |
| 22. **RT-03 — live infrastructure generation** | L | RT-02, decision 42, accepted materials | Road track. Addon roads plus project-script sidewalks, curbs and crosswalk markings generate from the saved network in the editor and at level load; collision ownership, seams and bounded edit-to-visible time. |
| 23. **RT-04 — hybrid intersection system** | L + art | RT-02, RT-03, C1.3, decision 44 | Road track. Blender prefab 3/4-way pieces with crosswalk/fixture anchors; procedural fallback for odd angles/widths; turns, clearance and save/reload regression. |
| 24. **RT-05 — load-time derivation and consistency core** | L | RT-02–RT-04, C2.1 | Road track, world integrator. One bounded pass on host and clients publishes traffic, foot, crossing, spawn and minimap datasets with one source/schema revision before admission; disagreement fails `CONTENT_INVALID`. Update the bake-fingerprint wording in the derived-data contracts ([assets](../assets.md), [scene contracts](../scene-structure.md), [API contracts](../api-contracts.md)) to decision 41's load-time derivation. |
| 25. **RT-06 — traffic graph and spawn derivation** | L | RT-05, accepted S09 | Road track. Directed lanes/turns, stable maneuvers, work caps, legal spawn candidates, signal/crossing conflicts, blocked/stuck integration tests. |
| 26. **RT-07 — foot graph, crossings and reservations** | L | RT-05, RT-06, C3.0, decision 32, accepted S10 | Road track. Continuous sidewalk links, marked crossing IDs and conflict sets derived at load and exposed through C3.0's injected navigation interface and finite reservation API, which AI traffic yields to; illegal-road negatives. |
| 27. **RT-08 — traffic signals and street lights** | M + art | RT-04, RT-06, RT-07, C1.3, decision 43 | Road track. Independently configured signalized junctions (a few landmarks first) and road-type light spacing; authoritative signal groups; fixtures placed without Blender in the edit loop. |
| 28. **RT-09 — minimap derivation** | M | RT-05 | Road track. ROAD centre/area data, widths, bounds and seams from the same revision; 3 px/m consumption plus stale, corrupt and cross-dataset negatives. |
| 29. **RT-10 — connected whole-Brackett pilot and greybox road replacement** | L | RT-03–RT-09, C2.1 | Road track, world integrator. All 50 routes/69 junctions and the bridge. Replace the greybox's Blender road/walk strokes: a coordinated `ground_*.blend` revision stops exporting road/walk surfaces while land, coast, fields and the sole flat terrain collider stay; the bridge structure stays Blender-authored. Building `world_id`s unchanged. Edit-time p50/p95, generation/load cost and the C2.1 capacity baseline rerun with road nodes and colliders. |
| 30. **RT-11 — runtime packaging and upgrade gate** | M | RT-10, accepted S08-X export tooling | Road track. Windows/Linux clean import and Boot; packages contain the runtime addon and road dependencies but no GUT/test/development content; re-pin repeats the regressions. |
| 31. **M1-C3.1 — traffic controller and car population** | M | B1.2, RT-06, C3.0, accepted S09, accepted S17, owner question 1 | P4, population lane. 24 traffic/32 total cap placed per the population decision; lanes/turns, decision 32 yielding to C3.0's crossing reservations, obstacle/wreck recovery, abandoned cars parked and bounded unseen replenishment pass seeded runs. |
| 32. **M1-C3.2 — pedestrian world integration and population** | M | C3.0, B2.2, RT-07, accepted S17, owner question 1 | P4, population lane. Bind C3.0's core to RT-07's load-time foot/crossing graphs, ActorMotion bodies and the [Off-Shift Worker](../assets/pedestrian_civilian_first.md) presentation with palette variety and stride-matched clips; 64 cap placed per the population decision, flee from real threats, damage/death/16 retention and bounded unseen replenishment; C3.0's behavior thresholds still pass in the island and the total is tracked through D3.0. |
| 33. **M1-C3.3 — population replication and capacity profile** | L | C3.1, C3.2, accepted S11, accepted S17 | P4, replication integrator. Full current join, lifecycle reliability incl. spawn/despawn churn, smoothing, baseline and all four-player bandwidth budgets pass. |
| 34. **M1-C4.2 — road minimap** | M | C4.1, RT-09 | **P4 complete**, UI lane. Player-centred minimap window over the whole-island ROAD data with the controlled marker, rebind and late join; settle S06 size/look through the UI iteration. |
| 35. **M1-C2.2 — replace greybox districts with production art** | L | C2.1, C1.1, RT-10 | Content track, sole world integrator. District by district, swap greybox types for accepted families keeping placement `world_id`s; seams, clearance, routes, minimap agreement and capacity rerun per district. |
| 36. **M1-D1.2 — complete production validation/CI** | M | D1.1, B4.1, C3.3, C4.2, RT-11 | Tooling lane. Contract/resource/export discovery includes every production path and catches unused/broken scripts without broad suppression. |
| 37. **M1-D2 — integrated playtest and tuning** | L | M1-A-GATE, B4.1, C3.3, C4.2, A3.2, RT-10, accepted S04-T | Integration/owner review. Walk/aim/shoot/drive/transition/chain/explore across the island, menus/focus, audio and readability findings are fixed or explicitly scoped out. |
| 38. **M1-D3 — integrated capacity and adverse delivery** | L | D1.2, D2, D3.0, accepted S08-C, accepted S08-X, accepted S17 | Performance/network lane. Final integrated acceptance after D3.0's ongoing tracking. Named Windows/Linux hardware, host+3 clients together and in four distant areas of the island at full caps/bursts/lifecycle; decision 15 frame targets, decision 22 soft total, memory/bandwidth/recovery and S05 final-body evidence with raw data. |
| 39. **M1-D5 — LocalSettings and settings UI** | S | D1.1; before D4 | Settings/UI lane. Audio volumes/mutes first; defaults, validation, corrupt recovery, live preview, atomic-save failure and restart pass without mutating shared gameplay. |
| 40. **M1-D4 — private review builds** | M | D2, D3, D5, RT-11, accepted S08-X | Release lane. Exact Windows/Linux exports, identity/exclusions, clean launch/input/audio/ENet, retained hashes/results/rollback and VCS delivery; no Steam upload. |
| 41. **M1-GATE — owner review** | — | D4 | Owner accepts the playable Brackett game or records bounded follow-ups/scope changes; district art scope per owner question 4. |

Actor, replication and world integrators agree on APIs before parallel file work; they do
not concurrently edit Boot, Match or world scenes. Do not start A2.2 by copying the S03
fixture: accepted S11 and S17 evidence are hard codec-freeze inputs. Do not start C3
population with dummy road data or a second road layout.

### 5.3 Whole-city scope: population, budgets, world capacity, minimap and spawns

**Scale.** The greybox coast is 1,155 × 620 m with 10.117 km of road centreline across
50 routes, measured by the whole-island benchmark in the
[road-tool evaluation record](../spikes/road-tool.md) (its explicit-bake production breakdown
is superseded on `main` by decisions 40–44 and this plan's RT rows; RT-01 lands the rewritten
record). The fixed 47 m / 42° camera sees
about 58 × 36 m of ground (~2,100 m²) at 1280×800, roughly 0.3% of the island's bounding
rectangle. The arithmetic below is planning inference, not measurement.

**Population placement (owner question 1).** Two policies keep design.md's global caps:

- **(a) Island-wide uniform:** 64 pedestrians and 24 traffic cars spread across the island.
  This averages roughly 0.2 pedestrians and 0.2 traffic cars per screen, depending on how
  much road a view covers; the city reads empty.
- **(b) Relevance-based placement:** the same global caps, but replenishment places entities
  in a ring outside every player's view and inside a tunable radius (e.g. 45–120 m, larger
  for drivers), and recycles entities that are beyond a far radius from every player and
  not occupied, in a chain or otherwise required. With all players together, a 100 m radius
  gives roughly four pedestrians per screen; four separated players share the caps.

**Recommendation: (b).** It keeps one global population (not multiplied per player) and keeps
host authority for every live entity, off camera included; only placement changes. Host
budget: simulation cost scales with live count and per-entity work, not island area, so
S17's full-cap composition (2.069/3.989/5.849 ms median/p95/p99) remains the reference for
decision 22's soft ~4 ms total. New work is bounded recycling/replenishment (S11's
≤10 candidates per job per tick) and distance checks against at most four players.
Replication: keep S11's full replication of every live entity to every admitted client and
no per-client interest management in M1; steady bandwidth (worst 55.16 KiB/s host output
against 256 KiB/s) and the join baseline (~3.2 KiB against 1 MiB) are unchanged by
placement, while spawn/tombstone churn adds reliable lifecycle traffic that C3.3 must
measure. Per-player caps are rejected because they multiply host and bandwidth cost.
If approved, C3.1/C3.2 update design.md's "district-wide" population row and S11's
visibility-ring policy together.

**World capacity.** From the saved scenes (inspection, not runtime measurement), the
greybox has 290 building placements with 293 box collision shapes plus 12 concave ground
colliders (~305 static shapes) in 9 district and 12 ground sectors. S07's last passing
96-block shared-grey-block row expanded to 13,254 nodes and 768 static colliders; its
384-block row (composition implies 52,998 nodes and 3,072 colliders) crashed historically,
and S08-C later loaded current 384 content without reproducing the crash or finding its cause. The greybox is therefore well inside S07's
passing collider envelope, but its 27 building types are larger unique GLBs, and S07 is not
production-art evidence. Under decision 41 the addon's live road nodes remain at runtime: the
naive whole-island road proxy alone measured 3,466 nodes, 331 draw surfaces and 331 trimesh
colliders before sidewalks and intersections. M1-C2.1 records load time, RAM/VRAM, node,
static-collider and draw counts and a 60-capped 42° route frame time for the greybox;
RT-10 repeats them with the connected roads and M1-C2.2 per replaced district.

**Streaming and chunking.** Load the whole island at once; [assets](../assets.md) requires
measured justification for streaming. The existing 12 ground and 9 district sectors give
spatial grouping for culling; road collision ownership stays with RT-03/RT-10, and the
terrain collider remains the sole flat driving surface. No separate capacity spike is
needed now: C2.1's baseline replaces it. Commission a bounded spike only if C2.1, RT-10 or
D3 shows a crash, an over-budget load or frame time, or memory growth.

**Camera and towers (owner question 3).** Glassward offices are 42 m tall (roofs 5 m below
the 47 m camera) and its placed towers reach 68 m, above the camera. Play near downtown will
put roofs at or above the lens; the greybox handoff leaves roof occlusion and camera-follow
to integration, and decision 3 removed the building cutaway.

**Minimap.** At S06's 3 px/m the whole island is about 3,465 × 1,860 px of ROAD data. C4.2
draws a player-centred window from RT-09's single ROAD dataset, drawing only polylines that
intersect it; no separate minimap splines. A full-island map screen is not in M1 scope.

**Spawn anchors.** Player spawns and initial parked cars use authored saved markers from
C2.1, validated through CityData clearance and Match SpawnReservations. Traffic and
pedestrian spawn candidates come from RT-06/RT-07's derived data, never from hand-placed
copies of road data.

### 5.4 Road tool tasks and ownership

The RT rows above follow the decisions 40–44 no-bake production breakdown that RT-01 lands
in the road-tool evaluation record; until then the record on `main` still shows the superseded
explicit-bake proposal, and these rows are the current plan. There is no bake command; roads,
sidewalks, curbs and crosswalks generate live in the editor and at level load under the
decision 42 exception; gameplay data derives at load on host and clients; the addon ships as
a runtime dependency. The critical path is RT-01 → RT-02 → RT-03/RT-04 → RT-05 →
RT-06/RT-07/RT-09 → RT-10. The world integrator owns CityData and is the sole publisher of
road revisions and derived datasets throughout. Traffic (C3.1), pedestrians (C3.2) and the
minimap (C4.2) consume RT-06, RT-07 and RT-09 respectively once their schemas settle; RT-07
exposes its crossings through C3.0's navigation interface and reservation API. Final signal
and light art does not block that schema work. RT-01 is pending the owner's editor trial;
everything after it waits for that trial.

### 5.5 Delivered asset inputs

Each handoff lists its own checks and limits; this table is the integration input for the
actor, vehicle, combat and world rows. [docs/asset-catalogue.md](../asset-catalogue.md) does not
yet list these assets; the first integrating row adds each catalogue entry from its handoff's
reconciliation delta.

| Asset (handoff) | Reusable scenes and resources | Status | Remaining integration → consumer |
| --- | --- | --- | --- |
| Coral Courier player ([handoff](../assets/player_character/README.md)); shared rig `shared_humanoid/1.0.0` ([contract](../assets/shared_humanoid_rig.md)) | `scenes/prefabs/player_character/coral_courier.tscn` with `player_character_visual.gd` (`play_clip`, `play_layered`, `apply_skin`, `select_grip`, `Sockets/WeaponMount`); `art/animations/characters/shared_humanoid/player_v1.tres`, `player_upper_v1.tres`, `player_lower_v1.tres` (24 clips) | Owner approved | Heading/blend timing, stride matching, collision envelope, remote presentation, fire/reload event timing, city readability, device cost → A2.5, A2.3, B2.1, B2.2 |
| Off-Shift Worker pedestrian ([handoff](../assets/pedestrian_civilian_first.md)) | `scenes/prefabs/pedestrian_civilian/pedestrian_worker_a.tscn`; `scripts/presentation/pedestrian_civilian/pedestrian_worker_visual.gd` (`play_clip` idle/walk/run/death, nine-colour `apply_palette`); `art/animations/characters/pedestrian_worker/npc_locomotion_v1.tres` | Independently accepted; owner final art judgement retained | Collision, stride matching, state transitions, crowd variety/readability, crowd cost (S13 throttling), lifecycle/network → C3.2, C1.2 |
| Sable, Latch, Crate cars ([Sable](../assets/car_sable_a.md), [Latch](../assets/car_latch_a.md), [Crate](../assets/car_crate_a.md)) | `scenes/prefabs/city_cars/car_sable_a.tscn` (4.28 m), `car_latch_a.tscn` (3.43 m), `car_crate_a.tscn` (3.68 m); `Sockets/DriverSeat`, `EntryLeft/Right`, `ExitLeft/Right`; `Wheels/Steer*/Spin*`; `Doors/Hinge*` | Reviewed first-pass checkpoint; final art pending | Physics bodies and driver fit, wheel/door controllers, grounded exit clearance, spawn queries, wreck states (none delivered), Forward+ appearance → B1.1, B1.2, B3.1, C1.2 |
| Coral Stub pistol ([handoff](../assets/pistol_coral_stub.md)) | `scenes/prefabs/pistol_coral_stub/pistol_coral_stub.tscn` (`Sockets/Grip`, `Sockets/Muzzle`) | Owner approved | Equipped fit with the Courier grip profile, authoritative muzzle query, fire/ammo, effects, ~12 px readability → B2.1 |
| Wedgewire SMG ([handoff](../assets/smg_wedgewire_a.md)) | `scenes/prefabs/weapons_smg/smg_wedgewire_a.tscn` | Independently reviewed static asset | Equipped fit, gameplay/effects, city readability → B2.1 |
| Dock Thumper launcher and rocket ([handoff](../assets/rocket_launcher_dock_thumper.md)) | `scenes/prefabs/rocket_launcher/dock_thumper_launcher_a.tscn`, `dock_thumper_rocket_a.tscn` (`Sockets/Trail`); preview `tests/assets/weapons/dock_thumper/preview.tscn` | Owner concept approved; one review finding awaits reviewer roundtrip disposition | Hold/aim/fire fit, projectile simulation, trail lifecycle, collision, network → B2.2 |
| Weapon effects A ([handoff](../assets/weapon_effects_a.md)) | `scenes/effects/weapon_effects/weapon_effects_a_muzzle.tscn`, `_hit.tscn`, `_trail.tscn`, `_explosion.tscn` with `effect.gd` (`play`, `is_active`, `finished`, `clear`, `stop_emission`) | Independently accepted | Every-event allocation without a pool cap, EventId deduplication, moving-trail bounds, 12/24-burst cost, readability → B2.1, B2.2, B3.1, B4.1 |
| Brackett greybox ([handoff](../assets/brackett_greybox.md)) | `scenes/world/brackett_greybox/city.tscn` with 12 ground and 9 district sectors and 27 building prefabs; `world_id`s `brackett/district_NN/building_NNNN`; `preview.tscn` is review-only | Technically accepted; owner density/height review pending | Play-world identity, spawn anchors, traversal/clearance, camera vs towers, capacity baseline → C2.1; road replacement → RT-10; district art → C2.2 |

Large-vehicle (bus/truck) concepts are awaiting approval and have no approved envelopes; the
greybox's road accommodation for them is unverified. They are not M1 inputs.

### Current starts

1. **Now:** decision 14's first production work — M1-C3.0 pedestrian core behavior/budget and
   M1-D3.0 host-budget instrumentation — plus M1-A1.2 and M1-C2.1 (P1 shell and play world),
   M1-A2.1 and the B1.1 standalone drive-rule port, M1-A3.2 audio and the C1.2a tracer effect.
   All depend only on integrated A1.1/D1.1, accepted foundations or delivered handoffs.
2. **After the owner's RT-01 editor trial:** land RT-01, then RT-02 with the world integrator.
3. **After owner question 1:** dispatch C3.1/C3.2 once RT-06/RT-07 schemas exist; C3.0 does
   not wait for either.
4. **After the owner reports M1-C0 integrated:** C1.1 and later C2.2. Under decision 24,
   concept-dependent art waits for that report; C1.2 items that extend already-approved
   asset concepts (such as car wreck states) and greybox-grade C1.3 fixtures do not.

Decision 28 keeps LocalSettings/settings UI in M1-D5 before D4. Production audio uses
default bus levels until settings land.

## 6. Risk register and owner-review questions

| Risk | Consequence | Mitigation / owner question |
| --- | --- | --- |
| Historical requirements name Steam/Deck and rejected controls/effect cap | Teams implement or gate against superseded scope | Existing scope decisions settle ENet-only desktop M1; decision 17's GodotSteam removal is complete. Treat older wording as historical. |
| Prediction against CharacterBody contacts is approximate | Visible corrections, divergent foot/car behavior or replay side effects | S03-L precedes S03-P/S04-P; production ports their shared-rule evidence, keeps revision fences and snaps/resyncs on overflow. No historical-world rollback claim. |
| Confirmed foot→car transfer has multiple owners | Rejected claims or revision changes leave camera/HUD/control on the wrong body | Decision 23 transfers ownership only on host acceptance after a short presentation; rejection cannot snap. S04-T's predicted machinery remains a documented later option. |
| Vehicle handling remains subjective | B1 foundations may be rebuilt after integration | Decision 30 ratifies the owner-tested handbrake-fixed values as playtest-tunable B1.1 starting handling; B1.1's production drive/tuning entry keeps owner re-tests cheap. |
| Initial hitscan policy needs production acceptance | High-latency disagreement or exploit surface | Decision 18 starts with host-current-time verdicts, forgiving hit shapes and view-tick-ready intents; add bounded host-only rewind later only if playtests require it. |
| “Every explosion visible” has no accepted quality-degradation rule | 12/24 effects may violate frame budget or produce unreadable output | S15 measures authored full/cheap variants. **Owner:** confirm reducing particles/lighting while retaining one visible effect per explosion is allowed. |
| Production art differs greatly from grey-block evidence | Memory, draw and animation costs arrive late | C2.1 records the whole-island greybox baseline; repeat the capped capacity checks as RT-10 and each C2.2 district land, and reforecast art from the delivered tracks' actual throughput. |
| Whole-island city exceeds an engine or desktop limit | Crash, long load or missed frame target at production scale | Greybox static colliders (~305) sit inside S07's passing 96-block envelope by inspection; the live road addon adds runtime nodes (decision 41). C2.1, RT-10 and D3 measure; commission a bounded spike only on a measured problem. |
| Uniform island-wide population reads as an empty city | The playable slice feels lifeless despite full caps | Owner question 1 recommends relevance-based placement under unchanged global caps and full replication. |
| Downtown towers rise above the fixed 47 m camera | Roofs at or above the lens hide players near Glassward | Owner question 3; first spawns stay outside Glassward until it is decided. |
| Pre-1.0 road addon is a runtime dependency (decision 41) | Upgrade breakage or load-time cost in shipped builds | RT-01 pins an exact release; RT-05 owns one bounded load-time derivation with host/client agreement; RT-11 gates packaging and re-pins. |
| Windows Blender output differs from accepted Linux output | Source/export checks fail after production art starts | S01-W is a hard C1/S13 input; select byte or semantic comparison before asset production. |
| AI spikes may meet correctness but threaten the soft ~4 ms total host p95 target | Integrated host misses its tracked simulation target | Decision 14 starts C3.0 (pedestrian behavior/budget) and D3.0 (host-budget tracking) first; decision 22 keeps subsystem timings as reports only; D3.0 checks the total as each simulation row lands and at every checkpoint, optimizing the largest contributor, pedestrians first. Population counts remain tunable. |
| Full population codec misses bandwidth/join targets | Late replication rewrite | Accepted S11 baseline/codec evidence is a hard A2.2 dependency, reinforced but never replaced by S17. Retain replaceable motion, per-entity refresh and immutable durable ownership. |
| Foundation validation remains red or incomplete | Production lanes cannot make honest pass claims | P0-TOOLING must make the canonical check green and discover every Python test before D1.1. |
| GUT or its editor plugin conflicts with pinned dev engine/addons | CI instability or exported test code | D1.1 pins and proves headless CLI on both OSes, keeps plugin disabled at runtime and verifies export exclusion. No broad warning suppression. |
| Shared scenes become parallel merge hotspots | Lost authored placement/identity or accidental multiple writers | Assign one Boot/Match integrator and one world (CityData and road revision) integrator; decision 35 makes the orchestrator the integration owner pending confirmation. Parallel lanes contribute saved prefabs/public APIs and hand off for placement. |
| Real project export behavior differs from stripped spike exports | Autoload/native-extension or Linux failures arrive at A-GATE | S08-X is a hard Boot/gate/release input and records GodotSteam removal, continued package rejection, templates and both target launches. |
| Linux release diagnostics or dev-engine regressions recur | One target cannot pass clean export | S08-X runs Linux early; retain exact logs and escalate an engine-pin decision rather than suppress diagnostics. |
| S02 cutaway removal breaks retained S07 environment scenes | Historical: rebased fixtures had missing scripts/shaders | Resolved for capacity guidance by S08-C's no-cutaway reruns; S07 scenes are now archived reference under decision 39. |
| The 384-block crash or unsafe uncapped method is reused | Engine/device failure or unsupported city-size inference | S08-C bounds the crash and establishes capped GPU measurement; C2.1, RT-10, C2.2 and D3 use only capped runs. |
| Driver-death lifecycle is implemented inconsistently | Seat/control or abandoned-car cleanup diverges | Decision 16 releases the seat, neutralizes controls, coasts the surviving car and then applies abandoned-car cleanup/replenishment. |
| No Deck acceptance in M1 | Later handheld work may require renderer/input/UI changes | Keep 1280×800 and controller-friendly composition in design, but label it unverified. Deck becomes a separately planned post-M1 target. |
| Schedule pressure encourages making large tasks monolithic | Review and regression gaps | Split every L row at its named owner seams before dispatch; gate integration on public-API tests rather than completion prose. |

The audit's five [owner questions](../reviews/p0-readiness-audit-2026-10-08.md#5-owner-questions)
are now resolved or reassigned:

1. **Decisions 14/27:** P0 waited only for the integrated S17 quiet record and refreshed gate
   packet, then passed on 9 October 2026. Earlier all-foundation dependency wording is historical;
   named consumer edges remain M1 requirements.
2. **Decision 15:** M1 targets capped 60 FPS with p95 <= 16.7 ms and p99 <= 20 ms on
   named Windows and Linux hardware, tunable during implementation.
3. **Decision 16:** a surviving dead driver's car releases its seat, neutralizes controls,
   coasts and becomes an abandoned parked car under existing cleanup/replenishment.
4. **Decision 17, executed:** GodotSteam is removed from the ENet-only M1 project;
   S08-X keeps rejecting accidental package reintroduction.
5. **Decisions 13–14:** only S17 was rerun quietly, and its integrated record plus the
   refreshed packet complete the P0 inputs. M1-D3 still owns final production acceptance.

Remaining production reviews are assigned to their consumers rather than P0 prerequisites:

6. Ratify final vehicle body dimensions before B1.1 freezes them; decision 30 settled the
   starting drive tuning.
7. The production art quality bar and district asset lists now come from the owner-run
   M1-C0 work (decision 24); they gate C1.1/C2.2, not the playable slice.
8. Validate Windows/Linux desktop budgets on named available hardware while Deck remains
   explicitly untested.
9. **Decision 31, executed:** pinned test-only GUT landed with M1-D1.1.

The packet's still-open choices (VFX degradation tiers, first-pass audio caps and the safe
capped GPU wording) are presented when B4.1, A3.2 and D3 respectively reach them.

### 6.1 Owner questions from the whole-city replan

Each question names its consumer and a recommendation; none blocks P1.

**Owner answers (10 October 2026):** (1) relevance-based population placement around the
players; (2) orchestrator integration ownership stands (decision 35/45); (3) keep the modeled
Glassward tower heights and judge occlusion in play; (4) M1-GATE reviews the game with whatever
districts the greybox update has replaced, full district art does not gate M1; (5) spread player
spawn markers across the whole island for now, moving away from fixed markers later; (6) wreck
variants of the three cars are commissioned ([vehicle_wrecks](../assets/vehicle_wrecks.md)). The
greybox is a layout guide: the update may shift, merge or split footprints. The recommendations
below are kept for context.

1. **Population placement (C3.1/C3.2).** Island-wide uniform versus relevance-based
   placement under the same global 64-pedestrian/32-car caps (section 5.3).
   **Recommendation:** relevance-based placement with full replication and host authority
   for every live entity; update design.md's population row when approved.
2. **Integration ownership (all integrator rows).** Decision 35 assigns gameplay
   integration/production to the orchestrator, replacing the parallel-art record's
   "another person". **Recommendation:** confirm, with the orchestrator assigning one
   Boot/Match and one world integrator lane.
3. **Downtown towers and the fixed camera (C2.1/A2.5).** Glassward towers reach 68 m
   against the 47 m camera. Options: (a) lower greybox tower heights below the camera,
   (b) a narrow presentation-only fade of geometry above the player near the lens,
   (c) keep heights and accept occlusion. **Recommendation:** keep first spawns outside
   Glassward, playtest P1, then choose; (b) is the likely answer if occlusion hurts play.
4. **M1-GATE content scope (C2.2/GATE).** **Recommendation:** M1-GATE reviews the playable
   game in the Brackett greybox with whatever production districts C2.2 has replaced by
   then; full district art continues as its own track and does not gate M1.
5. **Player spawn area (C2.1/A2.4).** **Recommendation:** one authored spawn cluster in the
   low-rise Signal Row / Ironreach area selected in Stage 2, so players meet quickly;
   spread anchors across districts after the first playtest.
6. **Car wreck art (C1.2/B3.1).** No delivered car has a wreck state.
   **Recommendation:** commission Blender wreck variants of the three cars from the
   vehicle lead now; B3.1 implements the wreck lifecycle in parallel and swaps in the
   variants when they land.

## 7. Historical suggested task-record reconciliation

The bullets below preserve this plan's original 8 October reconciliation proposal. They are
historical: current `TODO.md`, task requirements and owner decisions 13–25 supersede them.

- **P0-GATE:** record the owner's answer on restoring S02/prediction and audit-derived
  dependencies; add P0-TOOLING, S03-L, S08-X, S08-C, S01-W, S03-P, S04-P, S04-T and
  S17 with the hard consumers listed above.
- **M1-A1/A-GATE:** ENet and standalone only for M1; prove the backend-neutral seam,
  but move real Steam gameplay/install criteria to a later milestone.
- **M1-A2:** explicitly require local foot prediction with world-relative WASD and
  mouse-facing, plus authoritative correction/replay side-effect fences.
- **M1-B1:** explicitly require local car prediction, stopped-only exit below 0.5 m/s,
  no firing from cars and coast-on-disconnect; leave driver-death stopping pending the
  separate owner answer.
- **M1-B3/B4:** every committed explosion receives a visible effect; quality may
  degrade under measured load, but dropping effects is not an accepted fallback.
- **M1-D3/D4:** M1 target exports are Windows and Linux desktop. Remove Deck and
  Steam from M1 acceptance and retain them as later target/transport work.
- **S07/C2:** use the environment cost-versus-block envelope as city-planning guidance,
  not a population/network/capacity gate; require S08-C before the full district and
  use only capped GPU measurements on this machine.

Suggested TODO refinement: keep the existing M1-A..D outcome bullets concise and
link this plan for the ordered child tasks and acceptance checks rather than copying
this table into `TODO.md`.
