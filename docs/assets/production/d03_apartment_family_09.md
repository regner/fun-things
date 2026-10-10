# d03_apartment_family.09 — Balcony / loggia frontage insert

10 October 2026. **Original source, linked export and bounded prefab checks delivered;
independent review and world acceptance pending.** Commissioned under the
[register commission](commission.md), superseding the concept-only restriction in the
[family brief](../d03_apartment_family.md). Producer: commissioned implementation worker.
Accepting art/technical reviewer: unassigned. No shared register, district placement,
road, gameplay or sibling asset files changed.

## Design and dimensions

A selective **upper-storey bolt-on balcony**, not a replacement apartment bay or a
recess cut into its facade. A shallow blue-grey cantilever deck, pale edge nosing and
U-shaped pale railing with paired teal front panels continue the delivered
[straight bay](d03_apartment_family_05.md). Sparse uprights and open space above the
panels preserve broad domestic rhythms. Solid teal side screens close the returns.
No coral or amber is added: those remain reserved for the delivered
[corners](d03_apartment_family_06.md), [end closure](d03_apartment_family_07.md) and
[entrance](d03_apartment_family_08.md). All four sibling handoffs were inspected.

**Exterior decoration only:** the host windows and facade stay closed. There is no
interior, working balcony door, climbing, accessible deck, roof route, destruction
state or interaction socket. The slash in the register label is resolved as the
balcony option; no ground-floor loggia or second variant is delivered.

Original Blender construction only: no downloads, third-party geometry, brands,
textures, image-to-mesh or runtime-generated visible meshes. References inspected:
[Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03), and
the sibling interfaces. District area and existing greybox footprints are context,
not plot allocations or accepted replacement envelopes.

### Provisional interface — metres, Godot local axes

The supervisor explicitly approved a **5.4 m × 1.5 m upper-storey bolt-on insert**
for the existing **6 m bay / 12 m depth / 3.2 m storey** family, preserving the closed
facade. These authored dimensions are provisional, not inferred from concept imagery.

| Interface | Value |
| --- | --- |
| Root / mesh pivot | (0, 0, 0), ground-level facade centre anchor |
| Whole visual AABB | Min (-2.7, 3.2, -1.5); max (2.7, 4.48, 0) |
| Whole visual size X/Y/Z | 5.4 × 1.28 × 1.5 m |
| Lowest visible underside | Y = 3.2 m, already elevated in source geometry |
| Deck top / nominal thickness | Y = 3.38 / 0.18 m |
| Blue-grey deck | X = -2.7…2.7; Z = -1.48…0 |
| Pale nosing | X = -2.665…2.665; Y = 3.235…3.345; Z = -1.50…-1.455 |
| Rear mounting plane | Z = 0, no geometry projects behind it |
| Handrail top / height above deck | Y = 4.48 / 1.10 m |
| Front handrail | X = -2.66…2.66; Y = 4.39…4.48; Z = -1.47…-1.33 |
| Left / right handrail X | -2.66…-2.53 / 2.53…2.66 |
| Side handrail Z | -1.33…0 |
| Front infill panels X | -2.50…-0.10 / 0.10…2.50 |
| Front infill panels Y / Z | 3.47…4.10 / -1.43…-1.36 |
| Repeated-balcony horizontal gap | 0.60 m at the family's 6 m pitch |
| Dimensional / source-to-export tolerance | ±0.001 / ±0.00001 m |

The **ground-level mounting anchor is deliberate**, not a ground-contact pivot for a
freestanding prop. The entire source/export already sits above it. Do not move the
mesh or `Visuals/Model` down to the origin. Blender +Y front maps once to Godot -Z;
Blender +Z maps to +Y. No sockets: documented static mounting planes are the interface.

### Placement relative to the existing straight bay

For a base bay at the origin and the upper straight bay at (0, 3.2, 0):

| Mount | Balcony root position | Rotation about Godot +Y |
| --- | --- | --- |
| First upper-storey front | (0, 0, -6) | 0° |
| First upper-storey rear | (0, 0, 6) | 180° |
| Another bay along the run | Add (±6, 0, 0) | Same rotation |
| Next storey | Add (0, 3.2, 0) | Same rotation |

The first balcony underside is therefore **3.2 m above the base ground**, not 6.4 m.
The source's elevated datum avoids a default ground-level deployment. Only rigid yaw
and nonnegative storey-height offsets are supported; no negative scale, downward
placement or pitch/roll. The underlying terrain remains flat. Never place this
visual-only prefab where another accessible elevated surface reaches it.

The deck mates with the upper floor ribbon; rear rail terminals meet the shallow
outer window-frame zone. Those small hidden mounting intersections are intentional.
No existing glazing, aperture or sibling mesh is edited. The visible front envelope
extends to Z = -7.5 relative to the bay, 1.32 m beyond its ordinary 0.18 m trim.
Selective placement must account for that projection: keep open court mouths and
cross-links visually clear, and check facing/inside-corner balconies for overlap.
Corner-specific packing, plot fit and route sightlines are not certified here.

## Source, export and materials

- Source: `art/source/models/environment/d03_apartment_family_09/d03_apartment_family_09.blend`.
- Collection: `export_d03_apartment_family_09`.
- Root / mesh: `D03ApartmentFamily09` / `D03ApartmentFamily09_Mesh`.
- Export: `art/models/environment/d03_apartment_family_09/d03_apartment_family_09.glb`
  with its committed `.import` metadata.
- Prefab: `scenes/prefabs/environment/d03_apartment_family_09.tscn`.
- Tools: `tools/asset_production/d03_apartment_family_09/` (`author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` with its UID, and `record.py`).

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export consumes
`tools/assets/blender/export_settings.json`, selecting only the named collection,
with animation/skin export disabled. Metres, applied transforms, identity root and
mesh, no corrective scale. The 18 original closed solids are joined into one mesh;
bevel and weighted-normal modifiers are applied. Studio lights, camera, ground and
hidden one-metre reference are excluded from the export. Render-only linked sibling
context is loaded **after** source save/export and never enters this source or GLB.

Three opaque, back-culled, texture-free Principled surfaces in export order:

| Slot | Material | sRGB swatch | Roughness / metallic |
| --- | --- | --- | --- |
| 0 | `terrace_bluegrey_render` | `#829398` | 0.76 / 0 |
| 1 | `terrace_pale_frame` | `#C5CABF` | 0.53 / 0 |
| 2 | `terrace_teal_spandrel` | `#31656A` | 0.65 / 0 |

The engine check compares all three materials' actual names, color, roughness and
metallic values to the straight-bay import. No textures, embedded images, external
material dependencies, rigs, clips or explicit LODs. Default Godot automatic mesh LOD
generation remains enabled; simplification appearance and repeated-instance cost
remain unprofiled.

## Evidence and measured validation

[Mounted hero](d03_apartment_family_09-evidence/hero.png) ·
[isolated reverse side](d03_apartment_family_09-evidence/side.png) ·
[railing detail](d03_apartment_family_09-evidence/railing_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_09-evidence/overhead_47m_42deg.png).

All four final renders were inspected by the producer. Isolated Blender Cycles CPU,
32 samples, AgX, 1280 × 720, PNG compression 95, no dithering; every PNG is below
300 KiB. Hero and overhead include two unchanged, source-linked straight bays as
render-only mounting context. Their bare top/end faces are unfinished mating planes,
not a completed roof/end composition. Side and detail isolate this balcony.

The overhead is vertical-down, north-up perspective, 47 m above ground with 42°
**vertical FOV**, using the standing 720 px evidence-height cap. The pale U and shallow
projection remain visible above the quiet facade; rail microdetail is not essential
gameplay information. The component necessarily occludes part of the ground beneath
it. These are not Godot captures or proof of actor/court visibility in city placement.
An initial render exposed coplanar nosing faces and a cropped context roof; the deck
front was recessed 0.02 m behind the nosing and the hero widened before final export.

[validation.json](d03_apartment_family_09-evidence/validation.json) retains source,
actual binary GLB and engine observations. [manifest.json](d03_apartment_family_09-evidence/manifest.json)
hashes every produced payload except itself. [Final checks](d03_apartment_family_09-evidence/final-checks.log)
distinguish successful assertions from known tool diagnostics.

- **1,944 triangles; 1,008 source vertices; 1,296 exported vertices; one mesh / three surfaces.**
- Zero non-manifold edges, degenerate source faces or actual GLB triangles.
- Unit source corner/exported normals, finite source coordinates, identity transforms,
  actual binary-accessor bounds and all 18 closed-solid islands pass.
- Independent literal bounds identify the deck and all three U-handrails; source,
  actual GLB and Godot agree on minimum underside **3.20000005 m > 2.5 m**.
- Fresh re-export from the final saved source is byte-identical to the delivered GLB.
- Final source: **133955 bytes**, SHA-256
  `a73bec9a99c41ca68d2fb7e90d1a3c0b39ffcb522e1a353932a91411218a8da3`.
- Final GLB: **56252 bytes**, SHA-256
  `998ff78484fd85a2f89e375821977ad01492ae19a050ba3fc70eb7ce3ea3c0d0`.

Counts describe disjoint closed solids, not a boolean union. Rail/post and
screen/post intersections are deliberate construction joins. No new visible geometry
is authored in Godot.

### Prefab, collision decision and engine checks

**Explicit supervisor direction, 10 October 2026:** the approved upper-storey balcony
is unreachable because there are no interiors or climbing; all geometry above 2.5 m
stays **visual-only, with no deck or guard colliders**. This resolves the standing
walk-deck/guard rule for this particular inaccessible decoration. It is not a general
exemption for reachable platforms. The supervisor's ground-floor alternative would
require one blocking box and no walk deck; that alternative is not delivered here.

The source and prefab have a 3.2 m minimum underside, leaving **1.4 m above a 1.8 m
actor** and 0.7 m above the overhead-only threshold. The actual host continues to own
its closed core collision. This prefab adds no PhysicsBody3D, CollisionShape3D,
navigation, gameplay script, access route or authority state.

Godot **4.8.dev7.official.c971f93e7** final headless import and runtime checks exit 0
without ERROR/SCRIPT ERROR lines or missing dependencies. The wrapper was authored
as text because live sessions are prohibited and the windowed editor is unavailable,
then loaded, packed, saved and reloaded with pinned headless Godot. The second save
is byte-stable, preserving UIDs, node identities and linkage. `Visuals/Model` instances
the GLB at identity; no mesh copies, overrides, editable children or inherited variants.
Prefab UID: `uid://bqipnjwt85ymj`; model UID: `uid://b884ykljetvmh`.

Bounded checks use the actual balcony and two actual straight-bay prefabs:

- Three r = 0.35 m / h = 1.8 m capsule queries stay clear under the overhang.
- A yawed 1.9 × 1.5 × 4.3 m car-sized box fits beneath it without an invisible blocker.
- An upper-facade aim ray passes the decorative guard and hits the unchanged closed
  host wall at Z = 0 in the test's facade-anchor coordinates.
- Two production **`ActorMotion.step`** runs, 60 ticks each, cross beneath the balcony
  in AUTHORITY and REPLAY. Both produce the identical endpoint
  (0.99999869, 0.00087790, -0.80000001) from (-4, 0, -0.8), without a balcony snag.
  This is local API evidence, not vehicle handling or multiplayer transport proof.

Tool limitations: editor-mode normalization exits 0 and proves byte-stability but
emits headless editor RID/ObjectDB shutdown-leak diagnostics also observed in the
sibling handoffs. Final import/runtime checks are clean; no errors are suppressed.
The addon warns that this pinned engine version is untested. Blender's `use_nodes`
deprecation notices concern Blender 6, not the required pin. No live session was used.

## Exact reproduction

From repository root in Git Bash. Scratch exports and raw logs stay outside the
repository. Never attach to a live Blender or Godot session.

```sh
NID=d03_apartment_family_09
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

`validate.py` loads the saved source and calls `export.py` into scratch before a
whole-file byte comparison; it also requires the normalization/runtime receipt.
Manual export: open the saved `.blend` using the same bounded Blender invocation,
then run `export.py -- C:/tmp/ft/assets/d03_apartment_family_09/reexport`. Rebuilding
with `author.py` is not promised to serialize the source identically; re-export from
the committed source is the strict comparison. After intentional changes, refresh
validation/handoff receipts, run the final pinned import, then run `record.py` without
`--check` last. Its check verifies every payload, handoff source/export hashes and
byte counts, and the normalized prefab hash. No `production_checks.py` was run
(owner decision 52).

## Remaining acceptance

- Independent art/technical review of the component and its provisional interface.
- World-integrator approval of selective upper-storey placement, corner/facing
  clearances, roof coverage and court-mouth/cross-link/actor visibility.
- Actual in-engine visual/gameplay-camera review, production vehicle movement,
  contextual authoritative multiplayer/transport behavior and packaged dependencies.
- Repeated-placement draw-call, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, target-device or full gameplay acceptance is claimed. The
registry tracks other family records. None of the four earlier sibling handoffs had
a stale pending item for this delivery, so no sibling doc/manifest edits were needed.
