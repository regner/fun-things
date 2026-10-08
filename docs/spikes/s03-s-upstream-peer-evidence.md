# S03-S — immutable upstream peer source evidence

8 October 2026. Public source investigation commissioned by ROOT under option 1 of
the [stopped compatibility record](s03-s-compatibility.md#lifecycle-limitation-and-exact-stopdecision-boundary).
Direct owner: `1a866e53-0b25-46d6-863d-107746aafb49`, GPT-6.1-Sol HIGH,
workspace `wks_4b9392e6198b3f47`, branch `s03-s-upstream-peer-evidence`.
The clean, empty branch began at `352f5706d87bee973df40c73c3fffb1ef01df72e` and
was rebased before implementation onto exact held LOCAL main
**`52941da4b4c92a547a8066b5c13f733043ecbe48`** (accepted S08).
Effective model/effort, auto-review and `plan_mode:false` were verified once;
ROOT's supplied empty-profile launch receipt was used without rediscovery.

**STOP: none of the three inspected revisions meets the unchanged four-stream
contract.** This is a bounded source assessment, not a claim that no qualifying
implementation exists elsewhere. The investigation exhausted its three-candidate
cap in one focused session within the 60–90 minute target. It selects no adapter,
pin, build or protocol. Full S03-S, Steam/Deck, P0/M1 and production gates stay OPEN.
Independent static review is pending at this frozen candidate boundary; ROOT owns
the review slot and subsequent integration.

## Requirements and evidence boundary

The complete accepted S03-S TODO block and prior option/stop boundary at the base
above remain the raw requirements. [Canonical API](../api-contracts.md),
[multiplayer](../multiplayer.md#accepted-stopped-steam-compatibility-boundary),
[accepted S03](s03.md) and [saved criteria](s03-s-compatibility-evidence/criteria.md)
own the acceptance rules. The actual S03 callers still use reliable RPC channels
0/1 and ordered-unreliable channels 2/3; no second transport contract is introduced.

| Existing stream | Required behavior |
| --- | --- |
| 0 session/admission/actions | Reliable ordered; missing baseline traffic cannot order-block this stream. |
| 1 baseline/durable/results/events | Reliable ordered; retain complete cut/journal/handoff transactions. |
| 2 held intent | Unreliable ordered: skip loss, discard late/duplicate packets, no reliable substitution. |
| 3 movement subsets | Independent unreliable ordering; application freshness remains per entity/control, with every relevant subset revisited within provisional 250 ms before loss. |

Channels do not promise separate congestion capacity or cross-channel receive order.
Godot's documented channel-0 mode separation is also relevant to a general peer;
the fixed S03 streams alone do not exercise all channel/mode combinations.
Sender authentication, admission, SessionId/MatchRevision/entity/life/control fences
and durable-state ownership remain with the existing application owners.
Four players includes the host and pending reservations. Packet/rate/queue/work/
history bounds and exactly-once operation completion still apply. Relevant logical
budgets remain provisional: 1200-byte held/motion, 4096-byte actions, 16 KiB reliable
batches/chunks, 1 MiB/128-chunk baseline, bounded journal and five-second local close.
These are not measured Steam limits, MTUs or native allocation guarantees.

Only public repository metadata, a few relevant source files and primary API
documentation were read. No native/engine/Steam/account experiment, registration,
synthetic model, SDK/binary download, build, install or maintainer contact occurred.
No editor/display/service resource was acquired. Existing source/model/registration
and dated failure records remain historical; source presence cannot pass delivery,
cancel/drain, platform/export or external-account proof.

## Exact candidates and provenance

[Candidate ledger](s03-s-upstream-peer-evidence/candidates.json) records full commit
identities, discovery refs, dates and primary metadata URLs. Branch names were only
discovery locators; all source downloads use the resolved commit. These are the
three assessed implementations, not three approved integration choices:

| ID | Immutable revision and reason to inspect | Compatibility limit |
| --- | --- | --- |
| G | [GodotSteam GDExtension `2cfe81d58d85f7a8a78cd0a19a5642d011e9c8fc`](https://codeberg.org/godotsteam/godotsteam/commit/2cfe81d58d85f7a8a78cd0a19a5642d011e9c8fc), resolved `gdextension`; commit dated 19 August 2026. Official separate GDExtension source path with Sockets lanes and a MultiplayerPeerExtension. | Different source layout from retained 4.23; not presumed newer than the installed release. `SConstruct` requests API 4.4; tree records godot-cpp `7e18e40d7591429f915035a7de7cf79457d555cc`. Neither is an ABI/export proof on pinned `4.8.dev7.official.c971f93e7`. |
| E | [Expresso `13a2e888a7159c1a145333c7ea100dfd2b6a8aa7`](https://github.com/expressobits/steam-multiplayer-peer/commit/13a2e888a7159c1a145333c7ea100dfd2b6a8aa7), resolved `main`; 4 December 2025. Independent C++ Sockets peer with explicit send-result/retry code. | README says development paused and channels absent. Tree records godot-cpp `714c9e2c165db2dcb7e6ea57e62a04204d3cfbfa`; no compatibility build or native dependency validation here. |
| C | [C# peer `a826c72e7d936c6af6a10122be1047a89e29cd36`](https://github.com/craethke/steam-multiplayer-peer-csharp/commit/a826c72e7d936c6af6a10122be1047a89e29cd36), resolved `main`; 22 January 2025. Managed MultiplayerPeerExtension over the singleton API, useful for checking whether that boundary can preserve required semantics. | README requires GodotSteam plus separate C# bindings and reports missing channels. No matching bindings revision, .NET engine, export or source/binary linkage established; not a drop-in for the current GDScript project. |

[Source manifest](s03-s-upstream-peer-evidence/sources.json) records each immutable
URL, full-source byte length and SHA-256. Candidate files also match the blob SHA-1
from their public commit-tree metadata. Small peer files are retained as exact `.txt`
snapshots; the large singleton and two Valve headers use explicitly numbered
excerpts with separate stored-byte hashes. A stored excerpt hash is never presented
as the full-source hash. Whole-source readback was checked against the downloaded
scratch files. [Retained peer diff](s03-s-upstream-peer-evidence/retained-peer-diff.txt)
compares G with the previously hashed exact `532740f3` peer/packet files;
the earlier [manifest](s03-s-compatibility-evidence/sources.json) anchors that baseline.
No new baseline experiment was run.

Primary source keys below:

- G-peer: [peer implementation](https://codeberg.org/godotsteam/godotsteam/src/commit/2cfe81d58d85f7a8a78cd0a19a5642d011e9c8fc/godotsteam/godotsteam_multiplayer_peer.cpp).
- G-packet: [packet implementation](https://codeberg.org/godotsteam/godotsteam/src/commit/2cfe81d58d85f7a8a78cd0a19a5642d011e9c8fc/godotsteam/steam_packet_peer.cpp).
- G-singleton: [singleton implementation](https://codeberg.org/godotsteam/godotsteam/src/commit/2cfe81d58d85f7a8a78cd0a19a5642d011e9c8fc/godotsteam/godotsteam.cpp).
- E-peer: [peer implementation](https://github.com/expressobits/steam-multiplayer-peer/blob/13a2e888a7159c1a145333c7ea100dfd2b6a8aa7/steam-multiplayer-peer/steam_multiplayer_peer.cpp).
- E-connection: [connection implementation](https://github.com/expressobits/steam-multiplayer-peer/blob/13a2e888a7159c1a145333c7ea100dfd2b6a8aa7/steam-multiplayer-peer/steam_connection.cpp).
- C-peer: [single managed implementation](https://github.com/craethke/steam-multiplayer-peer-csharp/blob/a826c72e7d936c6af6a10122be1047a89e29cd36/addons/steam-multiplayer-peer-csharp/SteamMultiplayerPeer.cs).

## Source-backed capability matrix

**Mismatch** means the inspected source implements conflicting behavior. **Partial**
means a useful source path exists but does not establish the complete requirement.
**Unproved** means this static scope cannot certify it. None means a runtime pass.

| Requirement | G: official GDExtension | E: Expresso | C: managed singleton peer |
| --- | --- | --- | --- |
| Godot peer and actual Steam route | Partial: required virtual declarations, packet/channel/peer getters, P2P Sockets host/client and poll group (G-peer 56–93, 479–565; header 99–132). | Partial: Sockets peer, direct host/client, next-packet getters (E-peer 19–104). | Partial: managed extension, P2P Sockets wrappers (C-peer 8, 46–84, 86–188). No registration/ABI/native route observed for any candidate. |
| Reliable 0/1, independent channels 0–3 | Mismatch at unchanged default4: lane field and receive lane exist, but channel `>= configured_lanes - 1` falls to0; requested3 aliases0 (G-packet 59–65, 85–110; settings 87–90; G-peer 74–80). | Mismatch: channel setters do nothing/getters return0; convenience send has no lane (E-peer 64–84; E-connection 7–8). | Mismatch: no-op channel setter, getters0; singleton convenience send (C-peer 159–188, 516–518). |
| Ordered-unreliable 2/3; loss/late/duplicate handling | Mismatch: ordered mode maps to reliable; receive mode only reliable/plain-unreliable, with no freshness filtering (G-peer 65–71, 120–154, 710–725). | Mismatch: ordered mode maps to reliable; receive mode only reliable/plain-unreliable (E-peer 68–76, 399–417). | Mismatch: switch supports reliable/plain-unreliable only; ordered mode takes the throwing default. ProcessMessage discards native flags/number; incoming packet defaults reliable (C-peer 293–304, 429–434, 486–502). |
| Byte ownership and checked lane/send results | Partial: allocates `p_size` and copies bytes before native send, retains/releases received messages. Configure result ignored; SendMessages result array null, failure-retained pointer unhandled, returns OK; broadcasts discard child errors (G-packet 44–50, 59–65, 85–113; G-peer 439–476). | Partial: packet owns copied fixed buffer; raw send checks EResult internally, drops failed unreliable and retains reliable. SendPending always returns OK; no bound on reliable retry list (packet cpp 9–13/header 28–31; E-connection 7–41). | Partial: managed arrays passed to singleton; native ownership depends on unpinned bindings. EResult read but SendPending always returns OK; unbounded retry list (C-peer 486–547). Native ownership safety unproved. |
| Bounded native receipt, queued bytes/messages and per-poll work | Partial: one poll caps255 returned messages, but retains them in an uncapped incoming list; no per-message logical cap, queued-byte cap or native receive configuration established (G-peer 120–154; header 60–63). | Partial:255 per connection; checks native message against512 KiB before copying into fixed packet, then uncapped incoming list. Connection count, total poll work and native limits not established (E-peer 110–131, 529–539). | Partial:255 per connection; wrapper has already materialized payload; uncapped incoming queue and no pre-wrapper byte bound (C-peer 199–220, 429–434). |
| Cancel while connecting; retire queues/mappings before retry | Partial: close force-disconnects known handles and releases incoming/current packets. Callback drain/retirement fence absent from inspected paths; tracked lobby remains, retry and lobby-entry callback paths can initiate connections (G-peer 156–205, 307–369, 371–415). | Mismatch in ordinary close path: returns early unless CONNECTED, so CONNECTING cancellation does not run force_close. force_close clears maps but not incoming packets (E-peer 153–180); active-state guard is not an attempt identity. | Mismatch: close returns early unless active and CONNECTED; does not clear incoming queue or unsubscribe constructor event handler (C-peer 40–44, 222–244). |
| Native identity/admission, capacity, host loss | Partial: Steam account↔peer helpers and close on lost peer1; native peer-ID ping is not admission. Convenience lobby mesh path needs topology assessment (G-peer 95–109, 145, 634–667, 730–750). | Partial: native account/peer maps and close/force_close host-loss paths; not admitted ParticipantId or bounded pending reservations (E-peer 426–511, 521–558). | Partial: account/peer maps and disconnect callbacks; not admission; close-during-connect guard above also matters (C-peer 307–418). Native authentication and four-player pending-capacity behavior remain unproved for all. |
| Exactly-once OperationId completion, five-second local close, native cancel/drain and lobby retry | Unproved as an integration; peer alone supplies no SessionService completion protocol. Singleton create/join does not expose native request handles (G-singleton 2900–2904, 3021–3024, 7780–7786). | Unproved; peer does not implement project SteamPlatform/lobby-operation integration. | Unproved; account-keyed callbacks and C# bindings do not establish operation correlation/drain. |

G therefore exposes more of the low-level packet boundary than the retained singleton
(actual `m_idxLane` on send/receive and native message lifetime), but it still fails
the fixed stream contract. Raising lane count alone would neither fix mode semantics
nor checked results, bounds or drain; no five-lane setting is chosen.
E/C expose some send-error handling, but logging an error while returning success and
retaining an uncapped queue does not satisfy checked, bounded outcomes.

## Comparison with the retained singleton and primary API semantics

The G-singleton bodies for `sendMessages`, `sendMessageToConnection`,
`receiveMessagesOnConnection`, `configureConnectionLanes`, `createLobby`, `joinLobby`,
`lobby_joined` and `lobby_created` are byte-identical to the retained `532740f3`
bodies. `receiveMessagesOnPollGroup` differs only in pointer/delete spacing.
[Body comparison](s03-s-upstream-peer-evidence/singleton-comparison.json) records
source/body hashes and equality separately. This does not certify the whole branch.

Consequently the earlier narrow-API gaps persist at this revision: no lane argument
or assignment on singleton send; no receive lane key; batch `sizeof(Variant)` payload
allocation/pointer assignment and Release before SendMessages; successful result and
message-number handling require care; received bytes are copied before application
size validation. Lane configuration alone restores none of the missing metadata.
The helper peer bypasses these singleton packet wrappers; its copied native payload
path is a distinct partial improvement, not proof that the singleton batch is safe.

[Valve Sockets documentation](https://partner.steamgames.com/doc/api/ISteamNetworkingSockets)
was read alongside immutable public GameNetworkingSockets headers at
[`d534c19aa760df3fb75fd20db13ba1932b8a5463`](https://github.com/ValveSoftware/GameNetworkingSockets/commit/d534c19aa760df3fb75fd20db13ba1932b8a5463).
This fourth identity is API context, **not a fourth peer candidate**, an SDK download,
or proof that its implementation is in the installed Steam library. Header/source
applicability to the actual native pin remains a separate gate.

The [Sockets header](https://github.com/ValveSoftware/GameNetworkingSockets/blob/d534c19aa760df3fb75fd20db13ba1932b8a5463/include/steam/isteamnetworkingsockets.h)
defines lane-specific message numbers, same-lane reliable ordering and no guaranteed
unreliable receive order (419–487). SendMessages can return per-message success,
negative EResult failure or zero for unattempted messages. With delete-failed false,
successful pointers are nulled and failed/unattempted pointers remain caller-owned
(270–322). Under these documented semantics G's missing result/pointer handling
leaves failed message ownership unresolved; no actual leak/crash was observed.
Reliable lane isolation does not guarantee availability under shared-buffer pressure.

The [types header](https://github.com/ValveSoftware/GameNetworkingSockets/blob/d534c19aa760df3fb75fd20db13ba1932b8a5463/include/steam/steamnetworkingtypes.h)
documents receive-byte/message and maximum-message-size controls (1164–1184).
Their existence does not bound a peer's own retained list, prove configured limits
on the installed SDK or make512 KiB a safe RPC/datagram budget. CloseConnection
invalidates the handle and discards unread connection data; optional linger concerns
sent data (Sockets header170–191). It does not certify lobby callback drain.
[Godot peer documentation](https://docs.godotengine.org/en/stable/classes/class_multiplayerpeer.html)
and [extension documentation](https://docs.godotengine.org/en/stable/classes/class_multiplayerpeerextension.html)
explain next-packet channel/mode/peer metadata and close while connecting. These
mutable docs supplement the accepted pinned-engine reflection record; no new engine
API execution is claimed.

Concrete static lifecycle risk in G: `_close` does not reset `tracked_lobby`, while
`lobby_chat_update` can call `add_peer` for that lobby after close; BadCert retry also
has no project operation fence. This shows why local map cleanup is insufficient
evidence for safe reuse. It does not assert that such callbacks were delivered here.
Singleton create keeps one call-result object, join discards its request handle and
joined callback identifies the lobby, so two obsolete/new attempts to the same lobby
remain uncorrelated at this public boundary. New local counters cannot solve that.

## Bounded remaining decision and unsupported cases

ROOT can commission option2, a **separate native-boundary design only**, using the
unchanged criteria: specify lane-addressed owned bytes and checked configuration/
per-send errors including failure ownership; faithful receive lane/mode/number and
bounded allocation/retention/poll work; per-connection/per-stream ordered freshness;
peer mapping and host-loss behavior; and operation-correlated or serialized/drained
close/lobby integration with cleanup-only stale callbacks and an unavailable state
when five-second local cleanup cannot prove safe reuse. Design must identify the
minimum upstream delta and validation prerequisites before any fork/build/adapter
decision. This document grants none of that implementation work. Keeping Steam
unavailable remains valid. Broadening the search beyond these three needs another
bounded commission; there is no open-ended search or request to upstream people.

Future dynamic acceptance must still cover lane1 saturation while0/2/3 progress when
capacity permits; configure/send failures, NoDelay/LimitExceeded and failed-message
release; loss/reorder/duplicate/mode/channel metadata; payload edges plus overhead;
pre-decoder allocation and queue/work bounds; cancel during connection/route/lobby,
late callbacks after close and retry to the same target, host loss and safe handle
retirement. No arbitrary delay or native close bool proves drain. Application
watermarks cannot replace missing native lanes or reliable lifecycle fences.

Actual lobbies/invites, authenticated baseline/intent gameplay over Steam relay across
distinct authorized accounts/machines/networks, Windows/Linux native exports,
private app entitlement/depot/install/update/launch and LCD/OLED Deck Gaming Mode/
input/suspend/1280×800/60 FPS remain deferred/unproved. App5294580 and its intended
`fun-things` route remain historical requirements, not live verification. Accepted
S08 on this base does not convert this source read into Steam or device execution.

## Static validation and frozen handoff

[Session receipt](s03-s-upstream-peer-evidence/session.json) records the exact scope,
settings, public retrieval commands and their limits. Restricted DNS first failed;
the browser denied Codeberg via robots rules. Small read-only raw/API retrievals
succeeded through scoped network escalation; no network configuration was changed.
The complete restricted diagnostic is retained separately from successful hashes.
The first staged whitespace check failed on literal upstream whitespace and warned
that Git would normalize the CRLF SConstruct snapshot. Its full diagnostic is saved.
The adjacent `.gitattributes` now preserves exact snapshot/license/source-diff and
raw diagnostic bytes and exempts only those literal artifacts from whitespace rules; authored prose,
metadata and verification code retain ordinary checks. Index readback checks exact
bytes, including CRLF. The first index readback caught the previously normalized
SConstruct entry; a scoped index refresh restored its original bytes. A subsequent
check caught the literal whitespace inside the saved diagnostic itself; raw `.log`
files now receive the same preservation treatment. These packaging failures are
retained separately from the final passes. Upstream licenses accompany the snapshots.

Run the [offline verifier](s03-s-upstream-peer-evidence/verify.py) from repository root:

```sh
python3 docs/spikes/s03-s-upstream-peer-evidence/verify.py \
  --source-dir /tmp/s03-s-upstream/sources
git diff --check
```

The optional source directory checks complete original hashes and excerpt readback;
without it, committed snapshot/metadata hashes, identities, local links and scoped
base/TODO preservation are checked. The saved stdout/stderr/exits are static checks,
not gameplay, lint/compilation, registration or native/platform tests. Only this new
record/evidence directory and a concise S03-S TODO addition are owned. Prior records,
contracts, vendor/pins, fixtures and every other TODO block remain unchanged.
No owned fetch/check writer or runtime is left running; no merge/archive/push.

## Accepted original review and single rebase — 8 October 2026

The sole clean-context reviewer `c19abd41-4cbf-45cc-88ef-c8301fba3501`, effective
GPT-6.1-Sol HIGH, **ACCEPTED** original exact
`b0587a843cdea0c696b1e72a2fe24503677dd791` against
`52941da4b4c92a547a8066b5c13f733043ecbe48`, with no actionable findings.
This accepts the stopped source/evidence result only. The full original report,
declared package, actual check sources/argv/exits/full streams and failures are
retained losslessly in local `refs/notes/paseo-orchestration` on original b0587a8.
The original candidate remains reachable through
`refs/paseo-evidence/s03-s-upstream-peer-evidence-original`; no recursive review
archive or copy of the old candidate package is added to this tree.

```sh
git notes --ref=paseo-orchestration show b0587a843cdea0c696b1e72a2fe24503677dd791
```

ROOT supplied held accepted LOCAL main
**`30a97532ed2ae922c22d21fd9ac48bd2bab8b145`**, containing TODO cleanup48aef3d and
accepted S07 static inventory/run-card preparation. The actual original-base→new-base
diff changes TODO and adds S07-owned source/evidence; it changes none of the Steam
contracts, original S03/S03-S criteria/callers, vendor/pins or earlier dated records.
The accepted S07 addition is preparation, not a native/Steam result.

One rebase was started from a clean saved boundary. Its sole conflict was TODO:
resolution used the exact cleaned base bytes and inserted only the original three
S03-S evidence lines into the shortened task block. No historical TODO prose was
restored. The S07 task link, source/evidence and every unrelated cleaned TODO byte
remain identical to this base. The original standalone TODO patch stays historical;
its old context is not a patch to restore after cleanup.

All 19 immutable source identities/snapshots, candidate/metadata ledgers, singleton
comparison, peer diff, licenses, raw retrieval records and original checks/streams
remain unchanged. The original retention ledger still verifies the original b0587a8
tree; it is not relabeled as a current-tree ledger. The verifier now uses30a97532 for
scoped ancestry/TODO checks while retaining52941da as immutable source provenance,
checking the historical package and unchanged evidence. This dated supplement is
appended to the original report without altering its technical matrix or STOP.

Only justified static preservation, source/metadata identity, links, scope, Git
history and whitespace checks run. No refetch, engine/native/model/runtime/build,
editor/service query or adapter/protocol selection occurred. The SAME reviewer owns
the compact exact-new-HEAD/base/rebase-delta disposition. The final full receipt,
actual check sources/streams and complete readback belong in ordinary same-HEAD
orchestration notes; metadata retention creates no renewed acknowledgement cycle.
No new workstream/checkpoint/workspace is created. ROOT integrates/archives;
the worker remains saved/quiescent and idle after handoff. All existing gates stay OPEN.
