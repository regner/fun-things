# d03_apartment_family.06 — Inside/outside corner bay set

10 October 2026. **Original source, two linked exports and bounded prefab checks delivered;
independent review and world acceptance pending.** Commissioned under the
[register commission](commission.md), superseding the concept-only restriction in the
[family brief](../d03_apartment_family.md). Producer: commissioned implementation worker.
Accepting art/technical reviewer: unassigned. No shared register, gameplay, district,
road or sibling asset files changed.

## Design and dimensions

Two one-storey Terrace Ward elbows extend the delivered
[straight bay](d03_apartment_family_05.md): a compact square **outside** turn and a
larger **inside** turn with exposed courtyard returns. Broad paired domestic windows,
blue-grey render, pale frames and continuous floor ribbons preserve the family.
Coral aprons and narrow coral arrises mark the shared corners rather than every bay
or roof edge. Teal remains the ordinary spandrel color. Closed window faces, top
mating planes and blank run-connection faces do not imply interiors, roof traversal,
working windows, doors or destruction states.

Original Blender construction only: no downloaded geometry, third-party meshes,
brands, textures, image-to-mesh or runtime-generated visible geometry. References:
[Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03), and
the sibling's delivered numeric interface. The 4.80 ha district and existing greybox
footprints are context, not plot allocations or approved replacement envelopes.

### Provisional family interface — metres, Godot local axes

The existing **6 m bay pitch, 12 m run depth and 3.2 m storey pitch** are preserved.
The two corner footprints below are provisional authored choices allowed by the
standing production brief, not measurements inferred from concept imagery. Use
rigid rotations, repeat counts and setbacks; never stretch windows to fit a plot.

| Interface | Outside elbow | Inside-court elbow |
| --- | --- | --- |
| Core X/Z bounding box | (-6, -6)…(6, 6) | (-9, -9)…(9, 9) |
| Core footprint | Full 12 × 12 m square | 18 × 18 m L, excluding X > 3 **and** Z > 3 |
| Ground/top | Y = 0 / 3.2 | Y = 0 / 3.2 |
| Structural area | 144 m² | 288 m² |
| North/west exterior walls | Z = -6 / X = -6 | Z = -9 / X = -9 |
| Court-facing returns | Meet at the subsequent run junction | Z = 3, X = 3; each 6 m long |
| East connector | X = 6, Z = -6…6 | X = 9, Z = -9…3 |
| South connector | Z = 6, X = -6…6 | Z = 9, X = -9…3 |
| Whole visual AABB min | (-6.18, 0, -6.18) | (-9.18, 0, -9.18) |
| Whole visual AABB max | (6, 3.2, 6) | (9, 3.2, 9) |
| Whole visual size X/Y/Z | 12.18 × 3.2 × 12.18 | 18.18 × 3.2 × 18.18 |

Both roots and meshes are at identity, with the pivot at ground level and the center
of the **structural bounding box**, not the asymmetric L's area centroid. Godot +X
is east, -Z north, +Y up. The inside notch is at the southeast corner: its structural
void X = 3…9, Z = 3…9 is open toward both positive axes. The visual trim projects up
to 0.18 m into it from the return walls. This is a corner recess, **not an approved
6 m-wide complete communal court or an approved pedestrian-route placement**.

Independent literal footprint vertices, in X/Z order:

- Outside: (-6,-6), (6,-6), (6,6), (-6,6).
- Inside: (-9,-9), (9,-9), (9,3), (3,3), (3,9), (-9,9).

The inside variant includes a full 6 m return bay beyond the compact elbow in each
arm, so both outgoing connectors still span the full 12 m building depth. Its
recessed window treatment is not a solid square with an invisible court blocker.
The source core is a single watertight concave prism; its collider uses two exact
rectangles described below.

### Assembly contract with the delivered straight bay

Relative transforms for a corner placed at the world origin, in Godot metres:

| Linked component | Outside elbow | Inside elbow | Rotation about +Y |
| --- | --- | --- | --- |
| East straight bay origin | (9, 0, 0) | (12, 0, -3) | 0° |
| South straight bay origin | (0, 0, 9) | (-3, 0, 12) | +90° |
| Next stacked corner origin | (0, 3.2, 0) | (0, 3.2, 0) | 0° |

Each following straight bay advances 6 m along its run. Core connector and storey
edges are intentionally unbeveled: no seam pinholes. Exterior floor ribbons terminate
exactly at the outgoing planes; window trim never crosses them. Their square-ended
ribbons meet the sibling's Y = 0.04…0.20 m ribbon. Closed mating faces are retained
for per-component manifold topology and are hidden in assembled runs. Neither blank
connector face is a finished exposed-end design. The top plane accepts a compatible
roof/next-storey component at Y = 3.2; it is not itself a finished roof.

Window centers remain 3 m apart (two per 6 m bay), with 2.10 m glazing width and
Y = 1.00…2.55 m glazing height, matching the sibling. Frames, mullions, sills, heads,
aprons, bevels and the 0.18 m maximum outward trim envelope retain that treatment.
The corner accent adds a 0.24 m-wide bent arris, Y = 0.24…3.12 m, projecting 0.06 m.
Continuous bent ribbons avoid overlapping coplanar top faces at the corner. Dimensional
tolerance is ±0.001 m; source-to-GLB coordinate tolerance is ±0.00001 m. No sockets:
static documented connector planes are the assembly interface.

## Source, exports and materials

- Source: `art/source/models/environment/d03_apartment_family_06/d03_apartment_family_06.blend`.
- Collections: `export_d03_apartment_family_06_outside` and
  `export_d03_apartment_family_06_inside`.
- Roots: `D03ApartmentFamily06Outside` / `D03ApartmentFamily06Inside`;
  one child mesh per root with `_Mesh` appended.
- Exports: `art/models/environment/d03_apartment_family_06/d03_apartment_family_06_outside.glb`
  and `d03_apartment_family_06_inside.glb` in the same directory; each has its `.import` sidecar.
- Wrappers: `scenes/prefabs/environment/d03_apartment_family_06_outside.tscn`
  and `d03_apartment_family_06_inside.tscn`.
- Tools: `tools/asset_production/d03_apartment_family_06/` (`author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` with its UID sidecar, and `record.py`).

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Explicit export
uses `tools/assets/blender/export_settings.json`, selecting one named collection
per output, with animation/skin export disabled. Metres, applied transforms, no root
scale correction. Blender +Y maps once to Godot -Z; Blender +Z maps to Godot +Y.
The saved variants are co-located at their export datum: isolate the relevant export
collection for source editing. Studio ground, lights, camera and hidden one-metre
reference are excluded. Presentation-only offsets are applied after source save/export.

Each export has five opaque, back-culled, texture-free Principled materials in order:

| Slot | Material | sRGB swatch | Roughness / metallic |
| --- | --- | --- | --- |
| 0 | `terrace_bluegrey_render` | `#829398` | 0.76 / 0 |
| 1 | `terrace_pale_frame` | `#C5CABF` | 0.53 / 0 |
| 2 | `terrace_teal_spandrel` | `#31656A` | 0.65 / 0 |
| 3 | `terrace_petrol_closed_glass` | `#1E3645` | 0.29 / 0.12 |
| 4 | `terrace_coral_corner` | `#FF725D` | 0.62 / 0 |

The first four slots' names and actual Godot color/roughness/metallic values are
checked against the imported straight bay, not merely copied into the handoff.
No embedded images, textures, external material dependencies, rigs, clips or explicit
LODs. Default Godot automatic mesh LOD generation remains enabled; repeated-instance
cost, simplification appearance and camera-distance behavior remain unprofiled.

## Evidence and measured validation

[Hero](d03_apartment_family_06-evidence/hero.png) ·
[reverse side / court returns](d03_apartment_family_06-evidence/side.png) ·
[inside corner detail](d03_apartment_family_06-evidence/corner_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_06-evidence/overhead_47m_42deg.png).

All four renders were inspected by the producer. Isolated Blender Cycles CPU,
32 samples, AgX, 1280 × 720, PNG compression 95, no dithering; all are below 400 KiB.
The overhead is vertical-down, north-up perspective, 47 m above ground with 42°
**vertical FOV**; the 720 px height follows the standing evidence-size cap. Outside
is left and inside right in that view. Their roots are separated at X = -11 / +8 m
for presentation only. The square/L silhouettes and open notch are clear. Windows
and coral trims remain secondary, not overhead gameplay information. Plain upper
faces are storey mating planes, not a completed roof composition. These are not
Godot captures, placement acceptance or proof of court/actor visibility in a district.

[validation.json](d03_apartment_family_06-evidence/validation.json) records final source,
actual binary GLB and engine observations. [manifest.json](d03_apartment_family_06-evidence/manifest.json)
hashes every delivered payload except itself. [Final checks](d03_apartment_family_06-evidence/final-checks.log)
distinguish successful assertions from tool diagnostics.

| Measurement | Outside | Inside |
| --- | --- | --- |
| Triangles | **5,044** | **10,084** |
| Source vertices | 2,624 | 5,244 |
| Exported vertices | 3,464 | 6,946 |
| Meshes / surfaces | 1 / 5 | 1 / 5 |
| Non-manifold edges | 0 | 0 |
| Degenerate source faces / GLB triangles | 0 / 0 | 0 / 0 |
| Closed structural volume | 460.8 m³ | 921.6 m³ |
| Fresh saved-source re-export | Byte-identical | Byte-identical |

Finite vertices, unit source corner and actual GLB normals, identity transforms,
literal connector corners, volume, ground datum, material slots and binary-accessor
bounds pass. Counts describe disjoint closed trim solids joined into one mesh,
not a boolean-unioned building; hidden trim/core intersections are deliberate.

Final receipts, copied from the final validation JSON:

- Source: **315986 bytes**, SHA-256
  `7793bdae44007443dc987fdd69ae6a73e4cdd10f8d10d4fdbc5c6db3e5b976d1`.
- Outside GLB: **146052 bytes**, SHA-256
  `bd302c433ef855fd25f41632202aa68a8c0a288b9829020ddc59c85146dc69ad`.
- Inside GLB: **287724 bytes**, SHA-256
  `2ec9bcd5de8c5abe4d0250ec2d91c4d38aaf8b538c991ff1f633f2e335a0789e`.

### Prefab, collision and engine checks

Godot **4.8.dev7.official.c971f93e7** final headless import and runtime checks exit 0,
with no ERROR/SCRIPT ERROR lines or missing dependencies. Text-authored wrappers
were loaded, packed, saved and reloaded with the pinned headless editor because
live sessions are prohibited and the windowed editor is unavailable. The second
save is byte-stable for each wrapper, preserving UIDs, node identities and linkage.
`Visuals/Model` is the identity-transform GLB instance; no mesh data, material overrides,
inherited variants, editable children or gameplay script is embedded in either scene.

Both wrappers own `Collision/Body`, StaticBody3D layer 1 / mask 0:

- Outside: one `Core` BoxShape3D, size (12, 3.2, 12), center (0, 1.6, 0).
- Inside: `NorthWing`, size (18, 3.2, 12), center (0, 1.6, -3), plus
  `WestReturn`, size (12, 3.2, 6), center (-3, 1.6, 6).
  These disjoint rectangles share Z = 3 across X = -9…3. Their union exactly equals
  the documented L footprint, with no diagonal hull across the notch.

Decoration adds no snagging collision. The actor cannot enter the closed core;
no route, doorway, ramp, rail or navigable interior has been invented. The smooth,
exact core envelope intentionally omits shallow frames/sills/arrises.

Retained bounded checks through real resources and production APIs:

- **17 capsule solid/clear queries** (r = 0.35 m, h = 1.8 m), including the free
  inside notch, both court walls, near-corner clearance and internal collider seam.
- **Seven seam rays** using the actual straight prefab on both outgoing connectors,
  an actual stacked corner, and the inside two-box seam. Every expected facade hit
  occurs at its exact wall datum; no measured connector or compound-collider gap.
- **14 production ActorMotion runs**, 60 ticks each, using AUTHORITY and REPLAY:
  north stop, west stop, east bypass for both variants, plus inside diagonal-corner
  stop. Both modes give identical positions. North/west contacts are -6.3502574 m
  outside and -9.3502665 m inside; the concave stop is X/Z = 3.3506491 m.
- **Four car-sized box sweeps** (1.9 × 1.5 × 4.3 m): each facade blocks and each
  east bypass remains clear. These are shape sweeps, not production driving tests.

Tool limitation: editor-mode normalization exits 0 and proves byte-stability, but
emits headless editor shutdown RID/ObjectDB leak diagnostics, also observed in the
straight-bay handoff. The final import/runtime checks are clean; no errors are hidden
or broadly suppressed. The addon warns that this pinned engine version is untested.
Blender emits `use_nodes` deprecation notices for Blender 6; they are not failures
on the required pin. The initial style pass found overlong test helpers; they were
split and the final formatting/lint checks pass with zero warnings.

## Exact reproduction

From the repository root in Git Bash. Do not attach to any live editor session.
Scratch exports and raw logs stay outside the repository.

```sh
NID=d03_apartment_family_06
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

`validate.py` opens the saved source and calls `export.py` into scratch, comparing
both complete GLBs byte-for-byte. Manual export: open the saved source using the
same bounded Blender invocation, run `export.py -- C:/tmp/ft/assets/d03_apartment_family_06/reexport`.
A fresh `author.py` run is not promised to serialize the `.blend` byte-identically;
re-export from the committed source is the strict comparison. After intentional
source changes, refresh validation and handoff receipts, run the final pinned import,
then run `record.py` without `--check` last. `record.py --check` verifies payloads,
handoff bytes/hashes and normalized prefab hashes. No `production_checks.py` was run
(owner decision 52).

## Remaining acceptance

- Independent art/technical review of the two components and provisional joins.
- World-integrator approval of actual plot fit, storey counts, run lengths, open
  court mouths/cross-links, roof compositions and actor sightlines in saved placements.
- In-engine visual/gameplay-camera review, production vehicle movement, contextual
  authoritative multiplayer/transport behavior and packaged dependency checks.
- Repeated-placement draw-call, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, target-device or full gameplay acceptance is claimed. The
registry tracks other family records. The earlier straight-bay handoff contained no
stale pending item for this delivery, so no sibling doc/manifest change was needed.
