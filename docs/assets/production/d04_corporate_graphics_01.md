# d04_corporate_graphics.01 — Large facade panel art

**Artwork, original full-size Blender carrier, linked prefab and bounded producer checks
delivered; independent review and world/gameplay/device acceptance pending.** Producer:
commissioned implementation worker on `lane/a-d04g`; supervisor retains acceptance authority.
The [commission](commission.md) supersedes the earlier concept-only stage. References:
[family brief](../d04_corporate_graphics.md), [Glassward identity](../../concepts/world-v1/stage-03-district-identities/README.md#glassward--the-skyline-presses-in),
[downtown grid](../../concepts/world-v1/stage-04-streets/README.md#owner-refinement--a-gridded-high-rise-centre),
[asset workflow](../../assets.md), and [tower dimensions](d04_towers_01.md).
No shared brief, register, world placement, gameplay or earlier asset was changed.

## Design, provenance and approved carrier decision

**TOMORROW / HAS BEEN / RESCHEDULED.** Original continuous-stroke capital lettering,
a pair of cyan offset appointment corners and one small magenta appointment marker on
an overwhelmingly quiet indigo field. Warm ivory carries the main copy. The concept's
self-important office humour is decorative, not required navigation. Copy and the
abstract emblem are fictional/provisional; no real company identity or final naming
choice is implied. No downloaded font, texture, mesh, image-to-mesh or generated image.
Every line and letter is explicitly authored in `artwork.py` using Python/Pillow.

The existing `city_sign_supports_01` is a **1.40 × 1.00 m** poster/civic panel, not a
large facade carrier. The supervisor explicitly rejected enlarging that panel through
root/placement scale because it would enlarge its bevels, bolts and depth. Instead the
supervisor approved **one original approximately 5.6 × 4.0 m carrier** under this asset,
with thin flush mounting, real-scale frame details and a dedicated UV-validated face.
This is not a duplicate small-panel model. Later artwork may reuse this carrier unchanged.
No editable-imported-child exception is needed: this new GLB uses a saved external-material
import remap on `sign_face`, with an ordinary noneditable linked prefab.

### Family graphic grammar

| Role | sRGB | Treatment |
| --- | --- | --- |
| Field | `#15263D` | Quiet indigo, over 80% of pixels |
| Primary accent | `#57D9E5` | Cyan corner emblem and subordinate line |
| Copy | `#F6F1DC` | Warm ivory |
| Rare accent | `#EB62B7` | One small magenta marker, less than 0.3% of pixels |

Keep later family artwork restrained, with generous margins, clear hierarchy and few
large accents. The palette and glyph recipe are discoverable in `artwork.py`; the new
carrier's dimensions and face interface below are reusable, not a demand for another
mesh. No neon/bloom dependency, light node, alpha overlay, grime or dense microcopy.

## Dimensions and mounting

All dimensions are **provisional authored values**, not inferred from concept images or
approved site geometry. They follow the supervisor's large-panel direction and the tower
family's 6 m lobby / 3.6 m floor rhythm. Proposed mounting centre is **Y=9 m**, giving
lower/upper edges **7/11 m** within the first broad facade group above the lobby. The
5.6 m width fits a nominal 6 m facade allocation without changing tower geometry. Actual
flat-wall availability, window conflicts and facade attachment remain placement review.
Do not scale the prefab, place it over a passage/window or infer an automatic tower socket.

| Contract | Metres / value |
| --- | --- |
| Overall Godot X/Y/Z | **5.60 × 4.00 × 0.14** |
| Godot AABB | min **(-2.8,-2,-0.14)**, max **(2.8,2,0)** |
| Pivot | Wall-contact centre `(0,0,0)`, not a ground pivot |
| Front | Blender +Y maps to Godot -Z; Blender +Z maps to Godot +Y |
| Back tray | 5.60 × 4.00, depth 0.086, front at Z=-0.106 |
| Concealed mounting rails | Two 4.80 × 0.10 strips; wall contact Z=0 |
| Frame lip | Godot Z=-0.140; actual bevels 0.018–0.020 |
| Artwork carrier | **5.36 × 3.76**, closed 0.030-thick sheet |
| Artwork plane | Godot Z=-0.128; recess 0.012 behind frame lip |
| Face bevel | 0.006; mapping domain includes this narrow clipped edge |
| Safe content rectangle | Centred **4.96 × 3.36** (60 px margins, 0.20 m each edge) |
| Bounds/axis tolerance | ±0.00001 in source/binary checks; engine approximate comparison |

Metre units and applied transforms. Root and both meshes are identity; no compensating
prefab rotations/scales. The frame uses joined closed manufactured components rather than
Boolean union geometry. Their seams and concealed overlaps are intentional.

**Visual-only above-head facade element.** The proposed lower edge is 7 m, well above
the 2.5 m rule. Structural blocking remains with the wall; no collider, interaction,
navigation or gameplay state is added. Ground-level/freestanding installation is not this
prefab's contract and requires an intentional thin collider and movement checks. No
interiors, destruction, sockets, animations, rigs or runtime-created scene hierarchy.

## Source, exports and face material

- Source: `art/source/models/environment/d04_corporate_graphics_01/d04_corporate_graphics_01.blend`.
- Collection: `export_d04_corporate_graphics_01`; root: `D04CorporateGraphics01`.
- Meshes: `D04CorporateGraphics01_Hardware` and `D04CorporateGraphics01_ArtworkCarrier`.
  Mesh datablock names append `_Mesh`. Preview camera/lights are never saved/exported.
- GLB: `art/models/environment/d04_corporate_graphics_01/d04_corporate_graphics_01.glb`
  with pinned-engine `.import`. Shared `tools/assets/blender/export_settings.json` is
  applied explicitly; static animations/skins disabled. No embedded images/textures.
- Texture: `art/textures/environment/d04_corporate_graphics_01/tomorrow_albedo.png`,
  **1608 × 1128 RGB**, 67:47, 300 px/m; adjacent `.import` has lossless compression,
  mipmaps enabled and automatic 3D compression switching disabled.
- Material: `art/materials/environment/d04_corporate_graphics_01/tomorrow.tres`:
  opaque sRGB albedo, white multiplier, metallic 0, roughness 0.56, backface culled,
  linear mipmapped filtering, clamp/no repeat, no emission/normal/ORM maps.
- Prefab: `scenes/prefabs/environment/d04_corporate_graphics_01.tscn`.
  `Visuals/Model` is an identity-transform GLB instance, no editable children or mesh copies.
- Tools: `tools/asset_production/d04_corporate_graphics_01/` contains `artwork.py`,
  `author.py`, `export.py`, `validate.py`, `preview.py`, `test_artwork.py`,
  `check_prefab.gd` (+ generated `.uid`) and `record.py`.

Hardware slots: `glassward_frame`, `recess_gasket`, `mount_metal`.
Artwork-carrier slot **0 `sign_face`** owns only the front; slot **1 `mount_metal`** owns
back/bevel/sides. `.glb.import` remaps only `sign_face` to `tomorrow.tres`; changing artwork
must not replace the whole material set. Source neutral face plus external runtime art
is intentional. UV0 `UVMap`: Blender **U=(2.68-X)/5.36, V=(Z+1.88)/3.76**;
exported glTF flips V to top-origin texture coordinates. Front screen-right is -X.
Decoded front positions/normals/UVs prove upright and unmirrored mapping. No tiling.
Default automatic import LOD/tangent/shadow-mesh settings remain; no performance budget
or LOD/readability acceptance is inferred.

## Evidence and measured validation

[Hero](d04_corporate_graphics_01-evidence/hero.png) ·
[side](d04_corporate_graphics_01-evidence/side.png) ·
[face/frame detail](d04_corporate_graphics_01-evidence/detail.png) ·
[47 m / 42° overhead](d04_corporate_graphics_01-evidence/overhead_47m_42deg.png).
All four and the runtime artwork PNG were personally inspected. Hero/side show upright
copy, generous dark margins, a thin frame and the correct small magenta accent. Detail
shows clean artwork seating and smooth edges. The vertical face is a small strongly
foreshortened strip at gameplay scale: **full copy is not reliably readable**. Emblem and
contrasting line survive only as decoration. Architecture/world cues must carry essential
navigation; no added tilted/roof-facing sign disguises this limitation.

Isolated Blender Cycles CPU, 32 samples/denoising, AgX, 1280×720, PNG compression 95,
dither disabled. Overhead is vertical-down/north-up, 42° vertical FOV, camera Blender
`(0,10,47)` and panel temporarily translated to `(0,0,9)` without rotation/scale. This is
a mount proposal rendered in isolation, not a saved placement or Godot visual capture.
All four images are below 400 KB. Exact studio values are in `preview.py`.

[validation.json](d04_corporate_graphics_01-evidence/validation.json) records:

- **848 source vertices, 1,007 split GLB vertices, 1,660 triangles, two meshes, five surfaces**.
- **Zero nonmanifold source edges, degenerate source faces or exported triangles**;
  positive closed-solid volume, consistent winding, finite coordinates, unit normals.
- Fifteen independent front ray tests hit the artwork before any backing hardware.
- Actual GLB buffer decoding validates bounds, normals/winding and front UVs, not just
  exporter metadata. Applied weighted normals have less than 0.001 direction error at
  the face corners; unit-length tolerance remains 0.00001.
- Fresh saved-source reexport is **byte-identical**, **47,136 bytes**, SHA-256
  `d3fff40c9b3e1c9c17db86cd96fcf85302cebdedf7f7800537f16f107753209b`.
- Four artwork tests pass: aspect/opaque format, safe margins, sparse palette/emblem
  pixels, and fresh scripted PNG byte identity.
- Godot **4.8.dev7.official.c971f93e7** final import has no ERROR/SCRIPT ERROR lines.
  Fresh non-editor load checks linked geometry, bounds, no collision, dependencies,
  exact texture size/mipmap/filter settings and exactly one imported artwork surface.
- Two normalized save/reload cycles preserve scene bytes/UIDs/node identities, including
  after the last reexport. Scene/material UIDs are inline, texture/model UIDs in `.import`;
  the engine does not generate separate `.tscn.uid`/`.tres.uid` files.
- Pinned gdstyle 0.3.0 owned GDScript format and zero-warning lint pass. No global
  production suite was run, per owner decision 52.

[manifest.json](d04_corporate_graphics_01-evidence/manifest.json) hashes every produced
payload except itself; [final.log](d04_corporate_graphics_01-evidence/final.log) is the only
retained command summary. Scratch exports/retries/logs stay in
`C:/tmp/ft/assets/d04_corporate_graphics_01/`, not the repository.

## Exact reproduction

Run from the worktree root in Bash, with Python/Pillow 12.3.0 available:

```sh
NID=d04_corporate_graphics_01
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export PYTHONIOENCODING=utf-8
python tools/asset_production/$NID/artwork.py
python -m unittest discover -s tools/asset_production/$NID -p 'test_*.py' -v
# author.py deliberately rebuilds the owned source and explicit GLB.
for script in author validate preview; do
  timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python tools/asset_production/$NID/$script.py
done
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . \
  --script res://tools/asset_production/$NID/check_prefab.gd -- --normalize
timeout 300 "$GODOT" --headless --path . --import \
  > C:/tmp/ft/assets/$NID/import-final.log 2>&1
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/$NID/check_prefab.gd \
  > C:/tmp/ft/assets/$NID/prefab.log 2>&1
"$GDSTYLE" fmt --check tools/asset_production/$NID/check_prefab.gd
"$GDSTYLE" --max-line-length 100 --max-warnings 0 tools/asset_production/$NID/check_prefab.gd
python tools/asset_production/$NID/record.py
```

`validate.py` writes a fresh scratch export and source/binary validation receipt. Export
only: load the saved `.blend` after `--factory-startup` with the same pinned/audio/timeout
flags, use `--python tools/asset_production/$NID/export.py -- C:/tmp/ft/assets/$NID/export-only`.
For a new producer receipt, redirect the unit-test output to scratch `artwork-tests.log`,
run the engine steps, update this handoff/final log, and use `record.py --write` last.
Without `--write`, `record.py` only verifies the current manifest. Rebuilding `.blend`
preserves the recipe, not binary-identical Blender serialization. Source validation
replaces its receipt, so regenerate the combined receipt/manifest after revalidation.

## Diagnostics and remaining acceptance

Initial self-review caught a backing gasket obscuring the artwork. Its front was moved
behind the face, and 15 front-visibility rays now protect that correction. An initial
normal-direction expectation was tighter than Blender's applied weighted-normal corner
influence; the direction check now uses 0.001 while preserving strict unit-length tests.
One 101-character GDScript constant was split to satisfy the pinned 100-character limit.
These owned faults are corrected, not suppressed failures.

Headless editor normalization assertions pass and exit 0, but the editor shuts down with
scan-aborted, RID/ObjectDB leak diagnostics (168 objects), matching the known documented
asset-tool pattern; this is **not a clean editor shutdown claim**. No independent empty
baseline was rerun. Final ordinary import and non-editor dependency load are separately
error-free. Import retains the addon's known 4.8-versus-4.7 compatibility warning. Blender
only emits its future `Material.use_nodes` deprecation notice; the pinned tasks exit 0.
Live MCP/windowed sessions were prohibited and never accessed. Direct text creation plus
isolated headless normalization is the required fallback, not synchronization of an
owner's separate open editor scene.

Pending: independent art/technical review; final copy/dimension selection; actual flat-wall
mounting and facade-grid fit; renderer/gameplay-camera, tower occlusion and populated-world
visibility; packaged target filtering/LOD, repeated-placement profiling and Deck performance.
No actor/car/network or world-placement test is claimed for this non-colliding decorative
asset. No TODO, tracker stage or whole-register production acceptance was closed.
