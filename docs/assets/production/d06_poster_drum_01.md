# d06_poster_drum.01 — Short cylindrical poster support

**Source/export and bounded prefab checks delivered; independent review and gameplay
acceptance pending.** Commission: [production commission](commission.md), resumed by
the per-asset production task. Family: [poster drum](../d06_poster_drum.md).
Producer: commissioned implementation/modeling specialist. Supervisor approved the
provisional dimensions, blank wrap, cap interface and static cylinder envelope during
this handoff. No shared register, brief, project setting or world placement changed.

## Design and dimensions

Original Blender construction: a broad cylindrical ivory poster carrier between a
chunky cast petrol foot and a low, flat, rounded petrol cap. Quiet smooth shading,
opaque materials, no glow, logos, text, interactive parts or advertising system.
Signal Row supplies the commercial-corner context, not a new placement plan.
The 1.45 m height keeps the support below the 1.8 m reference actor; the small round
roof stays subordinate to people and the entertainment hall. This is a carrier,
not the commercial-graphics asset: its blank wrap is intentional.

Authored provisional measurements, **not measured from concept imagery**:

| Property | Metres |
| --- | --- |
| Complete Godot X/Y/Z size | 0.90 / 1.45 / 0.90 |
| Godot AABB min → max | (-0.45, 0, -0.45) → (0.45, 1.45, 0.45) |
| Foot maximum diameter / top of foot transition | 0.89 / 0.24 |
| Poster surface radius / bottom / top | 0.397 / 0.24 / 1.28 |
| Poster usable height / circumference | 1.04 / approximately 2.4945 |
| Standard cap bottom / top / maximum radius | 1.35 / 1.45 / 0.45 |
| Body top seating radius | 0.42 |

Ground-centred origin (0,0,0), metre units, applied identity object transforms.
Blender +Z becomes Godot +Y; Blender +Y/front becomes Godot -Z. Bounds tolerance
±0.001 m; source/export coordinate tolerance 0.00001 m. No gameplay clearance
margin is implied by those tolerances.

### Family .02 and commercial-graphics interfaces

`D06PosterDrum01_Body` and `D06PosterDrum01_Cap` are separate closed meshes under
`D06PosterDrum01`, in `export_d06_poster_drum_01`. Both origins remain at ground,
not at their individual geometric centres. The next family specialist can reuse
the **unchanged body** from this saved source and author a replacement cap at
Y=1.35 m in Godot (Z=1.35 m in Blender), with maximum radius 0.45 m and mating
radius 0.42 m. Do not stack an alternate cap on top of the existing cap. No .02
output is created by this task, and no socket/animation is required.

Body material slot 0 is `drum_frame_petrol`; slot 1 is `poster_wrap`. Cap slot 0
is `drum_frame_petrol`. `UVMap`/glTF TEXCOORD_0 maps the complete poster surface
once over [0,1]². U=0/1 is the rear seam (Godot +Z); U=0.5 is front (-Z).
Blender V=0 is the lower edge and V=1 the upper edge; glTF reverses V for its image
convention (top V=0, bottom V=1). Suggested artwork aspect is 2.4945:1.04, about
2.40:1. Use a seamless full-width wrap, repeat disabled/clamped edges, mipmaps,
opaque material. Future graphics resolution/filtering remain the artwork owner's
choice. No duplicate decal mesh or embedded placeholder image is supplied.

## Source, export, materials and prefab

- Source: `art/source/models/environment/d06_poster_drum_01/d06_poster_drum_01.blend`.
- Export: `art/models/environment/d06_poster_drum_01/d06_poster_drum_01.glb`, with
  its Godot `.import` metadata.
- Recipe/checks: `tools/asset_production/d06_poster_drum_01/author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` and its engine-generated `.uid`.
- Prefab: `scenes/prefabs/environment/d06_poster_drum_01.tscn`; embedded scene UID
  and Godot-generated node identities retained. No separate TSCN `.uid` is needed.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. The export
script loads `tools/assets/blender/export_settings.json`, overrides the explicit
collection, disables skins/animations, and exports only its three declared objects.
Studio floor/camera/lights remain outside that collection. No prototypes, downloads,
image-to-mesh, paid assets, fonts or third-party textures were used.

Two Principled materials, no texture dependency: frame linear RGB (0.025, 0.075,
0.09), metallic 0.4, roughness 0.43; ivory (0.922, 0.880, 0.716), metallic 0,
roughness 0.7. Both opaque and backface-culled; no emission. Actual exported
material values are recorded in validation.json. Import-generated LODs and shadow
meshes use the existing defaults; no custom LOD or performance budget is claimed.

The wrapper follows the existing street-furniture convention: imported GLB at
identity `Visuals/Model`, with separate `Collision/Body` StaticBody3D and direct
`Shape` child. The CylinderShape3D is radius 0.45 m, height 1.45 m, centre Y=0.725 m,
static-world layer 1 / mask 0. This intentionally simple envelope includes the cap
and avoids decorative snag points. No runtime mesh/hierarchy construction, material
override, light, script, navigation, interaction or destruction component is attached.

## Evidence and validation

[Hero](d06_poster_drum_01-evidence/hero.png),
[side](d06_poster_drum_01-evidence/side.png),
[cap detail](d06_poster_drum_01-evidence/cap_detail.png),
[47 m / 42° overhead](d06_poster_drum_01-evidence/overhead_47m_42deg.png).
The first three are 900×900 isolated Blender renders. The overhead is vertical-down,
north-up, perspective 1280×800, 47 m height, 42° vertical FOV. All four were visually
inspected: smooth quiet circular silhouette, broad uninterrupted wrap, no tiny
advertising detail. At the calibrated overhead view the roof is roughly 20 pixels
across; the side wrap is not essential overhead-readable information. These are
not Godot gameplay screenshots, populated-scene or actor/hall comparison evidence.

[validation.json](d06_poster_drum_01-evidence/validation.json) records:

- **2,296 triangles; 1,152 Blender vertices; 1,556 exported vertices; two meshes;
  three surfaces using two materials.**
- Zero non-manifold edges, zero degenerate source faces and zero degenerate GLB
  triangles. Unit-length source corner and exported normals.
- Correct literal approved bounds, ground pivot, identity transforms, wrap UV
  extent, cap seating plane, and no cameras/lights/skins/animations/images in GLB.
- Fresh export from the reopened saved source is **byte-identical** to the 66,628-byte
  committed GLB (SHA-256 in the report).
- Pinned Godot **4.8.dev7.official.c971f93e7**: imported ancestry, two meshes/three
  surfaces, bounds, resolved model/prefab UIDs and byte-stable save/reload pass.
- Actual physics ray queries hit the centre cylinder and clear its side and top.
  This is a bounded query check, not actor/car motion or network acceptance.

The final script is formatter-clean, lint-clean and explicitly compiles. Canonical
production checks pass nine Python tests, nine GUT tests / 70 assertions, GUT import,
engine/vendor pins and the intentional-negative GUT test. The overall suite is
**not green**: only the authorized pre-existing five fixture compile failures
(missing S02ActorMotion/S02AimProbe) and formatting in `batch_observation.gd`,
`integration/batch03_author.gd`, and `integration/inspector.gd` remain. The owned
script compiles in the canonical 46-script report; final targeted checks also pass.

The concise [final log](d06_poster_drum_01-evidence/final.log) classifies diagnostics.
Headless editor packing exits 0 with passing assertions but emits editor teardown
RID/ObjectDB leak diagnostics and the toolkit's 4.8-version warning. A separate
headless runtime load exits 0 with **no errors, warnings or missing dependencies**.
Neither exit status nor import alone is treated as all-script validation. Early
runtime-mode saves lacked UIDs; editor-mode save corrected them. One local typing
error and lint warnings were corrected; a signal-based scan wait stalled, replaced
by bounded frame polling. Scratch attempts/logs stay outside the repository.

## Exact reproduction

Run from the repository root in Bash; `mise exec` supplies the pinned Python,
Godot and gdstyle. No owner's live editor/Blender session is used. Prefab text was
normalized with isolated headless editor mode because windowed editor/toolkit
mutation is disallowed by this production task. Existing open scenes are not
claimed synchronized by these headless checks.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
N=d06_poster_drum_01
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/$N/author.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/$N/validate.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  art/source/models/environment/$N/$N.blend --python-exit-code 1 \
  --python tools/asset_production/$N/export.py -- C:/tmp/ft/assets/$N/reexport
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/$N/check_prefab.gd
timeout 180 "$(mise which godot)" --headless --path . \
  --scene res://scenes/prefabs/environment/$N.tscn --quit-after 3
timeout 180 "$(mise which godot)" --headless --path . --check-only \
  --script res://tools/asset_production/$N/check_prefab.gd
mise exec -- gdstyle fmt --check tools/asset_production/$N/check_prefab.gd
mise exec -- gdstyle --max-line-length 100 --max-warnings 0 \
  tools/asset_production/$N/check_prefab.gd
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/$N/checks
```

Production-check output must be a fresh directory; final recorded suite output is
`C:/tmp/ft/assets/d06_poster_drum_01/checks-complete/`. `validate.py` creates a
scratch reexport and compares bytes itself. Reauthoring the .blend can change its
internal save metadata; byte identity is asserted for a fresh GLB reexport, not
for Blender file regeneration. The producer `manifest.json` hashes every retained
asset file except itself (self-hashing is not possible), including import/UID
metadata, scripts, documentation and evidence.

## Remaining acceptance

Independent technical/art review is pending. Artwork remains the separate
`d06_commercial_graphics` owner's task. `.02` cap variant remains its separate row.
World integration must keep the support away from intersection sightlines,
passage mouths and bridge landings, test actor/car movement and aim, approve final
placement/dimensions, and refresh relevant collision/navigation data. Actual camera
readability, multiplayer/prediction collision behavior, repeated-placement cost,
packaged builds and sustained target-device/Deck performance remain pending.
No whole-register readiness, world placement or gameplay gate is marked complete.
