# First city car — concept selection

Concept images for completed production assets were removed during production cleanup; retrieve them from commit `80d0f24`.

9 October 2026. Vehicle lead: Codex, dedicated `brackett-vehicle` worktree and
agent `103de18c-e4b8-4daa-83d8-17d3da68128c`. Concept accepting owner: Regner.
Baseline: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.
Status: Regner **approved all three cars** on 9 October 2026:
“I like and want all three.” Approved concept families are `car_latch_a`,
`car_crate_a` and `car_sable_a`; all three enter the modeling queue. This is art
direction approval, not measured dimensions, gameplay or production acceptance.
Production source, export and prefab checkpoints now exist for all three cars. The deleted
rendered gallery and saved preview scenes were historical checkpoint evidence and remain available
at commit `80d0f24`; final art acceptance is pending.

Regner also requested a larger bus and a dock/workshop truck. Their retained
[Tandem city bus](04_tandem_city_bus.png) and
[Keel service truck](05_keel_service_truck.png) concept sheets are **pending** approval.
See [larger vehicle brief and self-review](larger_vehicles.md).

[Exact imagegen prompts](prompts.json) ·
[Scoped handoff and reconciliation delta](handoff.md).

## Brief and options

Three reusable original ordinary city cars for the smooth stylized cyberpunk city.
Broad bevelled shapes, quiet surface detail, practical wheels/doors and a readable
roof/hood/rear arrangement. No real brands. The selected
[island reference](../../world-v1/stage-01-setting/15-long-island-cyberpunk.png)
supplies city mood; [parallel commissioning](../../../workflows/parallel-art-production.md)
owns the current work sequence. Names below are working asset-family labels.

| Option | Shape and color | Provisional visual W × H × L, metres | Selection consideration |
| --- | --- | --- | --- |
| A — Latch compact | Rounded three-door hatch; coral, ivory hood, petrol glass | 1.88 × 1.54 × 3.40 | Compact footprint and strong warm color; closest nominal dimensions to existing S04 fixture |
| B — Crate hatch | Squared five-door utility hatch; ivory roof, petrol hood, rubber bumpers | 1.90 × 1.64 × 3.65 | Recommended: broad light roof and blunt hatch give the clearest shape from above |
| C — Sable sedan | Low four-door three-box sedan; aubergine and muted coral hood | 1.92 × 1.44 × 4.25 | Long hood and separate trunk distinguish it; dark paint needs more ambient contrast |

These are requested concept proportions, **not measurements of generated art**,
approved production dimensions, or collider changes. All visual extents, including
mirrors, will be measured in Blender and Godot after selection. B is nominally
0.25 m longer, 0.02 m wider and 0.10 m taller than the S04 visual fixture; C is
0.85 m longer, 0.04 m wider and 0.10 m lower. Even A's equal nominal dimensions
do not prove collision/socket compatibility.

## Camera and self-review

Target is vertical downward perspective, north-up, 47 m street height, vertical
FOV 42°, 1280 × 800. Each sheet provides an enlarged overhead roof view, a
three-quarter view and an ivory silhouette study. The ivory studies contain dark
window cutouts; they are not pure binary silhouette masks. Front points up in the
roof views. The gallery also shows small CSS crops at an approximate floor-level
pixel length. They are illustrative concept reductions, not engine captures.

At the frame centre, a ground-plane metre projects to approximately
`800 / (2 × 47 × tan(21°)) = 22.17 px`. Nominal floor footprints are approximately
A 42 × 75 px, B 42 × 81 px, C 43 × 94 px. Roof elevation and perspective will
change the actual projection; screenshot scale, lights, shadows, off-centre views
and material contrast still require the saved asset-local Godot preview.

Self-review of all three generated PNGs:

- A: short rounded roof and ivory hood read clearly. Enlarged wheel spokes and
  glass/interior detail should be simplified in the selected model.
- B: ivory rectangular roof, dark windshield and short teal hood are strongest
  at small scale. Fine stamped ribs/door lines are optional surface detail;
  recognition must survive without them. Avoid turning it into an oversized SUV.
- C: length and trunk distinguish it from the hatchbacks. Purple roof against dark
  streets is the weakest contrast; raise broad roof value after selection if needed.
- Roof and three-quarter views agree broadly on paint, body family and windows;
  generated perspective and panel proportions are not exact construction references.
  All have four plausible wheels, no visible real brand/logos and no weapons.
- The sheets are somewhat more detailed than the intended chunky game model.
  Preserve primary masses and color blocks rather than every tire groove or trim line.

Initial concept self-review only. Production acceptance and independent production
review have not run. Regner has accepted A/B/C and chooses/iterates D/E directly
in this workspace. The original prompts remain unchanged for provenance.

## Provenance

Original concept brief and prompt authorship: Regner's commissioning plus Codex
vehicle lead's three direction prompts. Images generated using the built-in
`image_gen.imagegen` tool; no external vehicle model, stock photo, texture library
or branded reference used. All prompts are retained verbatim in `prompts.json`.
Reference is repository-owned city concept art viewed for mood. No third-party
license dependency was intentionally introduced; AI output is a concept reference,
not a guarantee of exclusive rights or Blender-source provenance.

The initial three tool calls continued to completion after an owner-directory
message interrupted the turn. Outputs were recovered from this agent's own
generated-image directory, visually checked and copied unchanged into this folder.
No replacement generation or image editing was needed. SHA256 and sizes are in
`checks.json`. The authoring source for the eventual vehicle will be original
committed Blender geometry, separate from these images.
