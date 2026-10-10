# d03_apartment_family.03 — Short infill block assembly reference

10 October 2026. **Saved linked reference and bounded checks delivered; independent
review and world acceptance pending.** Commissioned under the [register commission](commission.md),
superseding the concept-only restriction in the [family brief](../d03_apartment_family.md).
Producer: commissioned implementation worker. Accepting art/technical reviewer: unassigned.

## Design and dimensions

A **three-bay, two-storey short infill** breaks up Terrace Ward's longer apartment
bars. One warm central ground entrance, one selective upper balcony on the east bay,
two finished exposed ends and a continuous quiet blue-grey roof retain the delivered
kit's domestic character. Coral remains at the terminal arrises, not every roof edge.
The short, low rectangular mass contrasts with the earlier L and U groups without
introducing a bespoke building mesh, a new window proportion or a new material.

This is an **Assembly reference**, not a Model output, district placement or parcel
replacement. It composes unchanged [.05 straight](d03_apartment_family_05.md),
[.07 end](d03_apartment_family_07.md), [.08 entrance](d03_apartment_family_08.md),
[.09 balcony](d03_apartment_family_09.md) and [.10 straight/end roofs](d03_apartment_family_10.md).
All seven component handoffs, including [.06 corners](d03_apartment_family_06.md) and
[.11 height-step closure](d03_apartment_family_11.md), and the earlier
[.01 L](d03_apartment_family_01.md) / [.02 U](d03_apartment_family_02.md) references
were inspected. Corners and height changes are unnecessary for this level short run;
their absence is deliberate, not an unproduced dependency.

References: [Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03).
The district's 4.80 ha and 18 × 16 m small-apartment greybox are context, not a plot
allocation or approved replacement envelope. Run length, height and reservations
below are **provisional authored composition choices**, not image measurements or
a city-wide grid. No roads, terrain, world scenes or shared register were changed.

| Interface | Godot local metres |
| --- | --- |
| Root datum | (0,0,0), ground-centred structural footprint |
| Orientation | +X east, -Z north/front, +Y up |
| Bay / storey pitch | 6 / 3.2 m, unchanged |
| Structural building depth | 12 m |
| Closed structural bounds | (-9.24,0,-6)…(9.24,6.4,6) |
| Structural width / ground footprint area | 18.48 m / 221.76 m² |
| Whole visual minimum / maximum | (-9.34,0,-7.50) / (9.34,6.72,6.18) |
| Whole visual size X/Y/Z | 18.68 × 6.72 × 13.68 m |
| Roof field / coping top | Y = 6.62 / 6.72 |
| Balcony underside / handrail top | Y = 3.2 / 4.48 |
| Dimensional tolerance | ±0.001 m |

Keep these connected **empty, unroofed reservations** when using the reference:

- West side: X = -15…-11, Z = -12…12, 4 m wide.
- East side: X = 11…15, Z = -12…12, 4 m wide.
- Front connection: X = -15…15, Z = -12…-8, 4 m deep.

Each side reservation starts 1.66 m beyond the visible end; the front reservation
starts 0.50 m beyond the balcony's maximum projection. They extend outside this
asset intentionally. These are checked empty reservations, not delivered roads,
paths, navigation, vehicle lanes or approved traffic. A world integrator must connect
them to real routes and keep them clear; this small building must not close a court
mouth. Its apparent entrance is closed decoration, not a walking shortcut.

### Saved component interface

`scenes/prefabs/environment/d03_apartment_family_03.tscn` is the runtime placement
owner. [validation.json](d03_apartment_family_03-evidence/validation.json) records
all **16 direct prefab instances / 16 transitive GLB instances** and actual transforms.
No sockets, custom runtime scripts, material overrides or editable-child overrides.

| Named components | Root placement / Godot +Y yaw |
| --- | --- |
| `WestBayL0/L1` | .05 at (-6,0,0) / (-6,3.2,0), 0° |
| `EntryBayL0/L1` | .08 at (0,0,0); .05 at (0,3.2,0), 0° |
| `EastBayL0/L1` | .05 at (6,0,0) / (6,3.2,0), 0° |
| `WestBayRoof/EntryBayRoof/EastBayRoof` | .10_straight at X = -6/0/6, Y = 3.2, Z = 0, 0° |
| `WestEndL0/L1` | .07 at (-9.12,0,0) / (-9.12,3.2,0), 180° |
| `EastEndL0/L1` | .07 at (9.12,0,0) / (9.12,3.2,0), 0° |
| `WestEndRoof/EastEndRoof` | .10_end at (-9.12,3.2,0), 180° / (9.12,3.2,0), 0° |
| `EastFrontBalcony` | .09 at (6,0,-6), 0° |

End walls add 0.24 m at each terminal, not between the connected bays. Each roof is
at its top-storey host root: its geometry already contains the 3.2 m vertical offset.
The balcony also already contains its upper-storey offset. Do not double these
translations, stretch a bay, mirror a closure or alter `Visuals/Model` from identity.

## Sources, exports and materials

**No new .blend, GLB, texture or material applies to this assembly-only output.**
Every visible mesh traces through unchanged prefab → imported GLB → original committed
Blender source. Six distinct GLBs, their imports, five sources and six linked prefabs
are hash-pinned in validation. The existing opaque Principled materials, source
pivots, resource identities and automatic import LOD settings remain unchanged.
No copied mesh data, download, brand, third-party geometry or runtime-authored visible
hierarchy. No interior, operable door/window, climbing, accessible balcony/roof,
destruction state, rig, animation or physics authority was introduced.

The palette remains blue-grey render `#829398`, pale frames `#C5CABF`, teal spandrels
`#31656A`, petrol closed glazing `#1E3645`, selective coral `#FF725D`, warm entrance
`#E7B46E` and blue-grey roof `#526B7B`. Sibling handoffs own the slots and authorship.

Tools in `tools/asset_production/d03_apartment_family_03/` follow the earlier assembly
conventions. `author.py` seeds the saved scene once and refuses to overwrite saved
identities. `check_prefab.gd` normalizes and inspects the real linked scene, checks
physics/production motion, and exports actual transforms to scratch. `render.py`
instances linked Blender collections at those transforms without saving a duplicate
source. `export.py` delegates scratch reexports to the original sibling exporters
and shared `tools/assets/blender/export_settings.json`. `validate.py` checks source
and binary GLB geometry, roof coverage, empty reservations and the ground union.
`record.py` verifies receipts and generates the lean producer manifest last. There
is no shared generic assembly validator in this checkout; composition-specific
expectations remain in this asset's allowed tool directory.

## Evidence and measured validation

[Hero](d03_apartment_family_03-evidence/hero.png) ·
[reverse side](d03_apartment_family_03-evidence/side.png) ·
[entry/balcony/end detail](d03_apartment_family_03-evidence/assembly_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_03-evidence/overhead_47m_42deg.png).

All four final images were inspected by the producer. Isolated Blender **5.2.2 LTS**,
build `d13f752e3b9c`, Cycles CPU, 32 samples, AgX, RGB PNG compression 100, no dithering.
Hero/side/overhead are 1280 × 720; detail is 1024 × 576. Largest PNG is 366538 bytes
(about 358 KiB). Overhead is vertical-down, north-up at Godot **(0,47,-0.66)**,
42° **vertical FOV**. The compact continuous roof and selective balcony are legible;
the warm entrance and domestic window rhythm remain secondary at gameplay distance.
Hero/side show both finished end closures and continuous coping. Detail deliberately
crops the far ends to inspect the entry, mounted balcony and terminal connection.
The ground is an evidence-only studio backdrop, not delivered paving. These are not
Godot captures, moving-camera or populated-city actor-visibility acceptance.

Measured totals count repeated instances:

- **23,296 triangles; 12,168 source vertices; 16,362 exported vertices.**
- **16 linked meshes / 57 material surfaces**, not 57 unique materials.
- Zero non-manifold edges, degenerate source faces or actual GLB triangles in all
  six used dependency meshes; unit source corner/exported normals pass.
- Six fresh GLBs from five unchanged saved Blender sources are **byte-identical**
  to their delivered dependencies. No source/export is replaced or flattened.
- Actual binary-vertex assembled bounds and engine bounds match within 0.001 m.
- **13 actual-triangle first-hit samples** verify all three roof fields, both bay
  joins, both end-coping strips and front/rear coping heights.
- **126 actual-triangle vertical samples** across three lanes per reservation find
  no visible geometry over the side/front links. These are bounded unroofed-space
  checks, not perspective actor-occlusion or exhaustive rasterization evidence.
- Five literal ground rectangles independently match the inherited base colliders,
  including both terminal extensions; the union is 221.76 m².

### Prefab, collision and engine checks

The scene inherits **10 simple static boxes**, layer 1 / mask 0: six bay cores and
four end-wall slabs. Each remains owned by its linked sibling, not a new whole-block
hull. There is no collider spanning either side link. Shallow trim, inaccessible
upper balcony and overhead roofs retain their established visual-only contracts.
No floor, reachable walk deck, guard blocker or gameplay state is added. The checker
uses a temporary invisible physics floor for motion tests only.

Pinned **Godot 4.8.dev7.official.c971f93e7** headless import and runtime load/check
exit 0 with no ERROR/SCRIPT ERROR lines or missing dependencies. Live sessions are
prohibited and the windowed editor is unavailable, so the text-authored scene was
loaded, packed and saved headlessly. **Two subsequent byte-stable reload/save cycles**
preserve scene identities, UID and all links. No sibling resource was edited.

- Thirteen r = 0.35 m / h = 1.8 m capsule solid/clear queries pass.
- Eleven physics rays hit expected facade/end/stack seam planes. Terminal seam
  samples bracket ±1 mm to avoid exact-edge grazing ambiguity; the independent
  five-rectangle union verifies continuous structural coverage.
- Fifty vertical physics rays find both side links unobstructed.
- A 1.9 × 1.5 × 4.3 m car-sized box sweeps **20 m** down the east bypass clear.
- Eight production **`ActorMotion.step`** runs, four cases × AUTHORITY/REPLAY,
  60 ticks each, pass with identical mode endpoints: both side links Z = 2.99999976,
  front seam/balcony bypass X = 6.00000191, closed entry stop Z = -6.35026121 m.
  These are bounded local API checks, not production vehicle handling or multiplayer
  transport/admission/prediction validation.

Final scene receipt, copied from final validation and checked by `record.py --check`:
**3532 bytes**, SHA-256
`cd7b30d1caa01c055cba40b89a114b1a262a4063b6e865b825b36cc5af55bddb`.
Prefab UID: `uid://c84b22w5cf0e5`. Dependency receipts stay in validation rather than
another duplicated inventory. [manifest.json](d03_apartment_family_03-evidence/manifest.json)
hashes every produced payload except itself. [Final check log](d03_apartment_family_03-evidence/final-checks.log)
records checks and classified diagnostics.

Tool limitations: headless editor normalization exits 0 and proves stable saves but
emits the same RID/ObjectDB shutdown-leak diagnostics seen in earlier siblings.
Final import/runtime logs are clean; no errors are suppressed. The addon warns this
engine pin is untested. Blender's `use_nodes` deprecation notice concerns Blender 6,
not this pin. No live Blender/Godot session or production-checks runner was used.

## Exact reproduction

From repository root in Git Bash; scratch logs/reexports stay outside the repository:

```sh
NID=d03_apartment_family_03
TOOLS=tools/asset_production/$NID
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
mkdir -p C:/tmp/ft/assets/$NID
# Only for a fresh scene without saved identities: python "$TOOLS/author.py"
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . --script "$TOOLS/check_prefab.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "$TOOLS/check_prefab.gd"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8 timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/render.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8 timeout 300 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/validate.py"
mise exec -- gdstyle fmt --check "$TOOLS/check_prefab.gd"
mise exec -- gdstyle --max-line-length 100 --max-warnings 0 "$TOOLS/check_prefab.gd"
python "$TOOLS/record.py" --check
```

After intentional changes, refresh validation and the handoff, run the final pinned
import, then regenerate the manifest with `record.py` without `--check` last.
Rendering is not needed merely to recheck unchanged exports. Do not run
`production_checks.py` (owner decision 52).

## Remaining acceptance

- Independent art/technical review of this reference and provisional proportions.
- World-integrator approval of plot fit, final heights, actual entry positions,
  connected side routes/court mouths and actor sightlines in saved world placements.
- In-engine visual/gameplay-camera and moving-camera review, contextual gameplay,
  production vehicle motion, authoritative transport and packaged dependencies.
- Repeated-placement draw calls, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, full gameplay or target-device acceptance is claimed. None
of the nine earlier sibling handoffs lists this reference as a stale pending production
item; their world-context checks remain pending. No sibling doc/manifest edit was
needed. The register, not this handoff, tracks other family records.
