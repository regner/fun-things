# Godot multiplayer guidance

Build multiplayer around explicit simulation ownership, current-state admission,
and clean session teardown. Prove a small real-process connection flow first, then
add authoritative gameplay and responsiveness. This project has no networking yet;
the topology, player count, transports, rates, and platform integration remain design
decisions. The practices below generalize VCS's host-authoritative approach.

## Starting choices and boundaries

A listen server with ENet is a practical desktop prototype: the host plays and
simulates authoritative outcomes. It is a starting recommendation, not a constraint
on a future dedicated server or another model. Decide target platforms, player
count, trust model, late-join behavior, and host-loss policy before implementing.
Server authority protects against client mutation; it does not make a player-host
trustworthy against its own cheats.

Use Godot's `MultiplayerPeer` and high-level RPC/replication facilities. Keep
backend-specific connection and discovery details out of gameplay. Define a narrow
session/transport contract before implementation, with one initial provider and
explicit capability, failure, cancellation, and lifecycle behavior. Add another real
provider when a selected target requires it; do not wrap every RPC in another
networking framework. RPC endpoints require matching node
paths and compatible RPC declarations across peers. Peer 1 is the server in Godot's
high-level model. Verify platform transport support before committing to ENet,
especially for browser targets.
[Godot high-level multiplayer](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html).

| Responsibility | Suggested owner |
| --- | --- |
| Peer creation, connection attempts, timeouts, discovery | Session service and optional transport adapter |
| Match loading, readiness, roster, spawn/reset policy | Match controller |
| Input validation, protocol encoding, replication | A focused admission/replication boundary |
| Movement, health, inventory, interaction rules | Existing gameplay components |
| Local input, camera, HUD, prediction | One local rig for this process's player |
| Remote interpolation, audio, visuals | Replica presentation |

These are responsibilities, not a requirement to create six classes or autoloads.
Keep level/match-owned state local. Give each replicated field one writer. Choose
`MultiplayerSpawner`/`MultiplayerSynchronizer` or explicit lifecycle/snapshot RPCs
according to the required contract; avoid two systems writing the same state.
Synchronizers do not support Resources, RIDs, or peer-local object instance IDs.
Send stable IDs and primitive data and resolve definitions locally.
[Godot synchronizer API](https://docs.godotengine.org/en/stable/classes/class_multiplayersynchronizer.html).

## Authority and input admission

Clients send intent rather than authoritative poses, damage amounts, or timer
results. The host/server owns outcomes: movement results, spawning, equipment,
pickups, damage, death/respawn, and persistent world changes. A client may own an
input channel without becoming multiplayer authority over its gameplay body.
Godot scene `owner`, input ownership, and multiplayer authority are distinct concepts.

Configure replica simulation flags before nodes enter the tree, including scripts
on children. Replicas must not apply damage, collect pickups, run respawn timers,
or spawn gameplay projectiles from `_ready`, physics callbacks, or overlaps.
Separate presentation entry points so disabling simulation leaves visuals usable.

At every remotely callable input boundary:

- Derive identity from `multiplayer.get_remote_sender_id()` while handling the RPC;
  do not trust a payload claiming a peer/entity identity. The host's local commands
  use the same validator through an explicit local path.
- Require the expected session, admission phase, entity generation, and lifecycle
  revision. Validate exact types, allowed fields, finite numbers, control ranges,
  aim constraints, monotonically accepted sequences, and sequence-ahead limits.
- Bound packet size, batch length, request rates, queue length, and processing per
  tick. Rate-limit edge actions such as reset. Reject invalid data before mutation.
- Release held input after a bounded loss-of-input timeout and immediately on
  disconnect, death, or teardown. Handle focus loss so firing cannot remain stuck.

Use the server's fixed simulation step. Never trust client elapsed time or run
extra simulation steps just to drain a backlog. Define a bounded backlog policy
that prevents a host stall from causing persistent delayed controls. Superseding
obsolete controls must agree with acknowledgement/replay semantics and preserve
important discrete actions.

## Session and join lifecycle

Track explicit connection states, such as idle, connecting/hosting, loading,
in-match, and closing. Bound connection and loading waits independently. A slow
joiner must not pause the host. Keep RPC endpoints available before messages can
arrive, or gate transport use until their scene exists.

1. Establish transport, negotiate protocol and required content/map compatibility,
   and associate the connection with a fresh session identity.
2. Load the agreed content. Disable client mutation and register static gameplay
   IDs before declaring world readiness. Transport connection is not gameplay admission.
3. Host validates readiness and sends an authoritative baseline with a server tick,
   roster/entity generations, current poses, equipment, lifecycle/health, and all
   persistent world state relevant to that player.
4. Client applies it idempotently, creates replicas, and binds its one local rig.
   Required collision and lifecycle state must be ready before prediction begins.
5. Admit input/live replication after baseline acknowledgement. Cover changes during
   loading with a bounded reliable change replay or a fresh complete state handoff;
   choose and document one consistent scheme. Send fresh movement after admission.
6. On leave/failure, stop producers, close the peer, remove entities/rig, clear
   pending callbacks and histories, release local input/cursor state, and return
   to a usable menu. A second host/join attempt must start cleanly.

Choose safe, unoccupied spawn locations and reserve admission slots where necessary.
When none is available, bound retries and report a useful failure rather than
stacking actors. Deduplicate readiness/baseline requests. Bound catch-up state and
abort only the stalled admission if it exceeds its limits.

Late joins receive partially changed state as well as destroyed/dead states. Apply
historical state without replaying old explosions, pickup sounds, or damage effects.
Distinguish a baseline hydrate from a new live transition.

Canceling an asynchronous attempt invalidates its work, but still clean up any peer
or lobby created by a late callback. Correlate callbacks using actual operation
handles/IDs when supported. A local counter alone cannot identify callbacks that
carry no attempt identity; serialize/drain such operations or use the backend's
documented correlation mechanism. Do not switch transport inside an active session.

## Message ordering and state revisions

Reliable and unreliable streams can interleave. A server tick alone cannot protect
against all resets, respawns, reused entity IDs, or a new match.

| Identity or revision | Purpose |
| --- | --- |
| Session identity | Reject packets from a previous match/connection lifecycle |
| Entity ID plus generation | Distinguish a new spawn from an older entity with the same ID |
| Movement tick/input sequence | Reject obsolete movement and duplicate commands |
| Reset/life revision | Prevent old input and poses from undoing reset, death, or respawn |
| Component revision | Order independent equipment, health, or persistent world changes |
| Collision revision, when needed | Gate movement that depends on changed world collision |

Use only revisions needed by the chosen features. Keep movement from overwriting
reliable component state. Retain generation tombstones for departed entities so a
delayed snapshot cannot recreate them. Bound waiting for future lifecycle/world
state and provide resynchronization or failure behavior.

If destruction changes collision, publish its collision revision only after
deferred shape changes have taken effect. Hold dependent movement until that
revision is applied; keep the waiting buffer bounded. A collision fence protects
ordering, not historical collision replay: old predicted frames replayed against
today's geometry can still need correction. Document that approximation unless
historical worlds are actually implemented.

Complete reset/death/respawn state before notifying observers: neutralize commands,
restore owned component state, apply collision and presentation, clear prediction
history as appropriate, then publish the transition. Avoid intermediate alive/
zero-health or restored-pose/stale-velocity states leaking into callbacks.

## Replication and packet budgets

Send durable lifecycle/world changes reliably; send replaceable frequent movement
using an appropriate unreliable mode. Reliable delivery does not guarantee that
an unrelated unreliable packet arrives afterward. Separate traffic by purpose when
ordering or congestion requires it, and verify channel behavior on each peer backend.
Godot's default channel 0 has separate streams for transfer modes.
[Godot RPC transfer modes and channels](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html#channels).

Keep high-frequency snapshots compact. Avoid repeating names, inventory metadata,
or durable health state in every movement row when reliable component messages
already own them. Measure worst-case serialization at intended capacity, account
for RPC/transport overhead, and retain a documented payload budget below the
transport's observed limit. Large baselines need separate bounded transfer and
admission deadlines; do not treat them as normal movement packets.

For simple projectiles, replicate a stable shot ID, launch parameters, and host
impact/expiry instead of every transform. Clients can animate cosmetic flight
without deciding hits. Deduplicate launch/impact effects, keep lifetimes and effect
counts bounded, and let already-fired projectiles survive equipment replacement
when gameplay requires it. Use authoritative movement/weapon telemetry for HUD,
wheels, particles, and audio instead of stale local collision queries.

Rates and limits must be measured. VCS's 60 Hz physics, roughly 30 Hz input and
20 Hz snapshots, 250 ms input expiry, 120-frame history, and 1200-byte movement
budget are examples for its small vehicle match, not universal defaults.

## Interpolation prediction and reconciliation

Start with authoritative simulation and remote snapshot interpolation. Add owned
client prediction when measured latency makes local controls insufficiently
responsive. Interpolation smooths remote presentation; prediction responds locally
and then reconciles with the server. Neither grants authority to the client.

Prediction should use the same movement function as host simulation:

1. Sample numbered inputs on physics ticks and retain a bounded history. Redundant
   recent frames can recover brief controls lost in unreliable delivery.
2. Host validates/deduplicates frames and simulates within its tick budget. Acknowledge
   inputs actually simulated, or explicitly superseded under a defined policy,
   rather than merely received. Missing-frame synthesis must not add elapsed time.
3. Reconcile on a physics tick: restore authoritative pose, velocity, required
   contact/grounded state, and telemetry; remove acknowledged history and replay
   permitted remaining inputs. Suppress damage, inventory changes, world mutation,
   duplicate audio, and gameplay effects during replay.
4. Smooth small visual corrections separately from the collision body. Clear/snap
   history for resets, new generations, large corrections, teardown, or overflow
   according to a documented recovery policy. Never allow unbounded replay work.

Keep physics pose, render interpolation, visual correction, and animation/suspension
under separate ownership so transforms do not compete. Cameras may follow a smoothed
anchor while retaining the correct actor collision exclusion and gameplay telemetry.
Check aiming from both camera and muzzle during turns and reconciliation.

Character-body contacts and interactions with remote moving actors can make replay
approximate. Do not assume identical physics across peers or claim full-world rollback.
Test slopes, flight, walls, moving contacts, and changing collision explicitly. VCS's
optional local collision exceptions for predicted prop impacts are a feature-specific
technique, not permission to mutate authoritative world collision.

## Transport and platform acceptance

ENet loopback/LAN is a useful initial test path. Remote players still require UDP
reachability; discovery does not supply NAT traversal. If browser support is needed,
evaluate supported WebRTC/WebSocket paths rather than assuming desktop UDP works.
Keep platform initialization optional in shared code when supporting non-platform
builds, and verify installed native class/API signatures and export dependencies.

If Steam is selected, distinguish lobby membership/discovery from gameplay transport
and admission. Use the networking route the installed integration actually supports;
do not assume that exchanging addresses through a lobby makes ENet relay through
Steam. Steam Networking can use SDR, but its availability and the actual connection
route need independent verification.
[Valve SDR documentation](https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay).

Test with distinct authorized accounts on separate networks, inspect connection
diagnostics, and exercise unavailable-service errors. Friend/overlay invites and
launch arguments must feed the same join/cancel flow, including while loading or
already in another match. Use this project's own application identity if configured.
Never reuse VCS's AppID, depots, protocol string, or release configuration.

End a listen-server match cleanly on host loss unless host migration is deliberately
implemented. A platform lobby ownership change alone does not transfer simulation.
Distribution, installation, lobby success, and gameplay connectivity each need
their own acceptance checks.

## Implementation milestones and checks

1. **Connection flow:** launch two separate processes through normal host/join APIs;
   prove distinct entities/spawns, one local rig each, cancel, leave/rejoin, host
   loss, incompatible/full/unreachable sessions, bounded failures, and clean retry.
2. **Authoritative gameplay:** prove independent controls, rejected client mutation,
   stale-input release, real collision, reset/lifecycle ordering, and matching-tick
   replication. Add each gameplay system's current state to late-join baselines.
3. **Adverse delivery:** inject delay, jitter, loss, duplicates, stale sessions and
   revisions, slow admission, deferred collision, and host stalls. Verify queue,
   packet, processing, and timeout limits at intended capacity.
4. **Responsiveness:** if prediction is added, show local response before host
   confirmation and convergence afterward. Measure correction sizes/continuity,
   test history exhaustion, and inspect two real windows for HUD/camera/aim/audio.
5. **Target delivery:** exercise exported builds and each chosen transport on the
   supported platforms and actual external networks.

The runner should allocate separate writable user/log directories, configurable
ports, structured readiness/results, and wall-clock deadlines. Stop only its own
child processes and retain failure logs. Drive production APIs rather than a
parallel test implementation. Distinguish socket/path startup failures from failed
gameplay assertions, and reject new engine/script errors even with exit code zero.
Loopback tests establish shared flow; they cannot certify another transport or
external-network connectivity.
