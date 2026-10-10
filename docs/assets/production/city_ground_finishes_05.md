# city_ground_finishes.05 — Quiet garden soil

10 October 2026. **Material, source/export and linked swatch delivered; independent review and
world/gameplay/device acceptance pending.** Output type: Material study. Regner's current
production commission supersedes the concept-only wording in the
[family brief](../city_ground_finishes.md); see [commission](commission.md).
Original author: commissioned Codex production worker. Accepting reviewer: pending.
Original deterministic artwork and Blender construction; no downloads, brands, third-party
geometry, generated-image textures or paid sources.

## Design and dimensions

Quiet, matte, low-chroma brown loam with three heavily flattened, unequal earthen washes. Base sRGB
reference **(105,91,78), #695B4E**; actual albedo ranges R **104–106**, G **90–92**, B **77–78**.
No channel varies by more than two code values after review retuning. No gritty soil grains,
cracks, mulch specks,
raked rows, wet highlights, bump/displacement or hazard-like dark puddles. This is a visual
soil finish, not a terrain, friction, planting or weather system.

Recorded demand covers **Northpoint, The Crescents, Terrace Ward, Glassward, Old Quay,
Broadlot and Ironreach**: gardens, planted courts/islands and sparse working-yard margins.
The approved Stage 3 identities and Stage 4 street/open-space contract guide appearance,
not inferred measurements, new plots or district boundaries. Existing flat ground datums stay.
The dark warm soil complements the muted emerald [short grass](city_ground_finishes_04.md),
cool slate [plaza paving](city_ground_finishes_01.md) and grey-green
[service concrete](city_ground_finishes_02.md). All three sibling records and overhead outputs
were read and inspected during initial production; none was changed in that initial pass. The
shared **4 m repeat / 512 px** interface is retained.

The portable swatch is a review sample, **not a garden floor module for world placement**:

- Provisional Godot X/Y/Z dimensions **4.000 × 0.080 × 4.000 m**.
- AABB **(-2,-0.08,-2) → (2,0,2) m**, tolerance ±0.000001 m.
- Surface-centred pivot **(0,0,0)**; flat top at **Y=0**, thickness below that datum.
  This follows the family sample's surface-datum exception, not a raised planting bed.
- Metre units; root/mesh origins zero, unit scale and applied rotation.
  Blender +Z maps to Godot +Y; Blender +Y maps to Godot -Z.
- **8 source vertices / 24 exported vertices / 12 triangles; one mesh, one surface**.
  Six hard face normals explain the exported corner splits.
- No rig, clips, sockets, moving parts, destruction states or real lights. No explicit LOD;
  automatic LOD is disabled only on this already-minimal sample.

## Source, export and material mapping

| Deliverable | Path |
| --- | --- |
| Editable Blender source | `art/source/models/environment/city_ground_finishes_05/city_ground_finishes_05.blend` |
| Explicit export | `art/models/environment/city_ground_finishes_05/city_ground_finishes_05.glb` + `.import` |
| Reusable material | `art/materials/environment/city_ground_finishes_05/quiet_garden_soil.tres` |
| Original runtime texture | `art/textures/environment/city_ground_finishes_05/quiet_garden_soil_albedo.png` + `.import` |
| Linked review sample | `scenes/prefabs/environment/city_ground_finishes_05.tscn` |
| Parametric source and checks | `tools/asset_production/city_ground_finishes_05/` |

`author.py` constructs the Blender sample; `texture.py` is the editable deterministic artwork
source. Collection `export_city_ground_finishes_05` contains root `CityGroundFinishes05` and
`CityGroundFinishes05_Mesh`, mesh data `QuietGardenSoilSwatch`. The Principled source material
links the committed PNG through a relative path and never packs it.

`export.py` loads shared `tools/assets/blender/export_settings.json`, with explicit collection
filtering and static animation/skin exclusions. It temporarily disconnects albedo for export,
then restores the Blender link. Saved GLB import settings remap the **quiet_garden_soil** slot
to the external Godot `.tres`. The GLB has **zero embedded images**; Blender and Godot use the
same committed PNG. No cache edits, editable-child overrides or replacement render meshes.
Existing family sample/check conventions are adapted; shared export settings and canonical
production checks are reused. No shared material-study harness exists; none was added.

Material: opaque/backface-culled, nonmetallic, roughness **0.98**, white albedo multiplier.
Texture: **512 × 512 RGB sRGB albedo**, **2,257 bytes**, lossless import, mipmaps, repeat and
linear mipmap filtering; automatic 3D compression conversion disabled. No normal, ORM or
emission texture is needed, so no tangent-normal orientation conversion applies.

### Surface-tool / UV interface

**Apply `quiet_garden_soil.tres` to the site/surface owner's geometry, not repeated swatches.**
Decision 42 keeps generated road/sidewalk/curb/intersection infrastructure with the road tool.
This delivery neither generates roads nor adds a competing site-layout or collision owner.

UV0: **one unit = 4 m**, material UV scale (1,1,1). For flat site geometry use
`UV0 = (local_x - anchor_x, local_z - anchor_z) / 4`; U east/+X, V south/+Z. The centred
sample anchor is (-2,-2). Keep common anchors and uniform metre density across neighbouring
patches, bends and triangulation; preserve existing flat ground datums. Normalized
0–1-per-segment road UVs need an adapter in that owner; do not stretch one tile over a garden.
No node scaling, triplanar shader or world-state dependency. Opposite texture border samples
match exactly; the GLB validator independently checks top UVs against Godot-axis positions.

The actual road addon/UV adapter is not present in this checkout. **Live generated-surface
compatibility remains pending**, not inferred from swatch import. Review repeat rhythm under
district lighting; site boundaries, edging and applied planting patches remain layout-owned.

## Prefab and collision

Saved `Visuals/Model` is an identity-transform imported PackedScene instance. Godot assigned
fresh model/material/texture/scene/script identities; no sibling UID or node identity was copied.
Resource/scene UIDs are embedded in `.tres`/`.tscn`; the check script has its `.gd.uid` sidecar.
Two headless load/pack/resave rounds preserved exact wrapper bytes/IDs.

The walkable review sample has **one continuous 4 × 0.08 × 4 m box** centred at (0,-0.04,0),
under `Collision/SwatchBody/Shape`, static-world layer 1 / mask 0. Five public physics rays
(centre and inset corners) hit Y=0 with +Y normals; an outside ray misses. Soil variation has
no collision seams. These checks establish the sample collider/datum, not production
ActorMotion/car handling or networking. Real sites retain their collision: never overlay this
sample on an existing floor or add duplicate swatch colliders. No world collision was changed.

## Evidence and validation

- [Hero](city_ground_finishes_05-evidence/hero.png),
  [side](city_ground_finishes_05-evidence/side.png),
  [soil detail](city_ground_finishes_05-evidence/soil_detail.png): **960 × 640**.
- [47 m / 42° overhead](city_ground_finishes_05-evidence/overhead_47m_42deg.png): **1280 × 720**,
  vertical-down perspective, north up. The current 720-pixel cap supersedes the historical
  800-pixel height without changing camera height or vertical FOV.
- Isolated Blender Cycles CPU, 24 samples, AgX, PNG compression 100, no dithering;
  **12–61 KB per render**. These are **not Godot screenshots**.
- Overhead uses 48 temporary linked sample repetitions over 32 × 24 m. Unchanged Coral Courier
  and Latch GLBs are read-only, original-source-backed scale references, never saved or
  re-exported here. The revised overhead and a contact sheet of the three other views were
  visually inspected: a near-uniform warm field replaces the faint broad patch rhythm,
  without hard tile seams or speckles; the coral car and ivory/coral person remain distinct.
  Tiny true-overhead actor footprints, other palettes and moving/shadowed readability
  still need engine review; no authored garden boundary is relied on to mask this change.

[validation.json](city_ground_finishes_05-evidence/validation.json) records **zero degenerate
faces / zero non-manifold edges**, unit normals, outward winding, exact envelope/UV checks and
**fresh re-export byte identity**. Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter
**5.2.40**. Godot **4.8.dev7.official.c971f93e7** imports dependencies, resolves the external
material and passes standalone load/physics checks. Explicit owned-script compilation and
plugin-free compiler-mirror load/physics checks also pass without warnings/errors.

Five independent texture tests pass: exact recipe equality, seamless borders, bounded muted
earth colour, no abrupt grit/crack edges and a two-code contrast cap at four texture/minified
scales. Pinned gdstyle
passes. The **initial production run** exited 0: formatting/lint, **all 166 script compilations**,
**14 repository Python tests**, GUT import, **all 137 GUT tests / 6,523 assertions**, and the
negative-test harness. There are **zero aggregate compiler deadline failures** in this run.
The sibling runs' historical full-suite failures are not attributed to this successful run.

[final_log.txt](city_ground_finishes_05-evidence/final_log.txt) retains concise log disposition.
Full-project import emits the existing MCP-version warning. Editor normalization exits 0 after
its passing receipt but emits RID/ObjectDB shutdown diagnostics, consistent with the sibling's
retained empty-editor reproduction; this is a byte-stability observation, not a clean-log pass.
Pinned Blender material/world APIs emit deprecation warnings; the standalone version query
reports one tiny unfreed allocation. Source/render/validation processes exit 0 normally.
The [producer manifest](city_ground_finishes_05-evidence/manifest.json) hashes every delivered
file except itself. Scratch logs/reexports/mirrors stay outside the repository.

## Review round 1 — P3 repeat suppression

Finding: faint broad soil-repeat rhythm. The original recipe's unequal shapes were still
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
`C:/tmp/ft/assets/city_ground_finishes_05/review-round-1/`; the import log is in the concrete directory.
The final log linked above retains prior results as history and records this pass separately.
Same-reviewer visual disposition remains pending. Residual periodicity under different
lighting, camera motion and eventual world placement still needs engine review.

## Exact reproduction

From repository root in Git Bash, Python with Pillow 12.3.0 and pinned mise tools. Use a fresh
checks output directory; the canonical runner rejects nonempty output. Never connect to live
Blender/Godot sessions. Editor-managed resources used direct text authoring followed by pinned
headless load/pack/resave because live sessions are prohibited and the windowed editor is
unavailable. No claim is made that a separate open editor scene was synchronized.

```sh
N=city_ground_finishes_05
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
timeout 180 "$G" --headless --path "$S/checks/script-checks/compiler-project" --script "res://$T/check_prefab.gd"
timeout 120 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
python "$T/manifest.py" --write
python "$T/manifest.py"
```

## Remaining acceptance

Independent technical/art review; actual generated-surface UV integration; saved district
placement/edging; engine camera motion, shadows and all actor/car palette separation;
production movement and multiplayer checks if site collision changes; packaged builds,
sustained GPU/frame pacing and Deck validation. No queue, shared progress/brief,
project setting, gameplay code, world placement or TODO was changed. No whole-game READY claim.
