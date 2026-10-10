# d07_retail_graphics.02 — Sign-island face

10 October 2026. **Artwork, material and inherited prefab delivered; independent review and
world/gameplay acceptance pending.** Commissioned implementation worker on `lane/a-d07`
owns original artwork and bounded integration; supervisor/reviewer owns acceptance, and the
world integrator owns placement. The resumed commission supersedes the concept-only brief.

Inputs: [family brief](../d07_retail_graphics.md),
[Broadlot concept](../../concepts/districts-v1/broadlot.md),
[approved district identity](../../concepts/world-v1/stage-03-district-identities/README.md#broadlot--big-roofs-bigger-empty-spaces),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and delivered same-lane
[base](d07_sign_island_01.md), [support](d07_sign_island_02.md) and
[retail fascia artwork](d07_retail_graphics_01.md).

## Design and inherited dimensions

One complete sign-face artwork: **EVERYTHING YOU / NEARLY / NEEDED**. The phrase remains
candidate copy from the brief, not a selected real brand. The same original rounded capital
paths, nearly-closed coral shopping bag, missing upper-right corner and single small lime
ticket connect this freestanding directory identity to the retail fascia. The new three-line
layout fits the existing 48:23 face; it is not a stretched copy of the fascia texture.

Quiet petrol covers over **78%** of the texture and lime under **0.3%**. Coral carries the
main phrase, ivory the introductory line and underline. No prices, promotional lists, arrows,
parking rules, illuminated screen, giant roof advertising or vehicle population is implied.
This is a limited entrance/identity accent; essential overhead navigation cannot rely on copy.

The standing reuse rule applies: **no duplicate `.blend`, GLB or carrier geometry is created**.
The saved prefab inherits the delivered `d07_sign_island_02.tscn` including its collision,
then changes only its front-face material. Use this variant **instead of**, not on top of,
the blank support. The base remains a separate asset; no whole-island/world assembly is added.

| Interface | Inherited value |
| --- | --- |
| Whole support, Godot X/Y/Z | **4.400 × 2.600 × 0.800 m** |
| Godot AABB | **(-2.2, 0, -0.4) → (2.2, 2.6, 0.4)** |
| Root / mesh pivot | Ground/mounting-foot centre **(0,0,0)** |
| Front face | **3.84 × 1.84 m**, centre Y=1.42, plane Z=-0.29 |
| Artwork safe region | Centred **3.60 × 1.60 m**, 60-pixel / 0.12 m quiet perimeter |
| Topology of art slot | **One source quad / two GLB triangles / four vertices** |
| UV0 | Image top-left (0,0), bottom-right (1,1); one complete opaque face |
| Tolerance | Whole bounds ±0.001 m; source/export mapping 0.00001 m |

All dimensions are the sibling's **provisional authored choices**, not raster measurements
or a district parcel allocation. Metre units, applied rotations/scales, Blender +Z up / +Y
front map once to Godot +Y up / -Z front. From the front, local +X is screen-left: U=0 at
X=+1.92, U=1 at X=-1.92. Exported V=0 at Y=2.34 and V=1 at Y=0.50. The ordinary PNG therefore
reads upright and unmirrored; no material UV transform or corrective prefab transform is used.

For the documented base pairing, put this variant root at **(0,0.28,0)** relative to the
base root, identity rotation/scale. Combined top is **Y=2.88 m**. The support's foot corner
radius **2.236068 m** fits the base's **2.58 m** petrol deck radius with **0.343932 m** margin.
This is the inherited mounting contract, not a saved city arrangement or new socket API.
Preserve Broadlot's broad forecourt separation, open parking and routes at placement review.

## Source, runtime outputs and provenance

- Artwork recipe: `tools/asset_production/d07_retail_graphics_02/author.py`.
  Python **3.14.2**, Pillow **12.3.0**; original drawn paths at 3× resolution followed by
  one Lanczos reduction. It imports the committed earlier fascia's `LETTERS` and `PALETTE`
  definitions read-only, so the family letterforms have one owner rather than a private fork.
- Runtime texture: `art/textures/environment/d07_retail_graphics_02/sign_island_face_albedo.png`
  plus pinned `.import`: **1920 × 920 RGB**, opaque sRGB albedo, 48:23, not an atlas/tile.
  Lossless compression, mipmaps enabled, auto-3D compression disabled; no other maps.
- Material: `art/materials/environment/d07_retail_graphics_02/sign_island_face.tres`.
  White albedo multiplier, roughness **0.56**, metallic **0**, back culling, no transparency
  or emission, linear mipmap filtering and repeat disabled.
- Prefab: `scenes/prefabs/environment/d07_retail_graphics_02.tscn`.
- Reused source: `art/source/models/environment/d07_sign_island_02/d07_sign_island_02.blend`.
  Collection **export_d07_sign_island_02**, root **D07SignIsland02**, mesh **D07SignIsland02_Mesh**.
- Reused export: `art/models/environment/d07_sign_island_02/d07_sign_island_02.glb` plus
  unchanged `.import`; reused wrapper `scenes/prefabs/environment/d07_sign_island_02.tscn`.
- Owned `validate.py` calls the support owner's existing validator/exporter with only output
  paths redirected to owned evidence/scratch. It reopens the source, rechecks actual topology,
  normals, bounds and UVs, then byte-compares a fresh export using the shared
  `tools/assets/blender/export_settings.json`. No redundant private exporter is introduced.
- Owned `preview.py` opens that source, overrides slot 0 in memory and renders it without
  saving the source/export. `check_prefab.gd`, `test_artwork.py`, `verify.sh` and `record.py`
  own the bounded engine, artwork and receipt checks.

No downloads, external fonts, purchased assets, image-to-mesh, real brands, prototype
references or generated runtime meshes. The source, GLB, support prefab, import sidecar,
family letter recipe and existing audit/export contracts are hashed unchanged dependencies.

| Artwork role | sRGB |
| --- | --- |
| Quiet petrol | `#102C3C` |
| Shopping bag / main phrase | `#FF725D` coral |
| One small ticket | `#B8DC6F` lime |
| Introductory phrase / underline | `#F6F1DC` warm ivory |

Hardware slots **island_body_slate**, **island_deck_petrol** and **island_wayfinding_lime**
keep their original imported materials. Texture colours do not redefine their linear palette.

## Saved prefab and deliberate inherited collision

The prefab inherits the unchanged support, whose **Visuals/Model** remains an identity-transform
linked GLB instance. The one actual Godot imported face override path is:

`Visuals/Model/D07SignIsland02/D07SignIsland02_Mesh:surface_material_override/0`

The intermediate imported root **D07SignIsland02** is required. This full, engine-verified
path refines the shorthand path in the earlier support handoff; no hardware node is renamed.
Only **sign_island_artwork_face** changes. No global material override, mesh localization,
embedded vertex data, copied collider, new child hierarchy or runtime composition is used.

This uses the authorized static artwork **editable-child face-slot exception** in
[assets.md](../../assets.md#prefabs-and-authored-placement). After initial normalization,
**two additional load/pack/save roundtrips preserve complete prefab bytes**, including node
identities, parent-ID paths, inherited support and dependency UIDs. Fresh non-editor loading
checks that ancestry, every inherited node/transform, the actual shared mesh/collision resources,
all four material slots and all four face UV vertices. Future hardware hierarchy changes must
retest the saved override rather than assume it survives.

Prefab UID **uid://cln7r64887ab5**, material UID **uid://bq8w3kf5mj2hc**, texture UID
**uid://byhyw7sns787p**; inherited support UID **uid://c6ixrjw2dg7x1**, GLB UID
**uid://yafqxb7cebgu**. Scene/material UIDs are inline, texture UID is in `.import`, and the
checker retains its generated `.gd.uid` sidecar.

The flush art adds **no new collision**, but the freestanding support keeps its original
**one StaticBody3D / two-box compound**, layer **1**, mask **0**:

| Inherited shape | Size X/Y/Z (m) | Centre (m) |
| --- | --- | --- |
| `Collision/Body/Foot` | 4.4 / 0.24 / 0.8 | (0,0.12,0) |
| `Collision/Body/Casing` | 4.2 / 2.36 / 0.6 | (0,1.42,0) |

The boxes meet at Y=0.24; the lower wider foot does not create a full-height blocker.
The engine check compares the actual shape resource identities to an independent untouched
support instance as well as these literal dimensions, positions, enabled state and masks.
The art does not change the earlier bounded collision behavior; no new motion/network test
is claimed. Base collision remains with the base owner. No rigs, animations, destruction,
interaction, light nodes, LODs, navigation or authoritative gameplay rules are introduced.

## Evidence and measured validation

[Hero](d07_retail_graphics_02-evidence/hero.png) ·
[Side](d07_retail_graphics_02-evidence/side.png) ·
[Bag/face detail](d07_retail_graphics_02-evidence/detail.png) ·
[47 m / 42° overhead](d07_retail_graphics_02-evidence/overhead_47m_42deg.png).

All four final images were self-inspected. Isolated Blender Cycles CPU, **24 samples**,
denoised, AgX, **1280×720 RGB**, PNG compression **95**, dithering disabled; each below
400 KB, no quantization or painted correction. Hero and side show the whole support and
unmirrored copy; detail intentionally crops into the bag, smooth letter strokes and face seam.
The upright, unscaled support is not tilted to manufacture overhead readability.

Overhead is genuinely vertical-down perspective with fixed north-up yaw, Blender camera
**(0,10,47)**, **42° vertical FOV**, root at its mounting datum **(0,0,0)**. This off-axis view
shows the support at roughly **88×25 pixels**. The cap/lime segment and coral face form small
accents, but **the phrase and bag do not reliably read at gameplay scale**. Exact centred
overhead would hide the front entirely. Keep text as close-range dressing, not essential
wayfinding. The circular base/architecture must supply broader cues at world review; no
larger billboard, roof text or altered geometry is added to disguise this limitation.
These renders show the support variant alone, not an assembled island or Godot lighting proof.

[validation.json](d07_retail_graphics_02-evidence/validation.json) records:

- Reused support: **328 source vertices**, **332 source faces**, **380 GLB vertices**,
  **640 triangles**, **one mesh / four surfaces**.
- **Zero degenerate faces/triangles**, **zero nonmanifold edges**, finite coordinates,
  applied transforms, metre units; maximum normal length errors **1.51e-7 source /
  1.38e-7 exported**. Positive component-volume sum **6.478212 m³**, not a boolean-union
  volume because the closed carrier embeds slightly in the casing.
- Literal source/binary/imported bounds, ground datum and actual source/GLB/Godot UV corners
  pass. No topology claim is inferred from only a bounding box.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**; reopened-source fresh
  reexport is **byte-identical**, **19,936 bytes**, SHA-256
  `919350aa89fdb7056f324bc8938f90909c81315df2918c2a3a81f558da69d231`.
- **Three artwork tests** pass: opaque 48:23 format/fresh PNG byte identity, safe perimeter
  and quiet-field/sparse-lime limits, independent bag/ticket/gap/copy-colour samples.
- Godot **4.8.dev7.official.c971f93e7** import passes with **no ERROR/SCRIPT ERROR**.
  Fresh non-editor load is **error/warning-free** and checks actual mipmaps and inherited
  collision, ancestry, materials, UVs and identity transforms.
- Two byte-stable save/reload roundtrips, check-only GDScript compilation,
  **gdstyle fmt --check**, and **gdstyle --max-line-length 100 --max-warnings 0** pass.

[final.log](d07_retail_graphics_02-evidence/final.log) retains concise actual command exits and
all final warning/error lines. [manifest.json](d07_retail_graphics_02-evidence/manifest.json)
hashes every produced payload except itself and all unchanged dependencies. Scratch renders,
exports, raw logs and initial failed trials stay at `C:/tmp/ft/assets/d07_retail_graphics_02/`.

## Exact reproduction

From the repository root in Bash with mise pins available:

```sh
bash tools/asset_production/d07_retail_graphics_02/verify.sh
# Non-mutating final payload/dependency/hash readback:
python tools/asset_production/d07_retail_graphics_02/record.py
```

`verify.sh` is the exact command sequence: author PNG, run artwork tests, call the existing
source/export validator with owned output paths, render four views, pinned headless import,
headless editor normalization/two further stability roundtrips, final import, fresh dependency
load, script compilation and pinned format/lint. Every Blender process uses the prescribed
binary, audio environment, factory startup, four threads and Python exit code, with a
≤900 s timeout. Imports are bounded to 300 s and other Godot calls to 180 s. Final normalized
`.import`/`.uid` sidecars are retained. Receipts and manifest regenerate last.
No full-project `production_checks.py` suite runs (decision 52).

## Corrections, tooling limitations and remaining acceptance

The first scene trial followed the support handoff's shortened mesh path and therefore lost
the override while saving; logs also exposed a missing-node script error despite engine exit 0.
Inspection of the actual GLB/imported hierarchy identified the intermediate **D07SignIsland02**
root. The final scene uses the full path above, and both stable roundtrips and fresh load pass.
Initial error output is scratch-only, not acceptance evidence. The final receipt writer
explicitly rejects asset/script/missing-node errors even on exit 0; only the specifically
identified pinned-editor shutdown RID-allocation diagnostics are tolerated and retained.
An initial style warning was fixed by extracting the normalization helper without behavior changes.

Headless editor normalization exits 0 and proves byte stability, but retains the existing
pinned-engine/plugin shutdown RID/ObjectDB leaks and scan-aborted warning. Exact final lines
are retained, not hidden or called a clean shutdown. Import retains the known Godot 4.8 MCP
compatibility warning, but no errors. Blender preview has future-node-API deprecation notices;
source validation and renders exit 0. CLI-only instructions required direct-file authoring
followed by isolated headless saves. No live owner Blender/Godot session was accessed or
claimed synchronized; no addon, engine pin or global project settings changed.

Remaining gates:

1. Independent art/technical review of this exact candidate; no producer self-acceptance.
2. Final copy selection and saved base/support/forecourt placement, avoiding duplicate blank
   hardware and preserving clear actor/car routes, actual production queries and network checks.
3. Actual renderer filtering/lighting, populated-world camera recognition and assembled-island
   occlusion. Upright copy is explicitly not essential overhead wayfinding.
4. Future shared-hardware reexport identity retention, packaged dependencies, repeated-instance
   cost and sustained target-device performance; isolated/headless checks do not establish them.
5. Existing pinned headless-editor shutdown diagnostics remain a tooling limitation.

Earlier same-lane handoffs contain no stale unproduced-item entry for this face. The support's
remaining **final-artwork readability / assembled-camera review** is still a real world/engine
gate, not a pending asset-production task, and this Blender-only delivery does not close it.
Sibling docs/manifests and historical receipts therefore remain unchanged. This handoff records
the full imported mesh path without modifying sibling files outside the status-update exception.
No queue, progress, family brief, catalogue, world scene, TODO or project setting was edited.
Unproduced family records remain tracked by the registry rather than this handoff.
