# city_shop_fittings.07 — broad upper-floor window group

Original source/export candidate, 9 October 2026, for ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2`. Production and reversible dimensions are
commissioned beyond the old concept-only brief. **Not READY:** independent acceptance,
Godot import/prefab/save-reopen, actual-shell attachment, collision/query/runtime,
multiplayer and device/performance gates remain pending. No shared assets, project,
prefab, world, index or frozen six-asset candidate were changed.
User requested Astra MEDIUM; this worker cannot independently inspect or switch its
host model configuration, so effective model/effort is not certified in this report.
No subagents or live/shared editor sessions were used.

## Source and provenance

- Editable source: `art/source/models/environment/city_shop_fittings_07/city_shop_fittings_07.blend`.
- Collection/root: `export_city_shop_fittings_07` / `city_shop_fittings_07`.
- Explicit game GLB: `art/models/environment/city_shop_fittings_07/city_shop_fittings_07.glb`.
- Reproduction: `tools/asset_production/city_shop_fittings_07/`.
- Authoritative evidence: [city_shop_fittings_07-evidence/](city_shop_fittings_07-evidence/).
- Exact expected file/byte/SHA256 inventory: [manifest.json](city_shop_fittings_07-evidence/manifest.json).

Original Blender-authored profile meshes: continuous stepped insertion sleeve and
rounded face flange, narrow ivory glazing bead, three closed gaskets and opaque
panes, two meeting stiles and a folded shallow drip shoe. Eleven separately editable
meshes with applied normals/modifiers. The broad centre light is approximately twice
a side light; no transoms, dense grid, detailed interior, animation, opening mechanic,
tenant artwork, lighting behavior or essential wayfinding role. No external mesh,
texture, font, generated asset or library supplied production geometry. No external
license/attribution dependency. Source was not derived from another asset's GLB.

Read commission at `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661` (raw snapshot retained),
AGENTS.md, assets.md, art-direction.md, city_shop_fittings.md, Signal Row/Old Quay
texts, breakdowns and v03 images. Their broad upper-façade rhythm guides this original
composition; raster dimensions were not measured. Completed `.01/.02/.03/.05` reports
informed common slate-petrol/ivory trim. Exporter/decoder/receipt/manifest patterns
were adapted read-only from `.05`; its geometry and outputs were neither copied nor
changed. This wide, low three-light upper group differs from `.05`'s taller two-light
shop display bay. Shell structural wall opening and masonry trim remain shell-owned.

## Metre interface v1

Pivot `(0,0,0)` is the lower centre at the façade plane, an attachment datum above
ground when placed. Blender +Y front/+Z up maps once to Godot -Z front/+Y up:
`(X,Y,Z) → (X,Z,-Y)`. All exported objects/root have zero location/rotation and unit
scale; offsets are in mesh data. No corrective root scale or rotation is needed.

| Measurement | Contract in metres |
| --- | --- |
| Width × height × total depth | 4.800 × 1.600 × 0.310 |
| Blender bounds | min (-2.400,-0.160,0.000), max (2.400,0.150,1.600) |
| Godot-axis bounds | min (-2.400,0.000,-0.150), max (2.400,1.600,0.160) |
| Shell rectangular rough opening | X [-2.340,2.340], Z [0.060,1.540]; 4.680 × 1.480 |
| Insertion sleeve envelope | X ±2.320, Z [0.080,1.520], rear Y=-0.160 |
| Nominal opening clearance | 20 mm per jamb/head/bottom; rear void to Y≤-0.180 |
| Flange back / front | Y=0.010 / 0.074; 10 mm façade stand-off |
| Ivory bead front | Y=0.081; nonstructural glazing bead |
| Opaque pane sizes X/Z/depth | centre 2.250/1.310/0.098; sides 1.070/1.310/0.098 |
| Pane centres X/Z and depth | X=0, ±1.725; Z=0.800; Y=[-0.074,0.024] |
| Meeting stile centres / max width | X=±1.150; width 0.086; front Y=0.074 |
| Drip shoe | X ±2.400, Y [0.010,0.150], Z [0,0.063] |
| Suggested upper-floor pivot | 4.650 above ground; fitting top 6.250 |
| Bounds tolerance / placement tolerance | ±0.001 per bound / ±0.002 translation, axes aligned |
| Reserved installation envelope | X ±2.500, Y [-0.180,0.250], Z [-0.100,1.700] |

Install only in a flat wall with the declared hole and rear void; do not overlay an
uncut wall. The flange covers the rectangular rough opening by 60 mm nominally;
rounded outer corners retain coverage. The sleeve's 20 mm nominal clearance becomes
at least 18 mm under the stated translation tolerance. Opening fabrication tolerance
is not certified. Keep unrelated shell trim/fittings ≥100 mm outside visible bounds,
and use flat frontage at least 5.0 m wide. Reject undersized/curved/corner mounting
rather than stretching the fitting. The drip shoe is part of the removable window,
not an additional structural shell sill. Assembly solids overlap intentionally at
joints; no engineered weather seal or load-bearing capacity is claimed.

At the suggested elevation the window sits 450 mm above `.02`'s proposed 4.2 m fascia
top, 1.41 m above `.01`'s proposed canopy top and 2.17 m above `.03/.05`'s 2.48 m tops.
These are arithmetic separation checks, not a tested combined frontage or an accepted
floor-height rule. Collision stays with downstream prefab/shell owners.

## Materials and density

Five embedded opaque, single-sided Principled/glTF PBR materials, sRGB swatches
converted to linear base colours. One slot (index 0) per named mesh.

| Mesh use | Material / sRGB | Metallic / roughness |
| --- | --- | --- |
| continuous_window_frame, *_meeting_stile | upper_slate_petrol / #405B68 | .25 / .46 |
| inner_ivory_bead | upper_warm_ivory / #C8C2AD | .22 / .48 |
| *_glazing_seal | upper_dark_gasket / #23333B | 0 / .72 |
| *_opaque_pane | upper_opaque_tint / #345D64 | .18 / .28 |
| folded_drip_shoe | upper_satin_sill / #929D9F | .65 / .38 |

1,760 triangles, eleven meshes/primitive surfaces, five materials; GLB 35,940 bytes.
No transparency, transmission, emission, textures, UV dependency or tangents. No
separate material/texture files, rigs, clips, sockets or speculative LODs are needed.
Counts are measured, not accepted performance budgets.

## Checks, diagnostics and reproduction

`source_export_checks.json` verifies exact members, applied transforms/modifiers,
finite geometry, nondegenerate faces, manifold consistently wound edges and positive
signed volume per connected solid. `glb_checks.json` independently decodes binary
positions/normals/indices: unit finite normals, nondegenerate triangles, winding-normal
agreement, source/export triangle counts, axes/bounds and material/studio exclusion.
`interface_checks.json` checks all behind-wall vertices against the declared insertion
and opening envelopes, dependencies and exclusion. Straight profile edges remain in
those convex envelopes. `final_audit.json` verifies byte-identical fresh-process
saved-source GLB re-export and identical source/export diagnostic reports.

The saved source retains an excluded exact 1 × 1 × 1 m `authoring_1m_reference`.
`measured_1m_comparison.png` retains its 4.8:1 width and 1.6:1 height comparison.
`hero.png`, `rear_attachment.png`, `mounting_detail.png`, `upper_floor_scale.png` and
`project_camera.png` show the object and an original unsaved Blender aperture jig.
The 6.4 × 7 m jig contains no roof or room and is not a selected building shell.
All cameras/lights/jig geometry are excluded and unsaved. Project-camera preview is
straight-down fixed yaw, 47 m / 42° vertical perspective at 1280 × 800 in Blender;
it is not an engine capture or proof of gameplay readability/roof occlusion.

Visual self-inspection of all six views found the intended broad three-light rhythm,
quiet trim and no obvious inverted faces or exposed surface conflicts. At the
calibrated overhead distance it reads as a small horizontal strip; fine trim is lost.
No geometry fix was needed during the initial pass; the meaningful owned fix cycle
remains available for concrete review findings. This is self-check, not acceptance.
All final author/export/check/re-export/preview/audit jobs exit 0.

Complete substantive argv/environment/exits and unfiltered diagnostics are retained
in `execution.json` and matching `.log` files. `/usr/bin/blender5.2.2LTS` is absent
(recorded 127); `/usr/bin/blender` is verified exact 5.2.2 LTS build `d13f752e3b9c`,
glTF 5.2.40 before authoring/export. Optional MeshOptimizer absence logs `ERROR`;
compression is unused, binary checks pass. Material/World `use_nodes` future
warnings and private BlenderMCP registration messages remain in logs. Version probe
reports one 0.000023 MB unfreed block, exit 0. No diagnostic suppression, package
installation, global settings/service changes or shared live connector access.

Commands use `-b -noaudio -t 4 --python-exit-code 1`, process-local
`ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy` and an owned cache. From repository root,
use `run.py <new-log-label> <argv...>` to repeat the exact commands in `execution.json`;
labels cannot overwrite earlier logs. `author.py` builds the source; `export.py` loads
it and writes the game GLB, or takes `-- <scratch.glb>` for re-export. Run the GLB and
interface checks, `preview.py`, then `final_audit.py`. Byte-identical saved-source GLB
re-export is claimed; byte-identical regeneration of the `.blend` container is not.
`manifest.py` records all owned files, sizes and SHA256, excluding only itself;
`manifest.py --verify` detects missing, extra or changed files. New receipts require
regenerating the manifest. All owned writers are quiescent at handoff; available for
concrete findings. Acceptance remains with ROOT/integrator and independent reviewers.
