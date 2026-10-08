# S08 — Saved release entrypoint and assertion-safe ENet observation

8 October 2026. Commissioned sole implementation lead488b6000, workspace
`wks_e2ba2fe7704a8fa6`, branch `s08-release-entrypoint-enet`, verified Sol6.1 HIGH.
Accepted LOCAL main/base: `0c84f01f2a0c817a5c6851a3a360e193a5f846d8`.
This is a distinct bounded follow-up under existing unchecked S08. The accepted
[previous observation](s08-linux-observation.md#actual-stopped-observation) failed
its first asset invocation with S03 missing-role/exit1; its observer did not run
and ENet was never attempted. That history and its immutable evidence stay intact.

## Changed conditions and supported entry route

The exact pinned engine source is
[`c971f93e7e76b0ef919bf6009e7b868bea04db7f/main/main.cpp`](https://github.com/godotengine/godot/blob/c971f93e7e76b0ef919bf6009e7b868bea04db7f/main/main.cpp).
The retained source is214,477 bytes, SHA256
`1460993d3164d77f460b30b2e9a0a9d8f8d516e453c1bc30813966797cc35250`.
Its help marks `--script` as requiring path-override support (lines490–491,
638–645). The normal startup resolves `application/run/main_scene` when no
override is selected (lines4361–4373), loads/instantiates that PackedScene and
adds it as current scene (lines4777–4795). The user-argument separator collects
arguments into `OS.get_cmdline_user_args()` (lines1168–1169,2044–2045,2232).
The bounded read-only installed-editor `--help` exited0 with empty stderr under
private XDG paths; it confirms LSP/DAP/debug-server flags, not template behavior.

New saved `tests/fixtures/s08/release_boot.tscn` has one Node root and attached
`release_boot.gd`/engine-generated UID sidecar. The script performs explicit
release-enabled checks and emits one `S08` JSON receipt per process. It instances
the existing saved S01 roundtrip, checks linked/repeated models, appearance,
texture and resource identities, frees it, then either exits for `--role=asset`
or changes to the existing saved S03 boot for `--role=host`/`client`. S03 receives
the original role/port user arguments. Its saved hierarchy/RPC paths, dynamic
entity/local-rig scenes, authority, admission and lifecycle APIs remain in use.
There is no script/main-loop/scene CLI override and no authored runtime hierarchy
or generated render geometry. Root project settings remain unchanged.

The sole authorized existing S03 change executes `match_state.apply_journal`
outside `assert` in `replication.gd:40`, retaining a debug assertion on its saved
boolean result. `Session._world_ready` and `_resync` call `Replication.begin`;
`Match.apply_journal` owns injured health70 and durable revision advancement.
The proof independently checks health75 at the immutable baseline, health70
before admission and after resync/movement, fresh control/entity retention,
ownership, expiry and cleanup through its explicit `_check` API. Remaining S03
assertions only read byte sizes; they contain no required mutation. No broad
assertion/style refactor or other S03 behavior change is commissioned.

## Private authoring authorization request

Editor launch/authoring is **not yet granted**. Proposed private authoring mirror:
`/tmp/s08-private-488b6000/project`, containing exact accepted31 S01/S03 files
and an unchanged copy of the tracked MCP Toolkit addon only. No Steam addon,
native descriptor/library, source Blender/palette, other fixture, `.godot`,
credential, Git or shared configuration is copied. Scratch project keeps the
accepted rendering/physics/viewport settings and enables only the copied toolkit.
Its MCP autoload is present for toolkit startup, absent from the separate release
stage. This mirror is dedicated to this worktree's authoring; only the narrowly
changed S03 script and newly editor-saved S08 scene/script/UID are copied back as
identical bytes. Existing source/resource identities are compared before/after.

Exact editor executable is the pinned151,398,728-byte file:
`/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`,
SHA256 `6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd`.
Proposed argv: `--headless --editor --path /tmp/s08-private-488b6000/project
--lsp-port 17015 --dap-port 17016 --debug-server tcp://127.0.0.1:17017
--log-file /tmp/s08-private-488b6000/editor/engine.log`.
All editor/connector children inherit pinned `GODOT_MCP_EDITOR_PORT=17650`,
`GODOT_MCP_RUNTIME_PORT=17670`, `GODOT_MCP_LSP_PORT=17015`,
`GODOT_MCP_LSP_HOST=127.0.0.1`, project path equal to the mirror,
`GODOT_MCP_TOKEN_PATH=/tmp/s08-private-488b6000/editor/mcp_token`, and private
XDG data/config/cache/runtime directories under `/tmp/s08-private-488b6000/editor`.
Private directories use mode0700; token bytes never enter output or evidence.
No runtime/playtest launch is part of authoring. S05's reserved16650/16670/
16015/16016/16017 remain distinct and untouched.

Source mechanism: toolkit `transport/port_config.gd` pins exact WS ports or fails;
`security/auth.gd` supports the token-path override and requires an auth message;
`registry/store/registry_paths.gd` scopes registry/entries/locks to XDG_DATA_HOME;
`paths/project_key.gd` keys identity to canonical project path. Existing installed
Node package `/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@npgamedev/
godot-mcp-server/dist/transport/bridge.js` exports `createBridge` and editor `call`.
Its tokenPath module honors the private token override; `explicitEditorPort:true`
prevents port rediscovery. Private clients call the same toolkit editor command
handlers, with isolated registry reads and no shared connector switch/config edit.
No package download/install or framework/vendor change is needed.

After grant, bind/check only the five reserved private ports, close probes, launch
one owned editor handle and wait at most60 s for its private registry entry,
correct project path/owned PID/17650 and token file. Authenticate only17650;
verify editor-hint/project path and headless mode. Fail closed on wrong routing,
occupied endpoints, readiness timeout or unsupported commands. Do not repair the
framework, switch the shared connection or retry on another port.

Mutations through suitable toolkit editor handlers: surgical `script.edit` of
the one S03 call; `script.write` new S08 observer; `scene.create/open`, attach
script, and `editor.save_scene` for the new root. Scan/refresh before dependent
operations; validate scripts. Close/reopen/save/reopen the new scene and inspect
true scene/script/dependency UIDs and node IDs. Reopen affected S03 boot and S01
base/inherited roundtrip/variant for dependency verification, without saving
changes to originals. No private editor writes any S05 source, asset or fixture.
Toolkit console and raw editor streams are retained, with known toolkit diagnostics
distinguished from new errors. Save all mutation batches before switching scenes.
The main/shared editor483496, its16 saved tabs and shared configuration are never
queried, switched, focused, saved, quit or restarted.

Quiesce by saving and closing owned scene tabs after verification; request graceful
quit of this editor only, wait2 s, terminate/kill/reap surviving owned handles only.
Close connector handles and logs. Retain private registry/auth-path metadata with
no token contents; private scratch caches/config stay under `/tmp`. No global
process/listener/service inventory, shared cache write or unknown process kill.

## Ordered release observation predeclaration

Release operations start only after private authoring is separately granted,
resources are saved/verified, and protocol/source commits exist. One attempt per
phase, first actual failure stops later phases; no repair/re-export/retry/fallback.
Static analyzer/receipt corrections retain original failure and immutable bytes.

Reuse `/tmp/s08-observation-stpco415/Godot_v4.8-dev7_export_templates.tpz` and
`custom_template/release`. Actual fresh byte/hash reads rebind the1,436,879,719-byte
archive SHA256 `95c2677555b4f66c7eeca1a41368674703497e1907aad3fe56576423ca3c8cc6`,
version `4.8.dev7`, all four members and x86 architecture to the accepted manifest.
Linux release is78,376,584 bytes, SHA256
`c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695`.
Missing/mismatched artifacts stop; no replacement fetch/install/pin/SDK change.

Fresh `/tmp/s08-release-488b6000-*` stage uses exact committed candidate blobs:
accepted31-file S01/S03 closure with only the authorized S03 script difference,
new saved S08 scene/script/UID, and source-identity JSON. Record blob/size/SHA/UID/
import identities and source Blender/palette Git links without copying authoring
sources. Scratch-only project selects S08 release_boot as main, strips all addons,
MCP/autoload/plugins/icon and preserves Forward Plus/Jolt/native1280×800 settings.
Scratch Linux preset explicitly selects all saved/dynamic dependencies, verified
custom release template, x86_64, external unencrypted PCK. Binaries/PCK stay `/tmp`.

Let `E` be the exact installed engine, `P` the fresh stage project, `F` its complete
export folder and `B=F/FunThingsS08.x86_64`. Commands append dedicated `--log-file`
before the user separator; every phase/role has distinct private XDG scopes.

| Phase | Exact arguments and budget | Positive criterion |
| --- | --- | --- |
| Import | `E --headless --editor --path P --import --quit`;60 s | Exit0 and inspected clean streams; staged identities unchanged. No all-script compilation claim. |
| Export | `E --headless --path P --export-release "S08 Linux" B`;120 s | Exit0/clean streams, actual verified release binary and external PCK. |
| Pack inspection | Offline, same output bytes | Complete folder/PCK extent/hash inventories, logical remaps/import payloads/class/UID caches resolve; saved S08 main and S03 dynamic dependencies present. |
| Asset | `B --headless --log-file <asset-engine.log> -- --role=asset`;15 s | Exactly one literal `S08` ok:true receipt, saved asset/UID/link/material/texture checks, exact engine/executable identity, no S03 role launch. |
| ENet | Host: `B --headless --log-file <host-engine.log> -- --role=host --port=24740`; client analogous `--role=client --port=24741`;25 s combined | One positive S08 receipt per role before S03; host ready before client; distinct users; both literal S03 ok:true/exit0 and complete existing lifecycle cases; five-datagram proxy schedule. |

Required proxy events: armed, hold_subset_A, deliver_B_then_A, drop_subset_A,
refresh_subset, refresh_subset. Reuse only the existing narrow S03 proxy/result/
owned-handle cleanup logic, never its whole-repository/editor runner. Host cases:
provisional_rollback, authority_validation_and_expiry. Client cases:
provider_substitution_late_cleanup, baseline_cancel_retry, held_window_resync,
subset_reorder_loss_recovery. Require client movement_received=5, positive bounded
host baseline/held/movement sizes, native absence fields and all expected records.
Explicit release `_check` results establish admission/resync/ownership/expiry/
host-loss outcomes; elided asserts or exit status alone establish none of these.

Reject missing saved/imported/dynamic dependencies or UID errors, wrong identities,
incomplete/duplicate/false receipts, diagnostics, timeout or nonzero exit. Literal
folder/PCK membership excludes addons/native descriptors/SO/DLL, docs/captures/tools,
`.blend`/source palette, credentials, `.git`/`.mcp`, Steam app ID and other fixtures.
Imported remaps/cache payloads are observed representations, not31 literal filenames.
This proves addon-free execution only, not Steam uninstalled/stopped.

Retain full argv/environment policy/exit/timestamps, separate raw stdout/stderr/
engine logs including empty streams, proxy JSONL, results, input/output/package/
logical manifests and all failures. On any stop gracefully signal only owned child
handles, wait2 s, terminate/kill/reap survivors, close proxy and every stream.
Socket/sandbox failures stop without host/service repair. No graphics/timing/Windows/
native Steam experiment or expanded model/agent/profile inventory is commissioned.

One fresh clean-context Sol6.1 HIGH reviewer later receives raw commission,
accepted failed card/note references, exact base/candidate, source, protocol,
authorization, logs and limits, without an implementer verdict. Notify ROOT before
launch to serialize conflicting S05 review. Independent static source/literal
receipt/outcome checks suffice; no runtime reproduction is granted. Reviewer checks
remaining assertion side effects only in owned S03/new observer route. Fix material
findings with narrowly proposed affected validation; use the same reviewer for exact
final delta/rebase. Full meaningful reports/check sources/argv/exits/raw streams/
failures/expected path set/index/empty streams are retained losslessly in the exact
final HEAD's strict JSON note and verified by actual readback. No metadata-only loop.

Full S08, Windows, Deck LCD/OLED Gaming Mode/native1280×800/60/input/focus/feel/
suspend/offline gameplay/native init/private Steam delivery/access/engine choice,
P0-GATE, six-block M1 and production remain OPEN. DOC12/13 stay OPEN; this experiment
does not repair canonical guides or create a checkpoint. S05 ownership remains intact.
ROOT alone integrates/archives/pushes; delivery freezes saved work, clean tracked/
untracked status, exact reviewed HEAD/base, source/resource identities, evidence
readback and all owned children/connector/editor leases stopped.
