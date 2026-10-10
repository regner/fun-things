# d02_house_family.04 — Compact corner home

10 October 2026. **Source, export, linked prefab and bounded headless checks delivered;
independent review and world/gameplay/device acceptance pending.** Commissioned by
Regner; [commission](commission.md), [family brief](../d02_house_family.md),
[Crescents v02](../../concepts/districts-v1/the-crescents.md). The explicit production
commission covers this formerly optional candidate and supersedes concept-only scope.

Producer: commissioned asset-production worker on `lane/a-house`. Read the preceding
[detached](d02_house_family_01.md), [paired](d02_house_family_02.md) and
[short terrace](d02_house_family_03.md) deliveries. Their domestic detailing, palette
and source/prefab conventions continue here; no sibling, shared tracker/brief,
project setting or saved district placement changed.

## Design and provisional dimensions

A compact two-storey **L-shaped corner home** with two street-facing gables. The long
blue/slate main ridge meets a **perpendicular, shorter and 0.65 m lower plum ridge**.
The sole warm entrance sits within a **3.6 × 3.6 m open corner setback**. Broad paired
windows face both streets, with smaller glazing on the returns. This is a smaller,
tighter footprint than the detached member, not a rotated copy: both wings have
upper-floor windows, the roof axes cross, and the entry belongs to the inside corner.
It also differs from the paired home's parallel ridges and terrace's lateral ridge.

Original Blender construction only; no downloads, brands, image-to-mesh, external
textures or runtime render meshes. Concepts supplied visual direction, not measured
dimensions. Closed windows, door, plinth and facade/roof trim are integral shell parts.
No porch canopy, dormer, chimney, garden wall, planting or ground surface was selected:
those remain separately owned shared/district fixtures. No interior, interactive door,
destruction, animation, rooftop traversal or new gameplay state is introduced. The
warm blind panels are opaque colour accents, not emissive lights.

**All dimensions are provisional authored choices**, not approved parcel allocations.
Godot local X/Y/Z, in metres:

| Region | Bounds / dimensions |
| --- | --- |
| Whole visual | min **(-4.55, 0, -4.55)**; max **(4.55, 7.55, 4.55)**; size **9.1 × 7.55 × 9.1** |
| Main structural footprint | X=-4.2…0.6; Z=-4.2…4.2; **4.8 × 8.4** |
| East wing footprint | X=0.6…4.2; Z=-0.6…4.2; **3.6 × 4.8** |
| Overall footprint | **8.4 × 8.4** bounding rectangle; occupied L area **57.6 m²** |
| Open corner setback | X=0.6…4.2; Z=-4.2…-0.6; **3.6 × 3.6** before shallow decoration |
| Main roof | ridge along Z at X=-1.8, height **7.55**; depth **9.1** |
| Wing roof | ridge along X at Z=1.8, height **6.90**; cross-section depth **5.5** |
| Roof construction | eave top **5.65**; vertical folded-plane thickness **0.20**; exposed overhang **0.35** |
| Collision height | **5.3**; gables and roofs above are visual-only overhead regions |
| Entry | centre X=2.6; facade Z=-0.6; closed leaf **1.30 × 2.38**, no step |
| Principal windows | **2.65 × 1.40**, two panes; return windows **1.45/1.55 × 1.40** |
| Decorative projections | plinth **0.04**; sill **0.20**; door pull **0.225** from facade |

The ground pivot is the centre of the **overall structural bounding footprint**, not
its occupied-area centroid. Root and mesh origins (0,0,0), applied transforms, metre
units and unit scale. Blender +Y front maps to Godot -Z; +Z up maps to +Y. Source/export
envelope tolerance ±0.001 m; axis-mapping tolerance 0.00001 m. Flat ground datum zero.
No sockets were requested or added. The corner setback is an exterior entry space,
not an interior or cut-through; placement must preserve paths outside the L solid.

## Source, export and materials

- Source: `art/source/models/environment/d02_house_family_04/d02_house_family_04.blend`.
- Collection `export_d02_house_family_04`; root `D02HouseFamily04`; one joined editable
  mesh `D02HouseFamily04_Mesh`. The two main wall volumes are Boolean-unioned in Blender
  to remove internal coplanar facade faces. The wing roof is clipped against the main
  roof slope to avoid a shelf projecting through the rear gable. Construction modifiers
  are applied. Closed roof/fitting solids still intentionally overlap the wall shell;
  this is not a single connected boolean interior model.
- Export: `art/models/environment/d02_house_family_04/d02_house_family_04.glb`, with
  pinned-engine `.glb.import` sidecar.
- Prefab: `scenes/prefabs/environment/d02_house_family_04.tscn`.
- Tools: `tools/asset_production/d02_house_family_04/` contains `author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` + UID and `record.py`.

Seven opaque Principled surfaces use the siblings' original sRGB swatches, converted
to linear shader colour. This mesh's imported slot order:

| Slot | Material | sRGB swatch |
| --- | --- | --- |
| 0 | `crescents_warm_render` | `#ACA69E` |
| 1 | `crescents_blue_slate_roof` | `#3E526C` |
| 2 | `crescents_ivory_trim` | `#D4CEBB` |
| 3 | `crescents_muted_plum_roof` | `#68566B` |
| 4 | `crescents_slate_plinth` | `#58636B` |
| 5 | `crescents_petrol_closed_glass` | `#263F4D` |
| 6 | `crescents_warm_entrance` | `#D4A16B` |

All backface-culled, no emission or transparency. PBR values are retained in
[validation.json](d02_house_family_04-evidence/validation.json). No images, UV-dependent
artwork, external material files or import remaps are needed. Opaque glazing avoids
implying interiors and bounds transparent-layer costs.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export loads
`tools/assets/blender/export_settings.json`, filters the named collection and disables
animations/skins. Applied bevels, normals and Boolean results remain editable mesh
geometry. Studio cameras/lights/ground and the hidden one-metre reference stay outside
export. Godot defaults retain generated LODs and shadow meshes. No explicit LOD family
or accepted polygon, draw-call, shadow or target-device budget is claimed.

## Prefab and collision

Identity-transform imported instance at **`Visuals/Model`**, no editable-child overrides,
embedded replacement render geometry or runtime-authored hierarchy. Scene UID
`uid://ci7ti66gkvhcs`, imported model UID `uid://dr5fr05u5ecr2`; node identities and
script UID sidecar retained. The scene stores its UID internally, not in a `.tscn.uid`.

One static-world body **`Collision/Body`**, layer 1 / mask 0, owns two boxes:
`MainHome` size (4.8,5.3,8.4), centre (-1.8,2.65,0), and `EastWing` size (3.6,5.3,4.8),
centre (2.4,2.65,1.8). They meet at the wall return and leave the corner setback open.
Closed windows/entry are blocked. Overhead roofs/gables and shallow plinth/sill/pull
projections do not enlarge collision or create snag points. No walkable decks, steps,
roof routes or rails are authored.

The brief forbids live Blender/Godot editor sessions and windowed operation. Direct
text prefab authoring followed by pinned **headless editor** load/pack/save/reload
normalized UIDs and proved second-save byte stability. No owner's live session was
touched; headless checks do not establish synchronization of any separate open editor.

## Validation and visual evidence

- **10,826 triangles; 5,619 source vertices; 5,687 exported vertices; one mesh / seven
  surfaces.** Export splits some vertices at normal/material boundaries.
- **Zero non-manifold edges, degenerate source faces or exported triangles**; finite
  coordinates, unit source/export normals and positive triangle/normal alignment.
- Raw GLB buffers match source-axis conversion and literal design bounds. Source rays
  verify the recessed entry, both perpendicular ridges, open corner and absence of the
  rejected rear-gable wing-roof shelf.
- Fresh saved-source re-export is **byte-identical**, **207,348 bytes**, SHA-256
  `ef6a28b07cf07ef01d789a05e0ce16660683bdb9244443fe7f568ed0c73c0d98`.
- Pinned headless load validates linked dependencies, bounds, identity, opaque materials,
  registered UIDs and both collision envelopes. **Nine** radius **0.35 m**, height
  **1.8 m** capsule overlap/clearance cases pass. Front ray hits **Z=-4.19999981 m**.
- Production **`ActorMotion.step`**, 60 fixed ticks per case in both `AUTHORITY` and
  `REPLAY`: main facade stops Z=-4.55077457; recessed entry stops Z=-0.95008039;
  east side stops X=4.55077457; inside return stops X=0.95052105; east bypass reaches
  Z=-2.99999356 m. Both modes yield exactly equal final coordinates. Independent
  literal contact expectations use **0.025 m** solver-separation tolerance.
- A **1.9 × 1.5 × 4.3 m test box** sweep blocks at the facade and clears the east
  bypass. This is a physics-envelope check, not production driving/turning acceptance.
- Final full production checks **PASS**, no ignored failures: pinned compilation,
  formatting/lint, **17 Python tests**, **149 GUT tests / 6,768 assertions**, and
  detected expected failing negative control. Fresh asset runtime has no ERROR/WARNING.

[Hero](d02_house_family_04-evidence/hero.png) ·
[side](d02_house_family_04-evidence/side.png) ·
[entry detail](d02_house_family_04-evidence/entrance_detail.png) ·
[47 m / 42° overhead](d02_house_family_04-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles CPU / 32-sample / AgX **1280 × 720** renders. Overhead is
perspective vertical-down at (0,0,47), +Y/north up, **42° vertical FOV**, not a crop,
oblique camera or orthographic substitute. Evidence-only RGB compression retains six
bits per channel (overhead seven), PNG compression 9; all four are below 400 KB.

Self-inspected all four final compressed views. The tight L footprint, perpendicular
unequal ridges and open corner read overhead. Two street-facing window groups and the
warm recessed door read in closer views, not directly above. The initial overlapping
wing roof exposed a plum shelf through the rear gable; clipping the hidden portion
removed it, with an independent regression ray. The main wall top was also fitted to
the roof underside. These are producer observations, not independent art acceptance.

Diagnostics: Blender future-6.0 API deprecation notices; headless toolkit 4.8 compatibility
warning and scan-aborted/RID/ObjectDB shutdown diagnostics during normalization.
Normalization exited 0 with stable saved bytes; fresh runtime passed without those
diagnostics. The exact default-PATH production command failed during engine detection
with a Windows cp1252 decode error. Its first explicit-path retry rejected a nonempty
output directory; the failed folder was preserved in scratch and a fresh-path rerun
passed. A function-length lint warning was resolved by separating motion case data from
execution. No unrelated failure was suppressed. Raw logs/retries are outside Git at
`C:/tmp/ft/assets/d02_house_family_04/`; [final.log](d02_house_family_04-evidence/final.log)
and validation retain concise results and diagnostic classifications.

## Exact reproduction

From this worktree in Git Bash. The full suite requires a fresh empty `checks` directory:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
STYLE="$(mise which gdstyle)"
TOOL=tools/asset_production/d02_house_family_04
TMP=C:/tmp/ft/assets/d02_house_family_04
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

`author.py` reconstructs source/export/renders; `validate.py` opens the saved source and
reexports to scratch. `record.py` collects final receipts and hashes every produced
payload, including source, tools, import/UID metadata, prefab, documentation and lean
evidence, except the self-referential manifest. `record.py --verify` is non-mutating.
Shared export and production-check tools are reused; member-specific recipes follow
sibling conventions without modifying them or adding a general-purpose framework.

## Remaining acceptance

Independent technical/art review remains required. No district placement changed.
Parcel fit, whole-row/sibling silhouette comparison, diverse spacing/setbacks, clear
cut-throughs, native fixed-light gameplay/combat visibility, real vehicle handling,
populated-city collision, separate-process multiplayer/transport/prediction, packaged
dependencies and sustained target-device performance remain downstream gates. The
bounded authority/replay comparison is **not a multiplayer test**. No register-ready,
TODO-completion or placement authorization is implied.
