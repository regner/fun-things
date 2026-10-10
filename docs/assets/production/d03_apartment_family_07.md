# d03_apartment_family.07 — Finished end bay / wall closure

10 October 2026. **Original source, linked export and bounded prefab checks delivered;
independent review and world acceptance pending.** Commissioned under the
[register commission](commission.md), superseding the concept-only restriction in the
[family brief](../d03_apartment_family.md). Producer: commissioned implementation worker.
Accepting art/technical reviewer: unassigned. No district placement, shared register,
road, gameplay or sibling asset files changed.

## Design and dimensions

A reversible **exposed-end wall closure**, not another complete apartment bay. It caps
the blank twelve-metre-deep end of the delivered [straight bay](d03_apartment_family_05.md)
or an unused connector on the [corner set](d03_apartment_family_06.md). Quiet blue-grey
render, four teal blind aprons at the family's 3 m domestic rhythm, pale shallow
pilasters/sills and two restrained coral terminal arrises make the exposed end read
as finished construction. One continuous U-shaped pale floor ribbon returns to the
adjacent bay. The broad upper fields are intentionally blank, not missing glazing.
No interior, door, window opening, roof traversal or destruction state is implied.

Original Blender construction only: no downloads, third-party geometry, textures,
brands, image-to-mesh or runtime-generated visible meshes. References inspected:
[Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03), and
both delivered sibling interfaces. District area/greybox footprints remain context,
not an allocation or approved replacement envelope.

### Provisional interface — metres, Godot local axes

The family keeps its **6 m bay pitch, 12 m building depth and 3.2 m storey pitch**.
The closure's 0.24 m structural thickness is a provisional authored value permitted
by the standing production brief, not a measurement from concept imagery. This is
an added end layer, not a replacement bay or a reason to stretch the shared windows.

| Interface | Value |
| --- | --- |
| Origin | Ground-centred structural slab footprint, (0, 0, 0) |
| Core / collider AABB | Min (-0.12, 0, -6); max (0.12, 3.2, 6) |
| Core size X/Y/Z | 0.24 × 3.2 × 12 m |
| Whole visual AABB | Min (-0.12, 0, -6.10); max (0.22, 3.2, 6.10) |
| Whole visual size X/Y/Z | 0.34 × 3.2 × 12.20 m |
| Mating face | X = -0.12; nothing projects behind it |
| Finished exposed wall | X = +0.12; shallow trim projects at most 0.10 m |
| North / south structural ends | Z = -6 / +6 |
| Bottom / top stack datum | Y = 0 / 3.2; no bevel gaps |
| Pale floor ribbon | Y = 0.04…0.20; returns project 0.10 m at north/south |
| Blind apron centres | Z = -4.5, -1.5, +1.5, +4.5 |
| Blind apron bounds | 2.30 m long; Y = 0.35…1.01 |
| Pale pilasters | Z = -3, 0, +3; 0.16 m wide; Y = 0.35…2.74 |
| Coral terminal strips | 0.24 m wide; Y = 0.24…3.12 |
| Dimensional / axis tolerance | ±0.001 m / ±0.00001 m |

The blank rear is a mating surface and must be buried against the building. The
slab's entire top is a storey/roof attachment plane, not a finished roof. Closed
mating faces are retained for manifold per-component geometry. No sockets: these
static numeric planes are the assembly interface. Blender +Z maps to Godot +Y,
Blender +Y to Godot -Z; this wall's exposed direction is deliberately **+X**.

### Placement relative to existing components

The following coordinates assume the receiving component remains at the origin:

| Receiving face | Closure origin | Rotation about Godot +Y |
| --- | --- | --- |
| Straight bay east end, X = 3 | (3.12, 0, 0) | 0° |
| Straight bay west end, X = -3 | (-3.12, 0, 0) | 180° |
| Outside corner unused east connector, X = 6 | (6.12, 0, 0) | 0° |
| Outside corner unused south connector, Z = 6 | (0, 0, 6.12) | -90° |
| Inside corner unused east connector, X = 9 | (9.12, 0, -3) | 0° |
| Inside corner unused south connector, Z = 9 | (-3, 0, 9.12) | -90° |
| Next stacked closure | Add (0, 3.2, 0) to the lower closure | Same rotation |

Rotate rigidly; no negative scale, mirroring or corrective model transform is needed.
A single straight bay with both closures has structural end planes X = ±3.24 and
outer decorative planes X = ±3.34. The closure **adds 0.24 m per finished end** to
the structural run length. Roof end coverage and plot clearances must include that
extension. It does not change the interior bay pitch or front/rear wall datums.
The ribbon tips end flush at the mating face and meet the sibling's same-height,
same-depth ribbon. Do not put a closure between connected bays or across an open
court mouth. It finishes an existing solid run; it must not create a new court wall.

## Source, export and materials

- Source: `art/source/models/environment/d03_apartment_family_07/d03_apartment_family_07.blend`.
- Export collection: `export_d03_apartment_family_07`.
- Root / mesh: `D03ApartmentFamily07` / `D03ApartmentFamily07_Mesh`.
- Export: `art/models/environment/d03_apartment_family_07/d03_apartment_family_07.glb`
  with committed `.import` metadata.
- Prefab: `scenes/prefabs/environment/d03_apartment_family_07.tscn`.
- Tools: `tools/asset_production/d03_apartment_family_07/` (`author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` with its UID, and `record.py`).

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Explicit export
consumes `tools/assets/blender/export_settings.json`, selecting only the named
collection, with animation/skin export disabled. Metre units, applied transforms,
identity root and mesh; no corrective scale or double axis conversion. The original
closed slab, extruded ribbon and beveled trim solids are joined into one static mesh.
Studio lights, camera, ground and hidden one-metre reference stay outside the export.

Four opaque, back-culled, texture-free Principled surfaces in export order:

| Slot | Material | sRGB swatch | Roughness / metallic |
| --- | --- | --- | --- |
| 0 | `terrace_bluegrey_render` | `#829398` | 0.76 / 0 |
| 1 | `terrace_pale_frame` | `#C5CABF` | 0.53 / 0 |
| 2 | `terrace_teal_spandrel` | `#31656A` | 0.65 / 0 |
| 3 | `terrace_coral_corner` | `#FF725D` | 0.62 / 0 |

The engine check compares all four imported materials' actual color, roughness and
metallic values to the delivered corner palette by name. There is deliberately no
glass surface. No textures, embedded images, external material dependencies, rigs,
clips, inherited variants or explicit LODs. Default automatic Godot mesh LOD generation
is retained; its appearance and repeated-placement cost are not performance-accepted.

## Evidence and measured validation

[Hero](d03_apartment_family_07-evidence/hero.png) ·
[reverse / mating side](d03_apartment_family_07-evidence/side.png) ·
[terminal detail](d03_apartment_family_07-evidence/closure_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_07-evidence/overhead_47m_42deg.png).

All four renders were inspected by the producer. Isolated Blender Cycles CPU,
32 samples, AgX, 1280 × 720, PNG compression 95, dithering disabled; every PNG is
below 273 KB. The overhead is vertical-down, north-up perspective, 47 m above ground
with 42° **vertical FOV**, using the standing 720 px evidence-height cap. The thin
continuous end layer reads as a quiet line; its face decoration is not essential
overhead gameplay information. These are isolated component renders, not a finished
roof composition, Godot captures or proof of court-route/actor visibility in placement.

[validation.json](d03_apartment_family_07-evidence/validation.json) retains measured
source, actual binary GLB and engine results. [manifest.json](d03_apartment_family_07-evidence/manifest.json)
hashes every delivered payload except itself. [Final checks](d03_apartment_family_07-evidence/final-checks.log)
distinguish successful assertions from tool diagnostics.

- **1,444 triangles; 752 source vertices; 1,008 exported vertices; one mesh / four surfaces.**
- Zero non-manifold edges, degenerate source faces or actual GLB triangles.
- Finite vertices, unit source corner/exported normals, identity transforms, literal
  core connector corners, dimensions, ground datum and binary-accessor axis bounds pass.
- Fresh re-export from the final saved source is byte-identical to the delivered GLB.
- Final source: **125749 bytes**, SHA-256
  `960644f294584dc0b22ea3ca789bcb2cd9fce5d347f68ab81910663024e1fa6e`.
- Final GLB: **44908 bytes**, SHA-256
  `463c81eeacbfe64ce4ff29d830babb1c7228800acca0b14246043da7dd4f9e51`.

Counts describe disjoint closed trim solids joined into one mesh, not a boolean union.
Shallow trim/core intersections are intentional; the single bent ribbon avoids
coplanar overlapping corner tops.

### Prefab, collision and engine checks

Godot **4.8.dev7.official.c971f93e7** final headless import and runtime checks exit 0
with no ERROR/SCRIPT ERROR lines or missing dependencies. The wrapper was authored
as text because live editor sessions are prohibited and the windowed editor is
unavailable, then loaded, packed, saved and reloaded in the pinned headless editor.
The second save is byte-stable, preserving UIDs, node identities and linkage.
`Visuals/Model` instances the GLB at identity; no render mesh or material override is
copied into the scene. The prefab's UID is `uid://bkg20p3m0vby4`; the GLB's UID is
`uid://dcrbd23apj046`.

`Collision/Body/Core` is the only collider: **BoxShape3D (0.24, 3.2, 12)** centred at
(0, 1.6, 0), owned by StaticBody3D layer 1 / mask 0. It matches the entire closed
slab, with no gap at ground, the mating plane or stack boundaries. Shallow aprons,
pilasters, arrises and the floor ribbon do not add snagging colliders. The slab is
solid even before assembly; the existing bay continues to own its own closed core.

Retained bounded checks use real imported resources and production APIs:

- Seven actor-capsule solid/clear queries, r = 0.35 m / h = 1.8 m, covering the wall,
  both tips and four clear setbacks. An aim ray hits the exposed wall at X = 0.12.
- Five assembly rays check both front/rear straight-bay seams, a stacked closure,
  the rotated west closure, and its north seam. Four more rays check the actual
  outside/inside corner east-connector seams. All expected wall datums match.
- Eight **production `ActorMotion.step`** runs, 60 ticks each: exposed-side stop,
  mating-side stop, north-tip stop and clear east bypass in AUTHORITY and REPLAY.
  Both modes produce identical positions: side stops X = ±0.47005245 m, north stop
  Z = -6.35025740 m, bypass Z ≈ -2.99999356 m.
- Two car-sized box sweeps, 1.9 × 1.5 × 4.3 m: the end wall blocks and the south
  bypass stays clear. These are shape sweeps, not production driving/turning tests.

Tool limitations: editor-mode normalization exits 0 and proves byte-stability but
emits headless editor RID/ObjectDB shutdown-leak diagnostics, also observed in both
sibling handoffs. Final import/runtime checks are clean; no errors are suppressed.
The addon warns that this pinned engine version is untested. An initial combined-shell
import invocation returned timeout 124 with runtime-style output and a static-string
shutdown error, without producing import metadata or the requested scratch log.
Resolving the pinned executable into an explicit shell variable and invoking import
separately succeeded. The malformed attempt is not counted as import evidence.
Blender's `use_nodes` notices concern Blender 6, not the required pin.

## Exact reproduction

From repository root in Git Bash. Never attach to a live Blender or Godot session.
Raw logs, retries and fresh comparison exports belong in the scratch directory.

```sh
NID=d03_apartment_family_07
TOOLS=tools/asset_production/$NID
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
mkdir -p C:/tmp/ft/assets/$NID
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/author.py"
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . --script "$TOOLS/check_prefab.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "$TOOLS/check_prefab.gd"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/validate.py"
mise exec -- gdstyle fmt --check "$TOOLS/check_prefab.gd"
mise exec -- gdstyle --max-line-length 100 --max-warnings 0 "$TOOLS/check_prefab.gd"
python "$TOOLS/record.py" --check
```

`validate.py` opens the saved source, calls `export.py` into scratch and compares the
entire GLB byte-for-byte; it also requires the runtime/normalization receipt. To export
manually, open the saved `.blend` in the same bounded Blender CLI and run `export.py --
C:/tmp/ft/assets/d03_apartment_family_07/reexport`. A new `author.py` run is not promised
to serialize the `.blend` identically; re-export from the committed source is the
strict comparison. After intentional changes, refresh validation/handoff receipts,
run the final pinned import, then regenerate the manifest with `record.py` without
`--check` last. Its check verifies all payloads, handoff receipt hashes/byte counts and
the normalized prefab hash. No `production_checks.py` was run (owner decision 52).

## Remaining acceptance

- Independent art/technical review of the closure and its provisional interface.
- World-integrator approval of plot fit, added end thickness, storey counts, roof
  coverage, open court mouths/cross-links and actor sightlines in saved placements.
- Actual in-engine visual/gameplay-camera review, production vehicle movement,
  contextual authoritative network/transport behavior and packaged dependency checks.
- Repeated-placement draw-call, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, target-device or full gameplay acceptance is claimed. The
registry tracks other family records. Neither earlier sibling handoff had a stale
pending item for this delivery, so no sibling doc/manifest edits were necessary.
