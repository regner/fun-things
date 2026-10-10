# city_boardwalk.01 — Straight deck section

10 October 2026. **Source, export and linked prefab delivered; bounded headless checks pass.
Independent review, world placement and gameplay/device acceptance remain pending.**
Produced by the commissioned implementation specialist on `lane/a-boardwalk` under the
[production commission](commission.md) and the current per-asset common brief. The latter
supersedes the historical commission's lead-only Git/prefab restrictions. No shared register,
brief, project setting or world scene was changed.

Family: [shared island boardwalk](../city_boardwalk.md). References inspected: Petrol & Coral
[art direction](../../art-direction.md), The Crescents v02 concept, world-v1 stage-03 district
identities and stage-04 streets. These guide appearance, not measured construction or routes.
This first family member establishes **provisional**, not owner-ratified, interfaces for later
members. Original Blender construction only; no downloaded geometry, image-to-mesh, brands,
external textures or generated runtime meshes.

## Design and dimensions

Quiet weathered warm-brown cross-deck timbers, broad regular seams, softly rounded arrises and
an inset dark-slate underdeck core. Restrained three-tone timber variation avoids noisy grain,
fasteners or high-contrast stripes. This is a walking deck, not a floating marina pontoon.
No duplicated lamps, seats, rails, shore rocks, seawalls, support legs or applied edge fascia.

All dimensions below are **provisional** under the standing instruction to proceed with
sensible family-consistent values. They require shore/route fit review before world placement.
Numeric source/export/import tolerance: **±0.001 m**.

| Contract | Godot local metres |
| --- | --- |
| Overall width X / height Y / length Z | **3.600 / 0.240 / 6.000** |
| Whole visual AABB | **(-1.800, -0.240, -3.000) → (1.800, 0, 3.000)** |
| Pivot / walk-surface datum | **(0, 0, 0)**, centred on deck surface; not water or seabed |
| Straight route direction | Local **-Z** (Blender +Y); +Y up (Blender +Z) |
| End join planes | Z = **±3.000**, span X = ±1.800, standing surface Y = 0 |
| Repeat spacing | **6.000 m**, identity rotation; no overlap or corrective scale |
| Cross-deck boards | 20 × **3.600 × 0.080 × 0.288**, at **0.300 m** pitch along Z |
| Quiet board seams | **0.012 m**, plus 0.004 m edge roundover; never collision gaps |
| End half-seam | 0.006 m setback per end board, continuing the 0.012 m repeated seam |
| Recessed core | **3.520 × 0.160 × 6.000**, Y = -0.240 to -0.080 |

### Handoff to the remaining boardwalk family

- `.02` bend/corner members should meet a **3.6 m-wide, Y=0** walking section at their
  connectors and preserve the -0.24 m underside interface. Angle selection is their scope.
- `.03` owns exposed fascia and low edge trim. Side attachment planes are **X=±1.8**;
  terminal planes are **Z=±3**. The inset core is structural backing, **not** the finished
  exposed-edge treatment. Do not stack another full walking slab on this one.
- `.04` support members meet the **Y=-0.24** underside; support spacing and coast heights
  remain theirs to resolve. This shallow core is not a claim of real structural engineering.
- `.05` transitions meet the **Y=0** walking datum with no step. Exact landward locations,
  widths and grades remain transition/placement scope.
- Shared `city_quay_furniture.02` owns rail geometry and rail collision. It is not a source
  dependency of this bare deck. Mounting coordination remains pending; reserve the route and
  fit rails outboard where possible rather than silently reducing the nominal 3.6 m width.
  No invented rail sockets, post spacing or second rail set are delivered here.

No existing sibling outputs were present when this member was authored. Do not extrapolate
these provisional interfaces into coastline edits, a closed island ring, East Docks coverage,
or a bridge across navigable water. The six recorded coastal districts are candidate placement
consumers; this delivery places nothing in them.

## Source, export and materials

- Source: `art/source/models/environment/city_boardwalk_01/city_boardwalk_01.blend`.
- Named collection: `export_city_boardwalk_01`.
- Identity-transform export root / child: `CityBoardwalk01` / `CityBoardwalk01_Mesh`.
- Linked output: `art/models/environment/city_boardwalk_01/city_boardwalk_01.glb`, with
  committed `.glb.import` UID metadata.
- Parametric recipe, exporter, validator, isolated renderer and manifest script:
  `tools/asset_production/city_boardwalk_01/`.

Metre units, applied transforms and corner normals; glTF Y-up conversion is applied once.
Twenty closed timber solids and one closed backing solid share **one mesh / four surfaces**.
The export contains only the root and mesh, no studio objects. Studio cameras, lights and
plane are transient in `render.py`, never saved as asset source/export geometry.

Opaque, backface-culled Principled material slots, in exported order:

| Slot / name | Linear base RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `boardwalk_underdeck_slate` | (0.048, 0.069, 0.078) | 0.15 / 0.58 |
| 1 `boardwalk_timber_warm` | (0.235, 0.145, 0.085) | 0 / 0.68 |
| 2 `boardwalk_timber_light` | (0.260, 0.166, 0.101) | 0 / 0.68 |
| 3 `boardwalk_timber_muted` | (0.215, 0.136, 0.085) | 0 / 0.68 |

No texture dependency, embedded images, procedural shader, emission, transparency, rig,
animations, destruction states or custom LOD. Imported materials remain GLB-owned; no redundant
`.tres` copies. Default Godot automatic LOD/shadow-mesh generation is retained; repeated-route
LOD and performance review remain pending. Shared `tools/assets/blender/export_settings.json`
is the export-settings owner; no private alternative settings contract was introduced.

## Prefab and collision

`scenes/prefabs/environment/city_boardwalk_01.tscn` retains the imported GLB at
**`Visuals/Model` with identity transform**. No embedded meshes, editable imported children,
runtime hierarchy creation or behaviour script. Scene UID, node identities and dependency UID
were normalized by the pinned headless engine and survive save/load/resave.

`Collision/Body` is one StaticBody3D on **layer 1 / mask 0**, with a direct child `Deck`:
a **3.6 × 0.24 × 6 m BoxShape3D** centred at **(0, -0.12, 0)**. It continuously supports the
walking plane at Y=0, bridges visual plank seams, and deliberately envelopes the shallow
underdeck recesses. Bevels and the 4 cm backing inset cannot catch the actor. There are no
rails or invisible edge barriers in this bare component. Safe elevated/coastal placements
require the shared rails and compatible support/shore arrangement; a rail-free world route
is **not** accepted. Avoid coplanar duplicate terrain/deck collision at placement.

Saved `tools/asset_production/city_boardwalk_01/walk_check.tscn` instances two unchanged prefabs
at Z=0 and Z=6. Its collision-only capsule uses the **production ActorMotion API**, radius
0.35 m / height 1.8 m; no test-only movement formula or arbitrary visible fixture geometry.

## Validation and evidence

[validation.json](city_boardwalk_01-evidence/validation.json) records measured source and raw
binary GLB data, Godot import/physics results and production check results.
[manifest.json](city_boardwalk_01-evidence/manifest.json) hashes every delivered payload except
itself. [final.log](city_boardwalk_01-evidence/final.log) is a concise command/diagnostic receipt;
raw scratch logs and fresh reexports remain outside the checkout.

- Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**.
- **2,268 triangles; 1,176 source vertices; 1,512 exported vertices; one mesh; four surfaces.**
- **Zero degenerate faces, zero non-manifold edges**, consistent winding, finite coordinates,
  unit-length source/export normals and baked identity transforms.
- Source and actual binary GLB bounds match the independent dimensional contract above.
- Fresh-process reexport is **byte-identical**, GLB **66,032 bytes**.
- Godot **4.8.dev7.official.c971f93e7** loads the entire dependency chain and confirms GLB ancestry,
  identity placement, AABB, four opaque backface-culled surfaces and intended collider.
- Prefab and fixture pass two save/load/resave cycles with byte-stable saved files.
- **18 support rays** cover both sections, both sides and the join; **2 outside-edge rays** are
  clear. All support hits lie on Y=0 within 0.001 m.
- Production `ActorMotion.step` traverses the seam at X=-1.4, 0 and +1.4 m forward, and at X=0
  in reverse. Each case uses **48 fixed ticks per mode**, in AUTHORITY and REPLAY. Forward
  endpoints are Z=5.00000048 m, reverse Z=0.99999982 m; Y=0.001 m collision margin is retained.
  Both modes agree, no lateral drift, and final floor support passes `test_move`.
- Final canonical checks pass engine/GUT pins, owned GDScript compile/style, all 14 Python
  repository tests, GUT import and intentional-failure detection. Targeted gdstyle also passes.
  **The final GUT run fails 1 of 137 tests**: unchanged
  `tests/unit/session/test_session_service.gd::test_join_connection_deadline_reports_connect_timeout`
  observes CLOSING rather than IDLE (lines 170–172), then accesses absent disconnect history.
  The initial full run passed all 137 tests / 6,523 assertions. The final failure is retained,
  not ignored as an allowed baseline failure; no session code was changed or failing command
  repeated. The final suite is therefore **not fully green**; session-test follow-up is pending.

Four isolated Blender Cycles/CPU/AgX renders, **1280×720**, 32 samples and denoising:
[hero](city_boardwalk_01-evidence/hero.png), [side](city_boardwalk_01-evidence/side.png),
[detail](city_boardwalk_01-evidence/detail.png),
[overhead](city_boardwalk_01-evidence/overhead_47m_42deg.png).
Overhead is vertical-down at **47 m / 42° vertical FOV**, +Y Blender at image top. The 720 px
height follows the current production evidence cap, superseding historical 1280×800 evidence.
All four were visually inspected: the open silhouette, muted timber rhythm, slim slate core
and soft edge separation read cleanly; at gameplay scale the quiet warm walking strip matters
more than individual seams. These are **not** native Godot gameplay captures or world-fit proof.
PNG compression is 95 during render, then losslessly encoded after a documented 7-bit/channel
review-image quantization to keep evidence lean; this does not affect source/export materials.

### Exact reproduction (Git Bash, repository root)

Use a **fresh scratch directory** for each production-check run. No live Blender/Godot session
is used. The windowed editor is unavailable per task; direct scene text authoring followed by
headless normalization is the explicit fallback, not proof an unrelated open editor is synced.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TOOLS=tools/asset_production/city_boardwalk_01
SCRATCH="C:/tmp/ft/assets/city_boardwalk_01/reproduce_$(date +%s)"
mkdir -p "$SCRATCH"
for script in author export render; do
  timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python "$TOOLS/$script.py"
done
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
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
python "$TOOLS/manifest.py" "$SCRATCH/checks"
```

Diagnostics are not hidden: Blender's version-only probe emitted a 23-byte shutdown allocation
notice; author/render emit the pinned API's `Material.use_nodes` deprecation notice. Actual
source/export/validate/render jobs exit 0 without allocation errors. Headless editor
normalization emits the addon 4.8 compatibility warning and editor RID/ObjectDB shutdown
leak diagnostics despite completed saves. This is a retained editor-tooling limitation, not a
clean diagnostic run. An attempted non-editor save stripped scene/dependency UIDs on this pin;
self-review caught it before commit. The final helper **rejects non-editor normalization**,
requires saved scene/dependency UIDs, and the final editor save restores/retains them. The final
**non-editor headless load and movement checks** exit 0 without warnings/errors/leaks and do
not save scenes. Canonical checks have the unrelated session-test failure recorded above.
No addon edits or broad log suppression were used.

## Remaining acceptance

Independent technical/art review is required. World placement, final dimensions/shoreline fit,
corner/transition/support/rail mating, populated gameplay-camera readability, vehicle contact,
water-edge/falloff rules, navigation, combat queries, real multiplayer transport/admission and
sustained Deck/exported-platform performance remain **pending**. Bounded AUTHORITY/REPLAY mode
equivalence is not a multiplayer network test. This component is not permission to extend the
boardwalk through East Docks or change the island. No register row, TODO or whole-city readiness
was marked accepted by this delivery.
