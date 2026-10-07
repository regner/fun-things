# Ownership and simulation architecture

P0-02 draft, 7 October 2026. Owner: Codex. Effort cap: one focused documentation
session. These are proposed implementation contracts, not implemented systems or
measured results. The checkout contains an isolated
[S03 session proof](spikes/s03.md), with no production gameplay. The [ratified brief](design.md)
owns scope and gameplay policy. Spikes refine these drafts and P0-GATE settles them
before M1. Changing ratified product policy still requires a recorded product decision.

Read this with [scene structure](scene-structure.md), [API contracts](api-contracts.md),
[development](development.md), [assets](assets.md), and [multiplayer](multiplayer.md).
The ownership table here is canonical; API shapes and provisional limits live in
the API contract, and authored paths/placement live in the scene contract.

## Boundaries and lifetime

Use one authoritative listen server for 1–4 players, including the host, or a
standalone match with the same rules. Each process has one local player. Clients
submit commands; the host owns outcomes. A player-host remains trusted to run the
simulation honestly. A host loss ends the match; lobby owner changes do not migrate it.

Boot owns process-lifetime SessionService, LocalSettings and the optional platform
adapter as child nodes. Start with no project autoloads. Boot stays alive while its
View changes between menus and Match. A session selects ENet or Steam before
connecting and keeps it until closing finishes. Standalone uses the same match
entry points without a network peer, Steam initialization or a fake remote connection.

Match owns its CityRoot, dynamic entities, gameplay definitions, replication state
and local rig. All match state is discarded on leave. Resource definitions are
immutable shared tuning, not mutable player state. LocalSettings alone persists
audio preferences. Do not introduce inventory, persistence, store or streaming
managers for features outside M1.

## State and rule owners

Names below identify responsibilities and proposed components, not a requirement
for a separate class per row. Keep small related responsibilities on their owning
scene until separation helps. Each field has one simulation writer and one network
writer: Replication publishes the owner's committed state; it does not recompute rules.

| State or rule | Sole owner / writer | Consumers and replication |
| --- | --- | --- |
| Connection attempt, selected provider, operation ID, phase, participant roster and peer mapping | SessionService | Menu/Match observe; session control messages publish roster/admission |
| Native peer, provider callbacks and capability/connection facts | ENetTransport or SteamTransport | SessionService only; no native handles in gameplay |
| Steam availability, account/lobby bindings, invitations and launch join requests | SteamPlatform | SessionService receives opaque join targets; lobby membership cannot admit input |
| Audio levels/mutes, settings schema and save status | LocalSettings | Local audio/UI consume; never replicated |
| Match revision, fixed tick, entity ID/generation and EventId allocation, reset and teardown orchestration | Match | Replication publishes reliable lifecycle; all gameplay validates the revision |
| Authored sector/prefab transforms, spawn/route anchors, stable world IDs | Saved city/sector scenes, edited by the world integrator | CityData registers immutable references; simulation never rewrites placement |
| Road/sidewalk connectivity, shared spawn/exit clearance query and derived navigation/map bake revision | CityData resource/query code and its editor bake process | Host route/spawn/exit queries and local minimap read; content handshake checks identity |
| Population slots, replenishment and initial dynamic spawn descriptors | Population under Match | Creates entities through Match; cap accounting includes occupied cars |
| Spawn reservations shared across players and population | Match's SpawnReservations | Lifecycle/Population reserve atomically and release on completion/cancellation |
| Player life/respawn deadline, controlled entity and life revision | PlayerLifecycle under Match | Coordinates components before publication; HUD/input/Replication read |
| On-foot pose, velocity, facing and movement telemetry | ActorMotion | Authoritative simulation or permitted local prediction; movement snapshots only |
| Vehicle pose, velocity, handling/contact telemetry and stopping policy | VehicleMotion | Same command interface for AI/player; S04 chooses body and permitted prediction |
| Seat occupant, foot/car control transfer, command rebind and control revision | VehicleInteraction under Match | Coordinates player/vehicle state atomically; reliable seat/control transitions; resync changes revision without reseating |
| Pedestrian behavior and traffic route/blocked/stuck state | Population's AI controllers | Emit actor/vehicle commands; do not write movement or health |
| Selected weapon, magazine, reload/cooldown deadlines, equipment revision and shot allocation | WeaponState on actor | Validates fire/equip/reload; reliable equipment updates and launch events |
| Health value, damage deduplication and health revision | Health on damageable actor/vehicle | DamageResolver submits validated damage; life owners consume lethal outcome |
| One-time ShotId acceptance, hitscan/projectile hit rules, friendly/self damage and damage attribution | DamageResolver under Match | One resolution job per committed shot; host physics queries only; projectiles complete that job, clients cannot report damage |
| Explosion queue, chain order/deduplication, vehicle life phase/revision and wreck lifetime | Explosions under Match | Coordinates seat/health/lifecycle; reliable state plus live presentation events |
| Active gameplay projectile trajectory, contact and expiry | Projectile simulation under Match | Host spawns/terminates; client flight is cosmetic |
| Pedestrian life phase/revision, dead-NPC retention and removal deadline | Population | Uses lifecycle/health outcomes; reliable removal, no resurrection by movement |
| Committed gameplay collision revision | Match's collision transition coordinator | Owners request changes; publish after physics changes take effect; gate movement |
| Wire validation, durable revision allocation, baseline/delta/snapshot encoding, receipt buffers and delivery watermarks | Replication under Match, with the Boot Session endpoint for admission | Reads owners; replica application installs host state, never derives outcomes |
| Device focus, held local controls, action sequence and device prompts | LocalRig/Input | Produces intent; does not decide seat ownership, ammo or damage |
| Predicted motion/history, if justified | LocalRig prediction with ActorMotion/VehicleMotion shared steps | May affect owned motion only; authoritative correction wins |
| Remote display pose/interpolation and local visual correction | Entity presentation | Writes presentation anchors, never authoritative physics transforms |
| Camera follow, HUD/minimap, audio and VFX instances/deduplication | LocalRig and RuntimeEffects | State/event consumers; bounded cosmetic fallback cannot discard damage |

Respawn resets health through Health and equipment through WeaponState; it does not
create competing writers. Seat/control changes similarly call owned components
within one transition. Replica application is the only client installer of durable
authoritative state; prediction cannot touch life, seats, health or equipment.
Representation-only calculations, such as wheel animation, do not become gameplay state.

## Command, simulation and presentation flow

Local device input, host AI and admitted remote input all reach the same typed command
validator and motion/interaction APIs. Remote identity comes from the RPC sender
mapping, never from a claimed participant field. The host's local path receives
an explicit trusted context and still passes gameplay validation. Standalone uses
that same local path. AI receives an explicit host-owned controller context.

Match owns fixed-step ordering; choose explicit callbacks/priorities during the
spikes rather than relying on scene sibling order:

1. Commit completed collision transitions and lifecycle work; neutralize commands
   invalidated by death, disconnect, seat transfer or reset.
2. Validate and consume bounded command queues. Produce AI intent and resolve
   discrete actions in deterministic host acceptance order.
3. Step actor/vehicle motion once at the fixed physics rate; resolve firing,
   projectile contacts and the bounded damage/chain workload. A terminal transition
   prevents further commands from the affected life/control revision that tick.
4. Finish coherent component/lifecycle changes and capture committed state and
   command acknowledgements. Collision-dependent publication waits for its fence.
5. Publish durable changes and replaceable movement. Presentation consumes the
   committed state/events independently of the simulation schedule.

The host never runs extra physics time to drain queued client input. AI uses the
same motion commands as players. One controller supplies a vehicle at a time:
traffic AI, admitted driver or neutral/stopping control. Ownership is configured
on the entity and children before entering the tree; `_ready` on a replica cannot
spawn, damage, replenish or start authoritative timers.

Start with authoritative motion and remote interpolation. S03-R and S04 independently
decide whether foot/car prediction is necessary. If introduced, replay only the
shared permitted motion step. Suppress damage, seats, firing, population changes
and duplicate sounds/effects. Clear prediction when match/life/control/collision
state invalidates its history; historical collision rollback is outside M1.

## Coherent lifecycle transitions

PlayerLifecycle owns the three-second respawn policy from the brief and the safe
spawn process defined in [API contracts](api-contracts.md#spawning-and-lifecycle).
Health reports lethal damage; PlayerLifecycle commits death, command cancellation,
seat release, presentation and respawn deadline before notifying observers.

VehicleInteraction resolves entry/exit claims centrally. A successful transfer
updates seat occupant, controlled entity, foot-body collision/visibility and control
revision together. A blocked exit changes none of them. A surviving abandoned car
uses VehicleMotion's stopping policy and remains parked; traffic AI does not resume.

Explosions coordinates vehicle destruction: mark destroyed once, kill any driver,
clear the seat, neutralize control, install wreck/health/collision state, then publish
the committed transition. A collision fence can defer publication; it cannot allow
another explosion or seat claim while the vehicle is terminal. Queue limits bound
work, while S05 must prove all accepted chain outcomes complete even off-camera.

Match reset keeps admitted participants and the selected transport. It increments
match revision, closes input, cancels pending admissions/actions/timers, neutralizes
drivers, removes dynamic entities/projectiles and transient effects/history, and
restores initial dynamic spawn descriptors around the unchanged authored city.
Population and player owners restore their state; Replication hands off a new
baseline using the admission protocol before reopening each participant's input.
Slow clients are removed on timeout without pausing the host. Reset does not rewind
ticks or reuse event IDs within the session. No partial reset signal escapes.

Resynchronization preserves an existing participant's player, life, equipment,
health and seat while the host continues normal gameplay. It closes command
admission and asks VehicleInteraction to rebind commands with a fresh control
revision before baseline capture, then reopens after the current handoff. Initial
join alone creates a provisional player; failed/canceled admission removes that
player and its work/reservations. The API draft defines separate INITIAL, RESYNC
and RESET preparation/rollback around the shared bounded transfer protocol.

Teardown first closes command/admission producers, invalidates async work, releases
seats/reservations and clears effects/history, then removes Match and closes
transport/lobby resources. SessionService returns to idle only after local cleanup
is complete; a late native callback can only clean up its obsolete resources.

## Validation and remaining decisions

The [API acceptance matrix](api-contracts.md#contract-tests) names observable outcomes
and proof owners. [S03's ledger](spikes/s03.md) distinguishes its executable minimum
from the remaining production acceptance cases.
S01 validates source/prefab identities; S02 settles foot/camera/collision dimensions;
[S03](spikes/s03.md) proves the tiny session/baseline/command boundary with ENet
and a correlated fake replacement; it does not productionize these components.
S03-S proves the real Steam adapter and callback correlation; S03-R/S04 settle
responsiveness and simulation bodies; S05 settles combat/chain work and collision;
S06 settles topology representation/bakes; S07 owns map/content-capacity/culling
and diagnostic decisions; S08 owns exact export/input evidence.

Keep pending choices in those tasks, with resulting decisions linked back here.
Do not turn a spike into a production subsystem without the P0-GATE review. Any new
replicated field must be assigned an owner here and a wire/lifecycle/test contract
before implementation. External SDK types stay confined to the adapters.

S03 retains the listen-server topology and single writers. Session owns native-peer
mapping/admission; Match owns provisional lives and command bindings; Replication
owns baseline/journal/handoff and movement application. Sequence exhaustion uses
reliable resync plus a fresh host control revision, retaining the injured player's
entity and health. Split movement uses per-entity receipt watermarks and periodic
refresh of every relevant entity, including unchanged ones: ordered delivery across
different subsets can discard an entire older subset packet. Full life/seat/collision,
capacity and abuse acceptance remain M1 work.

Independent Godot-focused advisor review, 7 October 2026: the reviewer identified
gaps in held-sequence recovery, initial-admission versus resync preparation/rollback,
and duplicate ShotId acceptance. The follow-up corrects all three and adds acceptance
cases; the reviewer confirmed their resolution. Its final wording correction now
distinguishes the durable journal from fresh motion snapshots. At that review,
snapshot reordering and passive replica-body/physics-phase details remained S03/S04 proof work;
the current supplement below links the subsequent result and remaining owners.
The review used official stable Godot documentation; it did not test the pinned
development engine or run gameplay. P0-02 completes reviewed drafts, not those proofs.

Current supplement after S03 acceptance: the advisor paragraph above records the
P0-02 review's historical pending work. The subsequent
[S03 native reordering/loss experiment](spikes/s03.md#experiment-and-observations)
settled the minimum subset-refresh decision: per-entity freshness plus repeated
refresh of unchanged relevant entities recovers the tested ordered-stream loss.
It does not prove production codecs, capacity or adverse-profile convergence;
those remain M1-A2 implementation and M1-D3 acceptance. Passive replica-body and
physics-phase pose capture remain S04 decisions, followed by M1-B1/D3 validation.

Remaining acceptance has active owners in [TODO](../TODO.md) and the
[API matrix](api-contracts.md#contract-tests). M1-A1/M1-A-GATE own full admission,
cancel/error/retry and shell cleanup; S03-S proves native Steam correlation/drain
and transport, S08 exact target/export compatibility. S03-R/S04 decide foot/car
response; M1-A2/B1 implement it. M1-A2 owns the Match reset coordinator, M1-B3
adds combat/seats/rockets/chains/wreck cleanup, M1-C3 adds population, and M1-D3
validates reset while driving/firing/joining with retained peers and unchanged
placement. S04 specifies the seat matrix; M1-B1 owns its full implementation and
M1-D3 adverse races. M1-A2/B2/B3/C3 implement lifecycle; M1-D3 verifies collision
fences, tombstones/future-state buffers, reliable actions, floods/host stalls and
capacity. S05 owns bounded 12-car chain feasibility despite eight cosmetic slots;
M1-B3 productionizes chains and M1-D3 owns sustained load.

Current S02/S07 supplement, 7 October 2026: the
[reviewed S02 desktop fixture](spikes/s02.md#reviewed-desktop-handoff) and
[source handoff](assets/s02_kit.md) support bounded standalone foot/collision/query
and actual camera evidence. The 47 m/42° desktop camera is provisional, with the
historical 50° comparison retained. Human feel/latency, physical-key Alt-Tab,
moving-camera/roof/held-weapon readability and Deck cases remain unproved; current
native focus revalidation is incomplete, not closed by historical passes. Its fixed
engine-step motion is not a proven prediction replay contract; S03-R owns that proof.

[S07's accepted preparation](spikes/s07.md) is the sole map/content-capacity,
culling and diagnostic/organization evidence owner. It separates layout extent,
density, unique variety/residency, active simulation and player views; representative
S04/S06/S05 fixtures must precede actual measurements. Research is preparation only:
no measured capacity, universal map maximum, streaming implementation, renderer or
engine decision is selected. Render visibility, simulation scheduling, network
relevance and resource residency remain distinct; culling cannot remove required
authoritative outcomes. S06 owns topology, S08 exact exports/input, and M1-D3 sustained
integrated target acceptance. Six-block M1 and LCD/OLED native 1280×800/60 FPS remain
unchanged. S08 and M1-D4 retain physical Deck/exports and private Steam delivery gates.
All M1 work still follows P0-GATE; none of these tasks is closed by this supplement.
