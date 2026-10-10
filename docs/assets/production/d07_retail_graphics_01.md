# d07_retail_graphics.01 — Retail fascia art

10 October 2026. **Artwork, material and linked prefab delivered; independent review and
world/gameplay acceptance pending.** Commissioned implementation worker on `lane/a-d07`
owns original artwork and bounded integration; supervisor/reviewer owns acceptance and the
world integrator owns placement. The resumed commission supersedes the concept-only brief.

Inputs: [family brief](../d07_retail_graphics.md),
[Broadlot concept](../../concepts/districts-v1/broadlot.md),
[selected district 07](../../concepts/districts-v1/map-context.md#district-07),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md#broadlot--big-roofs-bigger-empty-spaces),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[shared fascia hardware](city_shop_fittings_02.md), and earlier same-lane
[base](d07_sign_island_01.md) / [support](d07_sign_island_02.md) deliveries.

## Design and inherited dimensions

One reusable entrance-fascia artwork: **EVERYTHING YOU / NEARLY NEEDED**. The exact phrase is
from the brief, still candidate copy rather than a selected real brand. Original rounded
capital paths sit beside an almost-closed coral shopping bag; its missing upper-right corner
and one small lime ticket echo the joke. The petrol field stays over 78% of the texture;
lime occupies under 0.3%. No dense promotional lists, roof carpet, repeated arrows, prices,
illumination behavior or traffic/parking rules. The two lines form one phrase, not two tenants.

The quiet petrol, coral entrance emphasis and sparse lime fit Broadlot and the sign-island
hardware without copying its geometry or recolouring it. Lime is an accent, not essential
information. This is a **single complete artwork/material/prefab set**, not a demand for many
sign placements or a replacement for the building's existing coral architectural band.

The standing hardware-reuse rule applies: **no duplicate Blender carrier or GLB is created**.
The Blender-sourced face is supplied by accepted `city_shop_fittings_02`. Its source, exporter,
mesh identities, UVs, five hardware materials and import metadata remain unchanged. This
uses the same saved face-only exception as delivered commercial artwork, not a new runtime API.

| Interface | Inherited value |
| --- | --- |
| Whole fascia, Godot X/Y/Z | **3.200 × 0.800 × 0.140 m** |
| Godot local AABB | **(-1.600, -0.400, -0.140) → (1.600, 0.400, 0)** |
| Pivot | Wall-contact centre **(0,0,0)**, not ground-centred |
| Artwork face | **3.000 × 0.600 m**, rounded corners, plane **Z=-0.128 m** |
| Safe content region | Centred **2.940 × 0.540 m**; 20-pixel petrol perimeter |
| UV0 | Godot/glTF U=.5-X/3, V=.5-Y/.6; top-left image convention |
| Dimensional tolerance | ±0.001 m in binary/imported checks; shared source audit uses 1e-6 m |
| Proposed mounting | Flat entrance bay, centre **3.8 m** above ground; bottom **3.4 m** |

Mounting height is a **provisional installation suggestion**, not saved city placement.
Use at a selected entrance or compact retail frontage with a flat backing area at least
3.2 × 0.8 m. Do not stretch it across the giant store, rotate it onto the roof for readability,
stack it with an existing fascia, or treat this as proof of attachment to the entrance annex.
World integration must verify that bay against the actual building geometry and trim.
District gross dimensions (6.84 ha / 474.5 × 234.8 m) are context, not asset allocation.

Blender +Z up / +Y front maps once to Godot +Y up / -Z front. From the front, local +X
appears screen-left; UV orientation makes the delivered PNG read upright and unmirrored.
The artwork slot is one **28-corner source n-gon / 26 exported triangles / 28 vertices**.
Only that front face gets art; all thickness, rear surfaces, trim and rails stay unchanged.

## Source, runtime outputs and provenance

- Editable artwork recipe: `tools/asset_production/d07_retail_graphics_01/author.py`.
  Python 3.14.2 / Pillow 12.3.0, drawn at 3× and filtered once with Lanczos. Original
  paths and icon; no downloaded images, fonts, purchased content, real brands or AI meshes.
- Texture: `art/textures/environment/d07_retail_graphics_01/retail_fascia_albedo.png`
  plus pinned `.import`, **2000 × 400 RGB**, 5:1, opaque sRGB albedo. One complete face,
  not a tile/atlas. Lossless compression, mipmaps enabled, auto-3D compression disabled.
- Material: `art/materials/environment/d07_retail_graphics_01/retail_fascia.tres`.
  White albedo multiplier, roughness **0.56**, metallic **0**, opaque/back-culled,
  linear mipmapped filter, repeat disabled, no emission or additional maps.
- Prefab: `scenes/prefabs/environment/d07_retail_graphics_01.tscn`.
- Existing source: `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`.
  Collection **export_city_shop_fittings_02**, source root **city_shop_fittings_02**.
- Existing export: `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb`.
  The existing hardware exporter owns its historical explicit export contract; this asset's
  validator calls it read-only on the reopened source and writes only to scratch. No private
  export settings, redundant `export.py`, new `.blend`, GLB or embedded texture are required.

| Artwork role | sRGB |
| --- | --- |
| Quiet petrol field | `#102C3C` |
| Bag / primary phrase | `#FF725D` coral |
| Sparse ticket | `#B8DC6F` lime |
| Secondary phrase / underline | `#F6F1DC` warm ivory |

These are texture colours, not a demand to alter the siblings' linear hardware palette.
Tools `validate.py`, `preview.py` and `check_prefab.gd` follow the delivered
`d06_commercial_graphics_01` same-carrier audit/render conventions, with this asset's
binary UV/normal checks, original art, lean render settings and two-roundtrip receipt.

## Saved prefab and collision

**Visuals/Model** is the identity-transform linked shared GLB. Exactly one override:

`Visuals/Model/city_shop_fittings_02/fascia_artwork_carrier:surface_material_override/0`

Original slot **fascia_artwork_face** receives `retail_fascia.tres`. No global material
override, embedded mesh, copied vertex data, geometry localizing or runtime composition.
Seven imported mesh resources and all eight surfaces retain their original resource links
and transforms. The other surface of the carrier remains **fascia_mount_metal**.

This explicitly uses the authorized static artwork **editable-child face-slot exception**
in [assets.md](../../assets.md#prefabs-and-authored-placement). After initial normalization,
**two further load/pack/save roundtrips preserve complete scene bytes**, hence identities,
parent-ID paths and dependency UIDs. A fresh non-editor process loads the saved result.
Prefab UID **uid://jmsuaxfymftt**; material UID **uid://cyiwv6f1ab4p8**; texture UID
**uid://yapgiofp4uo2**; shared GLB UID **uid://cdtnvrp3u64wi**. Scene/material UIDs are
inline, texture UID in `.import`, and the checker has its generated `.gd.uid` sidecar.
Future hardware hierarchy changes must retest this override rather than assuming retention.

**No collision**: this is flush wall-mounted/above-head decoration, not a freestanding sign.
The backing building owns blocking. No movement, navigation, inventory, destruction,
authority, network or interaction behavior changes. No rigs, animations, sockets, light
nodes or new LODs; original import LOD settings remain unchanged.

## Evidence and measured validation

[Hero](d07_retail_graphics_01-evidence/hero.png) ·
[Side](d07_retail_graphics_01-evidence/side.png) ·
[Face/trim detail](d07_retail_graphics_01-evidence/detail.png) ·
[47 m / 42° overhead](d07_retail_graphics_01-evidence/overhead_47m_42deg.png).

All four final images and the artwork were self-inspected. Isolated Blender Cycles CPU,
24 samples/denoised, AgX, **1280×720**, PNG compression **95**, render dithering off,
each below 400 KB. No image quantization or painted corrections.
Hero/side show the complete fascia and upright copy; detail intentionally crops into the
bag and first letters to inspect the seam and smooth edges. Preview temporarily overrides
only the source face material in memory; it never saves the shared source or exports it.

Overhead is vertical-down, north-up perspective at Blender **(0,10,47)**, **42° vertical
FOV**, with fascia root temporarily at **(0,0,3.8)**. It is deliberately off-axis, unscaled
and not tilted. At around **68×6 screen pixels**, the fascia is a small coloured strip;
**neither phrase nor icon reliably identifies an entrance from the gameplay camera**.
More texture resolution cannot fix this. This close-range dressing must not carry essential
wayfinding: the architecture, coral entrance band and broad sign-island silhouette supply
larger cues, whose actual placement/readability remains downstream. No Godot visual acceptance
is inferred from the Blender previews, and no giant billboard was added to fake readability.

[validation.json](d07_retail_graphics_01-evidence/validation.json) records:

- Shared carrier: **836 source vertices**, **1,072 GLB vertices**, **1,656 triangles**,
  **seven meshes / eight surfaces**, five unchanged hardware materials.
- **Zero degenerate faces/triangles**, **zero nonmanifold edges**, positive closed component
  volumes, finite positions, applied transforms, metre units and unit-length source normals.
- Actual GLB normal maximum length error **1.024e-7**; binary AABB matches the literal
  expected envelope. Source and all **28 actual exported face UV vertices** pass orientation
  checks; source geometry is not inferred from the prefab bounds alone.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**: reopened-source
  fresh export is **byte-identical**, **45,616 bytes**, SHA-256
  `4fd2106f09ef4a35edafbcf3a3a68ea94983e721fd84d852a406e2d26de6552f`.
- **Three artwork tests** cover exact opaque size and fresh PNG byte identity, safe margins,
  quiet field/sparse lime, independent bag/ticket/gap pixels and the copy colour hierarchy.
- Godot **4.8.dev7.official.c971f93e7** imports with **no ERROR/SCRIPT ERROR**. Fresh
  non-editor load has **no errors or warnings** and proves dependencies, unchanged mesh
  resources, one face override, bounds, identity transforms and absent collision.
- Two byte-stable save/reload roundtrips, owned check-only compilation, **gdstyle fmt
  --check**, and **gdstyle --max-line-length 100 --max-warnings 0** pass.

[final.log](d07_retail_graphics_01-evidence/final.log) retains concise actual exit codes and
all final warning/error lines. [manifest.json](d07_retail_graphics_01-evidence/manifest.json)
hashes every produced payload except itself and records the unchanged source/GLB dependencies.
Raw logs, scratch export and intermediate receipts live in `C:/tmp/ft/assets/d07_retail_graphics_01/`.

## Exact reproduction

From the repository root in Bash, with the mise pins available:

```sh
bash tools/asset_production/d07_retail_graphics_01/verify.sh
# Non-mutating retained payload/dependency/hash verification:
python tools/asset_production/d07_retail_graphics_01/record.py
```

`verify.sh` contains the exact commands: regenerate PNG, run artwork tests, reopen/audit
source and byte-compare a scratch reexport, render all four views, bounded pinned import,
headless editor normalization with two stability roundtrips, final import for normalized
UID registration, fresh dependency load, compilation and pinned format/lint. Every Blender
call uses the prescribed binary, audio environment, factory startup, four threads and
python exit code; each has a ≤900 s timeout. Imports use 300 s; other engine checks 180 s.
Receipts regenerate last. No full-project `production_checks.py` suite is run (decision 52).

## Corrections, limitations and remaining acceptance

An initial binary assertion assumed a four-vertex rectangular face. Inspection of the
actual accepted carrier showed a rounded **28-corner face**; the audit now checks all 28
UVs and its 26 triangles, without modifying geometry. First fresh load reported an unregistered
new material UID after normalization; the final reimport registers it and the fresh process
is warning-free. This ordering is retained in `verify.sh`. Initial Pillow deprecation warnings
were corrected by using its current pixel iterator; final artwork tests are clean. The first
receipt check caught 520–617 KB close renders; disabling output dithering (matching sibling
render settings) removed unnecessary background noise and brought final PNGs under 400 KB.

Headless editor normalization exits 0 and proves byte stability but emits existing
pinned-engine/plugin shutdown RID/ObjectDB leaks and scan-aborted diagnostics. Exact final
lines are retained, not suppressed or described as a clean editor shutdown. Import retains
the known Godot-4.8 MCP compatibility warning but no errors. Blender preview has future-node-API
deprecation notices; validation/rendering exit 0. Required CLI-only operation used direct-file
authoring then bounded headless saves. No live owner Blender/Godot MCP session was used or
claimed synchronized, and no project/addon/global configuration was changed.

Remaining gates:

1. Independent art/technical review of this exact candidate; no producer self-acceptance.
2. Final copy selection and saved entrance/bay placement; avoid duplicate fascia geometry,
   verify flat backing/trim fit and keep Broadlot forecourt routes/open space intact.
3. Actual renderer lighting/filtering, populated-world camera/entrance recognition and
   occlusion review. The small upright copy is explicitly not essential overhead wayfinding.
4. Packaged dependencies, future shared-hardware reexport identity retention, repeated-instance
   cost and sustained target-device performance. No new gameplay/network proof is claimed.
5. Existing pinned headless-editor shutdown diagnostics remain a tooling limitation.

The earlier same-lane sign-island handoffs contain no stale pending item for this fascia;
their final-artwork/assembled-camera **review gates** are not unproduced-asset tasks and are
not resolved by this different face. Both sibling docs/manifests and all hardware bytes stay
unchanged. No queue, shared progress, family brief, catalogue, world scene, TODO or project
settings changed. Unproduced family deliveries are tracked by the registry, not this handoff.
