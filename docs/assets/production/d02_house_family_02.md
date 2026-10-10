# d02_house_family.02 — Paired house

10 October 2026. **Source, export, linked prefab and bounded headless checks delivered;
independent review and world/gameplay/device acceptance pending.** Commissioned by
Regner; [commission](commission.md), [family brief](../d02_house_family.md),
[Crescents v02](../../concepts/districts-v1/the-crescents.md). The explicit production
commission supersedes the historical concept-only restriction.

Producer: commissioned asset-production worker on `lane/a-house`. The preceding
[detached house](d02_house_family_01.md) supplied the family palette and domestic detail
language. Its files, shared queue/progress/briefs and world placements are unchanged.

## Design and provisional dimensions

Two attached two-storey homes, each with its own full-depth gabled roof and closed
warm entrance. The western home projects **1.2 m** beyond the eastern frontage;
its ridge is **0.30 m** higher. Long paired ridges, a central valley and stepped
front edge distinguish this from the detached sibling's compact hip and low side
wing even without colour. Slate blue and muted plum planes, ivory bargeboards,
warm-grey render, broad two-pane windows and two restrained warm blind panels
keep the family consistent. Roofs remain quiet and free of fine tile noise.

Original Blender construction only: no downloaded geometry, brands, image-to-mesh,
external textures or runtime render meshes. Concepts were inspected for direction,
not measured for dimensions. Normal closed windows, doors and architectural trim
are integral shell parts. No porch canopy, chimney, dormer, garden wall, ground
surface or planting was selected; those remain separate shared/district fixtures.
No interior, interaction, destruction, animation or rooftop traversal is introduced.

**All dimensions below are provisional authored choices**, not approved parcel
allocations. Width/height/depth use Godot local X/Y/Z, in metres:

| Region | Bounds / dimensions |
| --- | --- |
| Whole visual | min **(-6.8, 0, -5.2)**; max **(6.8, 7.95, 5.2)**; size **13.6 × 7.95 × 10.4** |
| West structural footprint | X=-6.4…0; Z=-4.8…4.8; 6.4 × 9.6 |
| East structural footprint | X=0…6.4; Z=-3.6…4.8; 6.4 × 8.4 |
| Combined footprint | 12.8 × 9.6 bounding rectangle, occupied area **115.2 m²** |
| Solid collision height | 5.6 on both homes; upper gables/roofs are overhead visual regions |
| West roof | X=-6.8…0; Z=-5.2…5.2; ridge X=-3.2, height 7.95 |
| East roof | X=0…6.8; Z=-4.0…5.2; ridge X=3.2, height 7.65 |
| Roof eave / construction | top 5.85; underside 5.65; folded plane vertical thickness 0.20 |
| Overhang | 0.40 at exposed sides and ends; roofs meet at X=0, not across a route |
| Doors | centres X=-1.55 / +1.55; facade Z=-4.8 / -3.6; leaves 1.30 × 2.38, no step |
| Principal windows | 2.20 × 1.40/1.42; narrower upper-entry windows 1.40 × 1.42 |
| Decorative projections | plinth 0.04; sill 0.20; door pull 0.225 from wall |

Ground pivot is the centre of the overall **structural bounding footprint**, not
its occupied-area centroid. Root and mesh origins (0,0,0), applied transforms,
unit scale and metre units. Blender +Y front maps to Godot -Z, +Z up maps to +Y.
Source/export envelope tolerance ±0.001 m, axis-mapping tolerance 0.00001 m.
No sockets were requested or added. The stepped frontage is not a through passage;
placement must preserve cut-throughs outside the occupied footprint.

## Source, export and materials

- Source: `art/source/models/environment/d02_house_family_02/d02_house_family_02.blend`.
- Collection `export_d02_house_family_02`; root `D02HouseFamily02`; one joined editable
  mesh `D02HouseFamily02_Mesh`. Closed component solids intentionally overlap at
  fitting junctions; this is not a boolean-unioned interior shell. Each home's
  full-height gabled wall is one continuous solid, avoiding coplanar facade seams.
- Export: `art/models/environment/d02_house_family_02/d02_house_family_02.glb` and
  its pinned-engine `.glb.import` sidecar.
- Prefab: `scenes/prefabs/environment/d02_house_family_02.tscn`.
- Tools: `tools/asset_production/d02_house_family_02/` contains `author.py`,
  `export.py`, `validate.py`, `check_prefab.gd` + UID, and `record.py`.

Seven opaque Principled surfaces, no images, external material remaps, emission or
transparent interiors. The sibling's original sRGB swatches are converted to linear
shader colour; names and values match the family, while slot order follows this mesh:

| Slot | Material | sRGB swatch |
| --- | --- | --- |
| 0 | `crescents_warm_render` | `#ACA69E` |
| 1 | `crescents_blue_slate_roof` | `#3E526C` |
| 2 | `crescents_ivory_trim` | `#D4CEBB` |
| 3 | `crescents_muted_plum_roof` | `#68566B` |
| 4 | `crescents_slate_plinth` | `#58636B` |
| 5 | `crescents_petrol_closed_glass` | `#263F4D` |
| 6 | `crescents_warm_entrance` | `#D4A16B` |

Full PBR values appear in [validation.json](d02_house_family_02-evidence/validation.json).
All materials are backface-culled. No UV-dependent artwork or `.tres` is required.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export loads the
shared `tools/assets/blender/export_settings.json`, filters the named collection,
and disables animation/skins. Applied bevels and weighted normals remain editable
mesh data. Studio cameras/lights/ground and the hidden one-metre reference never
export. Default Godot import enables generated LODs/shadow meshes. No explicit LOD
family or accepted polygon, draw-call, shadow or target-device budget is claimed.

## Prefab and collision

The linked GLB is at **`Visuals/Model`**, identity transform, without overrides,
embedded replacement geometry or runtime-authored hierarchy. Engine-normalized scene
UID `uid://d1a7coqdekmp`, model UID `uid://c0c3mf8kmr1y6`; node identities and script
UID sidecar are retained. The scene stores its UID internally, not in a `.tscn.uid`.

One static-world body **`Collision/Body`**, layer 1 / mask 0, owns two boxes:
`WestHome` size (6.4,5.6,9.6), centre (-3.2,2.8,0), and `EastHome` size (6.4,5.6,8.4),
centre (3.2,2.8,0.6). They meet at the party wall and preserve the east entry setback.
Doors/windows are closed and blocked by these volumes. Overhead roofs/gables and
shallow decorative plinth/sill/pull projections do not enlarge gameplay collision
or create snag points. No walkable deck, stair, roof route or rail is authored.

Text authoring followed by pinned **headless editor** load/pack/save/reload normalized
UIDs and proved second-save byte stability. The brief forbids live editor sessions;
none were touched. A headless check does not establish synchronization of an open editor.

## Validation and visual evidence

- **12,848 triangles; 6,668 source and exported vertices; one mesh / seven surfaces.**
- **Zero non-manifold edges, zero degenerate source faces or exported triangles**;
  finite source coordinates, unit source/export normals and positive triangle/normal alignment.
- Raw GLB buffer bounds match source-axis conversion and literal design dimensions.
  Source rays confirm two different door planes, clear setback and continuous gable faces.
- Fresh saved-source re-export is **byte-identical**: **241,212 bytes**, SHA-256
  `a61de5dce12ffe74045d656dd4dbf623138bea5f07cdc9ac69174e929bb724d6`.
- Pinned Godot load checks dependencies, linked identity, bounds, materials, registered
  UIDs and both collision envelopes. Eight radius **0.35 m**, height **1.8 m** capsule
  overlap/clearance cases pass. Front ray hits Z=-4.80000019 m.
- Production **`ActorMotion.step`**, 60 fixed ticks per case in both `AUTHORITY` and
  `REPLAY`: west facade stop Z=-5.16666126; recessed east stop Z=-3.95051527; east side
  stop X=6.75000143; clear east bypass ends Z=-2.99999356 m. Both modes return exactly
  equal coordinates. Independent literal contact positions use a documented **0.025 m**
  solver-separation tolerance, not copied motion formulas.
- **1.9 × 1.5 × 4.3 m test box** sweep blocks at the facade and clears the east bypass.
  This is a physics-envelope observation, not production vehicle turning/handling.
- Final full production checks **PASS**, no ignored failures: pinned script compilation
  and formatting/lint, **17 Python tests**, **149 GUT tests / 6,768 assertions** and
  detected expected failing negative control. Fresh asset runtime has no ERROR/WARNING.

[Hero](d02_house_family_02-evidence/hero.png) ·
[side](d02_house_family_02-evidence/side.png) ·
[entrances detail](d02_house_family_02-evidence/entrance_detail.png) ·
[47 m / 42° overhead](d02_house_family_02-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles CPU / 32-sample / AgX **1280 × 720** renders. Overhead is
perspective vertical-down at (0,0,47), +Y/north up, **42° vertical FOV**, not a crop or
orthographic substitute. Evidence-only RGB compression retains six channel bits
(overhead seven), PNG compression 9; each image is below 400 KB.

Self-inspected all four final views: long twin ridges and unequal front edges read
from overhead; domestic doors/windows intentionally read in oblique/detail views,
not directly above. Compared to the detached sibling's hero, the roof and footprint
are different rather than a recolour. Initial overlapping body/gable faces produced
a dark facade seam; continuous full-height gable solids removed it. The setback plinth
now returns around the west corner. Rejected renders remain in scratch, not Git.
These are producer observations, not independent art acceptance.

Diagnostics: Blender future-6.0 API deprecation notices; pinned editor toolkit 4.8
compatibility warning, plus scan-aborted/RID/ObjectDB shutdown diagnostics on
normalization. Normalization exited 0 and saved stable bytes; fresh runtime passed
without those diagnostics. Initial formatter check required formatting (applied).
The exact default-PATH production command failed during engine-version detection
with a Windows cp1252 decoding error; rerunning with explicit `mise which` executables
passed all layers. No unrelated errors were suppressed. Raw logs are outside Git
at `C:/tmp/ft/assets/d02_house_family_02/`; [final.log](d02_house_family_02-evidence/final.log)
and validation retain concise final results and diagnostic classifications.

## Exact reproduction

From this worktree in Git Bash; use a fresh empty `checks` directory for the full suite:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
STYLE="$(mise which gdstyle)"
TOOL=tools/asset_production/d02_house_family_02
TMP=C:/tmp/ft/assets/d02_house_family_02
mkdir -p "$TMP"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOL/author.py"
python "$TOOL/record.py" --compress-renders
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOL/validate.py"
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . --script "$TOOL/check_prefab.gd" -- --normalize > "$TMP/normalize.log" 2>&1
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . --script "$TOOL/check_prefab.gd" > "$TMP/prefab-final.log" 2>&1
timeout 180 "$STYLE" "$TOOL/check_prefab.gd"
timeout 180 "$STYLE" fmt --check "$TOOL/check_prefab.gd"
timeout 1800 python tools/production_checks.py --godot "$GODOT" --gdstyle "$STYLE" --output "$TMP/checks"
python "$TOOL/record.py"
python "$TOOL/record.py" --verify
```

`author.py` reconstructs source/export/renders; `validate.py` separately opens the
saved source and reexports to scratch. `record.py` hashes every produced payload,
including source, tools, imports/UIDs, prefab, doc and lean evidence, except its
self-referential manifest. `record.py --verify` is non-mutating. Shared export and
production-check tooling are reused; member-specific construction and checks follow
the sibling conventions without changing it or adding a general-purpose framework.

## Remaining acceptance

Independent technical/art review remains required. No saved district placement changed.
Parcel fit, whole-row/sibling silhouette review, varied placement spacing/setbacks,
unobstructed cut-throughs, native fixed-light gameplay/combat/actor visibility, real
vehicle handling, populated-city collision, separate-process multiplayer/transport,
packaged dependencies and sustained target-device performance remain downstream gates.
Authority/replay equivalence here is **not a multiplayer test**. No register-ready,
TODO-completion or placement authorization is implied.
