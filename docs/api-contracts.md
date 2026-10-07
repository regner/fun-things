# Session, gameplay and presentation API contracts

P0-02 draft, 7 October 2026. Owner: Codex. Signatures below are contract notation,
not complete production classes. The isolated [S03 proof](spikes/s03.md) implements
a narrow executable subset of these boundaries. Implement records as typed local values
and explicitly validated primitive wire shapes when their spike needs them. No
generic RPC framework, service locator or abstraction over every engine call is
required. [Architecture](architecture.md) assigns state owners;
[scene structure](scene-structure.md) assigns paths and authored identity.

Product rules come from [the ratified brief](design.md). Values labeled provisional
are experiment defaults, not measured transport limits or approved combat tuning.
S03 settled only its minimum subset; S03-S/S03-R/S04/S05/S07/S08 refine remaining
limits, and P0-GATE records the settled contract before production acceptance. Contract
changes update these documents and acceptance cases together.

## Common types, identity and compatibility

| Type / field | Shape, units and scope |
| --- | --- |
| `OperationId` | Positive local 64-bit integer, monotonically allocated by SessionService; never reused during the process; not a network identity |
| `SessionId` | Host-created opaque 128-bit random value encoded as 32 lowercase hex characters; fresh for every host/standalone match session |
| `ParticipantId` | Positive host-allocated 64-bit integer, unique within SessionId; reconnect gets a fresh ID, including the same Steam account |
| `MatchRevision` | Positive integer, initially 1, incremented on reset; reject commands/events/baselines from older revisions |
| `EntityRef` | `{id: positive int, generation: positive int}` scoped to SessionId; Match increments generation if reusing an ID; reset never recreates an old ref |
| `WorldId`, `DefinitionId` | Explicit namespaced strings, at most 128 UTF-8 bytes; saved world identity and immutable gameplay/asset identity are separate |
| `Tick`, `Sequence`, `Revision` | Nonnegative 64-bit integers; no wrap during a session; tick never rewinds on reset; sequence acknowledgement is defined below |
| `Context` | `{session_id, match_revision, entity_ref, life_revision, control_revision}`; remote participant is resolved separately from sender |
| `EventId` | `{session_id, match_revision, sequence}` allocated monotonically by Match for gameplay/presentation events |
| `ShotId` | `{session_id, match_revision, shooter_ref: EntityRef, sequence}` allocated by that entity's WeaponState, monotonically across weapon/life changes |
| `Pose` | World position in metres, rotation as normalized quaternion, linear velocity m/s and angular velocity rad/s; exact movement-state extras chosen in S02/S04 |
| `Deadline` | Server tick for gameplay timers; monotonic wall-clock seconds for connection/loading/storage waits; no client clock decides outcomes |
| `Result<T>` | Success with value and optional nonfatal warnings, or normalized `Failure`; synchronous acceptance is separate from async completion |
| `Failure` | `{code, phase, operation_id?, retryable, message_key}`; adapter-only logs may contain provider diagnostics; UI receives no native exception/handle |

Local vectors/quaternions may use Godot value types; wire codecs allow only approved
primitive arrays/fields. Never serialize Node, Resource, RID, Callable, object instance
ID or arbitrary class. Fixed schema decoders reject unexpected types/fields, nonfinite
numbers and excessive sizes before their own allocations/mutation. Bound transport
receipt as well; application checks do not undo allocations made by the engine decoder.
Gameplay uses +Y up, local
-Z forward and radians. Minimap maps world XZ to 2D; S02 chooses its display orientation.

Handshake: `{protocol_version: int, content_id: string, district_id: WorldId,
topology_revision: int, definition_set_id: string}`. Protocol starts at 1; require
exact equality for M1, with no backward-compatible negotiation. Content/definition
IDs are build-time fingerprints of required gameplay resources/bakes, bounded to
128 bytes each; their generation is S06/M1 work. Display version and engine version
are diagnostic metadata, not compatibility. Unknown definitions or world IDs fail
admission with `INCOMPATIBLE`/`CONTENT_INVALID`, never a fallback gameplay definition.

SessionService maps `(active provider operation, native peer ID)` to ParticipantId
only after handshake validation. SteamPlatform maps native account/lobby IDs to opaque
targets/bindings; SteamTransport authenticates its connection identity using the
selected integration. Account identity, lobby membership and reused ENet peer numbers
grant no admission. Remove mappings on disconnect/closing and reject old callbacks.
Revisions reject obsolete state; they are not authentication secrets.

## Session and asynchronous operations

```text
SessionService.host(request: HostRequest) -> Result<OperationId>
SessionService.join(target: JoinTarget) -> Result<OperationId>
SessionService.start_standalone(district_id: WorldId) -> Result<OperationId>
SessionService.cancel(operation_id: OperationId) -> Result<void>
SessionService.leave() -> Result<OperationId>
SessionService.view() -> SessionView
signals: changed(SessionView), completed(OperationId, Result<SessionView>)
```

`HostRequest = {transport: ENET | STEAM, district_id, capacity: 1..4}`. Bind options
(ENet port/interface or Steam friend-lobby settings) are validated adapter-local
configuration. `JoinTarget` is an opaque adapter-owned value with a transport tag
and local handle; raw addresses, lobby/account IDs and native objects never reach
Match/actors. UI boundary calls `ENetTransport.parse_endpoint(address: String,
port: int) -> Result<JoinTarget>` or selects a platform-produced target. Targets
expire when their adapter is reset/closed; joining an expired target returns
`TARGET_EXPIRED`. Port is 1..65535; address text is bounded to 255 UTF-8 bytes and
parsed/normalized by the adapter. No public/LAN discovery is promised.

`SessionView = {phase, operation_id?, transport?, session_id?, local_participant_id?,
capacity, roster, failure?}`. Roster rows are `{participant_id, display_name,
phase: RESERVED | LOADING | SYNCHRONIZING | ADMITTED}`; names are bounded to 64 UTF-8 bytes and are
display data only. Pending connections reserve capacity from handshake onward and
are bounded with the same four-player total, including the host. Provider setup limits
pending native peers accordingly; excess connections fail without entering Match.
SessionService alone writes connection/roster state;
Match owns player entity/control bindings. A canceled reservation is released.

```text
IDLE -> STARTING (host/standalone) or CONNECTING (join)
     -> NEGOTIATING -> LOADING -> SYNCHRONIZING -> ACTIVE
any non-IDLE phase -> CLOSING -> IDLE
```

The host can be ACTIVE while individual joiners are loading/synchronizing. Their
per-participant admission phase lives in the roster and does not move the whole
host back to LOADING. An existing client transitions ACTIVE -> SYNCHRONIZING -> ACTIVE
for RESYNC/RESET, retaining its participant/slot while command admission is closed.
Errors populate the closing/idle view; exactly one completion
is emitted for each accepted operation. Failure return before acceptance allocates
no operation; accepted cancel completes the attempt with `CANCELED` after cleanup.
Repeated cancel/leave is idempotent; leave during closing returns the active close
operation. A second host/join during non-IDLE returns `BUSY`. Retry requires IDLE.

Invalidation precedes releasing a peer/lobby. Correlate callbacks with native request
handles plus OperationId; callbacks without native correlation require serialized
operations and a documented drain strategy. A counter alone cannot disambiguate them.
Late canceled results are closed/left by their adapter, never attached to the new
attempt. Closing has a bounded local deadline; unresponsive native work is detached
with a cleanup-only callback and cannot publish state. If an adapter cannot safely
correlate/drain within that deadline, mark it unavailable until it proves safe reuse
or the process restarts; offline/the other provider remain usable. Do not attach a
new uncorrelated attempt while obsolete native work is pending. S03-S must prove
the integration's actual safe cleanup/drain strategy before reuse.

SteamPlatform emits `join_requested(JoinTarget)`. In IDLE it enters this same join
flow; while connecting/loading the UI offers cancel-and-join, and in ACTIVE it asks
before leaving the match, as required by the brief. Keep at most one pending invite;
a newer target replaces the pending target, never silently leaves the current match.
Settings/menu focus neutralizes local intent without pausing shared simulation.

## Transport and platform adapters

```text
Transport.capabilities() -> TransportCapabilities
Transport.open_host(operation_id, adapter_config) -> Result<void>
Transport.open_client(operation_id, target: JoinTarget) -> Result<void>
Transport.close(operation_id) -> Result<void>
signals to SessionService only:
  peer_ready(operation_id, peer: MultiplayerPeer)
  connected(operation_id, native_binding)
  disconnected(operation_id, native_binding, Failure)
  failed(operation_id, Failure), closed(operation_id)

SteamPlatform.availability() -> PlatformCapabilities
SteamPlatform.create_friend_lobby(operation_id, capacity) -> Result<void>
SteamPlatform.join_lobby(operation_id, target: JoinTarget) -> Result<void>
SteamPlatform.leave_lobby(operation_id) -> Result<void>
signals: lobby_ready(operation_id, JoinTarget), failed(operation_id, Failure),
         join_requested(JoinTarget)
```

These native peer/binding signals are private boundary APIs, not gameplay data.
SessionService is the only consumer and attaches the Godot peer only when endpoints
exist. The transport supplies connectivity; it cannot allocate player entities or
admit input. SteamPlatform owns discovery/lobbies/invites; SteamTransport owns the
actual Steam gameplay peer. Host creation publishes a joinable lobby only when the
host transport/handshake endpoint is ready. A failure cleans up both resources.

`TransportCapabilities = {available, reliable, unreliable_ordered, channel_count,
max_payload_bytes_by_mode, route_diagnostics_available, failure?}`. Limits describe
tested logical-message support; native packet/fragment limits remain adapter-local
evidence. S03 exercised ENet's required modes/channels only at tiny fixture sizes;
S03-S proves Steam support, and M1-D3 validates each provider's production message
budgets. Unsupported capabilities fail with `UNSUPPORTED`, not silent fallback.
`PlatformCapabilities = {available, friend_lobbies, invites, launch_join, failure?}`.
No Steam initialization or native dependency is required by offline/ENet startup.
The absent adapter returns unavailable capabilities/`SERVICE_UNAVAILABLE`. Do not
add real providers for unselected stores. A fake provider exercises this boundary
in tests and cannot certify Steam delivery.

## Admission and replication

Use one explicit RPC writer, Replication, for match lifecycle, component changes
and motion in the first proof. Do not also enable Synchronizer/Spawner writers for
those fields. SessionService owns its separate connection/roster control stream.
Changing to engine replication helpers later requires a documented field-by-field
replacement. Use [Godot high-level RPCs](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html#remote-procedure-calls)
and fixed endpoints; do not build a second routing framework.

Clients accept baseline/durable/movement/event messages only from the authoritative
host peer, and host code rejects client attempts to publish those messages. RPC
annotations and explicit sender checks protect direction as well as payload shape.

All match envelopes carry SessionId and MatchRevision. Baselines use a fresh
`baseline_id` plus cut tick and durable revision. Each durable transition has one
global increasing `durable_revision`, kind and bounded rows; component revisions
remain scoped to their owners. A reliable remove retains a tombstone for EntityRef
until reset/teardown; newer movement cannot recreate it. Bound total entities
created per match revision as specified below; reset clears old tombstones safely
because the revision fence rejects their packets.

The baseline transfer/handoff steps are shared, but their preparation and rollback
depend on `hydration_mode: INITIAL | RESYNC | RESET`. A fresh baseline ID identifies
every hydration attempt, including retries within the same MatchRevision.

1. For INITIAL, validate protocol/content and reserve a participant slot. Client loads CityRoot
   and registers static IDs with authoritative simulation disabled, then sends
   world-ready. Duplicate readiness does not allocate a second entity/baseline.
2. For INITIAL only, reserve a safe spawn and create the provisional authoritative
   player life. For RESYNC, retain the existing player EntityRef, life, health,
   equipment and seat; do not spawn, respawn or restore defaults. Close host command
   admission, neutralize held input, invalidate queued old commands and clear client
   prediction. VehicleInteraction commits a fresh control revision for the player
   binding and controlled body together, preserving seat occupancy. This authorizes
   held sequence 1 under the new binding after handoff. For RESET, use the new
   MatchRevision and state already restored by Match's reset transition, not another
   player creation. At a committed tick, capture an immutable full baseline and start a journal
   after its cut revision. Host continues playing; the baseline is not regenerated
   on every moving-entity update.
3. Send bounded numbered baseline chunks with total bytes/chunks and checksum.
   Client validates the complete payload before installing entities/owned state.
   Install collision/lifecycle, seats/control, health/equipment, then poses; bind
   the one local rig with input still disabled. No historical effects are emitted.
4. On baseline-applied acknowledgement, send the reliable journal through a chosen
   commit revision and a handoff marker on the same reliable state stream. Following
   durable records continue on that stream, preserving order with the marker.
   No unbounded catch-up loop; overflow or deadline aborts this join only.
5. Client applies the journal/collision fences through the marker and acknowledges
   that baseline ID/commit revision. Host opens this participant's command admission,
   emits admitted, and sends fresh movement with required revisions. Client enables
   input after admitted and its matching movement state (or the committed dead/pending
   life state, which permits only lifecycle retry/menu actions). Future dependent movement
   remains gated by reliable state. Old acknowledgements cannot open admission.

RESYNC changes command admission/revision, not gameplay state. Normal host motion,
damage, timers and lifecycle continue during hydration. Durable changes reach the
client through the journal; ordinary motion catches up through fresh, revision-gated
movement snapshots. A later death/control transfer supersedes the binding
captured at the cut. The admitted grant and fresh motion identify the host's current
required durable/life/control revisions, and client input waits for those revisions.
Preserving a seat on resync never restores a driver killed while loading.
Existing-participant RESYNC/RESET hydration gets a fresh maximum 15 s deadline,
not the expired original join deadline. A superseding reset cannot extend an active
hydration's deadline. A pending initial join retains its original total deadline.

Failure/cancel of INITIAL after player creation removes the provisional player,
cancels its respawn/actions/callbacks, releases its seat/spawn/capacity reservations
and publishes removal to peers that saw it. Rollback is idempotent. RESYNC failure
does not create/remove a replacement life; it ends that participant's connection
through ordinary disconnect cleanup. RESET failure removes only the timed-out
participant. Discard the attempt's baseline/journal/acks in every case.

Reset uses this same baseline/handoff process with the new MatchRevision. If reset
interrupts a join, cancel its old baseline/reservation and restart hydration under
the existing operation and total deadline. Repeated resets cannot extend admission
indefinitely. Host/standalone also reach ACTIVE only after their coherent initial
state/rig is ready, without serializing a loopback baseline.

| State shape | Required fields / application contract |
| --- | --- |
| `Baseline` | Header: session/match/baseline IDs, hydration mode, cut tick/durable revision, compatibility, collision revision; player bindings, live entities, retained wreck/dead-NPC rows and active projectile launch/expiry state |
| `PlayerBinding` | ParticipantId, player EntityRef, controlled EntityRef or none, life/control revisions, life phase, respawn deadline or spawn-failure status |
| `EntityState` | EntityRef, kind, definition ID, optional origin WorldId, Pose/motion extras, life phase/revision, health/value/revision if damageable, weapon state/revision if present, driver/control revision if vehicle, retention deadline if terminal |
| `WeaponState` | Selected DefinitionId, equipment revision and per-weapon rows of DefinitionId/magazine/reload phase/end tick/next-fire tick; all three weapon magazine/cooldown states retained across selection |
| `MovementRow` | EntityRef, server tick, life/control/collision dependencies, Pose/motion extras, last consumed-or-superseded input sequence; never writes health, equipment, seat, respawn or destroyed state |
| `DurableTransition` | Durable revision, committed tick, kind, complete changed owner state/revisions; cross-entity seat/destruction/lifecycle rows applied as one transaction |
| `LiveEvent` | EventId, tick, kind, involved EntityRefs, required durable revision, bounded event-specific data; cosmetic launch/hit/blast feedback only |

No persistent world mutation beyond M1's dynamic population/combat state is promised.
If a later feature changes a saved-world gameplay object, add its current state to
Baseline and assign an owner first. Do not assume the default prefab state.

Logical traffic proposal: channel 0 reliable session control/admission; channel 1
reliable match baseline/durable state/action results; channel 2 unreliable-ordered
held input; channel 3 unreliable-ordered movement. Discrete action requests use
channel 0, so baseline transfer cannot order them behind its chunks. Live events
use the reliable match stream with state dependencies. No ordering is assumed
between channels. Both transports must prove four configured channels and these
modes; S03 exercises all four channels with ENet. Steam remains an independent
S03-S requirement; the fixture's tiny JSON baseline/Variant intent and movement
codec is not the production codec or a measured maximum transport limit.

**Split movement decision from S03:** a packet watermark does not imply receipt
of entities omitted from that packet. Apply freshness per EntityRef/control binding;
do not discard another entity's row merely because a newer subset arrived. ENet's
ordered stream can discard an older subset packet before application sees it.
The publisher must revisit every relevant entity, including unchanged ones, within
a provisional 250 ms interval using current complete movement rows. Loss delays
that refresh; it cannot permanently remove the subset from publication. No atomic
full-snapshot assembly is required. Dependence on reliable state remains unchanged.
The S03 proxy reorders A100 behind B101, loses A102, then delivers B103/A104; both
subsets converge without movement changing durable health. Production batching,
capacity bandwidth and adverse-profile recovery still need M1-D3 measurements.

Replica application rejects stale sessions/revisions/generations and duplicate
durable records. Future-dependency motion is bounded and replaced by the newest row
per entity, not appended forever. A collision fence completes only after the applied
shapes are effective in physics; prediction and movement cannot pass it early.
On gap/overflow, close local input and request one bounded RESYNC hydration using
the shared transfer/handoff steps above; on its failure, leave with
`SYNC_TIMEOUT`/`STATE_LIMIT`. The reliable Session endpoint accepts a resync request
containing SessionId/MatchRevision independently of held-input sequence validation.
Resolve the existing participant from its sender mapping, allow one active request
and rate-limit retries; duplicates reuse the pending hydration rather than spawning
another attempt. Host command admission stays closed until the current
handoff is acknowledged. Do not reuse INITIAL's spawn/reservation steps.
Reliable gaps do not invite applying a partial transaction.

## Commands and control transfer

```text
Match.submit_held(source: TrustedCommandSource, context: Context,
                  command: FootCommand | DriveCommand) -> Result<void>
Match.submit_action(source: TrustedCommandSource, action: ActionRequest) -> Result<void>
ActorMotion.step(command: FootCommand, delta_seconds: float, mode: AUTHORITY | REPLAY)
VehicleMotion.step(command: DriveCommand, delta_seconds: float, mode: AUTHORITY | REPLAY)
VehicleInteraction.try_enter(participant_id, player_ref, vehicle_ref, context) -> ActionResult
VehicleInteraction.try_exit(participant_id, context) -> ActionResult
VehicleInteraction.rebind_commands(participant_id) -> Result<Revision>
```

`TrustedCommandSource` is constructed only by host local/AI code or the network
boundary. Capture `multiplayer.get_remote_sender_id()` while handling the RPC and
resolve its admitted participant; never accept a caller-created source over the wire.
Check sender admission, SessionId/MatchRevision, live EntityRef, life/control revision
and controller binding before forwarding. Authority remains with the host even when
a client drives. Delta is the fixed host physics step, never a client value.

`FootCommand = {sequence, client_tick, move: -1..1, turn: -1..1, fire_held: bool}`.
Facing owns aim; there is no unratified independent mouse aim/strafe. `DriveCommand =
{sequence, client_tick, throttle: -1..1, steer: -1..1, brake: 0..1, handbrake: bool}`.
S04 defines reverse/brake handling. Tick is diagnostic/replay ordering within limits,
not permission to rewind host time. AI commands use host ticks through the same rules.

Held sequence starts at 1 for each new entity/control-revision binding and never
resets within that binding. Client tick stays diagnostic; a stalled/out-of-window
sender needs the bounded resynchronization path rather than forcing extra host steps.
Only the host's fresh control revision authorizes sequence 1 again; a baseline
without that rebind cannot reset a held sequence. Reliable action sequence continues
across resync, and queued actions from the old binding are invalidated.
Held input is replaceable. At most three recent frames per message recover loss;
accept only increasing in-window sequences. Each physics tick uses the newest valid
frame available and explicitly supersedes older pending frames. Acknowledgement
advances only after that tick's simulation, through consumed/superseded frames;
receipt alone is never an acknowledgement. Reuse held values until expiry, then
neutralize them. Dropped held frames carry no discrete action. Focus loss/local UI
releases controls immediately locally and sends neutral input; host expiry remains
the fallback. A new life/control revision starts neutral, even before another packet.

`ActionRequest = {context, action_sequence, kind, payload}`. Kinds/payloads: ENTER
`{vehicle_ref}`, EXIT `{}`, EQUIP `{weapon_id}`, RELOAD `{}`, RESET `{}` and
RESPAWN_RETRY `{}`. Player actions
use the live player EntityRef even when the controlled entity is a car; held drive
input uses the car EntityRef and its control revision. RESET validates session/admission
and host privilege, not a live body, so a dead host can reset. RESPAWN_RETRY requires
the current dead/spawn-failed life revision. Other actions validate live life/control/
equipment suitability. Draft M1 policy: weapons cannot fire/reload from a seat;
S04/feel review confirms it before P0-GATE.

`ActionResult = {action_sequence, status: APPLIED | REJECTED, failure?,
durable_revision?}` is emitted after processing, not mere queue admission. A
per-participant action sequence spans life/control changes. Cache recent results;
duplicates return the cached result without another mutation; an older evicted
sequence returns `STALE_SEQUENCE`. Syntactically valid rejected requests consume
their sequence too. Reject sequence jumps outside the bound. Results never install
gameplay state; the reliable transition is the sole state application.

Host acceptance order is `(accepted_tick, participant_id, action_sequence)` for
same-tick actions. The first valid seat claim wins; others get `SEAT_OCCUPIED`.
Entry checks alive/unseated player, available/nonterminal car, range, eligible
speed, authored sockets and clearance before disabling foot-body gameplay. S04
settles range/speed values on VehicleInteraction tuning. Exit tests left/right
authored candidates in a fixed order with the actor clearance query; all blocked
returns `EXIT_BLOCKED` and leaves the entire seat/control state unchanged.

Successful transfers increment control revisions, neutralize previous controllers,
clear affected prediction and commit both player/car rows. Traffic ownership stops
before player controls begin. Death/disconnect releases the seat and neutralizes
controls; surviving car stopping is S04-owned and never resumes AI immediately.

## Spawning and lifecycle

```text
CityData.find_spawn(kind, definition_id, bounded_candidates, reservations) -> Result<SpawnCandidate>
PlayerLifecycle.respawn(participant_id, now_tick) -> Result<EntityRef>
Match.request_reset(source: TrustedCommandSource, action_sequence) -> Result<void>
```

`SpawnCandidate = {world_id, pose, clearance_definition_id}`; CityData supplies
authored candidates. PlayerLifecycle/Population completes its own spawn; Match's
shared SpawnReservations atomically reserves/releases clearance for all entity kinds.
CityData's spawn/clearance query is the single implementation used by these owners
and VehicleInteraction, with shape/mask definitions appropriate to the entity kind.
For players, check the actor's actual S02 collision envelope expanded by a provisional
0.10 m skin, supporting ground/slope, world boundary and overlap against static
collision, live bodies, wrecks and other reservations. Ignore only the replacing
player's disabled old body. Reserve before adding the new body in the same host
step; same-tick requests cannot share clearance. Exit uses this same actor query.
Population/vehicle spawns use their own reviewed envelope, not the player capsule.

Death stops commands, clears seats/reload and starts the brief's three-second
server-tick respawn timer. On its due tick, try at most ten candidates per tick
for up to five seconds (provisional clearance/deadline values). Success restores
full health/default loadout and new life/control revisions before notification.
Failure leaves the player dead, sends `SPAWN_BLOCKED` with a retry UI action, and
does not place an overlapping actor. Retry is a rate-limited reliable player
lifecycle request with its own action sequence, using the same bounded search.
Initial join uses the same search but
fails admission/releases its slot if it cannot spawn; no invisible admitted player.
Population retries are bounded scheduled work, never an unbounded spawn loop.

Reset is host/standalone only and rate limited. It invalidates old life/control
and match state, clears queued actions/held input, shots, damage/chain queues,
reservations and histories, restores dynamic initial state and respawns players.
During rehydration input is closed. A failed safe spawn remains a reported pending
life state or fails initial admission; it never blocks all other participants.

## Weapons, damage and explosions

```text
WeaponState.try_equip(weapon_id: DefinitionId, context, now_tick) -> Result<void>
WeaponState.try_reload(context, now_tick) -> Result<void>
WeaponState.step_fire(fire_held: bool, context, now_tick) -> Result<ShotId?>
DamageResolver.resolve_shot(shot_id, shooter_ref, weapon_definition, launch_pose, now_tick) -> Result<void>
Health.apply_damage(damage: DamageRequest) -> Result<HealthOutcome>
Explosions.enqueue(blast: BlastRequest) -> Result<void>
```

These are host component APIs, never client-reported hits/damage. A fire step without
held fire returns success with no ShotId; rejected held fire cannot emit a shot event.
DamageResolver owns one-time acceptance of a committed WeaponState ShotId into one
resolution job. Duplicate submission, whether the job is active or completed, cannot
allocate another damage EventId, launch another projectile or apply another hit.
Each job retains its original ShotId and its assigned source-event identities;
projectile contact/expiry completes that job instead of resolving the shot anew.
Completed ShotIds remain inadmissible after active health/event deduplication is
released. S05 chooses a bounded retirement mechanism (for example, per-shooter
sequence watermarks with bounded active jobs), including shooter removal/generation
changes; eviction must never make an old shot acceptable again.
Actor/vehicle definitions own max health and movement/collision tuning. Weapon definitions
own `id`, kind, damage, range_m, fire_interval_s, magazine_size/reload_s for pistol/SMG,
and rocket speed_mps/lifetime_s/blast_definition_id/cooldown_s. Damage/blast definitions
own radius_m, obstruction/falloff policy and chain_delay_s. S05/M1-B2 settle exact
values, with weapon distinction required by the brief. WeaponState owns ammo/timers;
DamageResolver owns hit/friendly/self-damage policy. Shared immutable definitions
cannot carry mutable health/ammo or provider types.

Validate equipped/allowed weapon, alive/unseated life, current revisions, muzzle
clearance, ammo/reload/cooldown and gameplay capacity before committing a shot.
An active-rocket limit returns `STATE_LIMIT` without spending cooldown/ammo. Equip
validates the replacement before changing selected state, cancels active reload
without granting ammo, and preserves per-weapon magazines/next-fire deadlines so
switching cannot bypass cooldown. Death/reset cancels reload and held fire. Default
spawn loadout includes all three weapons, full magazines, unlimited reserve and
available rocket cooldown. Already-fired rockets survive weapon replacement.

`DamageRequest = {source_event_id, shot_id?, source_entity_ref?, credited_participant_id?,
target_ref, amount, damage_kind, tick}` is created by DamageResolver. Values must be
finite/nonnegative; `(source_event_id, target_ref)` deduplicates one outcome. Friendly
and self damage are always enabled. Attribution may remain as stable IDs after the
shooter disconnects; it does not give the departed participant control. `HealthOutcome`
contains committed health/revision and lethal flag; the lifecycle owner completes
the terminal transition before observers receive it.

Keep damage deduplication for active source-event jobs only, released after their
bounded target processing completes. DamageResolver/Explosions cannot recreate a
completed EventId, and clients have no damage-submit endpoint. S05 bounds active
jobs and target sets, including any out-of-order due events; do not retain an
unbounded per-health history or retire still-pending damage because a newer event ran.

`BlastRequest = {event_id, source_entity_ref?, shot_id?, origin_m, blast_definition_id,
due_tick}`. Explosions orders pending blasts by `(due_tick, event sequence)` and
marks a destroyed car terminal before scheduling its one blast. Damage to an already
destroyed car cannot schedule another. Active rockets have ShotId, launch tick/pose,
velocity, definition and expiry tick; host impacts/expiry end them once. No M1
lag-compensated historical hitscan/world rollback is implied; host current-state
queries choose hits. S03-R/S04 measure whether that policy meets feel requirements.

S05 must settle damage/chain queue capacity, processing budget, guaranteed completion,
overflow admission policy, obstruction/falloff, chain delay and wreck collision/retention
before P0-GATE. An accepted shot/blast cannot silently lose authoritative outcomes
to a cosmetic cap or queue overflow. Reserved pending-chain capacity/backpressure
must be proved on the 12-car burst before production. This is an explicit unresolved
spike decision, not permission for unbounded queues. Wreck/dead-NPC deadlines and
safe retention-cap cleanup are likewise S05/Population decisions; active chains
and occupied live cars cannot be deleted to satisfy a visual cap.

## City, presentation and settings

```text
CityData.route(kind: FOOT | TRAFFIC, from: WorldId, to: WorldId) -> Result<Route>
CityData.map_data() -> MapData
Presentation.apply_state(state, mode: HYDRATE | LIVE) -> Result<void>
Presentation.consume_event(event: LiveEvent) -> Result<void>
LocalRig.bind(participant_id, player_ref, controlled_ref) -> Result<void>
LocalSettings.load() -> Result<AudioSettings>
LocalSettings.set_audio(bus: MASTER | MUSIC | SFX, linear_gain: float, muted: bool) -> Result<void>
LocalSettings.save() -> Result<void>
```

`Route = {topology_revision, link_ids, world_points_m}`; S06 bounds route size/work
and chooses lane/sidewalk representation. `MapData = {district_id, topology_revision,
bake_fingerprint, world_xz_bounds_m, road_polylines_m}` derives from that same topology.
Missing/stale IDs return `CONTENT_INVALID`/`NO_ROUTE`; AI uses its bounded recovery
policy and never invents a second geometry layout. Pedestrian fleeing and traffic
blocked/junction/stuck recovery durations/work limits are Population/S06-owned
decisions before M1-C3; rendering visibility never suspends their required authority.

HYDRATE installs present state, including wrecks and active rocket flight, without
old muzzle/blast/hit/respawn sounds. LIVE consumes EventId once after required state;
old-match/revision events are dropped. Cache a bounded deduplication window with a
retired sequence floor so an evicted event cannot replay. Events delayed beyond
the live window may be dropped cosmetically; durable state still applies. Prediction
replay cannot emit live events. HUD health/ammo/seat/cooldown comes from owner state,
and camera follows the committed controlled entity. LocalRig rebind is idempotent,
not another rig instance. Effect/audio limits fall back by merging/dropping lower
priority cosmetics; gameplay still runs off-camera and when effects are saturated.

`AudioSettings = {schema_version: 1, master/music/sfx: {linear_gain: 0..1, muted: bool}}`.
Defaults are gain 1 and unmuted. Load validates each field; missing/corrupt fields
recover to defaults with a visible nonfatal `SETTINGS_INVALID` warning. An unknown
schema version recovers the complete default settings with that warning; a missing
file is a normal first-run default. Preview applies
locally immediately; save on committed settings edits. LocalSettings owns versioned
storage at `user://settings.cfg`, writes a temporary file then replaces the previous
file, and keeps the last good file if saving fails. A save failure reports
`STORAGE_FAILED`, retains preview values in memory and permits retry. No settings
are replicated and no Steam cloud dependency is required. Future storage providers
stay behind LocalSettings only when selected. Teardown stops entity loops/effects;
it does not reset saved audio preferences.

## Provisional limits and failure codes

The values below remain provisional. The runtime owner and active proof/acceptance
tasks are separate: S03 evidence covers only its [recorded minimum](spikes/s03.md#experiment-and-observations),
with [explicit omissions](spikes/s03.md#alternatives-limitations-and-resulting-work).
An S03 reference is accepted evidence, never an owner for new work. Spike tasks
settle bounded choices; M1 tasks implement and validate full production contracts.
Keep limits with the owner named here, not an unrelated global constants bag.
Use monotonic deadlines regardless of simulation slowdown. Gameplay seconds convert
to fixed-step deadlines without accepting client elapsed time.

| Limit | Draft value and scope | Owner / proof |
| --- | --- | --- |
| Connection/negotiation | 15 s connection plus 5 s handshake | SessionService / S03 minimum evidence; S03-S native decision; M1-A1/M1-D3 full failures/deadlines |
| World load | 30 s per participant, never pauses host | SessionService/Match / S08 export/content proof; M1-A1/A2/M1-D3 production loading/deadlines |
| Baseline/admission | 1 MiB serialized and decoded baseline; 16 KiB logical chunks; 10 s transfer/apply, 5 s handoff; 60 s total attempt, unaffected by reset/retry | Replication/SessionService / S03 tiny cut/handoff evidence; S03-S transport limits; M1-A1/A2/M1-D3 size/duplicate/overflow/reset acceptance |
| Join journal | 2 MiB serialized or 4096 durable records per join, whichever first; overflow aborts only that admission | Replication / S03 single-health-record evidence; S05 chain decision; M1-A1/B3/M1-D3 general journal/overflow acceptance |
| Closing | 5 s local cleanup; stale native callbacks retain cleanup-only ownership | SessionService/adapters / S03 correlated fake/local cleanup evidence; S03-S native drain proof; M1-A1/M1-D3 bounded/hung cleanup acceptance |
| Simulation / sending | 60 Hz fixed simulation; up to 30 Hz input and 20 Hz movement publication | Match/Replication / S03-R/S04 response decisions, S07 budgets; M1-A2/B1/M1-D3 production rates/load |
| Split motion revisit | Every relevant entity, even unchanged, within 250 ms before delivery loss; freshness tracked per entity/control binding | Replication / S03 subset-refresh evidence; M1-A2 implementation, M1-D3 capacity/adverse-profile proof |
| Held input | 1200 serialized bytes/message; 3 frames/batch; 8 queued frames/participant; sequence at most 120 ahead; 250 ms stale-input expiry | Replication / S03 individual receipt/window/expiry evidence; S03-R/S04 controller decisions; M1-A2/B1/M1-D3 batch/queue/gameplay acceptance |
| Held rate | 60 messages/s with burst 8 per participant; reject excess before queueing | Replication / S03 implemented receipt bucket, not flood proof; M1-D3 flood/host-stall/abuse acceptance |
| Reliable actions | 4096 bytes/message; 16 requests/s, burst 32; 16 queued/participant; process at most 4/participant/tick; result cache 64; sequence at most 64 ahead | Replication / S04 seat contract; M1-A2/B1/B2/B3/C3 action integration; M1-D3 queue/cache/rate/replay acceptance |
| Reset / respawn retry | Reset at most once/5 s; respawn retry once/5 s/participant | Match/PlayerLifecycle / M1-A2 reset coordinator, M1-B3 combat/seats/chains, M1-C3 population, M1-D3 reset acceptance; M1-A2/B2/D3 respawn retry |
| Future state wait | Latest motion row/entity only; up to 256 rows or 256 KiB; 1 s before resync, one resync at a time | Replication / M1-A2/B3 lifecycle/collision implementation, M1-D3 bounded buffer/timeout acceptance |
| Resync requests | At most one active hydration and one request/5 s/participant; same bounded transfer/handoff deadlines | SessionService/Replication / S03 retained-player/fresh-deadline evidence; S04 seated decision; M1-A2/B1/M1-D3 full resync/rate acceptance |
| Live event dedup | 512 IDs with retired floor; event presentation age at most 2 s | Presentation / S05 event/retirement decision; M1-B4 implementation, M1-D3 dedup/age/saturation acceptance |
| Entity tombstones | At most 65536 spawned refs per match revision; refuse further dynamic allocation and report limit, never discard live tombstones | Match/Replication / S07 load budgets; M1-A2/B3/C3 lifecycle implementation, M1-D3 allocation/retention-cap acceptance |
| Spawn | 10 candidates/tick; 0.10 m clearance skin; 5 s retry after due time | PlayerLifecycle/Population / S02/S04/S06 envelopes/query decisions; M1-A2/B2/C3 implementation, M1-D3 clearance/race/deadline acceptance |
| Population/effects | Brief's global 64 pedestrians, 32 live cars, 16 retained wrecks/16 dead NPCs, 16 active rockets; 8 explosion presentations and 64 transient instances/client | Population/Explosions/Presentation / S05 bounded 12-car feasibility, S07 measured budgets; M1-B2/B3/B4/C3 implementation, M1-D3 sustained capacity |

Chunk sizes describe logical messages, not safe UDP datagrams. Account for encoding
and transport overhead in measurements; adapters must verify fragmentation/logical
limits and preserve the brief's bandwidth budgets. S03 settles split-subset refresh;
production codecs and maximum rows/message remain M1-D3 measurements. No normal motion message exceeds
1200 serialized bytes. Reliable lifecycle/event batches are capped at 16 KiB and
split only between complete transactions; larger transactions need an explicit
bounded transfer contract before implementation. Decode chunk count/declared bytes
before allocating; baseline chunk count is at most 128 (allowing framing overhead)
and duplicate indices are ignored after checking identical content. Both phase and
total deadlines apply; whichever expires first ends the attempt. Retain serialized
payload and actual transport-byte measurements separately, including join overhead.

Normalized codes: `BUSY`, `CANCELED`, `TARGET_EXPIRED`, `SERVICE_UNAVAILABLE`,
`UNSUPPORTED`, `CONNECT_FAILED`, `CONNECT_TIMEOUT`, `HANDSHAKE_TIMEOUT`, `FULL`,
`INCOMPATIBLE`, `CONTENT_INVALID`, `LOAD_TIMEOUT`, `SYNC_TIMEOUT`, `HOST_LOST`,
`INVALID_COMMAND`, `NOT_ADMITTED`, `NOT_OWNER`, `STALE_STATE`, `STALE_SEQUENCE`,
`RATE_LIMITED`, `STATE_LIMIT`, `SEAT_OCCUPIED`, `OUT_OF_RANGE`, `VEHICLE_MOVING`,
`EXIT_BLOCKED`, `SPAWN_BLOCKED`, `NO_ROUTE`, `NOT_ALLOWED`, `COOLDOWN`, `NO_AMMO`,
`RELOADING`, `SETTINGS_INVALID`, `STORAGE_FAILED`, `CLEANUP_TIMEOUT`.
Unexpected provider failures normalize to `CONNECT_FAILED` with retained local logs.
Malformed/rate-limited gameplay requests are dropped/rejected before mutation;
M1-D3 must settle and test a bounded repeated-abuse disconnect policy; S03 exercises
bounded held receipt/rate and rejects individual bad requests. Session errors return to idle
after cleanup; component rejection leaves coherent prior state. Retryability is
explicit per occurrence (for example, change endpoint/access before retrying).

## Contract tests

These are required outcomes for executable tests through production APIs. S03's
isolated fixture now covers the minimum session proof; its exact coverage and
deliberate omissions are recorded in [the evidence](spikes/s03.md). The broader
rows below remain production acceptance, including full/incompatible/slow admission,
seated resync, reset, gameplay lifecycle/collision, floods and capacity. P0-03 has
script checks and a bounded runner, integrated with completed S01 asset/resource checks.

| Boundary / evidence and active owners | Independent observable expectation |
| --- | --- |
| Session/provider replacement — S03 minimum evidence; M1-A1/M1-A-GATE full shell, M1-D3 adverse cases | S03 verifies correlated fake/ENet cancel/retry, fresh identities, one placeholder rig and Steam absent in the isolated project. Production host/join/cancel/leave/Standalone and failure/menu flows must complete once and cleanly retry. |
| Real Steam — S03-S/S08 bounded proof; M1-A1/M1-A-GATE/M1-D4 production delivery | Two authorized accounts on separate networks exchange baseline/intent using a real Steam peer; lobby alone cannot pass; native late callback cannot attach to retry. Packaged gameplay/install/invite flows need production acceptance. |
| Admission — S03 tiny baseline/journal/handoff evidence; M1-A1/M1-A-GATE full shell, M1-D3 adverse/capacity | Connected-but-unadmitted input changes no actor; wrong content/full/unreachable/slow join fails boundedly; baseline plus during-load durable changes yields current state before control. S03 proves one health change, not the full journal/overflow suite. |
| Admission rollback — S03 provisional-cancel evidence; M1-A1/A2 full lifecycle, M1-B1/B3/C3 dependent cleanup, M1-D3 races | Cancel/fail after provisional player creation removes it once, cancels respawn/actions and releases seat/spawn/capacity; retry creates exactly one player. S03 has no gameplay timers, seats or spawn clearance. |
| Resync — S03 injured-marker/window/fresh-deadline evidence; S04 seated decision; M1-A2/B1/B2 implementation, M1-D3 acceptance | An injured seated player keeps the same entity, health, equipment and seat; commands stay closed during hydration; a sequence window overflow recovers under a fresh control revision and sequence 1; old frames/actions/acks cannot reopen control. S03 proves entity/health retention and held/ack fences only. |
| Lifecycle ordering — S04 body/seat and S05 destruction decisions; M1-A2/B1/B2/B3/C3 implementation, M1-D3 acceptance | Delayed movement cannot resurrect destroyed/dead entities or undo a seat/reset; required collision applies before dependent movement/prediction; duplicate baseline/ack causes no duplicate entity. S03 has no gameplay collision, tombstones or future-state buffer proof. |
| Input — S03 individual validator/expiry evidence; S03-R/S04 response decisions; M1-A2/B1/B2/C3 gameplay paths, M1-D3 abuse/load | Host local/remote/AI paths obey the same movement constraints; client cannot move another entity; invalid types/NaN/large/jumped sequences produce no mutation; expiry releases held fire/throttle. S03 does not prove real controllers, batching or discrete actions. |
| Split snapshots — S03 native subset-recovery evidence; M1-A2 implementation, M1-D3 capacity/adverse profiles | Different entity subsets recover after actual ordered-stream reordering/loss through repeated refresh; a newer subset cannot advance another entity's application watermark. Tiny fixture recovery is distinct from sustained production bandwidth/convergence. |
| Queue/work bounds — S05 reserved-chain decision; M1-A2/B1/B2/B3/C3 implementation, M1-D3 flood/stall/capacity | Flood/backlog/host stall stays within configured queues and one physics step/tick; acknowledgements cover simulated or explicitly superseded input, not receipt; overflow follows documented recovery. Reliable-action size/rate/cache/sequence limits and repeated-abuse disconnect policy require production proof. |
| Seat race — S04 specifies matrix; M1-B1 implements/full suite, M1-B3 destruction, M1-D3 adverse cases | Two same-tick claims yield one driver; blocked exit preserves seat/control/foot collision; death/disconnect releases controls and surviving car remains parked. S04's bounded seated-resync/body experiment does not close this suite. |
| Safe respawn — S02/S04/S06 envelope/query decisions; M1-A2/B2/C3 implementation, M1-D3 acceptance | Before 3 s no respawn; valid spawn has full health/default loadout; two requests cannot overlap; blocked district fails after a further 5 s of search with retry, without teleporting or freezing the match. |
| Combat — S05 damage/retirement decision; M1-B2/B3 implementation, M1-D3 acceptance | Submit one ShotId twice during its job and again after completion/damage-cache retirement: only one launch/hit/damage outcome; empty/reloading/cooldown/seat cannot fire; equip cannot grant ammo or reset cooldown; rocket survives weapon replacement but dies on reset. |
| Destruction — S05 bounded feasibility; M1-B3 implementation, M1-D3 sustained load | Three-car near/far fixture has known expected outcomes; occupant dies once/seat clears; bounded 12-car burst completes accepted chain outcomes off-camera despite eight visual slots. S05 feasibility is separate from production joining races and sustained capacity acceptance. |
| Hydration/effects — S05 state/event decision; M1-B3/B4 implementation, M1-D3 join/saturation acceptance | Joining after a blast shows current wreck/health and active rockets without historical sounds/blasts; duplicate live event plays once; effect saturation cannot alter health. |
| Reset/teardown — S03 tiny leave/host-loss evidence; M1-A2 reset coordinator, M1-B3 combat/seats/chains, M1-C3 population, M1-D3 full acceptance; M1-A1/M1-A-GATE shell cleanup/reset | Admitted peers remain after host reset; old-match commands/events do nothing; no layout transforms change; callbacks/history/input/loops are cleared on leave and retry. Reset while driving/firing/joining rehydrates new revisions and clears old work; S03 implements no reset. |
| City/asset identity — S01 bounded accepted route; S06 topology decision; M1-C1/C2/C4 production content, M1-D1/D4 checks/exports | Reexport/inheritance/roundtrip preserves placement/import ancestry/IDs; stale bake rejects use; route crosses two-sector seam and shared minimap roads align. S01 acceptance is limited to linked wrappers and wrapper-level variants, not direct imported-child overrides or production art. |
| Settings — M1-A3 implementation/tests, M1-A-GATE shell, M1-D4 targets | Levels/mute survive restart; corrupt fields default; save failure retains last good file and reports retry; live audio preview leaves shared simulation running. |
| Prediction/targets — S03-R/S04 response decisions, S07 budgets, S08 target proof; M1-A2/B1 implementation, M1-D3/D4 full acceptance | Matching-tick authoritative convergence and bounded replay meet selected budgets; no replay damage/effects; exact exported ENet and Steam paths each pass on required targets. Loopback markers cannot close gameplay, Steam or Deck requirements. |

Pending exact choices are owned: native integration/correlation and tested limits
(S03-S), production codecs/snapshot batching/abuse disconnect (M1-D3, informed by S03), motion extras/camera and
prediction (S02/S03-R/S04), interaction thresholds/stopping (S04), combat tuning and
chain/retention capacity policy (S05), topology/route/bake bounds (S06), toolchain and
measured budgets (S07/S08). These remain active tasks in [TODO](../TODO.md); P0-02
completes the draft, not those proofs or production acceptance.

## S02 desktop candidate boundary

The [S02 desktop fixture](spikes/s02.md) implements a bounded standalone facing-relative
step and pistol-ray probe. It selects no prediction/network/combat API. Candidate
values are 5/3 m/s forward/reverse, 180°/s turn, capsule radius0.38 m/height1.8 m,
World bit1 and Actor bit2. The query checks body centre to source-derived muzzle
before the forward ray, so an extended weapon cannot shoot through world collision.
Input cancellation is owned by LocalRig/Input; actual native-focus validation and
user feel remain pending. Rendering cutaway never changes solid collision. These
are spike candidates for S03-R/S04/P0-GATE, not accepted production tuning.
