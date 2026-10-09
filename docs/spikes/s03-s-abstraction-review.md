# S03-S — ENet-first transport/session abstraction review

8 October 2026. Documentation review only; no Steam implementation or testing was performed.
The owner selected ENet as the only initial transport. This review asks whether the M1-A1
session boundary can accept a later Steam adapter without changing Match, Replication, actors,
or gameplay rules. It uses the accepted public-source S03-S records as design evidence, not as
native/runtime proof.

## Result

The ownership split is sound: SessionService owns operations and admission, a transport owns
native connectivity, an optional directory owns lobby/invite discovery, and Replication owns the
four logical message streams. The existing draft already keeps native handles out of gameplay and
uses opaque join targets. The remaining gaps are mostly type and lifecycle precision at the adapter
boundary:

1. `HostRequest.transport: ENET | STEAM` is a closed product enum. Use a stable `provider_id` so
   adding a registered adapter does not change SessionService or UI flow.
2. `native_binding` and `closed(operation_id)` are too vague to fence reused handles and unsafe
   callback drain. Use an opaque connection generation and a close result that states whether the
   provider is safe to reuse.
3. Boolean reliable/unreliable capabilities do not describe the required four-stream profile,
   logical size limits, or replaceable-loss policy. Advertise the complete fixed profile.
4. The concrete `SteamPlatform` contract should be an optional provider directory contract. ENet
   has no directory; a future Steam implementation can supply one without exposing Steam IDs or
   lobby IDs to SessionService, Match, or Replication.
5. Route diagnostics need a bounded, optional transport query. Relay readiness or lobby success
   must not be represented as gameplay connectivity.

With the M1-A1 adjustments below, later Steam work is confined to a transport peer, optional
session directory, provider registration/composition in Boot, and platform packaging. Gameplay
continues to see only admitted ParticipantIds, stable session/entity identities, and the same RPC
endpoints. This is an abstraction acceptance, not evidence that a conforming Steam adapter exists.

### Coordinated product-brief reconciliation

This lane adds current owner-decision supplements to `docs/architecture.md` and
`docs/multiplayer.md` but deliberately does not edit the product brief. The concurrent
`decisions-docs` lane reconciles the pre-edit `docs/design.md` Steam requirements at lines **47–61**
(required transports/join flow), **216–222** (V6/real-Steam route), **319–320** (remaining evidence),
**324–338** (availability does not reduce requirements), **350**, **354–355**, and **362–370**
(Steam proof owners/gates). Historical AppID/depot/source observations may remain; current scope must
say that ENet is the only initial provider and a Steam adapter is separately commissioned later.

## Concept map and gap analysis

| Steam concept | Existing owner and fit | Gap | Smallest M1-A1 adjustment |
| --- | --- | --- | --- |
| SteamID account identity | Transport already authenticates native identity; SessionService maps an active native peer to a fresh ParticipantId. Gameplay never trusts an account or lobby identity. | `native_binding` does not express connection generation, and exposing a raw SteamID would couple the session/gameplay boundary to Steam. | Emit an opaque `ConnectionToken` plus native peer ID only after provider authentication. Keep SteamID↔token mapping inside the adapter. Reconnect still receives a fresh ParticipantId. |
| Lobby create/join | The existing platform/transport ownership split correctly treats a lobby as discovery, not admission or gameplay transport. | The canonical type is Steam-named, the host request has a Steam enum branch, and join resolution/transport opening was not ordered. | Use optional `SessionDirectory` beside a transport registered under the same `ProviderId`. A `DIRECTORY` target resolves through correlated `directory.join`/`join_ready` to a `TRANSPORT_READY` target before transport open. It never admits a player; ENet registers no directory. |
| Friend invite, rich-presence join, launch arguments | Existing `join_requested(JoinTarget)` enters the common join/cancel/confirm-leave flow and keeps one pending invite. | Source is not represented, and parsing rules are implicit. Raw lobby IDs or command-line text could leak into UI/session code. | Directory parses provider payloads strictly and emits `ExternalJoinRequest {target, source}` where source is invite, rich presence, or launch. Target remains opaque, bounded, provider-tagged, and generation-scoped. |
| SteamNetworkingMessages | It can address message channels but uses implicit sessions and exposes less explicit connection/open/close state. | The common contract requires a Godot `MultiplayerPeer`, four independent logical streams, host-loss callbacks, operation correlation, and safe close/reuse. The inspected API evidence does not establish that fit. | Do not expose Messages in gameplay or session APIs. A future adapter may use it only if it implements the same transport, lifecycle, bounds, and peer contract. Current evidence makes Sockets the smaller prospective fit, not a selected implementation. |
| SteamNetworkingSockets | P2P listen/connect, connection handles, callbacks, lanes, diagnostics, and relay routing map naturally to Transport. | No inspected peer currently satisfies all required modes, metadata, ownership, bounds, and cancellation rules. | Keep the native API private. A later adapter must produce the standard `MultiplayerPeer`, `ConnectionToken` callbacks, checked close result, and fixed stream profile. No raw socket handle crosses the boundary. |
| Channels and Sockets lanes | Replication already owns channels 0–3: reliable session, reliable state, ordered-unreliable held input, and ordered-unreliable movement. | `channel_count` plus booleans cannot detect aliasing, reliable fallback, or per-lane logical limits. A lane number is not an application acknowledgement. | `TransportCapabilities.streams` describes every channel's delivery and queue policy. The adapter maps logical channels to native lanes and implements ordered-unreliable filtering when native unreliable is unordered. Replication retains SessionId/revision/per-entity freshness and subset revisit rules. |
| Reliable delivery | Channels 0/1 already own complete admission/durable transactions. | A native queued result is not delivery, and shared native pressure can still reject a send. | Capability/profile requires `RELIABLE_ORDERED`. Adapter failures are explicit; accepted durable work cannot be silently dropped or converted to another stream. Existing bounded owner backpressure/close policy remains authoritative. |
| Unreliable delivery | Channels 2/3 are replaceable and already lossy by contract. | Existing prose can be misread as expecting one unreliable send to produce a result. Native unordered delivery also does not itself implement Godot's ordered-unreliable semantics. | Require `UNRELIABLE_ORDERED` logically, with loss and sequence gaps permitted. Adapter discards late/duplicate native messages per connection generation and channel. Replication republishes relevant movement subsets; callers never wait indefinitely for one send. |
| `NoDelay` / drop-if-congested | Suitable only as an adapter scheduling choice for replaceable traffic. | It is not a delivery guarantee, maximum queue-age guarantee, or valid substitute for reliable state. A dropped native submission must not be reported as durable success. | Record `queue_policy: REPLACEABLE_LOSSY` for channels 2/3. Adapter may use no-delay internally and reports bounded diagnostics/counters; Session/Replication semantics do not change. Channels 0/1 never use this policy. |
| Native and logical message sizes | Existing application limits distinguish 1200-byte motion/input, 4096-byte actions, and 16 KiB chunks/batches. | The current capability shape does not bind tested logical limits by stream. Valve's 512 KiB ceiling is not an MTU, predecoder bound, or production budget. | Capabilities report `max_logical_payload_bytes` per logical stream and `max_receive_packet_bytes`, including audited peer framing. Provider readiness fails if it cannot meet the required profile. Replication retains all stricter codec/rate/queue limits. |
| Connection-state callbacks | Session already correlates provider signals with OperationId and closes stale results. | Native callbacks may be queued with old userdata, handles may be reused, and `closed(operation_id)` does not state whether reuse is safe. | All connection callbacks carry an opaque generation-scoped token. `closed(operation_id, CloseResult)` reports `SAFE` or `UNAVAILABLE`; unsafe late work remains cleanup-only and cannot attach to a new operation. ENet can report safe after local peer close; future providers must prove their own retirement policy. |
| Relay / SDR | Route selection belongs to transport diagnostics and cannot affect authority/admission. | Relay initialization, a lobby, or a generic “relayed” flag does not prove actual SDR gameplay traffic. | Optional bounded `connection_diagnostics(token)` reports `DIRECT`, `RELAY`, or `UNKNOWN` plus provider-local detail. It is observability only. The handshake and admission still decide gameplay readiness. |
| Steam auth tickets | Provider authentication belongs at the native boundary; admission still belongs to SessionService and Match. | Auth tickets are often confused with P2P identity or treated as automatic lobby admission. This project has no selected backend ticket-validation requirement. | Add no ticket API to gameplay/session. A future Steam adapter must authenticate the expected account through its selected transport. If backend ticket validation is later selected, implement it inside the provider and expose only `identity_assurance` capability/readiness, never ticket bytes. |

## M1-A1 contract delta

The canonical contract now uses these provider-neutral shapes. They are contract notation; concrete
GDScript types may be smaller while preserving the same information and ownership.

```text
ProviderId = stable namespaced identifier; M1 initially registers only &"enet"
ConnectionToken = opaque, adapter-generated, non-reused across adapter/connection generations
JoinTarget = opaque {provider_id, adapter_generation,
                     kind: TRANSPORT_READY | DIRECTORY, local_handle}
ExternalJoinRequest = {target: JoinTarget,
                       source: INVITE | RICH_PRESENCE | LAUNCH}

HostRequest = {provider_id: ProviderId, district_id, capacity: 1..4,
               provider_options}

Transport.provider_id() -> ProviderId
Transport.capabilities() -> TransportCapabilities
Transport.open_host(operation_id, provider_options) -> Result<void>
Transport.open_client(operation_id, target: JoinTarget) -> Result<void>
Transport.close(operation_id) -> Result<void>
Transport.connection_diagnostics(connection: ConnectionToken)
    -> Result<BoundedTransportDiagnostics>
signals:
  peer_ready(operation_id, peer: MultiplayerPeer)
  connected(operation_id, connection: ConnectionToken, native_peer_id: int)
  disconnected(operation_id, connection: ConnectionToken, failure: Failure)
  failed(operation_id, failure: Failure)
  closed(operation_id, result: CloseResult)

SessionDirectory.provider_id() -> ProviderId
SessionDirectory.capabilities() -> DirectoryCapabilities
SessionDirectory.create_joinable(operation_id, capacity) -> Result<void>
SessionDirectory.join(operation_id, target: JoinTarget) -> Result<void>
SessionDirectory.close(operation_id) -> Result<void>
signals:
  host_ready(operation_id, published_target: JoinTarget)
  join_ready(operation_id, transport_target: JoinTarget)
  failed(operation_id, failure: Failure)
  closed(operation_id, result: CloseResult)
  join_requested(request: ExternalJoinRequest)
```

`TransportCapabilities` includes availability/failure, `identity_assurance: NONE |
PROVIDER_AUTHENTICATED`, the exact four logical stream rows, maximum logical payload per row,
maximum received packet bytes, and optional route diagnostics. ENet uses `NONE`; a future
account-targeted adapter emits `connected` only after authenticating its expected provider identity.
Each stream row is `{channel, delivery, queue_policy, max_logical_payload_bytes}`. The M1 profile is:

| Channel | Delivery | Queue policy | Existing logical ceiling |
| --- | --- | --- | --- |
| 0 | `RELIABLE_ORDERED` | `DURABLE` | 4096 bytes for actions; smaller control messages remain codec-bounded |
| 1 | `RELIABLE_ORDERED` | `DURABLE` | 16 KiB complete transaction/chunk |
| 2 | `UNRELIABLE_ORDERED` | `REPLACEABLE_LOSSY` | 1200 bytes |
| 3 | `UNRELIABLE_ORDERED` | `REPLACEABLE_LOSSY` | 1200 bytes |

These are application ceilings, not newly tested transport maxima. Provider-specific framing must
fit beneath the adapter's independently verified receive bound. `CloseResult = {reuse_status:
SAFE | UNAVAILABLE, failure?}` concerns adapter reuse after local cleanup; it does not claim every
remote/native callback queue was globally drained. SessionService completes at the shared five-second
deadline even if a component is silent, assigning it a forced `UNAVAILABLE`/`CLEANUP_TIMEOUT` result.
A provider binding is reusable only after both its transport and optional directory actually report
`SAFE` before that deadline.

Boot composes a fixed table of provider bindings before SessionService accepts operations. A binding
contains one Transport and zero or one matching SessionDirectory. SessionService resolves
`HostRequest.provider_id` or `JoinTarget.provider_id`; unregistered/unavailable providers return
`SERVICE_UNAVAILABLE`. Provider registration is not a gameplay extension point and cannot change
while a session is active or closing.

## Ownership walkthrough

### Host

For M1, Boot resolves `&"enet"`, SessionService opens ENet, and the ENet adapter applies the pinned
engine bandwidth workaround before `peer_ready`. There is no directory and no Steam initialization.
A future directory-backed provider first creates a transport endpoint, then calls
`create_joinable`; `host_ready` returns a publishable `DIRECTORY` target only when the endpoint is
ready. SessionService cleans both resources if either side fails. Host cleanup reverses acquisition:
it closes the published directory binding before the transport endpoint. A lobby member never
becomes a roster participant from directory state.

### Join and identity

ENet UI calls its adapter-local endpoint parser and receives an opaque `TRANSPORT_READY` target,
which SessionService opens directly. A future platform callback validates provider data inside
SessionDirectory and emits one external request containing a `DIRECTORY` target. SessionService
correlates the current OperationId, calls `directory.join`, and waits for `join_ready`. It verifies
that the result is a `TRANSPORT_READY` target for the same provider and current adapter generation
before opening Transport. Directory readiness alone cannot negotiate or admit gameplay.

Cancel/failure invalidates the operation and targets first. If transport opened, the client detaches
and invokes its close before closing the directory request/membership, reversing acquisition order.
All acquired components share the one five-second operation close deadline. A late `join_ready` is
cleanup-only and never opens transport. SessionService completes once after all components report or
the deadline expires. At expiry every non-reporter receives a forced
`UNAVAILABLE`/`CLEANUP_TIMEOUT` result and retains cleanup-only ownership; aggregate reuse is `SAFE`
only if every component actually reported safe before expiry. It then maps `(operation_id,
ConnectionToken, native_peer_id)` only while current. The application handshake, compatibility
checks, hydration, and handoff allocate ParticipantId and open input. Account identity, directory
membership and transport connection alone cannot do so.

### Replication

Replication continues using the four fixed high-level RPC channels and never calls Steam APIs.
Transport capabilities are checked before the session becomes ready. Provider mapping may use ENet
channels or future native lanes/filtering, but it cannot alias a channel, convert ordered-unreliable
to reliable, route raw bytes around RPC endpoints, or change durable/movement ownership. The ENet
bandwidth-defect workaround remains entirely inside `ENetTransport`. Unreliable held input and
movement remain lossy even on perfect loopback; expiry, redundant input frames, per-entity freshness,
and periodic subset refresh provide recovery.

### Close and late callbacks

SessionService invalidates targets, producer access, mappings, and the attached peer before invoking
acquired transport/directory closes in reverse acquisition order. Signals with an old OperationId or
ConnectionToken are cleanup-only. It returns to the local idle/menu state after every component
reports or the shared five-second deadline expires, whichever comes first. Deadline expiry forces an
`UNAVAILABLE`/`CLEANUP_TIMEOUT` result for each non-reporter, preserves cleanup-only late-callback
ownership and cannot emit a second completion. That provider cannot start another operation until its
own proven safe-reuse condition or process restart. This preserves ENet/Standalone availability
without inventing a Steam callback-drain timer.

## What is deliberately not added

- No Steam SDK, GodotSteam update/fork, native bridge, platform package, or runtime probe.
- No account/lobby/auth-ticket fields in gameplay records, wire envelopes, or roster identity.
- No general message bus, transport-specific replication codec, reliable fallback, or fifth lane.
- No promise that SteamNetworkingMessages, the inspected Sockets peer, relay, or SDR conforms.
- No Steam acceptance criterion in this phase. Future adapter implementation must supply its own
  native delivery, lifecycle, bounds, exports, route, and authorized-account evidence.

## Acceptance and residual gaps

This review accepts only the abstraction shape: an ENet-only M1-A1 can be implemented without
hard-coding Steam, and a later conforming provider can be composed without editing gameplay. The
following remain future adapter decisions/evidence:

- exact native implementation/pin and Godot peer framing overhead;
- lane configuration, ordered-unreliable metadata/filtering, send ownership/results, and bounds;
- authenticated identity and callback/handle retirement under cancel/retry;
- lobby/invite/rich-presence/launch parsing against the selected platform integration;
- route/relay observations, packaging, external networks, accounts, and supported targets.

The accepted S03-S source records show why these cannot be inferred from API presence. Keeping a
future provider unavailable is the required behavior until all mandatory capabilities and safe reuse
are demonstrated.

## Validation

The [retained evidence](s03-s-abstraction-review-evidence/README.md) records the pinned engine
version, documentation/link/whitespace checks, repository Python tests and all-owned script checks.
The only lint diagnostics are the three accepted pre-existing S07-driver warnings; formatting and
compilation pass. Direct Markdown editing was used because the Godot editor was not running. No
Steam, network, native, editor, export or gameplay test was run or inferred.
