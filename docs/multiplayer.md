# Godot multiplayer guidance

Build multiplayer around explicit simulation ownership, current-state admission,
and clean session teardown. The isolated [S03 proof](spikes/s03.md) now exercises
a tiny real-process ENet connection contract. Accepted bounded
[S03-R foot](spikes/s03-r.md) and [S04 car](spikes/s04.md#accepted-exact-final-disposition)
experiments add applied-physics response evidence; production gameplay and drawn
responsiveness/feel acceptance remain future work.
ENet for local testing and Steam for friends playtesting are confirmed first-milestone
requirements, using the existing Steam app. The [ratified brief](design.md) selects
an authoritative listen server, 1–4 players, late joining and match termination on
host loss. Rates, measured limits and the exact Steam integration remain spike
decisions. The practices below generalize VCS's host-authoritative approach.

The P0-02 [architecture](architecture.md), [scene](scene-structure.md), and
[API](api-contracts.md) drafts own the concrete state map, endpoints, admission
scheme, signatures and provisional limits. Refine them with spike evidence; the
general guidance here must not create competing rules or replication writers.

## Starting choices and boundaries

A listen server is the selected M1 model for both ENet and Steam: the host plays
and simulates authoritative outcomes. Standalone uses those same rules without
Steam or a remote peer. A dedicated-server product and host migration are outside
M1. The brief records target platforms, player count, late-join and host-loss policy.
Server authority protects against client mutation; it does not make a player-host
trustworthy against its own cheats.

Use Godot's `MultiplayerPeer` and high-level RPC/replication facilities. Keep
backend-specific connection and discovery details out of gameplay. Define a narrow
session/transport contract before implementation, with concrete ENet and Steam
providers and explicit capability, failure, cancellation and lifecycle behavior.
Keep Steam lobby/invite services separate from gameplay transport. Both providers
use the same match protocol and authority rules; select one before connecting and
retain it until teardown. ENet startup must work without Steam. Do not wrap every
RPC in another networking framework. RPC endpoints require matching node paths
and compatible RPC declarations across peers. Peer 1 is the server in Godot's
high-level model. Verify transport support when adding platforms,
especially for browser targets.
[Godot high-level multiplayer](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html).

| Responsibility | Draft owner (canonical detail in architecture) |
| --- | --- |
| Peer creation, connection attempts and timeouts | Session service with ENet/Steam transport adapters |
| Steam availability, friend lobbies, invites and launch requests | Platform adapter feeding the common session flow |
| Connection roster and admission operation | SessionService |
| Match loading, world readiness, spawn/reset policy | Match controller |
| Input validation, protocol encoding, replication | A focused admission/replication boundary |
| Movement, health, inventory, interaction rules | Existing gameplay components |
| Local input, camera, HUD, prediction | One local rig for this process's player |
| Remote interpolation, audio, visuals | Replica presentation |

These are responsibilities, not a requirement to create six classes or autoloads.
Keep level/match-owned state local. Give each replicated field one writer. The
first proof uses explicit lifecycle/snapshot RPCs from Replication. A later switch
to `MultiplayerSpawner`/`MultiplayerSynchronizer` must replace the relevant writer
and preserve its contract; avoid two systems writing the same state.
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

The draft selects an immutable baseline plus bounded reliable durable journal and
handoff marker, with input opened only after the marker acknowledgement. Movement
starts from fresh admitted state and remains gated by lifecycle/collision revisions.
See [admission and replication](api-contracts.md#admission-and-replication) for the
algorithm and [limits](api-contracts.md#provisional-limits-and-failure-codes) for its
deadlines/caps. S03 proves a two-chunk cut and one during-load durable record through
handoff, including provisional cancellation and a retained-player resync;
the complete journal/overflow/reset suite remains M1 work. Do not choose another catch-up
writer in a component.

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

S03's actual UDP reordering/loss experiment confirms that an unreliable-ordered
stream orders packets across entity subsets, not independently per entity. Use
per-entity application watermarks and periodically refresh every relevant entity,
even when unchanged; a global last-packet tick or dirty-only publication can starve
a subset. The API draft proposes a 250 ms maximum revisit interval; S03's two-row
experiment uses 120 ms packet spacing and a 240 ms revisit interval. It does not
establish capacity bandwidth or convergence under the brief's network profiles.

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

The pinned engine has a known ENet server-creation defect. Follow the workaround
contract in [Known upstream defects](#known-upstream-defects) until a fixed engine
is selected and verified.

Steam is required for friends playtesting. Distinguish lobby membership/discovery
from gameplay transport and admission. Use the route the selected integration supports;
do not assume that exchanging addresses through a lobby makes ENet relay through
Steam. Steam Networking can use SDR, but its availability and the actual connection
route need independent verification.
[Valve SDR documentation](https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay).

Use the project's existing Steam app. Record its AppID/app type, tester access,
private branch, depots and launch settings before the proof. The user designated
AppID 5294580 and Windows/Linux depots 5294581/5294582 from VCS; the
[product brief](design.md) records provenance and unresolved live setup/access.
Phase zero must choose and pin an integration compatible
with the exact Godot engine and target native libraries, and prove real gameplay
traffic over Steam. Preserve ENet builds/startup without Steam installed or running.
Map Steam account/lobby IDs and provider peer IDs to fresh session identities at
the boundary; a Steam identity or lobby membership does not grant input admission.

Test with distinct authorized accounts on separate machines/networks, inspect
connection/relay diagnostics, and exercise unavailable-service errors. Friend/overlay invites and
launch arguments must feed the same join/cancel flow, including while loading or
already in another match. Use this project's existing application identity.
The user explicitly authorized the existing VCS app/depot identities for this
project. Keep Fun Things protocol/content compatibility independent and use a
distinct private branch with a reviewed app-level launch recipe; preserve VCS's
existing build delivery. Do not infer tester access from checked-in upload configs.

End a listen-server match cleanly on host loss unless host migration is deliberately
implemented. A platform lobby ownership change alone does not transfer simulation.
Distribution, installation, lobby success, and gameplay connectivity each need
their own acceptance checks.
Friends need app/package access as well as access to the private build branch.
Establish that route during phase zero, then verify installation, updates, Steam
launch and gameplay on the milestone build. See
[Testing on Steam](https://partner.steamgames.com/doc/store/testing).

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
5. **Target delivery:** exercise exported builds through both ENet and Steam on
   supported platforms. Prove ENet without Steam and Steam with distinct accounts
   on actual external networks; verify private app access, install/update and launch.

The runner should allocate separate writable user/log directories, configurable
ports, structured readiness/results, and wall-clock deadlines. Stop only its own
child processes and retain failure logs. Drive production APIs rather than a
parallel test implementation. Distinguish socket/path startup failures from failed
gameplay assertions, and reject new engine/script errors even with exit code zero.
Loopback tests establish shared flow; they cannot certify another transport or
external-network connectivity.

## Known upstream defects

- **ENet server channel/bandwidth argument order:** the pinned engine and inspected
  upstream `master` pass `max_channels` as server incoming bandwidth and ignore the
  requested incoming limit. See the [source verification, runnable MRP, and upstream
  report draft](upstream/godot-enet-create-server-bandwidth.md). Until M1-A1 selects
  and verifies a fixed engine, every ENet adapter must call
  `host.bandwidth_limit(0, 0)` (or its explicit intended limits) immediately after
  successful `create_server` and before publishing the peer or allowing connections.
  Tests must keep the client peer's `PEER_PACKET_THROTTLE_LIMIT` at
  `PACKET_THROTTLE_SCALE`. This does not change the lossy contract for unreliable
  held input or motion; never wait indefinitely for a result from one unreliable send.

The [bounded S03-R ENet candidate](spikes/s03-r.md) exercises the actual unchanged
S02 controller in two headless processes over baseline and impaired UDP delivery.
Its simulation-response/convergence metrics do not prove visible response, remote
presentation continuity, prediction corrections or user feel. No production foot
prediction choice is selected. S03-R remains open for drawable measurements,
bounded host-tick/held replay mapping if warranted, and the existing Steam/target gates.

## Accepted S04 technical boundary

The [body/seat record](spikes/s04-contracts.md#executable-technical-envelope) refines
the canonical API; it owns these fixture details rather than a second networking
contract. `S04DriveRules` shares handling across character and rigid adapters.
Pre-tree passive bodies disable collision and simulation; rigid replicas additionally
freeze STATIC with sleep/zero velocities/gravity. Character capture follows solved
movement; rigid capture represents the prior solver interval before next writes.
Acknowledgement records consumed/superseded held intent, which may span many ticks.

The fixed two-driver ENet fixture preflights baseline dependencies, fences old
session/entity/generation/life/control/collision state and waits for grant plus fresh
movement. The P2-corrected actual producer checks input admission every callback and
clears held keys while closed; movement cannot write health/seat/equipment. Injured
player/seat/equipment retention is bounded seated reauthorization. Player markers
and explicit vehicle IDs are a compatibility codec; production drive context must
address the controlled vehicle EntityRef. No production wire compatibility is implied.

[M1-B1's specified matrix](spikes/s04-contracts.md#m1-b1-transition-matrix-specified-not-implemented)
keeps seat transactions with VehicleInteraction under Match, adverse acceptance with
M1-D3, and no-seated-fire/reload feel confirmation before P0-GATE. Entry/exit races,
disconnect/death/destruction/reset and production late join are specified, not proved
by this fixture. Exact [2370ad1 acceptance](spikes/s04.md#accepted-exact-final-disposition)
closes P2/P3. Original physics p95 97/269/401 ms and fixed normal/adverse248/380 ms
remain separate,20/20 each; no drawn receipt exists. Zero matching-tick install error
and update jumps are not prediction correction. Physical input/focus, visible
response/camera/readability/feel, final body/dimensions/turning/prediction, full S04,
Steam/Deck/Windows/exports/capacity and P0/M1/production gates remain open.

## Accepted stopped Steam compatibility boundary

The [S03-S compatibility record](spikes/s03-s-compatibility.md#lifecycle-limitation-and-exact-stopdecision-boundary)
and [saved criteria](spikes/s03-s-compatibility-evidence/criteria.md) apply the existing
[canonical API transport contract](api-contracts.md#transport-and-platform-adapters);
they create no second contract. Four independent streams retain reliable0/1 and
ordered-unreliable2/3 modes, application admission/identity/durable ownership and
bounded work. The exact inspected singleton API lacks lane-addressed send and
receive lane metadata; batch payload ownership, checked send results and peer mode
mapping need evidence. Five configured lanes cannot fix ordered-unreliable sent
reliably or missing ownership/results/metadata. A finite freshness filter supplies
neither a conforming peer nor authenticated admission.

Native callback handles/current identity do not prove operation ownership or safe
cancel/drain/retry. Obsolete callbacks must remain cleanup-only and never attach to
a new attempt; unsafe reuse keeps Steam unavailable until safe reuse/restart is
proved. See the record's complete decision boundary rather than deriving a drain
guarantee from arbitrary waits or close return values. Exact
[ca38e4f acceptance](spikes/s03-s-compatibility.md#accepted-exact-final-compatibility-disposition)
accepts stopped source/model/reflection evidence only. No actual delivery/lifecycle,
loss/saturation/send-error/queue/allocation, native or external route/relay/package/
device acceptance follows. Root can commission exact immutable upstream evidence,
a separately bounded native-boundary design, or keep Steam unavailable; no adapter,
integration, five-lane fix, reliable fallback, SDK/vendor/pin choice is selected.
Full S03-S/Steam/Deck/S04/P0/M1/production gates remain open.

## Accepted partial S05 damage and settled hydration boundary

[Exact754a0b5 partial S05](spikes/s05.md#accepted-exact-final-disposition) consumes
unchanged S03 admission/replication and S04 body APIs. ONE
[fixture contract](spikes/s05-contracts.md#reliable-cut-and-admission-boundary) defines
the minimum local S05Damage writer, sender-derived fire validation, current cut and
live-event adapters on the same four channels/endpoints. Movement never installs
health/life/seat/collision. Replicas begin passive before tree callbacks; current
wreck dependencies install while input is closed, before normal grant/fresh movement.

Actual separate ENet host/live/settled-late processes reject active and retired
ShotId duplicates, wrong owner/context and exercised malformed/oversize/rate/window
cases; live events consume once, post-chain hydration consumes zero historical tokens.
This is settled joining only. Arbitrary car changes during an in-flight immutable
baseline still need canonical durable journal/handoff, collision fences and reset/
admission races under M1-B3/M1-D3. No new baseline/journal framework is accepted.

The retained shooter floor survives active-cache retirement/departure until teardown;
reserved twelve-car jobs finish independently of cosmetic capacity. The four lifetime
shooter-slot guard (including pending initial reservations) is finite safety evidence,
not full fifth-peer/reconnect/loading/abuse acceptance. Application512-byte intent/
8192-byte cut caps are not predecoder/MTU/native allocation or sustained flood proof.
Sentinel occupant9001 is not an admitted player death/respawn/seat transaction.
Stationary wreck collision/query retirement is not final moving-contact proof.

Eight TOKEN reservations/four drops with hidden complete outcomes supply no actual
effect draw/load evidence. Full S05 needs source-linked eight-effect drawable
saturation/live-versus-hydrated receipts, Regner policies and spacing/contact reruns
following final S02/S04 dimensions. M1-B1/B2/B3/B4/D retain full lifecycle, journal,
reset, feedback and sustained acceptance; S07 needs real S06 topology/seams, effects
and hardware/four views/residency/load. All Steam/native/Deck/input/feel/P0/M1/
production gates and the normative contracts above remain open.
