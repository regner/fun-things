# city_parking_furniture.04 — Simple bus-stop sign

10 October 2026. **Artwork, inherited prefab and bounded source/engine checks delivered;
independent review and world/gameplay acceptance pending.** Produced by the commissioned
implementation specialist on `lane/a-park4`. The [commission](commission.md) and current
common production brief supersede the historical concept-only restriction in the
[family brief](../city_parking_furniture.md). No register, shared brief, progress, world
scene or gameplay rule changed. Acceptance remains with the supervisor and reviewer.

## Design and reuse

A broad, original ivory bus-front pictogram on a quiet petrol square, with a small amber
roof/destination strip. Rounded corners, split windscreen, two lamps and two wheels carry
the meaning without type, route numbers, real brands, timetables or decorative clutter.
The existing small single-post carrier supplies all physical geometry. This is optional
street dressing: **no bus operation, new vehicle, stop interaction or traffic rule**.
District use remains unconfirmed; it is not added to Signal Row's starting set.

The [district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[streets](../../concepts/world-v1/stage-04-streets/README.md) and
[shared concept contract](../../concepts/districts-v1/brief-contract.md) inform the sparse
furniture/quiet-road treatment. The existing [wheel stop](city_parking_furniture_01.md)
and [cycle stand](city_parking_furniture_03.md) establish restrained petrol/amber parking
furniture; this sign retains that palette rather than adding a district-specific brand.

**The family specifically requires reuse of [city_traffic_fixtures.03](city_traffic_fixtures_03.md).**
The current standing reuse rule therefore takes precedence over the register's generic
“Model design” output template: no duplicate `.blend`, GLB, carrier mesh or coplanar panel
is produced. The original hardware already exists on main. New deliverables are the
reproducible artwork, texture/import metadata, material, and an inherited prefab with
exactly one face-only material override. Blender source/export provenance and collision
remain with that unchanged shared hardware. No private copy of its author/export/validator
is added; the owned validator invokes the existing source audit with scratch-only outputs.

Original artwork is explicitly drawn by `author.py` using Python/Pillow, not generated
from a prompt or downloaded. No fonts, image-to-mesh, third-party artwork or attribution
dependency. No rig, animation, destruction state, light node, socket, extra LOD or geometry.

## Dimensions and placement interface

All dimensions are **inherited provisional production values**, not new approved street
setbacks or measurements inferred from concept images:

| Quantity | Metres / contract |
| --- | --- |
| Godot X/Y/Z visual size | **0.700 × 3.250 × 0.280** |
| Visual AABB | **(-0.350,0,-0.140) → (0.350,3.250,0.140)** |
| Ground shoe / shaft | Maximum diameter 0.280 / shaft diameter 0.130 |
| Plate | 0.700 square; bottom 2.550, top 3.250; depth 0.055 |
| Artwork face | 0.680 square; centre `(0,2.900,-0.135)` |
| Safe graphic rectangle | 0.600 square; actual pictogram stays comfortably inside |
| Ground pivot | `(0,0,0)`, centre of the shoe, not the sign panel |
| Envelope / ground tolerance | ±0.001; source/export comparison ±0.00001 |

Root, imported model and mesh retain identity transforms, metres and applied transforms.
Blender +Z/+Y maps once to Godot +Y/-Z. Rotate the prefab about +Y so local -Z faces the
road approach; place the root at the saved sidewalk/ground datum. The root is the shared
road-tool placement anchor; no additional mounting socket or placement system is added.
Do not place both this prefab and its blank carrier at the same position.

Keep the shoe out of driving sweeps, passage mouths, pedestrian bypasses and aim lines.
The overhead panel is not an overhead gameplay marker and must not replace a route cue.
Sparse placement, clear aisles and turning areas remain layout-owner responsibilities.

## Source, runtime files and material interface

- Artwork source: `tools/asset_production/city_parking_furniture_04/author.py`,
  Python **3.14.2**, Pillow **12.3.0**; original shapes supersampled 4× then downsampled once.
- Runtime image: `art/textures/environment/city_parking_furniture_04/bus_stop_albedo.png`
  and `.png.import`; **512×512 opaque RGB**, sRGB albedo, no embedded images.
- Material: `art/materials/environment/city_parking_furniture_04/bus_stop.tres`.
  White multiplier, metallic 0, roughness .52, opaque/backface-culled, no emission,
  clamped UVs, linear mipmapped filtering. Lossless texture import, mipmaps enabled,
  automatic 3D compression conversion disabled. No normal/ORM/emission map.
- Prefab: `scenes/prefabs/environment/city_parking_furniture_04.tscn`, inheriting
  `scenes/prefabs/environment/city_traffic_fixtures_03.tscn`.
- Shared source: `art/source/models/environment/city_traffic_fixtures_03/city_traffic_fixtures_03.blend`;
  collection `export_city_traffic_fixtures_03`; root/mesh
  `CityTrafficFixtures03` / `CityTrafficFixtures03_Mesh`.
- Shared export: `art/models/environment/city_traffic_fixtures_03/city_traffic_fixtures_03.glb`
  and its unchanged `.glb.import`. The existing exporter loads
  `tools/assets/blender/export_settings.json`, filters the declared collection and
  disables skins/animation. Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**.

| Artwork role | sRGB |
| --- | --- |
| Field / window and lamp cutouts | Petrol `#123646` |
| Bus silhouette | Warm ivory `#F6F1DC` |
| Roof/destination strip | Amber `#FFC05A` |

Hardware surfaces 0/1 retain `traffic_dark_metal` and `traffic_fixture_rim`, matching the
shared lights/traffic hardware. Only surface **2**, `road_sign_face`, receives the new
material. The UV0 `UVMap` is the carrier's unchanged 0–1 square: viewed from its front,
image right follows Godot -X, image top follows +Y; glTF V=0 is the top. Rounded face
corners clip only the petrol margin. No mirror correction, UV rewrite or whole-mesh
material override. Original binary UV landmarks and normal orientation are revalidated.

## Prefab, identities and collision

The prefab inherits the existing support rather than rebuilding its composition.
`Visuals/Model` remains the original imported GLB at identity transform. Its one saved
editable-child change is:

`Visuals/Model/CityTrafficFixtures03/CityTrafficFixtures03_Mesh: surface_material_override/2`

This implements the standing instruction to reuse existing hardware through face-only
saved overrides. Imported geometry is not copied or made local, and no runtime appearance
writer is added. The inherited support remains a serialized dependency; parent-ID paths,
mesh identity and all other materials/transforms survive two load/pack/save roundtrips.
This is a narrow saved-override use, not a new general appearance API. Future shared
hardware hierarchy changes must revalidate the saved path and IDs.

Inherited `Collision/PoleBody/Shape` is still **one cylinder**, radius **0.140 m**, height
**2.500 m**, centre `(0,1.250,0)`, static-world layer **1** / mask **0**. Its resource and
transform are identical to the original prefab. No second collider, broad false sign
box or collision below the plate is added. The plate and shaft above 2.5 m remain
visual-only under the standing overhead rule. Actor/vehicle contact and world clearances
still require placement review; inherited collision does not imply new bus gameplay.

Under the isolated-CLI brief, live MCP/windowed editor tools were deliberately not used.
The wrapper/material were authored as text, loaded/packed/resaved by **headless editor**
Godot only, then imported and checked in a separate non-editor headless process. Scene
and material UIDs are inline; the texture UID is in `.import` and the checker has its
engine-generated `.gd.uid`. Godot does not generate `.tscn.uid` sidecars. No owner live
scene was accessed or claimed synchronized.

## Evidence and validation

[Hero](city_parking_furniture_04-evidence/hero.png),
[side/rear](city_parking_furniture_04-evidence/side.png),
[face detail](city_parking_furniture_04-evidence/detail.png),
[47 m / 42° overhead](city_parking_furniture_04-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles CPU renders, **1280×720**, 32 samples, AgX, shared carrier
studio lights/ground. PNG compression 100 with six or seven significant RGB bits keeps the
retained images near/below 400 KB each. The current 720-pixel cap supersedes historical
800-pixel examples. Overhead is vertical-down, 47 m high, 42° vertical FOV, north-up,
centred at the unscaled ground-mounted prop. No enlarged face or camera tilt.

Producer inspected the four renders and texture. The close views show a clean generic
bus pictogram and restrained warm strip, with untouched metal backing and clamps. From
the actual overhead camera the plate collapses to a tiny edge; **the bus symbol is not
readable there**. This is an expected limitation of the mandated shared vertical sign,
not solved by more texture resolution. It is optional dressing, not essential wayfinding.
These images are not Godot captures, populated-city readability or device acceptance.

[validation.json](city_parking_furniture_04-evidence/validation.json) records:

- Reused hardware: **732 source vertices, 578 source faces, 800 exported vertices,
  1,428 triangles; one mesh / three surfaces**. Added geometry: **zero**.
- **Zero degenerate faces/triangles, zero non-manifold edges**, positive sum of closed
  component volumes .08323797794 m³; source normal length error <1.69e-7, export <1.09e-7.
- Source/export AABBs, ground datum, pivots, transforms, actual face-only UV landmarks
  and front normals pass the existing hardware validator without modifying its files.
- Fresh saved-source export is **byte-identical** to the shared **37,340-byte** GLB,
  SHA-256 `bc40bd426b79d6515b37e37738adfbc189ac75114135aee7116be65360f5958f`.
  Source/GLB/import/prefab dependency hashes remain unchanged.
- **Four artwork tests** pass: opaque size/mode, safe margins and quiet field, independent
  bus-feature pixel landmarks, and fresh PNG byte identity.
- Godot **4.8.dev7.official.c971f93e7** checks actual linked geometry, AABB, inherited
  collider resource identity, exactly one surface override, clamped material, actual
  imported mipmaps, recursive dependency resolution and saved inline UIDs. Two editor
  save/reload cycles preserve exact scene bytes; final import/load confirms persistence.
- Actual physics queries: low ray hits the pole; ray at Y=2.9 m clears the panel;
  radius-.35 m / height-1.8 m capsule overlaps the post and clears at X=.8 m.
  These are bounded queries, **not new actor movement, vehicle or transport tests**.
- Final full production checks **PASS**: pinned GDScript format/lint and explicit script
  compilation, **17 Python tool tests**, **149 GUT tests / 6,768 assertions**, isolated
  import and intentional failing diagnostic sentinel. No known-failure exception used.

The [producer manifest](city_parking_furniture_04-evidence/manifest.json) hashes every
produced file except itself, including this document, four renders, tools and import/UID
metadata. Shared dependencies are separately hashed in validation. One concise
[final log](city_parking_furniture_04-evidence/final.log) retains outcomes and diagnostic
classification; scratch renders, earlier attempts, reexports and raw logs stay in
`C:/tmp/ft/assets/city_parking_furniture_04/`.

### Corrected findings and diagnostics

- Initial Blender previews showed a blank face: the shared source has a valid `UVMap`
  but no active render UV layer. The preview now explicitly binds that named UV map in
  its temporary shader; no source/GLB was changed. Final hero/detail show the symbol.
- Initial new-resource saves preceded UID registration. A non-editor normalization
  attempt also removed inline UIDs despite cache-based load success. The checker now
  **requires --editor for normalization**, waits for its filesystem scan, registers
  newly saved identities and checks inline headers as well as cache paths. Final
  serialized resources retain UIDs and saved parent/node identities.
- Headless editor normalization passes its assertions and exits 0 but emits existing
  editor/plugin RID/ObjectDB shutdown leaks. These diagnostics are not called a clean
  editor exit. Final non-editor load is separately required with no errors/warnings;
  final full import reports only the existing MCP 4.8/latest-tested-4.7 warning.
  No live MCP connection or unrelated-process operation was performed.
- Blender preview logs contain the pinned `use_nodes` future-API deprecation notice;
  final source validation and rendering exit 0. No broad diagnostic suppression.

## Exact reproduction

From the repository root in Git Bash. `checks-final` must be fresh/empty before rerunning
the full suite; move an earlier scratch run aside rather than mixing its receipts.

```sh
N=city_parking_furniture_04
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$N"
mkdir -p "$T"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
python "tools/asset_production/$N/author.py"
python -m unittest discover -s "tools/asset_production/$N" -p 'test_*.py' -v
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/validate.py"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/preview.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$N/check.gd" -- --normalize
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks-final"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script "res://tools/asset_production/$N/check.gd"
python "tools/asset_production/$N/record.py"
python "tools/asset_production/$N/record.py" --check
```

`validate.py` calls the existing hardware validator/exporter, redirecting its receipts
and fresh GLB to this asset's external scratch directory. It verifies shared hashes
before/after; it never rebuilds, saves or exports over a shared file. There is deliberately
no per-ID hardware `export.py`. For a separate saved-source export, use the same pinned
Blender flags, open the shared `.blend`, and invoke
`tools/asset_production/city_traffic_fixtures_03/export.py -- "$T/manual-reexport"`.

## Remaining acceptance

Independent technical/art review is required. District selection, sparse world placement,
road-tool placement integration, actual engine gameplay-camera/presentation and aim
occlusion, vehicle swept clearance/contact, real-process networking/prediction, packaged
texture filtering and sustained repeat-placement/Deck performance remain **pending**.
No register READY status, bus system, finalized district use, completed gameplay gate or
world placement is claimed. Future shared carrier reexports must retain the face slot,
UV interface and saved inherited override identity or trigger coordinated revalidation.
