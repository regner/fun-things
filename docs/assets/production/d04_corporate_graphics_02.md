# d04_corporate_graphics.02 — Low directory face

**Original artwork, face-only material and source-linked inherited prefab delivered;
bounded producer checks pass. Independent review and world/gameplay/device acceptance
remain pending.** Producer: commissioned implementation worker on `lane/a-d04g`;
supervisor retains acceptance authority. The [commission](commission.md) supersedes the
historical concept-only stage. References: [family brief](../d04_corporate_graphics.md),
[Glassward identity](../../concepts/world-v1/stage-03-district-identities/README.md#glassward--the-skyline-presses-in),
[downtown grid](../../concepts/world-v1/stage-04-streets/README.md#owner-refinement--a-gridded-high-rise-centre),
[earlier corporate panel](d04_corporate_graphics_01.md), and
[shared low-panel hardware](city_sign_supports_02.md).

## Design and provenance

**DIRECTORY / A TOMORROW / B LATER.** Two fictional office entries continue the facade
panel's self-important scheduling joke. A/B are decorative suite labels, not actual
building destinations or an authoritative navigation interface. Copy remains provisional;
no final company naming decision, real brand, downloaded font/image/mesh, image-to-mesh,
emission or gameplay interaction is introduced.

The original offset appointment-corner emblem, continuous-stroke capitals and exact
Glassward palette are reused from `.01`: indigo `#15263D`, cyan `#57D9E5`, warm ivory
`#F6F1DC`, rare magenta `#EB62B7`. The field occupies **89.35%** of exact-color pixels;
the single magenta appointment marker occupies **0.079%**, excluding antialiasing.
Generous margins and two widely separated entries avoid dense advertising noise. A thin
cyan divider is optional close-view detail; neither it nor the copy must survive overhead.

`author.py` is the reproducible Python/Pillow source. It imports the sibling's original
palette/glyphs and reuses the existing `d06_commercial_graphics_02` supersampled Canvas,
with a private palette/glyph module instance. I/Y use that tool's original matching 4×6
continuous skeletons. No shared source is edited. The earlier `.01` handoff contains no
stale pending item for this asset, so no sibling document/manifest update is necessary;
its existing manifest was verified unchanged. No register, shared brief, TODO or world
scene was changed.

## Reused hardware, dimensions and collision

**No new carrier .blend or GLB.** The existing `city_sign_supports_02` already supplies the
correct low freestanding panel; reproducing its geometry would violate the standing reuse
rule. This artwork inherits its prefab unchanged and changes only the front material.
These dimensions are inherited **provisional authored values**, not an accepted site plan:

| Contract | Value |
| --- | --- |
| Overall Godot X/Y/Z | **1.60 × 1.35 × 0.40 m** |
| AABB | min **(-0.80,0,-0.20)**, max **(0.80,1.35,0.20)** m |
| Pivot / ground datum | `(0,0,0)`, centred between feet |
| Artwork face | **1.44 × 0.39 m**, height **0.88…1.27 m** |
| Front plane | Godot **Z=-0.071 m**, recessed 0.009 m behind frame |
| Safe copy rectangle | **1.38 × 0.33 m**, 30-pixel / 0.03 m minimum margins |
| Front / up | Blender +Y/+Z maps to Godot -Z/+Y |
| Transform contract | Metres; root, meshes and `Visuals/Model` at identity |
| Bounds / coordinate tolerance | ±0.001 m / ±0.00001 m |

Source: `art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend`.
Collection `export_city_sign_supports_02`, root `CitySignSupports02`, mesh children
`CitySignSupports02_Hardware` and `CitySignSupports02_ArtworkCarrier`.
Export: `art/models/environment/city_sign_supports_02/city_sign_supports_02.glb`, using
`tools/assets/blender/export_settings.json` through its existing `export.py`.
Shared `.blend`, GLB, import metadata, base prefab and tool dependencies are hash-protected
before/after validation and after final import. No embedded texture, copied mesh, corrective
scale/rotation, runtime-created hierarchy, rig, animation, socket or destruction state.

Inherited `Collision/Body/Shape`: one **1.60 × 1.35 × 0.40 m BoxShape3D** at
**(0,0.675,0)**, StaticBody3D layer **1**, mask **0**. This is the carrier's intentional
full-envelope collider, including its visually open under-panel gap. Artwork adds no
second collider and changes no physics. Hardware acceptance owns that simplification.
Keep the sign outside foot passages, vehicle swept paths and junction sightlines; no
placement is delivered. Production actor/replay checks in the hardware handoff are
historical evidence, not rerun or expanded claims here.

## Runtime artwork and prefab

- `art/textures/environment/d04_corporate_graphics_02/directory_albedo.png`:
  **1440 × 390 RGB**, aspect **48:13**, **1000 px/m**, opaque sRGB albedo. Its pinned-engine
  `.import` uses lossless compression, mipmaps enabled, automatic 3D compression switching
  disabled. No alpha, normal, ORM or emission maps.
- `art/materials/environment/d04_corporate_graphics_02/directory.tres`:
  `glassward_directory`, white multiplier, metallic 0, roughness **0.56**, backface culled,
  linear mipmapped filter, clamp/no repeat, UV scale 1/offset 0, no emission. Matching `.01`.
- `scenes/prefabs/environment/d04_corporate_graphics_02.tscn` inherits
  `city_sign_supports_02.tscn`. Its inherited `Visuals/Model` remains the identity GLB instance.
  Exactly one saved override: `CitySignSupports02_ArtworkCarrier` **surface 0 `sign_face`**.
  Surface 1 `mount_metal` retains sides/back; all hardware materials remain unchanged.
- This is the authorized **static artwork-on-reused-carrier editable-child exception** in
  [the prefab contract](../../assets.md#prefabs-and-authored-placement). No new appearance API
  is added. Two normalized scene/material save/reload cycles were byte-stable, preserving
  UIDs and saved node identities; a separate non-editor process then loaded the result.
- UV0 `UVMap`: Blender **U=(0.72-X)/1.44**, **V=(Z-0.88)/0.39**; exported glTF V is top-origin.
  Front screen-right is -X. Source and decoded binary UVs/normals prove upright, unmirrored
  artwork. The hardware's rounded corners clip only the blank field, outside safe copy.
- Prefab UID `uid://b70tbtytawmy5`; material UID `uid://c5ins07wluig6`; texture UID
  `uid://bum4elph54wi7`; inherited GLB UID `uid://bcgx64ss75j2s`. Text scene/material UIDs
  are inline; Godot creates no separate `.tscn.uid`/`.tres.uid`. The checker `.gd.uid` is kept.
  Default carrier LOD/tangent/shadow import settings are unchanged; no budget is inferred.

## Evidence and measured checks

[Hero](d04_corporate_graphics_02-evidence/hero.png) ·
[side](d04_corporate_graphics_02-evidence/side.png) ·
[face/frame detail](d04_corporate_graphics_02-evidence/detail.png) ·
[47 m / 42° overhead](d04_corporate_graphics_02-evidence/overhead_47m_42deg.png).
All four and the runtime PNG were personally inspected. Close views show upright entries,
clean face seating, coherent family emblem and ample blank space. Overhead shows a tiny,
foreshortened strip: **copy and suite labels are not gameplay-readable**. It is decorative
forecourt identity, never the only required route cue. No tilted face or enlarged duplicate
hardware disguises the limitation.

Isolated Blender **5.2.2 LTS**, build `d13f752e3b9c`; Cycles CPU, 32 samples/denoising,
AgX, **1280×720**, RGB PNG compression 95, no dithering. Images are 6–185 KB. `preview.py`
opens the unchanged source and assigns the artwork temporarily without saving. Overhead
is vertical-down/north-up perspective, **47 m height / 42° vertical FOV**, camera Blender
`(0,10,47)`; the carrier remains unscaled at ground datum. This is isolated source evidence,
not Godot visual, district-lighting, actor-occlusion or approved placement evidence.

[validation.json](d04_corporate_graphics_02-evidence/validation.json) records:

- **2,448 triangles; 1,244 source vertices; 1,596 split GLB vertices; two meshes; five surfaces**.
  These are the reused hardware's measured counts, not newly delivered geometry.
- **Zero nonmanifold source edges, degenerate source faces or exported triangles**;
  positive solid volume, consistent winding, finite positions and unit source/export normals.
- Actual binary positions/normals/UVs, bounds, material membership, transforms and collection
  membership pass the existing hardware audit. `validate.py` redirects only its two output
  paths to scratch; every original assertion remains intact and shared bytes stay unchanged.
- Fresh saved-source export is **byte-identical**, **70,712 bytes**, SHA-256
  `022dd559334d79c482182083be775c692ab4adf2a5277d3fb7ca7ec266ec76b7`.
- **Four artwork tests pass**: opaque aspect, independent safe margins, family palette/
  sparse accent/two-row hierarchy, and committed PNG byte reproduction.
- Pinned Godot **4.8.dev7.official.c971f93e7** import and separate non-editor load have
  **no ERROR/SCRIPT ERROR lines**. Actual texture mipmaps/filtering and exactly one front
  override pass; hierarchy, transforms, mesh resource references and inherited collision
  match the base prefab. Rays prove centre blocked at Y=0.7, X=0.9 bypass clear, Y=1.6 clear.
- **Two byte-stable scene/material roundtrips** pass, including saved IDs/UIDs. Final runtime
  and normalization hashes match the retained files. No copied render mesh or replacement hardware materials.
- Pinned **gdstyle 0.3.0** owned GDScript format check and zero-warning 100-character lint pass.
  No global `production_checks.py` run, per owner decision 52.

[manifest.json](d04_corporate_graphics_02-evidence/manifest.json) hashes every produced
payload except itself and separately identifies unchanged dependencies.
[final.log](d04_corporate_graphics_02-evidence/final.log) is the sole retained command summary.
Scratch exports and full process logs stay under `C:/tmp/ft/assets/d04_corporate_graphics_02/`.
Tools reuse existing canvas, low-panel audit, prefab/roundtrip/query helpers and manifest
inventory rather than introducing another shared framework. Helper chains are explicit in
source and their hashes are in the receipt; no shared tooling edits were authorized.

## Exact reproduction

Run from the worktree root in Bash with Python/Pillow **12.3.0** available:

```sh
NID=d04_corporate_graphics_02
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export PYTHONIOENCODING=utf-8
mkdir -p C:/tmp/ft/assets/$NID
python tools/asset_production/$NID/author.py
python -m unittest discover -s tools/asset_production/$NID -p 'test_*.py' -v \
  > C:/tmp/ft/assets/$NID/artwork-tests.log 2>&1
for script in validate preview; do
  timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python tools/asset_production/$NID/$script.py
done
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . \
  --script res://tools/asset_production/$NID/check_prefab.gd -- --normalize \
  > C:/tmp/ft/assets/$NID/normalize.log 2>&1
timeout 300 "$GODOT" --headless --path . --import \
  > C:/tmp/ft/assets/$NID/import-final.log 2>&1
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/$NID/check_prefab.gd \
  > C:/tmp/ft/assets/$NID/prefab.log 2>&1
"$GDSTYLE" fmt --check tools/asset_production/$NID/check_prefab.gd
"$GDSTYLE" --max-line-length 100 --max-warnings 0 tools/asset_production/$NID/check_prefab.gd
python tools/asset_production/$NID/record.py
```

`validate.py` reproduces the shared GLB into owned scratch without modifying any shared
artifact. Export-only: same pinned Blender/audio/timeout flags, load the shared `.blend`
after `--factory-startup`, then `--python tools/asset_production/city_sign_supports_02/export.py
-- C:/tmp/ft/assets/d04_corporate_graphics_02/reexport`. No duplicate per-artwork exporter is
needed. Revalidation replaces the measurement receipt; after running all checks, update
this handoff/final log and run `record.py --write` last to combine new receipts and manifest.
Without `--write`, `record.py` verifies current retained payload/dependency bytes only.

## Diagnostics and remaining acceptance

One initial GDScript constant exceeded the 100-character lint target; it was split and both
format/lint checks then passed. No geometry, texture, engine assertion or import failure
needed repair. Initial import defaults were intentionally changed to enable mipmaps and
preserve lossless compression before validation.

Editor normalization assertions pass and exit 0, but shutdown reports scan-aborted and
RID/ObjectDB leaks (**168 objects**), matching the documented sibling/hardware tool pattern.
This is **not a clean editor-shutdown claim** or a newly reproduced no-asset baseline.
Final ordinary import and non-editor load are independently error-free. The development
plugin retains its known 4.8-versus-tested-4.7 warning. Blender emits future `use_nodes`
deprecation warnings; bounded validation/render commands exit 0. No diagnostics were hidden.
Windowed editors/live MCP sessions were prohibited and never accessed. Direct text authoring
plus isolated headless normalization is the mandated fallback, not synchronization of the
owner's separate open scene.

Pending: independent technical/art review; final copy/dimension selection; actual saved
forecourt placement and route/vehicle clearance; populated-world actor/target visibility,
renderer/gameplay-camera/lighting captures and tower occlusion; actual network transport,
packaged target filtering/LOD, repeated-placement profiling and Deck performance. No world
placement, actor/car movement, separate-process multiplayer or device test is claimed here.
No whole-register or downstream production acceptance was closed.
