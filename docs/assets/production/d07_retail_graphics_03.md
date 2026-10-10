# d07_retail_graphics.03 — Parking-zone panel

10 October 2026. **Artwork, material and inherited prefab delivered; independent review and
world/gameplay acceptance pending.** Commissioned implementation worker on `lane/a-d07`
owns original artwork and bounded integration. Supervisor/reviewer owns acceptance; world
integration owns placement. The resumed commission supersedes the concept-only brief.

Inputs: [family brief](../d07_retail_graphics.md),
[Broadlot concept](../../concepts/districts-v1/broadlot.md),
[approved district identity](../../concepts/world-v1/stage-03-district-identities/README.md#broadlot--big-roofs-bigger-empty-spaces),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and same-lane
[base](d07_sign_island_01.md), [support](d07_sign_island_02.md),
[fascia](d07_retail_graphics_01.md) and [directory face](d07_retail_graphics_02.md).

## Design and inherited dimensions

One **P / ZONE A** parking identity face. The broad coral P, coral zone letter, warm-ivory
label and single small lime ticket use the earlier Broadlot palette and rounded capital
paths. The parking P and new Z are original drawn paths, not external font glyphs. **A is
provisional copy**, not an assigned parking sector, spawn rule, payment restriction, traffic
priority or vehicle count. No direction arrow implies a route before the forecourt is placed.
This small supporting accent complements the larger retail identity rather than repeating
its promotional phrase. Over **86%** of the image is quiet petrol; lime occupies under **0.1%**.

Standing hardware-reuse rule: **no new `.blend`, GLB or duplicate carrier**. The delivered
[`city_sign_supports_01`](city_sign_supports_01.md) wall panel already supplies a compatible
face. The saved artwork prefab inherits that wrapper and changes only its front-face material.
Use this variant **instead of**, not overlaid on, a blank panel. It is wall-mounted, not a
freestanding parking post. No enlarged carrier, road-marking decal or island assembly is made.

| Interface | Inherited value |
| --- | --- |
| Whole panel, Godot X/Y/Z | **1.40 × 1.00 × 0.10 m** |
| AABB | **(-0.70,-0.50,-0.10) → (0.70,0.50,0) m** |
| Root / mesh pivot | Wall-contact centre **(0,0,0)**, not ground-contact |
| Artwork face | **1.22 × 0.82 m**, plane **Z=-0.088 m** |
| Safe-copy rectangle | Centred **1.14 × 0.74 m**, 40-pixel / 0.04 m perimeter |
| Rounded face | 0.04 m corner radius; one source face / 34 triangles / 36 vertices |
| UV0 | One full **61:41** opaque image; no atlas/repetition |
| Dimensional tolerance | Source/binary bounds 0.000001 m; imported bounds 0.001 m |

These are the hardware owner's **provisional dimensions**, not concept-raster measurements.
Metre units, applied rotations/scales; Blender +Z up / +Y front maps once to Godot +Y up / -Z
front. From the front, local +X is screen-left: exported U=0 at X=+0.61, U=1 at X=-0.61;
V=0 at Y=+0.41, V=1 at Y=-0.41. The image reads upright/unmirrored without corrective transforms.
Rounded corners clip only quiet background. Original frame, gasket, sides, rear and mounts remain
unchanged. Place the pivot on an existing opaque wall; the inherited review-height proposal is
**Y=1.6 m**, putting the panel at Y=1.1–2.1 m. No wall or actual placement is part of this delivery.

## Source, outputs and provenance

- Artwork recipe: `tools/asset_production/d07_retail_graphics_03/author.py`.
  Python **3.14.2**, Pillow **12.3.0**, original paths drawn at 3× then reduced once with
  Lanczos. Read-only import of the earlier fascia's `LETTERS` and `PALETTE` keeps one
  family owner; only the new parking P and Z paths belong here.
- Texture: `art/textures/environment/d07_retail_graphics_03/parking_zone_albedo.png`
  and normalized `.import`, **1220 × 820 RGB**, opaque sRGB albedo. Lossless import,
  mipmaps enabled, auto-3D compression disabled. No normal/ORM/emission maps.
- Material: `art/materials/environment/d07_retail_graphics_03/parking_zone.tres`.
  White multiplier, roughness **0.56**, metallic **0**, back-culled, no transparency/emission,
  linear mipmapped filtering, repeat disabled; no UV scale/offset.
- Prefab: `scenes/prefabs/environment/d07_retail_graphics_03.tscn`.
- Reused source: `art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend`;
  collection **export_city_sign_supports_01**, root **CitySignSupports01**.
- Reused GLB: `art/models/environment/city_sign_supports_01/city_sign_supports_01.glb`;
  inherited wrapper `scenes/prefabs/environment/city_sign_supports_01.tscn`.
- Owned `validate.py` invokes the hardware owner's existing `export.py` source audit and
  `check_glb.py` independent binary audit, redirecting output only to scratch. The existing
  hardware exporter owns its historical explicit settings; no replacement export contract,
  private `export.py`, redundant model or embedded image is introduced.
- Owned `preview.py` opens the unchanged Blender source and overrides only the face in memory;
  it never saves the source/GLB. `check_prefab.gd` reuses the existing same-carrier hierarchy,
  surface and roundtrip helpers, adding this artwork's material and imported-UV expectations.

| Role | sRGB |
| --- | --- |
| Quiet petrol field | `#102C3C` |
| Parking P / zone A | `#FF725D` coral |
| Single small ticket | `#B8DC6F` lime |
| ZONE label / underline | `#F6F1DC` warm ivory |

No downloads, external fonts, purchased content, real brands, image-to-mesh, prototypes,
new generated runtime meshes, or runtime hierarchy construction. Shared source/export/prefab,
import sidecar and reused recipe/audit scripts are retained as hashed unchanged dependencies.

## Saved prefab and collision

The inherited **Visuals/Model** remains the identity-transform linked GLB. Exactly one override:

`Visuals/Model/CitySignSupports01/artwork_carrier:surface_material_override/0`

Only **sign_face** changes. Carrier slot 1 **mount_metal**, frame **support_petrol** and gasket
**recess_gasket** retain their original materials, including their existing double-sided flags.
No mesh localization, global material override, copied render data or new child hierarchy.

This uses the authorized static artwork **editable-child face-slot exception** in
[assets.md](../../assets.md#prefabs-and-authored-placement). After initial normalization,
**two further load/pack/save roundtrips are byte-identical**, preserving complete scene bytes,
node identities, parent-ID paths and UIDs. A fresh non-editor process verifies shared mesh
resource identity, unchanged hierarchy/transforms, all thirteen surfaces, one override and UVs.

Prefab UID **uid://btl6dipk8pe68**, material UID **uid://bndcp20ctmf21**, texture UID
**uid://b4d0crtcpr0tl**; inherited wrapper UID **uid://byqodl735ss1a**, GLB UID
**uid://bdlt6f8x0t868**. Scene/material identities are inline; texture `.import` and check-script
`.gd.uid` are retained. Future hardware hierarchy/reexports must retest this saved override.

**No collision**, consistent with the inherited wall panel and standing flush-face exception.
The opaque backing wall must supply blocking. Do not place this as a freestanding obstacle.
No movement, navigation, authority, network, equipment, interaction or destruction behavior
changes. No rigs, clips, light nodes or new LODs; hardware import defaults remain unchanged.

## Evidence and measured validation

[Hero](d07_retail_graphics_03-evidence/hero.png) ·
[Side](d07_retail_graphics_03-evidence/side.png) ·
[P/face detail](d07_retail_graphics_03-evidence/detail.png) ·
[47 m / 42° overhead](d07_retail_graphics_03-evidence/overhead_47m_42deg.png).

All four final images were self-inspected. Isolated Blender Cycles CPU, **24 samples**,
denoised, AgX, **1280×720 RGB**, PNG compression **95**, no output dithering, quantization or
painted corrections; each below **189 KB**. Hero/side retain the complete rounded panel and
upright artwork. Detail intentionally crops into the P, label and frame to inspect edges.

Overhead is vertical-down north-up perspective at Blender **(0,10,47)**, **42° vertical FOV**,
with the panel mounted at **(0,0,1.6)**. The unchanged upright panel is not enlarged or tilted.
At roughly **28×6 screen pixels**, it is a tiny coral/ivory strip; **P / ZONE A is not reliably
readable at gameplay scale**. Directly centred overhead hides the face. It is close-range
parking dressing, not essential navigation; architecture, entrance bands, circular-island
silhouette and the saved layout must supply broader cues. More texture resolution cannot
solve this geometric limit. These are not Godot lighting or populated-world camera captures.

[validation.json](d07_retail_graphics_03-evidence/validation.json) records:

- Shared hardware **1,380 source vertices**, **1,792 GLB vertices**, **2,720 triangles**,
  **12 meshes / 13 surfaces**. Four original materials; only the face uses the new material.
- **Zero degenerate faces/triangles**, **zero nonmanifold edges**, positive closed component
  volumes, finite positions, unit-length source/export normals, metre units and applied transforms.
  Topology and winding are checked from actual source meshes and decoded binary triangles.
- Source/binary bounds and all **36 face UV samples** pass at 1e-6 tolerance. Imported UV
  maximum error **0.0000305605716393** is below the separately named **0.00005** quantization
  tolerance (under 0.062 texel); imported positions and inherited bounds also pass.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**: fresh reopened-source
  export is **byte-identical**, **75,768 bytes**, SHA-256
  `5f54105825e00bb73c038bed252910abec548ad1beb81603b2713c2c69796e0b`.
- **Three artwork tests** pass: exact opaque format/fresh PNG byte identity; safe perimeter
  and quiet-field/sparse-lime ratios; independent P-stem/counter, A-gap, label and ticket pixels.
- Godot **4.8.dev7.official.c971f93e7** imports with **no ERROR/SCRIPT ERROR**. Fresh
  non-editor load is **error/warning-free**, proving dependencies, real mipmaps, no collision,
  shared hierarchy/meshes, the one intended material override and actual imported UV orientation.
- Two byte-stable save/reload roundtrips, check-only compilation, **gdstyle fmt --check** and
  **gdstyle --max-line-length 100 --max-warnings 0** pass.

[final.log](d07_retail_graphics_03-evidence/final.log) retains concise final command exits and
all final diagnostic lines. [manifest.json](d07_retail_graphics_03-evidence/manifest.json)
hashes every produced payload except itself and records unchanged dependencies. Raw logs,
intermediate receipts and scratch exports remain in `C:/tmp/ft/assets/d07_retail_graphics_03/`.

## Exact reproduction

Run from repository root in Bash with mise pins available:

```sh
bash tools/asset_production/d07_retail_graphics_03/verify.sh
# Non-mutating final payload/dependency/hash verification:
python tools/asset_production/d07_retail_graphics_03/record.py
```

`verify.sh` is the exact command sequence: original PNG authoring, artwork tests, source and
binary audits/fresh export byte comparison, four isolated previews, pinned import, headless
editor normalization plus two further roundtrips, final import, fresh dependency load,
check-only compilation and pinned formatting/lint. Blender calls use the prescribed executable,
audio environment, factory startup, four threads, Python exit code and ≤900 s timeout;
imports ≤300 s and other Godot calls ≤180 s. UTF-8 logs and final normalized sidecars are
retained. Receipts regenerate last. No `production_checks.py` runs (owner decision 52).

## Corrections, limitations and remaining acceptance

Initial pixel tests sampled a thin anti-aliased underline edge as an exact solid colour;
the final exact-colour sample uses the broad ZONE stroke instead. File-buffer handling was
also corrected to eliminate an initial Pillow ResourceWarning. No artwork change was needed.
An initial imported-UV assertion reused the source's 1e-6 tolerance despite the existing
compressed mesh import. Actual maximum error was measured; the named imported-only tolerance
above accounts for quantization without changing hardware/import settings or weakening the
source/binary checks. Initial error logs are scratch-only; receipt validation rejected their
SCRIPT ERROR lines even though Godot returned exit 0 and continued to print a pass marker.

Final headless editor normalization proves scene stability but retains known pinned-engine/
plugin shutdown RID/ObjectDB leak and scan-aborted diagnostics. Their exact final lines are
retained, not called a clean shutdown. Initial error-reporting also triggered a rich-text
`p_image.is_null()` diagnostic; it is absent from final checks. The import has the known MCP
Godot-4.8 compatibility warning but no errors. Blender emits future-node-API deprecation
notices and exits 0. Required CLI-only operation used direct-file authoring followed by isolated
headless saves. No live owner Blender/Godot session was used or claimed synchronized; no engine,
addon, project configuration or shared resource was modified.

Remaining gates:

1. Independent art/technical review of this exact candidate; no producer self-acceptance.
2. Final zone/copy selection and saved placement on an opaque backing wall, avoiding duplicate
   hardware and preserving broad forecourt lines of sight and clear walking/driving routes.
3. Actual renderer filtering/lighting and populated-world readability/occlusion review. This
   small upright panel must not carry essential overhead wayfinding or traffic instructions.
4. Future shared-hardware reexport identity retention, packaged dependencies, repeated-instance
   cost and sustained target-device performance. No new gameplay/network proof is claimed.
5. Existing pinned headless-editor shutdown diagnostics remain a tooling limitation.

All four earlier same-lane handoffs were checked: none lists this parking panel as an unproduced
pending item. Their remaining world/camera/final-artwork **review gates** are not resolved by
this isolated artwork delivery. Sibling docs/manifests and historical receipts stay unchanged.
No queue, shared progress, family brief, catalogue, world scene, TODO or project setting changed.
Unproduced family work is tracked by the registry, not by this handoff.
