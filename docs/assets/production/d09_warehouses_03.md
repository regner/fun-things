# d09_warehouses.03 — Loading-face annex

**Production source, export, linked prefab and bounded checks delivered; independent
review and world/gameplay/device acceptance pending.** Commissioned by Regner under
[the commission](commission.md) and the current asset-common lane brief, superseding
the older concept-only restriction. Producer: commissioned isolated asset-production
worker on `lane/a-whouse`. Accepting owners: independent technical/art reviewers and
the world/gameplay owners; this record does not mark those gates accepted.

Original Blender construction; no downloaded geometry, image-to-mesh, real brands,
external textures or runtime mesh generation. References: [family](../d09_warehouses.md),
[East Docks](../../concepts/districts-v1/east-docks.md), approved
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
and the [ridge](d09_warehouses_01.md) / [wide low](d09_warehouses_02.md) siblings.
Both siblings' handoffs, source conventions and renders were inspected; neither was
modified. The annex uses their existing rear attachment contracts.

## Design and dimensions

A **two-bay loading component**, with a short blue lean-to roof, two closed industrial
shutters, sparse amber headers/jamb accents, a side personnel door, two high opaque
side panes, restrained gutters and a rear wall-return/flashing. Its 72 m² footprint
is one twelfth of either warehouse's 864 m², not a third full warehouse. The roof has
one broad bay seam and no rooftop equipment. The larger siblings retain the long-roof
district identity; this component adds a compact loading face without duplicating a
whole building per plot.

No interiors, through opening, indoor freight handling, opening doors, loading deck,
ramp, crane, real light, freight artwork or new interaction is included. Closed lips
are flush facade details, not walkable platforms. Generous aprons/turns remain a world
placement requirement; these dimensions do not allocate any district plot.

Dimensions are **provisional authored values**, consistent with the sibling contracts,
not measurements inferred from a concept image or an approved district arrangement.

| Contract | Metres in Godot local coordinates |
| --- | --- |
| Whole visual size X / Y / Z | **12.360 / 5.750 / 6.510** |
| Visual AABB minimum | **(-6.180, 0, -3.350)** |
| Visual AABB maximum | **(6.180, 5.750, 3.160)** |
| Ground shoe / solid collision footprint | **12.000 × 6.000** |
| Ground shoe height | 0.360 |
| Solid wall collision height | 5.000 |
| Blue roof front / rear top | 5.150 / 5.650 |
| Highest rear flashing | 5.750; below the 5.800 family limit |
| Roof fall towards loading front | 0.500 over 6.420 (~4.45°) |
| Loading bay pitch / centres X | 6.000 / -3.000, +3.000 |
| Closed shutter face | **3.600 × 4.200**, bottom Y=0.300 |
| Nominal loading-front / rear bearing datum | Z=-3.000 / +3.000 |
| Ordinary front / rear steel wall faces | Z=±2.860 |
| Decorative side / front overhang | 0.180 / 0.350 beyond ground shoe |
| Rear flashing and side-return extension | 0.160 beyond rear datum |
| Envelope / ground validation tolerance | ±0.001 |

Ground-centred root and mesh pivots are (0,0,0). Blender +Y loading front maps once
to Godot -Z; Blender +Z maps to Godot +Y. Metres, unit scale, applied rotation/scale;
no corrective transform on the linked `Visuals/Model`.

### Sibling attachment and saved fit references

Use the existing **blank rear central two bays, X=-6 to +6** on either sibling.
With the warehouse at identity, rotate the **annex prefab root** 180° around +Y:

| Warehouse | Warehouse rear datum | Annex root position | Saved reference scene |
| --- | --- | --- | --- |
| `.01` long ridge | (0,0,+9) | **(0,0,+12)** | `d09_warehouses_03_fit_ridge.tscn` |
| `.02` wide low | (0,0,+12) | **(0,0,+15)** | `d09_warehouses_03_fit_low.tscn` |

The annex's rear local (0,0,+3) then meets the warehouse bearing datum; its loading
face points outward in warehouse +Z. The two body boxes **touch with zero gap**.
Rear flashing/side returns extend 0.16 m inward, bridging the siblings' 0.14 m inset
steel faces with 0.02 m overlap. Upper attachment is 5.75 m, 0.05 m below the family
ceiling and below both eaves. The visible regular warehouse piers are not removed.
This is an exterior **closed butt attachment**, never an entrance or through passage.
No socket or dynamic attachment API is invented.

The two saved reference scenes compose the actual, unchanged sibling and annex
prefabs. They contain no new meshes or gameplay systems and are not district/world
placements. Their transforms are authored in the scene files, not assembled at
runtime. They also provide reproducible joint/shoulder physics checks.

## Source, exports and materials

- Source: `art/source/models/environment/d09_warehouses_03/d09_warehouses_03.blend`.
- Collection: `export_d09_warehouses_03`.
- Root / mesh: `D09Warehouses03` / `D09Warehouses03_Mesh`.
- Export: `art/models/environment/d09_warehouses_03/d09_warehouses_03.glb` and `.import`.
- Component prefab: `scenes/prefabs/environment/d09_warehouses_03.tscn`.
- Fit references: the two named `.tscn` files in the same prefab directory.
- Author/export/validate/check/receipt scripts: `tools/asset_production/d09_warehouses_03/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. The exporter
loads the existing shared `tools/assets/blender/export_settings.json`, selects only
the named collection, and disables skins/animations. The source retains editable
geometry and `author.py` retains the parametric construction. Applied static bevels
and weighted normals soften broad manufactured forms. Independent closed subparts
intentionally intersect at roof/wall/fitting joints; no open boundaries are used.
Studio camera, floor and lighting remain outside export.

One mesh with seven opaque, back-culled Principled surfaces, in **this GLB's** order:

1. `dock_base_slate` — shoe and flush thresholds.
2. `dock_wall_steel` — quiet steel wall fields and returns.
3. `dock_roof_blue` — short lean-to and its single bay seam.
4. `dock_frame_navy` — flashing, gutter, recesses and shutter folds.
5. `dock_shutter_teal` — closed loading/personnel doors.
6. `dock_loading_amber` — sparse headers/jamb accents, not emission.
7. `dock_glazing_opaque` — high side panes.

All seven names and exported PBR values are **identical to both siblings**, checked
against their actual committed GLBs. Order differs because this component has no
rooflights; no cross-asset index-based override contract is introduced. Exact values
are in validation.json. No textures, embedded images, transparent glazing, material
overrides, rigs, clips, opening/destruction states or sockets. Automatic Godot mesh
LOD and shadow-mesh generation retain engine defaults; transition appearance and
repeated cost remain unaccepted. No numerical triangle budget was supplied.

## Prefab and collision

`Visuals/Model` is an identity-transform imported GLB instance, not embedded mesh
geometry. `Collision/Body/Shell` is a single BoxShape3D directly under StaticBody3D:
size **(12,5,6)**, centre **(0,2.5,0)**, static-world layer **1**, mask **0**. The shoe
is the exact collision footprint; inset steel and tiny fittings do not create snag
colliders. High rear wall/roof/flashing above 5 m and decorative overhangs are
visual-only. No rooftop or interior traversal is provided.

Prefab UID **`uid://p7evfgl6vs8o`**; GLB UID **`uid://c77gv06wsgeg1`**. Fit reference
UIDs: ridge **`uid://que2aa44xdy4`**, low **`uid://d07yokjjgftgp`**. All three owned
scenes preserve complete bytes, UIDs and named node identities across **two
save/reload roundtrips each**. Text authoring followed by pinned headless PackedScene /
ResourceSaver normalization is the brief's authorized fallback: the windowed editor
is unavailable and live owner sessions are excluded. No live-editor synchronization
or graphical playtest is claimed. Script `.gd.uid` and model `.import` are included;
scene UIDs reside in their headers.

## Evidence and validation

[Hero](d09_warehouses_03-evidence/hero.png) ·
[side](d09_warehouses_03-evidence/side.png) ·
[loading detail](d09_warehouses_03-evidence/loading_detail.png) ·
[47 m / 42° overhead](d09_warehouses_03-evidence/overhead_47m_42deg.png).

Isolated **Blender Cycles CPU, 32 samples, AgX** renders; not Godot captures.
Hero/side/detail are 1152×648; overhead is **1280×720**, vertical-down perspective,
47 m height, 42° **vertical** FOV, Blender +Y at image top. The standing lean-evidence
720-pixel maximum supersedes the old 800-pixel requirement. PNGs use maximum
compression and evidence-only six-bit/channel hero / seven-bit/channel other views;
runtime material values and GLB are unchanged.

Producer inspected all four final views. The compact two-panel roof reads cleanly
at the gameplay camera; shutters and amber trim are subordinate facade details, not
essential overhead signage. Side/detail views show the shared industrial vocabulary.
Initial side framing cropped the silhouette; the camera was widened and the final
view rechecked. The hero was similarly given more margin. No gameplay dimensions
changed. Studio lighting does not establish a world-lighting choice.

Measured source / actual GLB accessors / imported prefab:

- **4,896 source vertices; 9,588 triangles; 5,810 exported vertices** with surface splits.
- **1 mesh, 7 surfaces**; **0 degenerate source faces / GLB triangles / non-manifold edges**.
- Maximum normal-length error: source **1.64e-7**, GLB **1.38e-7** (rounded up).
- Source/GLB/Godot AABBs match the literal expected envelope within 0.001 m; ground zero.
- Fresh saved-source reexport **byte-identical**: **250,340 bytes**, SHA-256
  `f13df5da5924c16b88a84642c0a00dc63b6dae846a36233cfc422481e6efd3de`.
- Component: **8 shape queries**, **6 motion casts**, front ray hit **(-3,1,-3)**.
- Both saved attachments: **5 seam/shoulder queries and 3 motion casts each**; zero
  collider gap, 5.75 m top, 0.02 m return past steel. Concave shoulder outside is
  clear; adjacent warehouse wall and annex side block; outer actor/car apron sweeps clear.
- Total bounded physics evidence: **18 shape queries, 12 motion casts, 1 ray**.
- Actor envelope **r=0.35 / h=1.8**; car-sized box **1.8×1.5×4.4**.
- All dependencies load, imported materials are opaque/back-culled, and all three
  scenes pass two byte-stable roundtrips. Fresh runtime exits 0 without errors/warnings.

These are public PhysicsDirectSpaceState3D queries against saved prefabs, **not**
production ActorMotion/car-controller movement, turning, multiplayer transport,
admission or prediction tests. Canonical production checks **pass every layer**:
pinned engine, owned-script compilation/style/formatting, **17 Python tests**,
**149 GUT tests / 6,768 assertions**, and expected rejection of the intentional
negative control. No known-failure exemption was needed.

See [validation.json](d09_warehouses_03-evidence/validation.json), lean
[final.log](d09_warehouses_03-evidence/final.log), and SHA-256
[manifest](d09_warehouses_03-evidence/manifest.json). The manifest hashes every produced
payload except itself; scratch exports/retries/raw logs remain outside the repository.

Diagnostics: Blender's version-only query printed the known 23-byte shutdown
allocation warning; authoring/validation exited 0 without it. Authoring emitted the
pin's forward-looking `use_nodes` deprecations. Headless editor import emits only the
existing toolkit Godot-4.8 compatibility warning. Initial owned lint warnings were
resolved by splitting the attachment checks; final lint/runtime/canonical checks
are clean. No warnings were broadly suppressed.

## Exact reproduction

Run from repository root in Git Bash. Keep timeouts, audio environment, factory
startup, thread count and error-exit flags. `record.py` requires Pillow. Use a fresh
empty canonical-check output directory.

```sh
NID=d09_warehouses_03
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

The validator opens the saved source and reexports to `$OUT/reexport`. For an
independent standalone export:

```sh
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 art/source/models/environment/$NID/$NID.blend --python tools/asset_production/$NID/export.py -- "$OUT/reexport"
```

## Remaining acceptance

Independent technical/art review; final district dimensions and saved world placement;
apron turning/route clearance; actual engine camera/material/LOD views; production
actor/car movement; relevant multiplayer collision behavior; exported platforms and
sustained Deck/performance checks remain **pending**. Bounded sibling fit is checked,
not accepted whole-city placement. No sibling, shared brief/register/progress file,
road generation, district boundary, world scene or gameplay implementation changed.
