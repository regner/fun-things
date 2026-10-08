# S08 — Standard private editor and saved release observation

8 October 2026. Direct sole Sol6.1 HIGH lead
`555e0330-1c44-47bb-a223-a8bdae88e605`, workspace `wks_c7fc8314996ebb13`,
branch `s08-standard-editor-release-proof`. Exact accepted starting LOCAL main/base:
`ef730df936b5b159f0894033f5d01e2b7124386c`; clean identity verified once.
This is a newly commissioned changed condition, independent of the consumed
[failed authoring grant](s08-release-entrypoint.md#actual-private-authoring-stop).
Prior STOPs, unsupported probe, toolkit diagnostic and failed release `--script`
route remain historical. Source hypotheses are not diagnoses. DOC12/13 are complete;
no checkpoint, profile, vendor, pin or accepted S05 source-only change is allocated.

## Committed pre-operation protocol

Owned root: `/tmp/s08-standard-555e0330`, with canonical `project` mirror. Copy exact
31 accepted S01/S03 closure files plus unchanged tracked toolkit inputs, preserving
all UID/import/inheritance metadata. Exclude `.godot`, shared config, Steam/native
addons, source assets and other fixtures. Scratch config preserves Forward+/Jolt/
1280×800; only authoring enables the unchanged toolkit/autoload. Root project stays
unchanged. Every child has private XDG config/data/cache/runtime and explicit engine
log paths. No global process/service inventory or main483496 operation is permitted.

**Supported changed settings mechanism:** pinned `EditorSettings::create()` creates
or loads the singleton; constructor loads defaults. `EditorInterface.get_editor_settings()`
returns it. Public `set_setting("mcp_toolkit/performance/keep_editor_responsive_unfocused",
false)` followed by `ResourceSaver.save(settings, settings.resource_path)` writes only
owned `XDG_CONFIG_HOME/godot/editor_settings-4.8.tres`. A cache-replacing ResourceLoader
readback requires boolean false. This uses engine serialization, no invented TRES.
Toolkit `plugin.gd:153–177` registers defaulttrue only if missing, preserving false;
`unfocused_sleep_controller.gd:104–107` returns before the old-key conversion when
opted out. Retained exact pinned EditorSettings source SHA256:
`28fc267db4c80c7d4bbc8993742c5b48a22ee2294ab7bc18f099ca0e613ad26b`.

One addon-disabled preparation project/child, at most15 s, performs that API write
before any peer authentication. Its script uses the editor singleton after deferred
initialization. Then one actual authoring editor, readiness at most60 s, session at
most20 min. Both use the pinned151398728-byte executable at
`/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`,
SHA256 `6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd`,
source `c971f93e7e76b0ef919bf6009e7b868bea04db7f`. No fallback/relaunch after failure.

**Standard discovery:** exposed connector has no per-call project override, so use
unchanged installed `@npgamedev/godot-mcp-server` bridge/portConfig/tokenPath modules.
Set only `GODOT_MCP_PROJECT_PATH` to canonical mirror, same cwd; no WS/runtime/token
pin. Toolkit selects first free6550–6560. Require private registry entry canonical
path/owned PID/actual WS, published token path inside owned XDG data; token value is
never output. `resolvePortConfig({}, project)` must return source=discovery/unpinned.
Only started engine listeners are isolated: select three available loopback ports
using socket bind0/close, pass help-supported `--lsp-port`, `--dap-port` and
`--debug-server tcp://127.0.0.1:<port>` to each sequential editor child. No LSP/DAP/
debug/runtime request is made. These are engine listener isolation, not five MCP
reservations. No unsupported disabling flags or shared registry/config repairs.

Readiness requires actual auth headless ack/version, dedicated `scene.open/get_tree`
for original S03 boot, node method scene-file-path identity, and node-scoped
Expression `get_tree()` methods identifying EditorNode and live
`MCPServer.is_unfocused_responsive_enabled()==false`. No Expression global singleton
probe. Require no new errors; distinguish the unchanged toolkit dev7/latest-tested4.7
warning explicitly. Verify copied source bytes unchanged before mutations. Raw
editor stdout/stderr/engine and connector stdout/stderr are separately retained,
including empty streams; parsed responses are additional receipts only.

After readiness, use suitable toolkit handlers to surgically edit only
`replication.gd`'s `apply_journal`: execute it outside assert, save typed boolean,
then debug-assert that result. Author new `release_boot.gd`, engine-generated `.uid`,
and saved `.tscn` single Node root/attached script/true IDs. Explicit release checks
instance original saved S01, inspect UID/model/repeated-wrapper/material/texture
contracts and literal S08 receipt. Asset role exits; host/client transition to saved
S03 boot via normal main/user args. Preserve all original APIs/RPC/hierarchy/UIDs.
Save each mutation batch; close/open/save/close/open new scene. Reopen affected
S03 and all original S01 base/inherited scenes without modifying their files.
One justified corrective mutation batch is allowed. No authored runtime hierarchy,
generated render meshes or placement override. Copy only exact saved new files and
narrow S03 bytes back. Check affected pinned format/lint, explicit compilation,
saved resource/UID identities and meaningful release public API journal health70,
authority/admission/lifecycle expectations. Import alone proves none of those.

## Conditional release sequence

Only after readiness, saved identities, meaningful affected checks and committed
protocol/source, freshly rebind existing TPZ under `/tmp/s08-observation-stpco415`:
1436879719 bytes, SHA256
`95c2677555b4f66c7eeca1a41368674703497e1907aad3fe56576423ca3c8cc6`, version4.8.dev7,
all four x86 members/architectures against the accepted manifest. Linux release:
78376584 bytes, SHA256
`c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695`.
No download/install/replacement. Fresh stage copies exact candidate31+newS08 files,
only one S03 difference, no addons/native/Steam/MCP/source. Scratch selects saved
S08 main; normal application launches use `-- --role=asset|host|client` and port args;
no `--script` template override. Preserve Forward+/Jolt resolution.

Ordered single attempts: scratch import60 s; export120 s; offline PCKformat4
inspection; asset15 s; ENet host/proxy/client25 s combined. Require complete output
folder/template identity, actual PCK members/remaps/import destinations/UID and class
cache/exclusion manifests; staged filenames differ from runtime representations.
Asset requires exactly one positive literal S08 receipt of actual saved outcomes.
Host/client each require S08 before actual S03, host ready before client, distinct
user scopes, two exit0/S03 ok:true results and existing explicit health70/admission/
rollback/resync/authority/held expiry/cleanup cases. Host cases: provisional_rollback,
authority_validation_and_expiry. Client: provider_substitution_late_cleanup,
baseline_cancel_retry, held_window_resync, subset_reorder_loss_recovery. Require
movement_received5, bounded positive payload sizes and five proxy datagrams/events:
armed, hold_subset_A, deliver_B_then_A, drop_subset_A, refresh_subset, refresh_subset.
Reuse narrow existing S03 proxy logic, never whole editor runner. No debugassert-
elided outcome claim. Addon-free proof does not show Steam uninstalled/stopped.

First actual phase failure stops all later phases. Preserve raw errors/exit/logs;
no engine/vendor/config repair/retry/reexport/force signal/window focus. Offline
receipt/checker corrections may retain failed source/stream without runtime rerun.
Track every owned Popen; graceful2 s then owned terminate/kill/reap only as needed.
Close connector/proxy/streams; clean only owned private registry/temp lifecycle.
Deliver bounded partial result promptly at STOP or completion. Full S08 unchecked;
Steam/native/private delivery/Windows/Deck/graphics/input/feel/performance/P0/M1 gates
stay open. Preserve S05 accepted2294 assets/links and new active owner56eb6b28/
wks_80583b9faf9f4332; no pending-result adoption.

Clean committed candidate then one fresh Sol6.1 HIGH clean-context independent
reviewer, notified to ROOT for serialization. Raw grant/requirements/base/exact HEAD/
contracts/source/logs, no implementer verdict and no runtime grant. One fix cycle;
same reviewer exact new delta after materialfix/rebase. Clean-boundary rebase onto
latest LOCALmain after inspecting accepted delta/TODO overlap. Same-HEAD note retains
complete new reports/sources/argv/exits/raw streams/failures/required empties, explicit
expected sets and actual decoded/hash/readback. Reference immutable prior notes
43140314/1229782 rather than copying giant historical packs. Final clean saved
quiescent worker never merges/pushes/archives; ROOT owns integration.

## Original prep STOP and distinct scan-complete ROOT grant

Original source0c46023/protocold5c8937 attempted only the preparation child555474:
exit0 in2.72 s; engine API save/cache-replacing readback reported booleanfalse,
editor_hinttrue/save0. Complete raw stdout/stderr/engine retain five RID-allocation
ERROR lines, scan-aborted/Canvas/CanvasItem/ObjectDB warnings. The supervisor's
strict diagnostic gate STOPPED before actual editor, authentication, mutation or
release. Original source/streams/lifecycle stay unchanged; this is not a clean prep
or a settings-cause diagnosis. The source-only S05 readiness relay is not S08 proof.

ROOT now explicitly grants ONE DISTINCT additional initialization condition:
finish actual initial filesystem scan/import, leave its completion callback, then
request deferred normal shutdown. This supersedes proceeding from the original
warning-bearing prep; do not repeat initialization again after this attempt.
New scope is `/tmp/s08-standard-555e0330/scan-complete-attempt`, fresh private XDG,
new `prepare-project` and distinct argv/stdout/stderr/engine/result files. Reuse only
byte-verified original31+toolkit mirror; no `.godot` copying or original stream overwrite.

Exact pinned `editor_file_system.cpp` SHA256
`2dd45efb21a8f62565c3f36b4b10f1b3f29578387536b16f4c8fc9c3f8d1b82a`,128067 bytes:
`is_scanning()` includes scanning/scanning_changes/first_scan; threaded completion
joins the scan thread, installs filesystem/updates actions and sets first_scanfalse
before `filesystem_changed` (1793–1809). Public is_scanning/is_importing/get_filesystem
are bound at3701–3703. Installed toolkit `editor.wait_for_idle` also observes
is_scanning. The new prep listens for the real completion signal, records actual
scanning/importing/root state, then defers a next-process-frame idle recheck before
SceneTree.quit. Exact pinned SceneTree source76957bytes SHA256
`4b04e0c3df187010102167245e5079127c3faaf474b2ac6325a82da6af73de34` shows quit sets
exit code/_quit (887–891), finalize deletes the owned root and flushes deletion
queues (856–872). No invented sleep/flag or suppression; actual clean streams and
exit/readback/idle receipts are required inside15 s, otherwise STOP remaining phases.
Fetch failures and source command/streams are retained separately.

On clean newprep only, ONE original-authoring editor allowance remains unattempted.
Actual startup uses read-only `editor_context.gd` through supported editor SceneTree
startup, proper Engine/OS/ProjectSettings/EditorInterface APIs, never Expression
singleton resolution. Its own editor_hint/PID/canonical path/full enginehash/live
private boostfalse/settingspath receipt plus matching registry/token and normal
installed discovery/auth headless/dedicated project/console/scene handlers establish
readiness within60 s. All other authoring/release/one-review budgets remain as above.

## Prospective distinct actual-editor phase grant

The additional prep557119/49b3f2a/2139034 also STOPPED: exit0/2.72 s,
real initial_scanningtrue -> completion signal with scanningfalse/importingfalse/
filesystem res://, deferred frame/idle receipt and save/readbackfalse. Scan-aborted
warning is absent; the same five RID errors and Canvas/CanvasItem/ObjectDB warnings
remain. This remains FAILED strict prep diagnostics, not clean runtime or a diagnosis.

ROOT explicitly commissions ONE ACTUAL AUTHORING readiness observation independently
of both prep shutdown diagnostic gates, prospectively. No prep is repeated or marked
passed, no suppression/vendor/renderer/pin/config repair. Use the existing second
private settings artifact unchanged, with fresh author/connector logs and lifecycle
under `/tmp/s08-standard-555e0330/actual-editor-attempt`. Owned artifact is
`scan-complete-attempt/private/config/godot/editor_settings-4.8.tres`:
prelaunch bytes/hash and exact source-qualified serialized booleanfalse are bound in
`settings-before-actual-editor.json`; live settings value is verified in actual context.
Correct mirror/pin/ownedPID/editor_hint/fullhash and private settings path, canonical
registry/published token/standard auth/headless and dedicated actual readiness commands
must pass within60 s. Actual editor/connector error/int/Expression/wrongidentity
fails before mutation; only the unchanged dev7/latest-tested4.7 warning is distinguished.
Prior prep shutdown errors are historical limitations, not actual auth errors.

Client handler failures after readiness are returned for local tool-gap assessment
without blindly quitting or discarding unsaved state. Identity/auth/facility failures
remain fatal. Save authorized mutation batches before switching/cleanup; no new
GLB helper is needed for the single Node S08 root. Successful readiness enables the
original narrow authoring/validation and conditional single release phases. One
20min authoring session/one actual editor, no fallback/relaunch after readinessfailure.

## Actual run01 STOP and separately granted corrected run02

Actual run01 at2f640c4 started editor558301 and connector558327. Own context proved
editorhint/fullc971/canonicalproject/privateboostfalse/settingspath and per-project
registry matched ownedPID/WS6551/published token path. Connector exited1 BEFORE auth:
implementer's client incorrectly required `_key` in `lookupProject()`'s projected
value. Installed `registry_projection.gd` explicitly erases `_key`; canonical path
is the `projects.json.by_path` key. Complete Node exception/empty connector stdout
remain. Owned editor SIGINT exit-2/connector1 were reaped; all streams closed.
No readiness pass, mutation, new S08 resource, S03 change or release phase occurred.
This is a client contract bug, not toolkit auth failure or stale-PID diagnosis.

ROOT explicitly grants ONE corrected actual-editor continuation run02, no prep
repeat/config/vendor/pin repair. Offline check against literal retained projection/
entry accepts exact canonicalproject/PID/publicport/token binding; rejects wrong
project/PID/port/token, missing entry waits without dialing. Supported standard
lookup/resolvePortConfig/token/bridge remain unchanged. Small client uses documented
projection shape; no unsupported projected `_key` requirement or custom routing.
Supervisor waits for BOTH current-Popen per-entry and matching canonical projection
within60 s, never dials stale/default/shared. Current Popen/argv is recorded before
gates. Fresh logs/lifecycle: `actual-editor-run02`. Existing owned settings artifact
is rebound/hashchecked before launch without rewriting. No third actual-editor
retry is granted. Remaining authoring/release criteria/budgets are unchanged;
one eventual independent review covers both prep STOPs and both actual attempts.

## Run02 STOP and independently granted stale-registration cleanup/run03

Run02 editor559412/connector559438 at1143e07 authenticated standard discoveredWS6551,
headlesstrue/4.8.0, liveboostfalse/fullc971/context/currentPID/route. Six dedicated
readiness handlers returned success. Full raw actual editor gate then STOPPED on
`ERROR: The process 558301 does not exist or is not a child of the calling process`,
backtrace registry_client.gd139 -> plugin_composer -> ws_transport. That names reaped
OWN run01 PID, not a queried peer. No mutation/release. Editor SIGINT-2/connectorEOF0
were reaped. No error is suppressed/relabelled as passed readiness.

ROOT explicitly grants ONE run03 after owned stale-registration lifecycle cleanup,
no prep/settings repeat/vendor/shared repair. Installed registry_client.gd149–163
normal deregister deletes its per-project entry, acquires private lock, rebuilds
projection and releases lock. `file_lock.gd` uses a regular private `PID:timestamp` file, PID-aware/10 s stale
recovery and bounded backoff; no live writer remains here, as all own handles are reaped. Actual
cleanup retained entry/projection, required canonicalkey and PID559412 in recorded
OWN558301/559412 set, and exact singleton private projection key before deleting
only owned entry/sole matching projection/token. No unrelated actual entry existed.
Offline fixture checks verify old key/PID absent and unrelated entry byte-preserved;
before hashes/actual absence/source/raw receipts are retained. No global PID scan.
Existing settings18167bytes/SHA49c7a18afbeb68e1d1c7aa586511c09b625bd05e210ad9e4c73c680e7939270e
and mirror sources remain byte-bound. Fresh unique logs under `actual-editor-run03`.

One editor <=60 s/context+currentPID+standard route/auth/dedicated handlers/complete
logs, stale-PID diagnostic MUST be absent (not exempt). Known dev7/latest-tested4.7
warning separately disclosed. Successful readiness enters narrow saved authoring,
<=20min, then original single release sequence. No further launch after failure.
Save each batch and inspect saved/unsaved state before supported SceneTree graceful
quit; wait2 s, owned SIGINT fallback only if needed. One eventual review covers all
attempts, raw failures and bounded result; source-only conditions are not diagnoses.

## Run03 transport STOP and distinct file-delivery run04 grant

Run03 at071be5e editor561147/connector561173 passed current canonical registry,
standard auth/context boostfalse/editorhint/fullc971 and all six dedicated readiness
commands. Complete ready streams contain only the known dev7 warning; no stale-PID
error. `script.edit` then saved exactly the commissioned S03 replacement, typed
boolean/outside-assert, diagnostics[]/validtrue. No other closure file was changed.

The next 8184-byte JSON script.write terminal request was rejected by automatic
review: "terminal input and permission details are too large to review safely; use
a smaller input or start a new terminal with fewer grants". Splitting its bytes
across the canonical PTY lost bytes beyond its line limit; supervisor STOP was
`JSONDecodeError('Invalid \escape: line 1 column 4095 (char 4094)')`. The request was
never issued to the connector; no S08 script/scene/UID exists. Both owned handles
were reaped via existing fallback (editor SIGINT-2, connector EOF0), all streams
closed. Normal SceneTree quit was not reached. This is implementer transport error,
not a toolkit/renderer/facility defect. Preserve raw STOP and all earlier failures.

ROOT explicitly grants ONE continuation run04, no prep/repeated S03 edit, from
existing private imports/settings and saved S03 bytes. Before launch, offline
`request_file.read_request` verifies an owned real file, SHA256, complete UTF8 JSON
and method. The actual representative8184-byte request (7464-byte script) readback
is exact; wrong hash and outside-scope file are rejected. Terminal sends only a
155-byte path/hash control. Supervisor copies original request bytes before issuing
unchanged installed bridge SDK calls through its ordinary pipe. This is local
file delivery, no new MCP protocol/router or string splitting. Original rejected
request and failures stay retained separately; no fabricated mutation receipt.

Source-qualified cleanup retained current private entry561147 and matching singleton
projection, proven against recorded/reaped run03 handles; removes only its canonical
entry and rebuilds the empty private projection. Synthetic unrelated row unchanged.
Actual `projects.json.lock` is absent; no writer/lock/global PID query. The executed
cleanup initially checked `projects.lock` (incorrect basename); the correct
source-defined `projects.json.lock` absence was separately asserted before run04
and the helper corrected. The original completed execution `exec-bd59a5ba-18c1-48ac-9ad1-6a045260e29c`,
full argv/stdout/empty stderr/exit0 is now retained at
[saved original lock check](s08-standard-editor-evidence/cleanup-before-run04/correct-lock-original-command.json).
It was recovered from the contemporaneous session event, not replayed. Both the
wrong-basename executed source and later correction remain. No lock repair.

Normal prior editor lifecycle saved the same private EditorSettings artifact;
current bytes18280/SHA7921c8f2cd4efbc3ef334415e174d4e1a6bb4567d07a04f4bd64eb7272ae1588
are freshly read/bound, exact supported booleanfalse preserved without a write.
Live run04 context must confirm it; old prep hashes/receipts remain immutable.
Verify unchanged installed inputs plus EXACT one saved S03 delta; reopen actual
S03 scene/script/UID before new resource authoring. Readiness <=60 s, authoring
<=20min, standard automatic route/current Popen PID recorded before gates, complete
clean auth/handler logs (only known dev7 warning), no stale-PID exception. First new
actual failure STOP; no further launch. Save each batch and inspect saved/unsaved
state before supported node-scoped `get_tree().quit()` and wait2 s; owned SIGINT
fallback only if unresponsive. Conditional original import/export/asset/ENet budgets
remain unchanged. One eventual exact-candidate review covers ALL attempts.

## Actual run04 authoring shutdown STOP; distinct addon-free grant

At364ee38 run04 editor563623/connector563653 passed readiness, authored the7464-byte
S08 script with trueUID `uid://cffyguysng6st`, sceneUID `uid://dn1ownu7vk3h2` and
single Node rootunique_id911609923. All41 handler calls succeeded; saved scene
roundtrip and original S01/S03 reopens/closes report no unsaved discard. Exact31
closure differs only in the commissioned S03 script, existing UID unchanged.
Affected pinned format/lint pass. Normal node-scoped get_tree().quit returned success;
registry deregistered, both child exits0/reaped and streams closed.

Complete shutdown stdout has five RID ERRORs, stderr Canvas/CanvasItem/ObjectDB170
warnings. AUTHORING_SHUTDOWN strict STOP stands. Supervisor finishoktrue only records
local command completion, NOT a diagnostic pass. No renderer/toolkit cause inferred.
No subsequent editor/prep/mutation is granted. Complete raw streams are retained.

ROOT explicitly commissions distinct addon-free validation/release observations
against exact committed saved bytes independently from that shutdown gate. Before
launch, bind34-file closure, original31 preservation except S03, three saved S08
identities and installed engine hash. Validation mirror removes toolkit/autoload/
native/Steam, retains ONLY needed owned imported payloads and filtered class/UID
cache for these resources. No engine import/editor runs in preparation of this probe.
ONE standalone SceneTree API probe <=60 s, private XDG/runtime/log scope, explicit
ResourceLoader CACHE_MODE_REPLACE and GDScript.reload on ONLY changed replication
and S08 script; resolve every saved dependency/UID. Instantiate original saved S03
boot off-tree (so network proof never runs), use public Match APIs for literal
health75->70, obsolete journal nonmutation, provisional/admitted/replica rejection,
resync preserving70/entity, closed admission, stale control and rollback cleanup.
All expectations are explicit bool checks outside debug assertions. Require exactly
one positive S08_API receipt, exit0 and error/warning-free full stdout/stderr/engine.
Unexpected failure STOP remaining distinct phases; no retry/fallback/error exception.

Only if probe passes, freshly bind existing exact TPZ/version/four members and exact
Linux release template/installed binary, ONE clean addon-free scratch import60 /
export120 / offline PCK4 inspection / asset15 / ENet25 original sequence, normal
saved S08 main/userargs. The authoring STOP is never erased or treated as clean;
addon-free proof does not establish Steam uninstalled/stopped, graphics/device/
performance/production acceptance. All full gates remain OPEN. One eventual fresh
Sol6.1 HIGH static independent review covers all grants/attempts/source/streams;
ROOT serializes after S05 if ready. No reviewer yet.

### Probe orchestration gap before any child

At3636b84 the first source-only probe runner staged the exact candidate and owned
filtered caches, then raised `TypeError('launch() takes 5 positional arguments but
6 were given')`: it imported the historical launch helper but called the draft's
private-env signature. No Popen/engine invocation occurred, no API phase/log directory
exists. Preserve full supervisor stderr (empty)/stdout/observation and source3636b84.
This is implementer Python contract error, not script/resource/runtime failure.
Correct the scoped helper using the already inspected draft launch function with
explicit env_factory; offline inspect.signature.bind validates the six arguments.
No engine/probe retry is involved: the granted ONE standalone child remains
unattempted. Fresh unique probe02 retains new source/argv/logs; probe01 never replaced.

## Bounded addon-free outcomes and exported ENet STOP

Exact source21b77cb: standalone child566755 exit0 in0.315 s, all106 explicit
compilation/resource/UID/public-API checks pass, no stderr/error/warning. Probe01's
Python signature gap remains separate and launched zero engine children.

One release attempt freshly hashes the existing1436879719-byte TPZ, version4.8.dev7,
four x86_64 members and exact78376584-byte Linux release template/installed engine.
Addon-free exact34-file stage passes post-import byte readback. Import567033 exit0 /
2.72 s, export567062 exit0 /2.72 s, complete output ELF exactly matches template.
PCKformat4 has48 fully hashed members,23 logical mappings including manifest,
22 decoded UID rows matching probe IDs/paths and expected scoped class cache;
no addon/native/source/other-fixture leak. Raw package/config/cache/exclusion
manifests and actual output hashes are retained.

Normal saved-main asset567092 exit0 /0.514 s, exactly one literal S08 ok:true,
roleasset,172 explicit checks/22 resources. All44 reported runtime payload hashes
match actual PCK members. This is actual asset execution, distinct from static pack.

Exported host567114 emits S08 ok:true BEFORE saved S03 ready, then S03 result
ok:false/`case deadline in ACTIVE`/cases[]/exit1. Runner stops immediately on failed
result. No client process was created, no connection outcome or exported ENet
case is passed; proxy0 datagrams/events[], actual raw proxy.jsonl is empty. Owned
host reaped/socket closed/streams closed. No reexport/retry/behavior repair.
Full S08 remains unchecked; asset/API partial positives do not erase authoring
shutdown STOP or establish Steam uninstalled/stopped, native transport, graphics,
input/feel/Deck/Windows/device/performance/production acceptance.

### Source and existing-receipt readiness-handoff assessment

A bounded offline assessment reads current observe.network and original S03 runner/
proof, exact pinned logger.cpp/logger.h and accepted cached main.cpp property source.
The runner requires complete newline records, sets ready, drains remaining complete
lines, raises on failed result before the outer client-start predicate. Existing
receipts prove it consumed ready and failure before that conditional; only host
command exists. Parent ready decode1791451408.2456071 is8.464263 s after Popen start,
compared with literal S03 CASE_DEADLINE_MS8000. That is decode timing, not emission
or exact child-exit timing; neither was captured in host prints.

Pinned main.cpp defaults application/run/flush_stdout_on_print false, debug override
true, then sets Logger's property. StdLogger uses vprintf and calls fflush(stdout)
only when enabled. Scratch config has no explicit override; host stdout is a regular
file. Historical runner used the pinned development binary, not the release template,
with a similar readiness protocol. This is a source-supported buffering hypothesis
consistent with late receipt, not a demonstrated sole cause from exit1. No runtime
property/syscall/buffer measurement exists. Full fetched sources/argv/exits/raw streams,
main source hash/excerpts and raw readiness/result byte offsets are retained.

Concrete future condition under this same S08 owner: qualify a release readiness
handoff observable while host remains within its case budget; predeclare receipt
consumption order and explicit release output behavior in a distinct ROOT grant.
No working remedy, source behavior repair or new experiment is claimed here.
