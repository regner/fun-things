# city_parking_furniture.03 — Cycle stand

10 October 2026. **Source/export, linked prefab and bounded headless checks delivered;
independent review and world/gameplay acceptance pending.** Produced by the commissioned
implementation specialist on `lane/a-parking`. [Commission](commission.md) and the current
asset-production common brief supersede the historical concept-only restriction in the
[family brief](../city_parking_furniture.md). The [wheel stop](city_parking_furniture_01.md)
sets the family's quiet petrol and paired amber-band language. Member .02 had no source,
prefab or document in this checkout at authoring; the stand has no dependency on it.
No shared brief, register, progress, world scene or gameplay rule was changed.

## Design and dimensions

An original, single inverted-U cycle hoop: one continuous round tube with tangent rounded
shoulders, two low softened mounting shoes and two flush amber bands on the horizontal
rail. No brands, text, textures, bolt-scale clutter, bicycle model or bicycle interaction.
Petrol coated metal follows the accepted lights; amber matches the wheel stop exactly.
The low quiet form supports Northpoint's sparse cycle stands and potential Terrace Ward,
Glassward or Signal Row placements. Supporting uses remain unconfirmed; this is not an
assembly of placed stands or a parking-layout prescription.

References: [district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) and
[shared concept contract](../../concepts/districts-v1/brief-contract.md). Dimensions below
are **provisional authoring choices**, permitted by the standing production brief, not
measurements inferred from concept images or approved street clearances.

- Godot width X / height Y / depth Z: **1.040 × 0.900 × 0.180 m**.
- Visual AABB: **(-0.520, 0, -0.090) → (0.520, 0.900, 0.090) m**.
- Hoop tube: 0.080 m diameter; leg centers X=±0.440 m. Shoulder centerline radius
  0.140 m; top centerline Y=0.860 m. Tube-only outer width 0.960 m.
- Ground shoes: each 0.160 × 0.025 × 0.180 m, centers X=±0.440 m, Y=0.0125 m;
  0.009 m edge bevel. Tube ends penetrate the shoes by 0.005 m to avoid a visible gap.
- Two 0.100 m-wide amber bands, X ranges [-0.220, -0.120] and [0.120, 0.220] m.
  Bands are material assignments on the continuous tube, not overlaid meshes.
- Ground-centered root and mesh pivot (0,0,0); metre units, identity object transforms,
  applied static modifiers. Width runs along X; Blender +Z/+Y maps once to Godot +Y/-Z.
  Front and back are equivalent. No corrective prefab rotation or scale.
- Envelope/ground tolerance ±0.001 m; source/export bound comparison 0.00001 m.

No new bay spacing, parking capacity, bus operation, attachment sockets, rig, clips,
destruction, movable state or interaction. Layout owners must preserve walking bypasses,
turning space and passage mouths; no interiors or under-hoop traversal is commissioned.

## Source, export and materials

Original Blender construction; no downloaded meshes, generated mesh service, external
artwork or third-party model. `author.py` sweeps a capped 16-sided tube through two
8-segment quarter-circle bends, assigns flush bands and adds two beveled mounting shoes.
The joined mesh has three closed islands. Shoe/tube overlap is deliberate concealed
assembly, not a Boolean union; the validator's signed volume is the sum of those islands.

- Source: `art/source/models/environment/city_parking_furniture_03/city_parking_furniture_03.blend`.
- Collection: `export_city_parking_furniture_03`; root `CityParkingFurniture03`,
  mesh `CityParkingFurniture03_Mesh`. Studio floor/camera/lights are outside the collection.
- Export: `art/models/environment/city_parking_furniture_03/city_parking_furniture_03.glb`
  plus the pinned engine's `.glb.import` sidecar.
- Reproduction/check scripts: `tools/asset_production/city_parking_furniture_03/`.
- One mesh, two opaque back-culled Principled surfaces:

| Slot | Material | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `parking_metal_petrol` | (0.025, 0.075, 0.090) | 0.45 / 0.46 |
| 1 | `parking_safety_amber` | (1.000, 0.527, 0.102) | 0 / 0.58 |

No emission, external materials, embedded images, textures or UV-dependent shading.
Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export loads the
shared `tools/assets/blender/export_settings.json`, selects the named collection and
disables skins/animation. No prototype dependency or studio geometry is exported.
Godot's default automatic LOD/shadow-mesh import remains enabled. No explicit LOD or
unmeasured optimization is added; repeated-placement performance is pending.

Shared export settings and `tools/production_checks.py` are reused unchanged. The owned
source/export and prefab checks follow the wheel-stop conventions with stand-specific
bounds and expectations. No general shared source validator/prefab-normalizer API is
provided by the repository; no new shared framework or sibling mutation was introduced.

## Prefab and collision

`scenes/prefabs/environment/city_parking_furniture_03.tscn` links the GLB at
**`Visuals/Model`, identity transform**, with noneditable imported children. No embedded
replacement render mesh or runtime-authored visual hierarchy.

Separate `Collision/CycleStandBody/Shape` is **one 1.040 × 0.900 × 0.180 m static box**,
center (0,0.450,0), layer 1 / mask 0, matching the whole visual envelope. The simple
collider intentionally fills the opening under the rail: it is too low for the 1.8 m
standing actor, and no crouch/under-hoop route is specified. It also conservatively covers
the small space beside the tube up to the shoes' depth. This means low rays hit the
filled envelope, not just visible tube geometry; gameplay owners must review query and
vehicle implications before placement. The fixture is not visual-only or a walkable ramp.

Live Blender/Godot editor sessions were not accessed. Under the isolated-CLI brief the
wrapper was authored as text, loaded/packed/resaved by pinned headless Godot, then loaded
and resaved again with byte-identical output. Embedded scene UID, dependency UID and saved
node identities resolve. The engine generated the script `.uid`; `.tscn` identity is in
its header, not a fabricated sidecar. Headless checks do not synchronize any open editor.

## Evidence and validation

[Hero](city_parking_furniture_03-evidence/hero.png),
[side elevation](city_parking_furniture_03-evidence/side.png),
[shoulder and band detail](city_parking_furniture_03-evidence/detail.png),
[47 m / 42° overhead](city_parking_furniture_03-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders, AgX, 32 samples, 1280×720, broad studio
fill. PNGs retain seven significant RGB bits and compression level 9. The current
720-pixel evidence-height cap supersedes the older 1280×800 reference.

Producer inspected all four: the close silhouette is a clean low cycle hoop with
continuous highlights, grounded shoes and restrained paired bands. The actual uncropped
47 m, 42° vertical-FOV, vertical-down view retains a small roughly 21×4-pixel bar with
two warm ticks. The upright opening naturally collapses in that view; the stand is quiet
street dressing, not an overhead landmark. No extra geometry or scale inflation was
added to force recognition. Actual engine lighting/moving-camera/group readability is
still pending. These Blender images are not Godot captures or collision evidence.

[validation.json](city_parking_furniture_03-evidence/validation.json) records:

- **576 Blender vertices, 566 source faces, 1,140 triangles, 712 exported vertices**.
- **One mesh / two surfaces; zero degenerate faces/triangles; zero non-manifold edges**.
- Sum of closed-island signed volumes 0.0133206373 m³. Unit-length source and GLB normals;
  maximum length errors <0.00000015. Measured source/export bounds meet the tolerances.
- Fresh export of the saved source is **byte-identical** to the 31,884-byte production GLB;
  SHA-256 `33406b69837c255034d36d4102a8c703214d59b97745aaaec446bed4d9ef700d`.
- Godot **4.8.dev7.official.c971f93e7** proves actual imported AABB, surface count,
  opaque/back-culled materials, linked ancestry, dependency resolution, identity model
  transform, separate single collider and byte-stable scene save/reload.
- Physics ray at Y=0.450 m hits the conservative box at Z=-0.090 m. Ray at Y=1.000 m
  clears above it. A radius-0.350 m / height-1.800 m capsule overlaps the center,
  clears the end at X=0.950 m and clears above with capsule bottom Y=1.000 m.
  These are direct-space envelope queries, **not actual actor movement or car handling**.
- Full `tools/production_checks.py`: **PASS**. Owned GDScript lint/format and explicit
  compilation pass; **17 Python tests**, **149 GUT tests / 6,768 assertions** pass,
  including the intentional GUT-failure detection. No pre-existing-failure waiver used.
- Import logs contain only the existing MCP plugin's Godot-4.8/latest-tested-4.7 warning.
  No live MCP tool was called. Blender's `--version` probe emitted the known 23-byte
  shutdown allocation diagnostic; authoring/validation exited cleanly. Authoring logged
  future Blender-6 `use_nodes` deprecation warnings, not current-pin failures.

[manifest.json](city_parking_furniture_03-evidence/manifest.json) lists SHA-256 for every
produced payload, excluding itself. Full scratch logs/check outputs and fresh comparison
exports are outside the repository at `C:/tmp/ft/assets/city_parking_furniture_03/`.
Only the four renders, validation and producer manifest are retained as evidence.

## Exact reproduction

Run from this worktree in Bash. Production-check output must be fresh/empty; move an old
scratch result aside before repeating the full command sequence.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
NID=city_parking_furniture_03
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

`validate.py` opens the saved source, reexports into external scratch `reexport/` and
compares actual bytes. For manual reexport, use the same Blender flags with
`--background art/source/models/environment/$NID/$NID.blend`,
`--python tools/asset_production/$NID/export.py -- C:/tmp/ft/assets/$NID/manual-reexport`.
`record.py` requires Pillow, compacts the renders and refreshes the validation/manifest.

## Remaining acceptance

Independent technical/art review is required. World layout owns sparse grouping,
placement, clear aisles, passages and walking bypasses. Gameplay owners must test actual
actor approach/contact, aim queries and vehicle contact against this conservative filled
box before placement. Real-process multiplayer/prediction behavior, engine gameplay-camera
views, packaged builds, sustained repeat-placement profiling and Deck LCD/OLED evidence
remain pending. No register READY status, world placement, bicycle system or completed
gameplay/performance gate is claimed.
