# d02_neighbourhood_graphics.02 — Parking-request notice

**Artwork/material/linked-prefab candidate delivered; independent review and world acceptance
pending.** Producer: assigned implementation worker on `lane/a-d02g`. Commission:
[production commission](commission.md), current per-ID assignment and standing reuse rules.
Family: [Neighbourhood notice graphics](../d02_neighbourhood_graphics.md). Earlier sibling:
[watch notice](d02_neighbourhood_graphics_01.md). Its current handoff contains no pending
parking-notice item to resolve, so no sibling document, manifest or historical receipt changed.

## Design, provenance and scope

Provisional original copy: **PLEASE USE / ONE SPACE / WE ARE COUNTING**. A single compact car
sits between two bay edges. The request is polite; the neighbours' counting supplies the petty
residential humour. This is decorative fictional copy, **not a parking rule, traffic sign,
interactive system or navigation cue**. Copy remains subject to final owner selection.

The watch notice supplies the family language: one fine border, generous warm ivory field,
quiet blue secondary copy, muted plum emphasis and smooth rounded-path lettering. No neon,
warning slashes, official seals, real brands, external fonts, downloaded images or textures.
The palette is exactly ivory `#F6F1DC`, blue `#526D86`, plum `#635168`. The original car/bay
composition and copy are authored in this asset's `author.py`. It imports the sibling's
palette and existing project-owned path canvas/letter skeletons, ultimately from
`d06_commercial_graphics_01/author.py` and `d06_commercial_graphics_02/author.py`; it does not
reuse the commercial artwork. Python 3.14.2 / Pillow 12.3.0, smooth 3× supersampling followed
by one filtered reduction. Source is the committed Python recipe, with no external rights
or runtime attribution dependency.

References inspected: accepted Petrol & Coral direction; approved stage-03 Crescents identity;
[The Crescents revision 02](../../concepts/districts-v1/the-crescents.md), exact district map
context and stage-04 street hierarchy. Domestic treatment remains quieter than Signal Row.
No dimension is inferred from concept imagery. No world/sector placement, roads, collision,
movement, gameplay, navigation or network code/data changed.

## Source, outputs and inherited interface

**No duplicate Blender source, GLB, panel or decal mesh.** The already-produced shared hardware
is reused under the standing artwork-reuse rule:

- Source: `art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend`.
- Collection/root: `export_city_sign_supports_01` / `CitySignSupports01`.
- Export: `art/models/environment/city_sign_supports_01/city_sign_supports_01.glb`.
- Base prefab: `scenes/prefabs/environment/city_sign_supports_01.tscn`.
- Contracts: [wall-panel source handoff](city_sign_supports_01.md),
  [accepted integration conventions](batch_01-integration.md).

New outputs:

- Tools: `tools/asset_production/d02_neighbourhood_graphics_02/`.
- Runtime texture: `art/textures/environment/d02_neighbourhood_graphics_02/parking_request_albedo.png`
  plus its engine-normalized `.import`.
- Material: `art/materials/environment/d02_neighbourhood_graphics_02/parking_request.tres`.
- Prefab: `scenes/prefabs/environment/d02_neighbourhood_graphics_02.tscn`.

`family_tools.py` retargets the existing watch-notice tooling **in memory only**: the ID,
artwork filename stem and diagnostic prefix change; validation assertions and the existing
studio/export/inventory implementations remain shared. The per-ID `export.py`, `validate.py`,
`preview.py`, `finalize.py` and `manifest.py` are small entrypoint adapters. Source validation
fingerprints every reused script and hardware dependency before/after, and finalization checks
them again. The Godot checker inherits the sibling's hierarchy/surface assertions while owning
this asset's material paths, roundtrip and receipt. No shared file was edited. Future shared
tool/hardware changes must rerun this dependent asset's checks; this is not a second exporter
or geometry validator. The shared carrier's established exporter settings are unchanged.

| Quantity | Measured inherited convention |
| --- | --- |
| Whole Godot X/Y/Z | **1.40 / 1.00 / 0.10 m** |
| Godot AABB | min **(-0.70, -0.50, -0.10)**; max **(0.70, 0.50, 0)** |
| Pivot | Wall attachment centre **(0,0,0)**, not ground contact |
| Front/up | Blender +Y/+Z → Godot -Z/+Y |
| Artwork face | **1.22 × 0.82 m**, Godot Z = **-0.088 m** |
| Safe copy rectangle | Centred **1.14 × 0.74 m** |
| Texture aspect | **61:41**, exact face match |
| Bounds tolerances | Source/export **0.000001 m**; engine **0.001 m** |
| Suggested mounting centre | **1.60 m** above ground, provisional placement choice |

No geometry, UV or root-transform correction is introduced. UV0 is Blender
U=(0.610-X)/1.220, V=(Z+0.410)/0.820; glTF flips V storage. Front-view screen-right is
local -X. All copy is upright and unmirrored. The outer forty texels are uninterrupted ivory,
protecting the rounded face crop and safe-copy rectangle.

## Material, prefab and collision

**1220 × 820 RGB**, opaque sRGB albedo, **56,788 bytes**, final texture SHA-256:
`c2d73aa5150379de43637c0a1a73984dd0f6566bd4724c44878cd4ce5a0ebc36`.
White base multiplier, roughness **0.8**, metallic **0**; no alpha, emission, normal or ORM.
Linear mipmapped filtering, clamp/no repeat. Lossless import, mipmaps explicitly enabled,
automatic 3D compression changes disabled. The engine check asserts mipmaps on the actual
imported image, not only in metadata. No embedded images in the reused GLB.

The prefab inherits the complete base hardware and overrides exactly one property:

`Visuals/Model/CitySignSupports01/artwork_carrier:surface_material_override/0`

The original slot name is asserted as `sign_face`; `mount_metal` on slot 1 and all remaining
surfaces are untouched. Imported `Visuals/Model` remains an identity-transform linked
instance. No copied mesh resources, runtime appearance script or global material override.
This uses the authorized narrow **static artwork editable-child face-slot override exception**
in [Prefabs](../../assets.md#prefabs-and-authored-placement).

After initial normalization, **two consecutive load/pack/save/reload cycles are byte-stable**,
including scene UID, unique IDs, imported ancestry and override. Final prefab SHA-256:
`868a11b405d801b01aeff8777c6c9891eb1f285e50e6a99356580c3ce803bac9`.
The carrier retains `unique_id=16194531` and parent ancestry
`PackedInt32Array(728591687, 1891583522)`. Scene/material UIDs are inline, texture UID is in
`.import`, and checker UID in `.gd.uid`. This engine generates no separate `.tscn.uid` or
`.tres.uid` for these resources.

**Visual-only wall-mounted decoration.** The facade owns actor/car blocking, matching the
accepted hardware and standing flush-face rule. Never use this as a freestanding obstacle.
No new collider, physics state, interaction, rig, animation, socket, destruction or light.
Placement must preserve facade collision and keep its 0.10 m projection out of restricted
passages; no placement acceptance is claimed.

Live editor/MCP access was forbidden. Text-authored resources were normalized by isolated,
pinned headless Godot; no owner live Blender/Godot/MCP session was touched. No separate open
scene is claimed synchronized. Existing project plugins automatically start/stop local servers
during checks; no MCP requests were sent.

## Evidence and measured validation

[Hero](d02_neighbourhood_graphics_02-evidence/hero.png),
[side](d02_neighbourhood_graphics_02-evidence/side.png),
[face detail](d02_neighbourhood_graphics_02-evidence/detail.png),
[47 m / 42° overhead](d02_neighbourhood_graphics_02-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders, **1280×720**, 24 samples, denoised, AgX,
PNG compression 100, display dithering disabled; each under 288 KB. The shared notice studio
supplies identical camera/light conditions for family comparison. Temporary wall, ground,
camera and lights are evidence-only and never saved/exported. All four final images were
opened and inspected: clean restrained palette, clear car/bay motif and upright readable
close-range copy, no clipped letters, mirrored UVs or rounded-crop loss.

Overhead: vertical-down perspective from Blender **(8,9,47)**, **42° vertical FOV**, north-up,
with the unscaled panel at mounting height **1.6 m**. It reads as a tiny foreshortened ivory
strip: **neither text nor car icon is reliably readable at gameplay scale**. This intentionally
subordinate decoration must not carry essential gameplay information. Higher texture
resolution cannot expose a vertical face. No populated-world/target-renderer acceptance is
implied by these Blender renders or by the texture-downsample test.

[validation.json](d02_neighbourhood_graphics_02-evidence/validation.json) records:

- Reused panel: **1,380 source vertices, 1,792 exported vertices, 2,720 triangles,
  12 meshes, 13 surfaces**; **zero new geometry** from this artwork.
- Zero degenerate faces/triangles and non-manifold edges; positive component volumes,
  consistent outward winding, unit source/export normals and identity transforms.
- Metre units, exact inherited bounds/pivot and all **36** front UV samples pass.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
  Fresh read-only saved-source reexport exactly matches the committed **75,768-byte** GLB:
  `5f54105825e00bb73c038bed252910abec548ad1beb81603b2713c2c69796e0b`.
- Godot **4.8.dev7.official.c971f93e7**: full headless import and separate runtime dependency
  check exit 0 with no ERROR/SCRIPT ERROR lines; runtime has no WARNING lines.
- Hierarchy, transforms, mesh resources, actual mipmaps, face-only override, bounds and two
  byte-stable save/reload cycles pass. Shared source/tool dependencies remain unchanged.
- Four Python tests pass: exact PNG reproduction, safe crop margin, independent car/bay and
  palette samples, small-texture car-contrast proxy. The last is not gameplay evidence.
- gdstyle **0.3.0** formatting and lint pass, zero warnings on the owned checker.

[manifest.json](d02_neighbourhood_graphics_02-evidence/manifest.json) fingerprints every produced
payload except itself and uncommitted Python caches. Shared dependencies are fingerprinted in
validation rather than copied. [final.log](d02_neighbourhood_graphics_02-evidence/final.log)
retains concise outcomes; full logs and scratch reexport live outside Git at
`C:/tmp/ft/assets/d02_neighbourhood_graphics_02/`.

## Exact reproduction

From the worktree root; never a windowed or live editor:

```sh
N=d02_neighbourhood_graphics_02
S=C:/tmp/ft/assets/$N
mkdir -p "$S"
python tools/asset_production/$N/author.py
python -m unittest discover -s tools/asset_production/$N -p 'test_*.py' -v

timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8 \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/validate.py

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8 \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/preview.py

timeout 300 "$(mise which godot)" --headless --path . --import
timeout 60 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/$N/check_prefab.gd -- --normalize
cp "$S/prefab.json" "$S/roundtrips.json"
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 60 "$(mise which godot)" --headless --path . \
  --script res://tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" fmt --check tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/$N/check_prefab.gd
python tools/asset_production/$N/finalize.py
# Write only after an intentional payload change; default verifies.
python tools/asset_production/$N/manifest.py --write
python tools/asset_production/$N/manifest.py
```

`validate.py` refreshes the source-only receipt; `finalize.py` requires current runtime,
normalization, tests and render receipts, rejecting changed dependency/prefab hashes.
No `tools/production_checks.py` run, per owner decision 52.

## Diagnostics and remaining acceptance

One initial lint check found a 104-character texture-path line; wrapping it fixed the warning,
and final formatting/lint pass. No source/export, artwork-test, import or prefab assertion
failed. The successful headless **editor normalization** emits the existing plugin-version
warning, aborted-scan warning and editor shutdown RID/ObjectDB leak diagnostics. Its resource
assertions pass, but normalization is not described as diagnostic-free. Full imports and the
separate non-editor dependency check are clean of errors. Blender emits existing node-API
deprecation warnings, with no source/export/audio failure.

Pending: independent technical/art review, final fictional copy selection, saved facade/world
placement and passage clearance, actual populated gameplay-camera/renderer visibility, packaged
texture filtering and repeat-placement/Deck performance. Future hardware/tool changes must
recheck the saved face override and dependencies. No new movement, collision, multiplayer or
platform acceptance is claimed. No registry, progress, shared brief, TODO or sibling file changed.
