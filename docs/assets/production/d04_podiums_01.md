# d04_podiums.01 — Low office block

10 October 2026. **Source/export, linked prefab and bounded headless checks delivered;
independent review, placement and gameplay/device acceptance pending.** Commissioned by
Regner through the asset-production task. Producer: isolated asset-production worker;
accepting owners: supervising art/technical reviewers and downstream layout/gameplay owners.
The production commission supersedes the family brief's historical concept-only restriction.

References: [commission](commission.md), [podium/office family](../d04_podiums.md),
[Glassward concept](../../concepts/districts-v1/glassward.md),
[asset breakdown](../../concepts/districts-v1/glassward-assets.md),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md),
[gridded streets](../../concepts/world-v1/stage-04-streets/README.md), and
[existing tower vocabulary](d04_towers_01.md).

## Design and dimensions

An original three-storey office with a slate body, broad opaque blue glazing, a tall
recessed entrance, quiet indigo roof and one small magenta entrance lintel. The full-height
entry notch breaks the otherwise rectangular roof and identifies the entrance axis without
competing with the towers' cyan crowns. Soft bevels and weighted normals retain ordinary,
smooth stylized architecture. There are no roof props, sign hardware, real brands or copy.

All dimensions are **provisional authored proposals**, permitted by the standing production
brief, not inferred measurements from concept images or accepted parcel allocations.
Godot dimensions are X width / Y height / Z depth; envelope tolerance is ±0.001 m.

| Contract | Provisional value |
| --- | --- |
| Nominal footprint | 26 × 16 m; 416 m² bounding rectangle |
| Entry recess | 5 m wide × 1.5 m deep; full-height roof notch |
| Solid footprint | 408.5 m², excluding the 7.5 m² recessed entry |
| Lobby / upper floors | 6 m lobby, two upper floors at 3.6 m pitch |
| Roof / parapet | Roof datum 13.2 m, parapet top 14.1 m |
| Whole visual AABB | min (-13, 0, -8), max (13, 14.1, 8) m |
| Whole visual size | **26 × 14.1 × 16 m** |
| Entry closed-door plane | Approximately Z=-6.5 m, behind facade Z=-8 m |
| Entry canopy | 5 × 1.45 m plan, contained within the recess; lowest soffit Y=3.54 m |
| Pivot and front | (0,0,0), nominal ground-centred footprint; front Godot -Z / Blender +Y |

The body sits slightly behind its footing/trim envelope (up to 0.05 m) to make layered
facade faces visible without coplanar surfaces. Door pulls project 0.13 m ahead of the solid
entry datum and are decorative, not separate snag colliders. The canopy remains above the
1.8 m actor and does not project outside the footprint. There are no steps, raised forecourt,
paving, interior route or rooftop gameplay. Ground in the entry is supplied by placement.

### Family handoff

This is the first podium/office delivery in this lane. It adopts the existing tower family's
6 m lobby, 3.6 m upper-floor pitch, opaque blue glazing, grey-blue framing, pale stone and
small magenta entry accent. `glassward_office_slate` supplies a lighter, quieter low-building
body; crowns remain the tall family's strong cyan cue. Source `structure()`, `windows()` and
`entrance_and_roof()` are the editable construction recipe. These are design datums, not an
attachment API or a promise that a tower can be mounted on this roof.

The standalone low office is not a sealed superblock podium or skybridge. Its small notched
footprint adds no lot-wide platform. Layout must still leave grid corners, walking gaps and
forecourts open; no asset-only check can establish that district composition. No sibling
source, shared family brief, registry, progress file or saved world placement was changed.

## Source, export and materials

- Source: `art/source/models/environment/d04_podiums_01/d04_podiums_01.blend`.
- Collection: `export_d04_podiums_01`; root `D04Podiums01`; mesh `D04Podiums01_Mesh`.
- Explicit export: `art/models/environment/d04_podiums_01/d04_podiums_01.glb` and its
  pinned-engine `.import` sidecar.
- Prefab: `scenes/prefabs/environment/d04_podiums_01.tscn`.
- Tools: `tools/asset_production/d04_podiums_01/{author,export,validate,record}.py`,
  `check_prefab.gd` and its generated `.uid`.

Original Blender construction only; no downloads, purchased/generated mesh assets,
image-to-mesh, external textures, fonts or prototype dependencies. Reproducible authoring
creates closed architectural parts, applies bevels and weighted normals, then joins them
into one ground-origin mesh. Closed overlapping parts are intentional; this is not a Boolean
union or a watertight single building volume. Every component is manifold. Studio plane,
camera and lights are outside the export collection. Metric units, scale length 1; root and
mesh have zero location/rotation, unit scale and no remaining modifiers. glTF performs the
single Blender +Z/+Y → Godot +Y/-Z axis conversion; the prefab applies no correction.

Seven opaque back-culled Principled materials, in exported surface order:

1. `glassward_office_slate` — broad body and parapet; linear RGB (0.18,0.25,0.32).
2. `glassward_lobby_stone` — footing, entry reveals and selected piers.
3. `glassward_frame` — floor spandrels, side piers and canopy.
4. `glassward_glazing_opaque` — grouped windows and closed door leaves.
5. `glassward_glazing_highlight` — one restrained front-window variation.
6. `glassward_accent_magenta` — one lintel, appearance-only emission strength 0.12.
7. `glassward_indigo` — quiet roof.

The six existing names and PBR values match the tower vocabulary, not external shared
material resources. Actual PBR values are retained in validation.json. No embedded images,
texture/material remaps, lights, animations, rigs, sockets, destructible states or extra
variants. Default Godot automatic LOD and shadow-mesh generation remain enabled; transitions
and repeat-placement performance await engine visual/device review. No speculative manual LOD.

## Prefab and collision

`Visuals/Model` is an identity-transform linked imported GLB, with no editable-child
material overrides or copied render geometry. `Collision/Body` is one StaticBody3D,
layer 1 / mask 0, with a minimal three-box compound following the actual notched footprint:

| Shape | Size (X,Y,Z) m | Centre (X,Y,Z) m |
| --- | --- | --- |
| Core | (26,14.1,14.5) | (0,7.05,0.75) |
| LeftWing | (10.5,14.1,1.5) | (-7.75,7.05,-7.25) |
| RightWing | (10.5,14.1,1.5) | (7.75,7.05,-7.25) |

The boxes meet at Z=-6.5 with no gap, fill the inaccessible building interior and preserve
the complete 5 × 1.5 m entry recess. No box crosses that recess. The entry canopy is overhead
visual decoration, and closed doors remain blocked by the core. Roofs are not authored
traversal routes; filling the building volume does not introduce rooftop gameplay.

Headless load/pack/save normalization plus **two byte-stable save/reload roundtrips** preserve
scene UID and node identities. A fresh process resolves prefab and GLB UIDs from the saved
scene/import. The `.tscn` holds its UID internally; only the GDScript requires a `.uid` sidecar.
Direct text authoring followed by the pinned headless roundtrip is the task-authorized editor
fallback. No owner's live Blender/Godot session was used or claimed synchronized.

## Evidence and validation

[Hero](d04_podiums_01-evidence/hero.png) · [side](d04_podiums_01-evidence/side.png) ·
[entry detail](d04_podiums_01-evidence/entry_detail.png) ·
[47 m / 42° overhead](d04_podiums_01-evidence/overhead_47m_42deg.png).

Four final isolated Blender renders inspected by the producer: Cycles CPU, 32 samples,
AgX, broad studio fill. Supporting views are 1152×648; overhead is 1280×720 per the lean
production rule. Evidence packaging uses 7-bit/channel RGB PNG compression level 9.
The gameplay camera is at Godot (0,47,0), vertically down, north-up, 42° vertical FOV.
The full low-building silhouette, indigo roof and entry notch read clearly; the canopy/door
and accent are elevation details, not promised overhead-readable cues. Initial hidden
glazing, coplanar trim artifacts and tight side framing were corrected before final capture.
These images are not engine captures or proof of actor/target visibility in a populated city.

Final receipt: [validation.json](d04_podiums_01-evidence/validation.json).
Complete producer inventory: [manifest.json](d04_podiums_01-evidence/manifest.json).
Concise outcomes and diagnostic classification: [final.log](d04_podiums_01-evidence/final.log).

- **5,120 source vertices; 9,864 triangles; 6,594 exported vertices including splits.**
- **1 mesh, 7 surfaces, 7 materials.** Zero degenerate source faces, zero non-manifold source
  edges and zero degenerate GLB triangles. Source and actual GLB normals are unit length;
  maximum exported normal-length error is below 0.000001.
- Source, actual GLB coordinates and imported Godot AABB meet the ±0.001 m contract.
- Fresh export from the saved `.blend` is byte-identical: **277,028 bytes**, SHA-256
  `4e8e66b8c8df4bad5331251436b59e1625f709cd0689cb6c01c2fe74ce370e7b`.
- Pinned headless import, linked-resource load, opaque/back-culled material checks,
  bounds/collider assertions, UID checks and two save/reload roundtrips pass.
- **16 shape queries** pass: core/closed door, all four outer corners, both box joins,
  both notch walls, clear notch points, clear under-canopy space and both side bypasses.
- **8 motion casts** pass: actor entry/front-wing/rear/side and car front blocked;
  actor side, under-canopy and car bypass clear. Capsule r=0.35 m, h=1.8 m; test car box
  1.8×1.5×4.4 m. The entry ray hits Z=-6.499999 m, confirming the recessed blocking face.
  These use PhysicsDirectSpaceState3D, not production ActorMotion/driving/network APIs.
- Owned gdstyle formatting/lint pass. No ERROR/SCRIPT ERROR lines in final engine logs.
  `tools/production_checks.py` was not run, as directed by owner decision 52.

Toolchain: Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**; gdstyle **0.3.0**. Full-process author/validator runs
exit 0. Blender's future-6.0 `use_nodes` deprecation warning is not suppressed. The initial
version-only probe reported one tiny unfreed block; subsequent full processes quit cleanly.
Scratch logs, old renders and fresh comparison exports stay in `C:/tmp/ft/assets/d04_podiums_01/`.

## Exact reproduction

Run from the repository root in Git Bash; do not use the owner's live editors:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_podiums_01/author.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_podiums_01/validate.py
# Retain these concise-input logs outside the repository for record.py.
timeout 300 "$G" --headless --path . --import > C:/tmp/ft/assets/d04_podiums_01/import-final.log 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_podiums_01/check_prefab.gd -- --normalize > C:/tmp/ft/assets/d04_podiums_01/prefab-normalize-final.log 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_podiums_01/check_prefab.gd -- --output C:/tmp/ft/assets/d04_podiums_01/prefab-fresh-final.json > C:/tmp/ft/assets/d04_podiums_01/prefab-fresh-final.log 2>&1
timeout 60 "$(mise which gdstyle)" fmt --check tools/asset_production/d04_podiums_01/check_prefab.gd
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/d04_podiums_01/check_prefab.gd
python tools/asset_production/d04_podiums_01/record.py --compress-renders
```

The validator invokes `export.py` on the saved source, using shared
`tools/assets/blender/export_settings.json` with the named collection and static-only
animation/skin settings. Fresh comparison output goes to the scratch `reexport/` folder.
`record.py` verifies geometry/engine receipts, packages the evidence and regenerates the
manifest last. Python Pillow is used only to losslessly store the reduced-bit evidence,
not to generate or alter model geometry. Inspect final images again after reproduction.

## Remaining acceptance

- Supervising art/technical reviewers: exact-commit independent review.
- Layout owners: confirm provisional dimensions, leave streets/grid corners and walking
  gaps open, preserve forecourt breathing room; no placement or tower attachment delivered.
- Render/gameplay owners: actual engine material/normal/LOD appearance, camera/shadow fill,
  populated-scene actor/target visibility and production controller walking/driving tests.
- Network/build/device owners: authoritative/predicted collision, real multiplayer processes
  and transports, packaged dependency checks, repeat-placement cost and sustained Deck tests.

No full production-ready/placement acceptance is claimed by these bounded checks.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
