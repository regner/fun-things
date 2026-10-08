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
