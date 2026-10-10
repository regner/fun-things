# city_sign_supports.02 — Freestanding low panel

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay/device acceptance pending.** Produced by the commissioned implementation
worker on `lane/a-signs`. The production lead owns acceptance and downstream integration.
[Commission](commission.md) and the current per-asset production brief supersede the
historical concept-only restrictions in [city_sign_supports](../city_sign_supports.md).
No register, shared brief, world placement, road tool or gameplay code was changed.

## Design and dimensions

An original low, twin-post civic/parking/loading panel: broad rounded petrol frame,
inset neutral face and gasket, closed quiet rear shell, two rear clamps, square posts,
cast shoes and shallow metal feet. The four material colors match the delivered
[wall panel .01](city_sign_supports_01.md); the frame uses the same continuous profiled
ring construction rather than four disconnected strips. No brands, lettering, downloaded
geometry, image-to-mesh, textures, or district-specific copy are included.

The lead explicitly approved these **provisional authored dimensions**, not measurements
from a concept image. The lead also required one simple static collider for freestanding
street furniture; the simplified full box is intentional even in the visual gap below
the panel. Layout acceptance remains pending.

| Quantity | Metres / contract |
| --- | --- |
| Overall Godot X/Y/Z size | **1.60 × 1.35 × 0.40** |
| Godot AABB | min `(-0.80,0,-0.20)`, max `(0.80,1.35,0.20)` |
| Ground pivot | `(0,0,0)`, centred between feet; no buried geometry |
| Panel body | Width 1.60, height 0.55; bottom 0.80, top 1.35 |
| Frame depth | Blender Y=-0.060…0.080; rear shell reaches -0.062 |
| Posts | Centres X=±0.58; 0.10 square; Blender Y=-0.018 |
| Feet | Each 0.28 wide × 0.40 deep × 0.055 high |
| Outer corner radius | 0.060, six segments per quarter |
| Artwork face | **1.44 × 0.39**, bottom 0.88, top 1.27; radius 0.022 |
| Artwork plane | Godot Z=-0.071; recessed 0.009 behind frame lip |
| Safe copy rectangle | 1.38 × 0.33, centred in face |
| Numeric tolerance | Envelope ±0.001; source/export coordinates ±0.00001 |

Metre units, applied transforms, no negative scales. Blender +Z maps to Godot +Y;
Blender +Y maps to Godot -Z (the front). Both mesh origins and the root are identity
at the ground datum. No corrective prefab rotation or scale. Suitable for forecourts,
parking islands and loading edges; do not obstruct passage mouths, escape routes or
junction views. The low height is not a claim of validated vehicle visibility.

## Source, export and artwork interface

- [Blender source](../../../art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend)
- [Explicit GLB](../../../art/models/environment/city_sign_supports_02/city_sign_supports_02.glb)
  and adjacent `.import` identity/settings.
- [Linked prefab](../../../scenes/prefabs/environment/city_sign_supports_02.tscn)
- [Author](../../../tools/asset_production/city_sign_supports_02/author.py),
  [export](../../../tools/asset_production/city_sign_supports_02/export.py),
  [source/binary validation](../../../tools/asset_production/city_sign_supports_02/validate.py),
  [headless prefab/motion checks](../../../tools/asset_production/city_sign_supports_02/check_prefab.gd).

Collection `export_city_sign_supports_02` contains exactly root `CitySignSupports02`,
`CitySignSupports02_Hardware` and `CitySignSupports02_ArtworkCarrier`. Hardware subparts
are joined into one mesh but remain editable connected components; each is a closed
manifold solid. Interlocking parts deliberately are not a single boolean-unioned shell.
Studio plane, lights and camera stay outside the export collection. Blender
**5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; shared
`tools/assets/blender/export_settings.json`, static animation/skin export disabled.

Four opaque, backface-culled Principled materials: `support_petrol`, `recess_gasket`,
`mount_metal`, `sign_face`. Exact linear PBR factors are in validation.json. No emission,
embedded images, external textures, rig, animation, damage states or sockets. No bespoke
LOD is warranted without a measured limit; Godot's default automatic LOD import remains
on. Imported tangent/shadow generation is unchanged. This is not a performance budget.

**Replace only `CitySignSupports02_ArtworkCarrier` slot 0 `sign_face`.** Slot 1
`mount_metal` owns carrier sides/back. Hardware is separate. UV0 `UVMap` covers the
single front face from 0–1, rounded corners clipping artwork. Use an opaque sRGB albedo,
white color multiplier, clamp (not repeat), and **48:13** image aspect (e.g. 1440×390).
Resolution, filtering and mip review belong to the artwork owner, not this blank carrier.
Blender UV: U=(0.72-X)/1.44, V=(Z-0.88)/0.39. glTF V is 0 at image top and 1 at bottom.
Viewed from the front, screen right is -X, as in .01. Actual exported positions/UVs/normals
are checked, including upright, nonmirrored mapping. District materials can change without
new hardware, GLB geometry or model duplication. No runtime material-swapping API is added.

## Prefab and bounded collision checks

`Visuals/Model` is the identity-transform imported instance, with no embedded render mesh,
editable imported children or runtime-composed hierarchy. Static collision is separate:
`Collision/Body/Shape`, one BoxShape3D **(1.60,1.35,0.40)** centred at **(0,0.675,0)**;
world layer **1**, mask **0**. The full box intentionally blocks passage/shots through
the visual under-panel gap; no crouch/underpass mechanic is implied. No breakability,
interaction or authoritative state is introduced.

Headless load, pack/save/reopen/resave preserved scene bytes and UIDs. GLB UID
`uid://bcgx64ss75j2s`; prefab UID `uid://bi65yynmg6q4t`. Scene identities are embedded;
Godot generated the check script's required `.gd.uid` sidecar. There is no `.tscn.uid`
sidecar for this text scene. Pinned engine **4.8.dev7.official.c971f93e7** resolves the
linked model and both meshes/five surfaces, matching measured bounds within 0.001 m.

Physics ray checks: centre below panel blocked by the deliberate box; X=0.9 bypass clear;
Y=1.6 overhead clear. A separate runtime invocation instantiates the **production player**
(0.35 m capsule radius / 1.8 m height) and calls `ActorMotion.step` for 60 fixed ticks/case.
Authority and replay both stop at **Z=0.550780952 m**, starting at Z=2 and moving -Z.
X=1.3 bypass reaches **Z=-2.999999762 m**. Independent endpoint bounds are asserted.
These are bounded production-API checks, not transport/admission/multiplayer proof,
vehicle handling, populated-city clearance or approved placement.

## Evidence and validation

[Hero](city_sign_supports_02-evidence/hero.png) ·
[Side/rear](city_sign_supports_02-evidence/side.png) ·
[Frame/face detail](city_sign_supports_02-evidence/detail.png) ·
[47 m / 42° overhead](city_sign_supports_02-evidence/overhead_47m_42deg.png).
All four were visually inspected after final rendering. Smooth broad frame highlights,
recessed face and grounded feet remain legible close up; back clamps are restrained.
Initial hero/side framing clipped the extremities and was widened before final evidence.

All are isolated Blender renders, **1280×720**, PNG compression 95, no dithering, Cycles
CPU 32 samples/denoising, AgX. Hero/side use orthographic scale 3.4; detail scale 1.35.
The overhead camera is vertical-down perspective, north-up, height **47 m**, vertical FOV
**42°**; 720-pixel height follows the current lean-evidence cap rather than the historical
800-pixel frame. Exact studio cameras/lights are in author.py. The overhead hardware is a
small quiet strip, and the vertical face is effectively edge-on at screen centre: **copy
is not gameplay-readable here**. Do not make it the only mandatory navigation cue. These
are not Godot screenshots, district-lighting acceptance or actor-occlusion measurements.

[validation.json](city_sign_supports_02-evidence/validation.json) records:
**2,448 triangles; 1,244 source vertices; 1,596 split GLB vertices; two mesh objects;
five surfaces; zero degenerate source faces/export triangles; zero nonmanifold source
edges; unit source/export normals; outward winding; correct ground pivot and bounds**.
Fresh export from the saved source is **byte-identical**, GLB **70,712 bytes**.
The [manifest](city_sign_supports_02-evidence/manifest.json) hashes all produced source,
export/import, prefab/tool/doc and lean evidence files, except itself to avoid self-hashing.
[Final concise log](city_sign_supports_02-evidence/final.log) records checks and diagnostics.
Scratch renders, retry logs and test mirrors remain outside the repository.

Production checks pass with the explicitly resolved mise tools and UTF-8 environment:
owned GDScript formatting/lint/all-script compilation; **14 Python tests**; **86 GUT tests,
2,178 assertions**; GUT import and intentional-negative failure detection. Owned GDScript
also passes direct pinned gdstyle with zero warnings. No known fixture errors needed to
be waived on this checkout.

### Diagnostics and limitations

- The requested default production-check command initially failed before tests: the
  Windows PATH shim/version subprocess hit cp1252 decoding and returned no engine version.
  Explicit `--godot`/`--gdstyle` from mise plus `PYTHONUTF8=1` resolved it; the complete
  suite then passed. No shared tooling/configuration was edited.
- Initial motion testing inside editor mode failed because production `ActorMotion` is
  not a tool script. Checks are now split: editor saves resources; runtime executes
  production motion. Helper returns fail closed if an assertion aborts. Final runtime
  logs have no error/warning diagnostics.
- Direct headless editor save checks exit 0 with successful assertions but emit shutdown
  GUI RID/ObjectDB leak diagnostics. A no-asset, timer-and-quit script in the production
  checker’s plugin-disabled mirror reproduces the same viewport/texture/scenario/font
  leaks (166 objects versus 168 with development plugins). Thus this is a bounded
  editor/SceneTree shutdown limitation, **not a clean editor exit claim**. The normal
  `--import --quit` path and canonical isolated compilation/GUT suite pass. The enabled
  development MCP plugin also warns that Godot 4.8 is newer than its tested 4.7 version.
  No live owner session was used or modified, and no diagnostic was suppressed.
- Blender reports future `use_nodes` deprecation warnings; final author/export/validation
  commands exit 0 without topology or dependency errors.

## Exact reproduction

Run from the worktree root in Bash; commands are bounded and never launch a windowed editor.
Use a fresh empty checks output directory on rerun (the canonical tool requires it).

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
NID=city_sign_supports_02
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/author.py
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/validate.py
# validate.py also reopens the saved source and freshly exports into C:/tmp/ft/assets/$NID/reexport.
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script res://tools/asset_production/$NID/check_prefab.gd
timeout 180 "$GODOT" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd
timeout 30 "$GDSTYLE" --max-warnings 0 tools/asset_production/$NID/check_prefab.gd
timeout 1800 env PYTHONUTF8=1 python tools/production_checks.py --godot "$GODOT" --gdstyle "$GDSTYLE" --output C:/tmp/ft/assets/$NID/checks-reproduce
```

For export-only use the same pinned Blender flags, load
`art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend`, then
`--python tools/asset_production/city_sign_supports_02/export.py -- C:/tmp/ft/assets/city_sign_supports_02/export-only`.
Rerunning source validation replaces validation.json measurements; run the editor/runtime
checks afterwards to restore engine results. Refresh manifest hashes after any artifact change.

## Remaining acceptance

Independent art/technical review; final placement, actor/target visibility and vehicle
movement/query checks; actual separate-process multiplayer collision behavior; district
artwork/material readability; actual engine gameplay-camera/lighting captures; repeated
placement profiling, packaged builds and Deck performance remain **pending**. The
source/prefab is ready for those downstream checks, not a claim that the whole asset
register or all production acceptance gates are complete. No TODO was closed.
