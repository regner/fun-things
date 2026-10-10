# d05_civic_graphics.02 — Noticeboard face

10 October 2026. **Artwork/material and linked prefab delivered; bounded producer checks pass.
Independent review, copy selection and world/device acceptance remain pending.** Produced by the
isolated implementation worker on `lane/a-d05`; parent/reviewer owns acceptance. The current
common production brief and [commission](commission.md) supersede the historical concept-only
scope of [Harbour civic graphics](../d05_civic_graphics.md).

## Design and provenance

One original three-notice layout: **OLD QUAY / PUBLIC NOTICES**, a large **TEMPORARY NOTICE /
UNTIL FURTHER NOTICE**, a smaller **QUAY MEETING / AGENDA TO COME**, and **LOST TIME / PLEASE
ENQUIRE**. Footer: **OFFICE OF TEMPORARY PERMANENCE**. A pediment, three piers and harbour line
link the board to the hall; one hourglass supplies a broad secondary symbol. All copy is
fictional and **provisional**, not an approved schedule, quest, interaction or navigation cue.

The [earlier hall fascia](d05_civic_graphics_01.md) owns the family grammar: slate **#344953**,
ivory **#F6F1DC**, muted amber **#E9B96E**, broad continuous lettering with softened terminals,
quiet borders and no luminous saturation. This recipe imports its original capital paths and
palette and adds only the letters required here. The three clean card fields replace noisy
microprint, modelled papers or grime. No real brands, downloads, external fonts, purchased or
generated images; original Python/Pillow path artwork, supersampled 3x and downsampled once.
Python 3.14.2 / Pillow 12.3.0. No separate font/license payload is required.

References read: approved Petrol & Coral direction; Stage 3 Old Quay municipal identity;
Stage 4 smaller quay streets; Old Quay asset breakdown/shared concept contract; shared sign
support brief and noticeboard handoff; earlier hall graphics and accepted city-light/batch
prefab conventions. Concepts are style references, not raster-derived dimensions.

## Source, material and reused carrier

The standing reuse rule applies: **no duplicate per-ID .blend, GLB, panel mesh or exporter**.
The artwork's editable source is `tools/asset_production/d05_civic_graphics_02/author.py`.
The Blender-linked chain remains the delivered [noticeboard hardware](city_sign_supports_03.md):

- Source: `art/source/models/environment/city_sign_supports_03/city_sign_supports_03.blend`.
- Collection/root: `export_city_sign_supports_03` / `CitySignSupports03`.
- Export: `art/models/environment/city_sign_supports_03/city_sign_supports_03.glb`.
- Base prefab: `scenes/prefabs/environment/city_sign_supports_03.tscn`.
- `validate.py` executes the existing source/binary validator, changing only its two exact
  output-path assignments in memory. The legacy audit has no callable output-path API.
  All owner assertions and shared exporter settings remain intact; receipts and reexports
  go only to external scratch. Shared source, export, import, prefab and tool hashes are
  checked before/after. No dependency is saved or private duplicate validator introduced.

Runtime texture: `art/textures/environment/d05_civic_graphics_02/noticeboard_albedo.png`
and pinned-engine `.import`: **1640 x 1040 RGB**, 41:26, opaque sRGB albedo; **128,077 bytes**;
SHA-256 `41a36e1a346cb99011d04512a0d545f3ab349ce9b4a52bb076b2248444295627`.
No normal/ORM/emission maps or embedded images. Material:
`art/materials/environment/d05_civic_graphics_02/noticeboard.tres`, white multiplier,
metallic 0, roughness 0.56, backface culling, no transparency/emission, linear mipmapped
filtering, clamp/no repeat. Texture import is lossless with mipmaps enabled and automatic
3D compression changes disabled. No UV correction, runtime swapping or artwork controller.

## Dimensions and attachment

Inherited provisional hardware dimensions, in Godot metres; tolerance +/-0.001 m:

| Interface | Contract |
| --- | --- |
| Overall X/Y/Z | **1.90 x 2.10 x 0.44** |
| AABB | min **(-0.95,0,-0.22)**, max **(0.95,2.10,0.22)** |
| Pivot | Ground `(0,0,0)`, centred between feet |
| Artwork face | **1.64 x 1.04**, bottom Y=0.90, top Y=1.94 |
| Artwork plane | Z=**-0.071**, recessed 0.009 behind frame lip |
| Safe content | Centred **1.58 x 0.98**; outer **30 px** on every edge stays slate |
| UV0 | U grows toward Blender -X; V grows toward Blender +Z |
| GLB UV | Image V=0 at top, V=1 at bottom; upright/unmirrored from the front |
| Axes | Blender +Y/+Z converts once to Godot -Z/+Y |

No dimensions, transforms, slots, rig, clips, sockets or LOD policy change. Rounded carrier
corners clip only the quiet margins. Ground hardware and the panel remain at their original
scale; do not enlarge or tilt this face to make the overhead camera read its text.

## Saved prefab and collision

`scenes/prefabs/environment/d05_civic_graphics_02.tscn` inherits the complete existing
noticeboard prefab. `Visuals/Model` stays an identity-transform linked GLB instance. The
sole saved appearance override is:

`Visuals/Model/CitySignSupports03/CitySignSupports03_ArtworkCarrier: surface_material_override/0`

Slot 0 is `sign_face`; slot 1 `mount_metal` and all hardware surfaces stay unchanged.
No copied mesh, duplicate coplanar plane, global material override or added node hierarchy.
This uses the authorized **static artwork face-slot editable-child exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement). After initial
normalization, **two full save/reload cycles preserve exact scene bytes, identities and UIDs**.
Three identical SHA-256 snapshots:
`268435056649d7ae20b7a2133b28f344c595b0f93b5a7989b709bf523f105644`.
A final import and two fresh runtime processes retain this hash and resolve all five
prefab/base/model/material/texture UIDs. Prefab UID: `uid://bhe22vtifyr12`.

The freestanding board retains exactly **one existing StaticBody3D and one BoxShape3D**,
size **(1.90,2.10,0.44)**, centre **(0,1.05,0)**, layer **1**, mask **0**. This unchanged
conservative envelope deliberately blocks the under-panel gap; it is not an underpass.
The graphics variant shares the exact base collision resource and child transforms.
Actual physics rays hit the centre at Y=0.7, clear the side at X=1.05, and clear above at
Y=2.3. No gameplay state, authority, movement rule or collision dimension is changed.

Place this prefab **instead of**, not on top of, a blank noticeboard. No saved district
placement or extra mounting reference is needed for this existing freestanding carrier.
Keep it out of passage mouths and narrow quay routes. The hardware's current remaining-
acceptance artwork item now links here; only that paragraph and its manifest doc hash/size
are refreshed under the standing sibling-status exception. Historical receipts are unchanged.
The earlier civic `.01` handoff contains no pending `.02` item, so it is untouched.

## Evidence and validation

[Hero](d05_civic_graphics_02-evidence/hero.png) ·
[Side](d05_civic_graphics_02-evidence/side.png) ·
[Face detail](d05_civic_graphics_02-evidence/detail.png) ·
[47 m / 42-degree overhead](d05_civic_graphics_02-evidence/overhead_47m_42deg.png).

All four were visually inspected. Isolated Blender Cycles CPU, 32 samples/denoising, AgX,
**1280 x 720**, RGB PNG compression 95, no dither. All below 284 KB. Hero/detail show upright
copy, safe recessed margins and the distinct three-notice hierarchy. Side framing was
widened after the initial preview cropped the cap/foot; final image includes the whole board.
The vertical-down north-up perspective uses **47 m height / 42-degree vertical FOV** at real
scale. The rain cap hides the vertical face at centre: **copy is unreadable overhead and
must not carry essential navigation**. No oversized symbol or camera tilt was invented.
These are Blender renders, not Godot screenshots or world/camera readability acceptance.

Final [validation.json](d05_civic_graphics_02-evidence/validation.json) records:

- Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**.
- Reused hardware: **1,340 source vertices / 1,711 GLB vertices / 2,636 triangles**;
  **2 meshes / 5 surfaces**, four hardware materials; no new geometry.
- **Zero degenerate source faces/export triangles; zero non-manifold source edges**;
  unit source/export normals, outward winding, applied transforms/metre units and ground datum.
- Source and decoded GLB bounds/face UVs match the carrier; 28 imported face vertices have
  maximum UV error **0.000015312**, below **0.00005** (Godot attribute compression tolerance).
- Fresh saved-source reexport **byte-identical**, **75,520 bytes**, SHA-256
  `f6ed9b4bd732c2e46104cf52453641e6c6e212483dd27d26d33a683dfefbdd8c`.
- **Four Python tests pass**: deterministic PNG/format, safe rectangle, three card fields,
  asymmetric lettering/emblem landmarks with bounded antialias tolerance.
- Pinned Godot **4.8.dev7.official.c971f93e7** import: no ERROR/SCRIPT ERROR.
  Two identical fresh runtime receipts verify mesh/hierarchy/collider identity, face-only
  override, material/filtering/mipmaps, bounds, imported UVs, dependencies and physics rays.
- Two byte-stable save/reload cycles; GDScript format check and zero-warning lint pass.

[manifest.json](d05_civic_graphics_02-evidence/manifest.json) hashes every produced payload
except itself/cache, including this doc, tests, sidecars, final receipt and four renders.
`record.py` reuses the existing civic manifest inventory helper without editing it.
[final.log](d05_civic_graphics_02-evidence/final.log) retains concise final outcomes and
actual diagnostics. Scratch exports/retry logs remain at `C:/tmp/ft/assets/d05_civic_graphics_02/`.

## Exact reproduction

From the worktree root in Git Bash; no live editor access:

```sh
NID=d05_civic_graphics_02
P="$(pwd -W)"
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
export PYTHONIOENCODING=utf-8
python "tools/asset_production/$NID/author.py"
python -m unittest discover -s "tools/asset_production/$NID" -p 'test_*.py' -v \
  > "$T/tests-final.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$P/tools/asset_production/$NID/validate.py" > "$T/validate.log" 2>&1
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$P/tools/asset_production/$NID/preview.py" > "$T/preview-final.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$T/import-first.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/normalize-final.log" 2>&1
cp "$T/prefab.json" "$T/roundtrips.json"
timeout 300 "$G" --headless --path . --import > "$T/import-final.log" 2>&1
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" > "$T/load-final.log" 2>&1
cp "$T/prefab.json" "$T/load-first.json"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" > "$T/load-second.log" 2>&1
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd" \
  > "$T/fmt-final.log" 2>&1
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd" > "$T/lint-final.log" 2>&1
python "tools/asset_production/$NID/record.py"
python "tools/asset_production/$NID/record.py" --manifest write
python "tools/asset_production/$NID/record.py" --manifest verify
```

`record.py` rejects script errors, missing success markers, mismatched runtime receipts,
stale scene snapshots or changed shared dependencies. No `tools/production_checks.py`
run (owner decision 52). Text scene authoring followed by pinned headless save/reload is
the mandated fallback: windowed editor unavailable; no owner's live Blender/Godot/MCP
session was accessed or claimed synchronized.

## Diagnostics and remaining acceptance

Initial lint caught one long redundant UID receipt field; removed those duplicate fields
in favour of the complete UID dictionary and reran lint. Formatting was rerun after that
edit; final format check passes. No failed run is counted as passing evidence.

Normalization exits 0 with stable scenes but retains the known pinned editor scan-abort,
RID and 168 ObjectDB-instance shutdown leak diagnostics and plugin compatibility warning.
It is **not a clean editor shutdown log**. Final import has only the existing plugin's
4.8-versus-tested-4.7 warning; both runtime logs have no ERROR/WARNING/SCRIPT ERROR.
Blender emits its future node-API deprecation warning. No global configuration changes or
broad error suppression were introduced.

Pending: independent art/technical review and final copy selection; district placement;
actual Godot lighting/filtering and populated gameplay-camera/actor visibility review;
world movement/aim/vehicle and relevant multiplayer checks; packaged builds, repeated-
placement profiling and target-device/Deck performance. Supporting district use is not
confirmed by this delivery. This unplaced decorative artwork claims no whole-world or
full production acceptance and does not close a TODO.
