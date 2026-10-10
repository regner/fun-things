# d09_freight_graphics.02 — Container ID panel

10 October 2026. **Artwork/material set and inherited container prefabs delivered;
independent review, placement and gameplay/device acceptance pending.** Commissioned by
Regner under the [production commission](commission.md) and current asset-common standing
rules, superseding the old concept-only restriction. Producer: assigned isolated worker on
`lane/a-freight`. Accepting owners: independent art/technical reviewers, then the world,
gameplay and device owners. This is not a registry-ready or world-placement verdict.

References: [freight graphics family](../d09_freight_graphics.md),
[earlier warehouse fascia](d09_freight_graphics_01.md),
[long container](d09_storage_01.md), [short container](d09_storage_02.md),
[East Docks identity](../../concepts/world-v1/stage-03-district-identities/README.md#east-docks--the-city-ends-at-work),
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).
The earlier freight handoff contains no stale pending container-ID item, so neither its
handoff nor manifest needs editing. No sibling, shared brief, queue, progress or world
scene was changed. Historical storage receipts remain unchanged.

## Design, provenance and family seam

Two fictional visual IDs, **UE 240** and **UE 481**, beneath the small **FREIGHT** header.
A broad amber parcel-clock supplies the same logistics joke as Urgent Eventually Freight;
three compact steel cargo bars complete the header cluster. Large ivory ID copy, generous
quiet gutters and a restrained petrol-steel field keep these small working accents separate.
No barcode, regulatory certification, real brand, saved entity ID, navigation instruction,
inventory/cargo state or essential gameplay information is encoded by either number.
Copy remains provisional; repeated instances may share it.

| Family role | sRGB | Use |
| --- | --- | --- |
| Quiet field | `#143344` | Cool petrol-steel; over 65% of each face |
| Emblem / header | `#FFC05A` | Warm amber accent |
| Primary ID | `#F6F1DC` | Warm ivory |
| Three cargo bars | `#85929D` | Cool steel |

Original reproducible Python/Pillow vector paths, not raster/pixel lettering: no external
fonts, downloads, image generation, purchased textures or generated geometry. `author.py`
imports the earlier freight author's original `GLYPHS` and `PALETTE` read-only, extending
only the digits needed here. The parcel-clock retains that sibling's outline/clock-hand
language at the container face's aspect ratio. Do not stretch the 5:1 warehouse fascia onto
these faces. Keep repeated containers in sparse loading-edge groups, not bright sign walls;
the district's 5.03 ha is context, not a new layout or asset allocation.

## Source, outputs and dimensions

The standing **carrier reuse rule** applies. Storage already supplies both identification
backings and UV-mapped faces: no redundant per-ID `.blend`, GLB, panel mesh or export script
is produced. The new prefabs **inherit the existing storage wrappers**, preserving their
linked Blender models and original collision rather than duplicating either owner.

| Variant / visual copy | Existing source / export / wrapper owner | New prefab |
| --- | --- | --- |
| Long / UE 240 | `d09_storage_01` | `scenes/prefabs/environment/d09_freight_graphics_02.tscn` |
| Short / UE 481 | `d09_storage_02` | `scenes/prefabs/environment/d09_freight_graphics_02_short.tscn` |

For each existing storage owner `<carrier>`:

- Blender source: `art/source/models/environment/<carrier>/<carrier>.blend`.
- Collection: `export_<carrier>`; root/mesh `D09Storage01` / `D09Storage01_Mesh`, or
  `D09Storage02` / `D09Storage02_Mesh`.
- Explicit export: `art/models/environment/<carrier>/<carrier>.glb` plus existing `.import`.
- Inherited prefab: `scenes/prefabs/environment/<carrier>.tscn`.
- Existing owner validator/exporter: `tools/asset_production/<carrier>/validate.py` and
  `export.py`. The new validator delegates read-only, redirecting receipts and fresh exports
  to this asset's scratch directory. No shared validation receipt is overwritten.

New texture/material outputs, for `<variant>` = `long` or `short`:

- `art/textures/environment/d09_freight_graphics_02/container_id_<variant>_albedo.png`
  plus engine-generated `.import`. **1400 x 460 RGB**, opaque sRGB albedo, 1000 px/metre on
  the existing faces. Python **3.14.2**, Pillow **12.3.0**, 3x supersampling and one Lanczos
  downsample. Both faces on a given carrier show the same visual ID.
- `art/materials/environment/d09_freight_graphics_02/container_id_<variant>.tres`.
  White multiplier, metallic **0**, roughness **0.62**, opaque/back-culled, no emission.
  Linear mipmapped filtering, clamp/no repeat, lossless texture import, mipmaps enabled,
  automatic 3D compression conversion disabled. No normal/ORM maps or embedded GLB images.
- Owned author/validator/preview/artwork tests, engine check and receipt tooling:
  `tools/asset_production/d09_freight_graphics_02/`.

| Interface | Inherited Godot-local metres |
| --- | --- |
| Long size X / Y / Z | **2.500 / 2.600 / 12.000** |
| Long AABB | **(-1.250, 0, -6.000)** to **(1.250, 2.600, 6.000)** |
| Short size X / Y / Z | **2.500 / 2.600 / 6.000** |
| Short AABB | **(-1.250, 0, -3.000)** to **(1.250, 2.600, 3.000)** |
| Root / mesh datum | Ground-centred footprint `(0,0,0)` |
| Face dimensions, either length | **1.400 x 0.460**, two outward quads |
| Long face centres | **(±1.230, 1.960, -4.650)** |
| Short face centres | **(±1.230, 1.960, -1.650)** |
| Face vertical interval | **Y=1.730 to 2.190** |
| Authored safe margins | Outer **30 texture pixels / 0.030 m** remain field |
| Guaranteed inner safe rectangle | **1.340 x 0.400** |
| UV0 | Unit square, upright and left-to-right from outside either side |
| Geometric normals | **±X**, outward; original weighted corner normals retained |
| Front / axes | Closed doors face -Z; Blender +Y/+Z maps once to Godot -Z/+Y |
| Measurement tolerance | Source/GLB envelope ±0.001; face/UV audit ±0.00001 |

These are the existing carriers' **provisional authored dimensions**, not newly approved
world clearances or dimensions measured from a concept image. All root/model transforms
remain identity, with no corrective scale, rotation, raised label or duplicate coplanar face.
No rig, animation, sockets, interior, moving door, destruction or new LOD is introduced.
Existing import-generated LOD/shadow meshes remain unchanged; no performance budget is inferred.

## Saved face override, collision and identities

The sole material change on each inherited prefab is `surface_material_override/3` at:

- `Visuals/Model/D09Storage01/D09Storage01_Mesh`, or
- `Visuals/Model/D09Storage02/D09Storage02_Mesh`.

The source slot is `storage_id_face`, exactly **four exported triangles / two outward
quads**. The body, frame, hardware, backing and edges stay in their original slots.
This uses the authorized static-artwork
[editable-child face-slot exception](../../assets.md#prefabs-and-authored-placement):
no copied mesh, no whole-object override, linked GLBs unchanged, two byte-stable
save/reload cycles **per prefab/material**, plus a fresh-process initial-byte stability
check. `Visuals/Model` remains an identity imported instance through the inherited wrapper.
The check compares the actual mesh resource, every override and collision resource against
an independent pristine storage-prefab instance. Face UVs and geometric winding are read
from actual GLB binary accessors, not only summary metadata.

Freestanding containers retain **one inherited StaticBody3D and BoxShape3D each** at
`Collision/Body/Shell`: layer **1**, mask **0**, centre **(0,1.3,0)**, size **(2.5,2.6,12)**
or **(2.5,2.6,6)**. This is the original shape resource, not a copied collider. Flush face
art adds no collider. The container collision envelope, motion/query rules and authority
are unchanged; this delivery does not re-claim the storage owners' historical movement,
ray or car-envelope tests as newly run physics evidence.

| Resource | Long UID | Short UID |
| --- | --- | --- |
| New prefab | `uid://djq3g6bhpao2t` | `uid://cjc4pdgd0ef24` |
| New material | `uid://xm4maj7v4uht` | `uid://ct5m3lmub8dtw` |
| New texture | `uid://bngji74f54nea` | `uid://578e3osufmpa` |
| Inherited storage prefab | `uid://bqm0xefctop4r` | `uid://dxo4oar28nrqj` |

Godot stores scene/material UIDs inline, texture UIDs in `.import`, and the check script's
UID in its `.uid` sidecar. It produces no separate `.tscn.uid` or `.tres.uid` here. Complete
saved bytes retain all imported-child identities through the measured roundtrips. Future
carrier hierarchy/slot migrations need this check rerun; no arbitrary reexport stability
is claimed. Dependency hashes in the manifest cover both sources, GLBs, import sidecars,
base prefabs, owner validators/exporters, shared export contract and freight glyph source.

The production brief forbids live MCP/editor sessions and the windowed editor is unavailable.
Text resources were therefore loaded, packed and saved via isolated pinned headless Godot
resource APIs, then reimported and checked in fresh processes. No owner's open scene was
used, touched or claimed synchronized. There is no runtime hierarchy-construction script.

## Evidence and validation

[Hero](d09_freight_graphics_02-evidence/hero.png) ·
[short-container opposite side](d09_freight_graphics_02-evidence/side.png) ·
[ID detail](d09_freight_graphics_02-evidence/detail.png) ·
[47 m / 42-degree overhead](d09_freight_graphics_02-evidence/overhead_47m_42deg.png).

All four are isolated **Blender Cycles CPU, 32 samples, AgX, 1280 x 720**, PNG compression
100, evidence-only seven-bit RGB reduction; each under 400 KiB. No reduction is applied to
runtime artwork. `preview.py` opens existing sources read-only and never saves them. Hero
and detail show the long carrier's +X face; side shows the short carrier's -X face, exposing
both outside-reading directions and both IDs. Overhead is perspective, vertically down,
north-up, camera **(0,0,47)** with **42-degree vertical FOV**, no geometry/placement boost.

Producer inspected both runtime textures, all four final compressed renders and the earlier
fascia hero. Emblem, warm/cool grouping, upright unmirrored ID and margins read cleanly in
close/side views. At the centred gameplay camera the side artwork is **not visible/readable**:
the quiet blue roof and ~50 x 250 pixel long-container silhouette dominate. This is correct
for flush side identity, not a reason to invent a roof sign or essential overhead cue.
Actual world-camera offsets, nearby objects and repetition still require placement review.
Evidence-background banding is compression, not runtime surface noise.

Final [validation.json](d09_freight_graphics_02-evidence/validation.json) records:

| Measured unchanged carrier | Long | Short |
| --- | ---: | ---: |
| Source vertices | **10,168** | **6,856** |
| Export vertices, including splits | **11,074** | **7,762** |
| Triangles | **20,100** | **13,476** |
| Meshes / surfaces | **1 / 4** | **1 / 4** |
| Degenerate source faces / triangles | **0 / 0** | **0 / 0** |
| Degenerate exported triangles | **0** | **0** |
| Non-manifold source edges | **0** | **0** |
| Maximum source normal-length error | **1.6391275980964792e-7** | **1.5568592659498393e-7** |
| Maximum GLB normal-length error | **1.1552321454999515e-7** | **1.2743446720087093e-7** |
| Fresh byte-identical GLB length | **479,048 bytes** | **333,324 bytes** |

**No new geometry.** Metre transforms, ground pivots, literal bounds, unit normals, both
outward face windings and UV orientations pass. Blender **5.2.2 LTS**, build
**d13f752e3b9c**, exporter **5.2.40** fresh reexports are byte-identical to the unchanged GLBs:

- Long SHA-256: `f3140a621c96f5ab2ecc17ec91dafa53b589d5e9ad5a9a151eba242c5d091876`.
- Short SHA-256: `590469bcc6db39bda4cf46c131edca349d0f2d357aebe1e26a9c568b242e5be0`.

Four artwork tests pass: exact RGB format/dimensions and safe quiet margins; independent
emblem/gutter/cargo-bar pixel expectations; unchanged family clusters with distinct ID copy;
both fresh PNG byte streams equal committed outputs. Pinned **Godot
4.8.dev7.official.c971f93e7** final import, fresh prefab/dependency/collision-retention check
and fresh-process normalization exit 0 with no ERROR/SCRIPT ERROR lines. Two stable
save/reload cycles per prefab/material retain UIDs/identities. **gdstyle 0.3.0** format
check and 100-column / zero-warning lint pass; the check invocation compiles and runs the
only new GDScript.

[manifest.json](d09_freight_graphics_02-evidence/manifest.json) hashes every produced payload
except itself and uncommitted Python cache, and verifies the unchanged shared dependencies.
[final.log](d09_freight_graphics_02-evidence/final.log) is the concise final receipt. Scratch
exports and raw logs stay at `C:/tmp/ft/assets/d09_freight_graphics_02/`, never in Git.

## Exact reproduction

Run from this worktree root in Git Bash; all Blender invocations are isolated and every
engine call is headless. `record.py` defaults to read-only verification; `--write` explicitly
rebuilds the measured receipts/manifest after the final handoff edit.

```sh
NID=d09_freight_graphics_02
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="$(mise which gdstyle)"
OUT="C:/tmp/ft/assets/$NID"
mkdir -p "$OUT"
export PYTHONIOENCODING=utf-8
python tools/asset_production/$NID/author.py
python -m unittest discover -s tools/asset_production/$NID -p 'test_*.py' -v > "$OUT/tests.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/validate.py > "$OUT/source.log" 2>&1
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/preview.py > "$OUT/render.log" 2>&1
python tools/asset_production/$NID/record.py --compress-renders
timeout 300 "$G" --headless --path . --import > "$OUT/import-initial.log" 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd -- --normalize --verify-stable > "$OUT/normalize.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$OUT/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd > "$OUT/prefab.log" 2>&1
"$S" fmt --check tools/asset_production/$NID/check_prefab.gd > "$OUT/format.log" 2>&1
"$S" --max-line-length 100 --max-warnings 0 tools/asset_production/$NID/check_prefab.gd > "$OUT/style.log" 2>&1
python tools/asset_production/$NID/record.py --write
python tools/asset_production/$NID/record.py
```

## Diagnostics and remaining acceptance

Initial owned validator assumptions incorrectly expected unrounded corner normals and the
opposite Godot U sign. Inspecting the actual accessors established outward **geometric**
normals, slightly rounded unit shading normals, and correct outside left-to-right UVs;
the validator now distinguishes these, without modifying or weakening the carrier contract.
Initial lint exceeded the local-variable limit; a per-variant helper resolved it. Initial
temporary-instance teardown emitted the dummy renderer's null-material diagnostic; retaining
material references until all temporary instances are destroyed resolved it. Final fresh
processes have no such errors; no errors are suppressed or vendor files edited. Blender
preview retains `use_nodes` forward-looking deprecation notices. Import retains the existing
MCP toolkit 4.8-versus-tested-4.7 warning, not an asset error.

Pending: independent art/technical acceptance of this exact candidate and final fictional
copy selection; saved district placement, sparse container grouping and actor/target occlusion;
actual renderer filtering/mip/LOD and gameplay-camera appearance in context; packaged devices,
Deck and sustained repetition performance. Existing storage gameplay/vehicle/network gates
remain their owners' responsibility. No gameplay authority, collision, road tool, navigation,
world identity or multiplayer behavior changed. No new movement/network acceptance is claimed.
No `tools/production_checks.py` run, under owner decision 52. No world placement is authorized
by this source/material candidate alone.

## Saved identity normalization

Identity normalized; imported-child override ids migrated by Godot 4.8 editor save; override target verified.
