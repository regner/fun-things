# city_small_shop_shells.04 — Compact square shop shell

9 October 2026. **Source/export and linked-prefab production candidate delivered;
independent review and world acceptance pending.** The current dispatch/common brief
and [commission](commission.md) supersede the historical concept-only restriction.
Original Blender construction, integration and self-checks: commissioned implementation
worker. The supervising production lead approved the provisional dimensions and collision
scope below before construction; independent reviewers remain the acceptance owners.
No shared tracker, sibling asset, gameplay code or world placement changed.

Family: [small shop shells](../city_small_shop_shells.md). References inspected:
[Signal Row B03](../../concepts/districts-v1/signal-row-assets.md),
[Signal Row / Broadlot identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[wide sibling .02](city_small_shop_shells_02.md), accepted inline .01 and fitting prefabs.

## Design and provisional dimensions

A compact single-storey shop with a **near-square quiet roof and one short frontage**.
The .01/.02 family palette, wrapped plinth and coping, warm frontage piers and head
course remain consistent. Two sparse standing folds interrupt the roof without adding
machinery or noise. The 6.4 × 6.4 m mass differs from the deep .01 and wide .02 by
footprint, not colour. Exposed rear/side walls are intentionally plain ordinary
architecture; this is neither a landmark nor a shop-home with upper accommodation.

The lead explicitly approved the **provisional, reversible 6.4 m wide × 6.4 m deep
structural footprint**, .01/.02 heights and palette, one 6.4 m fitting interface,
bare/fitted prefabs, and one solid exterior footprint collider. These are authored
measurements, **not dimensions inferred from generated images**. Flat terrain only;
no interiors, rooftop gameplay, door operation or destruction states.

| Measurement | Metres |
| --- | --- |
| Structural footprint, Blender X/Y | [-3.2, 3.2] × [-3.2, 3.2] |
| Full Blender mesh AABB | (-3.28, -3.28, 0) → (3.28, 3.32, 5.05) |
| Full Godot mesh AABB | (-3.28, 0, -3.32) → (3.28, 5.05, 3.28) |
| Full Godot width X / height Y / depth Z | 6.56 / 5.05 / 6.60 |
| Front plane / wall thickness, Blender Y | 3.20 / 0.28 |
| Roof deck underside / top | 4.14 / 4.30 |
| Side/rear wall top / coping top | 4.60 / 4.70 |
| Front parapet coping top | 5.05 |
| Front / rear / lateral visual projections | 0.12 / 0.08 / 0.08 |
| Source/export envelope tolerance | ±0.001 per bound; raw GLB comparison 0.00001 |

Ground-centred structural-footprint pivot `(0,0,0)`, applied identity root/mesh
transforms, metre units and unit scale. Blender +Y front / +Z up maps once to Godot
-Z front / +Y up. No corrective prefab rotation or scale. An excluded hidden 1 m
reference cube is saved in `authoring_excluded`. Components are closed manifold
geometry with real facade holes, not a fused engineering/weatherproof building.

## Source, exports and materials

- Source: `art/source/models/environment/city_small_shop_shells_04/city_small_shop_shells_04.blend`.
- Collection: `export_city_small_shop_shells_04`; root: `city_small_shop_shells_04`.
- Export: `art/models/environment/city_small_shop_shells_04/city_small_shop_shells_04.glb`
  with its committed `.glb.import`.
- Parametric construction, export, validation, render, engine check and manifest tools:
  `tools/asset_production/city_small_shop_shells_04/`.
- Original editable Blender construction following the sibling's family recipe;
  no downloaded/purchased/image-to-mesh geometry, brands, fonts or textures.
- Shared `tools/assets/blender/export_settings.json` owns export options; named
  collection filtering and static animation/skin exclusions are explicit.
- Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. All source
  modifiers are applied. glTF owns final triangulation. Cameras, lights, reference
  cube, studio, fittings and collision geometry are excluded from the shell GLB.

Five opaque back-culled Principled/glTF materials match .01/.02 names and linearized
swatches. Each of the 22 semantic meshes has one surface. No UV-dependent effect,
external textures, embedded images or Godot `.tres` override is needed.

| Material | sRGB reference | Metallic / roughness |
| --- | --- | --- |
| `shell_muted_plum_render` | #81777C | 0 / .78 |
| `shell_quiet_blue_roof` | #405B68 | .12 / .65 |
| `shell_warm_structural_trim` | #BBB6A8 | 0 / .70 |
| `shell_slate_plinth` | #4A5358 | 0 / .78 |
| `shell_dark_drain_coping` | #334950 | .35 / .48 |

Asset-local default Godot automatic LOD, shadow mesh and compression settings remain
unchanged. No measured repeated-instance budget or target-device cost is claimed.

## Fitting interfaces and saved prefabs

`scenes/prefabs/environment/city_small_shop_shells_04.tscn` is the **bare shell part**.
`city_small_shop_shells_04_fitted.tscn` inherits it and instances five unchanged shared
fitting prefabs: canopy .01, fascia .02, single surround .03, display window .05,
and single closed leaf .06. The fitted prefab is the complete static visual candidate.
Bare holes need fittings before presentation as a finished building. Blank signage
is intentional; commercial artwork belongs to a separate asset owner.

Both preserve identity `Visuals/Model` linked to the shell GLB. No copied render mesh,
stretched fitting, imported-child override or runtime scene composition is used.
Fitted placements exactly match the source/imported markers below; all rotations are
identity and all scales one. Each marker is parented to the source root.

| Marker | Godot translation | Consumer |
| --- | --- | --- |
| `mount_front_entrance_single` | (1.95, 0, -3.2) | .03 single |
| `mount_front_door_single` | (1.95, 0, -3.2) | .06 single |
| `mount_front_display_window` | (-.95, .48, -3.2) | .05 |
| `mount_front_canopy` | (-.95, 3, -3.2) | .01 |
| `mount_front_fascia` | (-.95, 3.8, -3.2) | .02 |
| `mount_roof_detail` | (0, 4.3, 0) | Optional separately owned roof fitting |

The entrance hole is 1.42 × 2.45 m at X [1.24,2.66], height [0,2.45]. The display
hole is 3.04 × 1.88 m at X [-2.47,.57], height [.54,2.42]. At least 0.55 m clear
rear insertion depth is reserved. **1,802 actual unchanged fitting rear vertices**
fit these voids; 450 hole rays are clear and four adjacent edge rays hit the wall.
Nominal entrance jamb/head gaps are 10 mm; window sleeve gaps are 20 mm. Retain
±2 mm fitting-mount tolerance; arbitrary offsets do not inherit the nominal gaps.

Canopy bottom is 2.58 m, 100 mm above the window; fascia bottom is 3.40 m, 160 mm
above the canopy. Canopy projection reaches Godot Z=-4.30. Reserve its existing
1.20 m installation envelope through Z=-4.40. Placement must account for fittings,
not just the bare-shell AABB. No inline party-wall joining interface is exposed.

### Deliberate exterior-only collision

One `Collision/Body` StaticBody3D on layer 1 / mask 0 owns a **6.4 × 4.3 × 6.4 m**
box centred at `(0,2.15,0)`. The entire footprint is solid, including apparent entrance
recesses and bare apertures. This follows .02, not .01's wall-span collision. Do not
use it for interior traversal. Coping, folds, signs and canopy remain decoration.

The fitted leaf's one shape and window's two shapes are disabled; their bodies have
layer 0 through explicit saved fitting-level editable overrides. Shared fitting scenes
and imported visuals are untouched. This keeps one collision owner without adding
new opening, interaction, authority or replication behavior.

Native headless tests query the actual fitted prefab: three exterior rays hit the
shell body, a side-bypass ray is clear, and a radius .38 m / height 1.8 m capsule
hits the footprint once but is clear on the front walkway. These are bounded public
physics-query checks, not production actor movement, network or world placement proof.

## Validation and visual evidence

[`validation.json`](city_small_shop_shells_04-evidence/validation.json) records:

- **3,540 triangles; 1,812 source vertices; 1,940 exported split vertices; 22 meshes /
  22 surfaces; five materials; six mounts plus one root; 62,392-byte GLB.**
- Zero degenerate source faces, raw GLB degenerate triangles or non-manifold edges.
  Closed, consistently wound components with positive signed volumes.
- Finite vertices, unit-length source corner/exported normals, consistent triangle
  winding, applied transforms, exact collection membership, metre bounds and ground datum.
- Fresh-process saved-source reexport **byte-identical** to committed GLB. Rebuilding
  the `.blend` itself is not claimed byte-identical.
- Pinned Godot **4.8.dev7.official.c971f93e7** import and fresh-runtime recursive
  resource loads resolve dependencies and saved UIDs. Bare/inherited scene save/reload
  roundtrips are byte-stable. Measured bounds match within .001 m; five fitting
  placements have zero error against actual imported markers. All fitting collision
  is disabled as specified; bounded native physics checks pass.

Four isolated Blender renders, Cycles CPU / 32 samples / AgX / broad studio fill,
all 1280×800: [hero, fitted](city_small_shop_shells_04-evidence/hero.png),
[side/rear, bare](city_small_shop_shells_04-evidence/side.png),
[frontage detail, fitted](city_small_shop_shells_04-evidence/detail.png),
[47 m / 42° overhead, fitted](city_small_shop_shells_04-evidence/overhead_47m_42deg.png).
The overhead is vertical-down perspective, north-up, Blender camera `(0,0,47)`,
42° **vertical** FOV. Self-inspected all four; initial tight hero/side framing was
widened so final inspection views retain the whole silhouette. The compact roof
reads distinctly from .02; roof and canopy dominate overhead, while fascia/door
copy is roof-occluded. Do not rely on facade copy for essential overhead navigation.
Fittings are temporary unchanged GLB imports only in the unsaved render composition.
These are not actual engine screenshots or combat/target-device acceptance.

[`manifest.json`](city_small_shop_shells_04-evidence/manifest.json) hashes all final
produced payloads except itself, plus ten read-only fitting dependencies.
[`final.log`](city_small_shop_shells_04-evidence/final.log) records concise outcomes
and diagnostic classification. Scratch exports and raw logs stay outside Git at
`C:/tmp/ft/assets/city_small_shop_shells_04/`.

## Exact reproduction (Git Bash, repository root)

No live Blender/Godot or connector sessions were used. Windowed editor is unavailable;
text prefab authoring followed by headless normalization is explicitly authorized.
Headless import does not synchronize any separate open editor scene.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=C:/tmp/ft/assets/city_small_shop_shells_04
mkdir -p "$T"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_04/author.py
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_04/export.py
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_04/export.py -- "$T/reexport.glb"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_04/validate.py -- "$T/reexport.glb"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_04/render.py
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script res://tools/asset_production/city_small_shop_shells_04/check.gd -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script res://tools/asset_production/city_small_shop_shells_04/check.gd
timeout 180 "$(mise which godot)" --headless --path . --check-only --script res://tools/asset_production/city_small_shop_shells_04/check.gd
timeout 30 "$(mise which gdstyle)" --max-warnings 0 tools/asset_production/city_small_shop_shells_04/check.gd
timeout 30 "$(mise which gdstyle)" fmt --check tools/asset_production/city_small_shop_shells_04/check.gd
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python tools/asset_production/city_small_shop_shells_04/manifest.py --verify
```

For read-only validation skip authoring/production export and export only to scratch.
Verify the manifest before regenerating evidence, since regeneration changes hashes.
Canonical check output must be a fresh directory. Refresh the manifest without
`--verify` only after an intentional rebuild and review.

### Checks and diagnostic classification

Final scoped lint, format, explicit compilation, source/raw GLB audit, fresh reexport,
rendering and separate runtime checks **pass**. Initial owned formatting drift was
corrected; final gdstyle reports no issues. Canonical production checks exit **1**
solely for known pre-existing compile failures in five asset-production fixtures
(`batch_02_observation`, `batch_02_process_probe`, `batch_03_observation`,
`batch_03_process_probe`, `batch_observation`) and formatting of `batch_observation.gd`,
integration `batch03_author.gd` and `inspector.gd`. All 47 scripts pass lint; this
asset's checker compiles. Python tests **9/9**, GUT **9/9** with **70 assertions**,
and negative-control failure detection pass. None of those unrelated files changed.

Import exits 0 with the existing plugin untested-4.8 warning. Editor-mode scene
normalization exits 0 and verifies stable scene bytes/UIDs, but logs editor/plugin
shutdown **RID/ObjectDB leak diagnostics**; this is not a clean-editor-exit claim.
Final separate runtime and explicit compile checks exit 0 with no warnings/errors.
Blender author/export/reexport/validate/render processes exit 0; only the separate
version query emitted the known one-small-block shutdown diagnostic. No error was
broadly suppressed and no unrelated process was touched or terminated.

## Remaining acceptance

Independent source/art/prefab review; final layout-owner dimensional approval;
actual actor movement/aim and corner clearances; authoritative/predicted/multiplayer
behavior; gameplay-camera combat readability; district placement/derived data;
commercial artwork; repeated-instance performance, packaged build and sustained
Deck/device validation remain **pending**. Bare apertures are not traversable under
the approved exterior collider. This delivery does not mark the register READY or
authorize world placement. Production lead owns review/next handoffs.
