# d09_warehouses.01 — Long ridge warehouse

**Production source, export, linked prefab and bounded checks delivered; independent
review and world/gameplay/device acceptance pending.** Commissioned by Regner under
[the production commission](commission.md) and the current asset-common lane brief.
The older concept-only restriction is superseded by that explicit commission.

Producer: commissioned isolated asset-production worker, branch `lane/a-whouse`.
Accepting owners: independent technical/art reviewers and the world/gameplay owners;
this document does not mark those gates accepted. Original Blender construction,
no downloaded geometry, image-to-mesh, real brands, external textures or runtime
mesh construction. Reference: [warehouse family](../d09_warehouses.md),
[East Docks concept](../../concepts/districts-v1/east-docks.md), and the approved
[industrial identity](../../concepts/world-v1/stage-03-district-identities/README.md).
No sibling warehouse output existed when this first member was authored.

## Design and dimensions

An eight-bay steel warehouse with one long blue pitched ridge, six closed industrial
shutters, two quiet service bays, a personnel door, sparse amber loading headers,
broad shutter folds, restrained gable vents, gutters and four low opaque rooflights.
The ridge and large uninterrupted blue fields distinguish the docks from Ironreach's
short repair sheds. No indoor freight handling, opening doors, platforms, cranes,
freight graphics, real lights or new interactions are included.

These are **provisional authored dimensions**, not measurements inferred from the
concept image or an approved district arrangement. The warehouse occupies 864 m²
at its ground shoe; this is not an allocation of the 5.03 ha district or a placement
at any saved placeholder. Preserve broad aprons and turns in later layout work.

| Contract | Metres in Godot local coordinates |
| --- | --- |
| Whole visual size, X / Y / Z | **48.760 / 9.265 / 18.980** |
| Visual AABB minimum | **(-24.380, 0, -9.490)** |
| Visual AABB maximum | **(24.380, 9.265, 9.490)** |
| Ground shoe / solid collision footprint | 48.000 × 18.000 |
| Ground shoe height | 0.360 |
| Nominal steel eave / main roof ridge | 6.400 / 9.200 |
| Highest ridge cap | 9.265 |
| Loading shutter face | 3.600 wide × 4.200 high; bottom Y=0.300 |
| Bay pitch | 6.000 along X; eight bays centred -21 through +21 |
| Closed loading-door centres X | -21, -15, -9, -3, +3, +9 |
| Nominal loading face / rear bearing line | Z=-9.000 / +9.000 |
| Ordinary steel wall face | Z=±8.860, under the ground shoe and trim |
| Roof/gutter overhang beyond ground shoe | 0.380 at gables; 0.490 at long sides |
| Envelope / datum validation tolerance | ±0.001 |

Ground-centred pivot and root/mesh origins are (0,0,0). The ridge runs along X;
loading-front Blender +Y maps once to Godot -Z, and Blender +Z maps to Godot +Y.
Metres, unit scale, applied rotation/scale, no corrective wrapper transforms.

### Family seam for subsequent members

Use the 6 m wall/loading bay rhythm, 3.6 × 4.2 m closed shutter design and the seven
named materials below as the shared visual vocabulary for `.02` and `.03`; no
private copy of a full building per plot is needed. The authoring recipe keeps
wall, roof, shutter and trim construction explicit before joining the export mesh.
This member is one reusable assembly, not a runtime procedural building generator.

The rear central two bays, X=-6 to +6, are blank and have no doors, vents or windows.
The **rear ground bearing datum is (0,0,+9)** with outward +Z and upward +Y; the
actual steel face is Z=8.86. A future annex may use a short wall-return/flashing
within the 0.14 m datum-to-steel allowance. Keep its upper attachment below Y=5.8
so it remains below the lowest eave/gutter (approximately Y=6.29). The existing
6 m piers remain visible outside an attached component. This is an exterior butt
attachment, **not a through opening**, traversable passage or third warehouse.
No socket or dynamic attachment API is requested or exported. Final annex size and
saved placement remain that member's/world integrator's responsibility.

## Source, exports and materials

- Source: `art/source/models/environment/d09_warehouses_01/d09_warehouses_01.blend`.
- Collection: `export_d09_warehouses_01`.
- Root / child: `D09Warehouses01` / `D09Warehouses01_Mesh`.
- Export: `art/models/environment/d09_warehouses_01/d09_warehouses_01.glb` plus its
  pinned-engine `.import` metadata.
- Prefab: `scenes/prefabs/environment/d09_warehouses_01.tscn`.
- Author/export/validate/check/receipt tools: `tools/asset_production/d09_warehouses_01/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
`export.py` loads `tools/assets/blender/export_settings.json`, restricts export to
the declared collection and disables animation/skins. Studio camera, plane and
lights are outside the collection. Static bevels and weighted normals are applied
before saving. The source retains editable geometry and the script retains the
parametric construction. Independent closed subparts intentionally intersect at
fitting/wall and roof joints; no open mesh boundaries are used.

One mesh, seven opaque, back-culled Principled surfaces, in exported slot order:

1. `dock_base_slate` — neutral continuous ground shoe and thresholds.
2. `dock_wall_steel` — broad quiet steel wall panels.
3. `dock_roof_blue` — blue pitched roof and sparse bay seams.
4. `dock_frame_navy` — ridge, gutters, frame recesses and shutter folds.
5. `dock_glazing_opaque` — four rooflights and two service clerestories.
6. `dock_shutter_teal` — closed loading and personnel doors.
7. `dock_loading_amber` — sparse headers and low jamb accents, not emission.

Exact linear colors, roughness and metallic values are retained in validation.json.
No textures, embedded images, transparent glazing, material overrides, rigs, clips,
opening/destruction states or exported sockets. Default Godot automatic mesh LOD
and shadow-mesh generation remain enabled; their transition appearance/performance
has not been accepted. No numerical production triangle budget was supplied.

## Prefab and collision

`Visuals/Model` is the identity-transform linked GLB instance, not embedded mesh
data. `Collision/Body/Shell` is one direct BoxShape3D under a StaticBody3D, size
**(48,6.4,18)**, centre **(0,3.2,0)**, static-world layer **1**, mask **0**.
The solid ground shoe is the collision footprint; the slightly inset steel panels
and tiny hardware details do not add snag colliders. The cap, gable upper area,
roof, high fittings and gutters are visual-only above the solid eave envelope.
No rooftop traversal or interior exists. The closed loading lips are part of the
solid frontage, not independently walkable loading decks or ramps.

Godot-generated scene UID `uid://dkunpbured7jv`; imported model UID
`uid://ceauhjdjxgbep`. Named node identities and the scene UID survived **two
byte-stable save/reload roundtrips**. The standalone headless saver uses Godot's
ResourceUID/ResourceSaver APIs; a subsequent pinned import registers the saved UID
before a separate fresh-process read-only check. No live editor session was used.

## Evidence and validation

[Hero](d09_warehouses_01-evidence/hero.png) ·
[long loading elevation](d09_warehouses_01-evidence/side.png) ·
[loading detail](d09_warehouses_01-evidence/loading_detail.png) ·
[47 m / 42° overhead](d09_warehouses_01-evidence/overhead_47m_42deg.png).

These are isolated **Blender Cycles CPU, 32 samples, AgX** renders, not engine
captures or movement acceptance. Hero/side/detail are 1152×648; the overhead is
1280×720, vertical-down perspective, 47 m height, 42° **vertical** FOV, Blender +Y
at image top. The owner-mandated lean 720-pixel evidence height supersedes the
older 800-pixel evidence requirement. PNGs use seven-bit/channel evidence-only
color reduction and maximum compression, around 300–400 KB each. Runtime materials
and the GLB are not color-reduced.

Producer inspected all four final views. The long blue ridge and two paired
rooflights remain clear from overhead; loading trim is deliberately subordinate.
The roof fills much of the gameplay frame: sightlines near routes and repeated
warehouse placements need actual camera review. Evidence lighting is not a new
world-lighting choice. A shallow studio-side framing artifact was corrected by
raising that camera; no gameplay dimensions changed during render cleanup.

Measured source / GLB / imported prefab:

- **13,744 source vertices**, **26,920 triangles**.
- **16,470 exported vertices** including material/normal splits.
- **1 mesh, 7 material surfaces**.
- **0 degenerate source faces, 0 degenerate GLB triangles, 0 non-manifold edges**.
- Maximum normal-length error: source **1.72e-7**, GLB **1.22e-7** (rounded up).
- Source, actual GLB accessors and Godot AABBs match the literal expected envelope
  within 0.001 m; ground datum is zero.
- Fresh export from the saved source is **byte-identical**, GLB **695,480 bytes**,
  SHA-256 `ec883db6d672a51b6653036cd95c25bed8cd796d388e6b4df83ce942062f87f1`.
- Eight independent solid/clear physics shape queries passed, including closed
  loading face, rear wall, solid interior, both clear side passages and visual-only roof.
- Six motion casts passed: actor capsule **r=0.35, h=1.8**, front/rear/end blocked
  and side bypass clear; car-sized box **1.8×1.5×4.4**, front blocked and side bypass clear.
- Front physics ray hits the saved body at **(-9,1,-9)**.
- All prefab dependencies load, material opacity/back-culling and collision dimensions
  pass; fresh runtime process exits 0 without ERROR/WARNING diagnostics.

Motion casts use public `PhysicsDirectSpaceState3D` APIs against this saved prefab;
they are not actual ActorMotion/car-controller movement, driving turns, transport,
prediction or network admission tests. Existing full production tests passing does
not expand the asset-specific evidence to those untested cases.

The canonical production checker **passed all layers**: pinned engine, owned-script
compilation/style/formatting, **17 Python tests**, **149 GUT tests / 6,768 assertions**,
and the intentionally failing GUT negative control. No known-failure exemption was
needed. See [validation.json](d09_warehouses_01-evidence/validation.json),
[lean final log](d09_warehouses_01-evidence/final.log) and the SHA-256
[producer manifest](d09_warehouses_01-evidence/manifest.json).

Initial diagnostics: editor-mode custom SceneTree normalization timed out at 180 s
and emitted shutdown errors; it is not a passing check. The proven runtime-mode
save API replaced that attempt. An initial fresh load before reimport could not
resolve the newly saved scene UID; import followed by fresh load passed. Initial
owned lint warnings were corrected. Final normalizer/runtime checks are clean;
headless editor import emits only the existing toolkit Godot-4.8 compatibility
warning. Scratch retries and raw logs are outside the repository.

## Exact reproduction

From the repository root in Git Bash; Blender commands must keep their timeout,
audio environment, factory startup, thread count and error-exit flags. `record.py`
uses Pillow for lean evidence packaging. Use a fresh `checks` output directory.

```sh
NID=d09_warehouses_01
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

`validate.py` opens the saved source and reexports to `$OUT/reexport`. To export
separately without validation:

```sh
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 art/source/models/environment/$NID/$NID.blend --python tools/asset_production/$NID/export.py -- "$OUT/reexport"
```

The source and GLB need not change when only wrapper checks or evidence packaging
are rerun.

## Remaining acceptance

Independent technical/art review; final district dimensions and sibling fit;
saved world placement/apron turn space; actual game-camera occlusion and in-engine
materials/LOD views; production actor/car movement and gameplay queries; relevant
multiplayer collision behavior; exported-platform and sustained Deck/performance
checks remain **pending**. No world placement, shared brief/register/progress file,
road generation, district boundary, gameplay code or sibling asset was modified.
