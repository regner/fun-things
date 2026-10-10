# d04_podiums.02 — Setback podium

10 October 2026. **Source/export, linked prefab and bounded headless checks delivered;
independent review, placement and gameplay/device acceptance pending.** Producer: commissioned
isolated asset-production worker. Accepting owners: supervising art/technical reviewers,
then layout/gameplay/device owners. The [production commission](commission.md) supersedes
the family brief's historical concept-only restriction.

References: [podium family](../d04_podiums.md), [earlier low office](d04_podiums_01.md),
[Glassward concept](../../concepts/districts-v1/glassward.md),
[asset breakdown](../../concepts/districts-v1/glassward-assets.md),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md),
[gridded streets](../../concepts/world-v1/stage-04-streets/README.md).

## Design and dimensions

An original two-tier slate office podium: a broad six-metre lobby base, smaller rearward
upper storey, quiet indigo roof setbacks and a deep covered entrance. Grouped opaque blue
glazing, pale piers and one restrained magenta lintel share the earlier low office's
Glassward vocabulary. The stepped silhouette, rather than added rooftop equipment or
luminous crowns, distinguishes this member. No real brands, copy, rooftop props or interiors.

All measurements are **provisional authored proposals**, permitted by the standing brief;
not inferred from concept images, accepted parcel allocations or a tower attachment API.
Godot axes are X width / Y height / Z depth. Envelope tolerance: ±0.001 m.

| Contract | Provisional value |
| --- | --- |
| Ground building footprint | 30 × 18 m, 540 m²; X ±15, Z ±9 |
| Lobby roof datum | Y=6 m |
| Upper footprint | 22 × 12 m, centred (X=0,Z=2); X ±11, Z=-4…8 |
| Upper setbacks | 5 m front, 4 m each side, 1 m rear |
| Upper storey | 3.6 m pitch, roof datum Y=9.6 m |
| Upper parapet | 0.9 m, top Y=10.5 m |
| Whole visual AABB | min (-15,0,-11), max (15,10.5,9) m |
| Whole visual size | **30 × 10.5 × 20 m**, including entrance canopy |
| Entrance | Closed door plane approximately Z=-9.02 m; no interior route |
| Deep canopy | 6.6 m wide, approximately 2 m projection; front Z=-11 m |
| Canopy clearance | Main soffit Y=3.69 m; overhead side returns bottom Y=2.8 m |
| Pivot / front | Ground centre of nominal 30 × 18 m body; front Godot -Z / Blender +Y |

The canopy shelters a ground-level strip in front of the facade; it is not a notch into the
solid footprint. It has no ground piers. Its above-head returns frame the entrance without
blocking the walk strip. Doors and pulls are decorative projections of at most 0.13 m;
the closed building face owns collision. The base has no raised forecourt, steps or paving.
Placement supplies flat ground and must reserve the entrance overhang/clearance.

### Family and tower interface

The 6 m lobby, 3.6 m floor rhythm, materials and restrained entry accent match
`d04_podiums.01`; the wider, lower, rearward-stepped silhouette is a different design, not
that sibling rescaled. The handoff doc for `.01` has no stale pending item for this delivery,
so no sibling files or historical receipts were changed.

This is a separate modest base, not a sealed superblock platform, skybridge or whole-site
assembly. Layout must leave grid corners, walking gaps and forecourts open between instances.
No roof access, raised walking route, tower socket or tower-on-roof compatibility is implied.
Existing tower prefabs contain their own full ground-to-crown building bodies; they are not
silently stacked on or embedded in this podium. Any actual tower/podium join needs a selected
assembly and coordinated interface review. This delivery provides the setback form and
measured datums, not a new attachment or placement system.

## Source, export and materials

- Source: `art/source/models/environment/d04_podiums_02/d04_podiums_02.blend`.
- Named collection `export_d04_podiums_02`; root `D04Podiums02`; mesh `D04Podiums02_Mesh`.
- Explicit export: `art/models/environment/d04_podiums_02/d04_podiums_02.glb`, with pinned
  Godot `.import` sidecar.
- Linked wrapper: `scenes/prefabs/environment/d04_podiums_02.tscn`.
- Reproduction/check tools: `tools/asset_production/d04_podiums_02/` contains
  `author.py`, `export.py`, `validate.py`, `record.py`, `check_prefab.gd` and its `.uid`.

Original Blender construction only: no downloads, purchased meshes, image-to-mesh, external
textures/fonts or prototype dependencies. Authoring follows the sibling's closed beveled
architectural parts and weighted normals. Parts overlap intentionally, then join into one
mesh; each component is manifold, but the building is not a Boolean-unioned single volume.
Metric scale length 1; root/mesh location and rotation zero, scale one, ground-origin pivot,
no unapplied modifiers. Studio ground, lights and camera are outside the export collection.
Shared `tools/assets/blender/export_settings.json` owns the export settings; the asset
selects its collection and disables animation/skins. Axis conversion happens once in glTF.

Seven opaque, back-culled Principled surfaces, in actual exported order:

1. `glassward_office_slate` — body and upper parapet; linear RGB (0.18,0.25,0.32).
2. `glassward_lobby_stone` — footing, piers, soffit, door mullion and pulls.
3. `glassward_frame` — broad fascia and entrance canopy/backing.
4. `glassward_indigo` — both quiet roof caps.
5. `glassward_glazing_opaque` — broad grouped windows and closed doors.
6. `glassward_glazing_highlight` — one upper front window variation.
7. `glassward_accent_magenta` — single entry lintel; emission strength 0.12, no actual light.

Names and PBR values match the sibling, but exported surface order is asset-specific.
Exact factors are in validation.json. No textures, embedded images, external remaps,
material overrides, animations, rigs, sockets, damage states or extra variants. Godot's
default automatic LOD and shadow-mesh generation remain enabled; transitions and repeated
placement performance remain unreviewed. No speculative manual LOD or platform budget.

## Prefab and collision

`Visuals/Model` is the identity-transform imported GLB instance. No copied render geometry,
editable children, procedural node hierarchy or corrective scale/rotation.
`Collision/Body` is one StaticBody3D, layer 1 / mask 0, with two deliberate boxes:

| Shape | Size (X,Y,Z) m | Centre (X,Y,Z) m |
| --- | --- | --- |
| Base | (30,6,18) | (0,3,0) |
| Upper | (22,4.5,12) | (0,8.25,2) |

The boxes meet at Y=6, filling the inaccessible building and upper parapet volume. The
setbacks above the base remain empty; no collider inflates the lower body to full height.
Roof caps are not authored traversal routes. Overhead canopy/returns remain visual-only;
no ground-level blocker extends to Z=-11. The entrance route is clear until the closed
facade at Z=-9. No imported render-mesh collision, thin glazing snags or per-pier colliders.

Task-authorized direct text scene authoring followed by pinned headless load/pack/save is
the editor fallback. Normalization plus **two byte-stable save/reload roundtrips** preserve
node identities and the internal scene UID. A post-normalization import registers that UID;
a fresh process then resolves both prefab and model UIDs. No owner's live Blender/Godot
session was accessed, and no claim of synchronizing a separate open scene is made.

## Evidence and validation

[Hero](d04_podiums_02-evidence/hero.png) · [side](d04_podiums_02-evidence/side.png) ·
[entrance detail](d04_podiums_02-evidence/entry_detail.png) ·
[47 m / 42° overhead](d04_podiums_02-evidence/overhead_47m_42deg.png).

Four final isolated Blender images inspected by the producer. Cycles CPU, 32 samples, AgX;
supporting views 1152×648, gameplay overhead 1280×720 per lean production rules. Gameplay
camera: Godot (0,47,0), vertically down, north-up, 42° vertical FOV. Final evidence is
7-bit/channel RGB PNG, compression level 9. The broad stepped roof silhouette and entry
canopy read overhead; magenta lintel and door hardware are supporting-view details, not
overhead wayfinding. Initial coplanar lower-roof faces produced black artifacts; separating
the roof/support datums corrected them before final captures. No engine or populated-city
visual acceptance is claimed by Blender evidence.

Final [validation.json](d04_podiums_02-evidence/validation.json), complete producer
[manifest.json](d04_podiums_02-evidence/manifest.json), concise
[final.log](d04_podiums_02-evidence/final.log):

- **3,584 source vertices; 6,912 triangles; 4,608 exported vertices including splits.**
- **1 mesh, 7 surfaces/materials**, zero source degenerate faces/non-manifold edges,
  zero degenerate GLB triangles. Source/GLB normals are unit length; exported maximum
  normal-length error is below 0.000001.
- Source, actual GLB positions and imported Godot AABB match the ±0.001 m whole-envelope
  contract. Validator separately asserts upper-tier X/Z extents to prove the actual setbacks.
- Fresh export from the saved source is byte-identical: **195,812 bytes**, SHA-256
  `23b695084e64a487cef9661b4a9be603746d9828a0cff653e6e9dd29836f5ec1`.
- Pinned headless import, dependency/UID checks, material/back-culling assertions, linked
  instance inspection and two save/reload roundtrips pass.
- **18 shape queries** pass: base/closed door, four ground corners, upper corners, tier
  seam, upper solid region, all four open setbacks, covered entry and side bypasses.
- **8 actor/car motion casts** pass: entry/front/rear/side blocked, actor/car side bypasses
  and passage under the canopy clear. Actor capsule r=0.35 m / h=1.8 m; test car box
  1.8×1.5×4.4 m. Front ray hits Z=-9 m. These are PhysicsDirectSpaceState3D checks, not
  production ActorMotion, driving, authoritative prediction or transport tests.
- Owned gdstyle formatting/lint pass. Final engine logs contain no ERROR/SCRIPT ERROR lines.
  `tools/production_checks.py` was not run (owner decision 52).

Toolchain: Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**, gdstyle **0.3.0**. Final full Blender processes
exit 0; the future-6.0 `use_nodes` deprecation warning is retained, not suppressed. The
first fresh engine check preceded the post-normalization UID scan and failed only the
prefab UID assertion; the required post-save import and fresh check then pass. Scratch
renders, initial diagnostics and comparison exports remain in `C:/tmp/ft/assets/d04_podiums_02/`.

## Exact reproduction

From the worktree root in Git Bash, using isolated CLI processes only:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_podiums_02/author.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_podiums_02/validate.py
timeout 300 "$G" --headless --path . --import > C:/tmp/ft/assets/d04_podiums_02/import-final.log 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_podiums_02/check_prefab.gd -- --normalize > C:/tmp/ft/assets/d04_podiums_02/prefab-normalize-final.log 2>&1
# Register the normalized scene UID before the independent fresh-process check.
timeout 300 "$G" --headless --path . --import > C:/tmp/ft/assets/d04_podiums_02/import-final.log 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_podiums_02/check_prefab.gd -- --output C:/tmp/ft/assets/d04_podiums_02/prefab-fresh-final.json > C:/tmp/ft/assets/d04_podiums_02/prefab-fresh-final.log 2>&1
timeout 60 "$(mise which gdstyle)" fmt --check tools/asset_production/d04_podiums_02/check_prefab.gd
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/d04_podiums_02/check_prefab.gd
python tools/asset_production/d04_podiums_02/record.py --compress-renders
```

The validator runs `export.py` against the saved `.blend`, byte-compares the fresh GLB and
records source/GLB geometry. `record.py` checks final engine/geometry receipts and hashes
all payloads last (except its self-referential manifest). Pillow packages evidence only;
it does not create or alter model geometry. Reinspect images after regeneration.

## Remaining acceptance

- Supervising art/technical reviewers: exact-commit independent review.
- Layout owners: approve provisional dimensions and actual site use, preserve grid corners,
  inter-site walking gaps, open forecourts and entry overhead clearance; any tower interface
  or assembly needs separate coordination. No saved world placement was authored.
- Render/gameplay owners: engine material/normal/LOD appearance, actual camera/shadow fill,
  populated actor/target visibility and production-controller walking/driving checks.
- Network/build/device owners: authoritative/predicted collision, real multiplayer processes
  and transports, packaged dependency checks, repeat-placement cost and sustained Deck tests.

No full production/placement acceptance is claimed by these bounded checks.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
