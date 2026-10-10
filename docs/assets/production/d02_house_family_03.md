# d02_house_family.03 — Short terrace

10 October 2026. **Source, export, linked prefab and bounded headless checks delivered;
independent review and world/gameplay/device acceptance pending.** Commissioned by
Regner; [commission](commission.md), [family brief](../d02_house_family.md),
[Crescents v02](../../concepts/districts-v1/the-crescents.md). The explicit production
commission supersedes the earlier concept-only restriction.

Producer: commissioned asset-production worker on `lane/a-house`. Read the preceding
[detached](d02_house_family_01.md) and [paired](d02_house_family_02.md) deliveries;
their palette, domestic details and source/prefab conventions continue here. Sibling
files, shared queue/progress/briefs, project settings and world placements are unchanged.

## Design and provisional dimensions

Three attached narrow two-storey homes. A single long **cross-frontage ridge** covers
the western two homes; the eastern end is **1.2 m shallower** with a **0.35 m lower**
ridge. This creates a broad short row with a stepped end rather than the paired
sibling's two front-facing gables or the detached sibling's hip and low side wing.
Three warm grade-level doors, broad two-pane windows, ivory courses and blue/slate
and muted-plum roof planes retain the quiet domestic family. Two warm blind panels
are opaque colour accents, not lights. No fine tile noise or roof clutter is added.

Original Blender construction only: no downloaded geometry, brands, image-to-mesh,
external textures or runtime render meshes. Concepts supplied direction, not measured
geometry. Doors, closed windows and trim are integral shell elements. No porch canopy,
chimney, dormer, garden wall, ground surface or planting was selected: those remain
separately owned fixtures, not duplicated here. No interior, interactive door,
destruction, animation, rooftop traversal or new gameplay state is introduced.

**All dimensions are provisional authored choices**, not approved parcel allocations.
Godot local X/Y/Z, in metres:

| Region | Bounds / dimensions |
| --- | --- |
| Whole visual | min **(-8.15, 0, -4.4)**; max **(8.15, 7.30, 4.4)**; size **16.3 × 7.3 × 8.8** |
| Main row structural footprint | X=-7.8…2.6; Z=-4…4; two 5.2 m homes, combined 10.4 × 8 |
| East end structural footprint | X=2.6…7.8; Z=-2.8…4; one 5.2 × 6.8 home |
| Combined structural footprint | 15.6 × 8 bounding rectangle; occupied area **118.56 m²** |
| Collision height | 5.3; upper wall/gable and roof regions are overhead visuals |
| Main roof | X=-8.15…2.6; Z=-4.4…4.4; ridge along X at Z=0, height 7.30 |
| End roof | X=2.6…8.15; Z=-3.2…4.4; ridge along X at Z=0.6, height 6.95 |
| Roof eave / construction | top 5.55; underside 5.35; folded plane vertical thickness 0.20 |
| Overhang | 0.35 at external gable ends, 0.40 front/rear; no route between attached homes |
| Entries | X=-6.45 / -1.25 at facade Z=-4; X=3.95 at Z=-2.8; leaves 1.20 × 2.38, no steps |
| Principal front windows | 1.80 × 1.40; upper-entry windows 1.25 × 1.40 |
| Decorative projections | plinth 0.04; sill 0.20; door pull 0.225 from wall |

The ground pivot is the centre of the **overall structural bounding footprint**, not
its occupied-area centroid. Root and mesh origin (0,0,0), metre units, unit scale and
applied transforms. Blender +Y facade/front maps to Godot -Z; Blender +Z maps to +Y.
Envelope tolerance ±0.001 m; source/export axis-mapping tolerance 0.00001 m. Flat ground
datum zero. No sockets were requested or added. The end setback is not a cut-through;
placement must preserve pedestrian paths outside the occupied footprint.

## Source, export and materials

- Source: `art/source/models/environment/d02_house_family_03/d02_house_family_03.blend`.
- Collection `export_d02_house_family_03`; root `D02HouseFamily03`; one joined editable
  mesh `D02HouseFamily03_Mesh`. Each building volume has continuous gabled-end faces.
  Closed constituent solids intentionally overlap at fitting junctions; this is not
  a boolean-unioned connected volume or an interior shell.
- Export: `art/models/environment/d02_house_family_03/d02_house_family_03.glb`, plus
  the pinned-engine `.glb.import` sidecar.
- Prefab: `scenes/prefabs/environment/d02_house_family_03.tscn`.
- Tools: `tools/asset_production/d02_house_family_03/` contains `author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` + UID and `record.py`.

Seven opaque Principled surfaces, matching the siblings' original sRGB swatches
(converted to linear shader colour). This mesh's slot order is:

| Slot | Material | sRGB swatch |
| --- | --- | --- |
| 0 | `crescents_warm_render` | `#ACA69E` |
| 1 | `crescents_blue_slate_roof` | `#3E526C` |
| 2 | `crescents_ivory_trim` | `#D4CEBB` |
| 3 | `crescents_slate_plinth` | `#58636B` |
| 4 | `crescents_muted_plum_roof` | `#68566B` |
| 5 | `crescents_petrol_closed_glass` | `#263F4D` |
| 6 | `crescents_warm_entrance` | `#D4A16B` |

All backface-culled, no emission or transparency; PBR values are retained in
[validation.json](d02_house_family_03-evidence/validation.json). No images, UV-dependent
artwork, external materials or import remaps are needed. Opaque glazing does not imply
an interior and avoids transparent-layer costs.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export loads
`tools/assets/blender/export_settings.json`, filters the named collection and disables
animations/skins. Applied bevels and weighted normals remain editable mesh data; no
unresolved modifiers. Studio cameras/lights/ground and hidden one-metre reference stay
outside export. Godot defaults keep generated LODs and shadow meshes enabled. No
explicit LOD family or accepted polygon, draw-call, shadow or device budget is claimed.

## Prefab and collision

Identity-transform imported scene at **`Visuals/Model`**, no editable-child overrides,
embedded replacement render geometry or runtime hierarchy construction. Saved scene
UID `uid://db4c5155yvphf`, imported model UID `uid://c5rksholr3uhx`; node identities
and script UID sidecar retained. The scene carries its UID internally, not in a
separate `.tscn.uid` file.

One static-world body **`Collision/Body`**, layer 1 / mask 0, with two boxes:
`MainRow` size (10.4,5.3,8), centre (-2.6,2.65,0), and `EastEnd` size (5.2,5.3,6.8),
centre (5.2,2.65,0.6). This minimal compound blocks all three closed homes and preserves
the end setback. Roofs/upper gables and shallow plinth/sill/pull projections do not
enlarge the gameplay solid or produce snag colliders. No walkable deck, stairs,
roof route or rail is authored.

The explicit brief forbids live Blender/Godot editor sessions. Text prefab authoring
followed by pinned **headless editor** load/pack/save/reload normalized UIDs and proved
second-save byte stability. No owner's live session was touched; these checks do not
establish synchronization of any separate open editor.

## Validation and visual evidence

- **16,820 triangles; 8,732 source and exported vertices; one mesh / seven surfaces.**
- **Zero non-manifold edges, zero degenerate source faces or exported triangles**;
  finite coordinates, unit source/export normals and positive triangle/normal alignment.
- Raw GLB buffer bounds match source-axis conversion and independent literal bounds.
  Source rays verify all three door panels, long shared ridge, lower end ridge and
  clear front setback. These are geometric checks, not inferred render measurements.
- Fresh saved-source re-export is **byte-identical**: **314,608 bytes**, SHA-256
  `56234a04b73c2accbd8ccbed2ecab64c962c424eba56941bfd0a10dcbd1229f2`.
- Pinned Godot load checks linked dependencies, identity, opaque materials, bounds,
  registered UIDs and both collider envelopes. **Nine** radius **0.35 m**, height
  **1.8 m** capsule overlap/clearance cases pass. Front aim ray hits Z=-4.0 m.
- Production **`ActorMotion.step`**, 60 fixed ticks per case in both `AUTHORITY` and
  `REPLAY`: west closed facade stops Z=-4.35025358; recessed end stops Z=-3.16666198;
  east side stops X=8.16667366; clear east bypass reaches Z=-2.99999356 m. Both modes
  return exactly equal coordinates. Independent literal contact expectations use
  **0.025 m** solver-separation tolerance, not copied movement formulas.
- A **1.9 × 1.5 × 4.3 m test box** sweep blocks at the facade and clears the east
  bypass. This checks a physics envelope, not production vehicle turning/handling.
- Final full production checks **PASS**, no ignored failures: pinned compilation and
  formatting/lint, **17 Python tests**, **149 GUT tests / 6,768 assertions**, and
  detected expected failing negative control. Fresh asset runtime has no ERROR/WARNING.

[Hero](d02_house_family_03-evidence/hero.png) ·
[side](d02_house_family_03-evidence/side.png) ·
[entrances detail](d02_house_family_03-evidence/entrance_detail.png) ·
[47 m / 42° overhead](d02_house_family_03-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles CPU / 32-sample / AgX **1280 × 720** renders. The overhead
is perspective, vertical down at (0,0,47), +Y/north up, **42° vertical FOV**, not a
crop or orthographic substitute. Evidence-only RGB compression retains six bits per
channel (overhead seven), PNG compression 9; all four are below 400 KB.

Self-inspected all four final compressed images. The broad lateral ridge, shorter
lower end and setback read overhead; three domestic entries read in oblique/detail
views, not directly above. The silhouette differs from the preceding hip/side-wing
and twin front-gable houses rather than only changing paint. Initial front floor
courses crossed party-wall piers; splitting the courses removed those intersections.
End courses were extended to their proper corners. These are producer observations,
not independent art acceptance or a whole-row placement review.

Diagnostics: Blender future-6.0 API deprecation notices; headless toolkit 4.8
compatibility warning and scan-aborted/RID/ObjectDB shutdown diagnostics during
normalization. Normalization exited 0 with stable bytes; fresh runtime passed without
those diagnostics. The exact default-PATH production command failed during engine
version detection with a Windows cp1252 decode error. A rerun using explicit
`mise which` executable paths passed all layers; no unrelated failure was suppressed.
Raw scratch logs are outside Git in `C:/tmp/ft/assets/d02_house_family_03/`;
[final.log](d02_house_family_03-evidence/final.log) retains concise final results and
classified normalization diagnostics.

## Exact reproduction

From this worktree in Git Bash; use a fresh empty `checks` output directory:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
STYLE="$(mise which gdstyle)"
TOOL=tools/asset_production/d02_house_family_03
TMP=C:/tmp/ft/assets/d02_house_family_03
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

`author.py` reconstructs source/export/renders. `validate.py` opens the saved source
and reexports to scratch. `record.py` records receipts and SHA-256 of every produced
payload (tools, source, imports/UIDs, prefab, doc and lean evidence), except the
self-referential manifest. `record.py --verify` is non-mutating. Shared pinned export
and production-check tooling are reused; member-specific recipes/checks follow sibling
conventions without modifying them or introducing a general-purpose framework.

## Remaining acceptance

Independent technical/art review remains required. No saved district placement changed.
Parcel fit, whole-row/sibling silhouette review, diverse spacing/setbacks, unobstructed
cut-throughs, native fixed-light gameplay/combat visibility, actual vehicle handling,
populated-city collision, separate-process multiplayer/transport/prediction, packaged
dependencies and sustained target-device performance remain downstream gates. The
bounded authority/replay comparison is **not a multiplayer test**. No register-ready,
TODO-completion or placement authorization is implied.
