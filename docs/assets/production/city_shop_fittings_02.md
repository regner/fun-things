# city_shop_fittings.02 — flat shop fascia frame

Source/export candidate, 9 October 2026; produced by the assigned per-asset worker
for ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2`. Model/source and explicit-export
checks pass. Independent art acceptance and engine import, linked prefab,
save/reopen, actual facade attachment, collision/query/runtime/multiplayer,
device/performance and world placement remain **pending**. No READY claim.
Commission `commission.md` at `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`
authorizes production and reversible interface refinement beyond the old draft.
The frozen six-asset engine candidate was not touched. No Git/index, shared docs,
shared editor, Godot, project, prefab or world writes were performed.

## Source, design and provenance

- Source: `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`
- Collection: `export_city_shop_fittings_02`; root: `city_shop_fittings_02`.
- Export: `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb`.
- Original authoring/reproduction: `tools/asset_production/city_shop_fittings_02/`.
- Authoritative evidence: `docs/assets/production/city_shop_fittings_02-evidence/`.

Original Blender-authored continuous formed perimeter, slim ivory trim, recessed
artwork insert/reveal, backing tray and two wall rails. Seven editable meshes,
eight material primitives, five materials, 1,656 triangles; no external geometry,
production textures, fonts, tenant names or district graphics. Rounded profiles
and applied weighted normals provide broad manufactured highlights. Solids overlap
intentionally at assembly joints; this is visual hardware, not an engineered
hollow enclosure. The insert seats 3 mm into its backing tray.

Signal Row v03's repeated horizontal fascia bands, Crescents v02's quiet corner
shop and Old Quay v03's warm shop-home fronts inform the broad silhouette and
restrained trim. Their raster dimensions were not used as measurements. Canopy
`.01` report and hero were read-only style/interface references; slate-petrol and
ivory coordinate without importing or depending on its unfinished source/export.
This 3.2 m commercial fitting differs from the 1.4 × 1.0 m civic/poster panel
`city_sign_supports.01`. No second panel source or graphic mesh is supplied.
Mesh/profile, exporter and accessor-check helper patterns were adapted read-only
from that asset's tools; all fascia geometry and its diagnostic chart are original.
The unchanged greybox shop GLB is a preview scale reference only.

## Metre attachment and artwork contract

Pivot is the centre of the fascia on its wall-contact plane, not a ground origin.
Blender +Y faces outward and +Z up; one glTF Y-up conversion gives Godot -Z outward,
+Y up. Every exported object's location/rotation is zero and scale is one.
Geometry is authored around the shared datum; modifiers are applied.

| Measurement | Contract |
| --- | --- |
| Width / height / projection | 3.200 / 0.800 / 0.140 m |
| Blender AABB | min (-1.600, 0.000, -0.400), max (1.600, 0.140, 0.400) m |
| Godot AABB | min (-1.600, -0.400, -0.140), max (1.600, 0.400, 0.000) m |
| Bounds tolerance | ±0.001 m per bound; automated numerical checks are stricter |
| Wall datum | Blender Y=0 / Godot Z=0; flat vertical bay, mounting placement ±0.002 m |
| Mount rails | 2.880 × 0.045 × 0.085 m in Blender X/Y/Z; Z centres ±0.240 m; rear Y=0 |
| Back tray / wall gap | tray rear Y=0.028 m; rail contacts are the only wall contact |
| Reserved fitting volume | X ±1.700, Blender Y -0.020–0.240, Z ±0.450 m |
| Suggested pivot height | 3.800 m above finished ground; lowest geometry 3.400 m |
| Adjacent fittings | ≥0.100 m physical gap; flat bay ≥3.400 m wide; reject curved/corner mounting |
| Artwork face | 3.000 × 0.600 m, 5:1 aspect; plane Blender Y=0.128 / Godot Z=-0.128 |
| Face corners / safe content | radius 0.012 m; keep important content inside centred 2.940 × 0.540 m |

The canopy reference uses the same wall datum/axis and 3.2 m width. If its proposed
3.0 m pivot and 0.24 m top extent are retained, this fascia at 3.8 m leaves 0.16 m
between visible bounds. This is arithmetic compatibility, not a tested assembly
or a dependency. Verify actual shell dimensions, canopy revision and clearances
before placement. No wall holes, fasteners, loads, collision, interiors, opening
mechanics, animations or runtime sign generation are claimed.

`fascia_artwork_carrier` has stable slots **0 `fascia_artwork_face`** (front only)
and **1 `fascia_mount_metal`** (sides/back). Only slot 0 should receive the separately
authored district material; use the material name, not assumed global GLB index.
UV0 spans the full face: source U=0 at Blender X=+1.5, U=1 at X=-1.5;
V=0 at Z=-0.3, V=1 at Z=+0.3. This is left-to-right and bottom-to-top when
viewed from the outward front. glTF stores V flipped; the decoder independently
checks all 28 front boundary samples. Map a 5:1 image without mirroring; use clamp,
with background bleed into the rounded corners. Do not add another coplanar panel.
Runtime image resolution/filtering/emission/remapping belongs to the graphics and
integration owners. The scratch 1500 × 300 chart is evidence only, never packed,
saved in the production source or exported.

## Materials and density

All five materials are opaque, single-sided Principled/glTF PBR with no emission,
alpha blending, textures or tangent requirement. sRGB swatches are converted to
linear base colours in Blender. No external `.tres` or texture dependencies.

| Material | sRGB swatch | Metallic / roughness | Mesh use |
| --- | --- | --- | --- |
| fascia_slate_petrol | #405B68 | .25 / .46 | formed frame, backing tray |
| fascia_warm_trim | #C8C2AD | .22 / .48 | continuous trim |
| fascia_recess | #23333B | 0 / .72 | artwork reveal |
| fascia_artwork_face | #C3C7BC | 0 / .56 | front face only; replaceable |
| fascia_mount_metal | #384850 | .45 / .50 | rails, insert back/sides |

Triangle counts: frame 392, trim 336, tray 164, reveal 224, insert 164,
two rails 188 each. No rig, clips, sockets or LODs are needed for this static
candidate; no measured device budget is implied. Source retains Blender's unused
startup `Material` plus internal `Render Result`/`Viewer Node` handles; none enters
the GLB. The sole excluded object is the exact 1 × 1 × 1 m authoring reference.
Measured width/reference ratio is 3.2; `measured_1m_comparison.png` shows both.

## Validation, limits and reproduction

`source_checks.json`, `glb_checks.json`, `reexport_checks.json` and
`final_audit.json` pass: exact collection/node membership, applied transforms,
finite positions/unit normals, closed manifold consistently wound solids,
positive signed volumes, nondegenerate faces/triangles, triangle-vs-normal winding,
material scope, artwork plane/UV orientation, axis conversion, source/export bounds,
reference/studio exclusion and **saved-source byte-identical GLB re-export**.
The standalone GLB decoder does not import the authoring/exporter implementation.
`manifest.json` is the exact expected relative path/byte/SHA256 inventory, excluding
only the manifest itself. Initial candidate source/export/checks/previews are
retained under `initial/`, explicitly not current delivery files.

`hero.png`, `rear_mounts.png`, `measured_1m_comparison.png` and
`artwork_interface.png` were visually inspected: broad smooth face and quiet trim,
shallow rails, correct TL/TR/BL/BR labels and right/up arrows. No obvious exposed
coplanar flicker or inverted surfaces was observed. This is self-review only.
`unchanged_shop_scale_comparison.png` uses the hashed, unchanged 18 × 15 × 10 m
shop. `project_camera.png` uses straight-down fixed-yaw perspective, 47 m / 42°
vertical FOV, 1280 × 800. At that distance the vertical fascia is a thin dark edge
with little face visibility; text readability/roof occlusion remains unresolved.
These unsaved Blender previews are not Godot captures or gameplay acceptance.
`preview_checks.json` records reference hashes, bounds and all camera transforms.

Exact successful and failed argv, process-local environment, durations and exits
are in `execution.json`; full combined logs remain alongside. `requested_pin.log`
also preserves the initial wrapper failure before launch-error recording was fixed.
Diagnostics and corrections:

- Requested `/usr/bin/blender5.2.2LTS` is absent: initial wrapper exit 1, recorded
  launch retry 127. `/usr/bin/blender` verifies 5.2.2 LTS `d13f752e3b9c`, exporter
  5.2.40 before authoring; no engine/version substitution was made.
- Initial author/export exit 1: adapted UV checker retained civic-panel dimensions.
  Corrected to the fascia's 3.0 × 0.6 m interface, then passed saved-source export.
- Initial scratch-chart exit 1: system Python lacks Pillow. Replaced the small
  diagnostic generator with standard-library PNG writing; no packages installed.
- One geometry fix cycle seated the insert into the tray (rear .117 → .070 m).
  Rebuilt source/GLB and reran fresh re-export, decoder and all six previews.
- Initial extra final-audit exit 1 rejected Blender's internal viewer image handles.
  Inventory proved these were `VIEWER` handles with no paths; the precise check now
  permits those only while still rejecting external texture images. Final audit passes.
- Exporter logs absent optional MeshOptimizer library as `ERROR`; compression is
  unused, raw GLB decoding and exact re-export pass. `use_nodes` future-deprecation
  warnings and BlenderMCP addon startup/shutdown messages remain unsuppressed.
  Private CLI only: no connector/shared live editor or global configuration access.

Reproduce from repository root (use new log labels; runner refuses overwriting logs):

```sh
python tools/asset_production/city_shop_fittings_02/run.py verify_again /usr/bin/blender -b -noaudio -t 4 art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend --python-exit-code 1 --python tools/asset_production/city_shop_fittings_02/export.py -- docs/assets/production/city_shop_fittings_02-evidence/reexport_city_shop_fittings_02.glb docs/assets/production/city_shop_fittings_02-evidence/reexport_checks.json
python tools/asset_production/city_shop_fittings_02/check_glb.py
```

`author.py` rebuilds the original editable source; `make_uv_diagnostic.py` then
`preview.py` reproduce previews. Full argv are in the receipt. All Blender jobs
use `-noaudio -t 4`, `ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy` and an owned local
cache. `manifest.py` creates the final inventory; `manifest.py --verify` checks it.
All owned authoring/render/export processes are complete at handoff. Available
for concrete independent review findings; downstream gates stay with ROOT/integrator.
