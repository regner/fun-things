# d03_apartment_family.01 — L-shaped apartment group assembly reference

10 October 2026. **Saved linked reference and bounded checks delivered; independent
review and world acceptance pending.** Commissioned under the [register commission](commission.md),
superseding the concept-only restriction in the [family brief](../d03_apartment_family.md).
Producer: commissioned implementation worker. Accepting art/technical reviewer: unassigned.

## Design and dimensions

An L-shaped Terrace Ward group with **two-storey low corners and a three-storey
accent on one straight bay**. Two unequal runs frame an open southeast court. Two warm
entrances face that court; selective balconies, coral terminal/corner accents and
quiet blue-grey roof fields retain the seven delivered modules' appearance. Both run
ends are finished, all hosts have matching roof caps, and two one-storey step closures
finish the raised bay. There is no bespoke building mesh or duplicate carrier.

This is an **Assembly reference**, not a new Model output, world sector or parcel
replacement. It composes existing prefabs from [.05](d03_apartment_family_05.md),
[.06](d03_apartment_family_06.md), [.07](d03_apartment_family_07.md),
[.08](d03_apartment_family_08.md), [.09](d03_apartment_family_09.md),
[.10](d03_apartment_family_10.md) and [.11](d03_apartment_family_11.md).
All seven current handoffs and interfaces were inspected. The compact outside elbow
is sufficient here; the inside-corner variant is not required or duplicated.

References: [Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03).
The district's 4.80 ha and greybox footprints are context, not this asset's allocation.
Run lengths and heights below are **provisional authored composition choices**, not
measurements from concept imagery, an accepted replacement envelope or a city-wide grid.

| Interface | Godot local metres |
| --- | --- |
| Root datum | (0,0,0), centre of the compact elbow at ground level |
| Orientation | +X east, +Z south, +Y up; court opens east and south |
| Bay / storey pitch | 6 / 3.2 m, unchanged |
| Structural run depth | 12 m, unchanged |
| Ground structural bounds | (-6,0,-6)…(24.24,3.2,18.24), L-shaped, not a solid bounding box |
| Ground solid footprint area | 509.76 m² including both 0.24 m terminal walls |
| Whole visual minimum | (-6.18,0,-7.50) |
| Whole visual maximum | (24.34,9.92,18.34) |
| Whole visual size X/Y/Z | 30.52 × 9.92 × 25.84 m |
| Low / high roof field | Y = 6.62 / 9.82 |
| Low / high coping top | Y = 6.72 / 9.92 |
| Dimensional tolerance | ±0.001 m |

The asymmetric pivot deliberately retains the elbow's reusable connector datum;
it is not the whole composition's area centroid. No root correction or mesh scaling.
The nominal unbuilt court sector lies beyond X = 6 and Z = 6, with no enclosing east
or south wall. The balcony projects to X = 7.5 over part of its west edge, starting
at Y = 3.2. Keep the conceptual **4 m-wide east link at Z = 10…14, X = 8…32** and
**south link at X = 10…14, Z = 8…32** unoccupied when using this reference. These are
checked empty reservations, not authored paths, roads, navigation or approved traffic.
They extend beyond this asset so a world integrator can connect them deliberately.

### Saved component interface

`scenes/prefabs/environment/d03_apartment_family_01.tscn` is the sole runtime placement
owner. `validation.json` lists all 30 direct instances and 34 transitive GLB instances
with their measured transforms. Static numeric datums are the interface; no sockets,
custom gameplay scripts, material overrides or editable-child overrides are added.

| Named group | Root positions / yaw / stacking |
| --- | --- |
| `CornerL0/L1` | Outside elbow at (0,0,0) / (0,3.2,0), yaw 0° |
| `EastA` | (9,0,0), two storeys; base entrance yaw 180°, upper bay yaw 0° |
| `EastB` | (15,0,0), three straight storeys at Y = 0,3.2,6.4; yaw 0° |
| `EastC` | (21,0,0), two straight storeys; yaw 0° |
| `SouthA` | (0,0,9), two straight storeys; yaw +90° |
| `SouthB` | (0,0,15), two storeys; base entrance yaw -90°, upper bay yaw +90° |
| `EastEnd` | (24.12,0,0) / (24.12,3.2,0), .07, yaw 0° |
| `SouthEnd` | (0,0,18.12) / (0,3.2,18.12), .07, yaw -90° |
| Roofs | One matching cap at each top-storey host transform, including both ends |
| `RiseWest` | Complete .11 at (11.88,3.2,0), yaw 180° |
| `FallEast` | Complete .11 at (18.12,3.2,0), yaw 0° |
| `EastBalconyLower/Upper` | .09 at (15,0,-6) / (15,3.2,-6), yaw 0° |
| `SouthCourtBalcony` | .09 at (6,0,9), yaw -90° |

The .11 instances already contain their upper walls and end caps: do not add duplicates.
Their 0.24 m wall thickness overlaps the low roof as specified by .11; bay pitch stays
6 m. Neither step touches the elbow. No abrupt multi-storey or corner-height transition
is introduced. Roof and balcony source geometry already includes its documented
vertical offset; never translate `Visuals/Model` to compensate a second time.

## Sources, exports and materials

**No new .blend, GLB, texture or material is applicable to this assembly-only output.**
All visible geometry traces through existing prefab → original GLB → committed Blender
source. Nine distinct GLBs across seven source files are pinned, with their `.import`
files and nine linked prefab receipts, in [validation.json](d03_apartment_family_01-evidence/validation.json).
The assembly keeps original identities, opaque Principled materials, automatic import
LOD settings and each child's identity-transform `Visuals/Model` instance. No imported
mesh data is copied into the scene. No downloads, brands, third-party geometry or
runtime-generated visible hierarchy was introduced.

The palette is unchanged: blue-grey render `#829398`, pale frames `#C5CABF`, teal
spandrels `#31656A`, closed petrol glazing `#1E3645`, selective coral `#FF725D`, warm
entries `#E7B46E`, and blue-grey roofs `#526B7B`. Existing module handoffs own material
slots and original authorship. There are no interiors, functioning doors/windows,
climbing, accessible balconies/roofs, destruction states, rigs or animation.

Tools in `tools/asset_production/d03_apartment_family_01/`:

- `author.py`: one-time seed construction of the saved reference; refuses to overwrite
  an existing scene so subsequent edits preserve saved identities. Not a runtime writer.
- `check_prefab.gd`: pinned engine normalization, real dependency/geometry inspection,
  physics and production `ActorMotion` checks; exports actual scene transforms to scratch.
- `render.py`: instances unchanged linked Blender collections using those actual transforms.
  No saved duplicate Blender scene. Studio plane/lights/camera are evidence-only.
- `export.py`: delegates fresh dependency exports to the existing sibling exporters and
  shared `tools/assets/blender/export_settings.json`; writes only scratch exports.
- `validate.py`: checks source topology, actual binary GLBs, assembled bounds/roof/link
  samples, strict re-export equality and engine receipt; emits final validation.
- `record.py`: generates/checks the final producer manifest and dependency receipts.

## Evidence and measured validation

[Hero](d03_apartment_family_01-evidence/hero.png) ·
[reverse side](d03_apartment_family_01-evidence/side.png) ·
[step / entry / court detail](d03_apartment_family_01-evidence/assembly_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_01-evidence/overhead_47m_42deg.png).

The producer inspected all four final images. Isolated Blender **5.2.2 LTS**, build
`d13f752e3b9c`, Cycles CPU, 32 samples, AgX, RGB PNG compression 100, no dithering.
Hero, side and overhead are 1280 × 720; detail is 1024 × 576. Largest PNG is 419355
bytes (about 410 KiB). The overhead is vertical-down, north-up, 47 m above ground,
42° **vertical FOV**, camera at Godot (9.08,47,5.42). The L silhouette, open southeast
court and raised straight bay remain distinct; fine windows/entry copy are secondary.
The court backdrop is a studio surface, not a delivered paving material. These are
not Godot captures or populated-city visibility acceptance.

Measured totals count all repeated instances, not just unique files:

- **53,364 triangles; 27,860 source vertices; 37,464 exported vertices.**
- **34 linked meshes / 119 material surfaces; 30 direct component instances.**
- Zero degenerate source faces, actual GLB triangles or non-manifold edges in all nine
  used dependency meshes; unit source corner and exported normals pass.
- Nine fresh GLBs exported from the seven unchanged committed Blender sources are
  **byte-identical** to their delivered dependencies. No source/export was replaced.
- Actual assembled binary-GLB vertex bounds and engine bounds agree within 0.001 m.
- Eleven actual triangle first-hit samples cover roof fields, both elbow/run joins,
  raised bay and both terminal strips. No roof geometry bridges the court.
- Seventy-eight actual-GLB vertical samples across three lanes in each open link find
  no visual surface. This is bounded sampling, not an exhaustive occlusion proof.

### Prefab, collision and engine checks

The scene inherits **19 simple static boxes**, layer 1 / mask 0: 13 bay/elbow cores,
four ground/second-storey end closures and two exposed upper-step walls. Every box is
owned by its linked sibling, not a new whole-L hull. No collider spans the court.
Shallow trim, roofs, flashing and the inaccessible elevated balconies retain their
existing visual-only contracts; no new floor, walk deck, rail or authority state.
The checker creates only a temporary invisible physics floor for motion tests.

Pinned **Godot 4.8.dev7.official.c971f93e7** headless import and runtime checks exit 0
with no ERROR/SCRIPT ERROR lines or missing dependencies. The scene was authored as
text because live sessions are prohibited and the windowed editor is unavailable,
then loaded, packed and saved headlessly. **Two subsequent byte-stable reload/save
cycles** preserve all scene identities and links. No sibling resource was rewritten.

- Eleven r = 0.35 m / h = 1.8 m capsule solid/clear queries pass.
- Eight seam/height-step rays hit the expected facade planes. At the rotated south
  terminal seam the two rays bracket the boundary by ±1 mm to avoid a floating-point
  grazing-ray ambiguity; the compound core geometry remains contiguous within tolerance.
- Forty-eight vertical physics rays find the east and south links unblocked.
- A 1.9 × 1.5 × 4.3 m car-sized box sweeps 18 m east through the court unobstructed.
- Eight production `ActorMotion.step` runs (four cases × AUTHORITY/REPLAY, 60 ticks
  each) pass with identical mode endpoints: east link X = 12.99998093, south link
  Z = 12.99998093, north connector bypass X = 9.00000381, closed court-entry stop
  Z = 6.35026121 m. These are local API tests, not vehicle handling or network transport.

Final scene receipt, copied from final validation and verified by `record.py --check`:
**6260 bytes**, SHA-256
`cbcfaede55bba1e7dafe25b8a635fbd30972a6afb8e96f0ffd1a42f51efb034a`.
Prefab UID: `uid://c76lfes4bx387`. All dependency hashes are in validation rather than
copied into a second source inventory. [manifest.json](d03_apartment_family_01-evidence/manifest.json)
indexes every produced payload except itself. [Final check log](d03_apartment_family_01-evidence/final-checks.log)
records checks and classified diagnostics.

Tool limitations: editor normalization exits 0 and proves stable serialization but
emits the same headless RID/ObjectDB shutdown-leak diagnostics observed in earlier
siblings. Final import/runtime checks are clean; no errors are suppressed. The addon
warns that this pinned engine version is untested. Initial checks caught reversed
text-serialized yaw signs, an extra imported-root ancestry level, and a grazing ray
at the rotated terminal edge. The owned scene/seed and checker were corrected before
final checks and renders. Initial RGBA evidence was larger; final RGB/detail resolution
keeps the lean evidence budget. No live Blender or Godot session was used.

## Exact reproduction

From the repository root in Git Bash; raw logs and exports stay outside the repository:

```sh
NID=d03_apartment_family_01
TOOLS=tools/asset_production/$NID
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
mkdir -p C:/tmp/ft/assets/$NID
# Only for a fresh scene with no saved identities: python "$TOOLS/author.py"
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . --script "$TOOLS/check_prefab.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "$TOOLS/check_prefab.gd"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8 timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/render.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8 timeout 300 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/validate.py"
mise exec -- gdstyle fmt --check "$TOOLS/check_prefab.gd"
mise exec -- gdstyle --max-line-length 100 --max-warnings 0 "$TOOLS/check_prefab.gd"
python "$TOOLS/record.py" --check
```

After intentional revisions, refresh validation and this handoff, run the final pinned
import, then regenerate the manifest with `record.py` without `--check` last. Rendering
is not needed merely to recheck the unchanged source exports. Do not run
`production_checks.py` (owner decision 52).

## Remaining acceptance

- Independent art/technical review of this saved reference and provisional proportions.
- World-integrator approval of plot fit, final storey counts, court mouths, connected
  walking routes, entry positions and actor sightlines in actual saved placements.
- Actual in-engine visual/gameplay-camera and moving-camera review, contextual gameplay,
  production vehicle motion, authoritative transport and packaged dependency checks.
- Repeated-placement draw calls, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, full gameplay or target-device acceptance is claimed. None
of the seven earlier sibling handoffs contains a stale pending production item resolved
by this delivery: their world-context checks remain pending. No sibling doc/manifest
edit was needed; the register owns other family records' progress.
