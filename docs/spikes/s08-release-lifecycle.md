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

## Phase A: ownership and qualified findings

S03 Session alone changes phase, closes peers and owns admission/operation mapping.
Its `_host_lost` initiates HOST_LOST; provider `close` waits 20ms before correlated
`closed`, which permits IDLE. Match owns entity/rig release and replication clears
attempt buffers. The provider's awaited timer cannot itself write Session.phase.
Proof awaits paced timers/helpers and never awaits `tree_exited`.

Exact dev7 public native source reveals a different `tree_exited` owner:
`SceneCacheInterface::_track` connects `_remove_node_cache.bind(oid)`; `clear`
disconnects the unbound callable. `SceneMultiplayer::set_multiplayer_peer` calls
clear during peer replacement. This is a qualified native connection mismatch,
not a demonstrated sole cause of gameplay loss. No engine/vendor change is allowed.
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

Full exported ENet, historical shutdown, Steam absent/native/external transport,
Windows/Deck/Gaming Mode/input/feel/drawability/performance/private install and full
S08/P0/M1/production gates remain open.
