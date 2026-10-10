# d06_shopfront_blocks.02 — Deep rear-court shell

**Production asset candidate delivered; independent review and world placement pending.**
Producer: commissioned implementation worker on `lane/a-sfront`, 10 October 2026.
Authority: current per-record commission and [production commission](commission.md), superseding
historical concept-only restrictions. Family: [Signal Row shopping blocks](../d06_shopfront_blocks.md).
This is a distinct rear-court building, not another ordinary shared shop or a replacement for the
continuous southern shopping parade. No district scene, road, saved placement identity or register
was changed.

## Design and provisional dimensions

A single U-shaped exterior shell has a shallow three-shop frontage and two unequal rear wings.
The western wing reaches further; the eastern wing stops **3.20 m earlier** and its roof steps down
**0.45 m**. The empty rear court and east-side opening carry the silhouette, rather than repainting
an ordinary box. Broad quiet blue roofs, muted-plum walls, warm structural trim and a slate plinth
retain the palette of the earlier [short-row reference](d06_shopfront_blocks_01.md). Blank fascia
carriers remain the existing shared fittings; selective tenant colour/copy can use the separately
delivered [commercial artwork](d06_commercial_graphics_02.md), but this shell does not choose tenants
or duplicate that artwork/hardware.

References inspected: [district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[Signal Row v03](../../concepts/districts-v1/signal-row.md) and its
[shared contract](../../concepts/districts-v1/brief-contract.md). These define character and map-fit
constraints, not measurements from illustration pixels. All new dimensions below are **provisional
producer-authored values** under the standing dimensional rule. Actual district fit remains untested.

Godot coordinates, metres: +X right/east, +Y up, front -Z. Blender +Y maps to Godot -Z.
The root is ground-centred on the **19.2 × 18 m structural bounding rectangle**, not the U's centroid.
Ground is Y=0; source root and mesh transforms are identity. An excluded 1 m reference is saved in
Blender; it is not exported.

| Structural mass | X interval, m | Z interval, m | Roof-deck Y, m | Upper coping Y, m |
| --- | --- | --- | --- | --- |
| Front bar | -9.6 to 9.6 | -9 to -2.6 | 4.30 | 5.05 front / 4.70 rear |
| Deep west wing | -9.6 to -3.2 | -2.6 to 9 | 4.30 | 4.70 |
| Short east wing | 3.2 to 9.6 | -2.6 to 5.8 | 3.85 | 4.25 |

- Shell visual AABB: **(-9.68,0,-9.12) → (9.68,5.05,9.08) m**;
  width/height/depth **19.36 × 5.05 × 18.20 m**.
- Fitted visual AABB: **(-9.68,0,-10.10) → (9.68,5.05,9.08) m**;
  width/height/depth **19.36 × 5.05 × 19.18 m**. Measurement tolerance ±0.002 m;
  source/export envelope tolerance ±0.001 m, coordinate mapping ±0.00001 m.
- Front bays have a 6.4 m pitch. Three existing canopy installations project 1.10 m;
  reserve their inherited **1.20 m installation depth** (front installation limit Z=-10.20).
- Court structural width **6.40 m**; ground-level visual plinth clearance **6.33 m**;
  overhead coping clearance **6.24 m**. Both wings bound the first **8.40 m** of court depth.
  The west wing continues another **3.20 m**, leaving the east side open beyond Z=5.8.
- The court is closed at the front bar, **not a tunnel through the storefronts**. Its rear and
  offset east opening require adjoining open ground in a placed district. The model includes
  no paving, sidewalk, road surface, floor collider, stairs, interior or rooftop route.

## Sources, exports, materials and shared fittings

Original Blender construction; no external/downloaded meshes, textures, fonts or real branding.
The parametric recipe uses the accepted shell's construction/interface conventions, but authors
a new U-shaped shell with its own editable source and export. Shared fittings remain unchanged.

- Source: `art/source/models/environment/d06_shopfront_blocks_02/d06_shopfront_blocks_02.blend`.
- Collection: `export_d06_shopfront_blocks_02`; root: `d06_shopfront_blocks_02`.
  Its 54 named mesh children and 15 mount empties are the complete export scope.
  `authoring_excluded/authoring_1m_reference` is outside that collection.
- Export: `art/models/environment/d06_shopfront_blocks_02/d06_shopfront_blocks_02.glb`,
  with engine-normalized `.glb.import` sidecar.
- Tools: `tools/asset_production/d06_shopfront_blocks_02/` contains `author.py`, `export.py`,
  `validate.py`, `render.py`, `check.gd` with its `.uid`, and `manifest.py`.
- Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
  Export loads `tools/assets/blender/export_settings.json`, restricts the named collection,
  disables skins/animations, and retains Y-up conversion, normals, UVs and materials.
  No embedded image, camera, light, rig, animation or collision geometry is exported.

Five opaque, backface-culled Principled materials use the shared shell's linearized swatches:

| Material | Source sRGB swatch | Metallic / roughness |
| --- | --- | --- |
| `shell_muted_plum_render` | `#81777C` | 0 / 0.78 |
| `shell_quiet_blue_roof` | `#405B68` | 0.12 / 0.65 |
| `shell_warm_structural_trim` | `#BBB6A8` | 0 / 0.70 |
| `shell_slate_plinth` | `#4A5358` | 0 / 0.78 |
| `shell_dark_drain_coping` | `#334950` | 0.35 / 0.48 |

Each shell mesh has one material slot; material assignments and exported PBR values are recorded
in the source and receipt. No external texture/material resource is necessary. Broad edge bevels
and applied weighted normals provide highlights. No custom LOD is authored; asset import retains
Godot's automatic LOD/shadow-mesh defaults. Repeated-instance rendering cost has not been measured.

### Front interface and fitted wrapper

`scenes/prefabs/environment/d06_shopfront_blocks_02.tscn` links the shell under identity-transform
`Visuals/Model`. `d06_shopfront_blocks_02_fitted.tscn` inherits that wrapper and supplies **15 unchanged
shared prefab instances**: three each of [canopy .01](city_shop_fittings_01.md),
[fascia .02](city_shop_fittings_02.md), [single surround .03](city_shop_fittings_03.md),
[display window .05](city_shop_fittings_05.md), and [single closed leaf .06](city_shop_fittings_06.md).
Their sources/GLBs remain owned by those assets; exact dependency paths and hashes are in the
manifest. No carrier geometry, mesh resource, material override or runtime node-construction
script is introduced. **Use the fitted prefab for a complete closed exterior**; the bare shell
is an installation interface with real facade apertures, not an interior-enabled building.

Frontage plane is Z=-9. `mount_{0,1,2}_{kind}` empties retain identity orientation/scale and map to
saved `Fittings/{West,Centre,East}{Entrance,Door,Window,Canopy,Fascia}` nodes:

| Kind | X for west / centre / east, m | Y, m |
| --- | --- | --- |
| `entrance_single`, `door_single` | -4.45 / 1.95 / 8.35 | 0 |
| `display_window` | -7.35 / -0.95 / 5.45 | 0.48 |
| `canopy` | -7.35 / -0.95 / 5.45 | 3.00 |
| `fascia` | -7.35 / -0.95 / 5.45 | 3.80 |

Each doorway has a 1.42 × 2.45 m structural aperture; each window a 3.04 × 1.88 m aperture with
bottom Y=0.54. Actual unchanged fitting rear vertices fit their voids; mount transforms agree in
Godot. These openings are filled by static leaves/panes and do not imply opening mechanics.

`Interfaces/CourtRear` is at (0,0,10), `Interfaces/CourtEast` at (10.6,0,7.4). These identity-basis
markers identify root-local ground reservations, not traffic, navigation or spawn approvals.
Translate/rotate the entire prefab on flat terrain; do not scale the kit or independently move
its fitting mounts. No world connector or second placement writer is created.

### Collision contract

One layer-1/mask-0 `StaticBody3D`, `Collision/Body`, owns exactly three simple boxes:

| Shape | Centre X/Y/Z, m | Size X/Y/Z, m |
| --- | --- | --- |
| `FrontBar` | (0,2.15,-5.8) | (19.2,4.3,6.4) |
| `WestWing` | (-6.4,2.15,3.2) | (6.4,4.3,11.6) |
| `EastWing` | (6.4,1.925,1.6) | (6.4,3.85,8.4) |

The boxes meet at Z=-2.6 without a gap and do not span the court or the shorter-wing setback.
They intentionally fill the exterior building masses, including closed apparent entrance recesses;
there is no interior navigation. The fitted wrapper disables the redundant inherited leaf/window
colliders and their layers, following the accepted shared fitted-shell convention. Editable children
are used **only for those collision disables**, not material/geometry overrides. Canopies, parapets,
trim and coping remain decoration; no low decorative snag shapes or duplicate court ground exists.
This asset adds no gameplay state, interaction, authority or replication behavior.

## Validation and evidence

[`validation.json`](d06_shopfront_blocks_02-evidence/validation.json) records final measurements:

- Shell: **8,668 triangles, 4,436 source vertices, 4,764 exported split vertices,
  54 meshes / 54 surfaces**, five unique materials.
- **Zero degenerate source faces, zero non-manifold edges, zero degenerate exported triangles**;
  finite coordinates, consistent winding/positive volume, unit-length corner/export normals,
  applied mesh/root transforms, exact export membership and axis/AABB checks pass.
- Six aperture tests: **1,350 clear rays and 12 edge hits**. Nine actual shared fitting insertion
  checks pass. The excluded reference measures exactly 1 m.
- Fitted instance-weighted raw-GLB totals: **34,288 triangles, 18,396 exported split vertices,
  132 meshes / 135 surfaces**, across 16 model instances. Godot mesh/surface counts agree.
  These totals are not a memory, draw-call, LOD or performance measurement.
- Fresh isolated export is byte-identical: **148,516 bytes**, SHA-256
  `31583e100f843eeb300eb3d3c76f243e3c945e83c535d68839a684ec1f87647c`.
- Pinned Godot **4.8.dev7.official.c971f93e7** loads both wrappers and all recursive dependencies.
  Two post-normalization load/pack/save cycles per wrapper preserve exact bytes and saved IDs.
  Shell scene: **1,784 bytes**, SHA-256
  `6fe846c86c6098796f1e28491bbb41ffbd04c71ccdba62488172291cdc11fae3`.
  Fitted scene: **5,935 bytes**, SHA-256
  `abafb7ef1903e99bb7b3ab237c6a8af99bab83d7682fbbe2554fb7bbff6b0191`.
- Native shape-query checks use the production-size **r=0.35 m, h=1.8 m capsule**:
  **12/12 bidirectional sweeps clear** through the court and east exit, five solid/seam overlap
  cases block, and three sweeps toward court walls block. These are bounded physics API proofs,
  not actor movement, floor continuity, car turning or multiplayer tests.
- Final headless import and runtime checks exit 0 with **no ERROR/SCRIPT ERROR lines**;
  owned GDScript format/lint passes. Import produces no unrelated tracked changes.

Four isolated Blender renders, all **1280×720**, Cycles CPU / 24 samples / AgX / PNG compression 95:
[hero](d06_shopfront_blocks_02-evidence/hero.png),
[side/rear](d06_shopfront_blocks_02-evidence/side.png),
[court detail](d06_shopfront_blocks_02-evidence/detail.png),
[47 m / 42° overhead](d06_shopfront_blocks_02-evidence/overhead_47m_42deg.png).
The overhead is vertical-down, fixed north-up, **42° vertical FOV**, height 47 m. All four final
renders were self-inspected. The unequal wing ends, height step and court read clearly; wall copy
is roof-occluded and must not carry essential overhead navigation. An initial visible coping-corner
overlap was corrected to butt joints, and side plinths were continued before final export/render.
The studio plane/lights/camera exist only in the isolated render session, never in the game asset.
These are not engine screenshots, actual gameplay views or independent visual acceptance.

### Exact reproduction (Git Bash, repository root)

No live Blender/Godot session was touched. The windowed editor is unavailable; permitted direct-text
scene authoring was followed by isolated headless editor normalization. This does not synchronize
any separately open scene. Check the manifest before intentionally refreshing artifacts.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=C:/tmp/ft/assets/d06_shopfront_blocks_02
P=tools/asset_production/d06_shopfront_blocks_02
mkdir -p "$T"
python "$P/manifest.py" --verify
# Source regeneration is optional; explicit export/reexport uses the committed source.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/export.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/export.py" -- "$T/reexport.glb"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/validate.py" -- "$T/reexport.glb"
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --editor --path . --script "res://$P/check.gd" -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script "res://$P/check.gd"
# Rerun the source audit after engine checks to refresh fitted-instance counts.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/validate.py" -- "$T/reexport.glb"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/render.py"
timeout 30 "$(mise which gdstyle)" fmt --check "$P/check.gd"
timeout 30 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$P/check.gd"
timeout 300 "$(mise which godot)" --headless --path . --import
```

After intentional changes, refresh this handoff from final validation, then run `manifest.py` without
`--verify` last. The manifest hashes every delivered payload except itself and records read-only
dependencies. Scratch/retry/raw logs stay under `$T`; the sole committed
[`final.log`](d06_shopfront_blocks_02-evidence/final.log) records outcomes and diagnostic classification.
Headless editor normalization exits 0 but emits the existing editor/plugin shutdown RID/ObjectDB
leak diagnostics. This is **not** a clean editor-shutdown claim. Separate runtime validation is clean;
final import has only the existing toolkit-version warning. One initial long-line lint warning was
fixed. Blender authoring has a pin-level `Material.use_nodes` deprecation warning, not an export error.
No broad production-check suite ran: owner decision 52 excludes it for unplaced assets.

## Remaining acceptance

Independent art/technical review; district selection/placement and route continuation; actual actor
motion/aim, car clearances and floor/road integration; authoritative/predicted/network behavior;
populated native gameplay-camera readability; packaged build and sustained repeated-instance GPU/Deck
performance remain **pending**. The footprint and connections are provisional until placement review.
This delivery does not approve a district layout, mark the register READY or close gameplay gates.
The earlier short-row handoff has no stale family-pending checklist item, so no sibling file was edited.
