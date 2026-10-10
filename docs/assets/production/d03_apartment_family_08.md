# d03_apartment_family.08 — Ground-floor entrance bay

10 October 2026. **Original source, linked export and bounded prefab checks delivered;
independent review and world acceptance pending.** Commissioned under the
[register commission](commission.md), superseding the concept-only restriction in the
[family brief](../d03_apartment_family.md). Producer: commissioned implementation worker.
Accepting art/technical reviewer: unassigned. No shared register, district placement,
road, gameplay or sibling asset files changed.

## Design and dimensions

A ground-floor replacement for the [straight apartment bay](d03_apartment_family_05.md),
not a frontage overlay. A warm double-door portal with pale liner, dark closed leaves,
teal kickplates, paired fixed pulls and a shallow head brow identifies the entrance.
A tall, narrow closed-glass strip with staggered landing bands suggests the stair core
from outside. The rear keeps the ordinary paired domestic windows. Blue-grey render,
pale trim and teal match the delivered [corners](d03_apartment_family_06.md) and
[end closure](d03_apartment_family_07.md); warm amber is confined to the entry rather
than competing with coral corner accents.

**Closed exterior only:** the apparent doors and glazing are not openings. No interior,
operable door, stairs, landing, threshold step, passage, roof traversal, destruction
state or interaction socket is supplied. The stair-core treatment is a facade cue,
not a promise of an accessible stairwell. Top and side core faces are mating planes,
not a finished roof or exposed-end design.

Original Blender construction only: no downloads, third-party geometry, brands,
textures, image-to-mesh or runtime-generated visible geometry. References inspected:
[Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03), and
the three delivered sibling interfaces. The 4.80 ha district and existing greybox
footprints are context, not an allocation or approved replacement envelope.

### Provisional interface — metres, Godot local axes

The family's **6 m bay pitch, 12 m building depth and 3.2 m storey pitch** are preserved.
Entry dimensions are provisional authored values permitted by the standing production
brief, not measurements inferred from concept imagery. Do not stretch the module.

| Interface | Value |
| --- | --- |
| Origin | Ground-centred structural footprint, (0, 0, 0) |
| Core / collider AABB | Min (-3, 0, -6); max (3, 3.2, 6) |
| Whole visual AABB | Min (-3, 0, -6.18); max (3, 3.2, 6.18) |
| Whole visual size X/Y/Z | 6.0 × 3.2 × 12.36 m |
| Left / right connector | X = -3 / +3, full 12 m depth |
| Bottom / top stack datum | Y = 0 / 3.2, square unbeveled core edges |
| Front / rear structural wall | Z = -6 / +6 |
| Maximum outward decorative trim | 0.18 m, both front and rear |
| Warm portal | X = -2.25…0.45; Y = 0…2.78 |
| Left / right closed door panels | X = -1.98…-0.94 / -0.86…0.18; Y = 0.035…2.30 |
| Door transom | X = -1.98…0.18; Y = 2.39…2.49 |
| Shallow head brow | X = -2.38…0.58; Y = 2.70…2.88; 0.18 m projection |
| Stair-core glazing | X = 1.24…2.36; Y = 0.48…2.90 |
| Stair-core surround | X = 1.12…2.48; Y = 0.35…3.02 |
| Staggered landing bands | Y = 1.10…1.21 / 1.91…2.02 |
| Rear window centres / glazing | X = -1.5 / +1.5; 2.10 m wide; Y = 1.00…2.55 |
| Pale floor ribbon | Y = 0.04…0.20; 0.10 m projection; interrupted only at front portal |
| Dimensional / axis-bound tolerance | ±0.001 m / ±0.00001 m |

The front ribbon spans X = -3…-2.25 and 0.45…3; the rear ribbon spans the full width.
Both connector ends match the straight bay's ribbon height/depth. No trim crosses
X = ±3 or Y = 3.2. The door starts at ground level without an exterior walkable step.
The 0.18 m brow is a shallow integral facade trim, not a separately placed canopy.

### Assembly contract

Replace one base straight bay at the **same transform**, rather than overlaying its
windows. Place adjoining straight bays at (±6, 0, 0), and an upper straight bay at
(0, 3.2, 0). Corners accept this entrance wherever they accept the straight bay:
outside elbow east (9, 0, 0), south (0, 0, 9) at +90° yaw; inside elbow east
(12, 0, -3), south (-3, 0, 12) at +90° yaw. The entrance itself is intended for the
lowest storey, not stacked as repeated upper-floor doors. Its stair-core strip does
not require a new upper-storey variant or change existing window proportions.

For an exposed end, use the delivered closure at (3.12, 0, 0) with 0° yaw or
(-3.12, 0, 0) with 180° yaw, relative to this entrance bay. Each closure adds 0.24 m
of structural length, as its own handoff specifies. Do not add closure walls across
court mouths. Closed mating faces are retained for per-component manifold topology
and hidden within assemblies. Rigid transforms only; no negative scale. No sockets:
static numeric connector planes are the assembly interface. World placement must
keep the court mouth and cross-links open; a decorative entrance is not a shortcut.

## Source, export and materials

- Source: `art/source/models/environment/d03_apartment_family_08/d03_apartment_family_08.blend`.
- Collection: `export_d03_apartment_family_08`.
- Root / mesh: `D03ApartmentFamily08` / `D03ApartmentFamily08_Mesh`.
- Export: `art/models/environment/d03_apartment_family_08/d03_apartment_family_08.glb`
  with its committed `.import` metadata.
- Prefab: `scenes/prefabs/environment/d03_apartment_family_08.tscn`.
- Tools: `tools/asset_production/d03_apartment_family_08/` (`author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` with its UID, and `record.py`).

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Explicit export
consumes the shared `tools/assets/blender/export_settings.json`, selecting only the
named collection, with animation/skin export disabled. Metres, applied transforms,
identity root and mesh. Blender +Y front maps once to Godot -Z; Blender +Z to +Y.
Original closed solids are joined into one mesh; bevel and weighted-normal modifiers
are applied. Studio lights, camera, ground and hidden one-metre reference stay outside
the export collection. No live editor session was used.

Five opaque, back-culled, texture-free Principled surfaces in export order:

| Slot | Material | sRGB swatch | Roughness / metallic |
| --- | --- | --- | --- |
| 0 | `terrace_bluegrey_render` | `#829398` | 0.76 / 0 |
| 1 | `terrace_pale_frame` | `#C5CABF` | 0.53 / 0 |
| 2 | `terrace_teal_spandrel` | `#31656A` | 0.65 / 0 |
| 3 | `terrace_petrol_closed_glass` | `#1E3645` | 0.29 / 0.12 |
| 4 | `terrace_warm_entry` | `#E7B46E` | 0.58 / 0 |

The engine check compares the first four imported materials' names, color, roughness
and metallic values against the actual straight-bay import. No textures, embedded
images, external material dependencies, rigs, clips or explicit LODs. Default Godot
automatic mesh LOD generation remains enabled; distance behavior and repeated-instance
cost are not performance-accepted.

## Evidence and measured validation

[Hero](d03_apartment_family_08-evidence/hero.png) ·
[rear and mating side](d03_apartment_family_08-evidence/side.png) ·
[entrance detail](d03_apartment_family_08-evidence/entrance_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_08-evidence/overhead_47m_42deg.png).

All four renders were inspected by the producer, also comparing the three sibling
hero views. Isolated Blender Cycles CPU, 32 samples, AgX, 1280 × 720, PNG compression
95, no dithering; every PNG is below 300 KB. The overhead is vertical-down, north-up
perspective, 47 m above ground with 42° **vertical FOV**; its 720 px height follows the
standing evidence-size cap. The quiet structural top dominates; the warm brow gives a
small frontage accent, while door/core details are not legible overhead. They carry no
essential gameplay information. These are not Godot captures, a finished roof
composition, or proof of court/actor visibility in district placement.

[validation.json](d03_apartment_family_08-evidence/validation.json) retains measured
source, actual binary GLB and engine observations. [manifest.json](d03_apartment_family_08-evidence/manifest.json)
hashes every delivered payload except itself. [Final checks](d03_apartment_family_08-evidence/final-checks.log)
distinguish successful assertions from known tool diagnostics.

- **2,724 triangles; 1,424 source vertices; 1,930 exported vertices; one mesh / five surfaces.**
- Zero non-manifold edges, zero degenerate source faces or actual GLB triangles.
- Finite vertices, unit source corner/exported normals, identity transforms, literal
  connector corners, ground datum and actual binary-accessor axis bounds pass.
- Independent literal bounds checks identify all six closed glazing solids: two rear
  windows, two doors, transom and stair-core strip.
- Fresh re-export from the final saved source is byte-identical to the delivered GLB.
- Final source: **153445 bytes**, SHA-256
  `8b135aa7ad453005868d37e513d4f7db2d684d63ef47c54ab7f0dfd057cf3d51`.
- Final GLB: **82996 bytes**, SHA-256
  `dd57a82732fba60234593432922760640dc8e52632fdcad19f0dacb020bb5c0b`.

Counts describe disjoint closed trim solids joined into one mesh, not a boolean union.
Shallow trim/core intersections are deliberate and hidden, as in the sibling bays.

### Prefab, collision and engine checks

Godot **4.8.dev7.official.c971f93e7** final headless import and runtime checks exit 0
without ERROR/SCRIPT ERROR lines or missing dependencies. The wrapper was authored
as text because live sessions are prohibited and the windowed editor is unavailable,
then loaded, packed, saved and reloaded in the pinned headless editor. The second
save is byte-stable, preserving UIDs, node identities and linkage. `Visuals/Model`
instances the GLB at identity; no copied mesh, material override, editable child,
inherited variant or gameplay script is embedded in the prefab. Prefab UID:
`uid://c2c862t4dwn35`; model UID: `uid://ccjf5eoqkdwk5`.

`Collision/Body/Core` is the only collider: **BoxShape3D (6, 3.2, 12)** centred at
(0, 1.6, 0), owned by StaticBody3D layer 1 / mask 0. This exactly matches the closed
core, including the closed door and stair-core facade. Shallow decorative trim does
not add snagging collision. No invisible court blocker, through-route, walk collider
or dynamic door is introduced; this component replaces an already-solid bay.

Retained bounded checks use real imported resources and production APIs:

- **Eight capsule solid/clear queries**, radius 0.35 m / height 1.8 m, including the
  entrance, stair-core wall, rear, solid centre and clear setbacks on all four sides.
- An entrance aim ray hits Z = -6. Two assembly rays use the actual straight prefab
  beside/above the entrance at X = 3 / Y = 3.2; both hit the exact Z = -6 wall datum.
- **Ten production `ActorMotion.step` runs**, 60 ticks each: entry stop, stair-core
  stop, rear stop, side stop and east bypass in AUTHORITY and REPLAY. Both modes give
  identical positions: front stops Z = -6.3502574 m, rear Z = 6.3502574 m, side
  X = 3.3502574 m, clear bypass Z ≈ -2.9999936 m.
- Two car-sized box sweeps, 1.9 × 1.5 × 4.3 m: the entrance facade blocks and the
  east bypass stays clear. These are shape sweeps, not production driving tests.

Tool limitations: editor-mode normalization exits 0 and proves byte-stability but
emits headless editor RID/ObjectDB shutdown-leak diagnostics, also observed in the
sibling handoffs. Final import/runtime checks are clean; no errors are suppressed.
The addon warns that this pinned engine version is untested. An initial GDScript
style check found a 52-line motion helper; extracting its literal cases resolved it.
Final formatting/lint checks pass with zero warnings. Blender's `use_nodes` notices
concern Blender 6, not the required pin.

## Exact reproduction

From repository root in Git Bash. Never attach to a live Blender or Godot session.
Scratch outputs and raw logs belong outside the repository.

```sh
NID=d03_apartment_family_08
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

`validate.py` loads the saved source and calls `export.py` into scratch before a whole
GLB byte comparison; it requires the runtime/normalization receipt. Manual export:
open the saved `.blend` using the same bounded Blender invocation, then run `export.py
-- C:/tmp/ft/assets/d03_apartment_family_08/reexport`. Rebuilding with `author.py` is
not promised to serialize either source or GLB identically across fresh construction;
re-export from the committed source is the strict comparison. After intentional
changes, refresh validation/handoff receipts, run the final pinned import, then run
`record.py` without `--check` last. Its check verifies all payloads, handoff source/
export receipt hashes/byte counts and the normalized prefab hash. No
`production_checks.py` was run (owner decision 52).

## Remaining acceptance

- Independent art/technical review of this entrance and its provisional interface.
- World-integrator approval of plot fit, entry locations, run lengths, storey counts,
  roof coverage, court mouths/cross-links and actor sightlines in saved placements.
- Actual in-engine visual/gameplay-camera review, production vehicle movement,
  contextual authoritative network/transport behavior and packaged dependency checks.
- Repeated-placement draw-call, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, target-device or full gameplay acceptance is claimed. The
registry tracks other family records. None of the three earlier sibling handoffs had
a stale pending item for this delivery, so no sibling doc/manifest edits were needed.
