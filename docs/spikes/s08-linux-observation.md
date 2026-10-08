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
subset_reorder_loss_recovery. Client movement_received=5, the native class
availability field `steam_available` must be false,
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

## Actual stopped observation

**STOP at the first exported asset observation; asset load and exported ENet NOT
passed.** Root reaffirmed the stop and held main at exact93da622 through handoff.
The predeclaration commit was `a32dfcd`; observer sources were saved at `e4299aa`
before engine execution. The source input remained that exact accepted base.
All operations used `/tmp/s08-observation-stpco415`; no shared surface was queried.
The [lossless evidence index](s08-linux-evidence/README.md) names receipts and limits.

| Actual phase | Observation |
| --- | --- |
| Acquisition | Available6,673,874,944 bytes before fetch covered archive,256 MiB extraction allowance and4 GiB headroom. One curl download,269 s, exit0; actual1,436,879,719 bytes/SHA256 exactly commissioned. No retry/install. |
| Verification | Safe ZIP manifest/version `4.8.dev7\n`; all four named members hashed and ELF64/PE32+ AMD64 verified. Only Linux release extracted. Installed engine151,398,728 bytes/SHA256 matches card. |
| Stage/import | Exact31 Git blobs and UID/import identities copied, no `.godot` copied; all31 still identical after import. Scratch preserved Forward Plus/Jolt/viewport, removed MCP/plugins/icon. One import2.72 s, exit0, all streams inspected/no diagnostics. No all-script compile claim. |
| Export | One release export2.72 s, exit0, no diagnostics. Exactly binary78,376,584 bytes and PCK180,988 bytes. Binary SHA256 `c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695`, identical to verified template. PCK SHA256 `4806cd62f3bb4b650a0cae86e466d535fca76569981ee2aa4d94af7018f51ea2`. |
| Static PCK | Actual unencrypted format4, flags2,46 entries; all MD5/extents and SHA256 checked.22 logical mappings include20 accepted runtime resources plus observer/input manifest. Imported GLB/texture payloads, scene/material remaps, compiled `.gdc` scripts, UID/class caches and project.binary present; dynamic entity/local rig included. No listed excluded entries. Static membership does not prove successful runtime resolution. |
| Analyzer correction | Initial assumption format3 failed before any asset launch; exact pinned `file_access_pack.h` defines current format4. Corrected offline analysis passed on the same immutable PCK, retaining initial failure and full source/header/outputs. No import/export retry. |
| Asset | One exact exported invocation below, exit1 in0.21 s, no timeout. It ran existing S03 boot and emitted `S03 {"cases":[],"event":"result","failure":"missing role","ok":false,"role":""}`. No `S08` receipt; the intended S01/UID/material/texture assertions did not run. stdout and engine log retain that result; stderr is empty. Runtime banner identifies4.8.dev7.official.c971f93e7. |
| ENet/cleanup | ENet not launched; no proxy/host/client created. Acquisition/import/export/asset owned handles all reaped, supervisor and stream handles closed. No shared process scan or kill. |

Exact failed asset argv (cwd the complete export folder):

```text
/tmp/s08-observation-stpco415/export-folder/FunThingsS08.x86_64 --headless --script res://s08_receipt.gd --log-file /tmp/s08-observation-stpco415/asset/engine.log
```

| Verified template member | Bytes | SHA256 |
| --- | --- | --- |
| linux_debug.x86_64 | 78,405,256 | `8b2871a1e2f8baf482282422f7e64cd7cfcc713eb53d8db671025b041bb23eb9` |
| linux_release.x86_64 | 78,376,584 | `c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695` |
| windows_debug_x86_64.exe | 105,650,176 | `c3287ae1c7fad6f6f2e0e09b0ebbb1321b49ec2423b74d513f12649e4c03bff6` |
| windows_release_x86_64.exe | 111,895,040 | `b538554df997ea699122d5b31f2ea8929301bcf3017e12dba664d85d351f60cd` |

The release template's observed handling of the card's `--script` invocation is
the stop boundary. No runtime cause, correction or alternate recipe is certified.
A future commissioned question is how to route an asset receipt through a supported
release entrypoint while preserving the saved S01/S03 inputs; it requires its own
protocol/grant. No repair/reexport/asset retry/ENet or further debugging is authorized.

Validation: focused probe formatting/lint, Python syntax, diff whitespace, immutable
source/31-input comparison, archive/package/member/remap/cache/exclusion inspection
and full actual log/result review. Original S01/S03/source assets, root project,
presets/pins/vendor/UIDs and accepted preparation remain unchanged. New observer
assertions and ENet supervisor code have no successful runtime validation here.
All full S08/asset runtime/exported ENet/strong Steam-unavailable/both-OS/Deck/input/
feel/offline/native-init/delivery/engine/P0/M1/production gates remain OPEN.
Independent review is of this stopped evidence and scoped code, not a passing package
runtime experiment; full reviewer report and exact disposition are retained in the
final HEAD's strict JSON delivery note without a report-only commit.
