# city_parking_furniture.02 — Parking-sign assembly reference

10 October 2026. **Saved assembly, derived artwork/material and bounded checks delivered;
independent review and world/gameplay/device acceptance pending.** Commissioned implementation
worker on `lane/a-park2` produced this handoff. Supervisor/reviewer owns acceptance; world
integration owns placement. The resumed [commission](commission.md) supersedes historical
concept-only restrictions in the [family brief](../city_parking_furniture.md).

Inputs: [approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), existing
[low hardware](city_sign_supports_02.md) and [Broadlot parking artwork](d07_retail_graphics_03.md).
This is an **assembly reference, not another model**. No new source `.blend`, GLB, wall panel,
posts, collider geometry or world placement is introduced.

## Design and approved interface reconciliation

One low freestanding **P / ZONE A** panel, reusing the complete existing twin-post petrol
hardware. The delivered Broadlot parking artwork is 61:41 on a wall panel, whereas this
record explicitly requires the 48:13 freestanding low panel. Before implementation the
supervisor approved an owned derived **48:13 recomposition**, preserving the same P / ZONE A
content, palette and typography. Stretching/cropping the wall texture, stacking wall hardware
or modifying either dependency was not approved and was not done.

The parking P is uniformly scaled from the earlier original path. ZONE and A reuse the
existing family capital paths, arranged horizontally; the single small lime ticket and thin
ivory underline remain. The owned recipe imports the existing parking recipe's Z path and
family palette/letter definitions read-only. This is the same original Broadlot design in a
carrier-compatible layout, not a competing city parking identity. No external fonts, downloads,
real brands, paid assets, image-to-mesh, generated runtime geometry or runtime hierarchy
construction. **A remains provisional copy**, not a selected parking area, payment mechanic,
traffic priority, navigation command, interaction or vehicle-count rule.

| Interface | Existing/provisional hardware value |
| --- | --- |
| Overall Godot X/Y/Z | **1.60 × 1.35 × 0.40 m** |
| AABB | **(-0.80,0,-0.20) → (0.80,1.35,0.20) m** |
| Ground pivot | **(0,0,0)**, centred between feet, ground at Y=0 |
| Panel body | Width 1.60 m; bottom Y=0.80, top Y=1.35 m |
| Front artwork face | **1.44 × 0.39 m**, bottom Y=0.88, top Y=1.27 m |
| Artwork plane | **Z=-0.071 m**, recessed behind the original frame lip |
| Safe-copy rectangle | **1.38 × 0.33 m**, centred; 30-pixel perimeter at authored resolution |
| UV0 | One complete **48:13** image, no atlas/repeat/crop/scale/offset |
| Tolerances | Envelope/imported bounds 0.001 m; source/binary coordinates 0.00001 m |

These are the hardware owner's provisional measurements, not dimensions inferred from a
concept raster. Unit scale, metre units and ground identity remain intact. Blender +Z up /
+Y front maps once to Godot +Y up / -Z front. Seen from the front, screen-right is local -X:
U=(0.72-X)/1.44; imported V=(1.27-Y)/0.39. Copy is upright and unmirrored. Rounded corners clip
only petrol background. No corrective root/mesh transform is used.

## Source, outputs, materials and reuse

- [Saved assembly](../../../scenes/prefabs/environment/city_parking_furniture_02.tscn)
  inherits `scenes/prefabs/environment/city_sign_supports_02.tscn` at identity.
- [Artwork recipe](../../../tools/asset_production/city_parking_furniture_02/author.py):
  Python 3.14.2 / Pillow 12.3.0, original paths at 3× resolution, one Lanczos reduction.
- Texture: `art/textures/environment/city_parking_furniture_02/parking_zone_low_albedo.png`,
  **1440 × 390 RGB**, opaque sRGB, with normalized `.import`. Lossless import, mipmaps on,
  automatic 3D recompression off. No normal/ORM/emission maps or embedded images.
- Material: `art/materials/environment/city_parking_furniture_02/parking_zone_low.tres`.
  White multiplier, roughness **0.56**, metallic **0**, backface-culling, opaque, no emission;
  linear mipmapped filtering and clamp, identity UV transform.
- Shared source: `art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend`;
  collection **export_city_sign_supports_02**, root **CitySignSupports02**, two source meshes.
- Shared GLB: `art/models/environment/city_sign_supports_02/city_sign_supports_02.glb`.
  Its import settings, source, linked wrapper, mesh resources and collision are unchanged.
- [Source/binary validator](../../../tools/asset_production/city_parking_furniture_02/validate.py)
  invokes the hardware owner's entire existing audit, redirecting only its receipt/export
  output constants to scratch. All original assertions and `__file__` resolution remain.
  The hardware owner's `export.py` uses `tools/assets/blender/export_settings.json`; no
  duplicate export contract or private carrier source is introduced.
- [Preview recipe](../../../tools/asset_production/city_parking_furniture_02/preview.py) opens
  the shared source read-only and applies the owned material in memory, never saving it.

Palette remains quiet petrol **#102C3C**, coral **#FF725D**, warm ivory **#F6F1DC**, lime
**#B8DC6F**. Tests enforce over 80% exact petrol pixels, under 0.4% lime, a fully quiet 30-pixel
perimeter and independent P-counter/letter/ticket landmarks. Hardware materials remain
`support_petrol`, `recess_gasket`, `mount_metal`, with only `sign_face` replaced.

## Saved assembly and collision contract

`Visuals/Model` is the inherited **identity-transform imported instance**. The sole override is:

`Visuals/Model/CitySignSupports02/CitySignSupports02_ArtworkCarrier:surface_material_override/0`

Carrier slot 1 `mount_metal`, the hardware mesh and every other material remain unchanged.
This uses the authorized static, non-identity-sensitive **editable-child face-slot exception**
in [assets.md](../../assets.md#prefabs-and-authored-placement). No copied/localized mesh,
global material override, detached imported children or duplicate hardware. After initial
normalization, **two further load/pack/save roundtrips preserve every scene byte**, including
node identities, parent-ID paths and resource UIDs. A fresh runtime independently checks the
same hierarchy, mesh resource identity, bounds, all five surfaces and exactly one override.

Prefab UID **uid://op1n8uo08w0l**, material UID **uid://sjxrf02ltlcj**, texture UID
**uid://8dsryi6w6y0t**. Existing wrapper UID **uid://bi65yynmg6q4t** and GLB UID
**uid://bcgx64ss75j2s** remain unchanged. Text scene/material UIDs are inline; texture `.import`
and the owned GDScript `.gd.uid` are committed. There is no `.tscn.uid` sidecar.

Collision is inherited, not redesigned: **one BoxShape3D (1.60,1.35,0.40) m**, at
**(0,0.675,0)** under `Collision/Body/Shape`; static-world layer **1**, mask **0**. Shape
resource identity matches the base. The full box intentionally blocks the visual gap below
the panel; do not treat it as an underpass. The inherited blocker remains separate from
visuals. Headless physics rays confirm centre blocking at Y=0.7 m, clear bypass at X=0.9 m,
and clear overhead at Y=1.6 m. No new motion/network/authority code is added. Existing
hardware ActorMotion evidence remains historical dependency evidence, not a newly run actor
or multiplayer test of this variant.

Place this assembly **instead of**, not overlaid on, the blank low-panel prefab. Place the
root at finished ground and rotate the complete assembly toward the intended frontage.
No mounting socket adapter is required: the existing face/UV interface owns attachment.
Keep it outside turning areas, foot passages, escape routes and junction sightlines. This
handoff does not decide parking aisle dimensions or saved district placements. No rigs,
clips, state variants, destruction, interactions, navigation, real lights or bespoke LODs;
existing hardware import defaults remain unchanged.

## Evidence and validation

[Hero](city_parking_furniture_02-evidence/hero.png) ·
[Side](city_parking_furniture_02-evidence/side.png) ·
[Face detail](city_parking_furniture_02-evidence/detail.png) ·
[47 m / 42° overhead](city_parking_furniture_02-evidence/overhead_47m_42deg.png).

All four final renders were self-inspected. Isolated Blender Cycles CPU, 24 samples/denoising,
AgX, **1280×720 RGB**, PNG compression 95, no output dithering; each below 176 KB. Hero and
side show the complete original frame, posts and feet; detail shows upright copy and the
recessed face. The initial side view was too tight and was widened before final evidence.
The fixed overhead is vertical-down perspective at Blender **(0,10,47)**, **42° vertical FOV**,
north-up. The hardware remains unscaled at ground. Its roughly 33-pixel-wide silhouette is
quiet; **P / ZONE A is not reliably readable at gameplay scale**. At the camera centre the
vertical face is edge-on. This is optional close-range dressing, never the only essential
wayfinding cue. No engine lighting, populated-city visibility or device acceptance is implied.

[validation.json](city_parking_furniture_02-evidence/validation.json) records:

- Shared hardware **2,448 triangles**, **1,244 source vertices**, **1,596 split GLB vertices**,
  **2 meshes / 5 surfaces**. **No new geometry.**
- **Zero degenerate source faces/export triangles**, **zero nonmanifold source edges**,
  positive source volume, outward binary winding, unit source/export normals, applied
  transforms, correct ground pivot and source/binary/imported bounds.
- Fresh reopened-source export with Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter
  **5.2.40** is **byte-identical**: **70,712 bytes**, SHA-256
  `022dd559334d79c482182083be775c692ab4adf2a5277d3fb7ca7ec266ec76b7`.
- All **28 imported face UV vertices** pass; maximum UV error **0.0000306765238444** is below
  the existing compressed-import tolerance **0.00005** (under 0.073 horizontal texel).
  Source/binary UV checks retain the stricter 0.00001 tolerance.
- **Three artwork tests pass**, including a fresh byte-identical PNG and independent content,
  format, quiet-margin and palette-density expectations.
- Godot **4.8.dev7.official.c971f93e7** import and final import: **no ERROR/SCRIPT ERROR**.
  Fresh non-editor dependency/hierarchy/material/collision load: **no errors or warnings**.
- Two byte-stable scene roundtrips, owned GDScript check-only compilation,
  **gdstyle fmt --check** and **gdstyle --max-line-length 100 --max-warnings 0** pass.

The [manifest](city_parking_furniture_02-evidence/manifest.json) hashes every produced payload
except itself and records unchanged dependencies. [Final concise log](city_parking_furniture_02-evidence/final.log)
retains command exits and exact final diagnostics. Scratch exports, intermediate renders and
raw logs stay under `C:/tmp/ft/assets/city_parking_furniture_02/`, outside the repository.

## Exact reproduction and diagnostics

From repository root in Bash:

```sh
bash tools/asset_production/city_parking_furniture_02/verify.sh
# Non-mutating payload/dependency/receipt consistency check:
python tools/asset_production/city_parking_furniture_02/record.py
```

`verify.sh` records the exact executable/argument sequence: authoring, three artwork tests,
shared source/binary audit and fresh GLB comparison, four renders, pinned import, headless
normalization and two further roundtrips, final import, fresh dependency load, compilation,
format and lint, then receipt/hash regeneration. Blender uses the prescribed Windows 5.2
executable, audio-null environment, factory startup, four threads, Python exit code and
900-second timeout. Godot is resolved through mise; imports are bounded to 300 seconds,
other checks to 180 seconds. Logs use UTF-8. No `production_checks.py` ran (decision 52).

The final normalization process exits 0 with successful roundtrip assertions but retains the
known pinned headless-editor **RID/ObjectDB shutdown leaks and scan-aborted warning**. Exact
lines are retained, not called a clean editor shutdown; the receipt checker permits only the
specific observed shutdown RID types and rejects script, assertion, dependency or UID errors.
Final imports retain the known MCP 4.8 compatibility warning but no errors. Blender's preview
emits future `use_nodes` deprecation warnings. Fresh runtime/compilation/style are clean.

An early runtime invocation before the post-normalization import warned about the newly
assigned material UID; the final import registered it and the fresh process is warning-free.
The initial full verification reached receipt checking before this handoff contained the
required final hash and correctly rejected the incomplete doc; final receipt checks passed
after the handoff was completed. No dependency was changed to address these observations.
CLI-only requirements mandated direct-file authoring plus headless resource normalization;
no live owner Blender/Godot sessions were used or claimed synchronized.

## Remaining acceptance

1. Independent technical/art review of this exact committed candidate.
2. Final copy/zone selection and saved placement, preserving walking/driving clearance,
   actor/target visibility and sparse forecourt composition. Vehicle movement and populated
   world query checks remain pending; no actual placement is delivered.
3. Actual renderer filtering, district lighting and gameplay-camera readability/occlusion.
   This small upright sign must not carry mandatory overhead instructions.
4. Future carrier reexport identity retention, separate-process multiplayer implications of
   placed collision, packaged dependency checks, repeated-instance cost and sustained Deck
   performance remain downstream. No new gameplay/device proof is claimed.
5. Existing headless-editor shutdown diagnostics remain a tooling limitation.

There are no earlier same-lane siblings. Existing hardware and parking-art handoffs do not
list this assembly as an unproduced pending item; their general world/artwork review gates
remain unresolved, so no sibling doc/manifest changes are warranted. No queue, shared progress,
family brief, catalogue, project setting, world scene or TODO was changed. The registry, not
this handoff, tracks other unproduced family work.
