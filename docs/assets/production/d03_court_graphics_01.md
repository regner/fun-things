# d03_court_graphics.01 — Large circular paving motif

10 October 2026. **Artwork, source/export and bounded prefab checks delivered; independent
review and world acceptance pending.** Produced by the commissioned worker on `lane/a-d03g`.
The [commission](commission.md) and current per-asset execution brief supersede the earlier
concept-only restriction in the [court-graphics brief](../d03_court_graphics.md).
Producing owner: worker, original art/source, integration, checks and self-review. Accepting
owners: independent art/technical reviewer and world/gameplay integrator; no acceptance inferred.

References: [Terrace Ward concept](../../concepts/districts-v1/terrace-ward.md), its
[asset breakdown](../../concepts/districts-v1/terrace-ward-assets.md), approved
[Stage 3 identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[Stage 4 streets](../../concepts/world-v1/stage-04-streets/README.md) and Petrol & Coral.
The earlier [short laundry frame](d03_laundry_frames_01.md) and
[cloth set](d03_laundry_frames_03.md) informed the muted teal/dusty-coral family palette.
Neither current sibling handoff lists this motif as pending; neither was modified.

## Design and provisional dimensions

An original **shared-circle inlay**: a broad muted-teal outer rim, restrained ivory inner
stripe, twelve large quiet paving sectors and two adjacent dusty-coral sectors marking
one shared corner. An inner teal edge frames a completely open centre. Broad sectors and
subdued joints imply communal paving without fine tile noise, slogans, a target symbol,
sports rules, neon, equipment, raised obstacles or additional ground systems.

Dimensions are **provisional authored choices**, permitted by the production brief, not
measurements inferred from concept imagery or an approved individual court allocation.
Godot local X/Y/Z, metres:

| Contract | Value |
| --- | --- |
| Outer diameter / nominal open-centre diameter | 14.000 / 8.800 |
| Annular artwork width | 2.600 |
| Visual AABB minimum / maximum | (-7, .015, -7) / (7, .015, 7) |
| Whole size, width / height / depth | 14 / 0 / 14; single-sided artwork |
| Root / mesh pivot | Ground-projected circle centre, (0,0,0) |
| Supporting ground / artwork datum | External ground Y=0 / artwork Y=.015 |
| Carrier construction | 128 quads, one segment every 2.8125 degrees |
| Outer teal band | Radius 6.60–7.00 |
| Ivory stripe | Radius 6.38–6.53, .15 m wide |
| Twelve sector panels | Radius 4.82–6.19, 29-degree painted arcs with 1-degree gaps |
| Sector joint bed | Radius 4.78–6.23 |
| Inner teal band | Radius 4.40–4.56 |
| Envelope / coordinate / UV tolerance | .001 m / .000001 m / .000001 UV units |

The circular boundaries are 128-sided polygons; the nominal inner radius is 4.4 m,
with minimum clear apothem approximately 4.3987 m. No geometry fills that centre. The
open centre is not a delivered ground surface or an invisible collider. +X is east,
-Z north, +Z south. Coral occupies angles 90–150 degrees clockwise from east in the
atlas, the south-to-southwest corner. Blender +Y maps to Godot -Z and +Z to +Y.
Metric units, identity root/mesh transforms, no corrective prefab transforms.

## Source, artwork, export and material

- Source: `art/source/models/environment/d03_court_graphics_01/d03_court_graphics_01.blend`.
- Collection: `export_d03_court_graphics_01`.
- Root / mesh / mesh data: `D03CourtGraphics01`, `D03CourtGraphics01_Mesh`,
  `D03CourtGraphics01_Geometry`.
- Export: `art/models/environment/d03_court_graphics_01/d03_court_graphics_01.glb`
  with saved `.import` metadata.
- Texture: `art/textures/environment/d03_court_graphics_01/communal_circle_albedo.png`
  with saved `.import` metadata.
- Material: `art/materials/environment/d03_court_graphics_01/communal_circle.tres`.
- Prefab: `scenes/prefabs/environment/d03_court_graphics_01.tscn`.
- Recipes/checks: `tools/asset_production/d03_court_graphics_01/`.

`artwork.py` draws the original geometry-based 2D artwork reproducibly in Pillow; `author.py`
constructs the minimal flush annulus in Blender. No downloaded art, external fonts, brands,
image-to-mesh, copied carrier or runtime-generated render meshes. This follows the standing
[d01 sports-surface](d01_sports_surface_01.md) ground-artwork convention, not an override or
duplicate of a ground-finish swatch. No rig, animation, sockets, destruction or interaction.

One material slot, **`communal_circle`**: Principled, roughness .94, metallic 0, no emission,
normal map or alpha. Opaque, upward-facing/backface-culled. Palette in sRGB:

| Region | Swatch |
| --- | --- |
| Stone / alternating panel | `#9BA8A2` / `#A7B0A5` |
| Teal / quiet joint | `#587D7C` / `#889C97` |
| Ivory / dusty coral | `#CECDB8` / `#B98377` |

Coral matches the delivered laundry towel body; the ivory and teal are subdued for a broad
walking surface. Blender stores a relative **unpacked** link to the committed PNG. Export
briefly disconnects that texture and restores it afterwards; **zero embedded GLB images**.
Godot's saved import remaps the one slot to the external material UID with a fallback path.
No editable imported-child override, copied mesh data or runtime material writer is used.

The PNG is **1024×1024 RGB8 sRGB**, supersampled at 4× then reduced with Lanczos. UV0 covers
one 14×14 m plan at approximately 73.14 texels/metre. Blender U=(X+7)/14, V=(Y+7)/14;
exported image coordinates run east and south. Clamp, linear mipmap filtering, full generated
mip chain, lossless import, no automatic 3D compression conversion, no tiling. Pixels inside
the hole or outside the outer polygon are unused, not an alpha mask. This material requires
the documented plan UVs and is **not a generic tiled paving or road-tool material**.
Imported CPU RGB8 data including mipmaps is **4,194,303 bytes**, not measured GPU allocation
or an accepted device budget. No explicit LOD; default per-import generated LODs remain enabled.

Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**, shared
`tools/assets/blender/export_settings.json`, named collection filter, animations/skins disabled.
Pinned Godot **4.8.dev7.official.c971f93e7**. Re-export is from the committed saved source;
fresh `.blend` authoring need not produce byte-identical Blender container files.

## Prefab, supporting ground and review context

The linked imported model stays at identity-transform `Visuals/Model`. The wrapper contains
**zero collision objects/shapes, terrain, navigation or gameplay nodes**. This is the standing
flush-ground-artwork exception: no sidewalls, kerb, slab, ramp or walkable deck. The world owns
continuous actor/car ground collision. Place only over existing flat collision-bearing ground,
retaining the .015 m lift; never use this prefab alone as a floor. The engine pads planar mesh
AABB height to .00001 m; all actual exported vertices remain at Y=.015.

The saved Blender review studio links the existing `export_city_seating_01` and
`export_coral_courier` collections through relative library paths. Two unchanged benches sit
at Blender (0,6.65,0), yaw 180 degrees, and (6.65,0,0), yaw 90 degrees. Three unchanged
source-pose Courier figures stand at (-.6,-.3,0), (-4.9,2.7,0), (3.2,-5.6,0), with respective
yaws -25/40/10 degrees. These are source-linked **review context only**, not new mesh copies,
delivered furniture, a saved world arrangement, animations or gameplay population proof.
Studio ground, camera, sun and these linked contexts are excluded from the export. Dependency
hashes are recorded in validation.json; both existing source files remain unchanged.

The authorized direct-file/headless fallback was used because this production brief forbids
live-owner editor sessions. Prefab and external material were loaded/packed/saved with the
pinned headless runtime and UID-preserving saves. Two fresh save/reload passes after initial
normalization retain exact bytes, node identities and UIDs. Subsequent import and two fresh
runtime processes resolve dependencies with identical passing receipts. Scene/material UIDs
are embedded; Godot produces no scene `.uid` sidecar. The check script's `.uid` is committed.
This does not synchronize or claim inspection of a separate open editor.

## Evidence and validation

[Hero](d03_court_graphics_01-evidence/hero.png),
[oblique side](d03_court_graphics_01-evidence/side.png),
[inlay detail](d03_court_graphics_01-evidence/detail.png),
[47 m / 42-degree overhead](d03_court_graphics_01-evidence/overhead_47m_42deg.png).
All four final isolated Blender Cycles CPU renders were inspected: 24 samples, AgX,
1280×720 RGB8, PNG compression 95, no dithering, overlays or post-quantization. Each is below
270 KB. The standing 720-pixel cap supersedes the older 800-pixel evidence height.

The overhead is true vertical-down perspective, north-up, Blender (0,0,47), **42-degree vertical
FOV**, framing the entire approximately 280-pixel-wide circle. The broad round outline and coral
corner remain recognizable with two benches and three people present. Local occlusion does not
erase the landmark; its open centre keeps the figure unobstructed. Side/detail show matte broad
inlays rather than a raised kerb; the detail intentionally crops the full circle. This addresses
the brief's visual criterion in an isolated source studio, **not actual Godot populated lighting,
movement, depth, aim or world acceptance**. Actual court placement remains a downstream gate.

Final [validation.json](d03_court_graphics_01-evidence/validation.json):

- **256 triangles; 256 source and exported vertices; one mesh; one surface.**
- Zero degenerate source faces and GLB triangles; finite positions, unit upward source/export
  normals. Literal bounds, pivots, UV mapping and exported angular spans pass.
- **256 intentional boundary/non-manifold edges** in exactly two closed 128-edge perimeters;
  **zero non-boundary non-manifold edges**. This is justified open decal topology, not a broken
  solid. No branching boundaries or triangles spanning the open centre.
- Fresh saved-source GLB re-export and Pillow PNG reproduction are **byte-identical**.
- 53 independent texture-region samples verify both rims, ivory stripe, twelve sectors,
  southwest-only coral corner, quiet joints and unused centre.
- Headless final import, normalization and two fresh dependency/load checks exit 0 with no
  `ERROR` or `SCRIPT ERROR` lines. Imported bounds, material, mips and UIDs pass; no collision.
- Two scene/material save/reload cycles retain bytes and UIDs; two runtime receipts agree.
- Python syntax checks, `gdstyle fmt --check`, and lint at 100 characters / zero warnings pass.
- `production_checks.py` deliberately not run, per decision 52.

Final identities copied from the validation receipt:

| Payload | Bytes | SHA-256 |
| --- | ---: | --- |
| `.blend` | 106,224 | `c377b10aae64c0d5423f1c500e8684985f9606763a1211c8d2c5f3321aea961c` |
| `.glb` | 10,992 | `69ee45e57e4736f8ea22f56704307bade352012587b33e1861ec5887ff034c9e` |
| Albedo PNG | 176,730 | `5f15ad788b19eeb9bea65621d1d26d5060f1b579e46dbe3aa8c09d89a70ad71a` |

[manifest.json](d03_court_graphics_01-evidence/manifest.json) covers every produced file except
itself; [checks.log](d03_court_graphics_01-evidence/checks.log) is the concise final diagnostic
record. Initial lint found one overlong constant; a subsequent format check requested one wrap;
both were fixed before final checks. Blender emits its pinned `use_nodes` future-removal
warnings. Import emits the existing MCP toolkit 4.8-version advisory. These warnings are
retained, not suppressed or presented as warning-free logs. Runtime/normalization logs are clean.

## Exact reproduction

Run from repository root in Git Bash, Python with **Pillow 12.3.0**. No live Blender/Godot
sessions are used. Preserve the committed import sidecars and resource identities. Scratch
renders/logs/re-exports remain outside the repository. `validate.py` opens the saved source
and exports into scratch before comparing; `record.py` runs last after handoff/check changes.

```sh
NID=d03_court_graphics_01
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

Standalone export from the saved source, without reauthoring or renders:

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

- Independent technical/art review at the committed candidate; approval of provisional scale
  and fit within the selected communal court.
- World integrator: saved placement over continuous flat collision-bearing ground, open
  movement mouths, furniture/people occlusion, depth separation and actual foot/car contact.
- Visual/gameplay owners: populated Godot lighting, moving-camera mip shimmer, actor/aim
  contrast, tyre/foot depth, and any later placement's multiplayer-world consequences.
- Build/performance owners: packaged resource resolution, automatic LOD appearance,
  repeated-placement cost, sustained target-device performance and Deck readability.

No world scene, road topology, registry, progress tracker, shared brief, sibling payload or
TODO changed. This is an importable tested asset candidate, not full-game or world acceptance.
