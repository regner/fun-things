# d04_podiums.03 — Short service-wing shell

10 October 2026. **Source/export, linked prefab and bounded headless checks delivered;
independent review, placement and gameplay/device acceptance pending.** Producer: commissioned
isolated asset-production worker. Accepting owners: supervising art/technical reviewers,
then layout/gameplay/device owners. The [production commission](commission.md) and current
asset task supersede the family brief's historical concept-only/candidate status.

References: [podium family](../d04_podiums.md), [low office](d04_podiums_01.md),
[setback podium](d04_podiums_02.md), [Glassward concept](../../concepts/districts-v1/glassward.md),
[asset breakdown](../../concepts/districts-v1/glassward-assets.md),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md),
[gridded streets](../../concepts/world-v1/stage-04-streets/README.md).

## Design and dimensions

An original single-storey service wing: short slate mass, quiet indigo roof, high grouped
opaque glazing, broad closed shutter and an off-centre recessed entrance. Four broad side
ventilation blades identify the service elevation without adding rooftop equipment. Pale
stone reveals, blue doors and one small magenta lintel retain the earlier office/podium
vocabulary. The low, narrow silhouette and asymmetric notch distinguish it from those
siblings; this is not a rescaled office or another tier of the podium.

All dimensions are **provisional authored proposals** under the standing production rules,
not inferred from generated images or accepted parcel allocations. Godot axes are X width,
Y height and Z depth; measured envelope tolerance is ±0.001 m.

| Contract | Provisional value |
| --- | --- |
| Nominal footprint | 20 × 10 m, 200 m² bounding rectangle |
| Entry recess | 4 m wide × 1.6 m deep, centred at X=5 m |
| Solid footprint | 193.6 m², excluding the 6.4 m² entry recess |
| Notch limits | X=3…7 m, Z=-5…-3.4 m; open to the sky above the inset canopy |
| Building roof datum | Y=6 m, matching the siblings' lobby height |
| Roof cap / parapet | Roof cap top Y=6.04 m; parapet top Y=6.9 m |
| Whole visual AABB | min (-10,0,-5), max (10,6.9,5) m |
| Whole visual size | **20 × 6.9 × 10 m** |
| Recessed door blocking plane | Z=-3.4 m; visual pulls project at most 0.13 m from it |
| Closed shutter | 6.2 × 3.2 m panel; front elevation within Z=-5 m envelope |
| Inset canopy | 4 × 1.55 m plan; lowest soffit Y=3.54 m |
| Pivot / front | Ground-centred nominal footprint, (0,0,0); Godot -Z / Blender +Y |

The shell has no interior, working door/shutter, steps, raised apron, paving, roof access,
rig, destruction or new interaction. The shutter and ventilation are normal building
facade details, not duplicate shared freestanding hardware. No roof fixtures, sign carriers,
artwork, real brands or text are included. Placement supplies flat ground in the recess.
Footing/trim define the nominal envelope; body faces sit up to 0.05 m behind them for layering.

### Family handoff

The six-metre roof datum aligns with the sibling lobby height; materials use exactly the
same named PBR vocabulary. The compact service wing can sit beside office sites, but no
attachment socket, structural connection or tower mounting compatibility is promised.
This freestanding exterior is not a sealed superblock platform or skybridge. Leave grid
corners, inter-site walking gaps and forecourts open in the actual layout. A source-only
asset check cannot establish that district arrangement.

Both earlier sibling handoffs were read. Neither lists this asset as a stale pending item;
no sibling document, evidence manifest or historical receipt needed an update. No family
brief, register, progress file, project setting or saved world placement was changed.

## Source, export and materials

- Source: `art/source/models/environment/d04_podiums_03/d04_podiums_03.blend`.
- Collection: `export_d04_podiums_03`; root `D04Podiums03`; mesh `D04Podiums03_Mesh`.
- Explicit export: `art/models/environment/d04_podiums_03/d04_podiums_03.glb`, with pinned
  Godot `.import` metadata.
- Linked wrapper: `scenes/prefabs/environment/d04_podiums_03.tscn`.
- Reproduction/check tools: `tools/asset_production/d04_podiums_03/` contains
  `author.py`, `export.py`, `validate.py`, `record.py`, `check_prefab.gd` and its `.uid`.

Original Blender construction only; no downloads, purchased meshes, image-to-mesh, external
textures/fonts or prototype dependencies. Editable closed architectural parts use applied
bevels and weighted normals, then join into one ground-origin mesh. Parts overlap
intentionally: each is manifold, but the shell is not a Boolean-unioned building volume.
Metric units, scale length 1; root/mesh location and rotation zero, scale one, no modifiers.
Studio plane, lights and camera stay outside the export collection. Shared
`tools/assets/blender/export_settings.json` owns the pinned export contract; the asset
selects its collection and disables animations/skins. Axis conversion happens once in glTF.

Seven opaque, back-culled Principled surfaces in actual export order:

1. `glassward_office_slate` — shell, parapet, shutter and ventilation blades.
2. `glassward_lobby_stone` — footing, entry reveals, shutter jambs, soffit and door hardware.
3. `glassward_frame` — fascia, shutter seams, vent/entry backing and canopy.
4. `glassward_glazing_opaque` — high windows and closed door leaves.
5. `glassward_glazing_highlight` — one restrained west-side window variation.
6. `glassward_accent_magenta` — single entry lintel; emission strength 0.12, no real light.
7. `glassward_indigo` — quiet roof cap.

Names and PBR factors match the siblings, not external shared material resources. Exact
factors are in validation.json. No textures, embedded images, external remaps, material
overrides, animations, sockets or additional variants. Default Godot automatic LOD and
shadow-mesh generation remain enabled; transitions and repeated-placement performance
await engine/device review. No speculative manual LOD or ratified performance budget.

## Prefab and collision

`Visuals/Model` is an identity-transform linked GLB instance, with no copied render mesh,
editable children or corrective scale/rotation. `Collision/Body` is one StaticBody3D,
layer 1 / mask 0, with a minimal three-box compound following the asymmetric footprint:

| Shape | Size (X,Y,Z) m | Centre (X,Y,Z) m |
| --- | --- | --- |
| Core | (20,6.9,8.4) | (0,3.45,0.8) |
| LeftWing | (13,6.9,1.6) | (-3.5,3.45,-4.2) |
| RightWing | (3,6.9,1.6) | (8.5,3.45,-4.2) |

The boxes meet at Z=-3.4 with no gaps, filling the inaccessible building volume while
preserving the entire 4 × 1.6 m entry recess. The closed doors and shutter remain blocked;
decorative hardware does not add snag colliders. The canopy is above head height and remains
visual-only. Roof caps are not authored traversal surfaces; solid shell collision does not
introduce rooftop gameplay. No automatic render-mesh collision or lot-wide invisible blocker.

Task-authorized direct text authoring followed by pinned headless load/pack/save is the
editor fallback. Normalization plus **two byte-stable save/reload roundtrips** preserve
node identities and the internal scene UID. A post-save import registers the scene UID;
an independent fresh process resolves both prefab and GLB UIDs. The scene stores its UID
internally; the check script has its engine-generated `.uid`. No owner's live Blender/Godot
session was accessed or claimed synchronized.

## Evidence and validation

[Hero](d04_podiums_03-evidence/hero.png) · [side](d04_podiums_03-evidence/side.png) ·
[entry detail](d04_podiums_03-evidence/entry_detail.png) ·
[47 m / 42° overhead](d04_podiums_03-evidence/overhead_47m_42deg.png).

Four isolated Blender images inspected by the producer: Cycles CPU, 32 samples, AgX, broad
studio fill. Supporting views are 1152×648, overhead 1280×720 per lean production rules.
Gameplay camera: Godot (0,47,0), vertically down, north-up, 42° vertical FOV. Final packaging
is 7-bit/channel RGB PNG, compression level 9. The quiet elongated roof and offset notch
read overhead. Doors, shutter seams, side ventilation and magenta lintel are elevation
features, not promised overhead wayfinding. Initial coplanar fascia corners and a roof-cap
gap were corrected before final captures. These are not engine or populated-city captures.

Final [validation.json](d04_podiums_03-evidence/validation.json), producer
[manifest.json](d04_podiums_03-evidence/manifest.json), concise
[final.log](d04_podiums_03-evidence/final.log):

- **2,820 source vertices; 5,424 triangles; 3,668 exported vertices including splits.**
- **1 mesh, 7 surfaces/materials**. Zero degenerate source faces/non-manifold edges and zero
  degenerate GLB triangles. Source/GLB normals are unit length; exported maximum length
  error is below 0.000001.
- Source, actual GLB positions and Godot AABB match the ±0.001 m envelope. The source/GLB
  validator additionally checks that no exported vertices fill the notch above the canopy.
- Fresh export from the saved source is byte-identical: **156,744 bytes**, SHA-256
  `3001a7bd82a993b57592d59d1143335610a0371bae469beef961eef1d3cf11ba`.
- Pinned headless import, resource/material/UID/bounds inspection and two byte-stable
  save/reload roundtrips pass with no ERROR/SCRIPT ERROR lines in final engine logs.
- **17 shape queries** pass: core, door, shutter, four corners, both box joins, both notch
  walls, both clear notch edges, entry/under-canopy space and both side bypasses.
- **8 actor/car motion casts** pass: actor entry/shutter/rear/side and car front blocked;
  actor side/under-canopy and car side bypasses clear. Capsule r=0.35 m, h=1.8 m; test car
  box 1.8×1.5×4.4 m. Entry ray hits Z=-3.400001 m. These use PhysicsDirectSpaceState3D,
  not production ActorMotion/driving/authoritative prediction or transport APIs.
- Owned gdstyle formatting and zero-warning lint pass. The initial check found one long
  line; it was formatted and rechecked. `tools/production_checks.py` was not run (decision 52).

Toolchain: Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**, gdstyle **0.3.0**. Full author/validator processes
exit 0; future-Blender-6.0 `use_nodes` deprecation warnings are retained, not suppressed.
Scratch logs and comparison exports are in `C:/tmp/ft/assets/d04_podiums_03/`.

## Exact reproduction

From the repository root in Git Bash, using isolated CLI processes only:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_podiums_03/author.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_podiums_03/validate.py
mkdir -p C:/tmp/ft/assets/d04_podiums_03
timeout 300 "$G" --headless --path . --import > C:/tmp/ft/assets/d04_podiums_03/import-initial.log 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_podiums_03/check_prefab.gd -- --normalize > C:/tmp/ft/assets/d04_podiums_03/prefab-normalize-final.log 2>&1
# Register the normalized scene UID before the independent fresh-process check.
timeout 300 "$G" --headless --path . --import > C:/tmp/ft/assets/d04_podiums_03/import-final.log 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_podiums_03/check_prefab.gd -- --output C:/tmp/ft/assets/d04_podiums_03/prefab-fresh-final.json > C:/tmp/ft/assets/d04_podiums_03/prefab-fresh-final.log 2>&1
timeout 60 "$(mise which gdstyle)" fmt --check tools/asset_production/d04_podiums_03/check_prefab.gd
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/d04_podiums_03/check_prefab.gd
python tools/asset_production/d04_podiums_03/record.py --compress-renders
```

The validator runs `export.py` against the saved `.blend`, compares fresh GLB bytes and
records source/GLB geometry. `record.py` verifies final engine/geometry receipts and hashes
all produced payloads last, excluding its self-referential manifest. Pillow packages evidence
only; it does not create model geometry. Reinspect images after regeneration.

## Remaining acceptance

- Supervising art/technical reviewers: exact-commit independent review.
- Layout owners: approve provisional dimensions/site use, leave grid corners, walking gaps
  and forecourts open; assess any later connection to adjacent buildings separately.
- Render/gameplay owners: actual engine material/normal/LOD appearance, camera/shadow fill,
  populated actor/target visibility and production-controller walking/driving checks.
- Network/build/device owners: authoritative/predicted collision, real multiplayer processes
  and transports, packaged dependencies, repeat-placement cost and sustained Deck tests.

No full production/placement acceptance is claimed by these bounded checks.
