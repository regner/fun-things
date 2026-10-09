# S08 — Source-first lifecycle discrimination

8 October 2026. **SOURCE-ONLY; no gameplay/native fix and no runtime experiment.**
Exact base `85282adddd8182a6f31b2c80e4419d1d406b3bb2`, workspace
`wks_f91a8960ca89fbf7`, branch `s08-source-discriminating-plan`. Direct pi/OpenAI
Sol6.1 HIGH lead; ROOT owns integration/archival. [Raw commission and static evidence](
s08-source-diagnosis-evidence/README.md), [raw requirements](
s08-source-diagnosis-evidence/raw-requirements.md), and [hash/source ledger](
s08-source-diagnosis-evidence/references.json).

## Boundary and two different unknowns

1. **Original saved-main held/resync stall:** [handoff at `0add6257`](
s08-exported-enet-handoff.md) reached real baseline/admission/journal health70,
then host deadline in ACTIVE and client deadline in IDLE. The first stalled step,
close reason and native registration ordering were not recorded. Client IDLE is
not proof that early client loss initiated the failure.
2. **Release-only native signal registration diagnostics:** [lifecycle at `fd375c03`](
s08-release-lifecycle.md) completed the minimal-S03 gameplay matrix in DEBUG and
RELEASE, but **both used UNPLANNED10ms UDP service: grant compliance FAILED**.
RELEASE strict diagnostics remain **2 host / 6 client `tree_exited` errors**, even
with exit0 gameplay receipts. The original saved S08 main/assets were **NOT rerun**.
Restored20ms helper source is offline-only/unexecuted. DEBUG success establishes
neither release/native correctness nor original-main20ms equivalence.

The [standard-editor/release record at `52941da4`](s08-standard-editor-release.md)
owns the saved-entrypoint/API/package/asset prerequisites and historical failures.
All original reports and raw streams stay immutable. This result can prepare a
separate commission; it cannot close original saved-main20ms, clean-release, S08,
P0, Windows/Deck/Gaming Mode, graphics/input/feel/performance or Steam acceptance.
Actual Steam testing remains deferred. No engine pin/integration is selected.

## Exact native ownership and lifetime

All native references below are retained public Godot source at
**`c971f93e7e76b0ef919bf6009e7b868bea04db7f`**. Ledger rows bind full bytes/SHA256,
Git blob and upstream locator. Paths here abbreviate
`docs/spikes/s08-release-lifecycle-evidence/source/`; line anchors are in the ledger.
The empty `callable.cpp` is a failed retrieval, not source evidence; use
`variant-callable.cpp`. No additional source download was necessary.

| Transition / owner | Supported path and identity | Lifetime / constraint |
| --- | --- | --- |
| Native API owns cache | `scene_multiplayer.cpp:683–698`: constructor instantiates cache with `this`, then replicator/RPC with its pointer; destructor calls `clear`, then unrefs RPC, replicator, cache in reverse order. | Peer replacement reuses this cache object; it does not construct a new cache per S03 operation. Source does not identify the actual release cache ObjectID in old logs. |
| RPC causes tracking | `scene_rpc_interface.cpp:305–340,473–500`: `rpcp` → `_send_rpc` → `send_object_cache`; received simplify-path in `scene_cache_interface.cpp:99–125` resolves node and calls `_track`. | Sent cache ID, remote cache ID, node ObjectID, Session operation ID, participant/entity/control revision and saved resource UID are different identity domains. |
| First track registers | `scene_cache_interface.cpp:41–49`: keyed by node instance ObjectID; insert `NodeCache` **before** connecting one-shot `tree_exited` to native cache `_remove_node_cache.bind(oid)`. | Existing node row skips registration. Connect return is not checked here; a failed registration can leave a logical cache row. Source identifies emitter node versus callback target cache, not a GDScript coroutine owner. |
| Tree exit removes | `scene_cache_interface.cpp:51–73`: callback erases assigned send ID, confirmed-peer sent-node membership and node cache. `object.cpp:1301–1312` disconnects one-shots **before** invoking callbacks. | Receive-node cleanup is deliberately disabled (`#if 0`); `get_cached_object:277–295` can resolve dead ObjectID by saved path and update receive identity. This is path reuse, not proof of ObjectID/UID reuse in these runs. |
| Peer loss differs from reset | `scene_cache_interface.cpp:75–97`: peer loss drops that peer's recv IDs/confirmations and peer record. `scene_multiplayer.cpp:168–176,188–207`: changed peer disconnects old peer callbacks and clears native state. | Peer loss alone does not erase all tracked nodes. Same-peer assignment is a no-op; replacement with OfflineMultiplayerPeer is a reset boundary. |
| Clear then reuse | `scene_cache_interface.cpp:297–308`: resolve tracked node through ObjectDB, disconnect callback, then clear peers/nodes/assigned IDs and reset send ID to1. | Disconnect failure does not stop map clearing. A surviving slot can therefore meet a new `_track` after reset and produce duplicate-connect. This is a source-compatible sequence, not an observed per-node timeline. |

### Comparator follow-through, not callable spelling

`Object::connect` stores the **original bound callable** in the connection but keys
`slot_map` by `*p_callable.get_base_comparator()` (`object.cpp:1624–1651`).
`is_connected` and `_disconnect` use that same base comparator (`1672,1713–1728`).
`Callable::get_base_comparator` asks custom callables for a comparator, otherwise
returns itself (`variant-callable.cpp:241–251`);
`CallableCustomBind::get_base_comparator` delegates to the underlying callable
(`callable_bind.cpp:90–92`). Thus the connect `.bind(oid)` versus unbound clear
spelling is **not** a demonstrated identity defect or source-justified fix.

For native method-pointer callables, `callable_mp.h:83–129` comparison data contains
cache instance pointer, target ObjectID and member-function pointer; constructor
zeroes the Data structure before assignments. `callable_mp.cpp:34–75` compares
size/data bytes and precomputes hash over those words. Callable equality also
requires matching equality-function identities unless custom pointers are already
the same (`variant-callable.cpp:263–288`). DEBUG-only text changes diagnostic
presentation; empty release callable text does not mean a null callable. No retained
binary comparator bytes/hash/function addresses demonstrate an ABI/compiler fault.
Do not infer one from DEBUG success, or turn hypothetical padding into a diagnosis.

Old minimal-release stderr identifies emitter nodes Session#27028096398 and
Replication#27078428051 in each **separate process**; these numeric IDs are not
cross-process identities. Failures point at `object.cpp:1713` (slot lookup missing),
not the no-signal branch1711; duplicate connects point at1630 (base key found).
Client raw order is two missing disconnects, two duplicate connects, two missing
disconnects. There are no per-error monotonic timestamps/native callback target IDs
or stacks tying each error to a specific `_track`/`clear` call. Native cache is the
source-supported owner; exact failed comparator/lifetime mechanism remains unknown.

## Original saved main versus minimal-S03 closure

| Bound input | Original saved S08 (`52941da4`, reused `0add6257`) | Latest actual minimal S03 (`a5756b4b`, retained at `fd375c03`) |
| --- | --- | --- |
| Main | `prototypes/s08/tests/fixtures/s08/release_boot.tscn`, scene `uid://dn1ownu7vk3h2`, script `uid://cffyguysng6st`, root unique_id911609923. | Scratch main `prototypes/s03/tests/fixtures/s03/boot.tscn`, `uid://bi4flpwo0wqyr`; no S08 entrypoint or S01 assets. |
| Startup | Deferred S08 observer resolves manifest resources/UID/remaps, instances saved S01 roundtrip, awaits process frames, queues it free, instances/frees dynamic S03 entity/rig off-tree; `_finish` requests saved S03 scene change then prints S08 before S03 enters tree. | S03 boot enters directly. Seven S03 classes,17 saved source/UID/scene inputs; existing private class/UID discovery only. |
| Package | 185044-byte PCK SHA256 `74f2526b43e0e776410a5ae2ff941ceeb00863593d0c7a2a3b2031b57128c836`;48 members,23 logical maps,22 UID rows;34-file source closure includes S01/S03/new S08. | 122748-byte PCK SHA256 `43cc8236fcb7a06f328c28cf45fed752d6630e1699ebea04e68e34d9aa40e3d7`;23 members,10 maps/UID rows. S03 Session/Proof have additive lifecycle telemetry; their source bytes differ from original. |
| Runtime/service | Same c971 dev7 release template SHA256 `c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695`; handoff uses `stdbuf -oL`, original20ms UDP service. | Same release template, `stdbuf -oL`; executed10ms service, new logging/physics observer. Final20ms source is not that measurement. |
| Observation | Both S08 receipts positive before S03; live readiness0.424353s, client launch0.424385s; baseline_cancel_retry means actual admission/journal70. Host fails at receipt9.164995s; client's full post-exit stream has held-stage IDLE deadline. No held-step log, no actual total traffic capture; proxy count0 means no **scheduled movement** experiment, not zero network traffic. | Full held/resync/recovery passes under10ms, yet strict signal failures. Actual recv123/9665 bytes, send122/9419; debug recv120/9659, send119/9413. These are changed-condition evidence, not replay of the original closure. |

S03 Boot persists across provider substitution, cancel/retry and resync; its Session
and Replication RPC endpoints are not the queue-freed dynamic entities/rigs.
`Session._peer_ready` assigns a new peer; `_close` sets CLOSING/reason, clears roster,
Match (queues entities/rig free), clears Replication buffers, installs offline peer
(native clear), then calls provider close. Provider closes its native peer, increments
epoch, awaits **20ms** timer, emits correlated `closed`; only Session `_closed` sets
IDLE. `_host_lost` routes HOST_LOST through this path. The timer cannot set phase
by itself. Proof awaits timers/helper coroutines/process frames, **not `tree_exited`**.

Held path: Proof `_send_expect` → Replication `send_held` → native RPC channel2
(unreliable_ordered) → host `_held` sender/rate/size validation → Match `submit_held`
→ reliable channel0 `_result` → client `held_result`. A send log alone cannot prove
host receipt or reliable return. Resync path: Session request disables input and
refreshes deadline → host `_resync`/Match control increment → Replication baseline
cut/chunks channel1 → journal70/marker → admission grant plus independent movement
channel3 → input enabled only after matching movement. Missing baseline, journal,
marker/grant or fresh motion can all stall at different boundaries. `begin` performs
authoritative `apply_journal` outside debug assert; no assert-elided mutation is
being proposed again.

## Competing explanations and distinguishing observations

These are hypotheses/unknowns, **not ranked proven causes**. G concerns the original
stall; N concerns release registration. Neither question is waived by the other.

| ID / explanation | Actual support | Unknown / contrary limit | Discriminating observation under a separate commission |
| --- | --- | --- | --- |
| G1: held request or result never completes while both sessions remain active; host later times out and quits, causing client HOST_LOST/IDLE. | Original host ACTIVE deadline and client post-exit IDLE are compatible; `_send_expect` waits for a result before snapshots, host waits for snapshots. | No first held send/host receipt/result receipt, native loss or close timestamps. Packet loss/return failure/guard rejection cannot be selected. | Correlate each held sequence with client send, host `_held` entry/reason/result-send, client result-receipt; show first absent edge and both phases before host case-deadline/quit. |
| G2: resync baseline/marker/grant/movement dependency stalls, or an earlier close invalidates those waits. | Source has separate reliable handoff and motion gate; original completed baseline case but not held_window_resync. | History does not say whether resync began at all. Client IDLE may be consequence, not cause. | Record resync start, fresh deadline, baseline ID/control/entity/health, old-marker rejection, journal/marker/grant/motion/input gates and first close reason. Close before stalled edge favors lifecycle-first; host deadline before close favors consequential teardown. |
| G3: original asset/main startup and timing/service/telemetry differences matter. | Original S08 exercises a larger closure and deferred scene transition; minimal measured sets omit it and service twice as often. | None of these differences was independently isolated; assets are not demonstrated faulty and10ms is not demonstrated curative. | One original-main20ms observation with explicit additive-telemetry delta can establish its first divergence. Compare to immutable minimal traces only as a qualified comparator, not a controlled single-variable experiment. |
| N1: freshly constructed clear comparator does not locate an existing slot; failed clear leaves a slot that new tracking later detects as duplicate. | Clear ignores failure, erases node maps, then `_track` inserts/reconnects; release logs show missing disconnects then duplicates on client. | No old/new base-key bytes/hash/equality-function identity or per-cache timeline. Zeroed comparison Data weakens simplistic uninitialized-padding claims. | At each actual peer boundary retain emitter ObjectID/path and full public `tree_exited` connection list, target ObjectID, callable hash/equality against prior stored slot, binds/flags; unchanged slot after failed clear followed by duplicate registration supports this sequence. Exact native comparator cause needs separately authorized native observation, not this public list alone. |
| N2: logical cache row exists without its expected signal slot (failed initial connect, one-shot consumption/reentrant clear, other teardown), rather than comparator inequality. | `_track` inserts before checking connect; one-shot disconnect precedes callback; clear and tree-exit are different removers. | Old logs do not show a failed initial registration or endpoint tree exit. No source path proves a reentrant clear in this fixture; persistent endpoints weaken ordinary entity-free explanation. | Observe first successful registration, all endpoint tree-exit callbacks, peer replacements and cache-target identities. Absent slot before clear, preceded by actual exit/removal or failed connect, distinguishes missing-slot lifetime from a surviving-slot lookup failure. |
| N3: cache target/API replacement or unobserved owner creates a different key/slot across reuse. | Callback target identity is part of native key; public logs print emitter only. SceneMultiplayer owns cache lifetime. | Source peer replacement reuses cache; no evidence this fixture substitutes SceneMultiplayer or another owner. Blank release text cannot identify target. | Retain actual SceneMultiplayer/cache-target ObjectIDs and each slot's target across operations; changed owner versus same owner separates this from N1. A native stack gap must stay explicit if public APIs cannot expose it. |

The native errors coexist with successful held/resync in minimal RELEASE10ms.
They are therefore not sufficient to reproduce the historical stall **in that changed
condition**. This does not establish harmlessness/noncausality in original-main20ms,
or prove a coroutine/native/ABI fix. Adding `.bind`, suppressing errors, retrying,
changing deadlines/service/pin or choosing another entrypoint is not justified.

## ONE prospective diagnostic card — UNEXECUTED

**Requires a separate bounded runtime commission. This card grants nothing now.**
Purpose: observe the first original-main20ms stalled edge/close ordering and native
slot state across its existing cancel/retry, in one release set; not test a fix.
No automatic second set, debug rerun, engine/native build/repair or pin selection.

- **Preconditions/freeze:** commission must name private process/project/XDG/socket
  ownership and separately authorize any additive telemetry authoring/package phase.
  First bind original34-file closure, source revision52941da4/0add6257, original PCK
  SHA74f2526b… and exact release template above; keep historical originals immutable.
  If original cached inputs are unavailable/differ, STOP rather than regenerate or
  silently use minimal S03. Bind all source/UID/import/scene/node identities, actual
  package members/remaps/class/UID cache/exclusions, scratch config and normal saved
  S08 main. If telemetry needs a derived package, commission/freeze its exact SHA and
  original-to-derived source/pack delta **before** launch: only approved additive
  observations, exact inverse recovery of original statements/values/await/RPCs,
  unchanged original assets, UIDs, hierarchy, renderer/physics and saved-main transition.
  Derived package is not byte-identical historical PCK and must never be reported so.
- **Preserved timing:** actual supervisor imports original `POLL_SECONDS` from
  `prototypes/s03/tools/run_s03.py`
  **0.020s**; poll/forward then sleep20ms,64-datagram poll bound and original stale-held
  deadline2s. No10ms service, independent fast polling thread or rewritten proxy.
  Preserve proof poll10ms, held result wait30ms, cancel retry wait100ms, snapshots120ms,
  provider close20ms, held expiry250ms, case8000ms/session15000ms/resync1000ms cooldown.
  Preserve arming at the original snapshot event and exact five-datagram hold A,
  deliver B then A, drop A, two refreshes. Record actual service wake/forward times;
  added logging overhead is a disclosed condition, not guaranteed timing-neutrality.
- **Bounded observations:** both roles report PID/operation/session/phase and case+
  session deadlines at first held send, host validator entry/result-send, client
  result-receipt, resync/baseline/journal/marker/grant/motion gates and close start/
  provider close-completion/IDLE/quit. At pre/post actual peer replacement and first
  endpoint registration capture public connection lists/flags/binds/target IDs/hash,
  endpoint ObjectIDs/path/scene UID and tree-exit callbacks. Do not add a gameplay
  writer, RPC, await, scheduled input, extra wait or free. Public connection lists
  cannot expose `_disconnect`'s freshly constructed base comparator bytes/function
  identity; retain that limitation, request separate native authority only if needed.
- **Clock/traffic:** Godot monotonic elapsed-usec/deadline ticks stay within each PID;
  parent Python monotonic timestamps bind receipt byte offsets, host/client live poll
  status, socket receive/send counts/bytes/hashes/endpoints, service wakes and observed
  exits. Never subtract host ticks from client ticks or call receipt time emission/
  syscall time. Capture full traffic from before admission, not just armed movement.
  On first divergence retain both roles through the fixed observation window if safe;
  preserve the failure, do not stop consumption so early that consequential close is lost.
- **Independent outcomes:** initial immutable cut75; provisional NOT_ADMITTED; retry
  two-player admission/journal70; held sequence **NOT_ADMITTED, OK, STALE_SEQUENCE,
  STALE_CONTEXT, INVALID, INVALID, WINDOW, WINDOW, WINDOW, NOT_ADMITTED,
  STALE_CONTEXT, OK**; exactly two valid frames consumed/expiry neutral. Resync retains
  entity/life/health70 and increments control; old marker cannot admit, old control
  STALE_CONTEXT, new control OK; subset refreshed samples11/22 with five movement
  RPC receipts and health70. Require original two host/four client case names, literal
  payload bounds baseline8192/held+movement1200 and positive observed sizes, actual
  five fault datagrams/events and intended teardown; partial admission is not full proof.
- **One absolute budget:** proposed runtime total **30s**, start before identity rebind,
  staging/setup, socket/child creation; readiness/client handoff by start+4s while host
  live, work/observation ends by start+20s. All cleanup/readback uses the SAME start+30s
  deadline, reserve final0.25s for stream/receipt closure. Shared cleanup stages normal
  grace2s, SIGINT2s, terminate2s, then concurrent kill/reap using only remaining time;
  no per-child new allowance or positive minimum after expiry. Bound hash/stage work
  and STOP before launch if it exhausts handoff; package preparation needs its own
  explicitly commissioned envelope, not hidden outside this runtime clock.
- **Strict disposition/STOP:** full argv/exits/stdout/stderr/engine/proxy/traffic and
  empty streams, actual Popen reap/socket/stream closure, expected-set/hash/readback.
  Any ERROR/WARNING, missing event/identity, exceeded deadline or incomplete cleanup
  FAILS its criterion even with two exit0 receipts. Observe without suppressing native
  diagnostics; no presumption of clean release or causal fix. On failure/unreproduced
  stall deliver first missing edge and remaining native unknown, then STOP. Another
  attempt requires a demonstrated changed condition and separate commission.

## Static delivery and limits

Checks bind exact retained source/hash/call-path and original-versus-minimal source/
package closure claims; independently read the full lifecycle initial/final reports,
check retained historical manifests/strict diagnostic and timing facts, scope and
preservation, strict JSON, local links, LF and authored whitespace. Actual sources,
argv/exits/full streams, exploratory static failures and the sole independent review
are retained with exact candidate/base metadata in the small delivery note. No engine,
compiler/export/socket/Steam test or fresh shared-state query ran. Filesystem cleanliness
claims only saved source state, not synchronization of an unrelated open editor.
S08 TODO stays open; canonical DOC14 paths and all gameplay/native/assets/pins are untouched.
