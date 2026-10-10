# d06_shopfront_blocks.03 — Chamfered corner block

**Production asset candidate delivered; independent review and world placement pending.**
Producer: commissioned implementation worker on `lane/a-sfront`. Authority: current per-record
commission and [production commission](commission.md), superseding the family's historical
concept-only restriction. Family: [Signal Row shopping blocks](../d06_shopfront_blocks.md).
No district scene, road, placed identity, shared fitting, sibling payload or register was changed.

## Design and provisional dimensions

One low pentagonal shop block has a **4.80 × 4.80 m clipped north-east corner**, with a storefront
on that diagonal rather than an ordinary rectangular shell painted differently. Three unequal
facade lengths carry the same shared 6.4 m storefront interface, at 0°, -45° and -90° yaw. The
corner creates genuine outside space; the deep roof and quiet rear walls leave surrounding rear
access to the world layout. This is a northern corner alternative, not the continuous southern
shopping parade and not an extra ordinary freestanding shared shop.

The muted-plum wall, quiet blue roof, warm trim and slate plinth retain the earlier
[short row](d06_shopfront_blocks_01.md) and [rear-court shell](d06_shopfront_blocks_02.md) palette.
The family varies negative space and roof depth: detached/setback row, unequal rear court, then
this solid clipped corner. Broad blank fascia carriers are unchanged existing fittings. Selective
cyan/magenta tenant graphics belong to [commercial artwork](d06_commercial_graphics_02.md);
this delivery does not select tenants, duplicate that hardware or introduce real branding.

References inspected: [district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[Signal Row v03](../../concepts/districts-v1/signal-row.md) and its
[shared contract](../../concepts/districts-v1/brief-contract.md). All new dimensions below are
**provisional producer-authored values** under the standing dimensional rule, not measurements
from concept pixels or approved site allocations. District fit remains untested.

Godot coordinates in metres: +X east/right, +Y up, primary front -Z. Blender +Y maps to Godot -Z.
Root pivot `(0,0,0)` is ground-centred on the **16.0 × 12.8 m structural bounding rectangle**, not
the pentagon's area centroid. Mesh/root transforms are identity; mount empties deliberately carry
their facade yaw. An excluded 1 m Blender reference is saved but never exported.

| Contract | Provisional value |
| --- | --- |
| Structural footprint, successive X/Z vertices | (-8,-6.4), (3.2,-6.4), (8,-1.6), (8,6.4), (-8,6.4) |
| Primary front / diagonal / east frontage lengths | 11.20 / 6.788225 / 8.00 m |
| Structural corner plane | X − Z = 9.60; building lies on the X − Z ≤ 9.60 side |
| Ground / roof deck / wall top / coping top Y | 0 / 4.30 / 4.95 / 5.05 m |
| Wall depth / coping outward projection | 0.28 / 0.08 m |
| Shell visual AABB | (-8.08,0,-6.48) → (8.08,5.05,6.48) m |
| Shell visual width / height / depth | 16.16 × 5.05 × 12.96 m |
| Fitted visual AABB | (-8.08,0,-7.50) → (9.10,5.05,6.48) m |
| Fitted visual width / height / depth | 17.18 × 5.05 × 13.98 m |

Envelope tolerance ±0.001 m in source/export; ±0.002 m in Godot; coordinate mapping ±0.00001 m.
Each canopy projects 1.10 m from its facade; reserve the shared **1.20 m installation depth**
along that facade's outward normal, including the diagonal. Front installation limit is Z=-7.60;
east installation limit X=9.20. Overhead trim is not a gameplay boundary. No road, sidewalk,
paving, interior, stairs, roof traversal, opening-door state or destruction mechanic is supplied.

## Sources, exports and materials

Original parametric Blender construction; no downloaded/purchased/image-to-mesh geometry, external
textures or fonts. Shared fittings stay source-linked to their existing owners.

- Source: `art/source/models/environment/d06_shopfront_blocks_03/d06_shopfront_blocks_03.blend`.
- Collection: `export_d06_shopfront_blocks_03`; root: `d06_shopfront_blocks_03`.
  Exactly **32 named mesh children and 15 mount empties** comprise the export scope.
  `authoring_excluded/authoring_1m_reference` is excluded.
- Export: `art/models/environment/d06_shopfront_blocks_03/d06_shopfront_blocks_03.glb`, with its
  pinned-engine-normalized `.glb.import` sidecar.
- Tools: `tools/asset_production/d06_shopfront_blocks_03/` contains `author.py`, `export.py`,
  `validate.py`, `render.py`, `check.gd` with its `.uid`, and `manifest.py`.
- Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export reads the shared
  `tools/assets/blender/export_settings.json`, limits the named collection and disables animations
  and skins. Y-up conversion, normals, UVs and opaque materials are retained. No cameras, lights,
  images, textures, rigs, animation or collision meshes are embedded in the GLB.

Each mesh has one opaque, backface-culled Principled material slot. Linearized shared swatches:

| Material | Source sRGB | Metallic / roughness |
| --- | --- | --- |
| `shell_muted_plum_render` | `#81777C` | 0 / 0.78 |
| `shell_quiet_blue_roof` | `#405B68` | 0.12 / 0.65 |
| `shell_warm_structural_trim` | `#BBB6A8` | 0 / 0.70 |
| `shell_slate_plinth` | `#4A5358` | 0 / 0.78 |
| `shell_dark_drain_coping` | `#334950` | 0.35 / 0.48 |

Broad applied bevels/weighted normals provide trim highlights; the uninterrupted roof has only two
quiet rear seam bands. No texture or external material resource is necessary. No custom LOD is
added; Godot's automatic LOD/shadow-mesh import defaults remain. Repeated-instance cost is unmeasured.

## Prefabs, fitting interface and collision

`scenes/prefabs/environment/d06_shopfront_blocks_03.tscn` wraps the linked shell under
identity-transform `Visuals/Model`. `d06_shopfront_blocks_03_fitted.tscn` inherits it, supplying
**15 unchanged shared prefab instances**: three each of [canopy .01](city_shop_fittings_01.md),
[fascia .02](city_shop_fittings_02.md), [single surround .03](city_shop_fittings_03.md),
[display window .05](city_shop_fittings_05.md) and [closed single leaf .06](city_shop_fittings_06.md).
The fitted prefab is the complete closed exterior. The bare shell has real installation apertures,
not an interior-enabled building. No render mesh resource or runtime hierarchy is copied/composed.

Facade frames are root-local; yaw is Godot rotation about +Y:

| Index / fitted prefix | Frame origin X/Y/Z, m | Yaw | Local +X tangent |
| --- | --- | --- | --- |
| 0 / `Front` | (-2.4,0,-6.4) | 0° | (1,0,0) |
| 1 / `Corner` | (5.6,0,-4) | -45° | (0.707107,0,0.707107) |
| 2 / `East` | (8,0,2.4) | -90° | (0,0,1) |

`mount_{index}_{kind}` maps to `Fittings/{prefix}{Entrance,Door,Window,Canopy,Fascia}`. In each
facade frame, local X/height offsets are: `entrance_single` and `door_single` (1.95,0),
`display_window` (-0.95,0.48), `canopy` (-0.95,3.00), `fascia` (-0.95,3.80). Each mount has unit
scale and the corresponding frame yaw. Exact source/import positions and yaws are in the receipt.
Door apertures are **1.42 × 2.45 m**; window apertures **3.04 × 1.88 m**, bottom Y=0.54. Actual
unchanged fitting rear vertices fit all three differently oriented facades.

`Interfaces/CornerForecourt` at (7,0,-5.4) and `Interfaces/RearLink` at (0,0,7.5) are identity-basis
ground reservation markers, not directed traffic links, navigation, approved spawns or guaranteed
world routes. Translate/rotate the entire prefab on flat terrain; do not scale it or independently
move fittings. Adjoining open ground and generated sidewalk/floor continuity remain placement work.

### Single solid-footprint collider

One layer-1/mask-0 `StaticBody3D`, `Collision/Body`, owns **one `ConvexPolygonShape3D`** at
`Footprint`. Its **ten authored points** extrude the five documented structural vertices between
Y=0 and Y=4.30. It is dimension-authored, never derived from the render mesh. The standing
non-rectangular-footprint exception permits this minimal convex shape; a bounding box would
incorrectly occupy the clipped corner. It fills the closed exterior mass, including apparent door
recesses, and does not imply navigable interiors. No ground surface collider is added.

The fitted wrapper disables redundant inherited leaf/window collider shapes and their layers,
following the accepted shared fitted-shell convention. Editable children are used **only for those
collision disables**, not geometry/material overrides. Canopies, parapets and trim remain decoration.

Bounded native physics checks use the production-sized **radius-0.35 m, height-1.8 m capsule**:
12/12 bidirectional sweeps stay clear along the corner, front, rear and west reservations; four
solid/end-join overlap cases hit exactly the single body; three probes inside the clipped-away
bounding-box corner remain empty. Three inward sweeps across the diagonal at centre and near both
ends stop at fraction **0.32421875** of a 2 m motion from 1 m outside the structural wall. This
agrees with a capsule radius of 0.35 m and proves the contact is on the visible plane, not an
invisible rectangular blocker or corner gap. These are shape-query proofs, not actual actor motion,
car turning, floor continuity or multiplayer acceptance.

## Validation and visual evidence

Final measurements in [`validation.json`](d06_shopfront_blocks_03-evidence/validation.json):

- Shell: **5,508 triangles; 2,812 source vertices; 3,084 exported split vertices;
  32 meshes / 32 material surfaces; five unique materials**.
- **Zero non-manifold edges, degenerate source faces or degenerate exported triangles**. Finite
  coordinates, consistent winding/positive component volume, unit-length source/export normals,
  applied mesh/root transforms, export membership, metre reference and axis/AABB checks pass.
- Six aperture tests: **1,350 clear rays and 12 edge hits**. Nine actual shared fitting insertion
  checks pass, including ray checks through their rotated facade openings.
- Fitted instance-weighted totals: **31,128 triangles; 16,716 exported split vertices;
  110 meshes / 113 surfaces across 16 model instances**. Godot mesh/surface totals agree.
  These are geometry counts, not draw-call, memory, LOD or performance measurements.
- Fresh-process export is byte-identical: **100,860 bytes**, SHA-256
  `46b7019e83c69853b8e5af1d05af2cfa1867febc8c9f5acf5785fc3e28afaad3`.
- Pinned Godot **4.8.dev7.official.c971f93e7** loads both scenes and every recursive dependency/UID.
  Two post-normalization load/pack/save cycles per wrapper preserve exact scene bytes and IDs.
  Shell scene: **1,321 bytes**, SHA-256
  `e39b86f6de6b25f34cb746683c3de89c3877430c5ace9197e55c704e31cc29dd`.
  Fitted scene: **6,240 bytes**, SHA-256
  `9e51f373fae067c37aa6295c720280b1c5eb0d1d08953ca99ed3fa95e5a381f7`.
- Owned GDScript formatting/lint passes. Final headless import and runtime checks exit 0 with
  **no ERROR/SCRIPT ERROR lines**. No unrelated import/UID changes were produced.

Four isolated Blender renders, **1280×720**, Cycles CPU / 24 samples / AgX / PNG compression 95:
[hero](d06_shopfront_blocks_03-evidence/hero.png),
[side/rear](d06_shopfront_blocks_03-evidence/side.png),
[corner detail](d06_shopfront_blocks_03-evidence/detail.png),
[47 m / 42° overhead](d06_shopfront_blocks_03-evidence/overhead_47m_42deg.png).
The overhead is vertical-down perspective, fixed north-up, **42° vertical FOV**, height 47 m.
The render script reads full fitting transforms from the validated saved Godot scene receipt;
it does not maintain a competing layout. All four images were self-inspected: the clipped silhouette,
three frontage orientations and quiet deep roof read clearly. Blank wall fascia copy is roof-occluded
from overhead and must not carry essential navigation. Rear walls intentionally stay quiet. Studio
ground/lights/camera exist only in the unsaved evidence process, never in a delivered game scene.
These are not engine screenshots, populated gameplay views or independent visual acceptance.

### Exact reproduction (Git Bash, repository root)

No live Blender/Godot session was touched. The windowed editor is unavailable; explicitly allowed
direct-text scene authoring was followed by isolated headless normalization. This does not prove
synchronization of a separate open scene. Verify the manifest before intentionally refreshing assets.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=C:/tmp/ft/assets/d06_shopfront_blocks_03
P=tools/asset_production/d06_shopfront_blocks_03
mkdir -p "$T"
python "$P/manifest.py" --verify
# Optional source regeneration; ordinary reexport reads the committed .blend.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/export.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/export.py" -- "$T/reexport.glb"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/validate.py" -- "$T/reexport.glb"
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --editor --path . --script "res://$P/check.gd" -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script "res://$P/check.gd"
# Refresh fitted totals from the saved engine receipt.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/validate.py" -- "$T/reexport.glb"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$P/render.py"
timeout 30 "$(mise which gdstyle)" fmt --check "$P/check.gd"
timeout 30 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$P/check.gd"
timeout 300 "$(mise which godot)" --headless --path . --import
```

After intentional changes, refresh handoff values from the final validation receipt, then run
`manifest.py` without `--verify` last. The manifest hashes every delivered payload except itself and
inventories read-only dependencies. Raw/retry logs and scratch exports remain under `$T`; one concise
[`final.log`](d06_shopfront_blocks_03-evidence/final.log) records final results and diagnostics.

The first normalization caught transposed yaw entries in the newly authored fitted TSCN; those
were corrected and all mount/AABB/physics checks rerun. An initial function-length lint warning was
resolved by separating contact probes. Headless editor normalization exits 0 but emits the existing
editor/plugin shutdown RID/ObjectDB leak/scan-abort diagnostics; this is **not** a clean editor-shutdown
claim. Separate runtime checks are clean; final import has only the existing toolkit-version warning.
Blender reports pin-level `use_nodes` deprecation warnings, not source/export failures. No broad
production-check suite ran, per owner decision 52 for unplaced assets.

## Remaining acceptance

Independent art/technical review; selected district placement and adjoining corner/rear routes;
actual actor motion/aim and car clearances; floor/road integration; authoritative/predicted/network
behavior; populated native gameplay-camera readability; packaged-build and sustained repeated-instance
GPU/Deck performance remain **pending**. Dimensions/interfaces remain provisional until placement
review. This does not approve a district layout, mark the register READY or close gameplay gates.
Neither earlier sibling handoff listed this asset as still pending, so no sibling file or historical
receipt needed modification.
