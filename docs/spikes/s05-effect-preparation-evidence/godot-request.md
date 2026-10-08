# Pending concrete Godot operation request

8 October 2026; source producer92400a44, workspacewks_437a9484cd5db686.
Commission base1229782, now rebased onto accepted0c84f01f2a0c817a5c6851a3a360e193a5f846d8.
**No launch/call/mutation is authorized by this card. Await explicit root grant.**
The same shared main editor/endpoint still has one writer; this proposal creates
an owned independent editor/bridge for this existing worktree, permitting parallel
authoring if actual isolation receipts pass. It does not relocate main483496.

## Installed capability and isolation proposal

Toolkit docs `addons/godot_mcp_toolkit/docs/multi-instance.md` explicitly support
Pattern A: distinct absolute project directories. Actual GDScript `port_config.gd`
accepts exact env pins and fails rather than scanning on collision. `security/auth.gd`
creates a fresh token at absolute GODOT_MCP_TOKEN_PATH. `registry_paths.gd` derives
its registry from XDG_DATA_HOME. `project_key.gd` hashes the canonical absolute
worktree path. The installed server1.0.3 `dist/index.js`, `startup/portConfig.js`,
`transport/tokenPath.js`, and `registry.js` implement matching project path, pins,
token override and XDG registry. Full identity receipt is committed beside this card.

This worktree's existing `.codex/config.toml` launches the unpinned `npx -y
@npgamedev/godot-mcp-server` with only config-version1. Do not call that connection,
reconfigure/reconnect it, or change any config file. Instead, after authorization,
launch an owned stdio client through the installed SDK to a separate bridge child:
`node /home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@npgamedev/godot-mcp-server/dist/index.js`.
Use the same private environment on bridge and editor, with cwd/project path exactly
this worktree. No downloaded package, extension or general routing framework needed.
The client invokes existing MCP tools, never the shared exposed tool namespace.

Root provisionally reserved ports, with no actual bind/scan/query now: editor WS16650,
runtime WS16670, LSP16015, DAP16016, remote debugger16017. Pin GODOT_MCP_EDITOR_PORT,
GODOT_MCP_RUNTIME_PORT and GODOT_MCP_LSP_PORT to those values on both processes;
GODOT_MCP_PROJECT_PATH=this worktree, GODOT_MCP_TOKEN_PATH=<private>/auth/mcp_token,
GODOT_MCP_CONFIG_VERSION=1. Create private auth/config/data/cache/log dirs under one
owned `/tmp/s05-godot-*` root (umask077), and set XDG_CONFIG_HOME, XDG_DATA_HOME,
XDG_CACHE_HOME there. Keep HOME unchanged. Own .godot cache lives only in this
worktree; other sources/configs and all main paths stay untouched.

Proposed exact editor argv: installed
`/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot
--editor --path <this-worktree> --lsp-port 16015 --dap-port 16016
--debug-server tcp://127.0.0.1:16017 --log-file <private>/logs/editor.log`.
The root-authorized `--help`-only call under private XDG/tmp exited0 in0.032s,
stderr empty/no private files, official4.8.dev7.c971f93e7. Full raw help/argv/exit are
retained. It explicitly documents editor debug-server URI, DAP port and LSP port
overrides, and log-file routing. The proposed flags/semantics therefore have actual
installed-build evidence. This help call started no editor/project/runtime and proves
neither listener binding nor private user-path behavior. If actual isolated startup
cannot isolate all listeners, stop: no invented flag, shared-setting change or
global repair. Ports fail closed if occupied; no fallback to main/default endpoints.

Actual isolation preflight must establish official engine pin, exact project root,
owned launch handle, private user/config/cache/log/token/registry paths, matching
project-key prefix `761b76f5e0fe`, port pins and route identity through the
private connection before any authoring call. Inspect only the private registry;
retain no token contents. Prove path/request mismatches fail before mutation.
Private XDG_CONFIG_HOME must isolate editor settings too: toolkit startup registers
personal settings and its responsiveness controller saves a backup in the registry.
Autoload already exists in project.godot, so startup self-heal should not write it;
compare all original project/pin/vendor bytes after startup and after cleanup.
Do not approve onboarding/config-write dialogs or change plugin enablement.
Any unisolated path/listener or unrelated persistent write stops this operation.
Static inspection is not actual zero-conflict proof.

## Exact prospective authoring scope

Root grants sole writer for NEW `art/models/spikes/s05_explosion_carrier.glb.import`
(actual engine-generated metadata), and new `tests/fixtures/s05_effect/` resources:
`explosion.tscn`, `presentation.gd` + actual `.uid`, `match.gd` + `.uid`,
`proof.gd` + `.uid`, `boot.tscn`, `burst.tscn`, `editor_harness.tscn`, and
`editor_probe.gd` + `.uid` only if the existing tools cannot instance a linked GLB.
Documentation/evidence remain beneath this handoff. Catalogue linking can be
coordinated as part of the later grant. No original accepted source/export/import,
scene, script, Damage/Replication/Session/S04 collision or placement is edited.

1. Refresh this editor's external files; import the new GLB with pinned engine.
   Inspect actual dependency/path/UID, unit root, converted bounds, materials and
   imported mesh ancestry. No fabricated sidecar/UID or copied render mesh.
2. Through suitable editor tools, create/save `explosion.tscn` with root Explosion,
   `Visuals/Model` linked GLB instance at saved identity transform. No collision,
   hierarchy creation at runtime or imported-child override. Source-only keyframe
   becomes one provisional static visible carrier for the accepted finite lifetime.
3. Create new `boot.tscn` inheriting immutable S05 boot, new `burst.tscn` inheriting
   immutable S05 burst, replacing only the new inherited script overrides and adding
   authored cosmetic `Presentation/Slots/Slot0..Slot7` instances of the saved effect.
   Each child's internal model transform stays authored. Instance root receives live
   event pose as cosmetic state; accepted cars/track placement stays unchanged.
   New Match subclass calls unchanged simulation APIs and injects saved car/effect
   refs into the presentation adapter; no child climbs to its parent/sibling.
4. Presentation adapter uses existing S05Presentation acceptance/deduplication fence,
   MAX_SLOTS8/LIFETIME_TICKS120 and existing live events (including Replication's
   `state.effects.consume` route), with finite per-slot generation/deadline state.
   A presentation-local monotonic lifetime advance must also expire effects on
   replicas without further host events; never advance Damage or write replicated
   lifecycle. Saturation advances history and drops visuals, never queues gameplay.
   `begin`/hydration/clear invalidate old callbacks/generations and hide all slots.
   New scripts/scene composition retain this single cosmetic owner.
5. Save each mutation batch. Refresh, safe-close/reopen/save base effect plus both
   inherited fixtures and inspection harness. Record actual UID/dependency/node/
   inherited IDs, ancestry and transforms before/after; inspect saved diffs. Use an
   editor-only helper only for a demonstrated tool limitation, authored through
   script tools and existing toolkit handlers, not an MCP extension/new framework.
6. Explicitly compile/lint only affected new scripts; resource checks cover new
   identities plus exact original-byte preservation. Exercise production APIs with
   literal expectations, never copied damage formulas or old whole-repo reruns.

## Finite observations and stop/cleanup criteria

Proposed budget: one editor + one bridge/client, <=60s startup/readiness, <=20min
bounded authoring/check session and one corrective batch for a local defect.
No shared editor operation. Root must grant drawable observations separately on a
named actual changed surface/condition meeting its declared receipt card. Merely
launching another Wayland process is not that changed condition.

With that additional grant: one finite12-event pressure row through accepted APIs
on host/live, then settled-hydrated observation; <=10s per observation after readiness,
at most one host/live/late set, <=3 actual runtime processes with private logs/user
dirs and owned handles. Existing12-car bodies/chain/S04 scene stay immutable. Positive:
eight actual linked carrier instances visible in automatic draw receipts, four actual
saturation drops, all12 authoritative outcomes and144 target visits unchanged;
duplicate/stale/future/session/generation events have no extra effect, hydrated
current wrecks produce zero historical effects, every slot clears within120 cosmetic
ticks and teardown invalidates generations. Record local lifetime/host ticks separately.
Hydration is settled only; no during-chain join/reset claim. Inspect log diagnostics,
camera/native surface/output/PNG against the root-approved draw card and retained IDs.
No force_draw, focus/window/input override, camera/model-placement correction or
renderer/device/config change. If the surface still reports can_draw=false, wrong
size, suspended required input or other declared negative, stop and retain failure;
no replay of the stopped S02 experiment. Actual costs remain unmeasured S07 work.

Without the drawable grant: stop after saved authoring/API/identity evidence and
report actual draw gates pending, or retain STOP_SOURCE_PREPARATION before launch.
Cleanup: stop only owned playtests through private toolkit/client and reap handles;
save authorized scenes, verify no unsaved work (never discard it), gracefully quit
only owned editor, bounded owned-handle fallback if necessary, close/reap bridge.
Retain full argv/stdout/stderr/engine logs/exits/hashes and raw failures. Compare
original bytes and new saved identities; private registry has no live owned entry.
No main PID query, restart, relocation or shared lease. Root alone integrates/archives.
