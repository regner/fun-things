# World concept handover

Status, 9 October 2026: **ready to start at Stage 1.** Regner (owner) commissioned this
work. This handover is for an agent that will produce world concepts and mockups for
Fun Things. It covers the world only: no UI, HUD or menu concepts (UI v1 exists in
[`docs/concepts/ui-v1/`](../concepts/ui-v1/README.md) and is out of scope here).

The work is **stage-gated**. Start with the broadest question, which is the setting
of the city as a whole. Each stage ends with an owner decision. Do not start detailed
work for a later stage until the owner has approved the stage before it. For example,
there is no point concepting buildings before the setting is agreed.

## How to use this document

1. Read the context and binding constraints below, plus the linked records.
2. Run Stage 1. Present options, iterate with the owner, and record the approval.
3. Move to the next stage only after that approval is recorded in
   `docs/concepts/world-v1/decisions.md`.
4. Within a stage, iterate as often as the owner wants. Narrow from several broad
   options to one refined direction.
5. If the owner changes or skips a stage, record that decision and continue from the
   point they chose.

Ask the owner questions one at a time, and give a recommended answer each time.
Keep every option grounded in what the game must do: drive, run, shoot, flee and set
off explosion chains, all seen from a top-down camera.

## What already exists

These records are accepted starting points. Each stage may refine them. Revisiting a
ratified decision is allowed, but present it to the owner as a change and record it.

| Topic | Current position | Source |
| --- | --- | --- |
| Experience | Playful, irreverent top-down 3D city sandbox with GTA2-style camera and controls; 1–4 players; drive arcade cars, shoot pedestrians and vehicles, set off readable car explosion chains; original art and humorous signage | [design](../design.md) |
| Look | **Petrol & Coral**: darker, vibrant colors inspired by cyberpunk palettes on **ordinary city architecture**; smooth stylized 3D with bevels and broad highlights; no pixel art, grime or dense fine detail | [art direction](../art-direction.md) |
| Swatches | Road petrol `#123646`, roof emerald `#15564F`, coral `#FF725D`, cobalt `#235FCC`, amber `#FFC05A`, warm ivory `#F6F1DC`, sidewalk slate `#85929D` (reference, not calibrated) | [art direction](../art-direction.md) |
| Height | Mixed low-rise blocks with a few tall towers; the owner asked for buildings that reach or pass camera height | [art direction](../art-direction.md) |
| Starting district | Six blocks (3×2), perimeter driving loop, inner cross-links, shop foot passage, depot service alley, central plaza, residential block, repair/stunt yard | [world layout](../world-layout.md) |
| Earlier concepts | P0-04 palette, roof, high-rise, street, car/people and weapons/effects concepts with prompts | [P0-04 review](../concepts/p0-04/review.html) |
| Lighting | Fixed daytime lighting is the ratified M1 scope; ambient fill must keep tower shadows readable; bloom must preserve silhouettes | [art direction](../art-direction.md) |

## Binding constraints

Every concept must respect these unless the owner explicitly changes them. Flag any
proposal that would change one as an owner decision; do not slip it in.

**Camera and readability**

- The gameplay camera looks **vertically down** with perspective projection: about
  47 m above the street, 42° vertical field of view, fixed north-up yaw, at the
  1280×800 baseline ([S02 controls](../spikes/s02-controls.md), [design](../design.md)).
  It shows roughly a 70 × 44 m patch of street at once.
- **Roofs are the most-seen surface.** Facades only show at the frame edges, through
  perspective. Judge buildings and props mainly by their roof and top-down silhouette.
- There is **no building cutaway** (removed by owner decision). Tall buildings must not
  hide players, cars or targets. Solve this through layout, setbacks and silhouettes.
- Actors and cars must read clearly against roads and sidewalks. Keep streets quieter
  than actors; flashes stay brief.

**Gameplay geometry** (current proven or provisional values)

- Ordinary street: 9 m two-way carriageway plus 4 m sidewalks, a 17 m corridor. Block
  lots are about 64 × 56 m in the starting brief ([world layout](../world-layout.md),
  [S06](../spikes/s06.md)).
- Cars are about 3.4–4.8 m long and 1.8 m wide; people are about 1.8 m tall
  ([world layout](../world-layout.md), [S04](../spikes/s04.md)).
- The road graph must have no dead ends. Traffic follows lanes and turns; pedestrians
  wander sidewalks and crossings ([S06](../spikes/s06.md); traffic and pedestrian AI
  spikes S09/S10 are in progress).
- Car explosions have a 4.1 m blast radius and chain between nearby cars
  ([S05](../spikes/s05.md)). Areas meant for chains need car clusters.
- Movement is proven on flat ground only. Slopes, ramps, bridges and multi-level roads
  are unproven and need flagging as a technical risk if proposed.
- Population is 64 pedestrians and 32 cars district-wide, plus four players
  ([design](../design.md)).

**Scope**

- **M1 builds one exterior district of about six connected blocks** ([design](../design.md)).
  The city-wide concept defines the world vision and where that first district sits in
  it. It does not expand M1 unless the owner decides so. Record that decision if made.
- No interiors, building destruction, police/wanted system, missions, passengers,
  procedural cities or off-map travel in M1.

**Scale and performance guidance**

- On the development laptop, cities of up to 96 test-kit blocks held 60 FPS (capped).
  This is planning guidance, not a limit and not a Steam Deck result
  ([S07 environment scale](../spikes/s07-environment-scale.md)).
- Prefer chunky, readable shapes and inexpensive effects. Avoid dense fine detail and
  heavy foliage.

**Assets and originality**

- All designs, names, logos and signage must be original. Real places may inspire the
  setting, but no real brands, trademarks or copyrighted designs.
- Concepts are reference art, not production assets. Every visible production 3D model
  must later come from committed Blender sources with linked exports
  ([assets](../assets.md)).
- Record the tool, prompt or method and any references for every image, as P0-04 did
  with `prompts*.json`. Record the licence of anything not made in-project.

## Points to raise with the owner early

These came up while preparing this handover. Raise each one at the stage where it
matters, with a recommendation:

1. **Whole city versus M1 slice (Stage 2).** The owner wants concepts for the whole
   city. M1 ships one district. Recommend concepting the whole city at a broad level,
   then choosing which district becomes the M1 slice.
2. **Lighting per area (Stages 1 and 5).** Ratified scope is fixed daytime lighting.
   Per-district lighting can still vary within daytime: grading, accent and emissive
   signage, shade and haze. Night or time-of-day changes would be a scope change. Ask
   before concepting them as final.
3. **Revisiting the six-block brief (Stage 2).** The starting district may become one
   district of the larger city, or be redesigned. Ask which.
4. **Elevation and water (Stages 1 and 2).** Coastlines, rivers, bridges and hills
   strongly shape a setting. Flat ground is the proven case. Recommend keeping
   gameplay areas flat in M1 and using elevation and water mainly at city edges.

## Tools and methods

- **Image generation:** the P0-04 concepts came from an image-generation tool. In the
  current pi setup, check first with
  `models.getAvailableOfType("image")` in codemode. On 9 October none was configured.
  If none is available, tell the owner before Stage 1 and ask whether to configure an
  image provider. Stage 1 mood boards benefit most from painted images.
- **Vector illustration (SVG):** suitable for maps, zoning, road sections, typology and
  prop sheets, and lighting keys. Commit the SVG source and a rendered PNG.
- **Blender renders:** Blender 5.2 is at
  `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`. Use headless scripted
  renders (`blender -b -P script.py`) and commit the script. Simple massing rendered
  from the gameplay camera is the most reliable way to judge scale, roofs and
  occlusion. Blender concept files are reference material. Production asset sources
  follow [assets](../assets.md) later.
- **Godot captures** are optional and only useful from Stage 9 (greybox). Never run
  uncapped rendering on this laptop: use a 60 FPS cap or VSync (uncapped D3D12 causes
  GPU device removal here).

## Where work goes

- Concepts: `docs/concepts/world-v1/stage-NN-<topic>/`, with a `README.md` per stage
  covering the question, options, rationale, open questions, and the owner's choice.
- One gallery page, `docs/concepts/world-v1/review.html`, showing the current stage
  first and earlier stages below, like the [P0-04 review](../concepts/p0-04/review.html).
- Decisions: `docs/concepts/world-v1/decisions.md`, a dated log quoting the owner's
  words for every approval, rejection, and change to a ratified decision.
- Provenance: `prompts.json` or `methods.md` per stage, listing tool, prompt or script
  and references for each image.
- Images: PNG at 1600 px or wider for boards, 1280×800 for gameplay-camera views.
  Keep each file under about 1 MB. Name files `NN-short-name.png`.

Work on your own branch in a git worktree. Keep history linear and do not push unless
the owner asks. Commit each stage's deliverables and its decision record together.
Do not edit Godot scenes, production assets, `TODO.md` or task requirements. The one
exception: update the `M1-C0` line in `TODO.md` as stages complete.

## Review before each owner presentation

Before showing a stage to the owner, check it against this list, or ask an independent
reviewer to:

- It answers the stage's question and nothing beyond it.
- It respects every binding constraint, or flags the conflict as an owner decision.
- It is readable from the top-down camera: roofs, silhouettes and actor contrast.
- It supports the gameplay: driving loops, escapes, chains, crowds, spawns.
- It is original, and its provenance is recorded.
- Options are genuinely different, each with a short pitch and trade-offs, plus a
  recommendation.

## Stages

Each stage lists its question, what to deliver, and what the owner approves. Stages 4
and 5 may run in either order or together if the owner prefers.

### Stage 1 — World premise and setting

**Question:** where and what is this city? Real-world inspiration, region and climate,
era and tone, and how Petrol & Coral color and humor fit it.

- Deliver **4–6 genuinely different setting options**. Seed ideas, not limits: a dense
  NYC-style island grid; a tropical resort-island city; a sun-bleached Pacific coast
  sprawl; a European port; a rust-belt river city; a fictional harbor megacity.
- Each option gets one key image (aerial or street mood), a one-paragraph pitch, a
  palette mapping onto Petrol & Coral, and its gameplay implications: driving lines,
  street widths, crowd feel, where explosion chains happen, signage humor, plus any
  conflicts with the constraints.
- Include a short comparison table and a recommendation.
- **Owner approves:** one setting, or a merge, plus a working city name and tone words.

### Stage 2 — City structure and macro map

**Question:** what is the overall shape of the city, its districts and their
relationships?

- Deliver 2–3 macro map options (SVG): coastline or water, edges, rough size, arterial
  road network, the district list (typically 5–8 for the whole city), adjacency,
  landmarks, and the playable M1 slice highlighted.
- Note scale against the S07 guidance and how each district's road grid works with the
  street dimensions above.
- **Owner approves:** the city map, the district list with one-line identities, which
  district (or districts) M1 builds, and how the six-block brief maps into it.

### Stage 3 — District identity briefs

**Question:** what makes each district distinct, and what is it for in play?

- Deliver one board per approved district: purpose in play (fast driving, crowds,
  chain hotspots, escapes, stunts), mood words, architecture character, road
  character, prop families, lighting mood, accent-color distribution, signage and
  humor themes, and one landmark idea.
- Go deepest on the M1 district. Others can stay broad.
- **Owner approves:** each district brief, with the M1 district fully agreed.

### Stage 4 — Streets and roads

**Question:** how do roads and sidewalks look and work, city-wide and per district?

- Deliver a road hierarchy (arterial, ordinary street, alley or service lane, plus
  bridges or ramps only if approved), cross-sections with dimensions, intersection and
  crossing designs, lane markings, curbs, medians, parking, and rules for placing
  street furniture.
- Show each at the gameplay camera, including how it reads on the minimap.
- Check against the traffic and pedestrian constraints (S06, plus S09/S10 when
  available).
- **Owner approves:** the road kit and the per-district variations.

### Stage 5 — Lighting and atmosphere

**Question:** how does light make each district feel different within the agreed scope?

- Deliver lighting keys per district at the gameplay camera: sun direction and shadow
  length, ambient fill, color grading, accent and emissive signage, haze, and wet or
  dry surfaces.
- State readability rules: actor contrast, shadows that never hide targets, bloom
  that preserves silhouettes.
- Keep to fixed daytime unless the owner has changed it (see point 2 above). Label any
  time-of-day options as scope changes.
- **Owner approves:** one lighting key per district and city-wide lighting rules.

### Stage 6 — Buildings

**Question:** which building families belong in each district, and how do they read
from above?

- Deliver typology sheets per district: roof plans and top-down silhouettes first,
  then corner and frame-edge facade views, height bands (below, near and above camera),
  setbacks that keep the street visible, and variant rules.
- Base them on the six starting families (corner shops, workshops, paired housing,
  circular landmark, office tower, apartment tower). Add families only where a
  district needs them.
- Include gameplay-camera mockups of a typical block per district.
- **Owner approves:** the building families and variants per district.

### Stage 7 — Props and set dressing

**Question:** what fills the streets, and which props matter for gameplay?

- Deliver prop sheets per district: street furniture, signage (with original humor),
  vegetation suited to the setting, and parked-vehicle placement.
- Split them into **gameplay props** (cover, obstacles, chain-reaction clusters) and
  **pure dressing**. Flag any prop that implies new mechanics, such as breakables or
  explosive barrels, as an owner decision outside current M1 scope.
- Give density rules that keep walking corridors clear and actors readable.
- **Owner approves:** the prop families per district and the gameplay-prop list.

### Stage 8 — Landmarks and set pieces

**Question:** what are the memorable places?

- Deliver landmark concepts for the M1 district first: plaza, stunt/chain yard and
  tower canyon from the starting brief, or their approved replacements. Then add one
  or two per other district.
- Show each from the gameplay camera and in an establishing view.
- **Owner approves:** the landmark set.

### Stage 9 — Greybox validation

**Question:** does the approved design work at real scale from the real camera?

- Build a Blender massing greybox of the M1 district at real dimensions: roads,
  sidewalks, building masses, key props as boxes. Render it from the gameplay camera
  at 1280×800 along several driving and walking routes, plus a top-down overview.
- Check tower occlusion, street visibility, minimap readability, chain-yard space and
  route variety. Report problems and the proposed fixes.
- This greybox is a concept check. Production saved sectors are M1-C2 work.
- **Owner approves:** the validated M1 district layout and any fixes.

### Stage 10 — Production handoff

**Question:** what exactly needs building?

- Deliver an asset list per district for the M1 slice: building families and variants,
  road and sidewalk pieces, props, landmarks and lighting setups. Give priorities,
  reuse notes and a size estimate (S16 currently estimates 60–96 artist-days for M1 art).
- Map each item to the M1-C1 art families and the M1-C2 district assembly in
  [the production plan](../plans/m1-production-plan.md).
- **Owner approves:** the production asset list, which then drives M1-C1 and M1-C2.

## Out of scope

UI and HUD, characters and cars (beyond fitting them into the setting), weapons and
effects design, audio, gameplay tuning, and Godot production scenes. Raise anything
these concepts reveal about those areas as a note for the owner. Do not redesign them.

## Seed questions for the owner

Use these as prompts, one at a time, at the matching stage:

- Stage 1: Which real places or films feel right? Coastal or inland? Hot or temperate?
  How satirical should the humor be?
- Stage 2: How big should the whole city feel? Which district should players start in?
  Should water and bridges separate districts?
- Stage 3: Which district should be the chaos hub? Which is calm, as contrast?
- Stage 4: Wide boulevards or tight streets? Alleys as shortcuts everywhere, or rare?
- Stage 5: Same sun everywhere, or a distinct grade per district?
- Stage 6: How many towers near the camera height per district?
- Stage 7: Any props players should be able to use or blow up later?
- Stage 8: What should be the signature place people remember?
