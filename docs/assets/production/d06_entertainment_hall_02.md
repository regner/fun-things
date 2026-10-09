# d06_entertainment_hall.02 — Broad roof-ring trim

**Source/export and linked prefab delivered; independent review and full gameplay acceptance pending.**
Production follows the resumed per-asset commission, [family brief](../d06_entertainment_hall.md),
accepted Signal Row identity and the preceding [.01 shell](d06_entertainment_hall_01.md).
Original Blender construction by the commissioned production worker. No downloads,
external artwork, brands, image-to-mesh, prototype dependencies or runtime mesh generation.
The existing shell remains unchanged at lane predecessor `4af533e`.

## Design and provisional dimensions

One continuous broad magenta diffuser wraps the upper/outward shoulder of a petrol
rounded-rectangle housing. It follows the shell rather than introducing a circular
crown. The top-facing shoulder remains visible beyond the shallow dome from the
47 m camera; the roof centre stays empty. The dark lower lip and inner return give
the luminous band a restrained manufactured section. No bolts, repeated signs,
secondary neon stripes, cyan canopy, actual light nodes or animated signage.

The supervisor approved this **provisional section/envelope** before authoring:
wall offset -0.10 to +1.10 m, overall height 0.90 m at Y=6.75–7.65, hall-ground
identity pivot, one modest-emission material appearance and no collision. This is
not a measured world route or final lighting approval.

| Measurement | Godot-local metres |
| --- | --- |
| Ring visual AABB min | (-13.95, 6.75, -9.95) |
| Ring visual AABB max | (13.95, 7.65, 9.95) |
| Width / height / depth | 27.90 / 0.90 / 19.90 |
| Existing wall mounting contour | 25.70 × 17.70, corner radius 5.85 |
| Corner centres | (X,Z) = (±7, ±3); 16 segments per quarter arc |
| Inner contour at rear face | 25.50 × 17.50, corner radius 5.75 |
| Outer contour | 27.90 × 19.90, corner radius 6.95 |
| Section radial width | 1.20, including 0.10 penetration into wall |
| Outward projection beyond wall / ground shoe | 1.10 / 0.95 |
| Shared mounting centre datum | Y=7.20 |
| Permitted shell quiet mounting band | Y=6.33–7.92 |
| Root and mesh pivot | (0,0,0), **hall ground datum**, not ring underside |
| Envelope tolerance | ±0.001 |

The 15-point closed cross-section has a rounded outer shoulder and a flat broad
top. The magenta region runs from outer Y=7.04 around the shoulder to the top at
wall offset +0.10; dark inner and lower returns complete the same watertight solid.
There are no coplanar stacked faces or disconnected diffuser islands. The 0.10 m
back penetration is deliberate mounting overlap, not a hall cutout.

### Family interface and placement

Place this prefab at **the same transform as .01**, with no extra 7.2 m translation,
scale or rotation. Blender +Z up / +Y front maps once to Godot +Y up / -Z front.
Ground-centred construction preserves family alignment even though this component
has no ground contact. These are construction datums, not runtime sockets or APIs.

The canopy .03 remains separate at the shell's (0,3.6,-9) wall-contact datum. No
canopy model or placement is included. The ring is visual-only; the existing .01
solid body remains the sole family collision owner. Ring underside Y=6.75 avoids
inventing overhead snag collision, traversal, navigation, damage or interaction.
World integrators must still preserve the plaza, boundary streets and one side
passage, including this **larger decorative footprint**. No saved world placement,
road geometry, collision layer or existing scene was changed.

## Source, export, materials and prefab

- Source: `art/source/models/environment/d06_entertainment_hall_02/d06_entertainment_hall_02.blend`.
- Collection: `export_d06_entertainment_hall_02`.
- Root / mesh: `D06EntertainmentHall02` / `D06EntertainmentHall02_Mesh`.
- GLB: `art/models/environment/d06_entertainment_hall_02/d06_entertainment_hall_02.glb`.
- Prefab: `scenes/prefabs/environment/d06_entertainment_hall_02.tscn`.
- Scripts: `tools/asset_production/d06_entertainment_hall_02/`.

One editable connected mesh, applied identity transforms, metric units. Studio
camera/ground/lights stay outside the export collection. Authoring saves and exports
**before** read-only append of the existing .01 source for comparison renders. No
shell geometry is duplicated into this asset's saved source or GLB; render and
occlusion validation dependencies are recorded by the shell source SHA-256.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export uses
`tools/assets/blender/export_settings.json`, explicit collection filtering, Y-up,
no animations/skins/extras/cameras/lights/morphs. No rig, textures, embedded images,
external materials, sockets, variants or explicit LODs are required. Godot's default
automatic LOD/shadow-mesh import remains enabled; silhouette/performance acceptance
at LOD transitions remains downstream.

Opaque back-culled Principled materials, actual source/GLB/import order:

| Slot | Name | Base linear RGB | Metallic / roughness | Emission |
| --- | --- | --- | --- | --- |
| 0 | `ring_housing_petrol` | .035, .105, .125 | .25 / .43 | None |
| 1 | `ring_diffuser_magenta` | .64, .018, .23 | 0 / .38 | Same RGB × .45 |

GLB emissive factor is (.288, .0081, .1035), without HDR strength extension or light
nodes. The Godot imported emission colour is approximately (.5731,.08684,.3550),
the colour-space conversion of those factors. Emission is an appearance accent,
not a promise of actual surrounding illumination, bloom or calibrated signage.

The headlessly packed/resaved prefab retains the linked import at **Visuals/Model**,
identity transform, with no imported-child edits or embedded render meshes. Scene
UID `uid://bd644nkpj1nrc`, model UID `uid://0ogdhrk2phok`; importer sidecar and owned
check-script `.uid` retained. The `.tscn` stores its scene UID internally.

## Evidence and validation

[Hero installed on unchanged shell](d06_entertainment_hall_02-evidence/hero.png) ·
[Isolated oblique side](d06_entertainment_hall_02-evidence/side.png) ·
[Installed shoulder detail](d06_entertainment_hall_02-evidence/ring_detail.png) ·
[47 m / 42° overhead](d06_entertainment_hall_02-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU, 32 samples, AgX, 1280×800. The overhead
is vertical-down perspective at 47 m, **42° vertical FOV**, +Y/north at image top.
All four were visually inspected. The broad unbroken pink/magenta shoulder reads
around the dome, remains smooth at corners, and does not fill the quiet centre.
The isolated side view exposes the ring opening and dark return. A fifth scratch-only
unlit overhead comparison was rendered and inspected: with emission zero the hall
still reads by rounded plan/dome and the band by base colour, not bloom. The .01
record also retains its complete unadorned shell evidence. These are Blender studio
observations, **not** actual game lighting, city placement or target-device evidence.

[validation.json](d06_entertainment_hall_02-evidence/validation.json) records:

- **2,040 triangles**, **1,020 source vertices**, **1,156 GLB vertices** after surface
  splits; **one mesh, two surfaces**, one connected ring and one connected diffuser.
- **Zero degenerate source faces**, **zero nonmanifold edges**, **zero degenerate
  GLB triangles**. Positive signed volume/outward winding. Maximum unit-normal
  error 1.11e-7 source / 9.92e-8 export; finite source coordinates asserted.
- Source, actual GLB accessor values and Godot bounds match independent literal
  AABB expectations within 0.001 m; source and import root/mesh scales are unity.
- Eight camera primary rays aimed at independent straight-side/corner coordinates
  hit the diffuser before the actual unchanged shell. Centre ray misses the ring
  and hits the quiet roof. This is a bounded source-geometry visibility check,
  not population/occlusion acceptance for all camera offsets.
- Fresh export from reopened saved source is **byte-identical**, **42,020 bytes**,
  SHA-256 `e1c09dc3af99375356654bbe4deaa5b98b989db139bb702ece14b5b1798317f4`.
- Headless pinned Godot import; two normalized prefab saves byte-stable; fresh
  process loads all dependencies, resolves both UIDs, asserts imported material
  slots, emission, opaque back-culling, bounds and absence of collision/light nodes.
- Owned GDScript passes pinned gdstyle **0.3.0** lint/format and compilation.
  Production checks exit **1 only for existing unrelated failures**: five fixture
  compilation errors under `tests/fixtures/asset_production/`, formatting in
  `batch_observation.gd`, integration `batch03_author.gd` and `inspector.gd`.
  All **47** discovered scripts lint-clean; this asset compiles. Python **9/9**,
  GUT **9/9**, **70 assertions**, and negative-control detection pass.

### Diagnostics and limitations

Blender completed with 5.2 API deprecation notices only. Godot import reports the
existing MCP plugin 4.8 compatibility warning. No live Blender/Godot session was
used; only timeout-bounded isolated CLI processes. Existing project plugin startup
was left unchanged; no global settings or vendor changes.

The initial editor normalization produced no receipt, with static-string/thread
shutdown errors; its exit status was not separately captured by that first shell
batch and is not claimed successful. The resource-only script was simplified to
remove unnecessary physics waits and a filesystem-signal wait after completed import.
The revised normalization exits 0 and proves UID/two-save stability, but still emits
editor shutdown RID/ObjectDB leak diagnostics, as the preceding .01 did. Root cause
is **not** claimed fixed. A fresh non-editor load exits 0 without ERROR/WARNING.
No unchanged failing normalization or whole-suite invocation was repeated.

[final.log](d06_entertainment_hall_02-evidence/final.log) retains a concise receipt,
including final diagnostic lines. [manifest.json](d06_entertainment_hall_02-evidence/manifest.json)
hashes every produced payload except itself. Raw logs and the additional unlit
render remain outside the checkout under `C:/tmp/ft/assets/d06_entertainment_hall_02/`.

## Exact reproduction

Run from the worktree in Bash. `mise` supplies the pinned engine/gdstyle. The
production-check directory must be fresh; no live/windowed editor is launched.

```sh
NID=d06_entertainment_hall_02
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py" > "$T/author.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py" > "$T/validate-final.log" 2>&1

timeout 300 "$G" --headless --editor --path . --import --quit > "$T/import.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/normalize-final.log" 2>&1
timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh.json" > "$T/prefab-fresh.log" 2>&1

timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python "tools/asset_production/$NID/record.py"
```

`author.py` reconstructs the editable ring and four final renders plus the scratch
unlit comparison. `validate.py` reopens the saved source, reads GLB triangle/normal
accessors, independently tests topology/bounds/visibility and reexports to scratch.
`export.py` also runs independently with the same Blender flags and optional output
directory after `--`. The exporter reopens source when its collection is absent.
`check_prefab.gd` validates production resource APIs, not generated test geometry.
`record.py` consolidates existing receipts and hashes payloads; it does not substitute
for running validation. Read-only .01 source is required for assembled evidence.

## Remaining handoffs

1. Independent art/technical review of the exact committed candidate.
2. .03 canopy production and combined-family check, with no change to this datum.
3. World placement/overhang review preserving plaza and passages; actual player/car
   movement and sightline checks with the shell's authoritative collision owner.
4. Actual Godot camera/lighting/bloom calibration, off-centre occlusion, LOD review,
   packaged dependencies and repeated-instance/Deck sustained performance.
5. Editor-mode CLI shutdown diagnostic investigation remains integration/tooling work.

No queue, shared brief, progress, catalogue, world scene, prototype or global project
file changed. Full gameplay/placement/performance readiness is not asserted.
