# city_small_shop_shells.03 — L-shaped corner shell

9 October 2026. **Source/export and linked-prefab production candidate delivered;
independent review and world acceptance pending.** The current dispatch/common brief
and [commission](commission.md) supersede the family's historical concept-only status.
Original Blender construction, integration and self-checks: commissioned implementation
worker. The supervising production lead approved the provisional dimensions and collision
scope below before construction. Independent reviewers remain the acceptance owners.
No sibling asset, shared tracker, gameplay script or world placement was changed.

Family: [small shop shells](../city_small_shop_shells.md). References inspected:
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[wide .02](city_small_shop_shells_02.md), [compact .04](city_small_shop_shells_04.md),
accepted inline .01/fittings and the three existing integration handoffs.
This citywide option is not an additional Signal Row rendering requirement or the
Crescents' separately owned wedge-shaped landmark.

## Design and provisional dimensions

A single-storey ordinary shop with a **continuous L roof and an open rear-right notch**.
Two front fitting bays and one outward-facing west return bay wrap the exterior;
the quiet notch walls have no entrances or windows. Sparse standing folds, wrapped
plinth/head courses, restrained warm piers and stepped parapets retain .01/.02/.04's
language. It differs by footprint, not colour: no rectangular slab fills the notch,
no central party wall divides the arms, and no interior detail or machinery is added.

The lead explicitly approved a **provisional, reversible 12.8 × 12.8 m bounding
footprint**: a 12.8 × 6.4 m front bar plus a 6.4 × 6.4 m left rear return, leaving
a 6.4 × 6.4 m rear-right notch. Three unchanged fitting interfaces, family heights
and palette, bare/fitted prefabs and two non-overlapping solid collision boxes were
approved together. These are authored choices, **not dimensions inferred from images**.
Final layout-owner approval remains pending. Flat terrain; no interiors or roof gameplay.

| Measurement | Metres |
| --- | --- |
| Front bar, Blender X/Y | [-6.4, 6.4] × [0, 6.4] |
| Rear return, Blender X/Y | [-6.4, 0] × [-6.4, 0] |
| Open structural notch, Blender X/Y | [0, 6.4] × [-6.4, 0] |
| Full Blender mesh AABB | (-6.52, -6.48, 0) → (6.48, 6.52, 5.05) |
| Full Godot mesh AABB | (-6.52, 0, -6.52) → (6.48, 5.05, 6.48) |
| Full Godot width X / height Y / depth Z | 13.00 / 5.05 / 13.00 |
| Front facade / west return facade, Blender | Y=6.4 / X=-6.4 |
| Wall thickness | .28 |
| Continuous deck underside / top | 4.14 / 4.30 |
| Plain perimeter wall / coping top | 4.60 / 4.70 |
| Front and west-return parapet / coping top | 4.95 / 5.05 |
| Front/west fitting-facade maximum visual projection | .12 |
| Other perimeter coping projection | .08 |
| Envelope tolerance / raw GLB comparison tolerance | ±.001 / .00001 |

Pivot `(0,0,0)` is ground-centred on the **bounding footprint**, not the L's area
centroid (the structural area centroid is X=-1.0667, Blender Y=+1.0667). The origin
coincides with the re-entrant structural corner; arms extend towards Blender +Y and
-X. Ground contact is Z=0 in Blender / Y=0 in Godot. Root and all mesh transforms
are identity, metre units, unit scale. Blender +Y front / +Z up maps once to Godot
-Z front / +Y up. West frontage faces Godot -X. No corrective model/prefab scale or
rotation. An excluded hidden 1 m reference cube is saved in `authoring_excluded`.
Components are closed manifold geometry, not a fused engineering/weatherproof building.

## Source, export and materials

- Source: `art/source/models/environment/city_small_shop_shells_03/city_small_shop_shells_03.blend`.
- Collection: `export_city_small_shop_shells_03`; root: `city_small_shop_shells_03`.
- Export: `art/models/environment/city_small_shop_shells_03/city_small_shop_shells_03.glb`
  and its committed `.glb.import` identity/settings.
- Author/export/validate/render/engine-check/manifest tools:
  `tools/asset_production/city_small_shop_shells_03/`.
- Original editable Blender construction following the accepted family conventions.
  No downloads, purchased or image-to-mesh geometry, real brands, fonts or textures.
- Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
  Shared `tools/assets/blender/export_settings.json` owns export settings; explicit
  named-collection filter and static animation/skin exclusions. Modifiers are applied;
  glTF performs final triangulation.
- No cameras/lights, studio, reference cube, fittings, collision geometry, rigs,
  animations, destruction states, embedded images or texture dependencies enter the GLB.

Five opaque, back-culled Principled/glTF PBR materials match .01/.02/.04's names and
linearized swatches. Each semantic mesh has one surface. No Godot material override
or separate `.tres` is needed. Actual exported values are retained in validation.json.

| Material | sRGB reference | Metallic / roughness |
| --- | --- | --- |
| `shell_muted_plum_render` | #81777C | 0 / .78 |
| `shell_quiet_blue_roof` | #405B68 | .12 / .65 |
| `shell_warm_structural_trim` | #BBB6A8 | 0 / .70 |
| `shell_slate_plinth` | #4A5358 | 0 / .78 |
| `shell_dark_drain_coping` | #334950 | .35 / .48 |

Default asset-local Godot automatic LOD, shadow-mesh and compression settings remain
unchanged. No ratified polygon budget or measured repeated-instance cost is claimed.

## Fitting interfaces and saved prefabs

`scenes/prefabs/environment/city_small_shop_shells_03.tscn` is the **bare shell part**;
its real apertures need fittings before presentation as a complete building.
`city_small_shop_shells_03_fitted.tscn` inherits it and instances fifteen unchanged
fitting prefabs: three each of canopy .01, fascia .02, single surround .03, display
window .05 and single closed leaf .06. Blank fascia artwork is intentional and belongs
to a separate asset owner. This is not missing shell geometry.

Both preserve identity `Visuals/Model` linked to the shell GLB. No copied render
geometry, stretched fitting, imported-visual override or runtime composition is used.
Mount markers are source-root children preserved by name. Saved fitting placements
are checked against their actual imported marker transforms, including west yaw.

| Marker suffix | `mount_left_` Godot XYZ | `mount_right_` Godot XYZ | `mount_west_` Godot XYZ |
| --- | --- | --- | --- |
| `entrance_single` / `door_single` | (-1.25, 0, -6.4) | (5.15, 0, -6.4) | (-6.4, 0, 1.25) |
| `display_window` | (-4.15, .48, -6.4) | (2.25, .48, -6.4) | (-6.4, .48, 4.15) |
| `canopy` | (-4.15, 3, -6.4) | (2.25, 3, -6.4) | (-6.4, 3, 4.15) |
| `fascia` | (-4.15, 3.8, -6.4) | (2.25, 3.8, -6.4) | (-6.4, 3.8, 4.15) |

Left/right rotations are identity. West markers have **Godot +90° Y yaw** (Blender
+90° Z): local -Z faces -X and local +X faces -Z. All scales are one.
`mount_roof_detail` is Godot `(-3.2,4.3,-3.2)` on the deck between folds; no roof
fixture is embedded. No inline party-wall joining interface is exposed.

Each 6.4 m bay retains .01's 1.42 × 2.45 m entrance hole and 3.04 × 1.88 m display
hole, with at least .55 m clear rear insertion. Local bay X intervals are [1.24,2.66]
for entrances at height [0,2.45], and [-2.47,.57] for windows at height [.54,2.42].
Front bay centres are X=-3.2/+3.2; west local X increases along Blender +Y from -3.2.
**5,406 actual unchanged fitting rear vertices** pass the insertion-void checks;
1,350 aperture rays are clear and 12 adjacent wall rays hit. Nominal entrance jamb/head
clearance is 10 mm; window sleeve clearance is 20 mm. Preserve ±2 mm mount tolerance.

Canopy bottom is 2.58 m (100 mm above window); fascia bottom is 3.40 m (160 mm above
canopy). Fitted canopies reach Godot Z=-7.50 on the front and X=-7.50 on the west;
reserve the existing 1.20 m installation depth through Z/X=-7.60 respectively.
Notch coping projects .08 m into its structural opening; plinth projects .045 m.
Do not infer walkway or notch clearances solely from the structural footprint.

### Deliberate exterior-only collision

One `Collision/Body` StaticBody3D, layer 1 / mask 0, owns two touching but
non-overlapping boxes:

- `FrontBar`: 12.8 × 4.3 × 6.4 m, centre Godot `(0,2.15,-3.2)`.
- `RearReturn`: 6.4 × 4.3 × 6.4 m, centre Godot `(-3.2,2.15,3.2)`.

The L is solid, including apparent entrances and bare holes. The rear-right notch
remains open; no bounding-rectangle collider fills it. Coping, plinth projections,
folds, canopies and fascia do not expand collision. This follows .02/.04's exterior
scope, not .01's wall-span collision. Do not use these prefabs for interior traversal.

All three leaf shapes and six window shapes are disabled and fitting bodies have
layer 0 through saved fitting-level editable overrides. Shared prefabs and imported
visual children are untouched. No door operation, interaction or authority rule is added.

Native headless tests query the **actual fitted prefab**: four exterior rays hit the
shell; side bypass, two notch approaches and vertical notch ray are clear; capsules
(radius .38 m / height 1.8 m) overlap each arm once, remain clear in the notch/front
walkway, and overlap both same-owner shapes at their seam. These are bounded public
physics-query checks, not production actor movement, transport or world-placement proof.

## Validation and visual evidence

[`validation.json`](city_small_shop_shells_03-evidence/validation.json) records:

- **6,420 triangles; 3,284 source vertices; 3,600 exported split vertices; 40 meshes /
  40 surfaces; five materials; 16 mounts plus one root; 114,228-byte GLB.**
- Zero degenerate source faces, raw GLB triangles or non-manifold edges. Closed,
  consistently wound components have positive signed volume.
- Finite geometry, unit-length source corner/exported normals, consistent raw index
  winding, applied mesh transforms, exact collection membership and metre bounds pass.
- Nine independent notch interior samples cast through all 40 source meshes: **360
  vertical-ray exclusions** confirm no accidental rectangular roof/surface spans it.
- Fresh-process saved-source reexport is **byte-identical** to committed GLB, SHA-256
  `e7996c135f617517e4c075000b7bdf211b30c850d5ba5a606510930378f2f887`.
  Regenerating the `.blend` itself is not claimed byte-identical.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports and recursively loads actual
  resources/UIDs; both bare/inherited scene save/reload roundtrips are byte-stable.
  Measured mesh bounds agree within .001 m; fifteen fitting placements agree with
  imported markers; all fitting collision is disabled. Bounded physics checks pass.

Four lean, isolated Blender renders, all 1280×800, Cycles CPU / 32 samples / AgX:
[hero, fitted](city_small_shop_shells_03-evidence/hero.png),
[side/notch, bare](city_small_shop_shells_03-evidence/side.png),
[frontage detail, fitted](city_small_shop_shells_03-evidence/detail.png),
[47 m / 42° overhead, fitted](city_small_shop_shells_03-evidence/overhead_47m_42deg.png).
The overhead is vertical-down perspective, fixed north-up, Blender camera `(0,0,47)`,
42° **vertical** FOV. All final images were self-inspected: the L and open notch read
clearly against the sibling rectangles; roof remains quiet. A small exposed notch
coping corner found in the first render was closed and all four views rerendered.
Frontage copy remains roof-occluded overhead, so it must not carry essential navigation.
Fittings are temporary unchanged GLB imports in an unsaved render scene, never saved
into the shell source. These are not native gameplay/device screenshots.

[`manifest.json`](city_small_shop_shells_03-evidence/manifest.json) hashes every final
produced payload except itself, plus ten read-only fitting dependencies.
[`final.log`](city_small_shop_shells_03-evidence/final.log) records concise outcomes
and diagnostic classification. Full logs/retries/scratch stay outside Git in
`C:/tmp/ft/assets/city_small_shop_shells_03/`.

## Exact reproduction (Git Bash, repository root)

No live Blender/Godot or connector sessions were used. Windowed editor is unavailable;
text prefab authoring followed by headless normalization is explicitly authorized.
Headless import does not synchronize any separate open editor scene. No such scene
was touched. Project plugins initialize automatically during headless editor/checks;
no MCP requests were sent.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=C:/tmp/ft/assets/city_small_shop_shells_03
mkdir -p "$T"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_03/author.py
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_03/export.py
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_03/export.py -- "$T/reexport.glb"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_03/validate.py -- "$T/reexport.glb"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_03/render.py
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script res://tools/asset_production/city_small_shop_shells_03/check.gd -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script res://tools/asset_production/city_small_shop_shells_03/check.gd
timeout 180 "$(mise which godot)" --headless --path . --check-only --script res://tools/asset_production/city_small_shop_shells_03/check.gd
timeout 30 "$(mise which gdstyle)" --max-warnings 0 tools/asset_production/city_small_shop_shells_03/check.gd
timeout 30 "$(mise which gdstyle)" fmt --check tools/asset_production/city_small_shop_shells_03/check.gd
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python tools/asset_production/city_small_shop_shells_03/manifest.py --verify
```

For read-only review verify the manifest first, skip authoring/production export, and
reexport only to scratch. Regenerating validation legitimately changes its hash.
Use a fresh canonical checks output directory. After intentional rebuild/review,
run `manifest.py` without `--verify` to refresh the payload inventory.

### Checks and diagnostics

Final owned lint/format, explicit compilation, source/raw GLB audit, fresh reexport,
rendering, saved prefab normalization and fresh runtime checks **pass**. Canonical
production checks exit **1** solely for the known pre-existing compile failures in
five `tests/fixtures/asset_production/*.gd` scripts and formatting of
`batch_observation.gd`, integration `batch03_author.gd` and `inspector.gd`.
All **48 scripts pass lint**; this asset's checker compiles. Python tests **9/9**;
GUT **9/9**, **70 assertions**; negative-control failure detection passes. Those
unrelated files were not edited and no broad error suppression was introduced.

Headless import exits 0 with the existing plugin's untested-4.8 warning. Editor-mode
normalization exits 0 and proves stable saved bytes/UIDs, but emits known editor/plugin
shutdown **RID/ObjectDB leak diagnostics**; this is not a clean-editor-exit claim.
Separate runtime and explicit compilation exit 0 without warnings/errors. Blender
build/export/reexport/validation/render calls exit 0; the standalone version query
emitted the known one-small-block shutdown diagnostic.

Initial owned faults corrected: source marker matrix evaluation lost unsynchronized
translations (fixed before validation); visible notch coping corner gap (fixed and
rerendered); manual west fitting transform row/column spelling reversed yaw (caught
by actual imported-marker comparisons, fixed without changing UIDs); initial lint
length/complexity warnings (split physics checks into named helpers). Final checks
were rerun after corrections. No unrelated process was terminated or vendor code patched.

## Remaining acceptance

Independent source/art/prefab review; final dimensional/layout approval; actual actor
movement/aim, seam/corner clearance and combat visibility; authoritative/predicted/
multiplayer behavior; district placement/derived data; commercial artwork; repeated
instance GPU/frame-pacing, packaged build and sustained Deck/device validation remain
**pending**. The notch is a geometric opening, not an approved route or spawn zone.
Bare apertures are not traversable under the exterior collider. Roof access, interior
play, animated doors, destruction and lights are out of scope. This delivery does not
mark the shared register READY or authorize world placement.
