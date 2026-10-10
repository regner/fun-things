# d09_warehouses.02 — Wide low warehouse

**Production source, export, linked prefab and bounded checks delivered; independent
review and world/gameplay/device acceptance pending.** Commissioned by Regner under
[the commission](commission.md) and the current asset-common lane brief, superseding
the older concept-only restriction. Producer: commissioned isolated asset-production
worker on `lane/a-whouse`. Accepting owners: independent technical/art reviewers and
world/gameplay owners; this handoff does not mark those gates accepted.

Original Blender construction; no downloaded meshes, image-to-mesh, real brands,
external textures or runtime geometry. References: [family brief](../d09_warehouses.md),
[East Docks](../../concepts/districts-v1/east-docks.md), the approved
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
and the [long ridge sibling](d09_warehouses_01.md). Its source recipe, prefab and
renders were read before authoring this member. No sibling output was modified.

## Design and dimensions

A six-bay warehouse with a broad shallow blue mono-pitch, two long opaque rooflight
ribbons, four closed industrial shutters, two quiet service bays, a personnel door,
small high end vents, continuous gutters/edge flashings and sparse amber loading
headers. The wider depth and **7.21 m maximum height** distinguish this member from
`.01`'s narrow **9.265 m** ridge silhouette without introducing a competing family.
The broad steel fields, large shutter folds and 6 m rhythm stay consistent. No indoor
freight handling, opening doors, loading decks, dense roof clutter, cranes, graphics,
real light nodes or new interactions are included.

Dimensions below are **provisional authored values**, not measurements from a
concept image or approved district placements. The 864 m² ground footprint equals
`.01`'s area with different proportions: 36×24 rather than 48×18 m. Neither consumes
a specific allocation of East Docks' 5.03 ha. World placement must preserve generous
aprons, freight turns, normal footways and the existing service spur.

| Contract | Metres, Godot local coordinates |
| --- | --- |
| Whole visual size X / Y / Z | **36.760 / 7.210 / 24.980** |
| Visual AABB minimum | **(-18.380, 0, -12.490)** |
| Visual AABB maximum | **(18.380, 7.210, 12.490)** |
| Ground shoe / solid collision footprint | 36.000 × 24.000 |
| Ground shoe height | 0.360 |
| Front nominal wall eave | 6.400 |
| Main roof front / rear top | 6.580 / 7.100 |
| Highest edge flashing | 7.210 |
| Shallow roof fall, rear to loading front | 0.520 over 24.800 (~1.20°) |
| Bay pitch along X | 6.000; six centres -15 through +15 |
| Closed loading-door centres X | -15, -9, -3, +3 |
| Loading shutter face | 3.600 wide × 4.200 high, bottom Y=0.300 |
| Nominal front / rear bearing datum | Z=-12.000 / +12.000 |
| Ordinary steel wall face | Z=±11.860 |
| Decorative roof overhang beyond ground shoe | 0.380 at ends; 0.490 at front/rear |
| Envelope / ground datum validation tolerance | ±0.001 |

Ground-centred root and mesh pivots at (0,0,0). Blender +Y loading front maps once to
Godot -Z; Blender +Z maps to Godot +Y. Metres, applied rotation/scale, no corrective
wrapper transforms. The roof falls towards the loading front; no roof traversal is
provided.

### Family and annex seam

Retains `.01`'s **6 m bay pitch, 3.6×4.2 m closed shutters, seven material names and
identical PBR values**. Shutters, thresholds, personnel door, gutters and ordinary
fittings belong to this building kit, not separate freight-graphics hardware. Each
warehouse is one reusable assembly, not a bespoke mesh per plot or runtime generator.
The authoring recipe follows the first member's construction conventions and uses
the shared export contract; no shared tooling or sibling script was changed.

The rear central two bays, **X=-6 to +6**, are blank except for the regular wall piers.
Rear ground bearing datum **(0,0,+12)**, outward +Z, up +Y; actual steel face Z=11.86.
This gives the same **0.14 m datum-to-steel return allowance** as `.01` at Z=+9.
Keep an annex's upper attachment **below Y=5.8**, below all eave fittings. This is a
closed exterior butt attachment, not a through opening. The future annex and world
integrator own its dimensions and saved placement; no dynamic socket/API is added.

## Source, exports and materials

- Source: `art/source/models/environment/d09_warehouses_02/d09_warehouses_02.blend`.
- Collection: `export_d09_warehouses_02`.
- Root / mesh: `D09Warehouses02` / `D09Warehouses02_Mesh`.
- Export: `art/models/environment/d09_warehouses_02/d09_warehouses_02.glb` and `.import`.
- Linked prefab: `scenes/prefabs/environment/d09_warehouses_02.tscn`.
- Author/export/validation/check/receipt scripts: `tools/asset_production/d09_warehouses_02/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. The exporter
loads `tools/assets/blender/export_settings.json`, filters the declared collection,
and disables animations and skins. Cameras, studio floor and lighting stay outside
export. Static bevels and weighted normals are applied before source save. Editable
geometry remains in the `.blend`; `author.py` retains the parametric recipe. Closed
subparts intentionally intersect at fitting/wall and roof joints; none has an open
boundary. No textures, embedded images, rigs, clips, sockets or destruction states.

One mesh, seven opaque back-culled Principled surfaces in exported slot order:

1. `dock_base_slate` — continuous ground shoe and flush thresholds.
2. `dock_wall_steel` — broad steel wall fields.
3. `dock_roof_blue` — shallow roof and sparse bay seams.
4. `dock_frame_navy` — flashings, gutters, frame recesses and shutter folds.
5. `dock_glazing_opaque` — rooflight ribbons and service clerestories.
6. `dock_shutter_teal` — closed loading/personnel doors.
7. `dock_loading_amber` — sparse headers and jamb accents, not emission.

Exact linear colors, metallic and roughness values are in validation.json. No
material overrides, transparent glazing or real lighting. Godot automatic mesh LOD
and shadow-mesh generation remain enabled; transition appearance and repeated cost
remain unaccepted. No numerical production triangle budget was supplied.

## Prefab and collision

`Visuals/Model` is the identity-transform linked GLB, with no embedded replacement
geometry. `Collision/Body/Shell` is one BoxShape3D directly under StaticBody3D,
size **(36,6.4,24)**, centre **(0,3.2,0)**, static-world layer **1**, mask **0**.
The continuous ground shoe is the exact collision footprint. The slightly inset
wall fields and flush loading lips do not create additional snag colliders or
walkable platforms. Roof, high flashings and the small upper rear wall area above
the 6.4 m solid envelope are visual-only. No interiors or rooftop gameplay.

Godot-generated prefab UID **`uid://d13riaqlafut3`**, imported model UID
**`uid://cj3imw3tbn7ut`**. Scene UID, named node identities and linked ancestry
survived **two byte-stable save/reload roundtrips**. This task used text authoring
followed by pinned headless ResourceSaver/PackedScene normalization, as required by
the brief: the windowed editor is unavailable and the owner's live sessions are
excluded. No live-editor synchronization or windowed playtest is claimed.

## Evidence and validation

[Hero](d09_warehouses_02-evidence/hero.png) ·
[loading elevation](d09_warehouses_02-evidence/side.png) ·
[loading detail](d09_warehouses_02-evidence/loading_detail.png) ·
[47 m / 42° overhead](d09_warehouses_02-evidence/overhead_47m_42deg.png).

Isolated **Blender Cycles CPU, 32 samples, AgX** renders, not Godot captures.
Hero/side/detail are 1152×648. Overhead is **1280×720**, vertical-down perspective,
47 m height, 42° **vertical** FOV, Blender +Y at image top. The current lean-evidence
720-pixel maximum supersedes the old 800-pixel requirement. Maximum PNG compression;
evidence-only six-bit/channel hero and seven-bit/channel other views keep all four
below 400 KB. Runtime materials and GLB are not color-reduced.

Producer inspected all four views and the sibling hero. The lower rectangular roof
and two long ribbons read distinctly from `.01`'s pitched ridge and paired short
rooflights. Broad quiet blue fields dominate; amber remains limited to the loading
face. The large roof fills much of the gameplay frame; actual route-side occlusion
and repeat placements need in-engine review. Studio lighting is not a new world
lighting choice. The lean hero has minor background gradient quantization only.

Measured source, actual GLB accessors and imported prefab:

- **10,944 source vertices; 21,432 triangles**.
- **13,095 exported vertices** including material/normal splits.
- **1 mesh; 7 surfaces**.
- **0 degenerate source faces, 0 degenerate GLB triangles, 0 non-manifold edges**.
- Maximum normal-length error: source **1.72e-7**, GLB **1.22e-7** (rounded up).
- All AABBs match the literal expected envelope within 0.001 m; ground datum zero.
- Fresh saved-source reexport **byte-identical**, GLB **554,556 bytes**, SHA-256
  `0cf3e3e48b154bb97af09f6c42b1014d1b00b610b2b94250ce146adedb5b510c`.
- **Eight physics shape queries** pass: interior, closed front, rear attachment wall,
  end wall, clear front apron and side passages, visual-only upper roof.
- **Six motion casts** pass: actor capsule **r=0.35 / h=1.8** blocked at front/rear/end,
  side bypass clear; car-sized box **1.8×1.5×4.4** blocked at front, side bypass clear.
- Front ray hits saved body at **(-9,1,-12)**. Dependencies, material opacity/culling,
  linked identity transform, collider dimensions and two save/reload rounds pass.

Casts use public PhysicsDirectSpaceState3D APIs against the actual saved prefab.
They do not prove production ActorMotion or car-controller movement, turning,
network admission, transport or prediction. The fresh headless process exits 0
without ERROR/WARNING diagnostics. No real-process multiplayer acceptance is claimed.

Canonical production checks **pass all layers**: pinned engine, owned script
compilation/style/formatting, **17 Python tests**, **149 GUT tests / 6,768 assertions**,
and expected rejection of the intentional GUT negative control. No known-failure
exemption was needed. [validation.json](d09_warehouses_02-evidence/validation.json),
[final.log](d09_warehouses_02-evidence/final.log) and the SHA-256
[manifest](d09_warehouses_02-evidence/manifest.json) retain lean receipts.

Diagnostics: the Blender version-only query printed a 23-byte shutdown allocation
warning; actual authoring/validation exited 0 without it. Authoring emitted the
pinned Blender's forward-looking `use_nodes` deprecations. Headless editor import
emits only the existing toolkit Godot-4.8 compatibility warning. Runtime prefab
checks and canonical checks are clean. Raw logs and scratch reexports remain
outside the repository.

## Exact reproduction

Run from repository root in Git Bash. Keep Blender timeout, audio environment,
factory-startup, four-thread and error-exit flags. `record.py` uses Pillow. The
canonical checker requires a fresh empty output directory.

```sh
NID=d09_warehouses_02
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
OUT="C:/tmp/ft/assets/$NID"
mkdir -p "$OUT"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/author.py
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/validate.py
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd -- --normalize --output "$OUT/prefab-check.json"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd -- --output "$OUT/prefab-fresh-final.json"
timeout 1800 mise exec -- python tools/production_checks.py --output "$OUT/checks"
python tools/asset_production/$NID/record.py --compress-renders
```

The validator freshly opens the saved source and reexports to `$OUT/reexport`.
A standalone reexport can instead be run with:

```sh
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 art/source/models/environment/$NID/$NID.blend --python tools/asset_production/$NID/export.py -- "$OUT/reexport"
```

## Remaining acceptance

Independent technical/art review; final district dimensions and annex fit; saved
world placement/apron turning; actual engine camera occlusion/material/LOD views;
production actor/car movement and queries; relevant multiplayer collision behavior;
exported platforms and sustained Deck/performance checks remain **pending**. No
shared brief/register/progress file, road generation, district boundary, world
placement, gameplay implementation or sibling asset was changed. Scene UIDs live
in the `.tscn` header; the engine-created script `.gd.uid` and model `.import` are
included. The manifest excludes only itself to avoid a self-referential hash.
