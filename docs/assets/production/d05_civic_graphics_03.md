# d05_civic_graphics.03 — Quay direction panel

10 October 2026. **Artwork/material and linked prefab delivered; bounded producer checks pass.
Independent review, final copy/bearings and world/device acceptance remain pending.** Produced
by the isolated implementation worker on `lane/a-d05`; parent/reviewer owns acceptance. The
current common production brief and [commission](commission.md) supersede the historical
concept-only scope of [Harbour civic graphics](../d05_civic_graphics.md).

## Design and provenance

One original three-direction face: **QUAY** with a left arrow, **HALL** with an ahead arrow,
and **SIGNAL ROW** with a right arrow. A small **OLD QUAY** heading and **ONWARD EVENTUALLY**
municipal aside provide restrained humour. Three broad filled arrows and quiet separators
carry the close-view hierarchy, not microprint, simulated wear or luminous outlines.

All copy and arrow bearings are **provisional decorative proposals**, not approved world
routes. The quay label denotes the waterfront; Signal Row denotes the neighbouring district,
not an invented bridge route or traversal promise. Layout must confirm actual bearings before
placement. There is no interaction, quest, minimap, navigation data or gameplay rule here.

The [hall fascia](d05_civic_graphics_01.md) and [noticeboard](d05_civic_graphics_02.md) own the
family grammar: slate **#344953**, ivory **#F6F1DC**, muted amber **#E9B96E**, broad continuous
capital paths, softened terminals and quiet fields. `author.py` imports those source paths
and palette, adding only the previously unused V/W characters. This is original Python/Pillow
artwork, supersampled 3x then downsampled once; no bitmap-grid font, downloads, real brands,
external fonts, purchased/generated images or separate font licensing payload. Python 3.14.2
and Pillow 12.3.0. Earlier family recipes and outputs are unchanged.

References inspected: Petrol & Coral direction; Stage 3 Old Quay identity; Stage 4 smaller
quay streets; Old Quay asset breakdown and shared concept contract; shared civic supports;
low-panel/wayfinding hardware handoffs; earlier civic graphics; city_lights.01 source/export,
evidence and batch 01–03 prefab conventions. No dimensions were inferred from concept rasters.

## Source, material and reused carrier

The standing reuse rule applies: **no duplicate per-ID .blend, GLB, carrier or exporter**.
The editable artwork source is `tools/asset_production/d05_civic_graphics_03/author.py`.
The existing low panel provides one generous face for all three destinations without adding
another mast or frame. The Blender-linked chain remains [city_sign_supports.02](city_sign_supports_02.md):

- Source: `art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend`.
- Collection/root: `export_city_sign_supports_02` / `CitySignSupports02`.
- Export: `art/models/environment/city_sign_supports_02/city_sign_supports_02.glb`.
- Base prefab: `scenes/prefabs/environment/city_sign_supports_02.tscn`.
- `validate.py` invokes that owner's source/binary validator and exporter, redirecting only
  two exact output-path assignments in memory because the legacy audit has no output-path
  API. All source/topology/UV/export assertions and shared export settings remain unchanged.
  Receipts/reexports go to external scratch. Dependency hashes are checked before/after;
  no shared source is saved and no private replacement geometry validator is introduced.

Runtime texture: `art/textures/environment/d05_civic_graphics_03/direction_panel_albedo.png`
and pinned-engine `.import`. **1440 x 390 RGB**, 48:13, opaque sRGB albedo; **43,768 bytes**;
SHA-256 `88d2875e68b7ff129d94f16977fa1965bb076ef26b4a311680b71595198e3d2a`.
No normal/ORM/emission maps or embedded images. Material:
`art/materials/environment/d05_civic_graphics_03/direction_panel.tres`; white multiplier,
metallic 0, roughness 0.56, backface culling, no transparency/emission, linear mipmapped
filtering, clamp/no repeat. Texture import is lossless with mipmaps enabled and automatic
3D compression changes disabled. No runtime material writer or UV correction is introduced.

## Dimensions and attachment

Inherited provisional carrier measurements, Godot metres; tolerance +/-0.001 m:

| Interface | Contract |
| --- | --- |
| Overall X/Y/Z | **1.60 x 1.35 x 0.40** |
| AABB | min **(-0.80,0,-0.20)**, max **(0.80,1.35,0.20)** |
| Pivot | Ground `(0,0,0)`, centred between feet |
| Artwork face | **1.44 x 0.39**, bottom Y=0.88, top Y=1.27 |
| Artwork plane | Z=**-0.071**, recessed 0.009 behind frame lip |
| Safe content | Centred **1.38 x 0.33**; outer **30 px** on every edge stays slate |
| UV0 | U grows toward Blender -X; V grows toward Blender +Z |
| GLB UV | Image V=0 at top, V=1 at bottom; upright/unmirrored from front |
| Axes | Blender +Y/+Z converts once to Godot -Z/+Y |

No dimension, transform, slot, rig, animation, socket or LOD change. Rounded face corners
clip only quiet margins. The panel stays at its source scale and upright orientation.

## Saved prefab and collision

`scenes/prefabs/environment/d05_civic_graphics_03.tscn` inherits the existing low-panel
prefab. `Visuals/Model` remains an identity-transform linked imported GLB. Exactly one
saved override changes appearance:

`Visuals/Model/CitySignSupports02/CitySignSupports02_ArtworkCarrier: surface_material_override/0`

Slot 0 is `sign_face`; slot 1 `mount_metal` and every hardware surface remain unchanged.
No copied mesh, duplicate coplanar plane, global override or added node hierarchy. This uses
the authorized **static artwork face-slot editable-child exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement). After initial
normalization, **two complete save/reload cycles preserve scene bytes, identities and UIDs**.
Three identical SHA-256 snapshots:
`87c9e94b57933a5acada03333bcb77310b6ce122d95eabeaaff04c203af74287`.
Final import and two fresh runtime processes retain the hash and resolve all five
prefab/base/model/material/texture UIDs. Prefab UID: `uid://bmquyr57xaguh`.

The freestanding panel retains exactly **one existing StaticBody3D and one BoxShape3D**,
size **(1.60,1.35,0.40)**, centre **(0,0.675,0)**, layer **1**, mask **0**. The conservative
full box intentionally blocks the under-panel gap; it is not an underpass. The variant
shares the exact base shape resource and child transforms. Actual physics rays hit the
centre at Y=0.7, clear the side at X=0.9 and clear above at Y=1.6. No gameplay state,
authority, movement rule or collision dimension changes.

Place this prefab **instead of**, not on top of, a blank low panel. Keep the envelope out
of passage mouths and narrow routes. No district placement or mounting-reference scene
is introduced. The hardware handoff's current remaining-acceptance artwork item now links
here, and only its doc hash/byte count is refreshed in its manifest under the standing
sibling-status exception; historical receipts remain untouched. The earlier civic `.01`
and `.02` handoffs contain no stale pending `.03` item and are unchanged.

## Evidence and validation

[Hero](d05_civic_graphics_03-evidence/hero.png) ·
[Side](d05_civic_graphics_03-evidence/side.png) ·
[Face detail](d05_civic_graphics_03-evidence/detail.png) ·
[47 m / 42-degree overhead](d05_civic_graphics_03-evidence/overhead_47m_42deg.png).

All four were personally inspected. Isolated Blender Cycles CPU, 32 samples/denoising, AgX,
**1280 x 720**, RGB PNG compression 95, no dither; each below 181 KB. Hero/side show complete
hardware without clipping; detail shows clear arrows, upright lettering and safe inset
margins. The straight-down north-up perspective uses **47 m height / 42-degree vertical FOV**
at real scale. At screen centre the panel is a tiny strip and its vertical face is edge-on:
**copy and arrows are not gameplay-readable overhead and must not be essential navigation**.
No tilted/enlarged panel, extra roof symbol or emission was invented to mask this limitation.
These are Blender renders, not Godot screenshots or populated-world visibility acceptance.

Final [validation.json](d05_civic_graphics_03-evidence/validation.json) records:

- Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**.
- Reused carrier: **1,244 source vertices / 1,596 GLB vertices / 2,448 triangles**;
  **2 meshes / 5 surfaces**, four hardware materials; no new geometry.
- **Zero degenerate source faces/export triangles; zero non-manifold source edges**;
  unit source/export normals, outward winding, applied transforms/metre units and ground datum.
- Source/decoded GLB bounds and face UVs match the carrier. The 28 imported face vertices
  have maximum UV error **0.000030677**, below **0.00005** attribute-compression tolerance.
- Fresh saved-source reexport **byte-identical**, **70,712 bytes**, SHA-256
  `022dd559334d79c482182083be775c692ab4adf2a5277d3fb7ca7ec266ec76b7`.
- **Four Python tests pass**: deterministic PNG/format, 30 px safe rectangle, independently
  sampled arrow bearings and asymmetric upright lettering/quiet fields.
- Pinned Godot **4.8.dev7.official.c971f93e7** final import: no ERROR/SCRIPT ERROR.
  Two identical fresh runtime receipts verify unchanged hierarchy, mesh/collider resources,
  face-only material override, filtering/mipmaps, bounds, imported UVs, UIDs and physics rays.
- Two byte-stable save/reload cycles; GDScript format check and zero-warning lint pass.

[manifest.json](d05_civic_graphics_03-evidence/manifest.json) hashes every produced payload
except itself/cache, including this doc, tests, sidecars, receipt and four renders.
`record.py` reuses the earlier civic manifest inventory helper without editing it.
[final.log](d05_civic_graphics_03-evidence/final.log) retains concise final results and actual
diagnostics. Scratch exports/retry logs remain at `C:/tmp/ft/assets/d05_civic_graphics_03/`.

## Exact reproduction

From the worktree root in Git Bash; never use a live editor session:

```sh
NID=d05_civic_graphics_03
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
stale scene snapshots or changed dependencies. No `tools/production_checks.py` run (owner
decision 52). Text material/prefab authoring followed by headless save/reload is the mandated
fallback because the windowed editor is unavailable. No owner's live Blender/Godot/MCP
session was accessed or claimed synchronized. Committed texture import options preserve the
explicit mipmap/lossless settings on fresh checkout.

## Diagnostics and remaining acceptance

The first artwork invocation revealed the family alphabet lacked W/V; only those original
paths were added here. One initial test sampled a header gap instead of its O stroke; the
fixed independent stroke coordinate passes without loosening tolerance. No failed run is
counted as a passing receipt. Texture import was initially generated with default mipmaps
off; the owned sidecar was set to the family mipmapped/lossless contract before normalization.

Normalization exits 0 with stable scenes but retains the known pinned-editor scan-abort,
RID and 168 ObjectDB-instance shutdown leak diagnostics and plugin compatibility warning.
It is **not a clean editor shutdown log**. Final import has only the existing plugin's
4.8-versus-tested-4.7 warning; both runtime logs have no ERROR/WARNING/SCRIPT ERROR.
Blender emits future node-API deprecation warnings. No global settings, addon edits or broad
error suppression were introduced.

Pending: independent art/technical review; final copy and arrow-bearing selection against
actual routes; district placement; actual Godot lighting/filtering and populated gameplay-
camera/actor visibility review; world movement/aim/vehicle and relevant multiplayer checks;
packaged builds, repeated-placement profiling and target-device/Deck performance. This
unplaced decorative artwork claims no whole-world or full production acceptance and closes
no TODO. Family progress remains the registry's responsibility, not this pending list.
