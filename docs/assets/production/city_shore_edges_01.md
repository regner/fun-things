# city_shore_edges.01 — Low seawall

10 October 2026. **Source/export, linked prefab and bounded physics checks delivered;
independent review and world/gameplay acceptance pending.** Original Blender construction
by the commissioned implementation specialist. Production follows the [commission](commission.md),
[shore-edge brief](../city_shore_edges.md), approved [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street context](../../concepts/world-v1/stage-04-streets/README.md). The explicit
production task supersedes the historical concept-only restriction. No downloaded
geometry, generated-image meshes, real brands or external artwork were used.

## Design and provisional dimensions

A straight, low mineral wall: broad battered slate body, darker recessed plinth,
slender mortar bed and pale chamfered coping. One shallow central coping joint gives
sparse construction rhythm without noisy masonry, grime, railings or dock furniture.
The pale top remains a clear boundary strip in the inspected gameplay-camera render;
the joint is intentionally subordinate. This is the first shore-family delivery.

Dimensions are **provisional authored values**, permitted by the production brief's
standing rules, not measurements inferred from concept images or approved coast fit.
No coastline, water polygon, terrain elevation or water-entry rule was changed.

| Contract | Godot local metres |
| --- | --- |
| Root/pivot | (0, 0, 0), centred on the land-contact footprint |
| Whole AABB | min (-2, 0, -.36), max (2, 1, .36) |
| Whole X/Y/Z size | 4.000 × 1.000 × .720 |
| Plinth ground footprint | 4.000 × .640; Y=0 |
| Plinth/body/mortar/coping levels | 0–.16 / .16–.79 / .79–.82 / .82–1.00 |
| Coping | .720 wide, .180 high; upper edge chamfers .025 |
| Coping centre joint | X=0; .016 wide, .008 deep, closed profiled groove |
| End joins | X=-2 and X=+2, identical square planar sections |
| Repeated straight | Translate 4.000 along X, no scale or corrective rotation |
| Intended water-facing side | -Z (Blender +Y); the cross-section is symmetric |
| Static collider | 4 × 1 × .72 box centred (0, .5, 0) |

Envelope/datum tolerance is ±.001 m. Blender +Z maps to Godot +Y; Blender +Y
maps to Godot -Z. Both root and mesh have identity transforms, metre units and
applied geometry; there are no socket markers or runtime attachment APIs.

### Handoff to the remaining shore-family assets

`.02` owns the heavier quay, `.03` rocks and `.04` the compatible corner/end
connector set. This asset supplies **only a straight low wall**; do not duplicate
corner or finished terminal families here. Normal visible coping/plinth stay with
this wall. `.04` can use the following ordered Blender (Y,Z) cross-sections at
both X ends; negate Y to obtain Godot Z. The source's `PROFILES` records the same
contract parametrically, and validation proves both end vertex profiles match.

- Plinth: `(-.32,0), (-.32,.13), (-.30,.16), (.30,.16), (.32,.13), (.32,0)`.
- Body: `(-.30,.16), (-.25,.77), (-.24,.79), (.24,.79), (.25,.77), (.30,.16)`.
- Mortar bed: `(-.255,.79), (-.255,.82), (.255,.82), (.255,.79)`.
- Coping: `(-.32,.82), (-.36,.855), (-.36,.975), (-.335,1), (.335,1),
  (.36,.975), (.36,.855), (.32,.82)`.

End planes deliberately have no longitudinal bevel: exact 4 m butt placement
avoids daylight cracks. Adjacent collinear pieces share planar end faces, not
exposed overlapping strips. Curves, corners, material/height transitions and
finished ends require `.04`; arbitrary rotations of the straight do not prove
polygon fit. World integration must keep the saved coast unchanged and establish
land/water elevation against it. This low wall has **no below-datum retaining face**
and does not define a tide level or replace boardwalk decks/supports or quay furniture.

## Source, export and materials

- Source: `art/source/models/environment/city_shore_edges_01/city_shore_edges_01.blend`.
- Collection: `export_city_shore_edges_01`; root `CityShoreEdges01`, child
  `CityShoreEdges01_Mesh`. Four closed solid component islands joined into one mesh.
- Explicit export: `art/models/environment/city_shore_edges_01/city_shore_edges_01.glb`
  with retained `.glb.import` identity/settings.
- Linked wrapper: `scenes/prefabs/environment/city_shore_edges_01.tscn`.
- Author/export/validate/render/check/manifest tools:
  `tools/asset_production/city_shore_edges_01/`.

Four opaque Principled surfaces, all metallic 0, back-face culled, no emission:

| Slot | Material | Linear RGB | Roughness |
| --- | --- | --- | --- |
| 0 | `shore_body_slate` | .20, .265, .29 | .72 |
| 1 | `shore_foot_dark_slate` | .095, .145, .16 | .78 |
| 2 | `shore_joint_recess` | .045, .075, .085 | .82 |
| 3 | `shore_coping_pale_slate` | .46, .52, .53 | .62 |

No textures, embedded images, material overrides, rig, animations, destruction,
water simulation, light nodes or interiors. Narrow geometric chamfers and flat
mineral panels are deliberate; no normal/texture dependencies. Blender **5.2.2 LTS**,
build `d13f752e3b9c`, glTF exporter **5.2.40**. Export uses the shared
`tools/assets/blender/export_settings.json`, the named collection only, Y-up,
no skins or animations. Studio geometry is outside the saved source and export.
Default Godot auto-LOD/shadow mesh generation is retained; transitions and
repeat-placement cost remain unmeasured.

## Prefab, collision and bounded engine checks

`Visuals/Model` is an identity-transform instance of the imported GLB. Collision is
separate at `Collision/Body/Wall`: one static box, world layer 1, mask 0. Its full
coping-width envelope intentionally ignores the battered sides and narrow trim:
at most .12 m conservative side padding near the narrowest body section, avoiding
small snagging ledges. It is a visible solid barrier, not visual-only shore dressing.
No walkable deck, invisible coast barrier, navigation or water-entry mechanic is added.

Pinned Godot **4.8.dev7.official.c971f93e7** headlessly imported the GLB, loaded/packed/
saved/reloaded the wrapper and two-wall fixture twice, with byte-stable saved scene
UIDs/node identities. Dependency checks resolve every linked path/serialized UID;
imported dimensions/materials and identity ancestry match. No live Blender/Godot
session was accessed. Text authoring plus isolated headless normalization is the
required fallback; this does not synchronize or validate a separate open editor.

The saved `physics_check.tscn` contains two wrappers at X=0 and X=4, a test-only
collision floor and a production `ActorMotion` body with radius .35 m, height 1.8 m.
No visible test geometry is generated. `check.gd` exercises:

- 12 physics rays across the body, either side of the join and exactly at X=2,
  at Y=.2/.9/1.1: low rays block at Z=-.36, above-wall rays remain clear.
- Eight 60-tick production movement cases: front, clear end bypass, rear and
  joined-end contact, in both AUTHORITY and REPLAY modes.
- Front/rear stops at Z=∓.710937142; join stop Z=-.709635079;
  bypass reaches Z=2.999999762 at X=-2.5.
- Mode results agree within **.001 m**, with measured maximum difference
  **.000129433 m** in vertical floor settling. Exact bitwise equality is not claimed.
- A second standalone headless process repeats the same recorded outcomes.

An initial overly strict `Vector3.is_equal_approx` comparison rejected that sub-mm
floor-settling difference; the final test uses the explicit 1 mm measurement tolerance
and records the actual error rather than hiding it. This is bounded movement/query
coverage, **not multiplayer transport/admission/prediction or vehicle-driving acceptance**.

## Evidence and validation

[Hero](city_shore_edges_01-evidence/hero.png) ·
[Side](city_shore_edges_01-evidence/side.png) ·
[Detail](city_shore_edges_01-evidence/detail.png) ·
[47 m / 42° overhead](city_shore_edges_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles/AgX renders, **1280×720**, not engine captures.
Overhead is vertical-down perspective, 47 m above the ground datum, vertical FOV 42°,
Blender +Y at image top. The brief's later 720-high cleanliness limit supersedes its
older 800-high reference. All four were inspected; the initial end-face overlap
artifacts were removed by aligning the closed component height intervals. Final
end faces and coping joint are clean; overhead reads a quiet pale boundary strip.
PNG compression 95 at render, then RGB seven-significant-bit encoding/compression 9
keeps each image below 400 KiB without palette quantization bands.

[validation.json](city_shore_edges_01-evidence/validation.json) records:

- **128 triangles, 72 source vertices, 240 exported split vertices**.
- **One mesh, four surfaces**, zero degenerate source faces/export triangles,
  zero non-manifold source edges, consistent winding and unit-length normals.
- Actual binary GLB positions/indices/normals checked, not only accessor metadata.
- 4 × 1 × .72 m bounds, ground-centred identity pivot and matching end profiles.
- Separate fresh export byte-identical to the **9,600-byte GLB**.
- Owned GDScript formatting/lint and explicit compilation pass with no warnings.
- Canonical production command **exited 1**, solely because its global **120 s
  compilation deadline** expired at the last eight unrelated scripts. The asset
  check compiled successfully. Repository formatting/style passed; **14 Python
  tests**, **137/137 GUT tests / 6,523 assertions**, pin/import and negative control passed.
- All eight timed-out scripts subsequently compiled individually in the same isolated
  mirror, each with a bounded 180 s command, exit 0 and no diagnostics. This supplements
  but does **not relabel** the failed canonical run as a pass. Shared tooling was not edited.

[manifest.json](city_shore_edges_01-evidence/manifest.json) lists SHA-256 and byte
counts for every delivered payload except itself. [final.log](city_shore_edges_01-evidence/final.log)
is the one concise retained receipt. Raw logs/retries/scratch exports remain under
`C:/tmp/ft/assets/city_shore_edges_01/`, never in the production payload.

Diagnostics: Blender emits pinned `Material.use_nodes` deprecation notices; actual
source/export/render/validation calls exit normally. Godot headless editor emits the
addon's version warning and shutdown RID/ObjectDB leak diagnostics after successful
normalization. Final standalone checks have no script/error/warning diagnostics.
The canonical suite deadline is an environment/tool-budget limitation, not a waived
script failure. Independent review remains required.

## Reproduction

Run from repository root in Bash; use only the isolated pins, never live sessions.
Pillow is needed for the manifest's lossless PNG recompression after seven-bit RGB
encoding. No general shared mesh-authoring helper exists; the asset recipe is local,
while export settings and production checks reuse the shared tooling.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_shore_edges_01
S=C:/tmp/ft/assets/city_shore_edges_01
mkdir -p "$S"
for step in author export render; do
  timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
    --python-exit-code 1 --python "$T/$step.py" || exit $?
done
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/export.py" -- "$S/reexport.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" -- "$S/reexport.glb"
timeout 300 "$G" --headless --editor --path . --import
timeout 180 "$G" --headless --editor --path . --script "$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "$T/check.gd"
timeout 180 "$G" --headless --path . --script "$T/check.gd"
timeout 60 "$(mise which gdstyle)" --max-warnings 0 "$T/check.gd"
# Use a fresh output directory on subsequent runs; retain any failure status.
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks-reproduction"
python "$T/manifest.py" "$S/checks-reproduction"
```

To reproduce a deadline-limited compilation independently, run each reported script
using `timeout 180 "$G" --headless --path "$S/checks-reproduction/script-checks/compiler-project"
--check-only --script "res://<reported-path>"`. The eight original paths and final
outcomes are retained in `final.log`; the original canonical result stays failed.

## Remaining acceptance

Independent art/technical reviewer disposition, actual engine blue-hour/camera views,
whole-coast fitting and transition/corner checks with `.04`, boardwalk/quay alignment,
water/land level, actor route clearance, vehicle contact/driving, real-process
multiplayer, packaged builds, LOD transitions and sustained GPU/Deck/repetition
profiling remain pending. Do not treat this component as approved world placement
or a water-entry system. No shared brief, queue, progress, road data, world scene,
other asset, gameplay rule or project setting was changed.
