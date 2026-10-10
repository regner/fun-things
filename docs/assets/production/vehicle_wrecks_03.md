# vehicle_wrecks.03 — Latch wreck

10 October 2026. **Source/export and bounded headless prefab checks delivered;
independent art/technical acceptance and gameplay integration pending.**
Commission: [decision-64 family brief](../vehicle_wrecks.md), continuing the
[production commission](commission.md). Producer: commissioned implementation specialist.
Regner owns direction approval; the production lead/reviewer owns acceptance. M1-B3.1
owns lifecycle integration. This handoff does not mark the registry ready.

## Design and dimensions

An original damaged derivative of the accepted [Latch source](../car_latch_a.md), retaining
its compact two-door silhouette, fixed rear quarters, coral body remnant and ivory bonnet
inset. Broad charcoal regions, a depressed bonnet, off-centre roof crush, folded hatch
sill, broken glazing, a drooping front-left door skin and sagging front bumper communicate
the wreck. The left mirror is missing. Scorched, vertically compressed wheels are joined
static geometry, not mechanical components. No fire, smoke, embers, occupants, interior,
rig, animated doors, sockets or vehicle physics are supplied.

The original glazing becomes opaque near-black aperture backing with sparse closed solid
triangular remnants, avoiding a visible/modelled cabin. Seats, dashboard, interior floor,
mechanical empties and interaction markers are removed. Broad bevels, charcoal/rubber/
metal surfaces and the studio match the [Sable](vehicle_wrecks_01.md) and
[Crate](vehicle_wrecks_02.md) wrecks. Smooth Petrol & Coral treatment remains citywide,
following the [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), without introducing
placements or district-specific gameplay.

- Godot X width **1.893090 m**, Y height **1.416800 m**, Z length **3.432000 m**.
- AABB minimum **(-0.946539, 0, -1.720000)**, maximum **(0.946551, 1.416800,
  1.712000)** m.
- Live horizontal bounds remain within **0.002 m**: width changes by under 0.0001 m
  through static-wheel simplification; length is unchanged. Height drops from 1.5400 m
  to 1.4168 m (**0.1232 m lower**). All four tyres are regrounded at zero.
- Origin remains the live ground-centred **(0,0,0)**, without translation or corrective
  scale. Blender +Y front/+Z up maps once to Godot -Z front/+Y up. Export root and mesh
  have identity transforms, applied rotation/scale and metre units.
- Provisional damage choices, not handling rules: bonnet depression up to 0.22 m;
  roof up to 0.16 m; hatch sill up to 0.14 m; front-left door droop up to 0.18 m/inward
  shift up to 0.08 m; front bumper droop up to 0.10 m. These precede the **0.92**
  vertical stance factor. The bonnet inset has 0.025 m extra separation from its support.

## Source, export and materials

| Role | Path / contract |
| --- | --- |
| Accepted input (unchanged) | `art/source/models/vehicles/car_latch_a/car_latch_a.blend` |
| Editable derivative | `art/source/models/vehicles/vehicle_wrecks_03/vehicle_wrecks_03.blend` |
| Collection / root / mesh | `export_vehicle_wrecks_03` / `VehicleWrecks03` / `VehicleWrecks03_Mesh` |
| Linked export | `art/models/vehicles/vehicle_wrecks_03/vehicle_wrecks_03.glb` + `.glb.import` |
| Saved prefab | `scenes/prefabs/city_cars/vehicle_wrecks_03.tscn` |
| Reproduction/check tools | `tools/asset_production/vehicle_wrecks_03/` |

The supervisor confirmed the family brief's vehicles art paths and city_cars prefab
path instead of the common brief's generic environment paths. `author.py` opens only
the accepted source and saves the separate derivative. Original part names survive as
vertex groups. The source-only studio and 1 m reference cube-empty stay outside the
export collection. No downloaded, purchased, real-brand, image-to-mesh or runtime-generated
geometry is used.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
`export.py` uses `tools/assets/blender/export_settings.json`, explicit collection selection,
and no skins/animations. All authoring modifiers are applied. The author reuses the
Sable wreck's existing closed-shell/material/shard/aim helpers; the validator reuses its
binary GLB readers. These committed sibling tools are read-only dependencies, not copied
geometry or modified sibling outputs. Latch-specific damage and independent literal
expectations live in this asset's tools.

One mesh, eight opaque Principled surfaces, back-face culling, no emission, textures or
embedded images. Exported surface order:

1. `wreck_latch_coral` — surviving coral paint.
2. `wreck_charcoal` — broad burnt bodywork, trim and dead rear lamps.
3. `wreck_latch_ivory` — surviving ivory bonnet inset.
4. `wreck_dead_lamp` — dulled, unlit headlights.
5. `wreck_scorched_rubber` — compressed static tyres.
6. `wreck_exposed_metal` — dull hubs.
7. `wreck_glass_void` — sealed near-black aperture backings.
8. `wreck_glass_remnant` — broad blue-green triangular fragments.

Exact linear PBR values are in [validation.json](vehicle_wrecks_03-evidence/validation.json).
No separate material/texture resources are necessary. Default per-asset Godot generated
LODs remain enabled; population/device appearance is not accepted by this handoff.

## Prefab and collision

`Visuals/Model` is an **identity-transform linked GLB instance**, without editable-child
overrides, embedded render mesh or runtime script. `Collision/WreckBody/Shape` is the only
collider: a dimension-authored **1.74 × 1.39 × 3.40 m BoxShape3D**, centred at
**(0, 0.695, -0.004)** m. Static-world layer **1**, mask **0**; ground is zero. It follows
the main body width and almost the full length. Rounded corners and the lower bonnet
are deliberately simplified by one continuous box. Tyres overhang about 0.077 m per side,
the roof about 0.027 m vertically, and front/rear extremities about 0.016 m longitudinally.
No wheel/door snag colliders are added. This is a blocking wreck, not a walkable platform
or dynamic rigid body.

Prefab UID: `uid://w4enlfdse3rn`; model import UID: `uid://dbxpnwlc2sgco`.
The saved scene header, every external resource and every authored node have explicit
UIDs/unique IDs. Two headless editor-mode load/pack/save/reload cycles are byte-identical
after normalization. A separate runtime process confirms unchanged bytes and identities,
linked ancestry, bounds and no missing dependencies. Five actual PhysicsDirectSpaceState3D
capsule expectations pass (r=0.35 m, h=1.8 m): body and front/rear diagonal corners block;
side and rear bypasses clear. These are bounded envelope queries, **not** ActorMotion
movement, driving, live-to-wreck swap or multiplayer tests.

M1-B3.1 should instantiate this saved prefab at the live visual origin. It owns stopping
commands, retiring the live collider, installing this static collider, authoritative
retention and dependent collision-state ordering. No state writer or automatic swap is
introduced here.

## Evidence and measured validation

[Hero](vehicle_wrecks_03-evidence/hero.png) · [Side](vehicle_wrecks_03-evidence/side.png) ·
[Bonnet/glass detail](vehicle_wrecks_03-evidence/detail.png) ·
[47 m / 42° overhead](vehicle_wrecks_03-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU renders, 32 samples, AgX, **1280×720**, with broad
area lighting and neutral slate ground, matching the family studio. The overhead is
vertical-down perspective at 47 m, vertical FOV 42°, north/+Y at image top; the other three
are inspection views. `finalize.py` strips alpha/metadata and the lowest two RGB bits,
then uses PNG deflate 9, affecting review evidence only without resizing or cropping.

Producer inspected all four views. The compact roof and short body retain Latch identity;
coral roof/side remnants and the broken ivory bonnet inset survive the gameplay-scale
image. The side view exposes the drooping door and roof/bonnet depressions. No noisy grime
or extra debris competes with the silhouette. Actual engine lighting, occupied-city
readability and independent visual acceptance remain pending.

| Check | Final result |
| --- | --- |
| Blender / exported vertices | **4,176 / 6,176** |
| Triangles | **8,176**, below live **10,480** (2,304 fewer) |
| Meshes / material surfaces | **1 / 8** |
| Degenerate faces / triangles | **0 / 0** |
| Non-manifold edges | **0** |
| Maximum source / export normal length error | **1.898e-7 / 1.341e-7** |
| Source-to-GLB AABB agreement | Within **0.00001 m** |
| Fresh saved-source re-export | **Byte-identical** |
| Pinned headless import / runtime load | Exit 0; **no ERROR/SCRIPT ERROR lines** |
| Prefab roundtrip / capsule probes | **2 stable cycles / 5 passing expectations** |
| Added GDScript format/lint | gdstyle 0.3.0: **passes, zero warnings** |

Final source: **357,429 bytes**, SHA-256
`d090db28fce218f74b51a80028f795f32085c9e8dd2a959a58e01f32f167ebae`.
Final GLB: **254,556 bytes**, SHA-256
`2a8e204a050c646cee5d2df4aadc634c4d61d1441da272b75417ecef57965ffa`.
Final prefab SHA-256:
`ad27db946131bd6f4a6425a5b2d4c6cc3f4f9f0f736f14029f88f023177a5c82`.
These values are copied from the final validation receipt. The
[producer manifest](vehicle_wrecks_03-evidence/manifest.json) hashes every produced payload
except itself. [Final log](vehicle_wrecks_03-evidence/final.log) retains concise check and
diagnostic history. Live source/export fingerprints are in validation.json; neither changed.

### Diagnostic boundary

Runtime-mode ResourceSaver omits external-resource UIDs on this engine pin, so the final
harness permits saving only with `--editor -- --normalize`, following the existing
boardwalk tooling. Editor-mode normalization passes all assertions and exits 0, but this
custom SceneTree/editor combination emits shutdown RID/ObjectDB leaks and a scan-aborted
warning even after waiting for initialization. These are retained as an **editor-harness
limitation**, not a clean editor exit claim. The final standalone import and separate
read-only runtime load/physics check exit 0 without ERROR/SCRIPT ERROR lines. The common
MCP addon warns that 4.8 is newer than its tested version; no live MCP session is used.
No broad error suppression or unrelated engine/addon edits were introduced.

## Exact reproduction

From repository root in Git Bash with pinned mise tools and Python Pillow installed:

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
TOOLS=tools/asset_production/vehicle_wrecks_03
SOURCE=art/source/models/vehicles/vehicle_wrecks_03/vehicle_wrecks_03.blend

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/author.py"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/validate.py"
# Optional standalone saved-source export (validator already does this):
timeout 180 "$BLENDER" -noaudio --background --factory-startup "$SOURCE" --threads 4 \
  --python-exit-code 1 --python "$TOOLS/export.py" -- C:/tmp/ft/assets/vehicle_wrecks_03/reexport

timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script "$TOOLS/check_prefab.gd" -- --normalize
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
retries stay in `C:/tmp/ft/assets/vehicle_wrecks_03/`. The prefab was text-authored then
loaded/packed/resaved in isolated pinned headless Godot. No live Blender/Godot session was
touched; headless import does not synchronize any separately open editor scene.
`production_checks.py` was not run, per owner decision 52.

## Remaining acceptance

- Independent art/technical review of this source/export/prefab candidate.
- M1-B3.1 same-pose live-to-wreck swap, collider retirement/installation, authoritative
  retention, chain behavior and late-join/lifecycle ordering.
- Production ActorMotion/car movement checks and relevant separate-process authoritative/
  predicted multiplayer tests against the installed wreck.
- Saved world placement/clearances and gameplay-camera readability with actual city
  lighting, actors and effects; no world scene was changed.
- Generated LOD appearance, repeated-wreck draw cost, packaged-platform and sustained
  Deck evidence. Clean editor-harness shutdown remains unproved as noted above.

Neither earlier wreck handoff lists Latch as pending, so no sibling document or manifest
required editing. Shared trackers, catalogue, TODO, live car sources/exports and historical
receipts are unchanged. No unproduced sibling is a pending item of this delivery.
