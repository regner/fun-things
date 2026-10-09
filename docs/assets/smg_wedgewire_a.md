# smg_wedgewire_a — Wedgewire SMG handoff

9 October 2026. Regner selected **C — Wedgewire** from the
[original concepts](../concepts/assets-v1/smg/README.md). This is a reusable rigid
weapon visual and asset-local review scene. Equipped player poses and gameplay
integration belong to their respective owners and remain pending.

## Files and review

- [Blender source](../../art/source/models/weapons_smg/smg_wedgewire_a.blend)
- [Explicit weapon GLB](../../art/models/weapons_smg/smg_wedgewire_a.glb)
- [Reusable wrapper](../../scenes/prefabs/weapons_smg/smg_wedgewire_a.tscn)
- Actual Godot captures: [overview](smg_wedgewire_a_evidence/overview.png),
  [side](smg_wedgewire_a_evidence/side.png),
  [native 1280×800 game camera](smg_wedgewire_a_evidence/game_camera.png).
- [Evidence gallery](smg_wedgewire_a_evidence/index.html).

SMG lead `c39c4577-4fa7-4fdf-9123-db3e81a3c554` owns brief, original concept prompts,
source, export, wrapper and local review. Regner owns art selection. Player lead
`7016b739-5eea-480c-afa3-2c0cbad484a2` owns the shared humanoid rig/holding clips.
Effects lead `c9207bb9-925b-46e4-bd68-e37aaa66a617` owns all flashes/trails/shells.
External integrator owns gameplay, equipment and world placement. No shared source,
material, scene, catalogue or TODO was modified by this asset.

## Authorship and model routing

Original fictional design and geometry; no real brand, downloaded mesh, external
texture, font or linked library incorporated. The selected generated image is a
reference, not model source. [Exact imagegen prompts](../concepts/assets-v1/smg/prompts.json)
record the concept tool inputs. The committed `.blend` and scoped Python authoring
scripts preserve original source provenance. Geometry uses broad bevels, simple
opaque palette regions and a tapered plan/profile; the cyan band wraps both sides.
Unrequested slogans, backgrounds and small sight details from the sheet were omitted.

The owner's prospective routing instruction requires Astra for modelling, UV/skin
deformation, spatial rig/rest/bone design, poses/keyframes/motion and spatial VFX
animation. Sol 6.1 medium/high may handle non-spatial Godot configuration, imports,
technical wiring and records. The first source preceded that instruction. Subsequent
spatial refinements ran only after Paseo verified active runtime `gpt-6-astra/high`,
turn `codex-turn-9`; [receipt](smg_wedgewire_a_evidence/model-routing.json).
Any later spatial work must verify effective runtime again after a model switch.

## Source/export map

| Saved source / collection | Explicit output + sidecar | Consumers |
| --- | --- | --- |
| `art/source/models/weapons_smg/smg_wedgewire_a.blend`, `export_smg_wedgewire_a` | `art/models/weapons_smg/smg_wedgewire_a.glb` + `.glb.import` | Wrapper `Visuals/Model` |

`art/source/.gdignore` excludes authoring files from Godot. A one-metre measurement
fixture lives in nonexported `source_measurement_reference`. There are no exported
cameras/lights, textures, animation tracks, armature, skin or collision hints.
The weapon export contains 16 mesh objects and five empties; 3,748 source triangles.
Source membership, settings and AABBs are in
[export_receipt.json](smg_wedgewire_a_evidence/export_receipt.json).

Blender **5.2.2 LTS d13f752e3b9c**, bundled glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**. `tools/smg_wedgewire_a/export.py` opens the
saved source and uses the inspected S01 export settings with explicit collections,
animations/skins disabled. Modifiers and triangulation are baked in source; explicit
corner normals are set after triangulation. Reexport never regenerates geometry.
The bootstrap/refinement scripts are historical authoring actions, not a build step.

Default per-asset Godot import settings remain in the source `.import` files:
root scale 1, LOD/shadow-mesh generation enabled, embedded material handling,
normal/tangent import defaults. No shared import setting changed. Materials remain
linked inside the imported model; imported children are not editable. No vertex arrays,
primitive meshes or runtime-generated visible geometry occur in owned scenes/scripts.
Resource UIDs and editor-generated node IDs are preserved in the saved scenes.

## Dimensions and interfaces

Godot local units are metres; +X right, +Y up, -Z forward. Blender +X/+Z/+Y maps once
through glTF conversion. Source object transforms are applied, with positive unit
scales. Wrapper and imported root are identity transforms. The origin is the main
grip grasp centre, not a shoulder/wrist joint. Bounds tolerance is 0.001 m.

| Measurement | Imported value |
| --- | --- |
| Width X × height Y × length Z | 0.270 × 0.344 × 0.800 m |
| Grip-relative AABB minimum | (-0.135, -0.131, -0.520) m |
| Grip-relative AABB maximum | (0.135, 0.213, 0.280) m |
| Main grip section in its own local cross-section | 0.064 m wide × 0.070 m deep; rounded edges |
| Main grip centreline | 0.190 m long, tilted 12° in the weapon's vertical/length plane |
| Muzzle visual aperture | 0.028 m diameter; rim outside diameter 0.052 m |
| Muzzle end plane | Z = -0.520 m, centre Y = 0.140 m |

The grip section is a mesh measurement, not a fitted hand size or human reach limit.
The fixed visual magazine is not an implemented reload state.

All socket bases are identity in Godot: X=(1,0,0), Y=(0,1,0), Z=(0,0,1), so local
forward is -Z and local up +Y. Blender markers use the matching weapon frame. Contact
normals below are separate surface data; marker axes are **not** wrist/bone twists.

| Source marker → wrapper path | Position in weapon local metres | Outward contact normal |
| --- | --- | --- |
| `socket_grip` → `Sockets/Grip` | (0, 0, 0) | Not applicable: grasp/pivot centre |
| `socket_grip_contact` → `Sockets/GripContact` | (0.032, 0, 0) | (1, 0, 0), right grip surface |
| `socket_support_hand` → `Sockets/SupportHand` | (0, 0.055, -0.310) | (0, -1, 0), underside surface |
| `socket_shoulder` → `Sockets/Shoulder` | (0, 0.128, 0.280) | (0, 0, 1), rear pad surface |
| `socket_muzzle` → `Sockets/Muzzle` | (0, 0.140, -0.520) | Not applicable: directional effect origin |

Wrapper sockets are copied from the imported source markers through an editor-only
helper, not hand-tuned in the wrapper. The helper is detached before save and never
runs on the production visual. The installed `scene_instantiate` command only accepts
`.tscn`, so `editor_author.gd` supplies the narrow linked-GLB insertion through the
private editor, retaining the import's scene ancestry and noneditable children.

Right hand is dominant, left hand supports the forward underside, and the stock
contacts the right shoulder during aim. Actual mesh-ray checks verify the three
contact surface centres within the 1 mm tolerance. Player has published the binding
contract **shared_humanoid/1.0.0** at commit
`3eccf8f691fe34132ee8504d10dfceda4f7e2bb6` on `art/brackett-player-character`:
`docs/assets/shared_humanoid_rig.md`, with source under
`art/source/models/shared_humanoid/`. That version freezes the 28-bone rest hierarchy
for skin binding; it does not establish weapon fit or production motion. Bone-to-grip
and contact offsets, hand twist, holding/aim/reload clips and equipped acceptance
remain pending player-led fitting. The shared source was not copied into this branch.
No S13 binding, guessed bone origin, retarget rig or corrective root rotation is used.
Player owns `Sockets/WeaponMount`; it is not duplicated inside this weapon.

This is a rigid visual: rig and weapon clips are not applicable to the current
approved scope. Player holding/aim/reload/death compatibility and any future moving
weapon part remain pending the player clip matrix. No simulation, damage, firing,
inventory, recoil rule, projectile or networking code is supplied.

Effects confirmed that `Sockets/Muzzle` is sufficient and requested no extra anchor.
A compact directional flash can start at the local muzzle origin, extending -Z.
Its extent must clear the 26 mm outside rim radius; effect dimensions/performance are
the effects owner's decision. No effect mesh, shell, tracer, flash or light is embedded.
Gameplay muzzle queries must use physics pose plus the authored socket transform;
smoothed visual attachment alone is not an authoritative firing position.

## Materials and visual review

Five stable weapon material names: `smg_wedgewire_coral_shell`,
`smg_wedgewire_cyan_band`, `smg_wedgewire_charcoal_body`,
`smg_wedgewire_grip_rubber`, `smg_wedgewire_muzzle_metal`.
Each source mesh has one assigned slot; exact exported indices/values are in
[materials.json](smg_wedgewire_a_evidence/materials.json). Flat swatches are converted
from sRGB to linear source shader values. Opaque surfaces, no emission or transparency.
No texture maps/UV baking are required by this palette design; no shared material
resource, remap or variant is introduced. Import LODs remain enabled; no independent
performance budget or device claim is made.

The saved preview places the weapon at Y=1.3 m at unit scale over a source-linked
petrol/concrete review pad. It supplies a white key, restrained cyan fill and ambient
light. Captures use Forward+ / Vulkan on NVIDIA GeForce GTX 1070, 1280×800,
60 FPS cap and VSync. The game camera is (0,47,0), rotation (-90°,0,0), FOV42°,
near/far0.1/160 m, north-up. Overview and side camera transforms are saved in the
preview and recorded by the capture logs. These are desktop asset-preview receipts.

Visual self-review: the coral silhouette, taper and side-wrapped cyan band match the
chosen broad-form direction. At native game framing the isolated weapon is roughly
18 px long and 6 px wide; the coral roof is visible but fine detail is absent. This
does not establish identification while held, player occlusion, other weapon-family
separation, city lighting, aiming/movement or device performance. Those checks remain
with player/effects/gameplay integration. No enlarged crop is presented as native scale.

An early preview showed large floor shading triangles. They were traced to stale
corner-normal mappings after triangulation, corrected in Blender, and reexported;
disabling shadows did not fix the cause, and shadows remain enabled. A tapered
underside initially displaced the support contact by 4 mm; explicit loft sections
restore the measured flat contact patch. Final contact errors are below 0.000001 m.

## Validation and acceptance

Baseline for this production checkpoint: concept commit
`4bab6edadcaf655473f36836706efe2f4a8a6683`; shared source baseline
`c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.
Independent Sol 6.1/high review inspected immutable static candidate
`bc1075c985e11ced6c2c23f948808ebf482ba178` against the concept base above.
No P0–P3 static asset defects were found. See the
[full review and limitations](smg_wedgewire_a_evidence/review.md).
This final receipt updates documentation only; the reviewed implementation is unchanged.

| Check | Evidence / scope |
| --- | --- |
| Source reexport freshness | Both GLBs reproduce byte-for-byte from saved `.blend`; fingerprints and reexport receipt in evidence |
| Private process ownership | `editor_ownership.json`: worktree root, pinned engine, editor PID65124, ports20650–20654, private `/tmp/brackett-smg` state |
| Full asset reimport and scene synchronization | Actual editor full scan/reimport, then close/reopen/save of wrapper, preview and inherited camera; stable saved bytes/IDs |
| Imported bounds, socket frames/relay and surface contacts | `check-asset-final.log`, zero failures; no collision; imported GLB ancestry, unit roots and inherited camera checked |
| Clean asset import | `clean_import.json`, fresh asset-only copy, exit0/no diagnostics; input bytes preserved |
| Script compilation | All four owned GDScripts explicitly compiled in the clean copy; logs retained; separate from import |
| Style | Pinned gdstyle0.3.0 format and lint pass; comments, tabs and two-line function spacing reviewed |
| Independent review | No P0–P3 static defects; independent byte-identical source reexport, contact/resource/compile/style checks and fresh diagnostic-free import; see `review.md` and retained evidence archive |
| Pixels | Three real Forward+ screenshots and capture logs, save_error0, native1280×800 |

The default MCP Godot endpoint6550 and Blender endpoint were unavailable. A fresh
private Blender CLI and a private worktree-bound Godot editor were used; mutations
went through the installed toolkit via its normal SDK. Reserved world16650–16654 and
rocket19650–19654 endpoints were untouched. Shared settings/configuration were not
changed. Targeted `editor_refresh` did not reimport changed GLBs, so full refresh was
used and actual triangle counts/fresh captures checked before accepting results.

Known tool diagnostics are scoped: Blender reports missing optional MeshOptimizer
library; explicit GLBs contain no compression extension. Source authoring reports a
Blender6.0 deprecation for `Material.use_nodes`. Full-project editor startup reports
the pre-existing Steam `get_godotsteam_version` API mismatch. Toolkit save/reimport
calls can log deferred progress-dialog diagnostics. Clean asset-profile import,
all four script compiles and final runtime checks/captures have no errors/warnings.
The independent reviewer initially hit restricted editor-listener errors; an authorized
fresh import with listener access passed without errors/warnings and preserved all
15 inputs, including sidecars/UIDs. Both logs are retained in the review archive.
These profiles do not certify the full project's plugins or gameplay.

The independent review accepts source/export freshness, measured markers and linked
wrapper/preview within bounded static technical scope. Gameplay/network acceptance,
Windows/Steam/Deck, sustained performance, equipped poses and camera readability in
the city remain pending. No movement/collision behavior changed in this task.

## Integrator notes and shared-planning delta

Instance the wrapper at the player-owned grip mount with identity root transform.
Resolve the documented sockets once; use player-fitted bone/hand offsets, not source
marker bases as hand-bone rotations. Keep imported model ancestry intact. Future source
changes reexport **both** collections, preserve `.import` UIDs, then full editor
refresh and close/reopen/save both base/inherited previews. Recheck sockets/bounds and
relevant equipped gameplay when contact/scale changes.

Shared files were intentionally left to their owner. Suggested catalogue row:
`smg_wedgewire_a | rigid Wedgewire SMG visual | docs/assets/smg_wedgewire_a.md`.
Record the linked review-pad output as preview-only under this same source record.
Concept selection is complete; static technical work and independent review status
are recorded here. Keep equipped pose/clip fitting, gameplay/effects integration and
device/city readability tasks open. No existing TODO was removed; no main scene,
shared rig/material, foundation task, merge, push or workspace archive was changed.
