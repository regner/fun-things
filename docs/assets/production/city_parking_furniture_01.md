# city_parking_furniture.01 — Wheel stop

10 October 2026. **Source/export, linked prefab and bounded headless checks delivered;
independent review and world/gameplay acceptance pending.** Produced by the commissioned
implementation specialist on `lane/a-parking`. [Commission](commission.md) and the current
asset-production common brief supersede the earlier concept-only restriction in the
[family brief](../city_parking_furniture.md). No other family member existed in this lane
at authoring time. No queue, shared progress, world scene or gameplay rule was changed.

## Design and dimensions

An original low molded wheel stop: a broad trapezoidal petrol body, rounded 8 mm edges,
flat ground contact and two flush amber bands crossing the top and both tire-facing
shoulders. No real brand, text, grime, floating trim or bolt-scale visual noise.
The quiet low form supports Broadlot's sparse parking rows and open turning areas;
Ironreach/East Docks and other supporting placements remain unconfirmed. The visual
language follows [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and the [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), not guessed
measurements from concept images. Colors follow the accepted petrol/amber infrastructure
palette, with higher roughness than metal barriers to suggest molded rubber.

**Dimensions are provisional authoring choices**, permitted by the standing production
brief, not ratified parking geometry or vehicle-clearance dimensions:

- Godot width X / height Y / depth Z: **1.800 × 0.160 × 0.300 m**.
- AABB: **(-0.900, 0, -0.150) → (0.900, 0.160, 0.150) m**.
- Top nominal depth 0.170 m before the bevel; low skirt 0.025 m tall.
- Two 0.300 m-wide amber bands, X ranges [-0.720, -0.420] and [0.420, 0.720] m.
  Bands are surface assignments in the continuous closed body, not overlaid geometry.
- Root and mesh pivots: (0,0,0), centered on the ground footprint. Metres, unit scale,
  zero object rotation/translation, no unapplied modifiers. Width runs along X;
  Blender +Z/+Y maps once to Godot +Y/-Z. Both long faces are equivalent.
- Envelope/ground tolerance: ±0.001 m; exported/source axis-bound comparison: 0.00001 m.

No new parking spacing, bay width, car stopping distance, bus operation, interaction,
state, destruction, rig, clips or sockets. Placement must preserve walking bypasses
and turning areas; this asset is not a full-width traffic barrier or a speed hump.

## Source, export and materials

Original Blender construction, with no downloaded/generated mesh service, texture or
third-party artwork. The parametric author script builds a closed six-sided section
along explicit stations, assigns the flush bands and applies bevel/weighted normals.

- Source: `art/source/models/environment/city_parking_furniture_01/city_parking_furniture_01.blend`.
- Collection: `export_city_parking_furniture_01`; root: `CityParkingFurniture01`;
  mesh: `CityParkingFurniture01_Mesh`. Studio floor/camera/lights are excluded.
- Export: `art/models/environment/city_parking_furniture_01/city_parking_furniture_01.glb`
  and its pinned-engine `.glb.import` sidecar.
- Author/export/validation/engine-check/evidence scripts:
  `tools/asset_production/city_parking_furniture_01/`.
- One static mesh, two opaque back-culled Principled surfaces, no textures or images:

| Slot | Material | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `parking_rubber_petrol` | (0.025, 0.075, 0.090) | 0 / 0.78 |
| 1 | `parking_safety_amber` | (1.000, 0.527, 0.102) | 0 / 0.58 |

No emission, external materials, UV-dependent shading or embedded textures. No explicit
LOD is warranted for this small mesh; Godot's default automatic LOD/shadow-mesh import
settings remain enabled and repeat-placement performance stays unmeasured.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. The export script
loads `tools/assets/blender/export_settings.json`, filters the named collection and
turns off animations/skins. No cameras, lights, studio geometry or corrective transforms
export. The validation/check structure follows the existing light/barrier production
conventions; no shared tooling or unrelated asset is modified.

## Prefab and collision

`scenes/prefabs/environment/city_parking_furniture_01.tscn` links the imported GLB at
**`Visuals/Model` with identity transform**. Imported children remain noneditable;
no embedded replacement mesh or runtime-authored visual hierarchy exists.

Separate `Collision/WheelStopBody/Shape` supplies **one 1.800 × 0.160 × 0.300 m box**,
center (0,0.080,0), on static-world layer 1 / mask 0. This intentionally conservative
simple envelope covers the sloped shoulders and soft edges without decorative snag
geometry. It does not reproduce the slope as a driveable ramp. The standing brief
requires a collider for ground props; no new vehicle response is invented here.

Editor tools were deliberately unavailable under the isolated-CLI brief. The wrapper
was authored as text, loaded/packed/resaved by pinned headless Godot and then reloaded
and resaved again with identical bytes. Dependency UIDs and saved node identities were
verified; source import and scene UIDs are retained. No live editor was accessed, and
these checks do not assert synchronization of any separately open editor scene.

## Evidence and validation

[Hero](city_parking_furniture_01-evidence/hero.png),
[end/side](city_parking_furniture_01-evidence/side.png),
[band and edge detail](city_parking_furniture_01-evidence/detail.png),
[47 m / 42° overhead](city_parking_furniture_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders, 1280×720, AgX, 32 samples, broad studio
fill. The overhead is vertical-down perspective with 42° vertical FOV and Blender +Y
at image top. It is not cropped/enlarged. The current common-brief 720-pixel height cap
supersedes the older 800-pixel evidence reference. Final evidence uses seven significant
RGB bits and maximum PNG compression to keep each image below roughly 400 KB.

Producer inspection: the low trapezoid and two broad bands read cleanly in close views;
the overhead retains a quiet roughly 36×6-pixel bar with two separated warm ticks.
This is an appropriate small parking prop, not a landmark or essential wayfinding.
No extra detail or scale inflation was added just for the gameplay camera. Actual
engine lighting, moving-camera readability and crowded-parking views remain pending.

[validation.json](city_parking_furniture_01-evidence/validation.json) records:

- **240 Blender vertices; 242 source faces; 476 triangles; 292 exported vertices**.
- **One mesh / two surfaces; zero degenerate faces or triangles; zero non-manifold edges**.
- Positive closed volume 0.07044479 m³; unit-length source and GLB normals, maximum
  length error <0.00000012. All source/export bounds meet the declared tolerances.
- Fresh re-export from the saved source is **byte-identical** to the 11,820-byte GLB;
  SHA-256 `ae2a0e968c2f0d6747f89517a99322333bfcd3ca78cbca6a3f5e99e543618196`.
- Headless Godot **4.8.dev7.official.c971f93e7** proves linked model ancestry,
  identity transform, actual imported AABB/surface/culling checks, recursive dependency
  resolution, simple collider structure and byte-stable scene save/reload.
- Physics queries hit the stop at Z=-0.150 m with a Y=0.080 m ray; a Y=0.200 m ray is
  clear. A production-sized capsule (radius 0.35 m, height 1.8 m) overlaps the solid
  stop at the center, clears the end at X=1.3 m and clears above it with bottom Y=0.2 m.
  These are bounded envelope/query tests, **not actor movement or vehicle braking tests**.
- Full `tools/production_checks.py`: **PASS**, including all owned script lint/explicit
  compilation, **17 Python tests**, **149 GUT tests / 6,768 assertions**, and the
  intentional GUT-failure detection. No known-failure exception was needed.
- Initial import logged only the existing MCP plugin's Godot-4.8/latest-tested-4.7
  warning. Owned author, validator and engine-check logs contain no errors. The Blender
  `--version` probe alone emitted a 23-byte shutdown allocation diagnostic; authoring
  and validation exited cleanly. No live MCP tools were invoked.

[manifest.json](city_parking_furniture_01-evidence/manifest.json) records SHA-256 for every
produced payload, excluding only itself. Scratch render/export/process logs and full
production-check output remain outside the repository at
`C:/tmp/ft/assets/city_parking_furniture_01/`.

## Exact reproduction

From the worktree root in Bash, with the pinned tools installed. Production-check output
must be fresh/empty; retain or move an old scratch run before reusing that path.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
NID=city_parking_furniture_01
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/$NID/author.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/$NID/validate.py
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/$NID/check.gd -- --normalize
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/$NID/checks
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/$NID/check.gd
python tools/asset_production/$NID/record.py
```

`validate.py` opens the saved `.blend`, reexports into the external scratch `reexport/`
directory and compares actual bytes. To export separately, use the same Blender flags
with `--background art/source/models/environment/$NID/$NID.blend`,
`--python tools/asset_production/$NID/export.py -- C:/tmp/ft/assets/$NID/manual-reexport`.
`record.py` requires Pillow, compacts the four renders and refreshes validation/manifest.

## Remaining acceptance

Independent technical/art review is required. Layout owners retain parking placement,
clear aisles and bypasses. Gameplay owners must check real actor approach/contact and
car wheels/underbody/braking against this low conservative box before world placement;
no promise is made that a low prop stops every capsule or vehicle. Real-process network
collision/prediction behavior, engine gameplay-camera visuals, packaged builds, sustained
repeat-placement profiling and Deck LCD/OLED evidence remain pending. No register READY
status, world placement, interaction feature or completed gameplay gate is claimed.
