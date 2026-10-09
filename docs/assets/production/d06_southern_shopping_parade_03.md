# d06_southern_shopping_parade.03 — North-end facade facing the bridge forecourt

**Source/export and bounded linked-prefab candidate. Independent review and final
production/world acceptance remain pending.** Original author and technical integrator:
commissioned isolated production worker. Current per-ID task and [commission](commission.md)
supersede the historical concept-only restriction in the [family brief](../d06_southern_shopping_parade.md).
The supervisor approved this provisional 17.4 × 4.8 × .18 m relief and its simple
collision envelope during production. Final parcel/proportion and bridge-fit selection
are not implied.

## Design and family ownership

A shallow architectural end-wall treatment terminates the single long parade: broad
muted-plum framing and field, a quiet blue/slate upper brow and toe, three tall west
relief blades and two shorter east blades. Narrow cyan and magenta inlays establish
an asymmetric commercial rhythm without another store, luminous roof ring or tenant
sign. Smooth bevels and broad plane normals preserve the family's restrained finish.
The central field is architectural cladding, not a duplicate fascia/artwork carrier.

References read: Petrol & Coral; Stage 3 Signal Row identity; Stage 4 streets; selected
Signal Row v03 and map extract; the family brief; completed [.01 shell](d06_southern_shopping_parade_01.md)
and [.02 fitting interface](d06_southern_shopping_parade_02.md); city_lights.01 source/export
quality bar; batch 01–03 prefab conventions. The district image, map, previous family
hero and accepted light example were visually inspected. Concepts guide style, not
measured geometry. All new visible geometry is original editable Blender construction;
no downloads, real brands, image-to-mesh, textures or runtime-generated render meshes.

- `.01` retains the continuous shell/roof, standard openings/mounts, north datum and
  main solid collision. A separately authorized source repair is recorded below.
- `.02` retains six existing shared-fitting bays. Its scenes/placements are unchanged.
- `.03` supplies only this end-wall relief and its narrow projecting collision envelope.
- Shared fittings still own doors, glazing, fascia and canopy hardware; commercial
  graphics own tenant copy. No duplicate fitting or sign meshes were authored here.
- The footbridge still lands on the **ground forecourt**, never the roof. No bridge,
  landing, paving, road, sidewalk, entrance hole, interior, opening door, roof traversal,
  destruction state, rig, animation, navigation or gameplay script is introduced.

## Metres, mounting and collision

Blender +Y faces north/outward and maps to Godot -Z; Blender +Z maps to Godot +Y.
All root/mesh transforms are identity, with metre units and geometry offsets baked in.
The origin is the **north wall's ground datum**, not the thin relief's volume centre.

| Measurement | Metres, Godot local coordinates |
| --- | --- |
| Component visual AABB min / max | (-8.700, 0, -.180) / (8.700, 4.800, 0) |
| Component width X × height Y × depth Z | 17.400 × 4.800 × .180 |
| Root/pivot and wall attachment plane | (0,0,0), Z=0 |
| Reference component translation | (0,0,-30), identity basis |
| Relief top / existing roof coping top | 4.800 / 5.400 |
| Component margin from each 18 m shell side | .300 |
| Toe backing / existing north plinth projection | .035 / .035 |
| Full fitted reference AABB min / max | (-10.100,0,-30.180) / (9.040,5.400,30.035) |
| Full fitted reference dimensions X/Y/Z | 19.140 × 5.400 × 60.215 |
| Bounds tolerance / source-to-GLB comparison | ±.001 / .00001 |

Mount the component root at the actual existing datum:
`Parade/Shell/Visuals/Model/D06SouthernShoppingParade01/north_facade_datum`
in the supplied reference. The checker compares complete global transforms, not only
handwritten positions. `Visuals/Model` is always an identity-transform linked import;
no corrective scaling, mirroring or rotation. No new socket is needed.

The lower toe starts .035 m forward of the wall to meet the existing plinth without
penetration. All remaining backing lies on or outside the north wall. Separate closed
relief pieces intentionally meet at hidden backing surfaces; there are no open-edge
panels. The relief is not a freestanding wall and must be used with the solid shell.

**Collision decision:** the supervisor required either ≤.05 m decorative projection
or a thin collider. This delivery uses the approved **.18 m projection plus one box**:
`Collision/Body/ReliefEnvelope`, size `(17.4,4.8,.18)`, centre `(0,2.4,-.09)`, static
world layer 1/mask 0. Its rear is flush with the shell collision plane. It conservatively
bridges shallow relief gaps, preventing a pressed .35 m actor capsule clipping into
inlays and avoiding per-blade snags. The separate `.01` box remains the main exterior
solid; fitting collisions stay disabled. The assembled reference has exactly **two**
active shapes. No collider is inferred from mesh import suffixes.

The relief consumes .180 m from the wall plane, .145 m beyond the prior .035 m visual
plinth. Within `.01`'s frozen-map north reserve to local Z=-40, an 18 × **9.820 m**
rectangle remains beyond the new outer face. This is a subset of the already checked
reserve, not a new bridge or current-road-tool clearance result. Side walking bands
and world transforms are unchanged. Final forecourt/bridge geometry, movement envelopes
and the three old building identity migrations remain world-integration work.

## Source, exports, materials and prefabs

- Source: `art/source/models/environment/d06_southern_shopping_parade_03/d06_southern_shopping_parade_03.blend`.
- Export collection: `export_d06_southern_shopping_parade_03`.
- Root / mesh: `D06SouthernShoppingParade03` / `D06SouthernShoppingParade03_Mesh`.
- Export: `art/models/environment/d06_southern_shopping_parade_03/d06_southern_shopping_parade_03.glb`, with committed `.import`.
- Standalone component: `scenes/prefabs/environment/d06_southern_shopping_parade_03.tscn`.
- Fitted reference: `scenes/prefabs/environment/d06_southern_shopping_parade_03_reference.tscn`.
- Reproducible tools: `tools/asset_production/d06_southern_shopping_parade_03/`.

The reference composes the unchanged `.02` scene and one `.03` component. It is not a
new building variant or world placement. Existing Blender source/export mappings stay
with the referenced family docs; `validation.json` records all 26 reused dependency
hashes. GLB UID `uid://2e3i68tsb4t3`, component UID `uid://vjfyl4jhgw8c`, reference UID
`uid://ciucr7qgmuw7l`; engine-generated node identities are retained.

Pinned **Blender 5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**.
`export.py` loads `tools/assets/blender/export_settings.json` with the named collection
and static animation/skin overrides. All modelling modifiers are applied. Studio
camera, lights, ground and one-metre reference remain outside the export collection.
No embedded images, external textures, unused material resources or prototype references.

Five opaque back-culling Principled material surfaces; sRGB swatches converted to linear:

| Material | Swatch | Metallic / roughness |
| --- | --- | --- |
| `parade_muted_plum_render` | #81777C | 0 / .70 |
| `north_deep_plum_relief` | #70616F | 0 / .70 |
| `parade_quiet_blue_roof` | #405B68 | .12 / .65 |
| `north_cyan_inlay` | #60ADBA | .15 / .50 |
| `north_magenta_inlay` | #B5628F | .15 / .50 |

The matching plum/slate names and values follow `.01`; other accents are confined to
the relief. All are non-emissive. UV textures, rigs, animations and additional LODs are
not applicable to this static flat-material component. Engine automatic LOD generation
stays at its default; transition/repeated-placement performance remains unaccepted.

## Validation and visual evidence

Component: **3,196 triangles; 1,632 source vertices; 1,632 exported split vertices;
one mesh; five surfaces; two exported nodes**. **Zero degenerate source faces/GLB
triangles and zero nonmanifold edges; unit-length source/export normals and positive
triangle/normal alignment.** Decoded GLB bounds match saved source conversion. Ground
and wall datums pass. Fresh saved-source reexport is **byte-identical**, **57,864 bytes**.
`validation.json` retains measurements, full material values and reexport SHA-256;
`manifest.json` hashes every produced payload except itself.

Reference totals, combining the checked `.02` inputs and this component: **58,440
triangles; 29,540 source vertices; 31,632 exported split vertices; 158 mesh instances;
172 surfaces; 32 linked GLB instances**. These are resource counts, not measured draw
calls or a device budget. Actual engine mesh count and assembled AABB are checked.

Pinned Godot **4.8.dev7.official.c971f93e7** resolves all dependencies, materials and
UIDs; both wrappers pass pack/save/reload byte stability. Four northward-approach rays
hit the relief at Z=-30.18, except the uncovered side margin ray which hits `.01` at
Z=-30. Five radius-.35 m, height-1.8 m capsule samples confirm the projecting envelope
and clear north/west/east approach space. An actual `CharacterBody3D.move_and_collide`
probe approaching from Z=-32 stops at **Z=-30.53125**, outside the relief. These bounded
queries/motion are not production player/vehicle, aim or multiplayer acceptance.

[Hero](d06_southern_shopping_parade_03-evidence/hero.png),
[side/full family](d06_southern_shopping_parade_03-evidence/side.png),
[relief detail](d06_southern_shopping_parade_03-evidence/relief_detail.png),
[47 m / 42° overhead](d06_southern_shopping_parade_03-evidence/overhead_47m_42deg.png).
All four final images were personally inspected. Isolated Blender Cycles CPU, 24 samples,
AgX, 1280×800. The renderer uses actual exported GLBs at the engine-recorded reference
transforms, not a separately authored assembly.

Hero/detail show smooth grouped strips, coherent shallow backing and a clean north
corner. The full-family side retains one continuous roof and six west shop stations.
The calibrated overhead is vertically down, north-up at Blender **(0,38,47)**, **42°
vertical FOV**, centred on the forecourt rather than `.01`/`.02`'s centre crop. The end
wall becomes a narrow oblique band: inlays are secondary color rhythm, **not essential
overhead wayfinding**. Empty studio ground demonstrates no added obstacles, not an
accepted ground material or actual bridge landing. No native Godot visual claim.

## Separate north-corner source repair

Initial close evidence exposed a pre-existing `.01` coplanar cap stripe beside the
relief, not a collision or .03 envelope defect. The supervisor explicitly extended the
otherwise per-ID scope to a minimal separate repair: recess the northmost west pier
and both north head-course caps **2 mm**, preserving envelope, collision, pivot and
identities. Commit **`dd66d23`** contains the .01 source/export, three regression ray
checks and refreshed `.01`/`.02` docs/evidence. All source/export, import/roundtrip,
reference-fit and production checks passed; `.02` scenes/placement stayed byte-unchanged.
All eight refreshed family renders were inspected. Final .03 detail confirms the black
stripe is gone. This delivery keeps its originally approved dimensions unchanged.

## Reproduction and diagnostics

The supplied task prohibits live MCP sessions and reports the windowed editor unavailable.
Scenes were therefore authored as text and normalized with isolated pinned headless
Godot; no live session was used or touched. A separate open editor is not claimed
synchronized. From repository root in Git Bash, with scratch outside the worktree:

```sh
NID=d06_southern_shopping_parade_03
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
SCRATCH="C:/tmp/ft/assets/$NID"
mkdir -p "$SCRATCH"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/validate.py"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --path . --script "res://tools/asset_production/$NID/check_prefab.gd"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/render.py"
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks-final"
python "tools/asset_production/$NID/record.py"
python "tools/asset_production/$NID/record.py" --verify
```

Production-check output must be a fresh directory. `record.py` requires completed
`geometry.json`, `prefab.json`, `normalize.json`, `checks-final/summary.json`, and raw
normalization/runtime logs under scratch. It reuses `.02`'s checked dependency map;
`--verify` validates both complete owned payload hashes and all dependency hashes
without writes. Regenerating source/exports requires refreshing import/evidence/manifests
together, never modifying sources merely to reproduce a read-only review.

Production checks **PASS**: all discovered owned GDScripts compile and pass pinned
format/lint; Python **9/9**; GUT **23/23, 196 assertions**; intentional negative control
correctly fails. No inherited failure was ignored. Initial owned lint warnings were
fixed by formatting and splitting test helpers. Blender emits non-failing API
deprecation notices. Headless editor normalization exits 0 but emits the known toolkit
4.8 compatibility warning and scan-thread/RID/ObjectDB shutdown diagnostics, retained
in `final.log`. Fresh runtime load/query/motion and production-check mirror are clean.

## Remaining acceptance

Independent technical/art review; owner final proportions/tenant selection; district
commercial graphics; native gameplay-camera readability; actual player/vehicle/aim and
multiplayer checks; current road-tool walking and bridge approach fit; saved world
identity consolidation/placement; packaged builds, sustained/repeated-placement profiling
and Deck checks remain pending. No queue, shared progress/brief, project setting, TODO,
road or world scene was changed. This is a checked asset candidate, not a blanket READY
claim for the family or district.
