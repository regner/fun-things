# S08 — Release lifecycle diagnosis

8 October 2026. Base `233493abc7d2e3c106fb620105cfb766f542813b`, workspace
`wks_994c911f32d1485c`, branch `s08-release-lifecycle-diagnosis`. Direct Sol6.1 HIGH
lead; effective `PI_PROVIDER=openai`, `PI_MODEL=gpt-6.1-sol`,
`PI_REASONING_LEVEL=high` read once. ROOT `56025a67-0fb8-4968-8d02-1fbec744bb12`
coordinates; this worker neither integrates nor pushes.

[Complete requirements/grant](s08-release-lifecycle-evidence/raw-requirements.md).
Starting historical input is exact `0add62579b3f98ec010badb31613c411e2ea7b12` and
its `refs/notes/paseo-orchestration` note. All 189 decoded retained payloads were
read back against their bytes/SHA256; old evidence is referenced, not reconstructed
from missing temporary files or recursively packed. Prior STOPs remain failures.

## Current result and material source correction

Both new diagnostic sets complete the original S03 gameplay matrix. RELEASE remains
**strict diagnostic FAIL** with two host/six client `tree_exited` errors. No gameplay
fix is implemented, historical stalling is not reproduced, and no sole cause is
claimed. The original S08 saved main/assets were not rerun.

**Superseded interpretation:** the initial bound-versus-unbound callable observation
below is NOT a demonstrated cache identity mismatch. Follow-through of exact dev7
`Object::connect`/`_disconnect` shows both key by `get_base_comparator()`;
`CallableCustomBind::get_base_comparator()` delegates to the underlying callable.
Merely adding `.bind(oid)` to disconnect is therefore not a source-justified fix.
The earlier tentative interpretation remains in protocol commit `79997a5` and raw
coordination history, explicitly superseded here. Native SceneCache owns the signal
operations; the release-only registration/comparison failure mechanism is still
unproved. This correction must accompany any downstream handoff.

## Phase A: ownership and initial tentative interpretation (superseded)

S03 Session alone changes phase, closes peers and owns admission/operation mapping.
Its `_host_lost` initiates HOST_LOST; provider `close` waits 20ms before correlated
`closed`, which permits IDLE. Match owns entity/rig release and replication clears
attempt buffers. The provider's awaited timer cannot itself write Session.phase.
Proof awaits paced timers/helpers and never awaits `tree_exited`.

Exact dev7 public native source reveals a different `tree_exited` owner:
`SceneCacheInterface::_track` connects `_remove_node_cache.bind(oid)`; `clear`
disconnects the unbound callable. `SceneMultiplayer::set_multiplayer_peer` calls
clear during peer replacement. Initially this was described as a qualified native
connection mismatch; the comparator follow-through above supersedes that reading.
It identifies the native owner, not an identity defect or gameplay-loss cause.
No engine/vendor change is allowed.
The historical host reports an ACTIVE deadline before the runner stops; client
full-stream readback later reports IDLE. That does not establish IDLE as the primary
fault: a stalled held/resync proof could make the host quit, followed by HOST_LOST
and IDLE on the client. Historical logs contain neither held-step progression nor
close reason/time. No causal gameplay correction is demonstrated yet.

## Committed diagnostic condition (not a fix)

ROOT separately authorized one DEBUG diagnostic set before a fix. Only additive
telemetry in saved S03 Proof and Session is proposed: public close-start signal,
state/completion/held-send/receipt observations, host simulation/expiry observations,
engine elapsed microseconds/PID/role/phases/deadlines. Existing gameplay statements,
values, waits, RPC declarations, names, UIDs and node identities remain unchanged.
`tools/s08/lifecycle_edits.py` declares exact toolkit requests and inverse readback:
removing only diagnostic additions must recover exact base script bytes.

One private editor session, at most 25min (reused supervisor author window 20min,
startup 60s and bounded cleanup). Fresh `/tmp/s08-lifecycle-author` owns project,
XDG/process/registry/token paths. Before launch, read-only existing seed at
`/tmp/s05-author-56eb6b28-run01/config/godot/editor_settings-4.8.tres` is present,
SHA256 `8b96a837c9de1511c7cb1c516f49543d61b332628fe29f260960ff6073843d57`;
copy exact bytes only into new private settings scope. No initializer, shared
settings or main editor operation. Use the unchanged installed MCP SDK through
accepted `tools/s05_effect/private_author.py`, actual canonical project/PID/token
and live boost=false startup verification. Inspect tool inventory and affected saved
scene, use `script_edit`, then script checks, save/reopen and saved diff. No hierarchy
or placement mutation; no historical shutdown experiment. Normal editor exit is
ordinary owned cleanup and full logs are retained without diagnostic suppression.

Pinned DEBUG binary:
`/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`,
151398728 bytes, SHA256
`6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd`, exact source
`c971f93e7e76b0ef919bf6009e7b868bea04db7f`. No acquisition, pin/renderer change,
Steam initialization or package export is needed for this diagnostic.

After saved-source checks and a committed candidate, one invocation:
`python3 tools/s08/lifecycle_diagnostic.py --output /tmp/s08-lifecycle-debug01
--revision <exact committed HEAD> --author-project /tmp/s08-lifecycle-author/state/project`.
Child argv: `stdbuf -oL <pinned DEBUG> --headless --path <private stage>
--log-file <role engine.log> -- --role=host|client --port=<owned loopback endpoint>`.
Source stage copies only committed S03 and private editor class/UID discovery;
strips addons/autoload in its scratch config, preserves renderer/physics, and uses
separate private XDG scopes with HOME unchanged. No shared cache is used.

One absolute 30s supervisor budget starts before identity hashing/staging/setup.
Work is bounded to 20s, readiness/client handoff to 4s from that same start;
existing shared-deadline owned cleanup reserves final receipt time. Two owned engine
children, one proxy socket; no process scans. Existing fault schedule is unchanged.
Actual UDP receive/send byte counts, sizes/hashes, endpoint and Python monotonic time
are logged even before schedule arming. Full stdout/stderr/engine/proxy/traffic and
command/result streams, including empty files, are retained.

Clock contract: Godot `Time.get_ticks_usec()` is elapsed since that engine started,
separate PID domains, NOT directly comparable between host/client. Parent Python
monotonic receipt/exit observations share one domain; poll status accompanies every
received event. These identify ordering bounds, not exact native exit/syscall times.

Independent expected held receipts in order: initial provisional NOT_ADMITTED;
then OK, STALE_SEQUENCE, STALE_CONTEXT, INVALID, INVALID, WINDOW, WINDOW, WINDOW;
resync provisional NOT_ADMITTED; old-control STALE_CONTEXT; new-control OK. Require
cut75/journal70/admission and resync entity/health70, exactly two consumed valid
frames and expiry to neutral, five received motion RPCs, health70 after subset
refresh and the original five-datagram hold/reorder/drop/two-refresh schedule.
Record first divergence and close reason rather than adjusting deadlines/results.
Two exit0 results do not pass strict diagnostics if native errors persist.

If no causal correction is established, deliver bounded partial diagnosis and the
specific next missing observation; no identical retry. A second set needs a
committed demonstrated material condition, fits remaining budget, and cannot use
debug evidence as release acceptance. Overall cap remains 3h lead, one editor,
one minimal dependency import <=90s, two exports maximum, two <=30s ENet sets.
One clean-context Sol6.1 HIGH reviewer assesses exact final HEAD/base and artifacts;
static review needs no editor lock and must not launch an unchanged runtime.

## Saved diagnostic candidate before the ENet set

The one author session started at 13:19Z, reached authenticated readiness in about
4s, and finished in 230s: editor 695199/connector both exit0, registry entry gone,
owned streams closed. Toolkit inspected the original full S03 tree/scripts, saved
the two additive script edits, compile-checked them, and completed a saved scene
close/reopen with `unsaved_changes_discarded:false`. All original S03 scenes, UIDs
and every other mirrored source are byte-identical. Only saved `session.gd` and
`proof.gd` were delivered back; no source checkout editor was involved.

The first style observation found 13 warnings despite exit0 (brace spacing and
callback ordering). One toolkit correction addressed these; strict pinned
format/lint then pass with zero warnings. A local Python request-generation edit
briefly produced a SyntaxError before any request was sent; its source/diagnostics
and a separately labelled capture rerun are retained. Corrected inverse readback
recovers the exact original scripts after removing telemetry. No gameplay outcome,
wait, deadline, RPC annotation or assertion was changed.

Authoring is NOT diagnostic-clean: saved-scene thumbnail creation reports
`Parameter "t" is null`; ordinary editor cleanup retains five RID ERRORs and
Canvas/CanvasItem/ObjectDB warnings. Full streams are retained, no exemption is
applied, and author exit0 is only mechanical completion. This is not a repeated
historical shutdown experiment or proof of its cause. The separately granted
addon-free debug diagnostic uses saved script checks independently; it cannot turn
these editor diagnostics or any historical failure into a pass. Initial private
editor dependency discovery was under 90s; no separate dependency import or export
was invoked.

## DEBUG diagnostic result and prospective RELEASE measurement

Sole DEBUG invocation on `f178c70efb657ea9fba5951d9440c23c761aea31` completes in
2.630392s aggregate including Python startup, staging, two processes, cleanup and
readback. Both full original case matrices exit0, zero runtime diagnostics, all 12
held receipts and health/resync/subset/expiry checks pass. Actual UDP receives are
120 datagrams/9659 bytes, sends 119/9413, with the exact five scheduled movement
packets. Parent receipt order observes host LEFT while live, then client HOST_LOST
while the host remains live, both IDLE, then observed process exits. Healthy
teardown itself includes client IDLE. This does NOT reproduce the historical
release failure, explain its first stalled step, or establish a gameplay correction.

ROOT prospectively authorizes the remaining ONE RELEASE diagnostic before a fix,
using identical saved telemetry. This is a changed measurement condition, not an
unchanged retry of the old uninstrumented release or credit from the debug result.
The second set has a stricter 27s aggregate budget, so both stay below 30s combined;
no third set, extra editor, dependency import, rule/deadline change or suppression.

Release preparation: `python3 tools/s08/lifecycle_release.py --output
/tmp/s08-lifecycle-release01 --revision <committed HEAD> --author-project
/tmp/s08-lifecycle-author/state/project`. One export command, at most120s plus
bounded owned cleanup, using exact installed dev7 exporter and already-present
TPZ/template. Verify the full TPZ SHA/version/four x86 members and Linux release
78376584-byte SHA256
`c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695` before export.
No acquisition or independent import/editor session. Copy only the 17 saved S03
files and already-completed private class/UID discovery, preserving renderer/physics;
normal main is original `s03/boot.tscn`. This intentionally excludes S01 assets/S08
asset entrypoint: those prior accepted positives are not rerun, and this set proves
only the original session API/case matrix in an instrumented release package.
Scratch main/preset changes are isolated export selection, not root config repair.

Freeze actual package identities before runtime: all actual PCK members/extents/
MD5/SHA256, logical remaps, class/UID caches, exclusions/output set, preserved source
bytes and template-exact binary. Direct authoritative journal mutation remains
outside asserts in unchanged `replication.gd`. Script hashes stay
`session.gd`: `bb77d7a0dd65ffd6d0e29da8489678cd3e24aa58470b026ea4f1570fd9ea84d7`,
`proof.gd`: `d11cb9065b894c112b24a3d5c6b934c94696e9c3575e10dd2aa7f74499954ff1`.
No other gameplay or saved UID/scene/node data changes.

Only after exact package/readback commit, invoke `lifecycle_diagnostic.py` with
`--release-bundle /tmp/s08-lifecycle-release01 --release-pck-sha256 <committed hash>`
and a fresh `/tmp/s08-lifecycle-release-set02` output. RELEASE child argv is
`stdbuf -oL <verified exported executable> --headless --log-file <role engine.log>
-- --role=host|client --port=<owned endpoint>`, cwd the export folder, no `--script`
or source project override. Same telemetry/12 held expectations/original scheduling,
new parent/PID clock domains and full UDP observations. Require actual release
outcomes independently; runtime errors remain strict failures even with exit0.
Retain the first failed boundary if any; ROOT decides subsequent scope.

Release preparation on `a5756b4b6126a5c9756de981b39fdadc35f3c8fe` passed: one exporter
699421, exit0/reaped, empty stderr/no diagnostics, 2.718s exporter and 4.787s entire
template/stage/export/inspection preparation. No explicit dependency import or new
author session. All 17 saved source/UID bytes remain unchanged after export. The
normal S03 main package has 23 actual PCK members, 10 logical remaps/UID rows and
seven S03 classes, no addon/native/other fixture families. Exact binary matches the
existing release template. New PCK: 122748 bytes, SHA256
`43cc8236fcb7a06f328c28cf45fed752d6630e1699ebea04e68e34d9aa40e3d7`.
Actual full package/readback identities and export streams are retained before the
second runtime; `release-launch.py` binds exact argv/source revision/PCK hash and
measures 27s aggregate/30s combined independently of the child supervisor timer.

## Final RELEASE observation and decision

Second/final runtime uses exact bound minimal S03 package. Aggregate runtime/setup/
cleanup/readback is 2.647172s; both sets total 5.277564s. Host699737/client699759 both
exit0 and are normally reaped with no signal fallback, socket and streams closed.
Original host/client case matrices and all 12 held outcomes pass; independent
literal trace checks also confirm exactly two consumed valid inputs, provisional/
ownership/invalid/window rejection, neutral expiry, preserved health/control during
resync, five received motion RPCs and actual five-datagram recovery schedule.
Existing unconditional proof checks establish cut75/journal70/admission/resync70
and movement-preserved70; this is not debug-assert credit. Actual transport receives
123 datagrams/9665 bytes and sends 122/9419; the dropped datagram is 246 bytes.

Strict release supervisor exits1: two host disconnect-nonexistent errors; client
four disconnect-nonexistent and two duplicate-connection errors. Both stderr and
engine streams retain all diagnostics. Successful outcomes do NOT make clean
teardown acceptance pass. Same client signal errors coexist with complete released
held/resync/recovery, so they are not sufficient to reproduce the historical stall
under this changed fixture/measurement condition. This does not prove harmlessness,
noncausality in the original configuration, or a sole engine defect.

Parent receipt ordering: host LEFT at98575.078181 while host poll is live;
client HOST_LOST at98575.088533 while host poll is still live; client/host exits
observed later at98575.150063/98575.180438. Both go IDLE after intended close, not
because of a reproduced early session loss. These are receipt/observed-status
bounds; separate Godot elapsed clocks are not incorrectly compared as global time.

Limits matter: no original S08 asset-main startup, shared editor, Steam installation
absence, other platform/device, drawable input or performance proof. Proxy servicing
uses this diagnostic supervisor's 10ms poll rather than the historical observer's
20ms poll; original gameplay timers and the hold/reorder/drop/refresh schedule are
unchanged. Telemetry/entrypoint/servicing changes can affect timing, so no claim
isolates the difference to one cause. Original cached release deadlines and all
historical STOPs remain failed. There is no authorized third measurement or spare
export just because one export allowance remains.

Next bounded question for ROOT: under a separately commissioned condition, inspect
actual release native cache comparator/connection registration across cancel/retry,
and compare the instrumented ORIGINAL S08 saved-main closure to this minimal
S03 result. Capture first stalled held/resync boundary and close reason if reproduced;
do not presume that avoiding/suppressing signal errors corrects it. Any source/native
repair or pin decision needs new scope and validation, not a speculative S03 change.

Consumed: one230s author session/one initial private dependency discovery under90s,
no explicit extra import; one export; two diagnostic sets, total5.278s; no acquisition,
shared editor/config/service operation, Steam initialization, merge/archive/push.
Owned writers are saved/quiescent. Full exported clean ENet, historical shutdown,
Steam absent/native/external transport, Windows/Deck/Gaming Mode/input/feel/drawability/
performance/private install and full S08/P0/M1/production gates remain open.

## Delivery base and preservation boundary

After inspecting the actual 43-path drawable-doc delta and 65-path Valve-doc/TODO
advance, rebased at the saved/quiescent boundary onto LOCAL main
`30471e6ae4c4ecbe01ce13313cd6d14c3b701bae`. Neither changes runtime code/settings/
resources or grants gate closure. One ordinary TODO table-line conflict was resolved
by keeping the exact accepted S03-S cell and changing only the authorized S08 phrase;
all other TODO bytes/tasks and added main files are preserved. Original runtime input
commits remain reachable through the scoped immutable ref recorded in the evidence
README. No measurements were repeated for these documentation-only advances.
