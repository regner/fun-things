# d03_court_graphics.02 — Small play-marking graphic

10 October 2026. **Artwork, source/export and bounded prefab checks delivered; independent
review and world acceptance pending.** Produced by the commissioned worker on `lane/a-d03g`.
The [commission](commission.md) and current per-asset execution brief supersede the earlier
concept-only restriction in the [court-graphics brief](../d03_court_graphics.md).
Producing owner: worker, original artwork/source, integration, checks and visual self-review.
Accepting owners: independent art/technical reviewer and world/gameplay integrator; no
acceptance is inferred from successful import or this handoff.

References: [Terrace Ward concept](../../concepts/districts-v1/terrace-ward.md), its
[asset breakdown](../../concepts/districts-v1/terrace-ward-assets.md), approved
[Stage 3 identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[Stage 4 streets](../../concepts/world-v1/stage-04-streets/README.md) and Petrol & Coral.
Read the earlier [short frame](d03_laundry_frames_01.md), [cloth set](d03_laundry_frames_03.md)
and [large circular motif](d03_court_graphics_01.md); this delivery uses the circle's same
muted teal, dusty coral and ivory palette. None of those current handoffs lists this asset
as pending, so no sibling handoff or manifest required a status edit.

## Design and provisional dimensions

An original **eight-step hopscotch-like marking**, with six rows alternating single and
paired cells. Broad clipped corners, a quiet ivory border and original rounded monoline
numerals make it recognizable as a small play corner without equipment, regulations,
sports mechanics or an interactive minigame. Only the first paired row is dusty coral;
the remaining cells are muted teal. No neon, distressed noise, brands or third-party fonts.

This is one artwork design/set and one linked prefab, not eight independently placed props.
The numbered cells are painted faces, **not raised stepping stones**. Shared ground remains
visible through every gap. Dimensions are **provisional authored values**, permitted by the
standing production brief, not inferred from the raster or an approved district allocation.
Godot local X/Y/Z, metres:

| Contract | Value |
| --- | --- |
| Whole footprint, width / depth | 1.900 / 5.300 |
| Visual AABB minimum / maximum | (-.950, .015, -2.650) / (.950, .015, 2.650) |
| Root and mesh pivot | Ground-projected footprint centre (0,0,0) |
| External ground / artwork height | Y=0 / Y=.015; zero-thickness single-sided faces |
| Each cell, width / depth | .900 / .800 |
| Clipped-corner leg length | .080 |
| Gap between successive rows / paired cells | .100 / .100 |
| Ivory border inset | .065; diagonal corner border slightly narrower |
| Numeral nominal box / stroke width | .250 x .380 / .055 |
| Total painted carrier area | 5.6576 square metres |
| Envelope / coordinates / UV tolerances | .001 m / .000001 m / .000001 UV units |

Numbered cell centres, X/Z in Godot: **1** (0,+2.250), **2** (0,+1.350),
**3** (-.500,+.450), **4** (+.500,+.450), **5** (0,-.450),
**6** (-.500,-1.350), **7** (+.500,-1.350), **8** (0,-2.250).
Numbers ascend from south to north and read upright in the north-up overhead camera.
Blender +Y maps to Godot -Z and +Z to +Y. Metre units, applied identity root/mesh
transforms; no corrective prefab rotation or scale. The saved studio contains a hidden-render
one-metre measurement cube, verified by the validator and excluded from the export.

## Source, artwork, export and material

- Source: `art/source/models/environment/d03_court_graphics_02/d03_court_graphics_02.blend`.
- Export collection: `export_d03_court_graphics_02`.
- Root / mesh / mesh data: `D03CourtGraphics02`, `D03CourtGraphics02_Mesh`,
  `D03CourtGraphics02_Geometry`.
- Export: `art/models/environment/d03_court_graphics_02/d03_court_graphics_02.glb`
  with committed engine-import metadata.
- Texture: `art/textures/environment/d03_court_graphics_02/play_steps_albedo.png`
  with committed `.import`.
- Material: `art/materials/environment/d03_court_graphics_02/play_steps.tres`.
- Prefab: `scenes/prefabs/environment/d03_court_graphics_02.tscn`.
- Reproduction/check tools: `tools/asset_production/d03_court_graphics_02/`.

`artwork.py` reproducibly draws the original shapes and eight hand-authored numeral paths
in Pillow. `author.py` constructs eight minimal Blender octagonal faces in one mesh. No
external art/font, downloaded mesh, image-to-mesh, copied carrier or runtime-generated
render geometry. This follows the standing [sports-surface](d01_sports_surface_01.md)
flush-ground-artwork convention; it does not override ground-finish swatches or introduce
a ground mesh system. No rig, animation, socket, destruction state or gameplay code.

One material slot: **`play_steps`**, Principled, roughness .94, metallic 0, no emission,
normal map or alpha. Upward-facing/backface-culled and opaque. The sRGB colors are
teal **#587D7C**, ivory **#CECDB8**, coral **#B98377**. These exactly match the circle's
corresponding swatches; coral also matches the laundry towel body. Blender converts sRGB
fallback colors to linear values and retains an unpacked relative link to the committed PNG.

The texture is **512x1024 RGB8 sRGB**, 4x supersampled then Lanczos-reduced. UV0 spans one
**3x6 m** atlas at approximately **170.67 texels/metre**; it is not tiled. Blender
U=(X+1.5)/3, V=(Y+3)/6. Exported image U points east and V south. Unconsumed atlas pixels
are ivory; only the eight clipped cell faces use the atlas, so no background slab or
transparent rectangle is present. Clamp, linear mipmap filtering, full generated mip chain,
lossless import, no automatic 3D compression conversion. Imported CPU RGB8 including mips
is **2,097,153 bytes**, not measured GPU allocation or an approved device budget.

Export temporarily disconnects and restores the source color texture. The GLB contains
**zero embedded images**; Godot's saved import remaps `play_steps` to the external material
UID and fallback path. No editable-child override, copied mesh data or runtime material
writer. No explicit LOD; default per-import generated LODs remain enabled. This is an
asset-specific plan atlas, not a generic paving material or road-tool texture.

Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Shared
`tools/assets/blender/export_settings.json`, named collection filter, Y-up conversion,
normals/UVs, animations/skins disabled. Pinned Godot **4.8.dev7.official.c971f93e7**.
Byte-identical export is tested from the saved source, not freshly reconstructed `.blend`
container bytes, which may differ after fresh authoring.

## Prefab, ground and studio context

`Visuals/Model` is the identity-transform imported instance. The wrapper has **zero
collision objects/shapes, navigation, terrain or interaction nodes**. This is flush painted
decoration under the standing collision exception, not a deck, ramp, kerb, obstacle or
walkable floor. Place only over existing flat collision-bearing paving, retaining the
15 mm visual lift. The world owns continuous foot/car collision, including the gaps.
Godot pads planar AABB height to .00001 m; exported vertices all remain at Y=.015.

Place in a secondary court corner, away from passage mouths and without overlapping the
large circular landmark. The smaller graphic must remain subordinate to that circle;
it does not replace the circle's existing bench/person visibility evidence. Selected
court arrangement and relative placement of both graphics are still world-integration work.

The saved Blender studio links existing `export_city_seating_01` and `export_coral_courier`
collections through relative library paths, without duplicating their geometry. One bench
is at Blender (2.7,1.3,0), yaw 90 degrees; source-pose people stand at (0,.45,0), yaw -25,
and (1.5,-1.6,0), yaw 40. These are **review context only**, not delivered furniture,
character animation, gameplay population or world placements. Dependency hashes are in
validation.json. Bench/people, studio ground, reference cube, camera and lighting are all
excluded from the GLB. Existing source files were not modified.

The execution brief prohibits live-owner editor use, so scene/material text was authored
directly, then loaded/packed/resaved headlessly. Two post-normalization save/reload passes
preserve exact bytes, node identities and resource UIDs; two fresh runtime processes resolve
the final dependencies with matching receipts. Scene/material UIDs are embedded; Godot
produces no scene `.uid` sidecar. The check script's generated `.uid` is committed. This
headless workflow does not synchronize or claim inspection of any separate open editor.

## Evidence and validation

[Hero](d03_court_graphics_02-evidence/hero.png),
[oblique side](d03_court_graphics_02-evidence/side.png),
[numeral/border detail](d03_court_graphics_02-evidence/detail.png),
[47 m / 42-degree overhead](d03_court_graphics_02-evidence/overhead_47m_42deg.png).
All four final isolated Blender renders were inspected: Cycles CPU, 24 samples, AgX,
1280x720 RGB8 PNG, compression 95, no dithering or post-quantization. Each is below 400 KiB.
The standing 720-pixel cap supersedes the earlier 800-pixel evidence requirement.

The overhead is true vertical-down perspective, north-up, at (0,0,47), **42-degree vertical
FOV**. The approximately **38x106-pixel** single/double stepping outline remains legible
around a person occupying cell 5; the coral pair and open gaps remain distinct. Numbers are
clear in close views, with rounded ends and low-contrast edges; reading every numeral during
play is not required for this secondary decorative landmark. The detail intentionally crops
the overall motif. Studio source-pose figures establish scale, not playable behaviour.
These are not Godot gameplay captures, moving-camera tests or independent art acceptance.

Final [validation.json](d03_court_graphics_02-evidence/validation.json):

- **48 triangles; 64 source and exported vertices; one mesh; one surface.**
- Zero source degenerate faces and GLB degenerate triangles. Finite coordinates, upward
  winding and unit source/export normals; literal cell bounds, painted area, pivots and UVs pass.
- **64 intentional boundary/non-manifold edges**, eight closed eight-edge perimeters;
  **zero non-boundary non-manifold edges**. Open planar decal topology is intentional.
  Every exported triangle stays within one cell; no geometry bridges the .100 m gaps.
- Fresh saved-source GLB re-export and Pillow PNG reproduction are **byte-identical**.
- 72 independent region samples, eight distinct nonempty numeral crops and specific numeral
  landmarks pass. Only cells 3/4 have coral fill; other fields and all borders match the palette.
- Pinned final headless import and two fresh dependency/load checks exit 0 with no `ERROR`
  or `SCRIPT ERROR` lines. Linked ancestry, external material, bounds, mips and UIDs pass.
- Two scene/material roundtrips preserve bytes/UIDs; final runtime receipts agree.
- Python syntax checks, `gdstyle fmt --check` and 100-character / zero-warning lint pass.
- `production_checks.py` deliberately not run, per decision 52.

Final payload identities copied from the validation receipt:

| Payload | Bytes | SHA-256 |
| --- | ---: | --- |
| `.blend` | 101,528 | `2fab4009fda66a09dcef8e00ae58c744d3e54aee9e0b6cca97d8f55c7c34fb7d` |
| `.glb` | 3,656 | `3b92565458ab96e5e96a0f33d3a4982e65cbd8f8cf78b02da396e37892736998` |
| Albedo PNG | 31,370 | `1d1077852b92b2559cf9c7c29a84789c8cfb36217532fa91a5844a46e5c19111` |

[manifest.json](d03_court_graphics_02-evidence/manifest.json) hashes every produced file except
itself. [checks.log](d03_court_graphics_02-evidence/checks.log) records concise final results
and diagnostics. One initial test probe intended for empty background landed on numeral 7's
antialiased diagonal; it was moved to the explicitly empty lower-right region, without
changing the artwork or suppressing the assertion. A hidden-render one-metre reference was
added before the final source validation. Blender emits the pinned `use_nodes` deprecation
warning; import emits the existing MCP toolkit engine-version advisory. Final import completed
all resource steps, then emitted a shutdown-only `Scan thread aborted` warning. Both following
runtime resource checks passed. No warning was suppressed; import is not claimed to be
warning-free. Runtime/normalization logs have no errors. Scratch/intermediates are not committed.

## Exact reproduction

Run from repository root in Git Bash, using Python with **Pillow 12.3.0**. Preserve import
sidecars and UIDs. No live Blender/Godot sessions. All engine calls use the mise pin;
all Blender/engine calls are bounded by `timeout`. `record.py` must run last, after the
handoff has been updated from final receipts, to refresh evidence and hashes.

```sh
NID=d03_court_graphics_02
T=tools/asset_production/$NID
S=C:/tmp/ft/assets/$NID
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
STYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
mkdir -p "$S"
python "$T/artwork.py"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/author.py" > "$S/author.log" 2>&1
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" > "$S/validate.log" 2>&1
python "$T/check_artwork.py" > "$S/artwork-check.log" 2>&1
python -m py_compile "$T/author.py" "$T/artwork.py" "$T/export.py" \
  "$T/validate.py" "$T/check_artwork.py" "$T/record.py" \
  && echo PYTHON_COMPILE_PASS > "$S/python-check.log"
"$STYLE" fmt --check "$T/check_prefab.gd" > "$S/format.log" 2>&1
"$STYLE" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd" > "$S/style.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-remap.log" 2>&1
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" -- \
  --normalize > "$S/roundtrip.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" \
  > "$S/prefab-check.log" 2>&1
cp "$S/prefab-check.json" "$S/prefab-first-process.json"
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" \
  > "$S/prefab-second-process.log" 2>&1
cmp "$S/prefab-first-process.json" "$S/prefab-check.json"
python "$T/record.py"
```

Standalone re-export from the committed source, without reauthoring or rendering:

```sh
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  "art/source/models/environment/$NID/$NID.blend" --python-exit-code 1 \
  --python "$T/export.py" -- "$S/manual-reexport"
```

## Review round 1 — saved dependency identities

Addressed the P2 finding by serializing existing UIDs for the prefab model and material texture dependencies.
No identity was reallocated. Header UIDs, node `unique_id` values, ancestry, transforms,
material settings and collision are unchanged. The checker follows the delivered
entrance-number asset's headless fallback: after Godot saves, restore dependency UID
fields from the warm import cache, then inspect the actual serialized text. Every owned
prefab/material (and owned fixture, where present) must have a header UID, a resolving
`uid=` on each `[ext_resource]`, and `unique_id=` on every node. Runtime checking is read-only
and rejects absent or mismatched dependency UIDs before other checks.

The strengthened checker rejected the original missing fields and a deliberately mismatched
registered UID (exit 1); restored files pass normalization, two byte-stable supplemented
save/reload cycles, pinned import and two fresh runtime checks with identical receipts.
Source validation and fresh re-export were rerun; existing source, GLB, artwork and render
bytes remain unchanged. Renders were not regenerated because no visual input changed;
the reviewed four images remain the visual evidence. Artwork reproduction checks, where
applicable, Python compilation and pinned GDScript format/zero-warning lint pass.
`validation.json` records the serialized dependency map and negative-test observations;
`manifest.json` was regenerated last. The exact reproduction commands below/above remain
valid. No live editor was accessed or synchronized. Full world/gameplay/device acceptance
remains pending; independent review must confirm this P2 repair.

## Remaining acceptance

- Independent technical/art review at the committed candidate and provisional scale approval.
- World integrator: saved placement over continuous ground, separation from the circular
  landmark, unblocked passage mouths, actual furniture/people occlusion and depth separation.
- Visual/gameplay owners: populated Godot lighting, moving-camera mip shimmer, actor/aim
  contrast, tyre/foot depth and any later placement's movement or multiplayer consequences.
- Build/performance owners: packaged dependencies, automatic LOD appearance, repeated-placement
  cost, sustained target-device performance and Deck readability.

No world scene, road topology, registry, progress tracker, shared brief, sibling payload or
TODO changed. This is an importable tested asset candidate, not full-game or world acceptance.
