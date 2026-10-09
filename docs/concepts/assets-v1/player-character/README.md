# Player character — first concept selection

9 October 2026. **Awaiting Regner's direction selection.** Concept preparation and
visual self-review only; no production model, rig, animation or gameplay acceptance.
Base: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.

Open [the local gallery](gallery.html) or the three full-resolution sheets:

| Direction | Sheet | Main visual idea | Tradeoff |
| --- | --- | --- | --- |
| A — Coral Courier | [image](01_coral_courier.png) | Rounded bomber shoulders, broad ivory yoke, pale forelock, compact street silhouette | Needs simplified sleeves/hair and separation from coral pedestrian outfits |
| B — Night Shift | [image](02_lime_utility.png) | Sturdy square mass, yellow shoulder blocks, silver head, ordinary municipal workwear | Very bright; could read as a service NPC without other player presentation |
| C — After Hours | [image](03_violet_hustler.png) | Slim fashion silhouette, angular shoulders, pale back triangle, platform shoes | Dark violet may merge into night streets; shoes and narrow legs need motion checks |

**Recommendation: A.** Its broad ivory shoulder marker and pale forelock are visible
above the body, and the short bomber leaves arms and hips available for weapon and
locomotion poses. B is strongest for immediate color contrast; C is strongest for
eccentric fashion. Identity, hairstyle, colors and clothing can be iterated directly
with Regner; this recommendation does not authorize modeling.

## Brief and ownership

Original fictional adult player for a smooth stylized, irreverent top-down city game.
Follow [the selected city reference](../../world-v1/stage-01-setting/15-long-island-cyberpunk.png),
[art direction](../../../art-direction.md), [asset workflow](../../../assets.md),
[scene contracts](../../../scene-structure.md) and the active
[parallel commission](../../../workflows/parallel-art-production.md).
The reference was visually inspected; its description informed the prompts.
No brands or external model/rig/texture libraries are incorporated.

Player lead (Paseo `7016b739-5eea-480c-afa3-2c0cbad484a2`) owns concept preparation,
later player source/export/presentation assets, and the shared humanoid rig contract.
Regner selects the concept. Independent production reviewer is assigned after a
reviewable production revision exists. Gameplay and world integration belong to
the external integrator; the player lead does not author the controller.

Target camera: vertical-down perspective, north-up, height 47 m, FOV 42 degrees,
1280 × 800. Target body height near 1.8 m is provisional; clothing/animated bounds
and collision fit require measurements after approval. Origin ground between feet,
metres, unit roots, Blender +Z up/+Y front → Godot +Y up/-Z forward/+X right.

## Visual self-review

All three sheets contain front/rear three-quarter views, an enlarged overhead study,
an ivory overhead silhouette and palette swatches. Clothing is short, hands remain
available, and head/shoulder markers carry the visual identity. No weapon design is
selected by these images. Generated decorative copy is not part of the brief.

The overhead characters face the bottom of the page despite the north-up prompt;
the gallery explicitly labels this mismatch. Enlarged overhead studies are artistic
approximations, not calibrated game captures. Silhouette panels approximate the
colored outlines rather than proving a shared mesh. All three use more fabric/hair
detail than the eventual chunky model should retain. C's shoulders appear broader
in its overhead study than its three-quarter view; reconcile before blockout review.
Skin identity and small facial details cannot establish top-down player recognition.

The gallery provides deliberately small views at 16/24/32 px subject widths to
expose loss of detail. These are browser-scaled raster crops, not Godot evidence.
At the target camera, the ground-plane vertical span is approximately 36.1 m,
or 22.2 px/m; a near-0.7 m shoulder span would be roughly 16 px before height and
perspective effects. Actual silhouette dimensions remain unmeasured. Production
must review the linked model from the exact saved game camera, including all
weapon poses, night contrast and death/animation bounds.

## Provisional compatibility and state coverage

[S13](../../../assets/s13_humanoid.md) is a 1.8 m, seven-bone technical fixture with
`idle`, `walk`, `run`, `death`; it has no hand sockets, production rest pose or
retarget contract. Its source/export and linked fixture were inspected. Do not bind
new skins to it or change its existing bone names/consumers implicitly.

Preserve source `socket_grip` / `socket_muzzle`, grip-pivot weapons and prefab-facing
`Sockets/WeaponMount` / `Sockets/Muzzle`, with -Z forward/+Y up. Bone attachments,
rest transforms and hand offsets are undecided. S02's mount and muzzle offsets are
spike references, not production hand transforms.

| Consumer | Received holding needs | Decisions after concept selection |
| --- | --- | --- |
| Pedestrian | Shared compatible humanoid skin/rest/clip contract | Final binding waits for a versioned rig; concepts proceed independently |
| Pistol | Primary one-handed grip; optional supporting hand around grip/guard; no foregrip/stock/shoulder contact | Hand fit, optional support pose, reload/recoil presentation |
| SMG | Firing-hand grip, support beneath front receiver, short stock shoulder contact; provisional length around 0.8 m | Contact transforms, shoulder clearance, aim/reload/recoil presentation |
| Launcher | Grip, support hand beneath forward body, shoulder contact behind grip, clear head | Pose/clearance for selected tube/pod, aim and firing recovery |

9 October dependency update from the pistol lead: Regner selected **A — Coral Stub**
for source-linked static weapon production. Keep its grip pivot/unit root and
`socket_grip` / `socket_muzzle`; one primary hand, optional support around the same
grip, no shoulder contact. The weapon lead will initially preserve the S02 0.42 m
grip-to-muzzle reference and inspect the actual camera before changing apparent
size. This is a provisional weapon dimension, not a settled player hand/rest offset.
Player concept selection remains pending. Once the versioned production rig defines
the hand pose and attachment transform, player lead sends settled grip dimensions
and pose needs to the pistol lead for a source-linked fit check.

9 October dependency updates: Regner selected **SMG C — Wedgewire**, a broad tapered
receiver/short stock around 0.8 m overall, and **launcher A — Dock Thumper**, a fat
shoulder tube with coral muzzle collar/pale upper stripe. Launcher lead proposes
1.4 m overall length, 0.34 m body diameter and 0.40 m muzzle diameter; these art
envelopes await measured exports and actual-camera review. Weapon leads author
static grip/support/shoulder references; launcher uses `socket_support_hand` beneath
the front and `socket_shoulder` behind the dominant grip. Launcher geometry is fixed,
with no weapon-owned skeletal clip requirement. Neither selection approves player
art, settles player reach or accepts equipped motion.

Provisional pose convention for weapon compatibility: **right dominant hand, left
support hand, right shoulder** for SMG/launcher. This is a player-lead art convention,
not a frozen bone/rest contract or gameplay handedness feature. Author contact
markers in the weapon frame: imported +X right/+Y up/-Z forward (Blender +X right/
+Z up/+Y forward), unit scale; include numeric imported positions and bases in the
weapon handoff. `socket_grip` remains the mount pivot at origin. Support/shoulder
markers identify measured contact-surface centres, not guessed wrist/bone origins.
Use the same forward/up frame for these reference markers; document each contact
surface's normal separately so palm/shoulder orientation can be fitted explicitly
later. Do not infer a hand bone basis, twist the weapon root to compensate for one,
or bind against S13. Player lead will derive and verify bone-to-grip and contact
offsets in the versioned production rig after player concept approval.

9 October pedestrian dependency update: Regner selected **C — Off-Shift Worker**
and authorized reusable per-NPC colours with the shared rig approach. Pedestrian
lead owns the cap, broad short amber/cobalt jacket, slate trousers and boots; no
held props or extra sockets. Required shared motion includes relaxed arm swing
with elbows/knees, in-place looping `idle` / `walk` / `run`, and one-shot `death`
retaining its final pose. Height near 1.8 m remains provisional. Worker mesh/source
can proceed independently; binding waits for the player-owned immutable contract/
source revision with hierarchy, rest pose, skin mapping and clip conventions.
Common production locomotion/death clips are **not ready for reuse** at this
checkpoint; S13's technical clips do not establish production compatibility.

Required coverage includes in-place unarmed idle/walk/run and retained final death
pose; pistol, two-hand SMG and shoulder-launcher holding/aiming while stationary
and moving; independent movement/aim directions from the design brief; and pistol/
SMG reload presentation. Recoil/fire recovery and transitions must be reviewed
with weapon leads and the integrator. This is a state checklist, **not a frozen
clip list**: decide full clips versus upper-body layers, names, hierarchy, rest pose,
frame rate, loops and attachment transforms in the versioned production contract.
No modeled driver is currently required by the design brief; vehicle interaction
does not by itself require seat/entry animation production.

After approval, player-specific paths use `player_character/` under source/runtime
art and asset-local preview areas. Shared ownership is
`docs/assets/shared_humanoid_rig.md` and `art/source/models/shared_humanoid/`.
These production files are not created or frozen at this concept checkpoint.

## Tool receipt, provenance and pending handoff

Exact prompts and saved output mapping: [provenance.json](provenance.json).
Built-in `image_gen.imagegen` generated the sheets. Original interrupted calls
continued and returned later; one extra A call produced an unused duplicate.
All three selected sheets are copied into this worktree; no external-only dependency.

Read-only editor discovery succeeded. Default Godot endpoint `127.0.0.1:6550`
refused connection; Blender MCP could not connect. Locally `/usr/bin/blender`
reports **5.2.2 LTS**; no `godot`/`godot4` executable was on PATH, and no local
Godot/Blender application process was observed in the available process namespace.
No editor/Blender writes, endpoint changes, scene changes or production tool
recovery were attempted. The greybox endpoint `16650` and ports `16651–16654`
are reserved to that workstream and must not be used. Verify a worktree-private
project/process/endpoint before future source/editor writes.

Production Blender/GLB/UV/materials, import/UID metadata, rig/clips, linked saved
Godot scene, capped preview, save/reopen and independent immutable-revision review
are pending. Gameplay/network/hardware acceptance is separate and not claimed.

For later catalogue/TODO reconciliation only: add the chosen player asset handoff
and versioned shared rig entry when those files exist; retain production/integration
tasks as pending. **No completed TODO removal or catalogue change is justified by
concept preparation alone.** Shared planning/catalogue/TODO files were not edited.
