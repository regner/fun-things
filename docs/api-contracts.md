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
S03 settled only its minimum subset; S03-R/S04/S05/S07/S08 refine remaining
initial-game limits, and P0-GATE records the settled contract before production acceptance.
S03-S now reviews future-adapter compatibility only; it does not select or test Steam. Contract
changes update these documents and acceptance cases together.

## Common types, identity and compatibility

| Type / field | Shape, units and scope |
| --- | --- |
| `OperationId` | Positive local 64-bit integer, monotonically allocated by SessionService; never reused during the process; not a network identity |
| `ProviderId` | Stable namespaced identifier for a Boot-composed session provider; M1 initially registers only `&"enet"` |
| `ConnectionToken` | Opaque adapter-generated local token; never reused across adapter or connection generations and never serialized as gameplay identity |
| `JoinTarget` | Opaque adapter-owned `{provider_id, adapter_generation, kind: TRANSPORT_READY | DIRECTORY, local_handle}`; raw addresses/account/lobby IDs and native objects never leave their adapter |
| `SessionId` | Host-created opaque 128-bit random value encoded as 32 lowercase hex characters; fresh for every host/standalone match session |
| `ParticipantId` | Positive host-allocated 64-bit integer, unique within SessionId; reconnect gets a fresh ID, including the same provider account |
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
128 bytes each; their generation is S06/M1 work. ENet admission uses `SceneMultiplayer`
authentication, not an RPC: `auth_callback` receives a fixed raw `PackedByteArray`, `send_auth`
returns the fixed verdict, and both sides call `complete_auth` only after acceptance. Unauthenticated
peers therefore cannot dispatch RPCs. The request is capped at 512 logical bytes; the host checks raw
lengths and UTF-8 before `StringName` conversion, rate-limits requests per transport peer and
disconnects repeated abuse. Display version and engine version are diagnostic metadata, not
compatibility. Unknown definitions
or world IDs fail
admission with `INCOMPATIBLE`/`CONTENT_INVALID`, never a fallback gameplay definition.

SessionService maps `(active provider operation, ConnectionToken, native peer ID)` to
ParticipantId only after handshake validation. A future provider maps native account/lobby
IDs to opaque targets and authenticates its expected connection identity inside the adapter.
Account identity, directory/lobby membership and reused native peer numbers grant no admission.
Remove mappings on disconnect/closing and reject old operation IDs/tokens. Revisions reject
obsolete state; they are not authentication secrets. Authentication-ticket bytes and native
identity objects never enter SessionService, Match, Replication or gameplay records.

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

`HostRequest = {provider_id: ProviderId, district_id, capacity: 1..4,
provider_options}`. Boot composes a fixed provider table before SessionService accepts
operations; M1 initially registers only `&"enet"`. Each binding contains one Transport
and zero or one matching SessionDirectory. Bind options are adapter-owned and validated;
provider registration cannot change while a session is active or closing. An unknown or
unavailable provider returns `SERVICE_UNAVAILABLE`, without changing gameplay APIs.

The UI boundary calls `ENetTransport.parse_endpoint(address: String, port: int)
-> Result<JoinTarget>` or receives a directory-produced target. ENet returns a
`TRANSPORT_READY` target. Invite, rich-presence and launch payloads are parsed strictly
inside their future SessionDirectory and become `ExternalJoinRequest = {target:
JoinTarget, source: INVITE | RICH_PRESENCE | LAUNCH}` with a `DIRECTORY` target. Raw
platform text and IDs do not reach SessionService.

Targets expire when their adapter is reset/closed; joining an expired target returns
`TARGET_EXPIRED`. Port is 1..65535; address text is bounded to 255 UTF-8 bytes and
parsed/normalized by the ENet adapter. No public/LAN discovery is promised.

`SessionView = {phase, operation_id?, provider_id?, session_id?, local_participant_id?,
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
attempt. Entering CLOSING starts one five-second monotonic local deadline shared by all
acquired components; invoking component closes in reverse acquisition order cannot extend
it. Finish when all close results arrive or when that deadline expires, whichever comes
first. At expiry, detach each non-reporting component into cleanup-only ownership and
record a forced `CloseResult {reuse_status: UNAVAILABLE, failure: CLEANUP_TIMEOUT}` for
it. Then emit the operation's one completion and restore the local menu/IDLE state. A
late callback can release obsolete native resources but cannot publish state, complete
the operation again or rewrite its forced result. Standalone/ENet and any safe provider
remain usable. Do not attach a new uncorrelated attempt while obsolete native work is
pending. Any later provider must prove its actual safe cleanup/retirement strategy before
registration and reuse.

An optional SessionDirectory emits `join_requested(ExternalJoinRequest)`. In IDLE it
enters this same join flow; while connecting/loading the UI offers cancel-and-join, and
in ACTIVE it asks before leaving the match. Keep at most one pending external request;
a newer target replaces the pending target, never silently leaves the current match.
Settings/menu focus neutralizes local intent without pausing shared simulation.

### M1-A1.1 production session shell

`res://scripts/session/session_service.gd` now owns the process-lifetime operation ID,
phase, selected provider, local session identity, retry request and five-second close deadline.
Its public `host`, `join`, `start_standalone`, `cancel`, `leave`, `retry` and `view` methods use
normalized Dictionary result records matching the contract shapes above. Synchronous rejection
allocates no operation; each accepted operation emits `completed` once. Standalone reaches ACTIVE
without creating a fake peer. `SessionTransport` is the provider seam, while
`FakeSessionTransport` supplies correlated delayed callbacks for unit tests only.

M1-A1.1 intentionally stops at the transport seam: Boot registers no network provider yet. Raw
address text remains in the menu until M1-A1.2 adds ENet endpoint parsing, transport capabilities
and real host/join behavior. `DIRECTORY` targets are rejected until a `SessionDirectory` can resolve
them; only `TRANSPORT_READY` targets reach the seam. Closing first replaces the active peer with an
offline peer, then waits for the correlated provider close result or the one shared five-second
monotonic deadline. A late peer is disposed and a late close/failure callback cannot change view
state or complete again. The shell publishes selected capacity with an empty pre-admission roster,
and same-instance registration cannot clear a forced-unavailable provider fence.

## Transport and session-directory adapters

This is the **M1-A1 contract**: ENet is the only initial provider, while the boundary
remains capable of accepting a separately selected later adapter. The fixed logical
stream profile and provider-neutral lifecycle are normative. The isolated S03 fixture's
smaller capability dictionary remains evidence for ENet behavior, not the production type.
The [S03-S abstraction review](spikes/s03-s-abstraction-review.md) maps future Steam
concepts to this boundary and records why no Steam implementation is accepted now.
Owner decision 17 removed GodotSteam from the project on 9 October 2026; these APIs do
not require its classes, settings or libraries.

```text
Transport.provider_id() -> ProviderId
Transport.capabilities() -> TransportCapabilities
Transport.open_host(operation_id, provider_options) -> Result<void>
Transport.open_client(operation_id, target: JoinTarget) -> Result<void>
Transport.close(operation_id) -> Result<void>
Transport.connection_diagnostics(connection: ConnectionToken)
    -> Result<BoundedTransportDiagnostics>
signals to SessionService only:
  peer_ready(operation_id, peer: MultiplayerPeer)
  connected(operation_id, connection: ConnectionToken, native_peer_id: int)
  disconnected(operation_id, connection: ConnectionToken, Failure)
  failed(operation_id, Failure)
  closed(operation_id, CloseResult)

SessionDirectory.provider_id() -> ProviderId
SessionDirectory.capabilities() -> DirectoryCapabilities
SessionDirectory.create_joinable(operation_id, capacity) -> Result<void>
SessionDirectory.join(operation_id, target: JoinTarget) -> Result<void>
SessionDirectory.close(operation_id) -> Result<void>
signals:
  host_ready(operation_id, published_target: JoinTarget)
  join_ready(operation_id, transport_target: JoinTarget)
  failed(operation_id, Failure)
  closed(operation_id, CloseResult)
  join_requested(ExternalJoinRequest)
```

These peer/token signals are private boundary APIs, not gameplay data. SessionService
is the only consumer and attaches the Godot peer only when endpoints exist. A token is
fresh for one adapter/connection generation and cannot be reconstructed from a native
handle. The transport supplies connectivity and authenticates any provider identity;
it cannot allocate ParticipantIds/player entities or admit input. A directory owns
optional discovery/lobbies/invites/launch parsing; its matching transport owns gameplay
connectivity. Host creation publishes a joinable target only when the host endpoint is
ready. `host_ready` returns the publishable `DIRECTORY` target; `join_ready` returns a
`TRANSPORT_READY` target for the same provider and current adapter generation. A failure
cleans up both resources. ENet has no SessionDirectory. Until the pinned engine defect is
fixed and verified, ENetTransport applies its intended bandwidth limits immediately after
server creation and before `peer_ready`; that workaround is adapter-internal and cannot
change the lossy contract of channels 2/3.

`TransportCapabilities = {available, identity_assurance, streams,
max_receive_packet_bytes, native_receive_packet_limit_available, max_auth_payload_bytes,
route_diagnostics_available, failure?}`. A zero receive limit means unknown/unavailable, not
unbounded safety. Identity assurance is
`NONE | PROVIDER_AUTHENTICATED`; ENet uses `NONE`, while any later account-targeted adapter
must authenticate the expected provider identity before emitting `connected`. Each stream
row is `{channel, delivery, queue_policy, max_logical_payload_bytes}`. M1 requires exactly:

| Channel | Delivery | Queue policy | Logical ceiling |
| --- | --- | --- | --- |
| 0 session/admission/actions | `RELIABLE_ORDERED` | `DURABLE` | 4096 bytes for actions; control codecs may be smaller |
| 1 baseline/durable/results/events | `RELIABLE_ORDERED` | `DURABLE` | 16 KiB complete transaction or chunk |
| 2 held input | `UNRELIABLE_ORDERED` | `REPLACEABLE_LOSSY` | 1200 bytes |
| 3 movement | `UNRELIABLE_ORDERED` | `REPLACEABLE_LOSSY` | 1200 bytes |

Limits describe tested logical-message support including audited peer framing; they are
not native MTUs, fragment ceilings or decoder-allocation guarantees. Godot 4.8-dev7 exposes no
configurable ENet receive/reassembly or native packet-size ceiling through `ENetMultiplayerPeer`,
`ENetConnection` or `ENetPacketPeer`; ENet reports that native limit as unavailable. The 512-byte
auth cap is enforced on raw `PackedByteArray` data before Variant/RPC decoding, but after native ENet
receive and reassembly. A substantially oversized native packet can therefore consume native receive
resources before application rejection; this is a residual release risk rather than a claimed
transport bound. The adapter must
reject aliasing, reliable substitution, unsupported modes and oversize packets instead
of silently falling back. Provider-specific native lanes and sequence filtering remain
inside the adapter. Native message numbers never acknowledge simulation, durable state
or gameplay application.

`UNRELIABLE_ORDERED` is lossy by contract: sequence gaps are permitted, late/duplicate
messages are discarded per connection generation and channel, and callers never wait
indefinitely for one send. A future adapter may use a native no-delay/drop-if-congested
flag only for `REPLACEABLE_LOSSY`; it is not a delivery or maximum-age guarantee.
Reliable submissions cannot be silently dropped, truncated or moved to another stream.
Replication retains its stricter codec/rate/queue limits, per-entity freshness and
periodic movement-subset revisit rules.

`CloseResult = {reuse_status: SAFE | UNAVAILABLE, failure?}`. SessionService invalidates
producer access, targets, mappings and the attached peer before close. Old operation IDs
or ConnectionTokens remain cleanup-only. The shared five-second local deadline does not
prove native callbacks drained: each component that has not reported by expiry receives
the forced `UNAVAILABLE`/`CLEANUP_TIMEOUT` result above. ENet close can report `SAFE`
after its local peer resources are released. A provider binding is reusable only when its
transport and optional directory all actually reported `SAFE` before the deadline; a
forced result or any reported unavailable result keeps it unavailable until its own
safe-reuse condition or process restart.

`BoundedTransportDiagnostics` may report `route: DIRECT | RELAY | UNKNOWN`, bounded
provider detail and traffic/queue observations. Diagnostics are local observability,
never authority or admission. Relay initialization, lobby success or a generic relayed
flag does not prove actual SDR gameplay traffic.

`DirectoryCapabilities = {available, friend_sessions, invites, rich_presence_join,
launch_join, failure?}`. No Steam initialization or native dependency is required by
Standalone/ENet startup. An absent later adapter returns unavailable capabilities and
`SERVICE_UNAVAILABLE`. Re-adding one requires a separately selected pinned release,
deliberate plugin enablement and an explicit tested export-inclusion decision; installing
an addon cannot register it as a conforming provider. Authentication tickets remain
adapter-private; no ticket bytes,
account IDs or lobby IDs enter common session/gameplay APIs. If later backend ticket
validation is selected, the provider exposes only its resulting identity assurance and
readiness. Do not add providers for unselected stores. A fake provider exercises this
boundary in tests and cannot certify native delivery.

A join with a `TRANSPORT_READY` target opens its matching transport directly. A join with
a `DIRECTORY` target first calls `SessionDirectory.join(operation_id, target)` and waits
for the same current operation's `join_ready`. SessionService validates that the returned
target is `TRANSPORT_READY`, names the same provider and current adapter generation, then
calls `Transport.open_client`; directory readiness alone cannot start negotiation or admit
input. Wrong-operation, expired or mismatched results are cleanup-only.

Cancellation/failure invalidates the operation and all targets before releasing resources.
Cleanup issues close calls in reverse acquisition order: a directory-backed client closes/
detaches its transport first if one was opened, then closes the directory membership/request;
a directory-backed host closes its published directory binding before its transport endpoint.
All calls share the operation's existing five-second deadline. A late `join_ready` after
invalidation is left/retired by SessionDirectory and never opens a transport. SessionService
emits one completion after all acquired components report `closed` or at deadline expiry.
Each non-reporter then gets a forced `UNAVAILABLE`/`CLEANUP_TIMEOUT` result and remains
cleanup-only. Aggregate reuse is `SAFE` only when every acquired component actually reported
safe before expiry. ENet has only the transport close step.

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
between channels. Every registered transport must prove four configured channels and
these modes; S03 exercises all four with ENet. A future provider must pass the same
profile before registration. The fixture's tiny JSON baseline/Variant intent and
movement codec is not the production codec or a measured maximum transport limit.

M1-A2.2 freezes S11's measured movement layout: a 12-byte header, complete 16-byte rows,
and at most 1,200 application bytes per chunk. Each row carries entity ID/generation,
kind/phase/flags, planar X/Z, planar velocity and yaw. X/Z use signed 16-bit two-centimetre
units around the fixed Brackett origin `(-0.51565, 199.42865)`, covering about ±655 m.
The codec reserves at least 50 m between every current saved Brackett node origin and
saturation. A production test traverses the saved city and fails if authored growth enters
that margin. Runtime values outside the representable domain saturate and increment a
counter; they never wrap. Full-precision authoritative state remains unchanged, and the
maximum planar quantization error is 1 cm. The measured row has no Y field, so it makes no
vertical clamp claim; a later vertical-pose field requires its own measured codec decision
rather than silently consuming flags or changing this row.

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
a client drives. Delta is the fixed host physics step, never a client value. `ActorMotion.step`
accepts a delta only when it approximately matches `1.0 / Engine.physics_ticks_per_second`; it
rejects the command and neutralizes motion before collision integration on any mismatch.

Production foot-command update, 10 October 2026 (owner decisions 3 and 25; M1-A2.1):
`FootCommand = {sequence: int, client_tick: int, move: Vector2 (world-relative, length <= 1),
aim_yaw: float (radians, facing), fire_held: bool, alt_held: bool}`. WASD movement is
world/screen-relative and independent of facing; mouse-derived `aim_yaw` owns facing. This
supersedes the stale turn-based shape. `DriveCommand = {sequence, client_tick, throttle: -1..1,
steer: -1..1, brake: 0..1, handbrake: bool}`. S04 defines reverse/brake handling. Tick is
diagnostic/replay ordering within limits, not permission to rewind host time. AI commands use host
ticks through the same rules.

Held sequence starts at 1 for each new entity/control-revision binding and never
resets within that binding. Client tick stays diagnostic; a stalled/out-of-window
sender needs the bounded resynchronization path rather than forcing extra host steps.
Only the host's fresh control revision authorizes sequence 1 again; a baseline
without that rebind cannot reset a held sequence. Reliable action sequence continues
across resync, and queued actions from the old binding are invalidated.
Held input is replaceable. At most three recent frames per message recover loss;
accept only increasing sequences within the separate 120-sequence freshness window,
and retain at most eight queued frames per participant. The dated S03-P revision
(8 October 2026; owner-accepted 9 October 2026 as the M1 contract) supersedes the earlier
newest-valid-frame wording: the host consumes queued frames in order, at most one per
physics tick. Pending lag is measured by sequence/input-tick distance from the newest
accepted frame. The host selects the oldest queued frame within three ticks (50 ms) of
that newest frame and explicitly supersedes everything older without extra simulation
steps. This one-to-one mapping keeps host simulation aligned with client replay. Receipt
age beyond `HELD_EXPIRY_MS` (250 ms) supersedes
pending intent and simulates neutral input. The acknowledgement watermark is the last
consumed or explicitly superseded frame and advances only on that simulation step;
receipt alone is never an acknowledgement. Dropped held frames carry no discrete action.
Focus loss/local UI releases controls immediately locally and sends neutral input; host
expiry remains the fallback. A new life/control revision starts neutral, even before
another packet.

`ActionRequest = {context, action_sequence, kind, payload}`. Kinds/payloads: ENTER
`{vehicle_ref}`, EXIT `{}`, EQUIP `{weapon_id}`, RELOAD `{}`, RESET `{}` and
RESPAWN_RETRY `{}`. Player actions
use the live player EntityRef even when the controlled entity is a car; held drive
input uses the car EntityRef and its control revision. RESET validates session/admission
and host privilege, not a live body, so a dead host can reset. RESPAWN_RETRY requires
the current dead/spawn-failed life revision. Other actions validate live life/control/
equipment suitability. Draft M1 policy: weapons cannot fire/reload from a seat;
S04/feel review confirms it during M1 before B1/B2 acceptance. Under owner decision 14,
this review is production work rather than a P0 prerequisite.

`ActionResult = {action_sequence, status: APPLIED | REJECTED, failure?,
durable_revision?}` is emitted after processing, not mere queue admission. A
per-participant action sequence spans life/control changes. Cache recent results;
duplicates return the cached result without another mutation; an older evicted
sequence returns `STALE_SEQUENCE`. Syntactically valid rejected requests consume
their sequence too. Reject sequence jumps outside the bound. Results never install
gameplay state; the reliable transition is the sole state application.

Host acceptance order is `(accepted_tick, participant_id, action_sequence)` for
same-tick actions. The first valid seat claim wins; others get `SEAT_OCCUPIED`.
Owner decision 23 makes M1 entry host-confirmed, not predicted: the client sends intent
and plays a short ~0.3 s get-in presentation, but control and camera/HUD ownership
change only on the accepted host transition. Rejection causes no ownership change or
snap. S04-T's predicted-entry machinery remains documented for a later upgrade.
Entry checks alive/unseated player, available/nonterminal car, range, eligible
speed, authored sockets and clearance before disabling foot-body gameplay; VehicleInteraction
tuning still settles entry range/eligible speed. Exit remains below 0.5 m/s with the authored
1.5 m offset; it tests left/right authored candidates in a fixed order with the actor
clearance query. All blocked returns `EXIT_BLOCKED` and
leaves the entire seat/control state unchanged.

Successful transfers increment control revisions, neutralize previous controllers,
clear affected prediction and commit both player/car rows. Traffic ownership stops
before player controls begin. Death/disconnect releases the seat and neutralizes
controls; surviving car stopping is S04-owned and never resumes AI immediately.

The [bounded S04 body/seat record](spikes/s04-contracts.md) specifies the complete
future race/exit/disconnect/death/destruction/reset matrix for M1-B1. Its executable
two-seat ENet adapter tests retained injured player/vehicle/seat/equipment with fresh
control, physics-phase poses and baseline floors; it is not the production vehicle
EntityRef codec or full transition implementation. Interaction/stopping values,
no-seated-fire/reload policy and prediction/feel selection remain open.

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
own radius_m, obstruction/falloff policy and chain_delay_s. Owner decision 21 accepts
these M1 starting values, tuned in playtests: health 100 for players/pedestrians/cars;
pistol 34 damage, 0.25 s fire interval, 12 rounds, 1.4 s reload and 45 m range; SMG
12 damage, 0.10 s, 30 rounds, 1.8 s reload and 35 m; rocket/S05 damage 100, 1.0 s
cooldown, 18 m/s, 2.5 s lifetime and 4.1 m radius. Car-pedestrian impact uses host
contact/velocity only: none below 6 m/s, 25 at 6 m/s linearly to 100 at 14 m/s, with
a 0.5 s per-car/target cooldown. WeaponState owns ammo/timers; DamageResolver owns
hit/friendly/self-damage policy. Shared immutable definitions cannot carry mutable
health/ammo or provider types.

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

S05/M1-B3 must settle damage/chain queue capacity, processing budget, guaranteed
completion, overflow admission policy, obstruction/falloff, chain delay and wreck
collision/retention before production acceptance. Under owner decision 14 these are M1
consumer requirements, not P0 prerequisites. An accepted shot/blast cannot silently lose
authoritative outcomes to a cosmetic cap or queue overflow. Reserved pending-chain
capacity/backpressure must be proved on the 12-car burst before production. This is
explicit unresolved production work, not permission for unbounded queues. Wreck/dead-NPC
deadlines and safe retention-cap cleanup are likewise S05/Population decisions; active
chains and occupied live cars cannot be deleted to satisfy a visual cap.

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
| Connection/negotiation | 15 s connection plus 5 s handshake | SessionService / S03 ENet minimum evidence; M1-A1/M1-D3 full ENet failures/deadlines; each future provider proves its native path separately |
| World load | 30 s per participant, never pauses host | SessionService/Match / S08 export/content proof; M1-A1/A2/M1-D3 production loading/deadlines |
| Baseline/admission | 1 MiB serialized and decoded baseline; 16 KiB logical chunks; 10 s transfer/apply, 5 s handoff; 60 s total attempt, unaffected by reset/retry | Replication/SessionService / S03 tiny cut/handoff evidence; M1-A1/A2/M1-D3 ENet size/duplicate/overflow/reset acceptance; each future provider separately proves its transport limits |
| Join journal | 2 MiB serialized or 4096 durable records per join, whichever first; overflow aborts only that admission | Replication / S03 single-health-record evidence; S05 chain decision; M1-A1/B3/M1-D3 general journal/overflow acceptance |
| Closing | 5 s local cleanup; stale native callbacks retain cleanup-only ownership | SessionService/adapters / S03 correlated fake/local cleanup evidence; M1-A1/M1-D3 bounded/hung ENet cleanup; each future provider proves correlation and safe reuse separately |
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
| Population/effects | Tunable initial settings of 64 pedestrians and 32 live cars; 16 retained wrecks/16 dead NPCs, 16 active rockets; 8 explosion presentations and 64 transient instances/client | Population/Explosions/Presentation / decision 22 tunable population; S05 bounded 12-car feasibility, S07 measured budgets; M1-B2/B3/B4/C3 implementation, M1-D3 sustained capacity |

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
`UNSUPPORTED`, `INVALID_REQUEST`, `INVALID_ENDPOINT`, `STALE_OPERATION`, `NOT_CANCELABLE`,
`NOT_ACTIVE`, `NO_RETRY`, `CONNECT_FAILED`, `CONNECT_TIMEOUT`, `HANDSHAKE_TIMEOUT`, `FULL`,
`INCOMPATIBLE`, `CONTENT_INVALID`, `LOAD_TIMEOUT`, `SYNC_TIMEOUT`, `HOST_LOST`,
`INVALID_COMMAND`, `NOT_ADMITTED`, `NOT_OWNER`, `STALE_STATE`, `STALE_SEQUENCE`,
`RATE_LIMITED`, `STATE_LIMIT`, `SEAT_OCCUPIED`, `OUT_OF_RANGE`, `VEHICLE_MOVING`,
`EXIT_BLOCKED`, `SPAWN_BLOCKED`, `NO_ROUTE`, `NOT_ALLOWED`, `COOLDOWN`, `NO_AMMO`,
`RELOADING`, `SETTINGS_INVALID`, `STORAGE_FAILED`, `CLEANUP_TIMEOUT`.
The request/endpoint/state codes are synchronous session-shell rejections and allocate no operation.
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
| Future provider conformance — not part of initial ENet acceptance | Before registration, a later adapter independently proves the fixed stream profile, authenticated identity, bounds, cancel/late-callback/retry safety and packaged gameplay delivery. Lobby success alone cannot pass. S03-S currently accepts only the reviewed abstraction; no Steam runtime test is required in this phase. |
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
| Prediction/targets — S03-P/S04-P bounded prediction evidence, S03-R/S04 response decisions, S07 budgets, S08 target proof; M1-A2/B1 implementation, M1-D3/D4 full acceptance | Matching-tick authoritative convergence and bounded replay meet selected budgets; no replay damage/effects; the exact exported ENet path passes on initial targets. A later provider requires its own target acceptance before registration; loopback markers cannot close that future proof. |

Pending exact choices are owned: future-adapter integration/correlation and tested limits
(a later separately commissioned provider task, informed by the S03-S abstraction review),
production codecs/snapshot batching/abuse disconnect (M1-D3, informed by S03), motion extras/camera
and drawable remote continuity (S02/S03-R/S04), interaction thresholds/stopping (S04),
combat tuning and chain/retention capacity policy (S05), topology/route/bake bounds (S06), toolchain and
measured budgets (S07/S08). These remain active tasks in [TODO](../TODO.md); P0-02
completes the draft, not those proofs or production acceptance.

## S02 desktop candidate boundary

The [S02 desktop fixture](spikes/s02.md) implements a bounded standalone facing-relative
step and pistol-ray probe. It selects no prediction/network/combat API. Candidate
values are 5/3 m/s forward/reverse, 180°/s turn, capsule radius0.38 m/height1.8 m,
World bit1 and Actor bit2. The query checks body centre to source-derived muzzle
before the forward ray, so an extended weapon cannot shoot through world collision.
Input cancellation is owned by LocalRig/Input. Owner decision 25 records the bounded S02
physical controls/readability and Alt-Tab native-focus owner play test as passing. Drawable
S03-R remote continuity and later production playtests remain open. Rendering cutaway never
changes solid collision. Under owner decision 14 the remaining production acceptance work is
not a P0 prerequisite or accepted tuning.

## S03-R bounded ENet candidate boundary

The [S03-R experiment](spikes/s03-r.md) extends only new fixture resources. It
calls the unchanged S02 facing-relative step once per authoritative host callback
and reuses S03 admission/context/held-expiry/lifecycle owners. Its two-body pose
extension carries host tick and consumed-or-superseded intent sequence after the
step; repeated held input can span several host ticks. This does not establish a
one-sequence/one-step replay mapping or select a production codec/prediction API.
Headless input-to-applied-physics latency, snapshot installation and settled-host
convergence are distinct from visible response and predicted matching-tick correction. The
[S03-P prediction record](spikes/s03-prediction.md) supplies completed bounded restore/replay
evidence; [M1-A2.3](plans/m1-production-plan.md#5-foundation-entry-criteria-and-ordered-m1-backlog)
owns production integration. S03-R retains drawable remote-continuity review, while later
production feel and hardware acceptance remain open.

## Accepted partial S05 executable boundary

The normative production signatures, identity shapes, limits and acceptance matrix
above remain requirements. [Exact754a0b5 partial S05](spikes/s05.md#accepted-exact-final-disposition)
implements a minimum fixture subset described by ONE
[bounded contract](spikes/s05-contracts.md), not a second production API.
S05Damage owns health/life/sentinel/EventId/work via `begin`, `register_shooter`,
`resolve_shot`, `advance`, `cut`, `valid_cut`, `apply_cut`, `retire_shooter`, `clear`.
S03 admission/marker/replication and unchanged S04 configure/neutralize/body APIs
remain collaborators. Fixture ShotId `{session, match, shooter, generation, sequence}`
and fixed car IDs are adapters, not the canonical production wire codec.

A retained per-shooter monotonic floor rejects an old ShotId after its active target
cache completes and after departure, until whole session teardown. The meaningful
[retirement negative](spikes/s05-evidence/README.md) removes just that floor and
fails specifically retired ShotId rejection. One job per terminal saved car reserves
all accepted chain work, twelve jobs maximum; four accepted roots/four target visits
per tick, with caches retired only on their own completion. Finite four-lifetime-
shooter registration/admission guard includes pending initial slots, without ID reuse.
Full reconnect, fifth-peer/loading/admission races and sustained churn remain open.

Sender-bound fire intent is exactly `{context, sequence, fire:true}`, <=512 Variant
bytes,4/s burst4, window16, no request queue; only the host chooses target/damage.
Current car cut <=8192 UTF-8 bytes/12 fixed rows extends the unchanged four-channel
S03 contract. Application caps do not prove predecoder allocation/MTU/flood capacity.
Atomic cut preflight and passive-before-tree roles keep current wreck dependencies
installed before input; marker movement cannot overwrite car state. Actual separate
ENet host/live/settled-late rows prove no historical tokens at baseline install,
not canonical during-chain journal/reset races or active projectile hydration.

Terminal state neutralizes motion and kills/releases nonrendering occupant9001
before publication. The sentinel is not an admitted player; production Health,
PlayerLifecycle and VehicleInteraction retain their owners and death/respawn/seat
acceptance. The stationary original wreck box remains300 ticks and until its blast
completes, then clears; final moving-contact/clearance proof remains open.
Normal twelve-car work is144 visits, peak4/tick, queue5, completion46 ticks; finite
pressure queue12 completes at tick41 with the same visits/peak. Both use8 TOKEN
reservations/4 drops and hidden visuals. They do not measure eight actual effects,
real draw cost or sustained capacity. Full S05 source-linked drawable saturation,
Regner provisional blast/obstruction/falloff/delay/order/occupant/wreck ratification
and post-final-S02/S04-dimension spacing/contact reruns remain required. M1-B1/B2/B3/
B4/D and S07 retain production lifecycle/journal/reset/load/feedback. Steam, Deck, P0, M1
and production gates remain open; input/feel checks beyond decision 25's bounded S02 pass
also remain open.

## Accepted partial S06 executable topology boundary

[Exact7fb302b partial ACCEPT](spikes/s06.md#accepted-exact-final-disposition) refines
one fixture subset through the [S06 contract](spikes/s06-contracts.md); production
CityData/Population/spawn/exit/admission signatures, owners and matrix above remain
normative. [S06City](../prototypes/s06/tests/fixtures/s06/city.gd) provides `validate_content`,
`signature`, `bake_content`, `route` and `map_data`. FOOT is an undirected sidewalk/
crossing graph; TRAFFIC uses directed lane curves, refusing reversal. Successful
route returns `code`, `topology_revision`, `link_ids`, `world_points_m`, `visits`;
map returns `code`, district/revision/fingerprint, imported-road world XZ bounds and
ROAD polylines/widths from the same scene-authored links. No second geometry writer.

Finite spike limits:64 anchors/128 links,64 visits/64 returned links/4096 route
samples;16 controls/link,128 m control-polygon length, exact0.25 m bake interval.
Finite vectors and finite positive ROAD widths are required before baking; total
admitted map samples <=4096. BFS scans at most64×128 links; controller nearest
search32 samples/tick and lookahead at most4096. These are fixture bounds, not
production capacity budgets. Explicit stable IDs survive reparenting; paths/local
transforms still affect the signature. District/revision/tool version, IDs/links/
widths/controls, collision flags/masks/boxes and linked GLB/import bytes bind the
bake; derived resource is excluded from self-reference. Derived roads/bounds also
must match current authored data, detecting corrupt/missing/duplicate entries.

Editor-only bake saves/assigns an external resource with cache replacement. Runtime
validation returns `CONTENT_INVALID` before route/controller/map admission for
missing/stale/revision-invalid content. Saved West+1 m rejects the old bake; coherent
City+1 m needs explicit rebake, then routes/map translate. Connectivity/missing/
duplicate IDs/corrupt roads and INF/NAN/zero/negative ROAD widths reject. No production
world-ready/network handshake codec is implemented by these offline boundaries.

[S06Controller](../prototypes/s06/tests/fixtures/s06/controller.gd) `bind_route(city, kind, from,
to, host)`, `intent(public_body_state, kind)`, `clear` supplies host commands through
unchanged S02 `step`/`motion_state`/`neutralize` and S04 `configure`/`step`/
`motion_state`/`neutralize`. Fixture sets passive state before child entry and stops
before notification. Actual recovery is1200/1800-tick finite stop; the contract's
blockage/contested-junction/stuck/wreck policies are specified, unimplemented and
untested M1-C3 work. No spawn/exit, admitted-player lifecycle, traffic-priority or
replication/prediction contract is closed. Actual unchanged-body seam routes and
four-arm map negatives satisfy provisional topology only; final-body/contact reruns,
drawn/feel, actual effects/saturation/live-versus-hydrated, S07 hardware/four views/
residency/sustained cost, Steam/Deck/P0/six-block M1/production remain open.
