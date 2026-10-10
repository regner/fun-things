# d04_corporate_graphics.03 — Entry wordmark

**Original artwork, face material and source-linked inherited prefab delivered; bounded
producer checks pass. Independent review and world/gameplay/device acceptance remain
pending.** Producer: commissioned implementation worker on `lane/a-d04g`; supervisor
retains acceptance authority. The [commission](commission.md) supersedes the historical
concept-only stage. References: [family brief](../d04_corporate_graphics.md),
[Glassward identity](../../concepts/world-v1/stage-03-district-identities/README.md#glassward--the-skyline-presses-in),
[downtown grid](../../concepts/world-v1/stage-04-streets/README.md#owner-refinement--a-gridded-high-rise-centre),
[facade artwork](d04_corporate_graphics_01.md), [directory](d04_corporate_graphics_02.md),
and [shared fascia hardware](city_shop_fittings_02.md).

## Design and provenance

**TOMORROW.** One fictional company wordmark continues the facade panel's scheduling joke
and the directory's first tenant. It is decorative entry identity, not an authoritative
building destination, navigation cue or final company naming choice. The original offset
appointment-corner emblem, continuous-stroke capitals and exact family palette are retained:
indigo `#15263D`, cyan `#57D9E5`, warm ivory `#F6F1DC`, rare magenta `#EB62B7`. Two large open
cyan corners, one small magenta appointment marker and one ivory word leave generous quiet
margins; there is no microcopy, extra slogan, glowing border or advertising collage.

`author.py` is the reproducible Python/Pillow source. It imports the original `.01` glyphs
and palette and reuses the existing `d06_commercial_graphics_02` supersampled Canvas through
an isolated module instance, as `.02` does. No external font, real brand, downloaded image,
mesh, generated concept raster or image-to-mesh is used. No shared tool is edited.

The two earlier family handoffs contain no stale pending item for this asset. Their current
manifests were verified unchanged; no sibling document or historical receipt needed editing.
No register, shared brief, TODO, progress tracker, world scene or gameplay code changed.

## Reused hardware, dimensions and mounting

**No duplicate carrier .blend or GLB.** The accepted `city_shop_fittings_02` fascia already
supplies the horizontal face needed by an entry wordmark. Its prefab is inherited unchanged;
only its front artwork material differs. This follows the standing reuse rule and the
[static artwork editable-child exception](../../assets.md#prefabs-and-authored-placement).
The larger `.01` panel and `.02` freestanding directory remain separate unchanged carriers.

All dimensions are inherited **provisional authored values**, not measurements inferred
from concept images or accepted Glassward placements:

| Contract | Value |
| --- | --- |
| Overall Godot X/Y/Z | **3.20 × 0.80 × 0.14 m** |
| AABB min / max | **(-1.60,-0.40,-0.14) / (1.60,0.40,0) m** |
| Pivot | Wall-contact centre `(0,0,0)`, not ground contact |
| Artwork face | **3.00 × 0.60 m**, front plane Godot **Z=-0.128 m** |
| Safe content | Centred **2.94 × 0.54 m**, 20-pixel / 0.03 m minimum margin |
| Front / up | Blender +Y/+Z maps to Godot -Z/+Y |
| Root / meshes / Visuals/Model | Identity transforms, metre units, no corrective scale |
| Proposed entry mounting centre | **Y=3.80 m**, lower edge **3.40 m** |
| Reserved fitting volume | X ±1.70; Y ±0.45; Godot Z -0.24…+0.02 m |
| Flat bay / adjacent gap | At least **3.40 m** wide / at least **0.10 m** physical gap |
| Mount tolerance | Wall placement ±0.002 m; source/binary bounds ±0.000001 m |

Proposed mounting retains the hardware contract above a lobby entry, below the tower
family's 6 m lobby band. It is not a delivered attachment/socket or proof of a particular
podium's flat-wall availability. Use an unscaled facade bay, never a curved wall or corner;
resolve windows, canopy, door and neighbouring signage conflicts in placement review.

**Visual-only above-head fitting.** At the proposed 3.80 m centre, its lower edge is 3.40 m,
above the standing 2.5 m rule. The wall owns structural collision; artwork adds no body,
interaction, navigation, light, destruction, rig, animation, socket or runtime hierarchy.
Do not use this prefab freestanding or at ground level without an intentional collider
and movement review. No new collision or gameplay behavior is claimed.

## Source, runtime material and prefab

- Reused Blender source:
  `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`.
  Collection `export_city_shop_fittings_02`; root `city_shop_fittings_02`; seven mesh children.
- Reused export: `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb`
  and its unchanged `.import`; existing hardware `export.py` validates and exports its
  declared selection with pinned Blender/glTF settings. No new export-settings choice is
  made by this artwork, and there are no embedded textures or copied render meshes.
- Runtime texture:
  `art/textures/environment/d04_corporate_graphics_03/entry_wordmark_albedo.png`,
  **2000 × 400 RGB**, 5:1 aspect, **666.67 px/m**, opaque sRGB albedo. `.import` uses lossless
  compression, mipmaps enabled and automatic 3D compression switching disabled.
- Material: `art/materials/environment/d04_corporate_graphics_03/entry_wordmark.tres`,
  `glassward_entry_wordmark`, white multiplier, metallic 0, roughness **0.56**, backface culled,
  linear mipmapped filter, clamp/no repeat, UV scale 1/offset 0. No emission/normal/ORM maps.
- Prefab: `scenes/prefabs/environment/d04_corporate_graphics_03.tscn`, inheriting
  `city_shop_fittings_02.tscn`. Its `Visuals/Model` remains the identity GLB instance.
  Exactly one editable-child override: `fascia_artwork_carrier`, **surface 0
  `fascia_artwork_face`**. Surface 1 `fascia_mount_metal` retains back/sides; frame, trim,
  reveal, tray and mounting rails retain every original material.
- UV0: Blender **U=0.5-X/3.0**, **V=0.5+Z/0.6**. Front screen-right is -X; exported glTF
  flips V to top-origin texture coordinates. Source and 28 decoded binary face samples
  prove upright, unmirrored mapping. Rounded face corners clip only background bleed.
- Prefab UID `uid://b2jsnjkcdjgcm`; material UID `uid://crf23fmg18cyc`; texture UID
  `uid://nrac0wjcs3e1`; inherited GLB UID `uid://cdtnvrp3u64wi`. Scene/material UIDs are inline;
  Godot does not create separate `.tscn.uid`/`.tres.uid` files. The checker `.gd.uid` is kept.
- Tools: `tools/asset_production/d04_corporate_graphics_03/` contains `author.py`,
  `validate.py`, `preview.py`, `test_artwork.py`, `check_prefab.gd` and `record.py`.
  No duplicate per-artwork exporter is needed; the existing hardware exporter is reused.
  All source/export/import/base-prefab and transitive tool dependencies are hash-protected.

The authorized static artwork exception is bounded by **two byte-stable scene/material
save/reload roundtrips**, preserving saved node identities and UIDs, followed by an ordinary
non-editor process load. No new appearance API or editable geometry is introduced. Existing
hardware LOD/tangent/shadow-mesh import settings stay unchanged; no performance budget or
production renderer acceptance is inferred.

## Evidence and measured checks

[Hero](d04_corporate_graphics_03-evidence/hero.png) ·
[side](d04_corporate_graphics_03-evidence/side.png) ·
[face/frame detail](d04_corporate_graphics_03-evidence/detail.png) ·
[47 m / 42° overhead](d04_corporate_graphics_03-evidence/overhead_47m_42deg.png).
All four images and the runtime artwork PNG were personally inspected. Hero and side show
upright copy, clean seating and the unchanged slim hardware. Detail shows the rounded frame,
blank safe margin and smooth letter strokes. **The word is not reliably gameplay-readable**:
the overhead face is a tiny foreshortened strip. Essential routes/entries must use world and
architecture cues, not this copy. No enlarged duplicate or tilted/roof-facing face disguises
that limitation.

Isolated Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; Cycles CPU,
32 samples/denoising, AgX, **1280×720**, RGB PNG compression 95, no dithering. Renders are
7–178 KB each. `preview.py` opens unchanged source and temporarily assigns the material,
without saving. Overhead is vertical-down/north-up perspective at **47 m / 42° vertical FOV**,
Blender camera `(0,10,47)`, temporarily mounted source root `(0,0,3.8)`, no rotation/scale.
This is isolated source evidence, not a saved placement, Godot visual capture or lighting test.

[validation.json](d04_corporate_graphics_03-evidence/validation.json) records:

- **1,656 triangles; 836 source vertices; 1,072 split GLB vertices; seven meshes;
  eight surfaces.** These are reused hardware counts, not new geometry.
- **Zero nonmanifold source edges, degenerate source faces or binary triangles**; positive
  closed-solid volumes, consistent outward winding, finite coordinates and unit normals.
- Original source audit plus the independent raw GLB decoder pass actual positions,
  normals, indices, topology, face slots, UVs, transforms, bounds and studio exclusion.
- Fresh saved-source export is **byte-identical**, **45,616 bytes**, SHA-256
  `4fd2106f09ef4a35edafbcf3a3a68ea94983e721fd84d852a406e2d26de6552f`.
- **Four artwork tests pass**: opaque aspect, hardware safe margins, exact family palette/
  sparse accent/single-word hierarchy and committed PNG byte reproduction.
- Pinned Godot **4.8.dev7.official.c971f93e7** final import and independent non-editor load
  have **no ERROR/SCRIPT ERROR lines**. Actual mipmaps/filtering, bounds, hierarchy, unchanged
  linked meshes and exactly one face-only override pass. No collider is introduced.
- **Two byte-stable scene/material roundtrips**, including saved IDs/UIDs, pass. Normalization
  and final runtime file hashes match the retained payloads.
- Pinned **gdstyle 0.3.0** owned GDScript formatting and zero-warning 100-character lint pass.
  No global `production_checks.py` run, per owner decision 52.

[manifest.json](d04_corporate_graphics_03-evidence/manifest.json) hashes every produced file
except itself and separately lists unchanged dependencies. [final.log](d04_corporate_graphics_03-evidence/final.log)
is the sole concise retained command summary. Full process logs and scratch exports remain
under `C:/tmp/ft/assets/d04_corporate_graphics_03/`, never committed.

## Exact reproduction

Run from the worktree root in Bash with Python/Pillow **12.3.0** available:

```sh
NID=d04_corporate_graphics_03
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

`validate.py` calls the existing fascia validator/exporter and independent decoder with
scratch-only outputs. Export-only: same pinned Blender/audio/timeout flags, load the shared
`.blend` after `--factory-startup`, then `--python tools/asset_production/city_shop_fittings_02/export.py
-- C:/tmp/ft/assets/d04_corporate_graphics_03/export-only.glb
C:/tmp/ft/assets/d04_corporate_graphics_03/export-only.json` (one command). Revalidation
replaces the combined receipt; after all checks, refresh this handoff/final log and run
`record.py --write` last. Without `--write`, it verifies retained payload/dependency hashes.
Reproducing artwork or previews never saves or modifies shared source/hardware.

## Diagnostics and remaining acceptance

No geometry, artwork, engine assertion or formatting failure required repair. Initial
texture import defaults were explicitly changed to enable mipmaps and disable automatic
3D compression switching before validation. All ordinary imports and runtime checks passed.

Editor normalization assertions pass and exit 0, but editor shutdown reports scan-aborted
and RID/ObjectDB leaks (**168 objects**), matching the documented sibling tool pattern.
This is **not a clean editor-shutdown claim**; no independent empty baseline was rerun.
Final ordinary import and non-editor dependency load are separately error-free. The addon
retains its known 4.8-versus-tested-4.7 compatibility warning. Blender emits future
`use_nodes` deprecation notices; the bounded export/render commands exit 0. No diagnostics
were suppressed. Windowed editors/live MCP sessions were prohibited and never accessed.
Direct text authoring plus isolated headless normalization is the mandated fallback, not
synchronization of the owner's separate open scene.

Pending: independent technical/art review; final copy/dimension selection; actual flat-wall
entry mounting and facade-grid/canopy fit; renderer/gameplay-camera, tower occlusion and
populated-world actor/target visibility; packaged filtering/LOD, repeated-placement profiling
and Deck performance. No actor/car movement, collision, separate-process multiplayer, world
placement or target-device test is claimed for this non-colliding artwork. No whole-register
or downstream production acceptance was closed.
