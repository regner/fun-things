# S03-S — bounded compatibility design/probe

8 October 2026. Direct implementation owner: `6a768b9c-b35d-4008-b94f-e713554dd1a5`,
GPT-6.1-Sol HIGH, workspace `wks_18746ba26c666eb7`, branch
`s03-s-compatibility-design-probe`. Starting LOCAL main:
`04f16d332636200e71e74862f64282224774d077`. One focused compatibility session,
within the 1–2 focused-day cap. Root owns any integration/contract decision.

**Disposition: infeasible through the inspected unchanged singleton Sockets API
as a four-lane peer; ordered filtering alone is feasible as a finite model.
Native delivery/lifecycle conformance remains uncertain/unobserved. STOP here.**
No adapter, custom peer, native build or integration is selected. No contract,
vendor, pin, project setting, scene, asset or shared-service change is made.
Full S03-S remains **OPEN**; P0-GATE and production remain gated.

The [accepted preparation](s03-s.md) at `6a012de` remains historical. This supplement
answers only its one ungated compatibility question: can plain Steam unreliable
plus bounded stream freshness and four independent native lanes present the
existing MultiplayerPeer contract through the exact installed API?

## Predeclared expectations and scope

The [criteria](s03-s-compatibility-evidence/criteria.md) were saved before probe
implementation/execution. They derive from [API contracts](../api-contracts.md),
[multiplayer](../multiplayer.md), [architecture](../architecture.md),
[scene ownership](../scene-structure.md), [design](../design.md) and
[accepted S03](s03.md), rather than a new compatibility contract.

| Stream | Mode and expectation |
| --- | --- |
| 0 session/admission/actions | Reliable ordered independently of baseline traffic |
| 1 baseline/durable/results/events | Reliable ordered; complete journal/handoff transactions |
| 2 held intent | Unreliable ordered; skip loss, discard late/duplicate packets, never retransmit via reliable fallback |
| 3 movement subsets | Unreliable ordered independently of input; per-entity/control application freshness plus every-subset revisit within provisional 250 ms before loss |

No cross-channel receive order or dedicated bandwidth is promised. Channels share
congestion/buffer capacity; lane separation must prevent reliable head-of-line
ordering between streams. Per-packet ordering does not prove receipt of omitted
entities. Admission, sender identity, SessionId, MatchRevision, entity generation,
life/control/collision dependencies and durable-state ownership remain application
contracts. A generic peer cannot inspect movement to recreate those rules.

The criteria retain packet/rate/queue/work/history/deadline limits, including
1200-byte held/motion, 4096-byte actions, 16 KiB reliable batches/chunks,
1 MiB/128-chunk baseline, bounded journal, latest future row/entity, four-player
capacity including pending reservations and five-second local closing.
They predeclare the future saturation/send-error observations before any native
implementation. Those sizes are existing provisional logical budgets, not tested
Steam limits or safe datagram sizes. This experiment has only finite traces,
four watermarks and two example entities; no reorder queue/history or codec.

## Exact source/native/API linkage

Fresh read-only public downloads use immutable ref
**`532740f3f9c6a826c68914db81af9de1e32d5dc3`** (v4.23-gde):
[source URLs, lengths and SHA-256](s03-s-compatibility-evidence/sources.json).
Fresh `godotsteam.cpp`, multiplayer peer and packet source hashes match the
preparation manifest; `godotsteam.h` is newly hashed here. Exact
[Steam declarations](https://codeberg.org/godotsteam/godotsteam/src/commit/532740f3f9c6a826c68914db81af9de1e32d5dc3/godotsteam.h),
[singleton implementation/bindings](https://codeberg.org/godotsteam/godotsteam/src/commit/532740f3f9c6a826c68914db81af9de1e32d5dc3/godotsteam.cpp),
[peer](https://codeberg.org/godotsteam/godotsteam/src/commit/532740f3f9c6a826c68914db81af9de1e32d5dc3/godotsteam_multiplayer_peer.cpp)
and [packet](https://codeberg.org/godotsteam/godotsteam/src/commit/532740f3f9c6a826c68914db81af9de1e32d5dc3/steam_packet_peer.cpp)
are the technical authority for this source inference. No latest-release search,
upgrade or replacement binary was attempted. Preparation's 4.23.1 identical
peer/packet observation is historical, not a fresh whole-release audit here.

All 22 installed native/configuration SHA-256 values still match the accepted
[release-byte manifest](s03-s-evidence/provenance.json). This links installed
libraries to published GodotSteam 4.23/Steamworks SDK 1.65 bytes. It does **not**
reproduce a build or prove source-body behavior in those binaries. No restricted
SDK was obtained, built or distributed.

[Valve Sockets documentation](https://partner.steamgames.com/doc/api/ISteamNetworkingSockets)
was consulted on 8 October: lanes have independent message numbers, unreliable
receive order is unspecified, same-lane reliable delivery is ordered, lane
scheduling and send-buffer failure are distinct concerns. It is a mutable public
API description, not an immutable SDK-1.65 implementation/runtime receipt.
The [message-types documentation](https://partner.steamgames.com/doc/api/steamnetworkingtypes)
provides additional context; exact wrapper declarations and accepted provenance
anchor applicability. Public documentation alone cannot establish native behavior
on our pin. A browser fetch of Codeberg failed; exact raw downloads succeeded
through scoped read-only network escalation after restricted DNS failure.
[Failure](s03-s-compatibility-evidence/fetch-restricted.log) and
[successful hash log](s03-s-compatibility-evidence/fetch-public.log) are separate.
No network configuration repair was performed.

## What the existing narrow API supplies and loses

The [static probe result](s03-s-compatibility-evidence/probe.json) records exact
function line numbers, signatures and returned keys. These are source observations;
the implications below are inferences, not native execution results.

| API/source | Observation and implication |
| --- | --- |
| `sendMessageToConnection`, cpp 3624–3632 | Accepts connection, bytes, flags; returns result/message number. Plain unreliable can be requested. No lane argument or lane assignment; this convenience path cannot address lanes 1–3. Check result before using message number: the source local `number` is not initialized before an unsuccessful native call. |
| `configureConnectionLanes`, 3941–3960 | Exposes configuration result, priorities/weights. Configuration alone supplies neither lane-addressed send nor missing receive metadata. Caller must validate array lengths/positive weights before this wrapper's indexed native allocations. |
| `sendMessages`, 3597–3620 | No per-message lane input or `m_idxLane` assignment. Allocates `sizeof(messages[i])`, assigns Variant to payload pointer and releases each allocated message before submitting saved pointers to native SendMessages. This source ordering conflicts with the documented ownership handoff; unsafe to choose as a byte/lane primitive without an upstream ownership/size audit. This is not an observed native use-after-free/crash. |
| `receiveMessagesOnConnection`/`OnPollGroup`, 3644–3677 / 3698–3730 | Return bytes, size, connection, identity, user data, receive time, message number, flags; omit `m_idxLane`. Cannot recover lane identity from independent message numbers or reliable flag alone. Copies native-sized payload before application size validation; max-message count alone is no byte/allocation proof. |
| `getConnectionRealTimeStatus`, 3895–3935 | Exposes connection/per-lane pending unreliable/reliable, unacknowledged reliable and queue time after successful response. Useful future observations; no metrics were called here. Validate requested lane count before native allocation. |
| `SteamPacketPeer::send`, packet 94–119 | Internal native send sets lane but is not script-bound; public PacketPeer put defaults to reliable lane 0. Internal channel 3 falls to 0 at configured 4; result array is null and function returns OK after submission, hiding native send failure. Getters expose connection handle, not the needed safe lane send API. |
| `SteamMultiplayerPeer` flags/mode, peer 682–699 / 83–90 | Ordered-unreliable is sent reliably and receive mode reports reliable/plain-unreliable. Five configured lanes changes the channel check, not this mode mismatch or send-result handling. |

Godot's [MultiplayerPeerExtension interface](https://docs.godotengine.org/en/stable/classes/class_multiplayerpeerextension.html)
requires packet peer/channel/mode, send target/mode/channel, polling, close,
connection/peer IDs and lifecycle signals. The pinned engine's reflected virtual
methods are retained in [registration API data](s03-s-compatibility-evidence/registration-selected.json).
The stable documentation is explanatory, not a pin check. No custom subclass was
created. Feeding raw arrays to gameplay would bypass the required high-level RPC
boundary; a working generic MultiplayerPeer requires more than a freshness function.

## One finite counterexample/model and registration check

[Probe tool](../../tools/probe_s03_s_compatibility.py) checks source hashes before
extracting exact function bodies. Its finite synthetic cases are independent
expectations from the predeclared criteria, with no Steam timing/loss simulator:

- Delivery 2,1,2 on stream 2 accepts only 2, without waiting/retransmission.
- Stream 2 sequence20 followed by stream3 sequence1/2 accepts both stream3 updates;
  a shared watermark would incorrectly discard them.
- Reordered A100 behind B101, lost A102, then B103/A104 produces per-entity freshness
  A104/B103. This illustrates the existing periodic refresh requirement; it does
  not claim Steam convergence, bandwidth or authoritative gameplay acceptance.
- Possible native messages `(lane2, number1, unreliable, same bytes)` and
  `(lane3, number1, unreliable, same bytes)` project to identical wrapper metadata.
  Other keys can be identical too (same peer/connection/user data/size/receive time);
  none carries lane identity. A generic adapter cannot identify both channels
  without added framing or a different native boundary. This is an information-loss
  counterexample, not an assertion that this wrapper actually sends on lane2/3.

Source-derived default mapping `[0,1,2,0]` versus five-lane `[0,1,2,3]` is retained
only to show that lane-count configuration cannot resolve the separate mode problem.
The finite filter has no arbitrary-input/network-boundary validation and is not
production code or an accepted peer. It cannot satisfy admission or lifecycle.

A fresh copied addon/project, seeded scratch extension discovery list and independent
XDG directories ran pinned `4.8.dev7.official.c971f93e7` headless. No editor/import,
shared connector, display or service lease was used. Only reflection and
version/settings getters were executed; auto-init false, 4.23, default channels4.
[Version log](s03-s-compatibility-evidence/version.log),
[registration log](s03-s-compatibility-evidence/registration.log) and
[getter/hash check](s03-s-compatibility-evidence/registration-check.log) pass with
zero exits and no engine/script diagnostics. A first reflection run omitted the
engine extension virtual list; the final copied run adds that API-presence check.
Both completed; neither is native delivery or lifecycle evidence. The preparation's
restricted editor-import failure remains historical and is not relabeled a pass.

## Lifecycle limitation and exact stop/decision boundary

Native Sockets status callbacks expose connection handle, identity, listen socket,
user data and state (cpp7919–7936). These can help bind one handle to an operation;
queued callback user data, handle retirement/reuse and teardown still need proof.
Current connection identity is not admission. The original SessionService/Match/
Replication owners continue to own fresh participants and reliable hydration.

Lobby create returns void, stores one call-result object; join returns void,
discards its native call handle. Lobby callback correlation does not provide the
local OperationId. Two canceled/retried joins to the same lobby can have identical
public lobby-result identity: tagging receipt with the new local counter cannot
prove ownership. This is a static ambiguity, not an observed callback trace.
Serialize and drain obsolete operations with cleanup-only ownership, or keep Steam
unavailable on cleanup timeout until proven safe reuse/restart. No arbitrary wait,
ENet close delay or native close bool is a drain guarantee. Cancel completion must
remain exactly once, input closed, old mappings/history invalidated, and old results
must never attach to the next attempt. None of these native cases ran.

**Minimum change exceeds a freshness shim.** One connection/four lanes needs safe
lane-addressed send with accurate per-message results, receive lane metadata,
ordered-mode identity/freshness and bounded receipt, plus a MultiplayerPeer endpoint
and lifecycle integration. If plain-unreliable and ordered-unreliable can share a
lane, reliable flag alone cannot distinguish them: constrain the unchanged declared
stream roles or supply explicit mode metadata without silently changing public
capabilities. Per-stream native numbers may avoid a custom sequence header only
after lane visibility, number semantics, retirement and mode identity are established.
A wire/session fence may still be needed for reused connections. These are design
questions, not an implemented/approved protocol.

Options for **root to commission**, under the unchanged contracts:

1. Ask upstream for one exact immutable peer revision covering ordered-unreliable,
   channels0–3, safe payload ownership, checked configure/send results, bounded
   receipt and lifecycle integration. Require source diff/hash/API presence evidence
   before replacing any pin. No qualifying revision was located in this focused
   exact-preparation-source experiment; no claim none exists elsewhere.
2. Separately authorize a narrow native API/peer design: lane-aware bytes/results,
   receive lane/mode/number/identity, explicit ownership and allocation limits, then
   specify bounded peer mapping/polling/close and platform drain. A vendor fork/build
   or SDK work is a separate decision; no such work is authorized/performed here.
3. Keep Steam unavailable/deferred while those integration questions remain open.
   Single-lane application multiplexing still orders baseline/actions together;
   four separate connections add binding/admission/close/failure aggregation machinery
   and have not been shown equivalent. Neither workaround is an accepted fix.

Actionable next step, same **S03-S compatibility owner**: root selects whether to
commission the exact-revision upstream evidence request or a separately bounded
native-boundary design, using the saved criteria as acceptance requirements.
Do not repeat this model expecting network proof; do not build a whole peer/reliable
routing/codec/replay service or weaken streams/modes on the basis of this record.

## Remaining proofs, reproduction and saved boundary

The predeclared lane1 saturation exercise must record configuration and individual
send errors, per-lane pending bytes/queue time and actual lane0/2/3 receive behavior.
Native LimitExceeded/NoDelay Ignored/invalid state/size results remain unobserved.
No overload independence, MTU, maximum payload, memory bound or latency was measured.
Actual native authentication/admission, cancel/drain/retry/host loss, lobby/invite,
route/relay diagnostics across distinct authorized accounts/machines/networks,
Windows/Linux exports/private install/update/launch/access, and LCD/OLED Deck
Gaming Mode/input/offline/suspend/native1280×800/60 FPS remain deferred/unproved.
App5294580, depots5294581/5294582 and intended `fun-things` remain historical
requirements, not live verification. No new access request or waiver is made.

Reproduce static/model results after downloading the four exact public URLs in
`sources.json` to a fresh source directory (no SDK):

```sh
python3 tools/probe_s03_s_compatibility.py --source-dir /tmp/s03-s-compatibility/sources
python3 docs/spikes/s03-s-compatibility-evidence/run_registration.py \
  /tmp/s03-s-compatibility-registration-new \
  /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot
git diff --check
```

The registration destination must be new and under `/tmp`; each subprocess has a
30-second timeout and separate logs. [Exact public-fetch script text](s03-s-compatibility-evidence/fetch.py.txt)
records the actual download commands, URLs and timeout. No import/all-script suite,
gameplay, native send/init, network/service/config repair, renderer/engine/package
choice, export or device test is claimed. [Static integrity checks](s03-s-compatibility-evidence/static-checks.log) retain original
base blobs and every unrelated TODO block; only S03-S discovery/next action changes.
Checkpoint examined watermark stays `8d60ff6`. At the original review boundary S04
was active/unaccepted under its own sole authoring lease, never queried or touched
here; the dated rebase supplement below records the subsequent accepted main state.

Python AST syntax for the three tools passes. A one-byte-change-in-scratch
[negative hash-guard check](s03-s-compatibility-evidence/hash-guard-negative.log)
returns the expected assertion/nonzero exit before source interpretation.
[Worker/model receipt](s03-s-compatibility-evidence/model-receipt.json) confirms
requested/effective Sol6.1 HIGH and supported review routing; zero installed
profiles, no profile/config change or representative launch.

Sole independent clean-context reviewer `ed0c2c1d-f028-497d-822c-c3be476c314e`,
requested/effective GPT-6.1-Sol HIGH, **ACCEPTED** exact substantive candidate
`64825b51e92e9b5f0eb94a5be5dda1f57cdb0f66`, with no actionable findings or fixes.
The [full original report](../reviews/s03-s-compatibility-review.md) is retained
verbatim with [retention hashes](../reviews/s03-s-compatibility-evidence/retention.json)
and independent source/static/1,555-trace/negative-guard/registration evidence.
These synthetic checks are distinct from native delivery/lifecycle acceptance.
At that historical boundary, the same reviewer was required to approve exact
final retention/rebase HEAD; the full receipt and worker handoff are retained in
local `refs/notes/paseo-orchestration`. The current exact acceptance is linked in
[the final disposition below](#accepted-exact-final-compatibility-disposition);
original approval is not automatically transferred to another SHA.
Retention validation initially rejected intentional empty stdout and then raw
Godot JSON without a terminal newline. Both [first failure](s03-s-compatibility-evidence/retention-check-initial.log)
and [second failure](s03-s-compatibility-evidence/retention-check-second.log)
are retained. The scoped checker now verifies every copied raw review receipt by
exact size/hash and preserves its original bytes; source/doc newline checks remain.
[Final retention integrity check](s03-s-compatibility-evidence/retention-check-final.log)
passes. This is a tooling/receipt correction, not a native experiment or technical
candidate finding; no probe/runtime rerun was needed. Technical acceptance belongs
to that reviewer. Root alone
integrates local main and archives. All owned fetch/registration/static children
completed; no shared lease or owned runtime is left. No merge/archive/push.


## Accepted-main rebase supplement — 8 October 2026

Root notified acceptance/integration of bounded S04 technical HEAD
`2370ad1c182b46e51f5dc4c6b6ab6157819e84b0`, now held LOCAL main/base.
A clean-boundary `git rebase refs/heads/main` completed without conflicts.
`git range-diff` confirms both original S03-S commits replay with identical patches:
`64825b5` → `673ae56`, `6df14a5` → `826e431`. The original preparation,
predeclared criteria, probe, native/API/source evidence, full original report,
retention ledger and previous exact-final receipt are historical and preserved;
previous approval of `6df14a5` is not relabeled as approval of the rebased HEAD.

Scoped reconciliation read the accepted-main TODO/API delta and the accepted
[S04 record](s04.md) / [body/seat contract](s04-contracts.md). The new canonical
API paragraph is an explicitly bounded seat/body fixture supplement; common
Steam modes/four streams, admission/identities, limits and cancel/drain requirements
are unchanged. S04's technical result, including its fresh-movement producer gate,
is accepted on this base; **full S04 remains OPEN** for drawable response, feel/
controls/dimensions/prediction selection, Steam, targets and the existing gates.
No car result becomes Steam evidence or a production body/seat decision here.

All S04 source/assets/evidence, canonical API additions and unrelated TODO blocks/
ownership prose remain byte-identical to accepted main. Historical/pending status
phrases already in that main are not a new S03-S judgment; the root's supplied
exact accepted technical revision above owns the current integration status.
The S04 lead exclusively owns its separate operational relocation; this worker
acquires no authoring/display/service lease and queries none of those surfaces.
No duplicate task, operational relocation or global documentation audit is added.
Checkpoint examined `8d60ff6`, profiles and all external/device/production gates
remain unchanged. The checker base changes only to the new accepted revision;
old reports/logs keep their exact old SHA/base/counts.

Only justified static reconciliation is run: accepted-base working bytes/tree
identity, all other TODO blocks, unchanged original S03-S evidence, exact raw
review receipts, links/JSON/whitespace and Git ancestry/clean state. The unchanged
model/source fetch/registration/native checks were not repeated. The required
same-reviewer exact disposition and root integration are now recorded below;
this dated supplement's original SHAs, bases, counts and S04 assignment remain
historical, not new operational ownership or experiment receipts.

## Accepted exact-final compatibility disposition

The SAME sole independent clean-context reviewer
`ed0c2c1d-f028-497d-822c-c3be476c314e`, GPT-6.1-Sol HIGH, explicitly **ACCEPTED**
exact final `ca38e4fc55b32a379ef7e3bf947e27d4ca8edc4c` against LOCAL base
`2370ad1c182b46e51f5dc4c6b6ab6157819e84b0`, with no actionable findings or fixes.
This covers rebased patches, retention and scoped accepted-main reconciliation,
not native delivery/lifecycle or full S03-S. Earlier64825b5/6df14a5 approvals,
original04f16d3 base/counts/failures and the historical S04 authoring assignment
remain tied to their original boundaries. The [full original report](../reviews/s03-s-compatibility-review.md)
and saved predeclaration remain unchanged.

The COMPLETE historical/original-final/rebase reports, actual check sources/stdout/
stderr, old final note, worker handoff and root FF integration/archival preflight
are retained losslessly in `refs/notes/paseo-orchestration` on exact ca38e4f:

```sh
git notes --ref=paseo-orchestration show ca38e4fc55b32a379ef7e3bf947e27d4ca8edc4c
```

Root integrated the exact accepted revision and archived its worker workspace.
This supplied receipt is operational history; no current editor/service/PID query
or lease follows. Original retention failures and reviewer scratch failures remain
separate from their corrected static passes. No source/model/registration/native
experiment was repeated for this guide reconciliation.

The stopped decision/options and same S03-S owner remain unchanged: root commissions
exact immutable upstream-revision evidence, separately bounded native-boundary design,
or keeps Steam unavailable. No adapter/integration/five-lane/reliable fallback/SDK/
vendor/pin/package is selected. Full S03-S/S04/Steam/Deck/P0/M1/production gates remain
OPEN. [DOC7 completion](../reviews/p0-doc7.md) records this guide reconciliation.
