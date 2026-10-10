# city_ground_finishes.04 — Short grass

10 October 2026. **Material, source/export and linked swatch delivered; independent review and
world/gameplay/device acceptance pending.** Output type: Material study. Regner's current
production commission supersedes the concept-only wording in the
[family brief](../city_ground_finishes.md); see [commission](commission.md).
Original author: commissioned Codex production worker. Accepting reviewer: pending.
Original deterministic artwork and Blender construction; no downloads, external brands,
image-generated textures or third-party geometry.

## Design and dimensions

Muted emerald short grass, with three heavily flattened, unequal growth patches, not blade noise,
mowing stripes or a sport-field grid. The base sRGB reference is **(81,117,91), #51755B**.
Actual albedo ranges are R **80–82**, G **116–118**, B **91–92**: no channel varies by more
than two code values after review retuning. Slight warmer/lighter growth variation remains
subordinate to actors.
No cracks, flecks, flowers, tuft geometry, wind shader, displacement or glossy normal map.
This is a flat visual lawn finish, not a foliage carrier or a terrain/friction rule.

Recorded demand covers **Northpoint, The Crescents, Terrace Ward, Glassward, Old Quay,
Broadlot and Ironreach**: courts, domestic gardens, planted islands and sparse working-yard
margins. The approved Stage 3 identities and Stage 4 street/open-space contract guide the
appearance, not inferred dimensions or new plots. No district geometry or placement changes.
The lawn intentionally contrasts with the slate [plaza paving](city_ground_finishes_01.md)
and grey-green [service concrete](city_ground_finishes_02.md), while retaining their
**4 m repeat / 512 px** interface and flat datum. Both sibling outputs were read and inspected;
neither was changed. Garden soil remains the separate .05 deliverable.

The portable swatch is a review sample, **not a lawn floor module for world placement**:

- Provisional Godot X/Y/Z dimensions **4.000 × 0.080 × 4.000 m**.
- AABB **(-2,-0.08,-2) → (2,0,2) m**, tolerance ±0.000001 m.
- Surface-centred pivot **(0,0,0)**. Top is **Y=0**, thickness below that datum.
  This follows the ground-material sample's surface-datum exception, not a raised lawn edge.
- Metre units; root and mesh at zero, unit scale and applied rotation.
  Blender +Z maps to Godot +Y; Blender +Y maps to Godot -Z.
- **8 source vertices / 24 exported vertices / 12 triangles; one mesh, one surface**.
  The six hard face normals explain corner splitting on export.
- No rig, animation, sockets, moving parts, destruction states or real lights. No explicit LOD;
  automatic LOD disabled only on this already-minimal sample.

## Source, export and material mapping

| Deliverable | Path |
| --- | --- |
| Editable Blender source | `art/source/models/environment/city_ground_finishes_04/city_ground_finishes_04.blend` |
| Explicit export | `art/models/environment/city_ground_finishes_04/city_ground_finishes_04.glb` + `.import` |
| Reusable material | `art/materials/environment/city_ground_finishes_04/short_grass.tres` |
| Original runtime texture | `art/textures/environment/city_ground_finishes_04/short_grass_albedo.png` + `.import` |
| Linked review sample | `scenes/prefabs/environment/city_ground_finishes_04.tscn` |
| Parametric source and checks | `tools/asset_production/city_ground_finishes_04/` |

`author.py` constructs the Blender sample; `texture.py` is the editable deterministic artwork
source. Collection `export_city_ground_finishes_04` contains root `CityGroundFinishes04` and
`CityGroundFinishes04_Mesh`, mesh data `ShortGrassSwatch`. The Principled source material
links the committed PNG using a relative path and never packs it.

`export.py` uses the shared `tools/assets/blender/export_settings.json`, explicit collection
filtering and static animation/skin exclusions. It temporarily disconnects the albedo link
for export, then restores it. Saved GLB import settings map the **short_grass** slot to the
external Godot material. The GLB has **zero embedded images**; Blender and Godot use the same
committed PNG. No cache material edits, editable-child overrides or replacement render meshes.
The existing family sample/check conventions were adapted; shared export settings and canonical
production checks are reused. No shared material-study harness exists, and none was introduced.

Material: opaque/backface-culled, nonmetallic, roughness **0.96**, white albedo multiplier.
Texture: **512 × 512 RGB sRGB albedo**, **2,347 bytes**, lossless import, mipmaps, repeat and
linear mipmap filtering; automatic 3D compression conversion disabled. No normal, ORM or
emission texture is needed, so no tangent-normal orientation conversion applies.

### Surface-tool / UV interface

**Apply `short_grass.tres` to the site/surface owner's geometry, not repeated swatch prefabs.**
Decision 42 leaves generated road/sidewalk/curb/intersection infrastructure with the road tool.
This material neither generates roads nor creates a second site-layout or collision owner.

UV0: **one unit = 4 m**, material UV scale (1,1,1). For flat site geometry:
`UV0 = (local_x - anchor_x, local_z - anchor_z) / 4`; U east/+X, V south/+Z. The centred
sample anchor is (-2,-2). Keep common anchors and uniform metre density across neighbouring
patches, bends and triangulation. Preserve existing flat ground datums. Normalized
0–1-per-segment road UVs need an adapter in that owner; do not stretch one repeat over a garden.
No node scaling, triplanar shader or world-state dependency. Both opposite border samples match
exactly; the GLB validator independently verifies top UVs against Godot-axis vertex positions.

The actual road addon/UV adapter is not present in this checkout. **Live generated-surface
compatibility remains pending**, not claimed from swatch import. Review large-area repeat rhythm
under district lighting; layout-specific edging and patches belong to the site owner.

## Prefab and collision

The wrapper retains `Visuals/Model` as an identity-transform imported PackedScene instance.
Godot assigned fresh model, material, texture, scene and script identities; no sibling UID or
node identity was copied. Resource/scene UIDs are embedded in `.tres`/`.tscn`; the check script
retains its `.gd.uid`. Two headless load/pack/resave rounds preserved exact wrapper bytes/IDs.

The walkable sample has **one continuous 4 × 0.08 × 4 m box**, centred at (0,-0.04,0), under
`Collision/SwatchBody/Shape`, static-world layer 1 / mask 0. Five public physics rays (centre
and inset corners) hit Y=0 with +Y normals; an outside ray misses. Growth patches have no
collision seams. This checks the saved sample datum, not ActorMotion/car handling or networking.
Real sites retain their own collision: do not overlay this sample on an existing floor or add
duplicate swatch colliders. No district/world collision was changed.

## Evidence and validation

- [Hero](city_ground_finishes_04-evidence/hero.png),
  [side](city_ground_finishes_04-evidence/side.png),
  [grass detail](city_ground_finishes_04-evidence/grass_detail.png): **960 × 640**.
- [47 m / 42° overhead](city_ground_finishes_04-evidence/overhead_47m_42deg.png): **1280 × 720**,
  vertical-down perspective, north up. The current 720-pixel evidence cap supersedes the
  historical 800-pixel height without changing camera height or vertical FOV.
- Isolated Blender Cycles CPU, 24 samples, AgX, PNG compression 100, no dithering;
  **17–151 KB per image**. These are **not Godot screenshots**.
- Overhead uses 48 temporary linked sample repetitions over 32 × 24 m. The unchanged Coral
  Courier and Latch GLBs are read-only, original-source-backed scale references, never saved
  or re-exported as part of this asset. The revised overhead, native grass detail and a
  contact sheet of the three non-overhead views were visually inspected: the former
  growth lattice is substantially reduced to a quiet emerald field, without hard borders.
  The coral car and ivory/coral person remain distinct. Moving/shadowed engine readability
  and other palettes remain pending, given the person's small true-overhead footprint.

[validation.json](city_ground_finishes_04-evidence/validation.json) records **zero degenerate
faces / zero non-manifold edges**, unit normals, outward winding, exact envelope/UV checks and
**fresh re-export byte identity**. Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter
**5.2.40**. Godot **4.8.dev7.official.c971f93e7** imports dependencies, resolves the external
material and passes standalone load/physics checks. Explicit owned-script compilation and
plugin-free compiler-mirror load/physics/compilation also pass without warnings/errors.

Five independent texture tests pass: recipe equality, seamless borders, bounded muted green,
no abrupt blade/grit edges and a two-code contrast cap at four texture/minified scales. Pinned
gdstyle passes.
The **initial production run** passed formatting/lint, 14 repository Python tests,
137 GUT tests / 6,523 assertions, GUT import and the negative harness, but exited 1:
compiler setup passed and the aggregate deadline expired after 122/165 scripts, with 43
deadline logs. Its owned script also passed independently. The cumulative review-round
results below supersede that incomplete compiler result; shared deadlines were not changed.

[final_log.txt](city_ground_finishes_04-evidence/final_log.txt) records command/log disposition.
Full-project import has the existing MCP-version warning. Editor normalization exits 0 after
its receipt but emits RID/ObjectDB shutdown diagnostics, consistent with the sibling's retained
empty-editor reproduction; it is a byte-stability observation, not a clean-log pass. Blender's
pinned material/world APIs emit deprecation warnings; its standalone version query also reports
one tiny unfreed allocation. Source/export/render/validation processes exit 0 normally.
The [producer manifest](city_ground_finishes_04-evidence/manifest.json) hashes every delivered
file except itself; scratch logs/reexports/mirrors are outside the repository.

## Review round 1 — P2 repeat suppression

Finding: regular growth-pooling checker/lattice at gameplay height. The original recipe's
unequal shapes were still
recognizable landmarks when repeated; seamless edges alone did not prevent a grid.
`texture.py` now scales the combined broad variation to **18% of the original amplitude**
before RGB quantization. Base colour, smooth patch placement, 512 px resolution, 4 m UV0
interface, material properties and all geometry/collision remain unchanged. No random noise,
shader, larger tile, scene placement or new surface system was introduced.

The previous minimum-five-code minification expectation was counterproductive for this
review direction. Tests now cap every channel at **two sRGB codes** at 512, 64, 16 and 8 px
while preserving exact recipe, border, palette and adjacent-pixel checks. The original
committed texture fails that cap at all four scales; the replacement passes all five tests.
This is a regression guard, not a substitute for the revised camera evidence above.

Regenerated the PNG and all four evidence views; reran headless import, two normalization
roundtrips, standalone and plugin-free-mirror prefab/physics checks, explicit compilation,
gdstyle, canonical checks and Blender validation/fresh export. Source `.blend`, production
GLB, material, prefab and import/UID bytes are unchanged: the source already links the
unpacked external PNG, and fresh GLB export is byte-identical. No source rebuild was needed.
`validation.json` now also records the exact tested texture SHA-256.

This asset's canonical run exited 0: **166/166 scripts**, **14 Python tests**,
**137 GUT tests / 6,523 assertions**, GUT import and the negative harness all pass.
The earlier concrete-associated run exhausted the aggregate compiler deadline (109/166);
its failure is retained in the concrete record, not hidden by this cumulative pass.

Exact rerun: the commands below from `texture.py` onward, **excluding `author.py`**; the
existing scratch `checks/` was moved to `review-round-1/checks-before-review/` first.
One full-project import covered all three changed textures. Raw round-1 logs are in
`C:/tmp/ft/assets/city_ground_finishes_04/review-round-1/`; the import log is in the concrete directory.
The final log linked above retains prior results as history and records this pass separately.
Same-reviewer visual disposition remains pending. Residual periodicity under different
lighting, camera motion and eventual world placement still needs engine review.

## Exact reproduction

From repository root in Git Bash, Pillow 12.3.0 and pinned mise tools. Use a fresh checks output
directory; the canonical runner rejects nonempty output. Never connect to live editor sessions.
Editor-managed resources used direct text authoring and pinned headless load/pack/resave because
live sessions are prohibited and the windowed editor is unavailable. No claim is made that a
separate open editor scene was synchronized.

```sh
N=city_ground_finishes_04
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="tools/asset_production/$N"
S="C:/tmp/ft/assets/$N"
mkdir -p "$S"
python "$T/texture.py"
timeout 120 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/preview.py"
timeout 300 "$G" --headless --editor --path . --import --quit
# Inspect diagnostics; normalization is not claimed to have a clean shutdown log.
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
placement and edge composition; engine camera motion, shadows and all actor/car palette
separation; production movement and multiplayer checks if site collision changes; packaged
builds, sustained GPU/frame pacing and Deck checks. The review-round cumulative compiler runs
pass all scripts; earlier deadline failures remain historical. No queue, shared progress/brief,
project setting, gameplay code, world placement or TODO was changed. No whole-game READY claim.
