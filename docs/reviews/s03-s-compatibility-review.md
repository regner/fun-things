# Independent S03-S compatibility design/probe review

8 October 2026, Europe/London. Sole fresh reviewer: Paseo agent
`ed0c2c1d-f028-497d-822c-c3be476c314e`, direct GPT-6.1-Sol HIGH.
Requested and effective model/effort are independently confirmed by this reviewer's
own scoped runtime snapshot in `reviewer-runtime.json`. No delegation, Astra,
implementation or coordinator layer was used. Context consisted of the commissioned
requirements and repository artifacts, not the implementer's conversation.

Workspace: `wks_18746ba26c666eb7`; branch `s03-s-compatibility-design-probe`;
cwd `/home/regner/.paseo/worktrees/0u71f39f/s03-s-compatibility-design-probe`.

**Verdict: ACCEPT the exact frozen candidate
`64825b51e92e9b5f0eb94a5be5dda1f57cdb0f66` for the single bounded,
stopped compatibility design/probe only. No actionable P0/P1/P2/P3 findings.**
Held LOCAL `refs/heads/main`/base:
`04f16d332636200e71e74862f64282224774d077`.

This accepts the documented insufficiency of the inspected unchanged singleton
Sockets boundary, its finite counterexamples and registration evidence. It does not
accept a Steam integration, adapter, five-lane setting, conforming peer, native
delivery/lifecycle result, contract change or any gate closure. Full S03-S remains
OPEN. P0-GATE and production remain gated.

This report precedes any retention commit. **Approval binds only to the SHA above.
Any subsequent retention, fix, substantive change or rebase requires my explicit
disposition of its exact FINAL HEAD.** I remain available for one justified
fix/final-revision follow-up. Root's completeness/integration check cannot replace
this independent technical disposition.

## Review basis and bounded scope

The commissioned question was whether plain Steam unreliable delivery plus bounded
stream freshness can faithfully supply four independent streams through the existing
narrow native API and preserve MultiplayerPeer semantics, or whether an exact upstream
peer revision supplies them. Substantial framing/sequencing/peer/lifecycle work was
a required stop boundary, not permission to implement it.

Read `criteria.md` before assessing probe expectations, then the complete candidate
record, probe, static checker, registration runner/script, source/hash manifest,
retained results/logs and candidate diff. Read AGENTS, current TODO (including full
S03-S and all gates), design, multiplayer, API identities/session/transport/admission/
streams/limits/acceptance, scene structure, architecture, accepted S03/S03-S and
preparation review. Consulted checkpoint index, fourth checkpoint and substantive
review, and DOC5 for current scope/ownership. Read the required orchestration and
Paseo skills; their review/handoff policy applies without turning this assignment
into orchestration. Paseo was used only to read this reviewer's own metadata.

Accepted preparation at `6a012de162b0d65cdf0c77b2914788ad56fbecf1` is historical
provenance. Its evidence and review were independently compared to this checkout;
no old tutorial or previous technical verdict was substituted for fresh source review.

Only 20 scoped paths differ from base: TODO, the historical S03-S supplement, the
new record/evidence and `tools/probe_s03_s_compatibility.py`. The range is one linear
commit. No candidate write, commit, Git note, rebase, merge, archive or push occurred.
All reviewer report, scripts, copied project and actual evidence are exclusively under
`/tmp/s03-s-compatibility-review`.

## Findings and exact source assessment

No actionable candidate findings of any severity were established. The following
are confirmed limitations correctly recorded by the candidate, not defects requiring
a candidate fix. Immutable source ref:
`532740f3f9c6a826c68914db81af9de1e32d5dc3`.

| Candidate location | Independent assessment |
| --- | --- |
| `docs/spikes/s03-s-compatibility.md:95` | `Steam::sendMessageToConnection`, cpp3624, takes connection/bytes/flags and returns result/number; no lane argument or assignment. Header and binding agree. Plain unreliable is requestable, but this is not a four-lane primitive. Its uninitialized local output number on failure is a source hazard; caller result checking does not establish binary safety. No send was attempted. |
| Same record:96 | cpp3941 lane configuration returns the native result; source allocates/indexes supplied counts/arrays without sufficient wrapper validation. Configuration cannot create a missing lane-addressed send or recover receive lane identity. Array/count/weight validation belongs before this boundary. |
| Same record:97 | cpp3597 `sendMessages` allocates by `sizeof(messages[i])`, assigns the Variant into `m_pData`, saves message pointers and releases their objects before submitting them. No lane selector/assignment exists. This is incompatible with the documented ownership handoff and unsuitable as the selected byte primitive. It is a static hazard, not an observed use-after-free or crash. The safe copy in internal PacketPeer send is a separate owner/path. |
| Same record:98 | cpp3644/3698 receive functions expose bytes/size/connection/identity/user data/time/number/flags but omit `m_idxLane`. They copy native-sized payloads before application validation; message-count bounds do not bound copied bytes or queued native memory. |
| Same record:99 | cpp3895 exposes connection and per-lane pending unreliable/reliable bytes, unacknowledged reliable bytes and queue time after successful result. These can support future observations; no status call or measurement ran. |
| Same record:100 | Packet source94 sets lane and copies bytes safely, but its send is not script-bound. PacketPeer public put uses reliable lane0. At configured4, `channel >= configured_lanes-1` maps channel3 to0. Native send result is discarded and the function returns OK after submission. This independently confirms the default channel defect and hidden send-error risk. |
| Same record:101 | Peer source682 maps ordered-unreliable to reliable. Source83 returns only reliable/plain-unreliable receive mode. Five configured lanes changes neither issue nor send-result handling. No setting was changed. |
| Same record:123 | Two unreliable native messages on lanes2/3 may each have number1 and identical payload and other exposed fields. Removing lane produces identical observations. Message number is not a unique channel key; payload inference cannot faithfully carry arbitrary Godot bytes. This is an information-loss counterexample, not evidence that the singleton actually transmitted on those lanes. |
| Same record:149 | cpp7919 status signal carries native handle, identity, listen socket, user data and state. This supports potential operation binding, not admission or safe handle reuse. Queued callbacks retain historical user data; current receive user data cannot serve as a universal historical operation fence. |
| Same record:155 | cpp2895 create-lobby keeps one call-result object without exposing its handle; cpp3016 join discards its call handle; cpp7740 lobby-enter signal contains lobby/permissions/locked/response, no local OperationId. Same-lobby canceled/retried results can be indistinguishable. A new local counter cannot establish ownership. Safe serialized drain/reuse remains unproved. |

All four source files were independently freshly downloaded from the exact immutable
raw URLs. The review did not use `/tmp/s03-s-compatibility/sources` as authority.
Fresh byte counts and SHA256 match `sources.json`; the three previously manifested
source hashes also match accepted preparation. Full fresh sources and actual download
logs are retained locally. Public Codeberg browser access failed; restricted direct
download separately failed DNS. A scoped read-only network retry of only the four
commissioned URLs succeeded. No network/system repair or SDK fetch/build occurred.

All 22 installed native/configuration hashes match the accepted preparation manifest
and are unchanged from base. Published-byte linkage remains accepted historical
provenance; this review did not redownload the release archive or reproduce a build.
Neither hash equality nor source inspection proves those bodies executed in the binary.

Primary public documentation was freshly consulted, independently of the record.
Valve documents per-lane message numbering, same-lane reliable ordering and no
general unreliable receive-order guarantee; lane scheduling differs from shared
send-buffer pressure. It documents send-result errors, ownership transfer of
allocated message objects, and queued callback user-data timing. These support the
inferences above; mutable documentation is not an SDK1.65 runtime receipt.
[Valve Sockets](https://partner.steamgames.com/doc/api/ISteamNetworkingSockets)
and [message types](https://partner.steamgames.com/doc/api/steamnetworkingtypes).

Godot's required peer methods include packet sender/channel/mode, send target/channel/
mode, polling and close/connection state. The finite filter supplies none of the
endpoint/lifecycle integration. The pinned reflected API was independently rerun;
stable documentation is explanatory only.
[MultiplayerPeerExtension](https://docs.godotengine.org/en/stable/classes/class_multiplayerpeerextension.html).

## Expectations, finite model and bounds

The criteria preserve reliable channel0 session/admission/actions independently of
channel1 baseline/durable/results/events, and ordered-unreliable channel2 held intent
and channel3 movement. They require reorder/duplicate discard without reliable
substitution, no cross-stream watermark and no cross-channel ordering assumption.
They distinguish ordering from guaranteed delivery or dedicated bandwidth.

The finite examples are meaningful for this question: 2,1,2 discards late/duplicate
packets; input20 cannot discard movement1; A100 reordered behind B101 and lost A102
need repeated complete subset refresh to recover A104/B103. The movement example does
not exercise entity/control/session fences or durable-state preservation through a
real receiver. Those remain application contracts, as explicitly stated. A stream
watermark cannot stand for freshness of omitted entities.

The candidate probe reproduced its committed JSON exactly. Independently checked
1,555 traces of length0..4 over two lanes and sequences1..3, using prefix-record
expectations and lane-erasure invariance. These checks cover duplicate/reorder/loss
prefixes and independent filtering. They are synthetic checks of the actual tiny
model function, not transport acceptance or a second implementation of gameplay.
The negative source guard rejected independently altered scratch bytes with exit1
before emitting interpreted facts.

Actual model execution is finite: four watermarks, two example entities, maximum
trace4, no reorder history/wait or native network calls. `accepted` is an output trace,
not a bounded production queue; source text and reflection data are finite scratch
inspection allocations, not packet budgets. Arbitrary input validation, sequence
exhaustion/reset, sender/operation keying, poll backlogs and stale callback retirement
are deliberately absent. No production memory/work guarantee is inferred.

Criteria retain existing provisional logical limits: <=1200-byte held/movement,
<=4096-byte actions with bounded rate/burst/queue/work/cache/ahead, <=16KiB reliable
complete batches/chunks, <=1MiB/128-chunk baseline, <=2MiB or4096-record journal,
bounded latest future row/entity and resync/deadlines. They preserve 250ms expiry/
revisit, input/movement/simulation rates and five-second local closing. None is
claimed as a measured native MTU, transport maximum, receive-allocation bound or
ratified new budget. Native configurable allocations and polling still need bounds.

Before a future native experiment, the criteria require lane configuration result,
per-send mode/lane/size acceptance/errors, received metadata, per-lane/connection
pending bytes and queue time. Withheld baseline acknowledgement tests separation
when capacity permits; bounded load tests shared-buffer pressure, failed send
reporting, NoDelay drop, invalid state/parameter/size and bounded recovery. Payload
edges plus overhead and native receive allocations remain observations to obtain,
not observations this model made. Stopping before implementation is appropriate once
the unchanged API cannot address or identify the lanes.

## Lifecycle, options and stop boundary

Connection/account/lobby membership is not admission. SessionService remains the
owner of fresh participant mapping, exactly-once accepted-operation completion,
BUSY/retry and closing; Match/Replication retain reliable hydration and identity/
generation/control/life/collision rejection. The criteria and record preserve
producer/mapping/history invalidation before release, cleanup-only stale callbacks,
serialized uncorrelated lobby work and unavailable-until-safe-reuse/restart after
cleanup timeout. No callback drain deadline is invented from a close boolean or
ENet delay. Host loss still ends the match.

The minimum exceeds a freshness shim: accurate lane-addressed send/results, lane/
mode/number receipt, ownership/allocation bounds, a MultiplayerPeer endpoint and
native lifecycle integration must be specified/proved. Native per-lane numbers may
avoid a custom sequence header only after those dependencies are established. Mode
identity must remain faithful if plain and ordered unreliable share a lane. No
framing/protocol/framework/codec/replay/service implementation was added.

The three options at record179-195 are correctly presented as a root commission
decision, not existing conforming solutions: (1) exact immutable upstream revision
evidence; (2) separately bounded native-boundary/peer design; (3) keep Steam
unavailable/deferred. No qualifying revision was located in the inspected pin; this
is not an exhaustive claim about all upstream history. Single-lane application
multiplexing cannot remove baseline/actions ordering; four connections introduce
additional admission/failure/close aggregation and are not accepted equivalents.
The same compatibility owner remains named, with the criteria as requirements and
no authorized expansion. This satisfies the exact stop/report boundary.

## Actual checks and retained evidence

All paths here are below `/tmp/s03-s-compatibility-review`.

| Actual check | Result / evidence |
| --- | --- |
| `python3 fetch.py`, restricted | Exit1 DNS failure, `fetch-restricted.log`; separate from successful result |
| Same four-URL fetch with scoped network access | Exit0, exact sizes/hashes in `fetch-public.log`; full `sources/*` |
| `python3 tools/probe_s03_s_compatibility.py --source-dir /tmp/s03-s-compatibility-review/sources` | Exit0; exact committed JSON equality; `probe.json`, empty `probe.stderr` |
| `python3 docs/spikes/s03-s-compatibility-evidence/check_static.py` | Exit0; 20 paths, 940 original blobs, 130 local links, 27 tasks, all22 hashes; `candidate-static.log` |
| `python3 docs/spikes/s03-s-compatibility-evidence/run_registration.py /tmp/s03-s-compatibility-review/registration /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot` | Exit0; `registration-runner.log`, fresh raw/project/selected API and exact commands/returncodes in `registration/` |
| `python3 /tmp/s03-s-compatibility-review/audit.py` | Exit0; independent scope/mode/blob/working-byte/native/accepted-preparation/TODO checks, 1,555 finite traces, negative guard and API comparison; `audit.log`, `audit-receipt.json`, `candidate.diff` |
| Negative guard subprocess on copied altered cpp | Expected exit1; no stdout/facts, `negative-hash.stderr`, `negative-hash.stdout`; `mutated-sources/` |

Every registration subprocess has a30s timeout, separate fresh copied project and
XDG directories. Exact engine `4.8.dev7.official.c971f93e7`, version4.23,
auto-init false, default channels4. Fresh method/signal/virtual/getter projection
matches committed evidence exactly apart from scratch command paths. Version and
registration logs match exactly and have no engine/script diagnostics. No editor,
import, Steam initialization, native send/connection/lobby or shared display was used.
This proves local debug-library registration/API presence/getters only.

Independent preservation checks cover all940 unaffected base entries by mode/blob
and working bytes; all TODO bytes outside S03-S, not just task IDs; all9 accepted
preparation evidence/review paths; original preparation prefix; all22 native hashes;
JSON, Python AST, LF/newline, whitespace and absence of Git operation/index lock.
Canonical contracts, project/pin/resources/Blender/vendor bytes, unrelated tasks,
S04 lease/unaccepted status, DOC5 and fourth-checkpoint/index/watermark are unchanged.
The examined watermark stays `8d60ff6`; this is not a new plan checkpoint. I did not
inspect any pending S04 source/candidate/process or contact/intervene with its owner.

## Limits, remaining gates and quiescence

Native delivery/modes/lane independence under loss/saturation, send errors, queue/
allocation/per-tick bounds, MTU/logical payload support, authentication/admission,
cancel/drain/retry/late stale callbacks and host-loss cleanup remain unobserved.
Reflection, model and static code cannot certify them. Predeclaration content was
read first and is consistent with the experiment; its historical save chronology
is the worker's stated receipt, not independently timestamped by this reviewer.

Two authorized accounts/separate machines/networks, actual gameplay/relay route,
lobby/invite/launch-join, app5294580 type/release/packages/tester entitlement,
depots5294581/5294582 filters/inclusion, live launch/private-branch setup and tester
install/update/access remain deferred. Windows/Linux exports, exact engine/templates,
ENet without Steam packaging, LCD/OLED Gaming Mode/input/native1280x800/60FPS,
host/client/offline/suspend and user feel/device/production acceptance remain unmet.
Six-block M1 and all original gates are retained. No renewed account/SDK/device
request, gate waiver, upgrade, renderer/package choice, profile install/representative
launch or restricted SDK work occurred.

No shared editor/Blender/display/service lease or query occurred. No Steam/client/
steamcmd/socket send, service/network repair, port kill, process inventory/kill or
live partner mutation occurred. Only the reviewer's bounded owned children ran;
all completed normally (the intentional negative hash child returned1). No owned
runtime/writer/verification session remains; none needed termination. I make no
claim about shared process absence or unsaved editor state.

**Reviewer artifacts are saved and quiescent. Final candidate tracked/untracked
status is clean; HEAD/main remain the exact candidate/base above. Approval is for
this stopped experiment only. Later retention/fix/rebase FINAL HEAD must return to
this reviewer for explicit exact-SHA disposition before integration.**
