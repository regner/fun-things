# S03-S — Valve public APIs and a minimal native/interface proposal

8 October 2026. **Research and interface design only; no peer implemented or
integration selected.** Base/contract revision:
`233493abc7d2e3c106fb620105cfb766f542813b`. The latest requirement is:

> The Steam integration work should focus on understanding what APIs are provided by Valve so that we can work towards building an appropriate interface. Beyond that lets leave the actual Steam testing until a later time.

The [complete task/authority](s03-s-valve-api-evidence/requirements.txt) and
[evidence index](s03-s-valve-api-evidence/README.md) retain scope and provenance.
Canonical [API](../api-contracts.md), [ownership](../architecture.md),
[multiplayer](../multiplayer.md), [scene paths](../scene-structure.md) and
[ratified brief](../design.md) are **read-only inputs**. All signatures, new native
budgets and guide changes below are proposals, not ratifications. Full S03-S,
Steam/Deck, P0-GATE and M1 gates remain OPEN. Actual Steam testing is postponed;
no accounts, access, SDK or devices are requested now.

The accepted immutable upstream assessment is
**`57d337312bb6f98a22e8d94a41eace3b9e7cc50b`**:
[record](s03-s-upstream-peer-evidence.md) and
`git notes --ref=paseo-orchestration show 57d337312bb6f98a22e8d94a41eace3b9e7cc50b`.
Its three inspected peers do not meet the unchanged contract. No peer search,
registration, finite model or earlier probe was repeated here.

## 1. Evidence and exact applicability

One public retrieval pass used Valve's Steamworks documentation and immutable
public GameNetworkingSockets (GNS) revision
**[`d534c19aa760df3fb75fd20db13ba1932b8a5463`](https://github.com/ValveSoftware/GameNetworkingSockets/commit/d534c19aa760df3fb75fd20db13ba1932b8a5463)**,
matching the prior API context, not a newly selected pin. The
[source manifest](s03-s-valve-api-evidence/sources.json) records retrieval UTC on
**2026-10-08**, URL, full original byte length/SHA-256, excerpt line ranges and
separate stored-byte hashes. Original HTML hashes identify fetched bytes, not a
stable documentation version. Doc excerpts are explicitly reproducible **parsed
text**, not literal HTML; immutable header excerpts preserve numbered source lines.
Prior Sockets/types originals were verified locally against accepted hashes, not
refetched. Their earlier excerpts remain linked rather than copied recursively.

| Key | Authoritative locator / signatures needed here |
| --- | --- |
| **S** | [Valve Sockets docs](https://partner.steamgames.com/doc/api/ISteamNetworkingSockets), [immutable header](https://github.com/ValveSoftware/GameNetworkingSockets/blob/d534c19aa760df3fb75fd20db13ba1932b8a5463/include/steam/isteamnetworkingsockets.h): P2P create/connect/accept 91–168; close/userdata 170–219; send/receive 234–354; diagnostics 361–384; lanes 419–486; auth/poll groups 489–582; callback dispatch 818–825; status callbacks 983–1053. Earlier send/lane/close excerpts are in the accepted [manifest](s03-s-upstream-peer-evidence/sources.json). |
| **T** | [Valve types docs](https://partner.steamgames.com/doc/api/steamnetworkingtypes), [immutable types header](https://github.com/ValveSoftware/GameNetworkingSockets/blob/d534c19aa760df3fb75fd20db13ba1932b8a5463/include/steam/steamnetworkingtypes.h): info/status 660–833; message fields 840–950; flags 956–1029; native bounds 1153–1198; creation userdata 1200–1233. |
| **M** | [Valve Messages docs](https://partner.steamgames.com/doc/api/ISteamNetworkingMessages), [immutable header](https://github.com/ValveSoftware/GameNetworkingSockets/blob/d534c19aa760df3fb75fd20db13ba1932b8a5463/include/steam/isteamnetworkingmessages.h): UDP-like implicit sessions, channel send/receive, accept/close, failure callbacks. |
| **U** | [Valve Networking Utils docs](https://partner.steamgames.com/doc/api/ISteamNetworkingUtils), [immutable header](https://github.com/ValveSoftware/GameNetworkingSockets/blob/d534c19aa760df3fb75fd20db13ba1932b8a5463/include/steam/isteamnetworkingutils.h): `AllocateMessage(int)` 26–41, relay readiness 51–81, config set/get 295–323. Distinct from **ISteamUtils**. |
| **L** | [Valve Matchmaking docs](https://partner.steamgames.com/doc/api/ISteamMatchmaking): `SteamAPICall_t CreateLobby(ELobbyType,int)`, `JoinLobby(CSteamID)`, `void LeaveLobby(CSteamID)`, owner/member/data/joinability APIs; `LobbyCreated_t`, `LobbyEnter_t`, `LobbyChatUpdate_t`, `LobbyDataUpdate_t`. Stored parsed-text locators accompany each signature. |
| **C** | [Valve SDK API guide](https://partner.steamgames.com/doc/sdk/api) sections Initialization, Callbacks, CallResults, Manual Callback Dispatch, Flat interface; [ISteamUtils](https://partner.steamgames.com/doc/api/ISteamUtils) `IsAPICallCompleted`, `GetAPICallResult`, `GetAPICallFailureReason`; [Friends](https://partner.steamgames.com/doc/api/ISteamFriends) `GameLobbyJoinRequested_t` and `GameRichPresenceJoinRequested_t`. |
| **R** | [Valve SDR guide](https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay) General requirements / P2P; immutable GNS [README](https://github.com/ValveSoftware/GameNetworkingSockets/blob/d534c19aa760df3fb75fd20db13ba1932b8a5463/README.md) API overview / Why Steam names; immutable `steam_api_common.h` explicitly says its public version is a callback **stub**. |

For example, complete S header SHA-256 is
`c45ace6be66d40731e670a44339951effc3e6fc4c22e0e2351f1c5205452611f` (60,197 bytes);
T is `638fc97a7f59a7baf60c465a1d68b4a836f3aebbad0fc5945ec2251dc6012925`
(97,804 bytes). All additional exact hashes, signatures/excerpts and readback checks
are adjacent; these are **public-source facts**, not SDK-1.65/runtime conformance.

The [preparation](s03-s.md) ties installed GodotSteam **4.23** bytes to a release
labeled Steamworks **1.65**, and records Linux debug registration on pinned Godot
**4.8.dev7.official.c971f93e7**. The [stopped compatibility record](s03-s-compatibility.md)
and [criteria](s03-s-compatibility-evidence/criteria.md) identify missing wrapper
lanes, unsafe batch ownership, unchecked results, modes/bounds/correlation. Nothing
here changes those installed bytes or proves these public headers match their ABI.
Steam interfaces are also provided/versioned by the running Steam client (**C**),
not solely by a checked-in redistributable. Public GNS interface-version strings
are not SDK-1.65 signatures. Exact authorized SDK declarations, exports, binding
layout and client/runtime behavior remain implementation prerequisites.

GNS supplies portable transport, encryption, lanes and custom-signaling P2P.
Its README explicitly separates **Steam authentication, Steam signaling and SDR**,
which are additional Steamworks services; the public source does not grant SDR
access (**R**). It also does not supply Steamworks lobbies/friends. Shipping GNS
alone cannot satisfy Steam friends across networks. Steam P2P Sockets is the
appropriate proposed surface for that future proof, not an SDR promise or a
selected library/fork. No restricted SDK was acquired.

## 2. Surfaces selected for the proposal (not integration selection)

| Surface | Fit to this project's requirements / deliberate exclusion |
| --- | --- |
| **ISteamNetworkingSockets** | Explicit `CreateListenSocketP2P`, `ConnectP2P`, `AcceptConnection`, connection-state callbacks and handles match host/client/cancel/loss. Lanes and poll/receipt metadata support the four streams. Use one host↔client connection per remote participant; no lobby mesh or symmetric-connect topology. |
| **ISteamNetworkingMessages** | `SendMessageToUser(identity,bytes,size,flags,channel)` copies into an implicit session; `ReceiveMessagesOnChannel` returns release-owned messages. Same-channel reliable order exists, but unreliable may reorder/duplicate. Channels are routing identifiers, not an exposed `ConfigureConnectionLanes` control. Sending implicitly accepts; there is no successful-connect notification and no proactive-close/inactivity callback (M). This requires extra session/host-loss machinery and exposes less lifetime control. Not the smallest fit, despite superficially convenient channel arguments. |
| **ISteamNetworkingUtils** | Needed for native owned message allocation, configuration/readback, relay readiness and bounded diagnostics; not gameplay state or admission. |
| **ISteamMatchmaking / Friends** | SteamPlatform creates/joins/leaves a friends lobby; obtains host account plus validated metadata; feeds invites/launch joins to the existing SessionService flow. Lobby data is discovery/compatibility hint, not authoritative gameplay or transport. No lobby chat gameplay codec. |
| **ISteamUtils / Steam callback dispatcher** | Preserve native `SteamAPICall_t` correlation, result type, I/O failure and provider error. One callback-dispatch owner shared by platform/transport, not two independent pumps racing for events. |
| **Deferred surfaces** | Legacy ISteamNetworking/P2P packets, FakeIP/FakeUDP, hosted dedicated-server tickets/coordinator, production matchmaking, stores/cloud/inventory and Web API are unnecessary here. SDR P2P needs neither a dedicated-server backend nor invented ticket service. ENet remains independent. |

## 3. Packet primitives: guarantees versus our responsibilities

### Lanes, modes and numbers

**Valve guarantee (S/T):** one default outbound lane; checked
`ConfigureConnectionLanes(conn,4,priorities,weights)` enables indices **0..3**.
Each direction configures its own outbound lanes. Weights are positive uint16;
lower numeric priority precedes higher. Same-lane reliable messages arrive in send
order if delivered. There is **no** unreliable or cross-lane receive-order guarantee.
Each lane starts native message numbers at 1 and advances independently. A number
is neither packet/fragment ID, gameplay acknowledgement nor a process/session ID.

**Proposed peer responsibility:** use these roles on every connection:

| Native lane / Godot channel | Peer mode / rule |
| --- | --- |
| 0 | RELIABLE: session/admission/discrete action requests |
| 1 | RELIABLE: baseline/durable/action results/live events |
| 2 | UNRELIABLE_ORDERED: held intent; native plain unreliable, no retransmission |
| 3 | UNRELIABLE_ORDERED: movement subsets; native plain unreliable, separate watermark |

Send via `AllocateMessage(size)` + `SendMessages`, **setting `m_idxLane`**. The
convenience `SendMessageToConnection` has no lane parameter. Validate lane/config
results; never alias an invalid channel to 0, add a fifth lane to mask a bug, or
substitute reliable for ordered-unreliable. Initial proposed scheduling: equal
priority and positive equal weights, so baseline cannot strictly starve other lanes;
future measured tuning belongs with transport, not a global constants collection.
Lanes isolate ordering, **not congestion/send-buffer capacity**.

For 2/3 keep exactly one highest accepted native message number per
`(ConnectionToken, lane)`; discard number <= watermark, accept newer immediately,
with no reorder queue or reliable retry. Sequence gaps are allowed. Duplicates and
late packets release their native messages without reaching Godot. Reset watermark
only for a proven fresh connection generation; invalidate it before closing. T's
received flags expose only the Reliable bit; infer ordered mode from the fixed role,
not a nonexistent native ordered flag. Reject unexpected lane/reliable-bit pairing.
Validate all receipt metadata/size before allocating a Godot packet or advancing the
watermark. A malformed high number cannot admit a message; repeated abuse is a
bounded disconnect-policy prerequisite.

This is a **fixed S03 stream profile**, not a general peer claim about all
channel×mode combinations. Unsupported combinations must fail explicitly. Godot
channel-0 mode separation and any internal peer-control packets require an exact
engine/peer API audit before implementation: if required beyond this profile,
commission the minimal explicit lane/mode mapping or framing delta and acceptance,
not silent channel aliasing. Fixed roles need no application sequence header merely
to replace native lane numbers. The native boundary still returns raw flags/number
so a later explicit mapping cannot erase metadata.

**Application owner unchanged:** Replication separately checks SessionId,
MatchRevision, EntityRef/generation/life/control/collision dependencies, freshness
per entity and the provisional **250 ms every-subset revisit**. A newer packet
says nothing about omitted entities. Native numbers must never drive simulation
steps or replace consumed/superseded held sequence acknowledgement. Durable state
retains one reliable writer; high-level Godot RPC stays at the saved endpoints.

### Allocation, ownership and send errors

**Valve contract (U/S/T):** `AllocateMessage(n)` supplies a native payload of at
least n bytes. Fill copied bytes and only documented send fields (`m_conn`,
`m_nFlags`, `m_idxLane`); do not point at Variant or transient Godot memory, release
before send, or allocate a message struct on the stack. No custom free callback is
needed for this small boundary. Custom buffers would require fast thread-safe
release, potentially even before SendMessages returns; avoid that extra lifetime.

Use **one message per native submission**, always supply the result slot, and
`bDeleteFailedMessages=false`. Positive result is a queued native message number:
the successful pointer is nulled and library-owned; never touch/release it again.
Negative result is `-EResult`; the surviving caller-owned pointer must be released
once. Zero means unattempted (possible in a larger batch after an earlier failure),
not success; release it too. Local allocation/validation failure releases anything
already acquired. The proposed `send` consumes neither the caller's source array
nor external ownership: copy synchronously and resolve all native ownership before
return. RAII guards cover early failures and every receive/drop/close path.

| Native result (S) | Proposed visible handling, never false success |
| --- | --- |
| Positive number / OK | `QUEUED(number)` only; does not prove delivery or application acknowledgement. |
| `Ignored` with NoDelay | `DROPPED(NO_DELAY)` for unreliable only; count observed loss, no queue/retry. NoDelay is invalid for reliable and does **not** promise a backlog-age limit (T 995–1013). |
| `LimitExceeded` | `REJECTED(STATE_LIMIT, retryable as explicitly decided)`; no unbounded retry list. Replace/drop obsolete unreliable work. A reliable RPC that cannot be queued must fail/close or use bounded owner backpressure before acceptance; never silently omit part of a durable transaction. |
| `InvalidParam` | `REJECTED(UNSUPPORTED/STATE_LIMIT)` after local lane/size checks; retain native code, investigate bad handle/oversize rather than guessing success. |
| `InvalidState` / `NoConnection` | Stop send, normalize `CONNECT_FAILED` (or `HOST_LOST` for established host loss), invalidate binding and close. |
| Zero / unknown negative / allocation failure | Explicit unattempted/provider/allocation failure; no message-number output, deterministic release, retain native diagnostics. |

Configuration errors are similarly terminal before readiness. Godot `_put_packet`
must map QUEUED to OK only; dropped/rejected outcomes need an explicit Error
(e.g. busy/unavailable/invalid parameter) and transport diagnostics. Exact Godot
Error mapping/RPC caller reaction is a subsequent implementation audit, not proof
that high-level RPC retries. Do not add another reliable protocol to compensate.

### Receive and work bounds

**Valve contract (S/T):** `ReceiveMessagesOnConnection(conn,out,max_count)` returns
0..max_count or -1 for invalid handle; poll groups return interleaved connections
with the same within-connection guarantees. Read `m_conn`, `m_identityPeer`,
`m_nConnUserData`, `m_idxLane`, `m_nMessageNumber`, Reliable bit, `m_cbSize` and
`m_usecTimeReceived`. Sockets lane is **not** Messages' `m_nChannel`. Release every
returned object, including invalid/duplicate/oversize messages and unprocessed
members of an early-aborted batch. Returned receive buffers are already allocated;
script-level length checks cannot undo that native allocation.

**Proposed boundary:** explicit checked/read-back native `RecvMaxMessageSize`,
`RecvBufferSize`, `RecvBufferMessages`, `SendBufferSize`, and appropriate initial/
connected timeouts, inherited on listen sockets before incoming connection setup.
U `SetConfigValue` returns bool; `GetConfigValue` returns a typed result and byte
size. Check types, values and inherited/effective settings, not just API presence.
T says receive-buffer overflow drops packets; max-message overflow closes the
connection. These are controls, **not** a total-memory or flood-conformance proof.
Reassembly/segment/handshake allocations and library callback queues remain unknown.
`RecvMaxSegmentsPerPacket` is another public defense, not a measured byte guarantee.
The public 512 KiB send ceiling is neither our budget, safe MTU nor Godot limit.

Preserve all canonical provisional logical limits: **1200-byte held/motion,
4096-byte actions, 16 KiB reliable transaction batches/chunks, 1 MiB/128-chunk
baseline, 2 MiB/4096-record join journal**, plus their existing rates/queues/work,
identity/deadline checks. They are not newly tested maxima. Peer packets include
Godot/peer framing: first bound/audit overhead **H**; set native max **W=16 KiB+H**,
then enforce stream-specific logical caps **before Godot decoding**. No ready
capability until H, framing validation and actual native applicability are known.

Additional **unratified starting native/peer limits** for a bounded implementation
commission: native pending send 256 KiB/connection; native received queue
256 KiB/128 messages per connection (must exceed W); peer retained receive queue
256 KiB/128 packets per connection, total 768 KiB/384 for three remotes; poll at
most 32 receipts and 64 KiB returned/copied bytes aggregate. Receive in round-robin
connection order with requested count bounded by both remaining count and
`floor(remaining_byte_budget/W)`; W must fit that poll budget. This small fixed
three-remote topology does not need a poll group. Queue overflow drops replaceable
unreliable traffic or fails the affected reliable stream/connection; no truncated
transaction, partial decoder call or unbounded backlog. All retained bytes have a
single native/peer owner and are counted until their release.

Proposed normalized event queue/pump cap is 64 events. It bounds boundary output,
**not** `SteamAPI_RunCallbacks` internal work: that function has no count/deadline
parameter. Manual dispatch is documented (C), but its exact pinned declarations,
result retrieval/free-last-callback ownership and cooperation with the existing
addon pump must be audited before promising a bounded native dispatcher. Use one
pump, finite per-request cleanup slots, coalesced advisory diagnostics, terminal
cleanup priority and explicit unavailable-on-overflow. Never discard a resource-
creating completion just to meet a callback quota. Native queue memory/CPU under
untrusted pre-accept traffic remains a future validation gate, not covered by these
local caps. No callback sleeps or loading phase may stall incoming accept/close.

## 4. Identity, pending capacity, diagnostics and host loss

**Valve facts (S/T/R):** connection callbacks identify handle/listen socket, identity,
old/new state and end reason. `InitAuthentication`/`GetAuthenticationStatus` concern
local certificate readiness; `GetIdentity` may return a SteamID even when not signed
in. An identity value alone is not successful peer authentication. Connection info
flags expose unauthenticated/unencrypted status; require the Steam path to authenticate
its expected remote SteamID. Never enable unauthenticated/unencrypted development
fallback to make availability look successful. Public GNS encryption alone cannot
prove a Steam account is authenticated.

**Transport responsibility:** bind opaque account target to authenticated connection
identity, reject mismatch, and allocate a fresh opaque ConnectionToken/generation.
Keep native handle/account maps adapter-private. Host is Godot peer **1**; remote
peer IDs are unique for this active transport generation and cannot be chosen by an
untrusted packet. A star topology does not create client↔client mesh authority.
SessionService alone maps native peer to fresh ParticipantId after the existing
compatibility/hydration/handoff. Match alone owns gameplay entities/outcomes.

Reserve each of at most **three remote slots**, including connecting/negotiating/
loading/synchronizing peers, before `AcceptConnection`; reject/close excess, duplicate
account connections and attempts while closing. A native incoming callback must be
accepted or closed promptly (Valve recommends within a second or two), even during
loading; check `AcceptConnection` result and free any terminal connection locally.
Lobby member limit 4 is discovery capacity, **not** this reservation/admission lock.
A connection object can be allocated by Valve before our callback: the public
surface inspected does not establish a hard global pending-native-connection cap.
Do not certify native flood/allocation safety from the four-player application cap.

**Diagnostics, bounded/local only:** retain connection state/auth flags/identity,
end reason/debug text, remote/relay POP, Relayed flag, ping, packet/byte rates,
quality, pending unreliable/reliable, unacked reliable and per-lane queue time.
Read status only on success; size-bound detailed text (proposed 8 KiB, mark truncation,
never retry allocate indefinitely), sanitize UI/log exposure. A Relayed flag can mean
SDR **or TURN** (T); relay readiness/POP alone is not evidence traffic used SDR.
Future external proof must record per-connection route plus actual gameplay traffic
from both ends. Relay readiness failure is actionable availability, not admission.

ClosedByPeer/ProblemDetectedLocally still require local CloseConnection (S).
Loss of the authoritative established host normalizes HOST_LOST, closes input and
ends the match via SessionService. A lobby owner transfer or membership event cannot
promote a replacement host. Lobby disappearance is advisory platform information,
not sufficient to fabricate a native host-loss observation; apply the current
session failure policy using validated connection/host binding and deadlines.

## 5. Native request/callback lifecycle

**Valve facts (L/C/S/T):** CreateLobby and JoinLobby return **SteamAPICall_t**;
create produces LobbyCreated_t call result and also a LobbyEnter_t broadcast for
joining one's own lobby. JoinLobby's correlated call result is LobbyEnter_t.
Result payload's lobby ID alone does not carry the request handle. Call results
and broadcasts are distinct, not interchangeable. A reused CCallResult object
listens only to its most recent Set(handle); replacing it can lose old cleanup
ownership. Keep a distinct native request record until retirement. I/O failure
(`bIOFailure`/`pbFailed`) is separate from LobbyCreated EResult or LobbyEnter
`m_EChatRoomEnterResponse`. ISteamUtils can query completion and typed results;
call its failure diagnostics without adopting its prose's unbounded retry advice.

LeaveLobby takes effect immediately **on the client side**, not as an acknowledged
backend leave or callback-queue drain. The inspected public contracts expose no
server-side create/join cancellation or completed global-drain guarantee. The
public GNS `steam_api_common.h` is a stub, not evidence for SDK CCallResult::Cancel
implementation. Deregistration/local cancellation is not remote cancellation;
any exact SDK Cancel behavior remains a prerequisite, not assumed here.

**Proposed platform policy:** serialize resource-producing create/join attempts;
register a request token containing native handle, expected result type and owning
OperationId **before any dispatch**, with a non-reused adapter generation. Poll or
per-handle call-result dispatch must never tag a result with the currently active
OperationId by target alone. Cancellation changes the old request to cleanup-only;
keep result observation alive. Late success leaves the created/joined lobby once,
late error retires the record without publishing readiness/failure into a new attempt.
No native result can allocate gameplay or cause transport connection outside the
owning active operation. Never reuse the old CCallResult storage prematurely.

Do **not** retry even the same lobby while its obsolete request/membership is
unresolved: LeaveLobby from the late success could leave the new attempt, since
membership is not per request. General LobbyEnter/Chat/Data broadcasts cannot
complete a request, initiate a peer or resurrect a closed binding. Treat them as
bounded advisory refresh hints only, re-query under an active correlated binding;
invites are fresh user requests converted to one pending opaque JoinTarget under
the existing cancel-and-join/confirm-leave flow. Parse `+connect_lobby` launch IDs
strictly at SteamPlatform; rich-presence strings are untrusted and only accepted
if they encode this selected lobby route. No arbitrary endpoint/executable commands.

**Connection correlation caveat:** S SetConnectionUserData explicitly warns queued
callbacks retain userdata from enqueue time; receive data gets latest userdata.
T allows atomic outbound creation cookies and inherited listen defaults, but warns
incoming state transitions can queue before the first callback. A current userdata
query does **not** prove an old callback belongs to that current attempt. Capture
outbound birth cookies before connecting; retain handle↔token/listen-generation
retirement records; never rewrite a stale callback to the current token. For inbound
callbacks, resolve the listener's generation and current handle lineage before
adopting/rejecting. Handle reuse and pre-binding queued callbacks need exact native
proof; if lineage is ambiguous, publish no state and disable reuse rather than
closing a possibly new connection by an old handle. Unknown guarantees stay unknown.

### Close, retirement and reuse contract

1. On cancel/leave/failure, SessionService enters CLOSING. Invalidate producer access,
   peer/account mappings and targets first; stop admission/input/publication; detach
   Godot peer and release its current/queued packets/watermarks. Match cleanup keeps
   its existing owner/rollback sequence. No new host/join is accepted while closing.
2. Close known connecting, route-finding **and connected** handles with linger=false;
   check close/listener-close results, release local queues and slots. CloseConnection
   invalidates handle and discards unread data. Linger=true merely attempts to flush
   sent data, does not acknowledge application delivery or drain callbacks. No
   graceful reliable goodbye is required for cancel; any future graceful leave has
   a separate bounded wait before the same local close, never a drain assertion.
3. Retire native requests and callback registrations into process-lifetime,
   cleanup-only ownership. A canceled create/join that completes late is still
   observed and left. Retired callbacks cannot call a freed Node or live UI/Match.
   Keep at most one unresolved platform request in this serialized proposal; do not
   accumulate attempts. Terminal connection callbacks retain only the bounded
   lineage needed to dispose safely. Quota/identity ambiguity makes Steam unavailable.
4. Within the canonical **5 s monotonic local cleanup deadline**, emit exactly one
   SessionService completion per accepted operation, including CANCELED. Deadline
   does not mean all native activity stopped. Record CLEANUP_TIMEOUT and mark Steam
   unavailable if retirement/safe reuse cannot be established; local IDLE/menu and
   ENet/Standalone stay usable. Preserve cleanup-only observation after timeout.
5. `reuse_status` may become SAFE only from exact correlated result cleanup plus a
   proven callback/handle retirement policy. An empty pump, elapsed delay, a close
   bool, zero pending send bytes or LeaveLobby return is **not** such proof. General
   advisory callbacks can be harmless without claiming they are drained; any
   uncorrelated resource-changing path requires serialized documented retirement.
   Default to UNAVAILABLE until that policy is demonstrated, or process restart.
   Unregister/release final native dispatch resources only after they can no longer
   require cleanup; normal process shutdown owns SteamAPI_Shutdown, not session leave.

## 6. Small proposed interface shape

Contract notation only, adapter-private; **not** a generic networking framework or
new gameplay API. The native bridge can be internal to a narrow GDExtension peer/
SteamPlatform implementation. It need not expose native pointers to GDScript.
Existing Transport/SteamPlatform signatures and their signals remain unchanged.

```text
ConnectionToken = opaque {adapter_generation, connection_generation}
RequestToken = opaque {adapter_generation, request_serial}
NativeFailure = {normalized_code, phase, retryable, native_code?, diagnostic_id}
SendOutcome = QUEUED {native_number} | DROPPED {reason} | REJECTED {NativeFailure}
ReceivedPacket = {connection_token, identity_binding, lane, reliable_bit,
                  native_number, receive_time_us, owned_bytes}
NativeEvent = ConnectionState(token, snapshot, birth_cookie)
            | LobbyResult(request_token, operation_id, expected_type, io_failure,
                          result_code, lobby_binding?)
            | AdvisoryLobbyChange(binding) | JoinRequested(opaque_target)
CloseProgress = {local_resources_released, unresolved_cleanup_count,
                 reuse_status: PENDING | SAFE | UNAVAILABLE, failure?}

# Only after explicitly requested optional Steam initialization; absent = unavailable.
Native.open_listen(operation_id, virtual_port, checked_bounds) -> Result<ListenToken>
Native.connect(operation_id, target_binding, virtual_port, checked_bounds)
    -> Result<ConnectionToken>
Native.accept(connection_token, reservation_token) -> Result<void>
Native.configure_lanes(connection_token, priorities[4], positive_weights[4])
    -> Result<void>  # check each direction before ready; no implicit channel default
Native.send(connection_token, lane: 0..3, delivery: RELIABLE | UNRELIABLE,
            bytes: borrowed_readonly, scheduling_flags) -> SendOutcome
Native.receive(connection_token, max_messages, max_bytes) -> Result<OwnedPacketBatch>
Native.diagnostics(connection_token) -> Result<BoundedRouteAndLaneStatus>
Native.close_connection(connection_token, reason, linger=false) -> Result<void>
Native.close_listen(listen_token) -> Result<void>

Native.create_lobby(operation_id, capacity: 1..4) -> Result<RequestToken>
Native.join_lobby(operation_id, target_binding) -> Result<RequestToken>
Native.retire_request(request_token) -> Result<void>  # logical cancel, observe cleanup
Native.leave_lobby(lobby_binding) -> Result<void>     # local request, no drain promise
Native.pump(max_events) -> BoundedEventBatch          # exact dispatcher prerequisite
Native.close_progress(operation_id, deadline_monotonic) -> CloseProgress
```

Tokens resolve privately to native handles; no native account/lobby IDs reach
actors/Match, and no external caller constructs identity_binding. Synchronous
Result success means accepted locally, not ready/admitted. `send` copies caller
bytes, consumes native message ownership internally as above; `receive` owns copied
bytes after releasing native messages. Batch lifetime is explicit: peer takes bytes
or disposes them once, counted against queue caps. No outstanding native message
pointer escapes to a Node or the Godot packet decoder. The Godot next-packet view
stays valid until the peer advances/disposes it, with peer/channel/mode getters all
referring to that same packet. Broadcast send returns per-recipient outcomes to the
transport; aggregate success must not hide a failed child send.

The proposed peer supplies the exact pinned MultiplayerPeerExtension packet,
metadata, send target/channel/mode, ID/status, poll, close/refuse-new-connections
and lifecycle signal contract, reviewed against the existing reflected API before
implementation. `_poll` consumes only bounded queues. `peer_ready` means a properly
configured peer can be attached at the saved Session endpoint; native connected
means handshake can begin, not gameplay admission. No raw byte routing around
Godot high-level RPC. SessionService still completes operations/roster; Replication
still serializes gameplay; existing motion/health/seat owners retain all rules.

SteamPlatform alone owns optional init/availability, targets, lobby metadata,
friends/invites/launch parsing. Publish host readiness/joinability only after the
transport endpoint exists; client checks protocol/content and original host binding
via the application handshake, not GetLobbyOwner alone. Platform failure cleans
its lobby and transport together through SessionService. An absent/unproven bridge
reports SERVICE_UNAVAILABLE/UNSUPPORTED; startup never initializes Steam just to
run ENet or Standalone. Installing/pinning/replacing GodotSteam is a separate decision.

## 7. Bounded prerequisites and future validation (DEFERRED / UNEXECUTED)

Next **separately commissioned implementation preparation**, not execution authority:

1. Decide whether to pursue this fixed Sockets/native delta or keep Steam unavailable.
   Audit exact authorized SDK-1.65/native declarations, versions/exports, struct layout,
   source↔binary linkage and pinned Godot peer/internal packet semantics. No restricted
   download is part of this delivery; access-dependent work waits for a later grant.
2. Specify H and checked stream framing/byte bounds before Godot decode; decide/ratify
   proposed local queue/poll/native limits and reliable send failure policy without
   weakening existing streams/logical limits. Account for the brief's sustained
   bandwidth including framing; neither 512 KiB nor source API presence proves it.
3. Resolve exact request-result ownership, typed retrieval/dispatcher cooperation,
   callback quotas and inbound handle retirement/reuse. If public guarantees remain
   insufficient, retain explicit unavailable-on-unsafe-reuse; do not invent a drain
   timer. Produce a narrow change list for native peer/platform wrappers, not a new
   session/codec/replay framework. Approve any fork/build/pin separately.

Every row below is **DEFERRED / UNEXECUTED**. None ran in this research. They name
future acceptance, not accounts/access requests or a grant to build/init/test now.

| Future case | Required independent outcome / evidence |
| --- | --- |
| ABI/registration/exports | Exact engine/templates, SDK/native/export signatures and Windows/Linux dependencies; do not infer binary behavior from public GNS. |
| Lane/mode selection | Four configured lanes in both directions; correct next-packet metadata; required generic/internal Godot cases explicit; unsupported combos reject without alias/fallback. |
| Ordering/loss | 2,1,2 delivers only 2 on one ordered stream; lane2 number20 cannot discard lane3 number1; reliable0/1 independently ordered. Native message numbers do not acknowledge simulation. |
| Baseline pressure | Withhold lane1 progress while 0/2/3 continue when capacity permits; increase shared pressure, observe checked LimitExceeded, queue/work peaks, no reliable substitution or false send success. |
| Ownership/errors | Configure failure, allocation failure, all send results including zero/unattempted batch; successful native pointer never double-freed, failed/unattempted and dropped receives released exactly once; broadcast child failure visible. |
| Size/receipt/work | 1200/4096/16 KiB edges plus audited overhead; oversize/invalid metadata rejected before Godot decode; effective native receive byte/count/max/segment controls; local/native queue and per-poll bounds, malicious pre-accept/native callback flood and host stall. No decoder-only memory claim. |
| Auth/capacity/admission | Expected authenticated Steam account, no unauthenticated fallback; host+three including pending slots, excess/duplicate/reconnect attempts bounded; fresh peer/ParticipantId; compatibility, baseline/journal/handoff precede input. |
| Lifecycle | Cancel in create/join/connect/finding-route/load; late success/error; duplicate callback; same-lobby retry collision; stale/reused native handle; close versus linger; five-second local cleanup and exactly-once completion. Unsafe drain/reuse remains unavailable, ENet remains usable. |
| Host loss/invites | Established host disconnect ends match, no lobby-owner migration; one pending invite; while loading/match, confirmation/cancel-and-join through same flow; malformed launch/rich-presence targets rejected. |
| Gameplay/route | Original admitted baseline/intent and subset-refresh/durable-state expectations over actual Steam gameplay transport across separate networks, without port forwarding; per-connection diagnostics and traffic prove route, not lobby/relay readiness alone. |
| Delivery/targets | Existing app5294580/depot5294581/5294582/private fun-things route and entitlement/install/update/launch preserve VCS; Windows/Linux and Deck LCD/OLED Gaming Mode/input/suspend/native1280×800/60 FPS; ENet without Steam. |

The existing connect15 s/handshake5 s/load30 s/attempt60 s, baseline10 s/handoff5 s
and all application rate/queue/history/deadline limits remain provisional and
unchanged. Real Steam/testing, device, production and P0 proofs remain postponed/open;
a proposed interface is useful preparation towards P0, not P0 completion.

## 8. Static delivery and proposed guide deltas

Only this document, its adjacent evidence and the S03-S task/readiness cell in TODO
are changed. Suggested **later coordinated guide updates**: add the selected native
ownership/result/metadata contract once integration is chosen; document tested native
bounds/overhead, exact mode profile and proven retirement/reuse policy; update capability
and failure evidence only from that implementation. No canonical guide is edited or
silently ratified here, and no S07/S08 commission is assigned by this delivery.

Static checks cover exact scope/TODO preservation, local links, JSON/Python syntax,
source/excerpt/hash integrity and whitespace. Logs/argv/exits and full independent
review are retained under the [evidence index](s03-s-valve-api-evidence/README.md).
No Godot/Blender/editor/service/config/native build, Steam initialization/lobby/traffic,
SDK download, account/depot/device setup, vendor/pin/code/scene/asset mutation or
runtime validation occurred. Read-only retrieval completed; owned writers become
quiescent at frozen candidate/review handoff. ROOT alone integrates/archives; no push.
