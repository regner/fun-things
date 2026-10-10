# d03_apartment_family.04 — Stepped bar assembly reference

10 October 2026. **Saved linked reference and bounded checks delivered; independent
review and world acceptance pending.** Commissioned under the [register commission](commission.md),
superseding the concept-only restriction in the [family brief](../d03_apartment_family.md).
Producer: commissioned implementation worker. Accepting art/technical reviewer: unassigned.

## Design and dimensions

A five-bay Terrace Ward bar rises through **2–3–4–3–2 storeys**, with two successive
one-storey terraces on each side of a central crown. Two warm ground entrances,
four selective upper balconies, finished terminal walls and quiet blue-grey roof
fields retain the delivered kit's domestic character. Coral remains on terminal
and step-wall arrises, not every roof edge. All four drops use the complete shared
height-step closure; none exceeds its approved one-storey limit.

This is an **Assembly reference**, not a new Model output, world sector or parcel
replacement. It composes unchanged [.05 straight](d03_apartment_family_05.md),
[.07 end](d03_apartment_family_07.md), [.08 entrance](d03_apartment_family_08.md),
[.09 balcony](d03_apartment_family_09.md), [.10 roofs](d03_apartment_family_10.md) and
[.11 step closure](d03_apartment_family_11.md). All seven component handoffs, including
[.06 corners](d03_apartment_family_06.md), and the earlier [.01 L](d03_apartment_family_01.md),
[.02 U](d03_apartment_family_02.md) and [.03 infill](d03_apartment_family_03.md) references
were inspected. A straight bar needs no corner variant; no substitute geometry or
bespoke building mesh is introduced.

References: [Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03).
The district's 4.80 ha and 32 × 14 m slab greybox are context, not an allocation or
approved replacement envelope. Run length, heights and route reservations below are
**provisional authored composition choices**, not image measurements or a city-wide
grid. No roads, terrain, world scenes, gameplay or shared register were changed.

| Interface | Godot local metres |
| --- | --- |
| Root datum | (0,0,0), ground-centred structural footprint |
| Orientation | +X east, -Z north/front, +Y up |
| Bay / storey pitch | 6 / 3.2 m, unchanged |
| Structural building depth | 12 m |
| Ground structural bounds | (-15.24,0,-6)…(15.24,3.2,6) |
| Structural width / ground footprint area | 30.48 m / 365.76 m² |
| Maximum structural height | 12.8 m at the central crown |
| Whole visual minimum / maximum | (-15.34,0,-7.50) / (15.34,13.12,6.18) |
| Whole visual size X/Y/Z | 30.68 × 13.12 × 13.68 m |
| Roof fields, west to east | Y = 6.62, 9.82, 13.02, 9.82, 6.62 |
| Coping tops, west to east | Y = 6.72, 9.92, 13.12, 9.92, 6.72 |
| Balcony undersides | Y = 3.2; second central balcony at 6.4 |
| Dimensional tolerance | ±0.001 m |

Preserve these connected **empty, unroofed reservations** when using the reference:

- West side: X = -21…-17, Z = -12…12, 4 m wide.
- East side: X = 17…21, Z = -12…12, 4 m wide.
- Front connection: X = -21…21, Z = -12…-8, 4 m deep.

Each side reservation starts 1.66 m beyond the visible end; the front reservation
starts 0.50 m beyond the balconies' maximum projection. They intentionally extend
outside the asset. These are checked empty spaces, not authored roads, paths,
navigation or approved traffic. The world integrator must connect them to actual
routes and keep them unoccupied. Do not use the bar to close a communal court mouth.
The apparent entrances remain closed decoration, not walking shortcuts.

### Saved component interface

`scenes/prefabs/environment/d03_apartment_family_04.tscn` is the sole runtime placement
owner. [validation.json](d03_apartment_family_04-evidence/validation.json) lists all
**33 direct component instances / 41 transitive GLB instances** with actual engine
transforms. No runtime scripts, sockets, material or editable-child overrides.

| Named components | Root placement / Godot +Y yaw |
| --- | --- |
| `WestLowL0/L1` | X = -12, Z = 0; Y = 0,3.2; .05; 0° |
| `WestMidL0/L1/L2` | X = -6, Z = 0; Y = 0,3.2,6.4; .08 base, .05 above; 0° |
| `CrownL0/L1/L2/L3` | X = 0, Z = 0; Y = 0,3.2,6.4,9.6; .05; 0° |
| `EastMidL0/L1/L2` | X = 6, Z = 0; Y = 0,3.2,6.4; .08 base, .05 above; 0° |
| `EastLowL0/L1` | X = 12, Z = 0; Y = 0,3.2; .05; 0° |
| Five run roofs | .10_straight at each top-storey host root; 0° |
| `WestEndL0/L1` | .07 at (-15.12,0,0) / (-15.12,3.2,0); 180° |
| `EastEndL0/L1` | .07 at (15.12,0,0) / (15.12,3.2,0); 0° |
| `WestEndRoof/EastEndRoof` | .10_end at (-15.12,3.2,0), 180° / (15.12,3.2,0), 0° |
| `WestLowerStep` | Complete .11 at (-9.12,3.2,0); 180° |
| `WestUpperStep` | Complete .11 at (-3.12,6.4,0); 180° |
| `EastUpperStep` | Complete .11 at (3.12,6.4,0); 0° |
| `EastLowerStep` | Complete .11 at (9.12,3.2,0); 0° |
| `WestBalcony/EastBalcony` | .09 at (-6,0,-6) / (6,0,-6); 0° |
| `CrownLowerBalcony/CrownUpperBalcony` | .09 at (0,0,-6) / (0,3.2,-6); 0° |

Each .11 already includes its exposed upper wall and end cap. **Do not add duplicate
.07/.10_end pieces at a step**, stack a complete .11 vertically at one edge, or bury
its cap in another wall. The 0.24 m wall thickness overlaps the lower roof as its
handoff specifies; six-metre bay pitch is unchanged. There is one full bay between
successive drops. No corner-height transition or abrupt multi-storey drop is used.

Terminal walls add 0.24 m only at each exposed end. Roof and balcony geometry already
contains its vertical offset: keep every imported `Visuals/Model` at identity.
Use rigid transforms, not stretching, mirroring or corrective model translations.
No accessible roofs, balconies, stairs, interiors or elevated walkways are introduced.

## Sources, exports and materials

**No new .blend, GLB, texture or material applies to this assembly-only output.**
Every visible mesh traces through unchanged prefab → imported GLB → original committed
Blender source. Seven distinct GLBs, their imports, six sources and seven component
prefabs are hash-pinned in validation. Existing resource identities, opaque Principled
materials, pivots and automatic import LOD settings remain unchanged. No copied mesh
data, downloads, brands, third-party geometry or runtime-generated visible hierarchy.
No operable doors/windows, climbing, destruction states, rigs, clips or authority state.

The palette remains blue-grey render `#829398`, pale frames `#C5CABF`, teal spandrels
`#31656A`, petrol closed glazing `#1E3645`, selective coral `#FF725D`, warm entrances
`#E7B46E` and blue-grey roofs `#526B7B`. Sibling handoffs own slots and authorship.

Tools in `tools/asset_production/d03_apartment_family_04/` follow the earlier assembly
conventions. `author.py` seeds the scene once and refuses to overwrite saved identities.
`check_prefab.gd` normalizes and inspects the real linked scene, checks physics and
production motion, and exports actual model transforms to scratch. `render.py` instances
unchanged linked Blender collections at those transforms without saving a duplicate
source. `export.py` delegates scratch reexports to the original sibling exporters and
shared `tools/assets/blender/export_settings.json`. `validate.py` measures original
source and binary GLB geometry, roof heights, local drops and empty reservations.
`record.py` verifies receipts and generates the lean manifest last. No shared generic
assembly validator exists in this checkout; composition-specific expectations stay
in this asset's allowed tool folder.

## Evidence and measured validation

[Hero](d03_apartment_family_04-evidence/hero.png) ·
[reverse side](d03_apartment_family_04-evidence/side.png) ·
[successive-step detail](d03_apartment_family_04-evidence/assembly_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_04-evidence/overhead_47m_42deg.png).

The producer inspected all four final images, comparing the sibling infill appearance.
Isolated Blender **5.2.2 LTS**, build `d13f752e3b9c`, Cycles CPU, 32 samples, AgX,
RGB PNG compression 100, no dithering. Hero/side are 1152 × 648; detail 1024 × 576;
overhead 1280 × 720. Largest PNG is 415668 bytes (about 406 KiB). The overhead is
vertical-down, north-up at Godot **(0,47,-0.66)**, 42° **vertical FOV**. The central
crown and paired successive terraces remain legible; windows/entry copy are secondary
at gameplay distance. Hero/side show finished ends and four step closures. Detail
intentionally crops outer roofs to inspect two successive wall/flashing junctions.
The ground is studio-only, not delivered paving. These are not Godot captures or
populated-city/moving-camera actor-visibility acceptance.

Measured totals count all repeated instances:

- **55,832 triangles; 29,160 source vertices; 39,308 exported vertices.**
- **41 linked meshes / 137 material surfaces**, not 137 unique materials.
- Zero non-manifold edges, degenerate source faces or actual GLB triangles in all
  seven used dependency meshes; unit source corner/exported normals pass.
- Seven fresh GLBs from six unchanged saved Blender sources are **byte-identical**
  to the delivered dependencies. No source/export is replaced or flattened.
- Actual binary-vertex assembled bounds match engine bounds within 0.001 m.
- **26 actual-triangle first-hit samples** cover all five roof fields, four step
  caps and adjacent lower/upper fields, terminal strips and front/rear coping.
- **144 actual-triangle vertical samples**, three lanes per reservation, find no
  visual geometry over the side/front links. These are bounded unroofed-space checks,
  not perspective actor-occlusion or exhaustive rasterization evidence.
- Seven literal ground rectangles independently match inherited colliders and their
  365.76 m² union. Literal storey levels and all four upper-wall bounds independently
  verify the 2–3–4–3–2 stack and only one-storey local drops.

### Prefab, collision and engine checks

The reference inherits **22 simple static boxes**, layer 1 / mask 0: 14 bay cores,
four terminal walls and four upper step walls. Each retains its sibling collision
owner; no whole-bar hull, new ground plane or collider spans a side link. Roofs,
flashing, shallow trim and inaccessible upper balconies retain existing visual-only
contracts. No walk deck, guard blocker or gameplay state is added. The checker uses
only a temporary invisible physics floor for motion tests.

Pinned **Godot 4.8.dev7.official.c971f93e7** final import and runtime load/check exit 0
without ERROR/SCRIPT ERROR lines or missing dependencies. Live sessions are prohibited
and the windowed editor is unavailable, so the text-authored scene was loaded, packed
and saved headlessly. **Two subsequent byte-stable reload/save cycles** preserve
scene identities, UID and all links. No sibling resource was edited.

- Twenty-one r = 0.35 m / h = 1.8 m capsule solid/clear queries pass, including
  elevated samples on both sides of all four step walls.
- Seventeen physics rays hit expected facade/end/stack and exposed upper-wall planes.
  Terminal seam samples bracket ±1 mm to avoid exact-edge grazing ambiguity; the
  independent ground union proves continuous structural coverage.
- Fifty vertical physics rays find both side links unobstructed.
- A 1.9 × 1.5 × 4.3 m car-sized box sweeps **20 m** down the east bypass clear.
- Eight production **`ActorMotion.step`** runs, four cases × AUTHORITY/REPLAY,
  60 ticks each, pass with identical mode endpoints: side links Z = 2.99999976,
  front seam/balcony bypass X = 6.00000191, closed entry stop Z = -6.35026121 m.
  These are bounded local API checks, not production vehicle handling or multiplayer
  transport/admission/prediction validation.

Final scene receipt, copied from final validation and checked by `record.py --check`:
**6452 bytes**, SHA-256
`bef48d45c0b27c8f84c9798fb90e44115a4cd1d4380a687386973f366e4c7288`.
Prefab UID: `uid://dnlup43t4wvto`. Dependency receipts remain in validation rather than
another duplicate source inventory. [manifest.json](d03_apartment_family_04-evidence/manifest.json)
hashes every produced payload except itself. [Final check log](d03_apartment_family_04-evidence/final-checks.log)
records checks and classified diagnostics.

Tool limitations: editor-mode normalization exits 0 and proves stable serialization,
but emits the same RID/ObjectDB shutdown-leak diagnostics seen in earlier siblings.
Final import/runtime logs are clean; no errors are suppressed. The addon warns this
engine pin is untested. Blender's `use_nodes` deprecation notice concerns Blender 6,
not this pin. Initial hero/side renders were larger; the final lower resolution keeps
the lean evidence target without altering geometry or camera framing. No live session
or production-checks runner was used.

## Exact reproduction

From repository root in Git Bash; scratch logs/reexports stay outside the repository:

```sh
NID=d03_apartment_family_04
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

After intentional revisions, refresh validation and the handoff, run the final pinned
import, then regenerate the manifest with `record.py` without `--check` last. Rendering
is unnecessary merely to recheck unchanged exports. Do not run `production_checks.py`
(owner decision 52).

## Remaining acceptance

- Independent art/technical review of this reference and provisional proportions.
- World-integrator approval of plot fit, heights, entry positions, connected side
  routes/court mouths and actor sightlines in actual saved placements.
- In-engine visual/gameplay-camera and moving-camera review, contextual gameplay,
  production vehicle motion, authoritative transport and packaged dependency checks.
- Repeated-placement draw calls, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, full gameplay or target-device acceptance is claimed. None
of the ten earlier sibling handoffs lists this delivery as a stale pending production
item; their world-context checks remain pending. No sibling doc/manifest edit was
needed. The register, not this handoff, tracks family production progress.
