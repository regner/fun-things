# S08 — One isolated Linux release observation

8 October 2026. Direct commissioned lead `076a388a-e638-4855-a91a-6f1965ff68c2`,
workspace `wks_aa2a7ef710b90059` / `s08-linux-release-observation`. Paseo's own
snapshot confirms configured/effective `gpt-6.1-sol`, HIGH, auto-review.
Accepted input: `93da622554e5739cf05bd2267d11b4c6745e4e2e` (LOCAL main).
The accepted [preparation card](s08.md#next-linux-desktop-observation-card--root-commission-required)
is dated history; this distinct operation is authorized by the supplied commission.
Full S08 remains OPEN. This protocol is saved and committed before engine operations.

## Question, scope and stop protocol

Can one exact Linux x86_64 release package carry the unchanged saved S01 imported
closure and all17 S03 files, omit development/native Steam dependencies, load the
saved assets, and pass the unchanged real ENet lifecycle/fault proof?
This existing environment cannot prove Steam uninstalled/stopped. Only addon-free
package execution is commissioned; that stronger ENet gate remains OPEN.

No shared Godot/Blender/display/editor/PID/service/Steam query or mutation is
authorized. The main editor stays untouched; authoring lease is UNASSIGNED.
Only private scratch CLI children and a private loopback proxy are permitted.
No graphics, timings/benchmarks, Windows execution, native Steam load/init, private
delivery, device/account requests, root project/preset/pin/vendor/resource changes,
canonical guide sweep, checkpoint watermark or profile configuration.

Finite ordered phases, one attempt each, FIRST failure stops later phases:

| Phase | Budget and criterion |
| --- | --- |
| Acquisition | Before fetch, available space must cover the 1,436,879,719-byte archive, extraction allowance and at least4 GiB remaining task headroom. One official URL download, at most600 s, no retry/mirror/pin fallback/global install. |
| Archive verification | Exact size/SHA256, safe ZIP names (no absolute/parent traversal, duplicate names or symlinks), exact version4.8.dev7, four named members hashed and ELF64/PE x86_64 verified. Extract only Linux release into `/tmp` custom template. |
| Import | One exact installed engine `--headless --editor --path <stage> --import --quit`, at most60 s. Exit0, no warnings/errors. Import is not all-script compilation. |
| Export | One `--headless --path <stage> --export-release "S08 Linux" <folder>/FunThingsS08.x86_64`, at most120 s. Exit0, no warnings/errors; binary plus separate unencrypted PCK. |
| Package inspection | Full folder and PCK path/size/hash inventories; generated remaps/imports/script/UID/class caches inspected, complete logical dependency resolution, exclusion checks and correct executable ELF64/template identity. |
| Asset receipt | One exported binary from export folder `--headless --script res://s08_receipt.gd`, at most15 s. Runtime engine identity and saved S01 load/link/repeated-wrapper/material/texture assertions, dynamic S03 scene and script resolution; no Steam class/singleton/MCP autoload. |
| ENet | One exported host/private proxy/client at ports24740/24741, at most25 s combined. Host ready before client; distinct private user directories; both result records literal ok:true and exit0; exact unchanged five-datagram reorder/drop/two-refresh schedule and lifecycle cases. |

Exact acquisition URL:
`https://github.com/godotengine/godot-builds/releases/download/4.8-dev7/Godot_v4.8-dev7_export_templates.tpz`.
Published asset603460756, SHA256
`95c2677555b4f66c7eeca1a41368674703497e1907aad3fe56576423ca3c8cc6`.
Publication metadata is distinct from actual downloaded-byte proof.
Required ZIP members under `templates/`: `version.txt`, `linux_debug.x86_64`,
`linux_release.x86_64`, `windows_debug_x86_64.exe`, `windows_release_x86_64.exe`.
Installed engine:
`/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`,
SHA256 `6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd`;
runtime version `4.8.dev7.official.c971f93e7`, full official source
`c971f93e7e76b0ef919bf6009e7b868bea04db7f`. Stop on any mismatch.

## Inputs, representation and independent expectations

Fresh `/tmp/s08-observation-*` staging reads exact accepted Git blobs, never
copies `.godot`, and records source blob IDs, bytes, SHA256, UIDs and import sidecars.
The exact31-file staged input set is14 S01 closure files plus all17 S03 files.
S01: four saved scenes `roundtrip`, `static_prefab`, `static_variant`, `rig_prefab`;
`fixture_identity.gd` and UID; two `art/models/spikes/s01_{static,rig}.glb` and
their imports; `art/materials/s01_{petrol,coral}.tres`; palette PNG and import.
S03: `boot.tscn`, `entity.tscn`, `local_rig.tscn`; `entity`, `fake_transport`,
`match`, `proof`, `replication`, `session`, `transport` scripts and seven UIDs.
Source Blender/palette links remain in Git evidence, outside stage/package.

Scratch project uses saved S03 boot as main. Preserve the source Forward Plus
feature, Jolt, viewport1280×800/stretch and rendering values; remove addons,
MCP autoload/editor plugins and unused root icon only in scratch. No saved input
resource is edited. A receipt script is the only added runtime observer. Scratch
preset explicitly selects saved S01 roundtrip and S03 scenes/scripts including
dynamic entity/local rig, plus observer; Linux release/x86_64 custom verified
template, embed_pck=false/encryption=false. No global templates are installed.

The31 source files are NOT the literal PCK membership expectation. Independently
inspect actual representations: converted scenes/resources/scripts, rewritten
import remaps, selected generated payloads, UID/class caches and project.binary.
Bind each logical runtime dependency to the actual entry/path/hash and successful
load. Require S01 UID resolution, both GLB-linked saved Models, StaticA/StaticB and
RigA/RigB wrappers, coral variant appearance and petrol palette texture resolution.
Do not author geometry, placement, collision or body rules.

Unchanged S03 public result expectations: host cases exactly provisional_rollback,
authority_validation_and_expiry; client cases exactly
provider_substitution_late_cleanup, baseline_cancel_retry, held_window_resync,
subset_reorder_loss_recovery. Client movement_received=5, Steam unavailable=false
as a native class availability field (the actual key `steam_available` must be false),
positive bounded baseline/held/movement bytes where produced. Existing assertions
cover baseline-before-admission, canceled cleanup/retry, stale native result disposal,
sender ownership, malformed/nonfinite/window/context/sequence rejection, injured
health/entity retention on fresh-control resync, obsolete marker rejection,
held expiry, subset refresh and host-loss teardown. This is the tiny unchanged S03
proof, not full gameplay/lifecycle/production or another transport acceptance.

Required proxy events exactly: armed, hold_subset_A, deliver_B_then_A,
drop_subset_A, refresh_subset, refresh_subset. Reuse only narrow parsing/proxy/
result/owned-child cleanup logic from `tools/run_s03.py`; do not execute its runner,
editor staging or whole-repository compilation path.

Full folder/PCK negatives: addons, native descriptor/SO/DLL, Steam/MCP caches or
autoloads, docs/captures/tools, `.blend`, source palette, `.mcp`, `.git`, credentials,
steam_appid and unrelated fixtures absent. CLI scratch settings exclusions and
actual PCK byte membership are separate checks. No missing imports/dynamic scenes,
UID fallback errors, diagnostics, timeout, nonzero exit or incomplete receipt passes.
Inspect ALL stdout, stderr and engine logs without broad suppression.

## Evidence, cleanup and handoff

Each phase/role receives unique private XDG data/config/cache and dedicated stdout,
stderr, engine logs (retain empty files), result/argv/environment/exit manifests.
The supervisor owns actual Popen handles: graceful signal then2 s, terminate/kill
and reap surviving owned children only; close private proxy and all logs even on
failure. No process scan, unknown kill, listener/service repair or environment fix.
Socket namespace/startup failure is retained STOP, not permission to expand scope.
No experiment rerun; static receipt/analyzer corrections retain original evidence.

Retain lossless raw receipts/manifests and meaningful new source in the same final
HEAD's committed minimum evidence or strict JSON note. Reachable old Git blobs/
size/SHA references suffice; no copied immutable trees/recursive note dumps or
template/package binary bloat. Archive/template/export binaries stay `/tmp` with
hash manifest. Explicit evidence path sets include indices and empty streams;
read back retained evidence. Before reviewer launch notify root for checkpoint
serialization; rebase only at a saved clean boundary onto its exact accepted
revision. One fresh independent clean-context Sol6.1 HIGH reviewer receives raw
commission/card/protocol/grant/base/exact candidate/source/evidence/limits with no
implementer verdict. Static receipt/source/outcome assessment suffices; reproduction
needs a new root commission. Same reviewer assesses any exact final delta/rebase.
Final handoff is frozen, clean including untracked files, children exited/proxy
closed, exact reviewed HEAD/base/receipt condition and source preservation reported.
No merge/archive/push; root owns integration/lifecycle.

Both OS/Deck Gaming Mode/native1280×800/60/input/focus/feel/offline gameplay/native
Steam initialization/engine choice/Steam delivery/P0/six-block M1/production/full
S08 remain OPEN. S02's stopped Wayland result supplies no packaging or physical
target validation.
