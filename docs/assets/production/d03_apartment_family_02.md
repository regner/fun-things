# d03_apartment_family.02 — U-shaped open group assembly reference

10 October 2026. **Saved linked reference and bounded checks delivered; independent
review and world acceptance pending.** Commissioned under the [register commission](commission.md),
superseding the concept-only restriction in the [family brief](../d03_apartment_family.md).
Producer: commissioned implementation worker. Accepting art/technical reviewer: unassigned.

## Design and dimensions

An asymmetric **open U** for Terrace Ward: three connected runs, two low corners,
a broad south-facing court mouth and a shorter east arm that leaves a side walking
link. Two storeys throughout, except for one three-storey bay in the north run.
Three warm ground entrances face the court; three selective upper balconies and
quiet blue-grey roof fields retain the delivered kit's appearance. Both exposed
arm ends have finished walls/caps; two complete height-step closures finish the
raised bay. No bespoke building, substitute component or duplicate carrier mesh.

This is an **Assembly reference**, not a new Model output, sector or parcel replacement.
It composes [.05 straight](d03_apartment_family_05.md), [.06 outside corner](d03_apartment_family_06.md),
[.07 end](d03_apartment_family_07.md), [.08 entrance](d03_apartment_family_08.md),
[.09 balcony](d03_apartment_family_09.md), [.10 roofs](d03_apartment_family_10.md) and
[.11 height step](d03_apartment_family_11.md). All seven current handoffs and the
[earlier L reference](d03_apartment_family_01.md) were inspected. The same compact
outside elbow is used at both turns, with rigid rotation rather than mirroring.
The larger inside-corner variant is not needed by this composition.

References: [Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03).
The district's 4.80 ha and greybox footprints are context, not this reference's
allocation. The following run lengths/heights are **provisional authored choices**,
not image measurements, an approved replacement envelope or a city-wide grid.

| Interface | Godot local metres |
| --- | --- |
| Root datum | (0,0,0), ground-level centre of the west elbow |
| Orientation | +X east, +Z south, +Y up; court opens south and southeast |
| Bay / storey pitch | 6 / 3.2 m, unchanged |
| Structural run depth | 12 m, unchanged |
| Ground structural bounds | (-6,0,-6)…(36,3.2,18.24), U-shaped, not a filled bounding box |
| Ground solid footprint area | 725.76 m², including two 0.24 m end walls |
| Whole visual minimum / maximum | (-6.18,0,-6.18) / (36.18,9.92,18.34) |
| Whole visual size X/Y/Z | 42.36 × 9.92 × 24.52 m |
| Low / high roof field | Y = 6.62 / 9.82 |
| Low / high coping top | Y = 6.72 / 9.92 |
| Structural court between arms | X = 6…24, Z > 6; 18 m wide at the narrower rear portion |
| West / east finished structural arm end | Z = 18.24 / 12.24 |
| Dimensional tolerance | ±0.001 m |

The asymmetric pivot preserves the shared elbow datum, not the composition centroid.
Never stretch the modules or apply corrective transforms to their imported models.
The north balconies project to Z = 7.5; the west balcony to X = 7.5, all starting at
Y = 3.2. They do not bridge the court. Reserve these **empty, unroofed connections**:

- South mouth: **X = 10…20, Z = 8…36**, a 10 m-wide central reservation.
- East side link: **X = 15…43, Z = 15…19**, a 4 m-wide reservation passing beyond
  the short arm, at least 2.66 m past its visible end. It is not a tunnel or a gap
  cut through a building. It joins the south mouth inside the court.

Reservations intentionally extend beyond the asset. They are measured empty space,
not authored paths, roads, navigation or approved vehicle traffic. The world
integrator must connect and keep them unoccupied. No circular paving, landscaping
or furniture is supplied; those are not required to prove this kit assembly.

### Saved component interface

`scenes/prefabs/environment/d03_apartment_family_02.tscn` is the runtime placement
owner. [validation.json](d03_apartment_family_02-evidence/validation.json) records all
36 direct instances and 40 transitive GLB instances with actual engine transforms.
No sockets, runtime scripts, material overrides or editable-child overrides.

| Named group | Root positions / Godot +Y yaw / stacking |
| --- | --- |
| `WestCornerL0/L1` | (0,0,0) / (0,3.2,0), outside elbow, 0° |
| `EastCornerL0/L1` | (30,0,0) / (30,3.2,0), outside elbow, -90° |
| `NorthA` | (9,0,0), two storeys; base entrance 180°, upper bay 0° |
| `NorthB` | (15,0,0), three straight storeys at Y = 0,3.2,6.4; 0° |
| `NorthC` | (21,0,0), two straight storeys; 0° |
| `WestA` | (0,0,9), two straight storeys; +90° |
| `WestB` | (0,0,15), two storeys; base entrance -90°, upper bay +90° |
| `EastA` | (30,0,9), two storeys; base entrance and upper bay +90° |
| `WestEnd` | (0,0,18.12) / (0,3.2,18.12), .07, -90° |
| `EastEnd` | (30,0,12.12) / (30,3.2,12.12), .07, -90° |
| Roofs | Matching .10 cap at each top-storey host transform, including both ends |
| `RiseWest` / `FallEast` | Complete .11 at (11.88,3.2,0), 180° / (18.12,3.2,0), 0° |
| `NorthCourtBalconyLower/Upper` | .09 at (15,0,6) / (15,3.2,6), 180° |
| `WestCourtBalcony` | .09 at (6,0,9), -90° |

The .11 already includes its exposed upper wall and end cap; do not duplicate them.
Its 0.24 m wall overlap into the low roof is the documented hidden junction, not a
change in bay pitch. Each drop is one storey and away from the elbows. No abrupt
multi-storey or corner-height transition. Roof/balcony geometry already contains
its vertical offset; keep every `Visuals/Model` at identity.

## Sources, exports and materials

**No new .blend, GLB, texture or material applies to this assembly-only output.**
All visible geometry traces through unchanged prefab → original GLB → committed
Blender source. Nine distinct GLBs, their imports, seven sources and nine component
prefabs are hash-pinned in validation. Original identities, opaque Principled
materials and automatic import LOD settings remain intact. No copied mesh data,
new brand, download, third-party geometry or runtime-generated visible hierarchy.

The palette remains blue-grey render `#829398`, pale frames `#C5CABF`, teal spandrels
`#31656A`, petrol closed glazing `#1E3645`, selective coral `#FF725D`, warm entrances
`#E7B46E` and blue-grey roofs `#526B7B`. Component handoffs own the slots/authorship.
No interiors, operable doors/windows, climbing, accessible balconies/roofs, rigs,
clips, destruction, new gameplay state or physics authority is introduced.

Tools in `tools/asset_production/d03_apartment_family_02/` follow the earlier L-reference
convention. `author.py` seeds the scene once and refuses to overwrite saved identities;
subsequent changes are made to the saved scene. `check_prefab.gd` performs headless
normalization, dependency/bounds inspection, physics and production motion checks,
and exports actual model transforms to scratch. `render.py` instances unchanged
linked Blender collections at those transforms, without saving a duplicate source.
`export.py` delegates to the existing sibling exporters and shared export settings,
writing scratch only. `validate.py` measures original topology, actual binary GLB
triangles, assembled roofs/open links and ground colliders. `record.py` verifies
final receipts and generates the lean producer manifest. No shared generic assembly
tool exists; composition-specific assertions stay in this asset's allowed tool folder.

## Evidence and measured validation

[Hero](d03_apartment_family_02-evidence/hero.png) ·
[reverse side](d03_apartment_family_02-evidence/side.png) ·
[court/step detail](d03_apartment_family_02-evidence/assembly_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_02-evidence/overhead_47m_42deg.png).

All four final images were inspected by the producer. Isolated Blender **5.2.2 LTS**,
build `d13f752e3b9c`, Cycles CPU, 32 samples, AgX, RGB PNG compression 100, no dithering.
Hero/side/overhead are 1280 × 720; detail is 1024 × 576. Largest PNG is 420702 bytes
(about 411 KiB). The overhead is vertical-down, north-up at Godot **(15,47,6.08)**,
42° **vertical FOV**. The asymmetric U, low corners, central rise and open mouth/side
remain legible. The detail intentionally crops outer roofs to inspect the mounted
balconies, step junction and entrance treatment. The court backdrop is studio-only,
not delivered paving. These are not Godot captures or populated-city visibility proof.

Measured totals count every repeated instance:

- **68,820 triangles; 35,924 source vertices; 48,282 exported vertices.**
- **40 linked meshes / 144 material surfaces; 36 direct component instances.**
- Zero non-manifold edges, degenerate source faces or actual GLB triangles in all
  nine used dependency meshes; unit source corner and exported normals pass.
- Nine fresh GLBs from the seven unchanged saved Blender sources are **byte-identical**
  to their delivered dependencies. No source or export was replaced or flattened.
- Actual binary-vertex assembled bounds match engine bounds within 0.001 m.
- **19 actual-triangle first-hit roof samples** check all four elbow/run connectors,
  both roof levels, both end strips and the rotated east elbow's exterior coping.
- **90 actual-triangle vertical samples**, three lanes per connection, find no visual
  geometry over either reservation. These are bounded unroofed-space samples, not
  perspective actor-occlusion, moving-camera or exhaustive rasterization evidence.
- Ten literal ground rectangles independently match the actual inherited colliders,
  including connector endpoints and end-wall extensions; their union is 725.76 m².

### Prefab, collision and engine checks

The reference inherits **23 static boxes**, layer 1 / mask 0: 17 bay/elbow cores,
four terminal walls and two upper step walls. No whole-U hull or collider spans the
court. Each component retains its existing collision owner. Roofs, flashing, shallow
trim and inaccessible elevated balconies retain their visual-only contracts. No new
walk deck, railing blocker or floor is added. The checker uses a temporary invisible
physics floor only for motion tests, never a prefab dependency.

Pinned **Godot 4.8.dev7.official.c971f93e7** final import and runtime load/check exit 0
without ERROR/SCRIPT ERROR lines or missing dependencies. Live sessions are prohibited
and the windowed editor is unavailable, so text-authored placement was loaded, packed
and saved headlessly. **Two subsequent byte-stable reload/save cycles** preserve
scene identities, UID and original dependency links. No sibling resource was edited.

- Sixteen r = 0.35 m / h = 1.8 m capsule solid/clear queries pass.
- Twelve physics seam/height-step rays hit the expected facade planes. Rotated corner
  and terminal seam boundaries are bracketed at ±1 mm to avoid exact-edge grazing
  ambiguity; the independent collider rectangles verify contiguous connector bounds.
- Fifty-six vertical physics rays find both connections unblocked.
- A 1.9 × 1.5 × 4.3 m car-sized box sweeps **22 m east** beyond the short arm clear.
- Eight production **`ActorMotion.step`** runs, four cases × AUTHORITY/REPLAY, 60 ticks
  each, pass with identical mode endpoints: east link X = 26.00003815, south mouth
  Z = 22.00003815, north seam bypass X = 9.00000381 and closed court-entry stop
  Z = 6.35026121 m. These are bounded local API checks, not vehicle driving or
  multiplayer transport/admission/prediction validation.

Final scene receipt, copied from final validation and checked by `record.py --check`:
**7306 bytes**, SHA-256
`c44973dc68c5a33cd2ad8f9345f5b0f69d91c5ec45efcb9cb36064f7b1cce473`.
Prefab UID: `uid://b2n6vu3s8vvq`. Dependency receipts are in validation rather than
copied into another source inventory. [manifest.json](d03_apartment_family_02-evidence/manifest.json)
indexes every produced payload except itself. [Final check log](d03_apartment_family_02-evidence/final-checks.log)
records results and classified diagnostics.

Tool limitations: editor-mode normalization proves stable saves and exits 0, but
emits the same headless RID/ObjectDB shutdown-leak diagnostics observed in earlier
siblings. Final import/runtime checks are clean; no errors are suppressed. The addon
warns this engine pin is untested. Initial checks caught reversed text-serialized
yaw signs and an exact rotated-edge grazing ray. The owned scene/seed signs and
bracketed ray were corrected before the final checks/renders. No live session was used.

## Exact reproduction

From repository root in Git Bash; scratch logs/exports stay outside the repository:

```sh
NID=d03_apartment_family_02
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

After intentional revisions, refresh validation and the handoff, run the final
pinned import, then regenerate the manifest with `record.py` without `--check` last.
Rendering is not necessary merely to recheck unchanged source exports. Do not run
`production_checks.py` (owner decision 52).

## Remaining acceptance

- Independent art/technical review of this reference and provisional proportions.
- World-integrator approval of plot fit, storey counts, connected court mouth/side
  routes, actual entrance placement and actor sightlines in saved world placements.
- In-engine visual/gameplay-camera and moving-camera review, contextual gameplay,
  production vehicle motion, authoritative transport and packaged dependencies.
- Repeated-placement draw calls, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, full gameplay or target-device acceptance is claimed. None
of the eight earlier sibling handoffs lists this delivery as a stale pending production
item: their world-context checks remain pending. No sibling doc/manifest edit was
needed. The register, not this handoff, tracks the other family records.
