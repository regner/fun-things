# d06_commercial_graphics.04 — Passage wayfinding face

9 October 2026. **Artwork/material/linked-prefab candidate delivered; independent review,
world/gameplay-camera and target-device acceptance pending.** Production authority:
[commission](commission.md), current per-record task and supervisor approval. Producer:
assigned lane worker on `lane/a-d06gfx`. Family: [Signal Row graphics](../d06_commercial_graphics.md).
Earlier deliveries: [hall](d06_commercial_graphics_01.md), [shops](d06_commercial_graphics_02.md),
[posters](d06_commercial_graphics_03.md). No shared hardware or earlier delivery was changed.

## Design, provenance and approved scope

One **rightward PASSAGE** face: a broad cyan open doorway with a dark negative-space opening,
a large ivory right arrow, a small magenta threshold, and supplemental original lettering.
The symbol pair, rather than the word, conveys passage/direction in close views. The layout
is distinct from the hall clock-ring, shop tag/bowl/disc and poster burst/tickets, while
retaining their exact palette and rounded path lettering:

| Role | sRGB |
| --- | --- |
| Quiet field / doorway opening | Petrol `#102C3C` |
| Doorway | Cyan `#45DFE5` |
| Arrow / supplemental copy | Warm ivory `#F6F1DC` |
| Threshold accent | Magenta `#F54BBA` |

Supervisor approved this provisional graphic/copy and explicitly resolved the geometry
interface: **reuse unchanged `city_sign_supports_01`, with a saved face-only material override;
no redundant .blend, GLB or coplanar carrier**. Its original Blender source → explicit GLB →
linked prefab chain satisfies the applied-artwork geometry requirement. There is intentionally
no per-ID `.blend` or `export.py`. Existing owner audits/exporter are reused read-only, with
fresh outputs only in scratch. One direction only; no mirrored variant, interaction, navigation
logic, lighting, collision, sign system, building dimensions or world placement is introduced.

The artwork is explicitly authored Python/Pillow construction, supersampled 3× and filtered
once. No image generation, downloads, real brands, external fonts or attribution dependencies.
The `.01` author script owns the original palette/letter skeletons; `.02` owns the smooth-path
canvas and G glyph. This recipe reuses them without changing their files. Copy remains
provisional, not final Regner naming approval. District identity/street references constrain
frontage accents, quiet roof centres/roads and clear passage mouths; no dimensions are inferred
from concept images.

**This small vertical panel is supplementary wayfinding, not an essential overhead route cue.**
The supervisor approved that limitation: an independent visible architectural/route cue must
carry overhead navigation. No such cue or route is created by this record.

## Source, outputs and inherited dimensions

- Artwork recipe: `tools/asset_production/d06_commercial_graphics_04/author.py`.
  Python **3.14.2**, Pillow **12.3.0**.
- Runtime texture: `art/textures/environment/d06_commercial_graphics_04/passage_albedo.png`
  and `.import`; **1220 × 820 RGB**, opaque sRGB albedo, aspect **61:41**.
- Material: `art/materials/environment/d06_commercial_graphics_04/passage.tres`.
  White albedo multiplier, roughness **0.56**, metallic **0**, opaque/backface-culled,
  no emission. Linear mipmapped filtering (default enum 3), clamp/no repeat, identity UV
  scale/offset. Lossless import, real imported mipmaps enabled, automatic 3D compression
  changes disabled. No additional maps or embedded images.
- Prefab: `scenes/prefabs/environment/d06_commercial_graphics_04.tscn`, inheriting the
  complete unchanged `scenes/prefabs/environment/city_sign_supports_01.tscn`.
- Existing source: `art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend`.
  Collection `export_city_sign_supports_01`, root `CitySignSupports01`, 12 mesh children.
- Existing linked export: `art/models/environment/city_sign_supports_01/city_sign_supports_01.glb`
  and its unchanged `.import`. See the [hardware handoff](city_sign_supports_01.md) and
  [bounded engine integration](batch_01-integration.md).

| Inherited interface | Measurement / convention |
| --- | --- |
| Whole Godot X/Y/Z | **1.400 × 1.000 × 0.100 m** |
| Godot local AABB | min **(-0.700, -0.500, -0.100)**; max **(0.700, 0.500, 0)** m |
| Pivot | Wall-contact centre **(0,0,0)**, not ground-centred |
| Artwork face | **1.220 × 0.820 m**, Godot **Z=-0.088 m**, rounded 0.040 m corners |
| Safe copy | Centred **1.140 × 0.740 m**; outer 40 texture pixels remain petrol |
| UV0 | U toward Blender -X; V toward +Z; glTF flips V storage |
| Image orientation | Ordinary top-left PNG; text/arrow upright and unmirrored |
| Mounting proposal | Centre **1.60 m** above ground on a vertical wall, inherited proposal |
| Tolerances | Whole bounds ±0.001 m; owner's source/GLB audit enforces 0.000001 m |

No new rig, clips, sockets or LOD. Shared hardware import settings remain unchanged.
Collision-free decoration: the existing facade owns blocking collision. Place one complete
variant, not another panel at the same transform; keep its 0.10 m projection outside passage
clearance. These are attachment constraints, not accepted world placement or movement tests.

## Saved override and identity contract

Exactly one saved override:

`Visuals/Model/CitySignSupports01/artwork_carrier:surface_material_override/0`

The original slot is checked as `sign_face`. Carrier rear/sides retain `mount_metal`;
all other surfaces and geometry remain unchanged. Inherited `Visuals/Model` remains the
identity-transform linked GLB. There is no embedded render mesh, global material override,
runtime appearance script or copied collision. Existing hardware's double-sided materials
are preserved; only the new artwork material is backface-culled.

Supervisor approved this **saved editable-child surface override** as the same narrow exception
used for earlier family graphics, not a project-wide replacement for wrapper appearance APIs.
The wrapper retains base-prefab inheritance and imported carrier `unique_id=1321061654`, with
parent-ID ancestry `(728591687, 1941652775)`. Two load/pack/save cycles and an additional
normalization invocation preserve scene/material bytes exactly. The checker reuses `.03`'s
hierarchy and roundtrip helpers but overrides its entrypoint to inspect/save only this panel.
Future shared-hardware hierarchy/reexport changes must recheck the path and imported identities.
This pass proves the current unchanged GLB, not arbitrary future migrations.

Scene/material UIDs are inline, texture UID is in `.import`, and checker UID is in `.gd.uid`;
the pinned engine does not create separate `.tscn.uid` or `.tres.uid` files. Live editor/MCP
mutations were prohibited by the task. The text-authored wrapper was normalized only by
isolated pinned headless Godot. No owner's live session was touched, refreshed or saved, and
no separately open scene is claimed synchronized. The existing plugin starts its own local
server during checks; no MCP requests were made.

## Evidence and measured validation

[Hero](d06_commercial_graphics_04-evidence/hero.png),
[side](d06_commercial_graphics_04-evidence/side.png),
[doorway/inset detail](d06_commercial_graphics_04-evidence/detail.png),
[47 m / 42° overhead](d06_commercial_graphics_04-evidence/overhead_47m_42deg.png).
All four are isolated **Blender** renders, **1280×800**, Cycles CPU **32 samples**, AgX.
Exact cameras/lights are in `preview.py`. Shared source is opened read-only; transient material
assignment and mounting translation are never saved or exported.

Self-inspected the runtime PNG and all four renders. Hero/side show upright, unmirrored copy,
an unambiguous right arrow, an open-door silhouette, complete frame and clean inset seating.
Detail deliberately crops into the doorway, threshold and frame; it is not a whole-panel
view. Hardware is not recoloured by the artwork. No bloom, alpha overlays or fine surface noise.

Overhead is vertical/north-up at Blender **(0,10,47)**, vertical FOV **42°**, with the unscaled
vertical panel temporarily mounted at **(0,0,1.6)**. There is no camera-facing tilt or enlargement.
The panel is only approximately **31×6 pixels**, with its artwork thinner still. **Neither the
arrow direction, doorway nor lettering is reliably identifiable at this camera scale.**
Increasing texture resolution cannot fix foreshortening or expose a face occluded by roofs.
Independent architectural/route cues, actual renderer and populated-world placement must
establish gameplay navigation. No overhead route-readability acceptance is claimed.

[validation.json](d06_commercial_graphics_04-evidence/validation.json) records:

- Reused panel: **1,380 source vertices, 1,792 GLB vertices, 2,720 triangles,
  12 meshes, 13 surfaces**, four unchanged source hardware materials.
- **Zero degenerate source faces/GLB triangles, zero non-manifold edges**, positive volume,
  outward consistent winding, unit source corner/export normals, applied transforms/metres.
- Existing source audit plus independent binary accessor audit both pass, including **36**
  actual front-face UV samples, expected axis conversion, pivot, bounds and no studio export.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**. Fresh saved-source
  shared export is **byte-identical**, **75,768 bytes**, SHA-256
  `5f54105825e00bb73c038bed252910abec548ad1beb81603b2713c2c69796e0b`.
- Godot **4.8.dev7.official.c971f93e7**: complete dependency chain loads; hierarchy/transforms
  and all 12 imported mesh resources match the base; one front-only override; inherited bounds,
  no collision, identity UVs, real imported mipmaps and repeatable resource/scene normalization.
  Independent non-editor load has **no WARNING/ERROR/SCRIPT ERROR** diagnostics.
- **Four artwork tests pass**: committed PNG byte reproduction/opaque dimensions, independent
  safe-border checks, right-arrow/open-door/threshold pixels, and symbol separation after
  **61×41** face downsampling. This front-facing texture proxy is not an overhead gameplay test.
- Pinned gdstyle **0.3.0** lint/format pass. Full production suite passes: owned formatting,
  style and explicit compilation (including this checker), **nine Python tool tests**,
  **23 GUT tests / 196 assertions**, import and the intentional-negative diagnostic check.

[manifest.json](d06_commercial_graphics_04-evidence/manifest.json) hashes every produced payload
except itself and uncommitted Python caches. Shared geometry/tool dependencies are hashed
separately in validation. [final_checks.log](d06_commercial_graphics_04-evidence/final_checks.log)
retains concise actual outcomes/diagnostics. Full logs, fresh exports and intermediate receipts
stay outside Git in `C:/tmp/ft/assets/d06_commercial_graphics_04/`.

## Exact reproduction

From this worktree root with pinned tools installed:

```sh
N=d06_commercial_graphics_04
python tools/asset_production/$N/author.py
python -m unittest discover -s tools/asset_production/$N -p 'test_*.py' -v

timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/validate.py

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/preview.py

timeout 300 "$(mise which godot)" --headless --editor --path . --import
# Only normalize when intentionally saving owned resources.
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/$N/check_prefab.gd -- --normalize
# Register newly saved UIDs before independent runtime validation.
timeout 300 "$(mise which godot)" --headless --editor --path . --import
timeout 180 "$(mise which godot)" --headless --path . \
  --script res://tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" check tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" fmt --check tools/asset_production/$N/check_prefab.gd
# Use a fresh output directory for each full suite run.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/$N/checks_reproduce
python tools/asset_production/$N/manifest.py
```

`validate.py` refreshes the source/export portion of validation.json. This retained candidate
also includes actual engine/normalization and production receipts; retain scratch `prefab.json`
before another checker invocation overwrites it and reassemble those receipts before writing
new evidence. The hardware decoder is top-level rather than a callable API: its sole evidence
path assignment is redirected in memory with an exact-match guard, keeping every assertion
and its original `__file__`. No shared file or geometry-validator copy is written. The hardware
owner's established explicit export settings/selection filter remain intact. `manifest.py --write`
explicitly refreshes hashes after intentional updates; default invocation only verifies.

## Diagnostics and remaining gates

- Initial owned lint flagged one 103-character constant; split its string declaration and
  reran pinned lint/format successfully. Initial default texture import had mipmaps disabled;
  configured the owned import before normalization, reimported and verified real mipmaps.
- Headless normalization exits 0 and passes resource/byte/UID checks but reports the existing
  addon 4.8-versus-4.7 warning, scan-aborted warning and editor shutdown RID/ObjectDB leaks.
  These are not suppressed or called a clean editor exit. Full imports complete with only
  the addon-version warning; independent non-editor load and full production suite pass.
- Blender rendering reports pinned `Material.use_nodes`/`World.use_nodes` future-deprecation
  warnings and exits 0. Source/export audits exit 0 without topology, export or audio failures.
- No known compile/style failure was ignored. No runtime movement/network behavior changed.

Pending: independent technical/art review, final copy selection, valid wall/passage placement
with a separately visible architectural/route cue, actual populated target-renderer/gameplay
visibility and occlusion, future hardware-reexport identity retention, packaged filtering,
repeat-placement cost and sustained Deck performance. No world placement, navigation,
collision, simulation or multiplayer acceptance is authorized by this artwork delivery.
