# vehicle_wrecks.02 — Crate wreck

10 October 2026. **Source/export and bounded headless prefab checks delivered;
independent art/technical acceptance and gameplay integration pending.**
Commission: [decision-64 family brief](../vehicle_wrecks.md), continuing the
[production commission](commission.md). Producer: commissioned implementation specialist.
Regner owns direction approval; the production lead/reviewer owns acceptance. M1-B3.1
owns lifecycle integration. This handoff does not mark the registry ready.

## Design and dimensions

An original damaged derivative of the accepted [Crate source](../car_crate_a.md).
The short bonnet, tall square hatch cabin, ivory paint remnant and petrol bonnet inset
retain Crate identity. Broad charcoal surfaces, an off-centre roof depression, buckled
bonnet and rear hatch sill, broken glazing, a sagging front-left door skin and drooping
rear bumper communicate the wreck. The right mirror is missing. Wheels are scorched,
vertically compressed static geometry joined into the mesh, not mechanical components.
No fire, smoke, embers, occupants, interior, rig, animated doors, sockets or vehicle
physics are supplied.

The original glazing becomes opaque near-black aperture backing with sparse closed
triangular glass remnants; it does not expose a cabin. Seats, dashboard, interior floor,
mechanical empties and interaction markers are removed. Broad bevels, muted glass,
charcoal/rubber/metal materials and the studio match the [Sable wreck](vehicle_wrecks_01.md).
The smooth Petrol & Coral treatment remains citywide, following the
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), without adding
placements or district-specific gameplay.

- Godot X width **1.912704 m**, Y height **1.508800 m**, Z length **3.680690 m**.
- AABB minimum **(-0.956191, 0, -1.845000)**, maximum **(0.956513, 1.508800,
  1.835690)** m.
- Live horizontal bounds remain within **0.002 m**: width reduces by about 0.00030 m;
  length reduces by about 0.00131 m at the rear bumper. The original height is 1.6500 m;
  final height is **0.1412 m lower**. Static-wheel simplification is regrounded at zero.
- Origin remains the live ground-centred **(0,0,0)**, with no translation or corrective
  scale. Blender +Y front/+Z up maps once to Godot -Z front/+Y up. Root and mesh have
  identity transforms and unit scale; source units are metres.
- Damage values are provisional authored choices, not handling rules: bonnet depression
  up to 0.23 m; roof up to 0.18 m; hatch sill up to 0.16 m; front-left door droop up to
  0.17 m/inward shift up to 0.09 m; rear bumper droop up to 0.12 m. These precede the
  **0.92** vertical stance factor. The bonnet inset has 0.025 m additional separation
  from its supporting body. The roof ribs follow the roof depression.

## Source, export and materials

| Role | Path / contract |
| --- | --- |
| Accepted input (unchanged) | `art/source/models/vehicles/car_crate_a/car_crate_a.blend` |
| Editable derivative | `art/source/models/vehicles/vehicle_wrecks_02/vehicle_wrecks_02.blend` |
| Collection / root / mesh | `export_vehicle_wrecks_02` / `VehicleWrecks02` / `VehicleWrecks02_Mesh` |
| Linked export | `art/models/vehicles/vehicle_wrecks_02/vehicle_wrecks_02.glb` + `.glb.import` |
| Saved prefab | `scenes/prefabs/city_cars/vehicle_wrecks_02.tscn` |
| Reproduction/check tools | `tools/asset_production/vehicle_wrecks_02/` |

The supervisor confirmed the family brief's vehicles art paths and city_cars prefab
path instead of the common brief's generic environment paths. `author.py` opens the
accepted live source and saves only this derivative. Original part names survive as
vertex groups. The source-only studio and 1 m reference cube-empty stay outside the
export collection. No downloaded, purchased, real-brand, image-to-mesh or runtime-generated
geometry is used.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
`export.py` uses `tools/assets/blender/export_settings.json`, the explicit named collection,
and no skins/animations. All authoring modifiers are applied. The author reuses the
existing Sable wreck's closed-shell/material/shard/aim helpers; the validator reuses its
binary GLB readers. Those committed sibling tools are read-only dependencies, not copied
geometry or modified sibling outputs. Asset-specific damage and independent literal
Crate expectations live in this asset's tools.

One mesh, eight opaque Principled surfaces, back-face culling, no emission, textures or
embedded images. Exported surface order:

1. `wreck_crate_ivory` — surviving warm ivory paint.
2. `wreck_charcoal` — broad burnt bodywork, trim and dead rear lamps.
3. `wreck_crate_petrol` — surviving bonnet inset paint.
4. `wreck_dead_lamp` — dulled, unlit headlights.
5. `wreck_scorched_rubber` — compressed static tyres.
6. `wreck_exposed_metal` — dull hubs.
7. `wreck_glass_void` — sealed near-black aperture backings.
8. `wreck_glass_remnant` — broad blue-green triangular fragments.

Exact linear PBR values are in [validation.json](vehicle_wrecks_02-evidence/validation.json).
No separate material or texture resources are necessary. Default per-asset Godot generated
LODs remain enabled; this does not establish population/device appearance acceptance.

## Prefab and collision

`Visuals/Model` is an **identity-transform linked GLB instance**, with no editable-child
overrides, embedded render mesh or runtime script. `Collision/WreckBody/Shape` is the only
collider: a dimension-authored **1.76 × 1.48 × 3.65 m BoxShape3D**, centred at
**(0, 0.74, -0.004)** m. Static-world layer **1**, mask **0**. Its ground is zero; it
matches the main body width and almost the full length. Rounded corners and the lower
bonnet are deliberately simplified by the continuous box. Tyres overhang by about
0.077 m per side, the roof by about 0.029 m vertically, and front/rear extremities by
about 0.016 m longitudinally. No wheel/door snag colliders are added. This is a blocking
wreck, not a walkable platform or dynamic rigid body.

Prefab UID: `uid://ckrjwghik6kgh`; model import UID: `uid://dlrc24mcxldex`.
Two headless load/pack/save/reload cycles are byte-identical after normalization. A fresh
process retains the same scene hash and UID. The asset-local save harness reads the saved
header UID before consulting the cache, so a stale pre-normalization import registry
cannot replace an already saved identity. An early cross-process run exposed this cache
issue; only the corrected runs are final identity evidence.

Five actual PhysicsDirectSpaceState3D capsule expectations pass (r=0.35 m, h=1.8 m):
body and front/rear diagonal corners block; side and rear bypasses remain clear. These
are bounded collision-envelope queries, **not** ActorMotion movement, driving, swap,
authoritative lifecycle or multiplayer tests.

M1-B3.1 should instantiate this saved prefab at the live visual origin. It owns stopping
commands, retiring the live collider, installing this static collider, authoritative
retention and dependent collision-state ordering. No state writer or automatic swap is
introduced here.

## Evidence and measured validation

[Hero](vehicle_wrecks_02-evidence/hero.png) · [Side](vehicle_wrecks_02-evidence/side.png) ·
[Bonnet/glass detail](vehicle_wrecks_02-evidence/detail.png) ·
[47 m / 42° overhead](vehicle_wrecks_02-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU renders, 32 samples, AgX, **1280×720**, with
broad area lighting and neutral slate ground, matching the Sable studio. The overhead
is vertical-down perspective at 47 m, vertical FOV 42°, north/+Y at image top; the other
three are inspection views. `finalize.py` strips alpha/metadata and the lowest two RGB
bits, then uses PNG deflate 9, affecting review evidence only, without resizing/cropping.

Producer inspected all four views: the short bonnet and large square roof retain the
Crate silhouette, while the surviving ivory roof edge and petrol inset contrast against
the burnt body. The lowered door and broad bonnet depression read in inspection views;
broken glazing and broad paint loss survive the gameplay-scale image. Actual engine
lighting, occupied-city readability and independent visual acceptance remain pending.

| Check | Final result |
| --- | --- |
| Blender / exported vertices | **4,742 / 7,009** |
| Triangles | **9,292**, below live **11,256** (1,964 fewer) |
| Meshes / material surfaces | **1 / 8** |
| Degenerate faces / triangles | **0 / 0** |
| Non-manifold edges | **0** |
| Maximum source / export normal length error | **2.298e-7 / 1.304e-7** |
| Source-to-GLB AABB agreement | Within **0.00001 m** |
| Fresh saved-source re-export | **Byte-identical** |
| Pinned headless import | Exit 0; **no ERROR/SCRIPT ERROR lines** |
| Prefab roundtrip / capsule probes | **2 stable cycles / 5 passing expectations** |
| Added GDScript format/lint | gdstyle 0.3.0: **passes, zero warnings** |

Final source: **390,941 bytes**, SHA-256
`a9e1afd43e283dcaa80b7f2b9972d17a920e3167ddfd943e24198c448ada5230`.
Final GLB: **287,912 bytes**, SHA-256
`dd7fc194de277f4ff08f5bc482571d95f228101672edf7cccf582e05d1752240`.
Final prefab SHA-256:
`b8bfb150b0845071aea693330cc40e0cd930d2cf3f1252a2a88719f6d1efbd49`.
These values are copied from the final validation receipt. The
[producer manifest](vehicle_wrecks_02-evidence/manifest.json) hashes every produced payload
except itself. [Final log](vehicle_wrecks_02-evidence/final.log) retains concise check and
repair history. Live source/export fingerprints are in validation.json; neither changed.

## Exact reproduction

From repository root in Git Bash with pinned mise tools and Python Pillow installed:

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
TOOLS=tools/asset_production/vehicle_wrecks_02
SOURCE=art/source/models/vehicles/vehicle_wrecks_02/vehicle_wrecks_02.blend

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/author.py"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/validate.py"
# Optional standalone saved-source export (validator already does this):
timeout 180 "$BLENDER" -noaudio --background --factory-startup "$SOURCE" --threads 4 \
  --python-exit-code 1 --python "$TOOLS/export.py" -- C:/tmp/ft/assets/vehicle_wrecks_02/reexport

timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --path . --script "$TOOLS/check_prefab.gd"
timeout 180 "$(mise which godot)" --headless --path . --script "$TOOLS/check_prefab.gd"
"$(mise which gdstyle)" fmt --check "$TOOLS/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$TOOLS/check_prefab.gd"
python "$TOOLS/finalize.py"
# Final import registers normalized scene identities and verifies import sidecars:
timeout 300 "$(mise which godot)" --headless --path . --import
python "$TOOLS/finalize.py"
```

`author.py` rebuilds geometry and renders from the live source; `validate.py` reads the
saved derivative and fresh-exports into scratch. On an intentional revision, copy the new
fingerprints into this handoff before running `finalize.py` last. Scratch exports and raw
retries stay in `C:/tmp/ft/assets/vehicle_wrecks_02/`. No live Blender/Godot session was
touched. Windowed tools are unavailable by contract; this prefab was text-authored and
normalized in the pinned headless engine. Import does not prove synchronization of any
separately open editor scene. `production_checks.py` was not run, per owner decision 52.

## Remaining acceptance

- Independent art/technical review of this source/export/prefab candidate.
- M1-B3.1 same-pose live-to-wreck swap, collider retirement/installation, authoritative
  retention, chain behavior and late-join/lifecycle ordering.
- Production ActorMotion/car movement checks and relevant separate-process authoritative/
  predicted multiplayer tests against the installed wreck.
- Saved world placement/clearances and gameplay-camera readability with actual city
  lighting, actors and effects; no world scene was changed.
- Generated LOD appearance, repeated-wreck draw cost, packaged-platform and sustained
  Deck evidence.

No unproduced sibling is a pending item of this delivery. The Sable handoff contains no
stale pending Crate item, so no sibling document or manifest required editing. Shared
trackers, catalogue, TODO, live car sources/exports and historical receipts are unchanged.
