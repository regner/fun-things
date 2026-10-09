# Player character — first concept selection

Concept images for completed production assets were removed during production cleanup; retrieve them from commit `80d0f24`.

9 October 2026. **Regner approved A — Coral Courier for production.** Regner also
confirmed a shared underlying skeleton with separate player/NPC animation libraries,
and future interchangeable player skins. Production is underway; production model,
rig, animation and gameplay acceptance remain pending.
Base: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.

The removed local gallery and full-resolution sheets remain available at commit `80d0f24`:

| Direction | Sheet | Main visual idea | Tradeoff |
| --- | --- | --- | --- |
| A — Coral Courier | historical image | Rounded bomber shoulders, broad ivory yoke, pale forelock, compact street silhouette | Needs simplified sleeves/hair and separation from coral pedestrian outfits |
| B — Night Shift | historical image | Sturdy square mass, yellow shoulder blocks, silver head, ordinary municipal workwear | Very bright; could read as a service NPC without other player presentation |
| C — After Hours | historical image | Slim fashion silhouette, angular shoulders, pale back triangle, platform shoes | Dark violet may merge into night streets; shoes and narrow legs need motion checks |

**Selected: A.** Its broad ivory shoulder marker and pale forelock are visible
above the body, and the short bomber leaves arms and hips available for weapon and
locomotion poses. B is strongest for immediate color contrast; C is strongest for
eccentric fashion. Identity, hairstyle, colors and clothing can be iterated directly
with Regner; the later explicit selection authorizes modeling.

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
`docs/assets/shared_humanoid_rig.md` and `art/source/models/characters/shared_humanoid/`.
These production files are owned by player lead; immutable compatibility checkpoints
will be sent to consumers as they become available.

## Production model routing and editor checkpoint

Owner instruction received 9 October 2026: all modeling/animation work uses Astra,
including geometry, UV/skin deformation, spatial rest/bone design and authored poses/
keyframes/motion. Non-spatial Godot import/configuration/wiring may use Sol 6.1.
Verify the actual runtime model before any resumed spatial mutation; preserve
in-flight state at a transition and end a Sol turn if settings cannot take effect.
This supersedes the cohort's earlier Sol lead policy. No optional feature override.

Before the first modeling mutation, Paseo `get_agent_status` reported active runtime
session `01a12094-20e5-7611-a755-76f746e02d3c`, model `gpt-6-astra`, reasoning `high`.
No geometry/bones/keyframes had been authored by this lead before that verification.
Pinned Godot `4.8.dev7.official.c971f93e7` was found through Mise. Private editor
PID 78374 runs this worktree, capped at 60 FPS, using `/tmp/brackett-player-editor`
XDG state and editor/runtime/LSP/debug/DAP ports 17650/17651/17652/17653/17654.
The default connector remains bound to an unavailable endpoint; owned
`tools/assets/characters/coral_courier/private_editor.mjs` calls the same toolkit commands through
the explicitly verified private endpoint, checking registry/project/PID before each
connection. It does not scan or switch other editors. Initial scene query found the
baseline `run/main_scene.tscn`; no scene mutation or replacement occurred.
Local generated `.mcp.json` is preserved as untracked configuration, not a deliverable.

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
