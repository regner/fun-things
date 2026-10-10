# vehicle_wrecks.01 — Sable sedan wreck

10 October 2026. **Source/export and bounded headless prefab checks delivered;
independent art/technical acceptance and gameplay integration pending.**
Commission: [decision-64 family brief](../vehicle_wrecks.md), continuing the
[production commission](commission.md). Producer: commissioned implementation specialist.
Regner owns direction approval; the production lead/reviewer owns acceptance and M1-B3.1
owns lifecycle integration. This handoff does not mark the registry ready.

## Design and dimensions

An original damaged derivative of the accepted [Sable source](../car_sable_a.md), not a
replacement live car. The long bonnet, short separate boot, plum body and coral bonnet
inset preserve Sable identity. Broad charcoal regions, a depressed bonnet, buckled boot,
shallow roof crush, large angular glazing remnants, a sagging rear-left door skin and
front bumper communicate a wreck without fine grime. The left mirror is absent. The
remaining wheel silhouettes are scorched and vertically compressed with the whole body;
they are joined static geometry, not wheel components. No fire, smoke, embers, occupants,
interior, rig, animated doors, sockets or vehicle physics are supplied.

The former glass panes are opaque near-black aperture backings with a few closed solid
triangular remnants, deliberately avoiding a visible/modelled cabin. All former seats,
dashboard, cabin floor, hinges, steering/spin empties and interaction markers are removed.
Broad bevels and continuous shading follow Petrol & Coral. Citywide use follows the
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md); it adds no yard
placement, routes, district-specific markings or new gameplay.

- Godot local X width **1.933080 m**, Y height **1.339200 m**, Z length **4.282000 m**.
- AABB min **(-0.966539, 0, -2.145000)**, max **(0.966541, 1.339200, 2.137000)** m.
- The live horizontal footprint is retained within **0.002 m**; the tiny width change
  from static-wheel simplification is under **0.0001 m**. Height drops from 1.4400 m
  to 1.3392 m (**0.1008 m**), while every tyre is regrounded to exactly zero.
- Origin remains the live ground-centred (0,0,0), without translation or corrective
  scale. Blender +Y front/+Z up maps once to Godot -Z front/+Y up. All export objects
  have identity translation/rotation and unit scale; scene units are metres.
- Damage depths are provisional authored choices: bonnet depression up to 0.24 m,
  boot/roof depression up to 0.13 m, rear door droop up to 0.16 m before the 0.93
  vertical stance factor. The raised buckled bonnet sheet clears the supporting body.
  These values do not establish physics or handling changes.

## Source, export and materials

| Role | Path / contract |
| --- | --- |
| Accepted input (unchanged) | `art/source/models/vehicles/car_sable_a/car_sable_a.blend` |
| Editable derivative | `art/source/models/vehicles/vehicle_wrecks_01/vehicle_wrecks_01.blend` |
| Collection / root / mesh | `export_vehicle_wrecks_01` / `VehicleWrecks01` / `VehicleWrecks01_Mesh` |
| Linked export | `art/models/vehicles/vehicle_wrecks_01/vehicle_wrecks_01.glb` + `.glb.import` |
| Saved prefab | `scenes/prefabs/city_cars/vehicle_wrecks_01.tscn` |
| Reproduction/check tools | `tools/asset_production/vehicle_wrecks_01/` |

The supervisor explicitly authorized the family brief's vehicles art paths and city_cars
prefab path in place of the common brief's generic environment paths. `author.py` opens
only the accepted input and saves only the separate derivative. Damage is authored in
Blender, with original part names retained as vertex groups for source discoverability.
The non-export studio and 1 m reference cube-empty remain outside the named collection.
No downloaded, purchased, real-brand, image-to-mesh or runtime-generated geometry.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. `export.py`
loads `tools/assets/blender/export_settings.json`, explicitly selects the wreck collection
and disables skins/animations. All authoring modifiers are applied. Export has one mesh,
eight opaque Principled surfaces, back-face culling, no emission, textures or embedded
images. Surface order:

1. `wreck_sable_plum` — surviving plum paint.
2. `wreck_charcoal` — broad burnt metal and trim.
3. `wreck_sable_coral` — surviving inset/tail-lamp color.
4. `wreck_dead_lamp` — unlit, dulled headlamp lenses.
5. `wreck_scorched_rubber` — flattened static tyre shapes.
6. `wreck_exposed_metal` — dull hubs.
7. `wreck_glass_void` — sealed near-black aperture backing.
8. `wreck_glass_remnant` — large angular blue-green shards.

Exact linear PBR values are in [validation.json](vehicle_wrecks_01-evidence/validation.json).
No separate materials/textures are needed. Default per-asset Godot generated LODs remain
enabled; their population/device appearance is not accepted by this handoff.

## Prefab and collision

The saved prefab instances the GLB at **`Visuals/Model` with identity transform**, with
no editable-child material overrides, embedded render geometry or runtime script.
`Collision/WreckBody/Shape` is the sole collider: a dimension-authored **1.78 × 1.30 ×
4.26 m BoxShape3D**, centred at **(0, 0.65, -0.004)** m. Static-world layer 1 / mask 0.
Its ground is zero; it follows the main body width/length. Rounded corners and low bonnet
are intentionally simplified by one continuous envelope; tyres overhang about 0.077 m
per side, and the roof is about 0.039 m above it. It has no separate wheel/door snag
colliders. This is a blocking wreck, not a walkable platform or dynamic rigid body.

Prefab UID: `uid://cirqey8gkmtan`; model import UID: `uid://de5l6y2f12pee`.
The saved scene header, external GLB dependency and all six authored nodes have explicit
UIDs/unique IDs, verified against the import UID and saved declarations. Two headless
editor-mode load/pack/save/reload cycles are byte-identical after normalization, retaining
all existing scene/node identities. A separate read-only runtime process reproduced the
same prefab hash and checked the serialized identities. Five actual
PhysicsDirectSpaceState3D capsule queries (r=0.35 m, h=1.8 m) passed: body and
front/rear diagonal corners block, side/rear bypasses clear. These are bounded envelope
queries, **not** ActorMotion movement, driving, live-to-wreck swap or multiplayer tests.

M1-B3.1 should instantiate this saved prefab at the live visual origin and owns stopping
commands, retiring the live collider, authoritative lifecycle/retention and dependent
collision-state ordering. No automatic swap or state writer is introduced here.

## Evidence and measured validation

[Hero](vehicle_wrecks_01-evidence/hero.png) · [Side](vehicle_wrecks_01-evidence/side.png) ·
[Bonnet/glass detail](vehicle_wrecks_01-evidence/detail.png) ·
[47 m / 42° overhead](vehicle_wrecks_01-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU renders, 32 samples, AgX, **1280×720**, with
broad area lighting and neutral slate ground. The overhead is vertical-down perspective,
47 m high, vertical FOV 42°, north/+Y at image top; the other three are inspection views.
`finalize.py` strips alpha/metadata and drops the lowest two RGB bits, then uses PNG deflate 9
for lean evidence without cropping or resizing. This affects review PNGs only.

Producer visually inspected all four views. The first pass was too pristine; the final
pass darkens most bonnet/boot/roof metal and preserves fewer paint regions. A coplanar
bonnet intersection was corrected, and static-wheel reduction keeps the triangle budget.
At gameplay scale, the long three-box silhouette, coral bonnet remnant and broken glazing
remain visible. Engine lighting/populated-city readability still requires art review.

| Check | Final result |
| --- | --- |
| Blender / exported vertices | **4,974 / 7,259** |
| Triangles | **9,768**, below live **11,116** (1,348 fewer) |
| Meshes / material surfaces | **1 / 8** |
| Degenerate faces / triangles | **0 / 0** |
| Non-manifold edges | **0** |
| Maximum source / export normal length error | **3.092e-7 / 1.290e-7** |
| Source-to-GLB AABB agreement | Within **0.00001 m** |
| Fresh saved-source re-export | **Byte-identical** |
| Pinned headless import / runtime load | Exit 0; **no ERROR/SCRIPT ERROR lines** |
| Prefab roundtrip / capsule probes | **2 stable cycles / 5 passing expectations** |
| Added GDScript format/lint | gdstyle 0.3.0: **passes, zero warnings** |

Final source: **410,116 bytes**, SHA-256
`175bf654f064639578cb881584c4246a27e8d79fa5482edcb202bf46224ccaf3`.
Final GLB: **298,748 bytes**, SHA-256
`43581a31648290374cd81e8b6bb5325ef0fc8ba8367e3a8735bed13d399997a3`.
Final prefab SHA-256:
`38b34405d400286171f18cf30f9c0240d7b5ed655efb06d52b4f19cf1fe75fac`.
These are copied from the final validation receipt. The
[producer manifest](vehicle_wrecks_01-evidence/manifest.json) hashes all produced payloads
except itself. [Final log](vehicle_wrecks_01-evidence/final.log) records concise check and
repair history. Live input/source export fingerprints are retained in validation.json;
neither live file was changed.

### Review round 1 - serialized dependency identity repair

The P2 finding was confirmed: the original runtime-mode saver omitted the GLB dependency
UID despite a valid import/cache identity. The new serialized-identity assertion rejected
the original prefab in a negative regression run (exit 1), specifically for the missing
external UID and imported-UID mismatch. The harness now follows the accepted Latch pattern:
only `--editor -- --normalize` may save, and runtime checks do not rewrite the scene.
Godot normalized the dependency UID and removed the redundant `type="Node3D"` from the
linked Model declaration; scene UID, all six node IDs, transforms and collision are unchanged.

The saved-source Blender validator and byte-identical scratch export were rerun; source,
GLB and all four reviewed PNGs are unchanged. No authoring or rendering rerun was needed
for this serialization-only fix. Finalization rechecked 1280x720 lean render payloads and
refreshed the receipt/manifest. Two stable save cycles, separate-process runtime checks,
five capsule expectations and pinned gdstyle checks pass. Independent re-review is pending.

Editor-mode normalization exits 0 and passes assertions, but the same editor-harness
shutdown limitation documented for Latch remains: RID/ObjectDB leak diagnostics, plus a
scan-aborted warning in the Sable run. This is **not** a clean editor exit claim. The
standalone imports and separate read-only runtime checks exit 0 with no ERROR/SCRIPT ERROR
lines. The addon also warns that 4.8 is newer than its tested engine. No diagnostics were
suppressed, no live editor was touched, and gameplay/device acceptance remains pending.

## Exact reproduction

From repository root in Git Bash, with the pinned mise tools and Python Pillow installed:

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
TOOLS=tools/asset_production/vehicle_wrecks_01
SOURCE=art/source/models/vehicles/vehicle_wrecks_01/vehicle_wrecks_01.blend

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/author.py"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/validate.py"
# Optional standalone saved-source export to scratch (validator also does this):
timeout 180 "$BLENDER" -noaudio --background --factory-startup "$SOURCE" --threads 4 \
  --python-exit-code 1 --python "$TOOLS/export.py" -- C:/tmp/ft/assets/vehicle_wrecks_01/reexport

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

`author.py` rebuilds geometry and renders from the accepted source. `validate.py` instead
reads the saved derivative and performs a fresh export into scratch. On an intentional
source revision, update the handoff's fingerprints from the new validation receipt before
running `finalize.py` last. Raw retries/intermediate exports stay under
`C:/tmp/ft/assets/vehicle_wrecks_01/`, never in the repository. No live Blender/Godot session
was touched. Windowed editor tools are unavailable by task contract, so the prefab was
text-authored and normalized with the pinned headless engine. A headless import is not
proof that any separately open editor scene is synchronized. `production_checks.py` was
not run, per owner decision 52.

## Remaining acceptance

- Independent technical re-review of the round-1 serialized-identity repair; the initial
  review accepted the bounded visual/source/export observations.
- M1-B3.1 integration: actual same-pose body swap, collision teardown/installation,
  authoritative retention, chain behavior, and late-join/lifecycle ordering.
- Production ActorMotion and car movement/query checks against the installed wreck;
  separate-process authoritative/predicted multiplayer checks where relevant.
- Saved world placement/clearances and gameplay-camera readability under actual city
  lighting, including actors and effects; no world scene was changed.
- Generated LOD, repeated-wreck draw cost, packaged-platform and sustained Deck evidence.

No unproduced family member is a pending item of this delivery; the registry owns family
progress. No shared tracker, catalogue, TODO, live car source/export or unrelated historical
receipt was changed.
