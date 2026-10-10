# city_ground_finishes.02 — Service concrete

10 October 2026. **Material, source/export and linked swatch delivered; independent review and
world/gameplay/device acceptance pending.** Output type: Material study. Regner's current
production commission supersedes the concept-only wording in the
[family brief](../city_ground_finishes.md); see [commission](commission.md).
Original author: commissioned Codex production worker. Accepting reviewer: pending.
No downloaded imagery, brands, external geometry or generated-image textures.

## Design and dimensions

Quiet, matte, desaturated grey-green concrete for **Ironreach service yards and East Docks
working aprons**. Signal Row and Broadlot remain candidate uses, not new placements. Two
broad, soft curing washes provide slight tonal variation without cracks, gritty aggregate,
normal-map sparkle, raised seams, stains that resemble hazards, or a dense repeating grid.
The base sRGB reference is **(139,146,144), #8B9290**. Actual albedo ranges are only
R **134–141**, G **141–148**, B **139–146**: seven code values per channel.

The warmer, joint-free field contrasts with the cooler, regular slate slabs of
[plain plaza paving](city_ground_finishes_01.md), while retaining its **4 m repeat / 512 px**
interface and surface datum. Inspected references include the approved Stage 3 district
identities, Stage 4 working-access layout and Ironreach/East Docks revision-02 concepts.
They guide appearance, not inferred measurements or new district geometry. Applied apron
markings and layout-specific joints remain outside this plain material; no road markings,
parking asphalt, site boundaries or road-tool geometry were added.

The portable Blender-sourced swatch is a review sample, **not a yard floor module**:

- Provisional Godot X/Y/Z dimensions: **4.000 × 0.080 × 4.000 m**, matching the family sample.
- AABB **(-2,-0.08,-2) → (2,0,2) m**; numeric tolerance ±0.000001 m.
- Surface-centred pivot **(0,0,0)**. Flat top remains **Y=0**, with thickness below the datum.
- Metre units, unit scale/applied rotation, root and mesh origins at zero.
  Blender +Z maps to Godot +Y; Blender +Y maps to Godot -Z.
- **8 source vertices, 24 exported vertices, 12 triangles; one mesh, one surface**.
  Exported corner splits preserve the six hard-face normals.
- No sockets, rig, clips, moving parts, destruction states, real lights or explicit LOD.
  Automatic LOD is disabled only on this already-minimal sample.

## Source, export and material mapping

| Deliverable | Path |
| --- | --- |
| Editable Blender source | `art/source/models/environment/city_ground_finishes_02/city_ground_finishes_02.blend` |
| Explicit export | `art/models/environment/city_ground_finishes_02/city_ground_finishes_02.glb` + `.import` |
| Reusable material | `art/materials/environment/city_ground_finishes_02/service_concrete.tres` |
| Runtime texture | `art/textures/environment/city_ground_finishes_02/service_concrete_albedo.png` + `.import` |
| Linked review sample | `scenes/prefabs/environment/city_ground_finishes_02.tscn` |
| Parametric source and checks | `tools/asset_production/city_ground_finishes_02/` |

`author.py` constructs the original Blender swatch. Collection `export_city_ground_finishes_02`
contains root `CityGroundFinishes02` and mesh `CityGroundFinishes02_Mesh` (mesh data
`ServiceConcreteSwatch`). `texture.py` is the original deterministic texture source: two
periodic smooth patches plus a very faint broad finishing sweep, with no random micro-noise.
The saved Principled material links the committed PNG by a relative, unpacked path.

`export.py` uses the shared `tools/assets/blender/export_settings.json`, explicit collection
filtering and static animation/skin exclusions. It temporarily disconnects the texture for
export, then restores the Blender link. The **service_concrete** slot is mapped to the external
Godot `.tres` by the saved GLB import settings. The GLB has **zero embedded images**; the source
and Godot material use the same PNG. No editable-child override or replacement mesh is stored
in the wrapper. Source/export/check conventions follow the sibling; the existing shared
export settings and canonical production checks are reused. No shared material-study harness
exists, and none was introduced outside the permitted per-record tools.

Material: opaque/backface-culled, nonmetallic, roughness **0.94**, white albedo multiplier.
Texture: **512 × 512 RGB sRGB albedo**, lossless import, mipmaps, linear mipmap filtering,
repeat enabled; automatic 3D compression conversion disabled. No normal, ORM or emission
texture is needed. The deliberately flat surface has no displacement or tangent-normal
orientation requirement.

### Surface-tool / UV interface

**Apply `service_concrete.tres` to the surface owner's geometry, not repeated swatch prefabs.**
Road, sidewalk, curb and intersection generation stays with the road tool under decision 42.
The sample neither replaces its mesh generation nor defines floor collision for a district.

UV0: **one unit = 4 m**, material UV scale (1,1,1). For flat site geometry use
`UV0 = (local_x - anchor_x, local_z - anchor_z) / 4`; U east/+X, V south/+Z. The centred
sample anchor is (-2,-2). Keep a common anchor across neighbouring patches, uniform metre
density and the existing flat ground datum. No object scaling or triplanar shader is required.
Normalized 0–1-per-segment road UVs require an adapter in the surface owner; do not stretch
one texture over an entire apron. Both opposite border samples match exactly. The export
validator independently checks the top vertices' UV-to-Godot-position relationship.

The actual road addon/UV adapter is not present in this checkout. **Live generated-surface
compatibility remains pending**; this is a concrete integration contract, not a claimed
road-tool test. Large-area repetition should be reviewed under district lighting before use.

## Prefab and collision

Saved `Visuals/Model` is an identity-transform imported PackedScene instance. Godot assigned
new scene, model, material, texture and script identities; no sibling UID was copied. Scene
and resource UIDs are embedded in `.tscn`/`.tres`; the check script retains its `.gd.uid`.
Two headless load/pack/resave rounds preserve exact wrapper bytes/IDs.

The walkable review sample has **one continuous 4 × 0.08 × 4 m box** centred at (0,-0.04,0),
under `Collision/SwatchBody/Shape`, static-world layer 1 / mask 0. Five public physics rays
(centre and inset corners) hit Y=0 with +Y normals; an outside ray misses. There are no
visual-wash collision seams. This satisfies the portable sample's floor contract, not
production ActorMotion/car traversal or networking acceptance. Existing sites retain their
own collision: never overlay this sample on a floor or add duplicate swatch colliders.

## Evidence and validation

- [Hero](city_ground_finishes_02-evidence/hero.png),
  [side](city_ground_finishes_02-evidence/side.png),
  [concrete detail](city_ground_finishes_02-evidence/concrete_detail.png): **960 × 640**.
- [47 m / 42° overhead](city_ground_finishes_02-evidence/overhead_47m_42deg.png): **1280 × 720**,
  vertical-down perspective, north up. The current 720-pixel evidence cap supersedes the
  historical 800-pixel height; height and vertical FOV remain unchanged.
- Isolated Blender Cycles CPU, 24 samples, AgX, PNG compression 100, no dithering;
  **22–87 KB per render**. These are **not Godot screenshots**.
- Overhead contains 48 temporary linked swatch repetitions over 32 × 24 m, with unchanged
  Coral Courier and Latch GLBs as read-only source-backed scale references. They are not
  saved or exported as part of this asset. All four final images and the sibling overhead
  were visually inspected: soft broad variation, no hard repeat seams or distracting fine
  texture, quieter than the coral car and ivory/coral figure. The figure's small overhead
  footprint, repeat rhythm and moving/shadowed readability still require engine review.

[validation.json](city_ground_finishes_02-evidence/validation.json): **zero degenerate faces,
zero non-manifold edges, unit-length normals, outward winding**, exact envelope/UV checks
and **fresh re-export byte identity**. Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF
exporter **5.2.40**. Godot **4.8.dev7.official.c971f93e7** imports, resolves the external
material and passes standalone load/physics checks. Explicit owned-script compilation and
plugin-free mirror load/physics/compilation also pass with no warnings/errors.

Five independent texture tests pass: recipe equality, matching borders, desaturated bounded
midtone, no abrupt grit/grout edges and restrained minified forms. Pinned gdstyle passes.
Canonical production checks pass formatting/lint, **14 repository Python tests, all 137 GUT
tests (6,523 assertions)**, GUT import and the negative-test harness. **The full command exits
1:** compiler setup exceeds its 30-second limit, then its 120-second aggregate compilation
deadline expires after **93/164** scripts pass; 71 rows contain `CHECK DEADLINE EXCEEDED`.
This is not a source compile-error claim or the historical fixture exception. The owned script
passes separately in both the worktree and initialized compiler mirror. Shared deadlines were
not modified and the unchanged full failing step was not repeated.

[final_log.txt](city_ground_finishes_02-evidence/final_log.txt) distinguishes these outcomes.
Full-project import emits the existing MCP-version warning. Headless editor normalization
exits 0 after the successful receipt but emits RID/ObjectDB shutdown diagnostics, consistent
with the sibling's documented empty-editor reproduction; it is not a clean-log pass.
Blender uses a pinned API that emits a `Material.use_nodes` deprecation warning. Initial owned
GDScript function-length and Pillow deprecation warnings were corrected and rechecked.
The [producer manifest](city_ground_finishes_02-evidence/manifest.json) hashes every delivered
file except itself. Scratch logs, mirrored projects and re-exports remain outside the repository.

## Exact reproduction

From repository root in Git Bash, with Pillow 12.3.0 and pinned mise tools. Use a fresh checks
output directory; the canonical runner rejects existing nonempty output. Do not use live
Blender/Godot sessions. Editor-managed resources were authored as text and normalized through
the required pinned headless load/pack/resave path because the windowed editor is unavailable.
No assertion is made that a separate open editor scene was synchronized.

```sh
N=city_ground_finishes_02
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="tools/asset_production/$N"
S="C:/tmp/ft/assets/$N"
mkdir -p "$S"
python "$T/texture.py"
timeout 120 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/preview.py"
timeout 300 "$G" --headless --editor --path . --import --quit
# Check diagnostics separately: normalization is a byte-stability observation.
timeout 180 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --normalize
cp "$S/prefab.json" "$S/prefab_normalized.json"
timeout 180 "$G" --headless --path . --script "res://$T/check_prefab.gd"
timeout 180 "$G" --headless --path . --check-only --script "res://$T/check_prefab.gd"
"$(mise which gdstyle)" fmt --check "$T/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd"
python -m unittest discover -s "$T" -p 'test_*.py' -v
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks"
# Initialized plugin-free mirror from the canonical checks:
timeout 180 "$G" --headless --path "$S/checks/script-checks/compiler-project" --check-only --script "res://$T/check_prefab.gd"
timeout 180 "$G" --headless --path "$S/checks/script-checks/compiler-project" --script "res://$T/check_prefab.gd"
timeout 120 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
python "$T/manifest.py" --write
python "$T/manifest.py"
```

## Remaining acceptance

Independent technical/art review; actual generated-surface UV integration; saved district
placement and apron-graphic composition; actual engine camera motion, shadows and actor/car
separation; production movement and multiplayer checks if site collision changes; packaged
builds, sustained GPU/frame pacing and Deck checks. Whole-project compiler acceptance remains
incomplete due to the recorded tool deadlines. No queue, shared progress/brief, sibling asset,
project setting, world placement, gameplay code or TODO was changed. No whole-game READY claim.
