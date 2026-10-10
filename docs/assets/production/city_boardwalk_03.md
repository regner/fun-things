# city_boardwalk.03 — Edge fascia and trim

10 October 2026. **Source, eight exports and linked prefabs delivered; bounded asset checks pass.
Independent review, world placement and gameplay/device acceptance remain pending.**
Produced by the commissioned implementation specialist on `lane/a-boardwalk`, under the
[production commission](commission.md) and current per-asset common brief. The current brief
supersedes the historical lead-only Git/prefab restriction. No sibling, shared brief, register,
project setting, route or shoreline was changed.

Family: [shared island boardwalk](../city_boardwalk.md). Read and matched the delivered
[straight deck](city_boardwalk_01.md) and [bend sections](city_boardwalk_02.md), Petrol & Coral
[art direction](../../art-direction.md), The Crescents v02 and world-v1 stage-03 district
identities / stage-04 streets. These establish family appearance, not measured coast fit.
Original Blender construction only: no downloads, image-to-mesh, brands, external textures,
duplicate deck carrier, road surfaces or runtime-generated render geometry.

## Design and dimensions

A continuous dark-slate exposed fascia with a slightly lighter, softly rounded **flush low trim**.
The 35 mm-deep cap projects 20 mm beyond the recessed fascia face. Both are one closed swept
profile, not separate floating trims. Broad, quiet shading matches the sibling underdeck slate;
no bolts, noisy wear, neon, raised kerb, duplicate railing or terminal furniture were introduced.
The full **3.6 m timber walking width remains unobstructed**. This is neither a new deck slab nor
a safety barrier: the shared quay rail `.02` still owns guard geometry and collision.

All dimensions are **provisional** under the standing instruction to proceed with sensible
family-consistent values. Actual coast, support and rail fit remain downstream.

| Profile interface | Godot metres |
| --- | --- |
| Walk-surface datum / underside | **Y=0 / Y=-0.240**, matching `.01` and `.02` |
| Fascia body | **0.080 m** outward depth, Y=-0.240 to -0.035 |
| Low cap | **0.100 m** outward depth, Y=-0.035 to 0 |
| Roundover | **0.003 m**, two bevel segments; no bevelled collision |
| Straight run length | **6.000 m**, matching `.01` repeat spacing |
| Terminal cap length | **3.800 m**: 3.6 m timber plus two 0.1 m side trims |
| Straight/terminal origin | Backing-plane centre at **(0,0,0)**; not ground/seabed |
| Straight/terminal axes | **+X outward**, length along Z; Blender +Z maps to Godot +Y |
| Curved origin | Same **deck entry centre (0,0,0)** as `.02`; not edge-centred |
| Curved angles | **90°, 45°, 22.5°**, separate inner/outer members |
| Curved circle centre | **(6,0,0)**; right bend towards +X, entry tangent -Z |
| Inner / outer trim radial bands | **4.1–4.2 / 7.8–7.9 m** |
| Arc stations | **2.8125°**, exactly matching the sibling chord spacing |

The slightly recessed curved arrises do not quite reach the nominal circle extrema. Source and
actual binary bounds are measured in [validation.json](city_boardwalk_03-evidence/validation.json).
Nominal AABB tolerance is **0.004 m**, explicitly admitting the 3 mm roundover; datum/depth and
engine comparison tolerance is **0.001 m**, source-to-binary comparison **0.00001 m**. The 4 mm
visual tolerance is not permission for a collision crack or step.

| Export/prefab suffix | Nominal Godot AABB min → max (X,Y,Z) |
| --- | --- |
| none (straight) | (0,-.24,-3) → (.1,0,3) |
| `_terminal` | (0,-.24,-1.9) → (.1,0,1.9) |
| `_outer_90` | (-1.9,-.24,-7.9) → (6,0,0) |
| `_inner_90` | (1.8,-.24,-4.2) → (6,0,0) |
| `_outer_45` | (-1.9,-.24,-5.586144) → (.484567,0,0) |
| `_inner_45` | (1.8,-.24,-2.969848) → (3.100862,0,0) |
| `_outer_22p5` | (-1.9,-.24,-3.023199) → (-1.206260,0,0) |
| `_inner_22p5` | (1.8,-.24,-1.607270) → (2.212094,0,0) |

### Family mating and terminal placement

- On an identity `.01`, place straight fascia at **(1.8,0,0), yaw 0** and
  **(-1.8,0,0), yaw π**. The cap adds width outboard, never intrudes into the walking line.
  Repeat at 6 m spacing, without scale correction. The backing faces meet the timber edges;
  the existing 4 cm underdeck core setback is concealed, not duplicated as another slab.
- On `.02`, choose the matching inner/outer angle variants and use **the same transform as
  the deck**. Do not offset their pivots to X=±1.8 a second time. Both strips meet the entry
  and exit width planes. Reversed traversal supplies left turns with rigid rotation/translation,
  no negative-scale mirroring.
- On an identity `.01`, place a terminal at **(0,0,-3), yaw +π/2** for the north end, or
  **(0,0,3), yaw -π/2** for the south end. It extends 0.1 m beyond that end and covers the
  side-strip end faces with a clean butt joint; small rounded joint lines remain intentional.
- The same terminal width can mate a curved connector: entry centre with yaw -π/2, or exit
  centre with yaw **π/2−θ**. The cap's +X faces outward from the route. Curved terminal
  placement is a dimensional handoff, not an additional tested world placement.
- **Do not put terminal caps at continuing deck joins or across landward access openings.**
  `.05` owns access/transition geometry. `.04` supports meet Y=-0.24; this fascia makes no
  claim of structural capacity, rail-post mounting capacity or final support spacing.
- Ironreach's northern boundary and Broadlot's southwestern boundary may use these clean caps
  with `.05` access and shared quay rail `.02` end returns. **East Docks remains excluded**;
  no closed whole-island ring, new bridge, inner-basin dock or shoreline change is authorized.
  The six recorded coastal districts remain prospective consumers; Old Quay is only a candidate.

## Source, exports and materials

- Source: `art/source/models/environment/city_boardwalk_03/city_boardwalk_03.blend`.
- Eight named collections: **`export_city_boardwalk_03{suffix}`** from the table above.
- Each collection has identity root **`CityBoardwalk03{suffix}`** and one identity child
  **`CityBoardwalk03{suffix}_Mesh`**. Collections overlap intentionally at their respective
  origins as alternatives; the source is not a placed assembly.
- Eight explicit GLBs and their `.glb.import` sidecars:
  `art/models/environment/city_boardwalk_03/city_boardwalk_03{suffix}.glb`.
- Parametric profile/author/export/validator, isolated renderer, initial prefab author, saved
  mating fixture, headless check and manifest helper:
  `tools/asset_production/city_boardwalk_03/`.

Metre units, applied transforms and weighted corner normals; glTF Y-up conversion occurs once.
Only the root and mesh export. No studio geometry is saved in the source or exported. The
renderer loads unchanged sibling Blender meshes as **context only**, alongside transient studio
placements and lighting. It never writes sibling sources or embeds their geometry in this asset.

Each export is **one mesh / two opaque backface-culled Principled surfaces**, ordered:

| Slot / material | Linear base RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `boardwalk_fascia_slate` | (.048,.069,.078), matching sibling underdeck | .15 / .58 |
| 1 `boardwalk_edge_trim` | (.090,.126,.137) | .20 / .50 |

No textures, UV-dependent shader, embedded image, external material copy, emission, transparency,
rig, animation, destruction state or sockets. Materials remain GLB-owned. No custom LOD; default
Godot automatic LOD/shadow-mesh generation is retained, pending repeated-route visual/performance
review. The shared `tools/assets/blender/export_settings.json` is the exporter-settings owner.
The local geometry and binary audit follow the accepted family conventions; no general shared
swept-profile builder/validator exists here, and no shared tooling or competing export contract
was added.

## Prefabs and collision

Eight `scenes/prefabs/environment/city_boardwalk_03{suffix}.tscn` wrappers retain their GLB at
**`Visuals/Model`, identity transform**. No embedded render meshes, editable imported children,
material overrides, runtime hierarchy creation or behaviour scripts. Pinned headless Godot
normalized scene/node/dependency identities and preserved them over save/load/resave.

Every wrapper has **one StaticBody3D at `Collision/Body`, layer 1 / mask 0**, with one direct
`Edge` CollisionShape3D. Straight and terminal use **0.1 × 0.24 × length BoxShape3D** at
**(.05,-.12,0)**. Curved members use a closed **ConcavePolygonShape3D ribbon**, with only top,
bottom, inside/outside perimeter and two end faces. This continuous static walk collider is
needed for the flush cap; a broad convex hull would incorrectly fill the inside of the bend.
The two materials and cosmetic 20 mm fascia recess do not create collision seams or snag points.
The full-depth collider deliberately fills that tiny recess. Concave ribbons are static-only.

Per curved ribbon: **260 triangles / 132 unique vertices (90°), 132 / 68 (45°), 68 / 36 (22.5°)**.
Saved float32 topology has zero degenerate triangles or open/nonmanifold edges. Collision is
independent of cosmetic roundovers and cannot be interpreted as an elevated guard. **Nothing
blocks actors above Y=0**. Actual waterfront use still requires shared guard rails, appropriate
supports/shore treatment and reviewed falloff/access rules. Avoid duplicate terrain collision.

`tools/asset_production/city_boardwalk_03/mating_check.tscn` saves all three dressed bends with
unchanged `.01` entry/exit decks, plus one straight/side/terminal assembly. Cases are separated by
20 m; the terminal case is centred at X=60. A collision-only capsule uses the production
**ActorMotion** API, radius **0.35 m**, height **1.8 m**. Edge-centred trajectories deliberately
stress cap support; they do not approve walking outside future guardrails or redefine route width.

## Validation and evidence

[validation.json](city_boardwalk_03-evidence/validation.json) records source/binary/serialized
collision measurements, engine results and canonical checks.
[manifest.json](city_boardwalk_03-evidence/manifest.json) hashes every delivered payload except
itself. [final.log](city_boardwalk_03-evidence/final.log) retains a concise command/diagnostic
receipt; scratch renders, fresh exports and raw logs stay outside the checkout.

- Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**.
- Per export (inner and outer have the same counts):

  | Member | Triangles | Source vertices | GLB vertices | GLB bytes |
  | --- | ---: | ---: | ---: | ---: |
  | Straight | 164 | 84 | 108 | 5,484 |
  | Terminal | 164 | 84 | 108 | 5,552 |
  | 90° inner / outer | 1,280 each | 642 each | 728 each | 27,124 each |
  | 45° inner / outer | 704 each | 354 each | 408 each | 16,004 / 16,008 |
  | 22.5° inner / outer | 416 each | 210 each | 248 each | 10,444 / 10,448 |

- All eight together: **5,128 triangles, 2,580 source vertices, 2,984 GLB vertices,
  118,188 GLB bytes**. These are alternative/reusable members, not one mandatory placed mesh.
- **Zero degenerate source/export faces and zero nonmanifold edges**, including actual binary
  export edge checks after exact-position welding across material/normal seams. Finite geometry,
  unit normals, consistent winding and identity transforms pass. Bounds/datum match the contract.
- **All eight fresh-process reexports are byte-identical**. Source/export/collision validation
  was also run against the final normalized saved scenes.
- Godot **4.8.dev7.official.c971f93e7** resolves the complete dependency chain, imported ancestry,
  bounds, two opaque surfaces and intended colliders. **Nine scenes** (eight wrappers and fixture)
  pass two save/load/resave cycles without byte drift or lost scene/dependency UIDs.
- **222 nominal support rays**, **10 outside rays** and **2 fascia-height rays** are checked.
  Of the nominal floor rays, **220 hit directly; two exact shared-edge rays miss in Jolt**.
  The two positions remain in JSON. Each requires four surrounding floor witnesses within
  **0.0001 m**, all hitting upward-facing Y=0. Saved collision topology independently proves
  exact float32 shared edges. This explicitly bounded ray precision limitation is not concealed
  as a claim that every exact-edge ray hit.
- **18 bend trajectories and 3 terminal trajectories, each in AUTHORITY and REPLAY: 42 full
  traversals / 4,572 fixed ticks**. Bend paths use radii **4.15, 6 and 7.85 m**, both directions,
  crossing both straight/bend joins. Every tick retains floor support; each segment endpoint
  is within 0.002 m of its intended position. Y stays at the 0.001 m contact margin. Terminal
  paths cross onto the cap at X=58.15,60,61.85 and finish Z≈-3.050001 m. Both modes agree.
  The below-deck side ray hits fascia before the deck; the above-deck ray confirms no new barrier.
- Pinned gdstyle passes without warnings; Python recipe byte-compilation passes. Canonical
  checks pass **engine/GUT pins, all 161 files' style/formatting, this asset's compile check,
  14 Python tests, 137/137 GUT tests / 6,523 assertions, GUT import and negative-test detection**.
  **The aggregate canonical command exits 1**: its shared 120-second compilation deadline is
  exhausted after 157 scripts, leaving four unrelated final scripts with `CHECK DEADLINE EXCEEDED`:
  `tools/assets/weapons/smg_wedgewire/editor_author.gd` and
  `tools/assets/world/brackett_greybox/{author_editor,capture,check_scene}.gd`.
  These are missing aggregate validation, not observed GDScript errors. They are not an allowed
  ignored fixture baseline: the full canonical suite remains **not fully green**. No unchanged
  failing aggregate command was repeated and no shared tooling was modified to hide it.

Four isolated Cycles/CPU/AgX renders, **96 samples**, denoising:
[hero](city_boardwalk_03-evidence/hero.png), [side](city_boardwalk_03-evidence/side.png),
[terminal detail](city_boardwalk_03-evidence/detail.png),
[47 m / 42° overhead](city_boardwalk_03-evidence/overhead_47m_42deg.png).
Native sizes are **1152×648 hero, 1024×576 detail, 1280×720 side and overhead**. Hero/overhead show
all eight trim variants on unchanged sibling decks; side/detail show the straight terminal fit.
All four, including final compact encodings, were visually inspected: the narrow quiet slate
border reads at gameplay scale without displacing the warm walking strip; close views show the
cap/fascia reveal and clean terminal butt joint. Overhead is vertical-down at **47 m / 42° vertical
FOV**, Blender +Y at image top. These are **not native engine gameplay or coast-fit captures**.
The current 720 px production cap supersedes historical 1280×800 evidence. PNG compression 95
at render and documented 7-bit/channel review-image encoding retain roughly 281–450 KB per image;
no runtime source/export material is quantized.

### Exact reproduction (Git Bash, repository root)

Use fresh external scratch for each canonical run. The windowed editor is unavailable per brief;
text-authored scenes followed by headless normalization are the authorized fallback. No owner
live Blender/Godot session is used, modified or synchronized by these commands. The project addon
starts its own short-lived local endpoint during CLI runs; no endpoint is contacted.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TOOLS=tools/asset_production/city_boardwalk_03
SCRATCH="C:/tmp/ft/assets/city_boardwalk_03/reproduce_$(date +%s)"
mkdir -p "$SCRATCH"
for script in author export render; do
  timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python "$TOOLS/$script.py"
done
# author_prefabs.py is INITIAL CREATION ONLY; it refuses existing normalized scenes.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOLS/export.py" -- "$SCRATCH/reexport"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOLS/validate.py" -- "$SCRATCH/reexport"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script "res://$TOOLS/check.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "res://$TOOLS/check.gd"
timeout 30 "$(mise which gdstyle)" check "$TOOLS/check.gd"
timeout 30 "$(mise which gdstyle)" fmt --check "$TOOLS/check.gd"
python -m compileall -q "$TOOLS"
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
python "$TOOLS/manifest.py" "$SCRATCH/checks"
```

Diagnostics are retained, not suppressed. Blender's version-only probe emits a 23-byte shutdown
allocation notice; author/render emit the pinned `Material.use_nodes` deprecation warning.
Actual author/export/render/validate jobs exit 0 without allocation errors. Headless editor import
emits the addon's Godot-4.8 compatibility warning. Editor normalization saves successfully and
exits 0, but emits RID/ObjectDB shutdown leak diagnostics, matching sibling tool limitations.
The final **non-editor resource/physics run exits 0 without warnings, errors or leak diagnostics**.
Initial targeted style warnings (one long line and an await-in-loop annotation) were corrected
before canonical checks. No vendor code or broad diagnostic filtering was changed.

## Remaining acceptance

Independent technical/art review is required. Final dimensions, actual coastline and district
terminal fit, support/access/rail mating, populated native gameplay-camera readability, vehicle
contact, water-edge/falloff rules, combat queries, navigation, real multiplayer transport/admission,
packaged platforms and sustained Deck/performance remain **pending**. AUTHORITY/REPLAY agreement
is not a network test. The bounded exact-edge Jolt ray limitation and incomplete aggregate compile
sweep are explicit review risks. No register, TODO, district route or whole-city gate is accepted
by this delivery.
