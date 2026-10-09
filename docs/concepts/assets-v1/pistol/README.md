# Pistol — first concept selection

Concept images for completed production assets were removed during production cleanup; retrieve them from commit `80d0f24`.

9 October 2026. Owner: Codex pistol workstream, Paseo agent
`04572f3d-e2f3-4779-8e40-03a35caaecd5`, branch `art/brackett-pistol`.
Baseline: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.
**Regner selected A — Coral Stub on 9 October 2026. Blender production is authorized.**

Production source/export/prefab and evidence: [Coral Stub handoff](../../../assets/pistol_coral_stub.md).

The removed `review.html` gallery remains available at commit `80d0f24`. Each original
generated sheet contained side, top, three-quarter and black silhouette views.

| Option | Direction | Self-review / tradeoff |
| --- | --- | --- |
| A — Coral Stub | Soft rectangular coral slide, cream rear patch, dark petrol grip | Recommended: compact familiar pistol shape, broad bright overhead blocks; small cyan patch and side grooves must not carry recognition. |
| B — Mint Capsule | Rounded pale mint shell, magenta rear cap, violet frame | Strongest playful consumer-object character and bright overhead contrast; rounder silhouette risks reading as a gadget. |
| C — Petrol Wedge | Tapered petrol shroud, orange rear shoulders, cream frame | Most distinct overhead contour; dark blue forward body risks blending into night streets. |

## Original commission and provenance

> Own the PISTOL game asset. Create three original stylized pistol visual concepts
> using imagegen skill/tool, clear at the game's top-down scale and fitting the
> city's irreverent cyberpunk tone. Include top-down and side/three-quarter
> silhouette views; these are game visuals, not real manufacturing designs.
> Present options/recommendation and await Regner's approval before Blender production.

The lead viewed the accepted [city reference](../../world-v1/stage-01-setting/15-long-island-cyberpunk.png)
and inspected [S02's source handoff](../../../assets/s02_kit.md), saved actor and
weapon study. Original art direction/prompts by this workstream; generated with
the built-in `image_gen.imagegen` tool. No external model/texture/brand incorporated.
Exact submitted prompts, generation parameters and original tool output paths are
in [provenance.json](provenance.json). PNGs here are unchanged copies of outputs.
AI concepts are visual references; future Blender source authorship must be recorded separately.

## Readability review and limits

Self-review inspected all three complete images: each has the requested views,
matching major color masses, full silhouettes and no visible brand. The designs
have materially different top contours: rectangular, rounded, tapered. Side grooves,
sights and grip texture are presentation details, not overhead recognition cues.
Generated views are concept approximations, not measured orthographic models.

Camera target: vertically down perspective, north-up, 47 m height, 42° vertical FOV,
1280×800. S02's grip-origin pistol body is 0.18×0.18×0.42 m and its handoff explicitly
flags weak native-camera pistol/SMG recognition. At the provisional 1.2 m held height,
the centre of this camera projects approximately 23 px/m: the 0.42 m S02 length is
roughly 9.6 px. The generation prompts' 14–18 px target would imply a larger apparent
length, approximately 0.62–0.79 m. That is an exploratory readability target, **not
an approved weapon dimension or permission to enlarge the player**. Choose appearance
now; settle scale with the selected player and actual held Godot captures before detail.

Bright color blocks are promising, but these boards do not prove actual camera,
hand occlusion, bloom, walking readability, gameplay, networking or device performance.
No firing, damage, ammo, hit registration or VFX is delivered in this concept checkpoint.

## Compatibility and ownership handoff

Preserve metres and positive unit roots. Blender +Z up/+Y front maps once to Godot
+Y up/−Z front; pistol origin is its grip attachment pivot. Future source markers:
`socket_grip` at grip origin and `socket_muzzle` at the front emission point,
local −Z forward/+Y up in Godot. Saved wrapper uses a linked `Visuals/Model` and
`Sockets/Muzzle`; player owns `Sockets/WeaponMount` and the presentation mount.
Relay authored socket transforms; do not invent a second hand-tuned muzzle.

S02 reference mount `(0.43, 1.2, -0.6)` and muzzle `(0, 0, -0.42)` relative to
grip remain unchanged spike data, not production hand offsets. Existing direct and
inherited S02/S03-R/S06 consumers are preserved; this is a new family, not a kit reexport.

All options need one primary gripping hand, optional support hand cupping the same
grip/guard region, no separate foregrip and no shoulder contact. Exact hand pose,
support-hand contact and holding clips await Regner's selection and player lead
`7016b739-5eea-480c-afa3-2c0cbad484a2`. Player alone owns the versioned
`shared_humanoid_rig.md` and shared source. S13's seven-bone fixture has no hand
sockets and is not a production rest/retarget rig. No competing rig files are authored.

Effects lead `c9207bb9-925b-46e4-bd68-e37aaa66a617` owns visual feedback using
the muzzle anchor. On 9 October the effects lead confirmed that `socket_muzzle`
→ `Sockets/Muzzle`, local −Z forward/+Y up and grip-origin unit root are sufficient;
no additional pistol anchor is requested. Effects will author a compact presentation-only
flash at local origin with forward extent along −Z. Pistol supplies measured aperture
and offset after Regner's selection; effects owns the resulting flash clearance/visual
envelope. This creates no physics-query dependency or pistol-owned VFX.
Dependency messages were sent to both leads asynchronously. Moving parts/clips are
optional pending a demonstrated presentation need; no automatic weapon rig requirement.
Collision and authoritative muzzle queries belong to the future gameplay integrator.

## Next approved production checkpoint

After selection, use the matching unique family/ID (`pistol_coral_stub`,
`pistol_mint_capsule` or `pistol_petrol_wedge`): source under
`art/source/models/<family>/<asset_id>.blend`, collection `export_<asset_id>`,
explicit `art/models/<family>/<asset_id>.glb`, necessary materials/textures,
import/UID metadata, `scenes/prefabs/<family>/<asset_id>.tscn`, and an asset-local
preview. Measure bounds, axes, grip/muzzle, held silhouette and save/reopen the
Godot wrapper. Obtain a clean-context independent review of immutable base/HEAD
before declaring production completion. Concepts need only this self-review.

Tool discovery found Blender 5.2.2 LTS `d13f752e3b9c` and pinned Godot
4.8.dev7 `c971f93e7`. Blender MCP was unreachable; Godot MCP at port 6550 refused
connection. No editor writes or recovery infrastructure were attempted. A private
worktree-bound process must be verified before later authoring. Greybox ports
16650–16654, PID49308 and `/tmp/brackett-greybox` state are reserved and must be avoided.
Concept/gallery filesystem edits need no scene-edit fallback. Production editor
refresh/reopen evidence remains pending and is not implied by this checkpoint.

## Small shared-record delta for later reconciliation

Do not edit shared catalogue/TODO during this parallel track. Suggested later delta:
add the selected pistol ID and asset-local handoff link to the catalogue when selected;
record “pistol concepts presented, owner selection pending” and keep production,
held-camera, sockets/export/import/preview and external gameplay integration open.
No foundation or gameplay TODO is completed by this checkpoint.
