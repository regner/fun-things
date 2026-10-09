# pistol_coral_stub — reusable static pistol handoff

9 October 2026. Pistol lead: Codex / Paseo `04572f3d-e2f3-4779-8e40-03a35caaecd5`.
Regner selected **A — Coral Stub** with “Lets go with concept A.” on 9 October.
Original concept/provenance: [selection gallery](../concepts/assets-v1/pistol/review.html),
[exact ImageGen prompts](../concepts/assets-v1/pistol/provenance.json).
Baseline `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`; asset-local production scope.
Regner approved the delivered Coral Stub static asset handoff with “Approved.” on
9 October 2026, after delivery commit `2f1846e9d883bbd15a0bcda4f826170b55ea2b5c`.

## Brief, ownership and current disposition

Smooth stylized short pistol for the ordinary city under dark vibrant cyberpunk lighting.
Coral upper slide, cream rear cap, petrol frame/dark grip and optional cyan status insert.
The large color masses carry overhead recognition; no real brand or external asset.
This workstream authored the original Blender geometry and materials from the selected
concept. Python bootstrap is original authoring tooling; the saved `.blend` is the source
of truth for subsequent edits and reexport. No third-party geometry/texture is incorporated.

Pistol lead owns source/export, local materials, wrapper, preview and checks. Regner owns
concept selection. Player lead owns shared humanoid rig, holding poses and hand offsets;
effects lead owns the flash/VFX. An external integrator owns gameplay/world use, collision,
authoritative muzzle queries, firing/damage/ammo, networking and production-player fit.
Shared planning/catalogue/TODO files remain untouched. The
[independent review](pistol_coral_stub-evidence/independent-review.md) accepts this
scoped static visual asset delivery with no actionable findings.

Owner routing update, 9 October 2026, applies prospectively: modeling/animation,
geometry, UV/skin deformation, spatial rig/rest/bone design, keyframes/poses/motion
and spatial VFX animation require **GPT-6-Astra**. Non-spatial Godot imports,
resource/rig/animation configuration, technical wiring and bookkeeping may use
**GPT-6.1-Sol medium/high**. The same boundary applies to subagents. Preserve
in-flight/unsaved work and verify the actual runtime before resuming spatial work;
end a Sol turn at its safe saved checkpoint if new settings cannot take effect yet.
No new worktree, duplicate lead, discarded work or process termination is authorized
by the routing update. Before any post-instruction spatial mutation, Paseo
`get_agent_status` verified this lead's `runtimeInfo.model=gpt-6-astra`,
`runtimeInfo.thinkingOptionId=high`, active turn `codex-turn-6`, session
`01a12094-4754-73a1-b9c5-6da017a10989`. The already-saved asset checkpoint
`117316a1ab182bcc13f59dfaa3f24c2fd72271ec` predates this instruction.

The asset is a static visual prop: no rig, clips or moving parts are needed for the selected
minimum presentation requirement. Textures are not applicable: six opaque flat PBR
materials meet the selected style. No collision, scripts, VFX or gameplay in the wrapper.
LOD tuning is deferred until measured; default import-generated LOD/shadow meshes remain.
Performance/device acceptance is unmeasured. This handoff does not close gameplay gates.

## Source → export → saved scenes

| Source / collection | Explicit output | Saved consumer |
| --- | --- | --- |
| `art/source/models/weapons/pistol_coral_stub/pistol_coral_stub.blend` / `export_pistol_coral_stub` | `art/models/weapons/pistol_coral_stub/pistol_coral_stub.glb` + `.glb.import` | `scenes/prefabs/pistol_coral_stub/pistol_coral_stub.tscn` / `Visuals/Model` |
| Same imported model, through reusable wrapper | Same GLB, no detached geometry | `scenes/prefabs/pistol_coral_stub/preview.tscn` / `Pistol` |
| Same wrapper, three held poses | Same GLB | `scenes/prefabs/pistol_coral_stub/preview_game_camera.tscn` / `North`, `East`, `South` weapon mounts |

Declared collection members and source sockets are in
[`manifest.json`](../../tools/pistol_coral_stub/manifest.json). Twelve render objects,
two source empties, six materials; 2,424 imported base triangles. No GLB images, skins,
animations, cameras, lights or compression extensions. No linked Blender libraries or
images. Source subtree is covered by committed `art/source/.gdignore`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, bundled glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**. Export uses the existing
`tools/s01/export_settings.json`, `export_animations=false`, named collection only.
Bevels, weighted normals and triangles are baked in the source; static scales are applied,
positive unit roots. Export only the declared collection. Cameras/lights are preview-only
saved Godot nodes. Reexport reads the saved source and never reconstructs geometry:

```bash
blender --factory-startup --background --threads 2 -noaudio \
  art/source/models/weapons/pistol_coral_stub/pistol_coral_stub.blend \
  --python tools/pistol_coral_stub/reexport.py -- /tmp/pistol_coral_stub.glb
cmp art/models/weapons/pistol_coral_stub/pistol_coral_stub.glb /tmp/pistol_coral_stub.glb
```

Use private XDG state/process ownership and pinned tool versions. Saved source reexport
was compared byte-for-byte with delivered GLB. Fingerprints and logs are in
[evidence](pistol_coral_stub-evidence/). Import sidecar retains Godot defaults including
root scale 1, generated LODs/shadow mesh and embedded material handling; no import suffixes
create collision. Wrapper imported children remain noneditable. Preserve model import UID,
scene UIDs, node identities, ancestry and socket paths on compatible reexports.

Preview-only reverse consumers also use unchanged S02 `s02_actor.glb` and `s02_ground.glb`
from `art/source/models/spikes/s02_kit.blend`; see [S02 handoff](s02_kit.md).
These are technical mannequins/ground, not newly produced player art. No S02 source,
export, import, fixture, S03-R or S06 consumer is modified by this new asset family.
No world placements, derived topology or runtime IDs are introduced.

## Measurements and attachment contract

Metres, Blender +Z up/+Y forward → Godot +Y up/−Z forward, converted once. Root is
the grip attachment pivot, identity transform; linked model has identity transform.
Imported rest AABB min **(-0.075, -0.205, -0.421)**, max **(0.075, 0.204, 0.143)** m:
width X **0.150**, height Y **0.409**, length Z **0.564** m. Measurement tolerance
**0.001 m**. Static bounds equal animated bounds because no clip/shader deforms geometry.
No effect extent belongs to this asset. Collider/clearance are external-integrator decisions.

| Source marker | Source parent | Godot rest pose | Stable wrapper / consumer |
| --- | --- | --- | --- |
| `socket_grip` | export collection, no bone | position (0,0,0), identity basis | `Sockets/Grip`; pistol origin aligns with player-owned `Sockets/WeaponMount` presentation mount |
| `socket_muzzle` | export collection, no bone | position (0,0.122,-0.421), identity basis | `Sockets/Muzzle`; effects/presentation, external gameplay authored relative offset |

Muzzle local forward **−Z**, up **+Y**. Cosmetic aperture radius **0.024 m**, diameter
**0.048 m**, front plane Z=−0.421 m centred Y=0.122 m. Source-authored transform is relayed
into saved wrapper marker; it is not a second manually tuned muzzle. Physics queries must
use the owning body's unsmoothed pose plus authored relative transform; the presentation
socket alone does not establish authoritative query behavior. The old S02 body-local
muzzle is not reused as a new production outcome rule.

Holding needs: one primary gripping hand at origin, optional support hand cupping the
same grip/guard region; no separate foregrip/shoulder contact. Handle width is about
0.117–0.122 m. Exact fingers/palm fit and support-hand contact await the player lead's
versioned `shared_humanoid_rig.md` and selected production hand. S13 fixture is not that
rig. No humanoid rig or holding clips are authored here. Effects confirmed no extra
anchor; measured transform/aperture were sent asynchronously on 9 October.

## Material contract

Each render object has one stable named slot; no multi-slot order ambiguity.

| Material / source slot | Source sRGB swatch | Roughness / metallic | Objects |
| --- | --- | --- | --- |
| `coral_shell` | (255,112,99) | 0.56 / 0.10 | CoralSlide, TriggerVisual |
| `cream_rear` | (246,235,210) | 0.66 / 0.00 | CreamRearCap |
| `petrol_frame` | (25,42,53) | 0.65 / 0.15 | frame, grip shell, guard, collar, sights |
| `dark_grip` | (19,25,32) | 0.85 / 0.00 | GripInsert |
| `cyan_status` | (59,225,233) | 0.55 / 0.00 | TopStatusInsert |
| `muzzle_dark` | (8,13,18) | 0.95 / 0.00 | MuzzleAperture |

Source swatches are explicitly converted to linear Principled base colors before GLB
export. Imported Godot StandardMaterial3D resources remain embedded in this GLB; there
is no shared material writer or runtime material mutation. Opaque, non-emissive,
no texture/UV density requirement or variant overrides. The small cyan insert is
decoration and does not provide gameplay feedback or carry overhead recognition.

## Preview and checks

Open `preview.tscn` for front three-quarter inspection or `preview_game_camera.tscn`
for the actual vertical camera. Neither replaces the project main scene. The latter
uses static S02 mannequin poses facing north/east/south, with provisional saved
mount `(0.43,1.2,-0.6)` m. Native capture is **1280×800**, perspective **47 m / 42°**,
vertical-down and north-up, near/far **0.1/160 m**. Close-up near/far **0.01/10 m**.
Compatibility/OpenGL 3.3 NVIDIA GTX1070 on Linux; neutral key plus ambient lighting,
not a production city/renderer/performance acceptance scene. No gameplay scripts in previews.

Private editor PID61057 / port16670 was verified bound to this worktree; private runtime
16671, LSP/DAP/debug16672–16674, XDG state `/tmp/brackett-pistol`. The exposed MCP connector
still targeted unreachable6550, so a temporary local authenticated client used the
existing toolkit commands at the verified private endpoint. `scene.instantiate` rejects
GLBs; the editor-only [bridge](../../tools/pistol_coral_stub/editor_bridge.gd) adds linked
imports and relays sockets through editor tool calls, then is detached before saves.
No direct authored `.tscn` writes were used. After external GLB replacement the editor
refreshed, closed/reopened and saved the prefab and both previews. Receipts are retained.

Checks performed: source/export freshness byte comparison; clean isolated asset-profile
import; focused resource checker for linked model/unit scale/12 meshes/6 materials/bounds/
source-relayed muzzle/no collision/no unwanted clips/camera; both owned scripts compile
checked through toolkit and pinned gdstyle; native and close-up graphical captures;
saved scene roundtrips. The resource checker runs with:

```bash
godot --headless --path . --script res://tests/fixtures/pistol_coral_stub/check_asset.gd
```

Log distinctions: Blender's known optional MeshOptimizer diagnostic is present; delivered
GLB has no compression extension. Initial sandbox authoring also reported unwritable
thumbnail/extension caches and saved files but hung in audio shutdown; those two owned
processes were stopped, then private-state unsandboxed exports
exited normally. Initial isolated checks had unwritable user-data/socket diagnostics;
private writable XDG/separate ports rerun passed without those errors. Vendor toolkit
reports an `int` constructor error at `unfocused_sleep_controller.gd:111` during auth on
this engine/private settings; requested tool operations still succeeded, and this is
not hidden or repaired in third-party code. Runtime captures/checks have no asset errors.

Visual observation: the coral top is visible beyond the hand in all three native poses,
but the pistol remains a small approximately 12 px shape; cream rear cap partially
merges into the pale technical hand. The large side concept is not native readability
acceptance. Production-player finger/support-hand fit, movement/aim poses, actual city
lighting/occlusion, effects bursts, physics/network behavior and device performance
remain pending with their respective owners.

## Acceptance and later reconciliation

| Stage | Status / owner | Evidence / limit |
| --- | --- | --- |
| Concept | accepted by Regner, 9 October | A selected; exact original prompt/selection retained |
| Source/export/import | checked, asset-local technical scope | committed source, explicit output, freshness, clean profile and measurements |
| Prefab/preview | checked, asset-local presentation scope | linked import, sockets, save/reopen, actual graphical views |
| Independent production handoff review | accepted, scoped static visual delivery | clean-context Sol6.1 medium reviewer `01e2af3f-334d-4831-9b95-7cf2e9031dc0`, candidate `b8363f55a6cfe8ab6cf02b1458a3d193629de59b`, base `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`; no actionable findings; [full receipt](pistol_coral_stub-evidence/independent-review.md) |
| Owner static asset approval | accepted by Regner, 9 October | “Approved.” for the delivered Coral Stub handoff at `2f1846e9d883bbd15a0bcda4f826170b55ea2b5c`; downstream fit/integration checks remain as listed below |
| Production-player/world/gameplay acceptance | pending, external integrator/player/effects | no completed gameplay/network/device claim |

Catalogue delta for later shared-file owner: add `pistol_coral_stub` → this handoff.
TODO delta: concept selection and scoped source/export/static wrapper/preview delivery
are complete, with independent review and owner approval accepted. Keep player grip/holding and gameplay/world/
effects/device integration tasks open. No unrelated foundation TODO is resolved.

The final receipt commit adds review evidence and updates handoff status only; source,
GLB, import metadata, scripts and saved scenes remain byte-identical to the independently
reviewed candidate. Both bounded graphical preview processes exited successfully.
The worktree-private editor retains the saved close-up preview for owner inspection.
