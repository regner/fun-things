# d06_shopfront_blocks.01 — Short-row assembly reference

**Assembly/interface candidate delivered; independent review and world placement pending.**
Production authority: current per-record commission and [production commission](commission.md),
which supersede the family brief's historical concept-only restriction. Producer: commissioned
implementation worker, `lane/a-sfront`. This is an **assembly reference**, not another shop mesh
or a claim of a placed/accepted district. Family: [Signal Row shopping blocks](../d06_shopfront_blocks.md).

## Design and provisional dimensions

Two existing wide fitted shops flank a recessed compact fitted shop, producing a **2–1–2 frontage
rhythm**, unequal setbacks, two visible passages and staggered rear edges. Wide roofs are 9 m
deep; the compact roof is 6.4 m deep. This meets the brief through massing and negative space,
not recolouring. The shared muted-plum walls, quiet blue roofs and broad blank fascia carriers
are unchanged. Selective cyan/magenta tenant graphics belong to the separately delivered
[commercial fascia artwork](d06_commercial_graphics_02.md); this neutral interface reference
neither chooses tenants nor adds district-specific material overrides.

References inspected: [district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[Signal Row v03](../../concepts/districts-v1/signal-row.md) and its
[common contract](../../concepts/districts-v1/brief-contract.md). This is a northern short-block
alternative, **not** a replacement for the continuous southern shopping parade. No district
boundary, road, placed identity, street width or site allocation is changed.

The following assembly translations and clearances are **provisional authored values** under
the standing dimensional rule, not measurements from concept pixels. Existing building
sizes/interfaces retain their source owners' contracts.

| Saved path under `Shops` | Reused fitted prefab | Translation X/Y/Z, m | Footprint X/Z, m | Front / rear Z, m |
| --- | --- | --- | --- | --- |
| `WestWide` | `city_small_shop_shells_02_fitted.tscn` | (-13.7, 0, -1.25) | 12.8 × 9 | -5.75 / 3.25 |
| `RecessedCompact` | `city_small_shop_shells_04_fitted.tscn` | (-0.5, 0, 2.55) | 6.4 × 6.4 | -0.65 / 5.75 |
| `EastWide` | `city_small_shop_shells_02_fitted.tscn` | (13.7, 0, 0.75) | 12.8 × 9 | -3.75 / 5.25 |

- Root pivot `(0,0,0)` is ground-centred on the combined **structural** envelope:
  X [-20.1,20.1], Z [-5.75,5.75]. Ground Y=0; all shops face local -Z, all bases unit scale.
- Full fitted visual AABB: **(-20.18,0,-6.85) → (20.18,5.05,5.83) m**;
  width/height/depth **40.36 × 5.05 × 12.68 m**. Validation tolerance ±0.002 m.
- Canopies project 1.10 m from their facades; reserve the inherited 1.20 m installation
  depth. The west installation limit is Z=-6.95, not the bare footprint's Z=-5.75.
- West passage: structural X [-7.3,-3.7], **3.60 m** wide; clear between visual plinth/coping
  extents **3.44 m**. East passage: structural X [2.7,7.3], **4.60 m**; visual **4.44 m**.
- Front setbacks relative to the western frontage: compact **5.10 m**, eastern **2.00 m**.
  Rear walls step from Z=3.25 to 5.75 to 5.25; the rear connection requires additional
  downstream open ground, rather than implying building interiors or rear doors.

## Saved reference and interface contract

Delivery: `scenes/prefabs/environment/d06_shopfront_blocks_01.tscn`.
Its only visible content is **three linked, unchanged fitted prefab instances**. The scene
owns their placement; no script constructs runtime geometry or scene hierarchy. Every nested
`Visuals/Model` remains an identity-transform imported GLB instance. There are no editable-child
or material overrides in this assembly and no copied mesh resources.

Four root-local `Marker3D` nodes under `Interfaces` document pedestrian connection reservations:

| Marker | Translation X/Y/Z, m |
| --- | --- |
| `WestPassageFront` | (-5.5,0,-8) |
| `WestPassageRear` | (-5.5,0,8) |
| `EastPassageFront` | (5,0,-8) |
| `EastPassageRear` | (5,0,8) |

Markers have identity rotation/scale; they identify ground points, **not directed traffic links**,
spawn/exit approvals or navigation. Consumers may translate/rotate the whole reference on flat
terrain, but must not stretch it. Recheck clearances after changing a shop's relative placement.
There is no saved road, floor, sidewalk or rear-court paving: those surfaces belong to the road
and world tooling. The Blender studio plane is unsaved evidence only, not a delivered surface.

### Collision ownership

Inherited collision remains one layer-1/mask-0 `StaticBody3D` box per shop: each wide box is
12.8 × 4.3 × 9 m, the compact box 6.4 × 4.3 × 6.4 m, all centred 2.15 m above their base.
The fitted prefabs already disable their redundant leaf/window colliders. The row introduces
**zero new collision shapes**; exactly three inherited shapes are enabled. Canopies and trim
remain decorative. Apparent door recesses are solid exterior footprints; no interiors,
opening doors, rooftop traversal or new gameplay state is implied.

Native public physics queries test the actual saved assembly with a **radius-0.35 m,
height-1.8 m capsule**: 12 bidirectional passage sweeps (centre and both near-edge tracks),
two rear cross-link sweeps, and three interior overlap checks. **14/14 sweeps clear**;
each shop blocks exactly once. Near-edge passage tracks reserve 0.10 m beyond capsule radius
from the structural wall. Rear sweeps at Z=6.3 reserve 0.20 m beyond capsule radius from the
furthest structural rear wall. These are bounded shape-query proofs, not production actor
movement, floor continuity, car-turning or multiplayer evidence.

## Reused Blender sources, exports and materials

All seven unique model dependencies already existed on `main` when work began:

- [Wide shop .02](city_small_shop_shells_02.md), used twice.
- [Compact shop .04](city_small_shop_shells_04.md), used once.
- Shared [canopy .01](city_shop_fittings_01.md), [fascia .02](city_shop_fittings_02.md),
  [single surround .03](city_shop_fittings_03.md), [display window .05](city_shop_fittings_05.md)
  and [single leaf .06](city_shop_fittings_06.md), each used five times through the fitted shops.

Each source remains under `art/source/models/environment/<owner>/<owner>.blend`; its explicit
GLB and import sidecar remain under `art/models/environment/<owner>/`. The single surround
and leaf use their `_single.glb` variants. Exact paths, named export/variant collections and
hashes are recorded in `validation.json`; the complete read-only dependency inventory is in
`manifest.json`. No source, export, material, fitting mount or shared prefab was modified.

**No per-assembly `.blend`, GLB, author.py or export.py is appropriate:** the common brief's
Assembly/Interface reference rule explicitly requires composition of existing prefabs, not
another arbitrary mesh. Fresh assembly GLB reexport comparison is consequently **not applicable**.
Source/export reproducibility remains with the linked producer handoffs. `validate.py` performs
a fresh read-only topology/normal/count audit of all seven original sources, not a second export
implementation. Materials are the unchanged opaque Principled/glTF materials; no new texture,
font, branding, external download, rig, animation, light, destruction state or LOD is introduced.

## Validation and evidence

[`validation.json`](d06_shopfront_blocks_01-evidence/validation.json) records source, raw GLB
accessor, saved-scene and physics results. Instance-weighted totals (not unique memory cost):

- **54,616 triangles; 27,632 source vertices; 29,300 exported split vertices.**
- **28 linked GLB instances**, comprising three shells and 25 fittings; **202 mesh instances,
  207 material surfaces**. Godot and raw-GLB weighted mesh/surface totals agree.
- **Zero degenerate source faces or non-manifold edges**, consistent winding and unit-length
  source corner normals; finite vertices, applied rotation/scale and triangle-area checks pass.
- Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`; pinned Godot
  **4.8.dev7.official.c971f93e7**. Recursive resource loading resolves all dependency UIDs/paths.
- Two post-normalization load/pack/save roundtrips preserve exact scene bytes and saved identities.
  The final scene is **1,642 bytes**, SHA-256
  `555c32009bdca87098a9d5a24b379e12b4eb740130da70cf8a5fce5f1c3e07b9`.
- Owned GDScript formatting/lint and runtime checks pass. Final headless import has no
  `ERROR` or `SCRIPT ERROR` lines. No unrelated import/UID changes were produced.

Four isolated Blender renders, **1280×720**, Cycles CPU / 24 samples / AgX, PNG compression 95,
zero dithering to keep evidence lean:
[hero](d06_shopfront_blocks_01-evidence/hero.png),
[side/rear](d06_shopfront_blocks_01-evidence/side.png),
[passage detail](d06_shopfront_blocks_01-evidence/detail.png),
[47 m / 42° overhead](d06_shopfront_blocks_01-evidence/overhead_47m_42deg.png).
The overhead is vertical-down perspective, fixed north-up, **42° vertical FOV**, height 47 m.
The render script reads actual model translations from the validated saved scene receipt rather
than maintaining another layout. All four final images were self-inspected: broad roof depths,
setbacks and both passage openings remain legible. Blank fascia faces and doors are roof-occluded
at overhead scale; wall copy must not carry essential navigation. These are not engine/gameplay
screenshots or populated-world visual acceptance.

### Exact reproduction (Git Bash, repository root)

No live Blender/Godot session was touched. The windowed editor is unavailable; explicitly
permitted direct text scene authoring was followed by isolated headless normalization. This
cannot synchronize any separate open editor. Verify the manifest before regenerating receipts.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=C:/tmp/ft/assets/d06_shopfront_blocks_01
mkdir -p "$T"
python tools/asset_production/d06_shopfront_blocks_01/manifest.py --verify
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --editor --path . --script res://tools/asset_production/d06_shopfront_blocks_01/check.gd -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script res://tools/asset_production/d06_shopfront_blocks_01/check.gd
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d06_shopfront_blocks_01/validate.py
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d06_shopfront_blocks_01/render.py
timeout 30 "$(mise which gdstyle)" fmt --check tools/asset_production/d06_shopfront_blocks_01/check.gd
timeout 30 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/d06_shopfront_blocks_01/check.gd
```

Only after an intentional evidence refresh and review, run `manifest.py` without `--verify`.
Scratch logs stay under `$T`; one concise [`final.log`](d06_shopfront_blocks_01-evidence/final.log)
records results and diagnostic classification. Headless editor normalization exits 0 but emits
known editor/plugin shutdown RID/ObjectDB leak and scan-abort diagnostics; this is **not** a
clean editor-shutdown claim. Separate runtime validation exits 0 without errors; import has only
the existing toolkit-version warning. Initial owned long-line lint warnings were fixed.

Historical pre-interruption validation, before the updated common brief's decision 52:
canonical production checks passed when given explicit mise tool paths and Python UTF-8 mode
(17 Python tests, 165 GUT tests / 6,918 assertions, script lint/format/compilation and negative
control). Earlier ambient-tool attempts failed version detection/Windows text decoding. The
current rule excludes that broad suite for unplaced assets; it was **not rerun on resume**, and
its passing tests are not substituted for this asset's own validation.

## Remaining acceptance

Independent art/technical review; actual actor motion/aim and car clearances; floor/road/sidewalk
integration and rear-route continuation; authoritative/predicted/network behavior; populated
native gameplay-camera readability; selected district placement and derived-data updates;
packaged-build and sustained repeated-instance GPU/Deck performance remain **pending**.
This reference does not authorize world placement, select tenant artwork, close gameplay gates,
or mark the shared register READY. No family-progress checklist is maintained here.
