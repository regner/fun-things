# city_boardwalk.05 — Landward access / promenade transition

10 October 2026. **Source, export and linked prefab delivered; bounded asset and canonical
checks pass. Independent review, world placement and gameplay/device acceptance remain pending.**
Produced by the commissioned implementation specialist on `lane/a-boardwalk`, under the
[production commission](commission.md) and current per-asset common brief. The current brief
supersedes historical lead-only Git/prefab restrictions. No sibling, shared brief, register,
project setting, route or shoreline was changed.

Family: [shared island boardwalk](../city_boardwalk.md). Read and matched the delivered
[straight deck](city_boardwalk_01.md), [bends](city_boardwalk_02.md),
[fascia/trim](city_boardwalk_03.md) and [support](city_boardwalk_04.md), Petrol & Coral
[art direction](../../art-direction.md), The Crescents v02 and world-v1 stage-03 district
identities / stage-04 streets. These establish appearance and route intent, not measured coast fit.
Original Blender construction only: no downloads, image-to-mesh, real brands, external textures,
road surfaces, duplicate props or runtime-generated render geometry.

## Design and dimensions

A **level, gently flared timber access** opens from the 3.6 m boardwalk into a 4.8 m promenade
interface over 3 m. Nine broad cross timbers continue the sibling's quiet seam rhythm; one
flush slate threshold clearly ends the timber route. The inset dark core and softly rounded
arrises match the family. No raised kerb, steps, handrails, lights, furniture, paving slab,
seawall or supports are duplicated. The threshold is integral access hardware, not a road or
sidewalk module. Road-tool-generated promenade surfaces remain outside this asset's ownership.

All dimensions are **provisional** under the standing instruction to proceed with sensible
family-compatible interfaces. This delivery is **level-only**, not a height-adapting ramp or
an authorization for elevated driving. Use it where the existing promenade and deck share a
walking elevation. Sloping sites or a 2.24 m deck-to-ground drop need separate fit review;
do not tilt/stretch this member or alter the shoreline to force a connection.

| Interface | Godot local metres |
| --- | --- |
| Entry width / exit width | **3.600 / 4.800** |
| Length / depth | **3.000 / 0.240** |
| Pivot | **Entry centre on walking surface (0,0,0)**, not footprint centre or seabed |
| Axes | **-Z toward land/promenade**, +X right, +Y up |
| Boardwalk connector | **Z=0**, X=-1.8 to +1.8, Y=0 |
| Promenade connector | **Z=-3**, X=-2.4 to +2.4, Y=0 |
| Walking / underside datum | **Y=0 / Y=-0.240** |
| Plan taper | Both sides widen **0.600 m** over **3.000 m**, symmetric |
| Timber | Nine tapered boards, **0.080 m** thick, **0.288 m** long at **0.300 m** pitch |
| Seam / entry half-seam | **0.012 / 0.006 m**, cosmetic only |
| Threshold | Z=-3 to -2.706, **0.294 m** long, **0.080 m** thick, top flush at Y=0 |
| Recessed core | Y=-.24 to -.08, **0.040 m** lateral inset, exact connector planes |
| Roundover | Timber/threshold **0.004 m**, two segments; no collision bevels |
| Nominal AABB | **(-2.4,-.24,-3) → (2.4,0,0)** |
| Actual binary GLB AABB | **(-2.399216,-.24,-3) → (2.399216,0,0)** |
| Actual size X/Y/Z | **4.798431 / .240000 / 3.000000** |

Nominal envelope tolerance **0.006 m** admits cosmetic half-seams and rounded corners;
walk/underside datum tolerance **0.001 m**, source-to-binary coordinates **0.00001 m**.
These visual tolerances never permit a collision step or hole. The continuous collider follows
the nominal trapezoid rather than every rounded timber edge. Eleven individually closed solids
share one mesh; the source is not a boolean union or a structural engineering certification.

### Family mating and placement

- **Terminal connection:** place an unchanged `.01` at **(0,0,3)** and this access at the
  origin, both identity. Its entry meets the deck's north end. The promenade starts at
  **Z=-3, Y=0**, across at least 4.8 m. Opposite directions use rigid yaw/translation,
  never negative scale. The saved fixture tests both traversal directions.
- **Landward side opening:** for a `.01` centred at the origin, place this access at
  **(1.8,0,0), yaw -π/2**. Its entry spans the deck side from **Z=-1.8 to +1.8** and exits
  at **X=4.8**, spanning Z=±2.4. Left-side access uses **(-1.8,0,0), yaw +π/2**. The saved
  fixture tests the right-side case translated X=12; left-side use is a dimensional handoff.
  Cross timbers turn through 90° at this intentional T connection; they do not pretend to
  preserve an uninterrupted parallel grain pattern.
- **Keep fascia, terminal caps and shared rails out of these connector openings.** Do not
  place a full `.03` 6 m strip across a side opening. This asset does not cut siblings at
  runtime or invent new short rail/fascia variants. Adjacent partial-run finish/rail fit is
  pending placement work; do not stretch `.03` to match the tapered flanks.
- `.02`'s entry/exit connectors have the same 3.6 m width and Y=0 datum. Matching rigid
  placement is possible, but bend-to-access mating is **not tested** by this fixture.
- `.04` meets the -0.24 underside, but its fixed-width bent does not establish support
  capacity under the wider mouth. This landward member requires existing compatible shore
  bearing; no unsupported cantilever or new foundation is authorized.
- `city_shore_edges` owns shore rocks/seawalls. `city_quay_furniture.02` owns guard geometry
  and collision. Safe waterfront placements require shared rails outside the walking line
  and appropriate shore/support fit. These are downstream dependencies for **placement**,
  not required to load or inspect the bare access component. No substitute hardware is made.
- Six recorded coastal districts remain prospective consumers; Old Quay remains a candidate.
  **East Docks is excluded.** Ironreach's northern and Broadlot's southwestern terminal
  connections must remain outside the freight working area. This is not a closed island
  ring, inner-basin dock, harbour bridge, reclamation or island polygon edit.

## Source, export and materials

- Source: `art/source/models/environment/city_boardwalk_05/city_boardwalk_05.blend`.
- Named export collection: **`export_city_boardwalk_05`**.
- Identity-transform root / child: **`CityBoardwalk05` / `CityBoardwalk05_Mesh`**.
- Explicit linked export: `art/models/environment/city_boardwalk_05/city_boardwalk_05.glb`,
  with committed `.glb.import` identity metadata.
- Parametric author, exporter, binary validator, isolated renderer, initial prefab author,
  saved mating fixture, headless checker and manifest helper:
  `tools/asset_production/city_boardwalk_05/`.

Metre units, applied transforms and weighted corner normals. Blender +Y/+Z maps exactly once
to Godot -Z/+Y. Only root and mesh export; source contains no studio objects. `render.py`
loads the unchanged `.01` source for transient context and never saves that geometry into this
asset. The accepted example and shared export contract supply conventions; no generic shared
Blender geometry/binary-audit helper exists here. Local recipes follow the family pattern;
`tools/assets/blender/export_settings.json` remains the sole export-settings owner.

One mesh, five opaque, backface-culled Principled surfaces in exported slot order:

| Slot / material | Linear base RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `boardwalk_underdeck_slate` | (.048,.069,.078) | .15 / .58 |
| 1 `boardwalk_timber_warm` | (.235,.145,.085) | 0 / .68 |
| 2 `boardwalk_timber_light` | (.260,.166,.101) | 0 / .68 |
| 3 `boardwalk_timber_muted` | (.215,.136,.085) | 0 / .68 |
| 4 `boardwalk_access_threshold` | (.090,.126,.137) | .20 / .50 |

Slots 0–3 match `.01`/`.02`; threshold values match `.03` trim and `.04` shoes. No textures,
embedded images, UV-dependent shaders, emission, transparency, redundant external materials,
rig, animation, destruction state or sockets. Materials remain GLB-owned. No custom LOD;
default Godot automatic LOD/shadow-mesh generation remains enabled, pending repeat-placement
visual/performance review.

## Prefab and collision

`scenes/prefabs/environment/city_boardwalk_05.tscn` retains its linked GLB at
**`Visuals/Model`, identity transform**. No embedded meshes, editable imported children,
material overrides, gameplay script or runtime hierarchy construction. Headless Godot normalizes
and preserves scene/node/dependency identities through repeated save/load/resave.

One StaticBody3D at **`Collision/Body`**, **layer 1 / mask 0**, has one direct enabled
`Access` CollisionShape3D: an **eight-point ConvexPolygonShape3D trapezoidal slab**, spanning the
literal nominal outline at Y=0 and Y=-.24. It is the minimal single convex shape for this
footprint; an enclosing rectangular box would incorrectly fill outside the narrow entry.
The smooth level walk collider bridges cosmetic seams and the small backing/roundover recesses.
No top step, internal seam, rail collision or invisible above-floor barrier is introduced.
Avoid duplicate coplanar promenade/terrain collision: adjacent surfaces butt at the connector,
not beneath the entire access.

`tools/asset_production/city_boardwalk_05/mating_check.tscn` saves separate terminal and right-side
connections with unchanged `.01` decks. Two **collision-only** promenade envelopes represent the
level receiving interface, not new rendered promenade geometry or delivered world placements.
The collision-only capsule uses production **ActorMotion**, radius **0.35 m**, height **1.8 m**.
The bare component does not depend on an unproduced promenade or rail prefab.

## Validation and evidence

[validation.json](city_boardwalk_05-evidence/validation.json) records measured source/binary,
Godot resource/physics and canonical-check results.
[manifest.json](city_boardwalk_05-evidence/manifest.json) hashes every delivered payload except
itself. [final.log](city_boardwalk_05-evidence/final.log) retains a concise command/diagnostic
receipt; raw logs, intermediate images and fresh exports remain outside the checkout.

- Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**.
- **1,092 triangles, 568 source vertices, 568 GLB vertices; one mesh / five surfaces**.
- **Zero degenerate source/export faces and zero nonmanifold edges**, including actual binary
  edges after exact-position welding across material/normal seams. Consistent winding, finite
  coordinates, unit-length normals, applied identity transforms and dimensional datums pass.
- Fresh-process reexport is **byte-identical** to the committed **20,252-byte GLB**.
- Godot **4.8.dev7.official.c971f93e7** resolves the full dependency chain, imported ancestry,
  AABB, opaque surfaces and exact eight-point collider. **Two scenes** preserve bytes and
  registered scene/dependency UIDs through repeated save/load/resave.
- **58 floor rays** pass across both sides of both joins and into the wide mouth; **8 outside
  rays** remain clear, proving the narrow end is not overfilled. All floor hits have upward
  normals and Y=0 within 0.001 m. These rays deliberately straddle rather than claim exact
  shared-plane edge coverage; no ray failures or precision exceptions were waived.
- **12 trajectories × two modes = 24 traversals / 1,152 fixed ticks** use production
  `ActorMotion.step`, **48 ticks per mode**. Terminal and side connections each test X offsets
  **-1.35, 0, +1.35 m** in access-local space, both directions, crossing deck/access and
  access/promenade seams. Every tick retains floor support at the 0.001 m contact margin;
  endpoints match independent targets within **0.002 m**. AUTHORITY/REPLAY results agree.
- Canonical checks **exit 0**: engine/GUT pins, all **163 scripts' compile/style/formatting**,
  **14 Python tests**, **137/137 GUT tests / 6,523 assertions**, GUT import and intentional
  failure detection pass. Targeted pinned gdstyle and Python recipe byte-compilation also pass.
  Rendering finished before canonical checks; no deadline failure was suppressed or retried.

Four isolated Cycles/CPU/AgX renders, **96 samples**, denoising:
[hero](city_boardwalk_05-evidence/hero.png), [side](city_boardwalk_05-evidence/side.png),
[threshold detail](city_boardwalk_05-evidence/detail.png),
[47 m / 42° overhead](city_boardwalk_05-evidence/overhead_47m_42deg.png).
Native sizes: **1152×648 hero, 1024×576 detail, 1280×720 side/overhead**. Hero/overhead include
one unchanged straight deck; side/detail isolate this component. All four were visually
inspected: the flare and quiet flush threshold remain legible at gameplay distance, the timber
palette continues the sibling, and the detail shows the intended shallow seam/core recess.
Overhead is vertical-down at **47 m / 42° vertical FOV**, Blender +Y at image top. These are
**not native Godot gameplay or populated coast-fit captures**. The current 720 px cap supersedes
historical 1280×800 evidence. Render PNG compression 95 plus the family 7-bit/channel review-image
encoding keeps evidence lean; runtime material precision is unchanged.

### Exact reproduction (Git Bash, repository root)

Use fresh external scratch for each canonical run. The windowed editor is unavailable per brief;
text-authored scenes followed by headless normalization are the authorized fallback. No owner
live Blender/Godot session is contacted, modified or synchronized. The project addon starts its
own short-lived local endpoint during isolated CLI runs; no endpoint is contacted.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TOOLS=tools/asset_production/city_boardwalk_05
SCRATCH="C:/tmp/ft/assets/city_boardwalk_05/reproduce_$(date +%s)"
mkdir -p "$SCRATCH"
for script in author export render; do
  timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python "$TOOLS/$script.py"
done
# author_prefabs.py is INITIAL CREATION ONLY; it refuses existing normalized scenes.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOLS/export.py" -- "$SCRATCH/reexport.glb"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOLS/validate.py" -- "$SCRATCH/reexport.glb"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script "res://$TOOLS/check.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "res://$TOOLS/check.gd"
timeout 30 "$(mise which gdstyle)" check "$TOOLS/check.gd"
timeout 30 "$(mise which gdstyle)" fmt --check "$TOOLS/check.gd"
python -m compileall -q "$TOOLS"
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
python "$TOOLS/manifest.py" "$SCRATCH/checks"
```

Diagnostics are retained rather than suppressed. Blender's version-only probe emits the known
23-byte shutdown allocation notice; author/render emit the pinned `Material.use_nodes`
deprecation notice. Actual author/export/validate/render jobs exit 0 without allocation errors.
Godot import emits the addon's Godot-4.8 compatibility warning. Editor normalization saves
successfully and exits 0 but emits RID/ObjectDB shutdown leak diagnostics, matching the sibling
editor-tool limitation. The final **non-editor resource/physics check exits 0 without warnings,
errors or leaks**. Initial targeted style warnings (local count and one long comment) were fixed
before canonical checks. No vendor code, production motion rule or global setting was changed.

## Remaining acceptance

Independent technical/art review is required. Final dimensions, actual shore bearing and coast
fit, terminal district placement, partial fascia/rail openings, bend/support mating, non-level
access sites, populated native gameplay-camera readability, vehicle contact, water-edge/falloff
rules, combat queries, navigation, real multiplayer transport/admission, packaged platforms and
sustained Deck/performance remain **pending**. AUTHORITY/REPLAY agreement is not a network test.
No register, TODO, district route or whole-city gate is marked accepted by this delivery.
