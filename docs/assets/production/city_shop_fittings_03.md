# city_shop_fittings.03 — recessed shop entrance surround

Source/export candidate, 9 October 2026; requested Astra MEDIUM specialist commission.
Produced by this assigned worker for ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2`.
Commission: `commission.md` at `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`.
Source/export checks pass after one owned geometry fix cycle. **Not production READY.**
Independent acceptance belongs to ROOT/reviewers; engine candidate
`c4067ff3abe1384301471d9a64e94e84201235e2` was not accessed or changed.

## Deliverables and original provenance

- Editable source: `art/source/models/environment/city_shop_fittings_03/city_shop_fittings_03.blend`.
- Export collection: `export_city_shop_fittings_03`, containing `variant_single`
  and `variant_double`. Identity roots: `city_shop_fittings_03_single` / `_double`.
- Explicit outputs: `art/models/environment/city_shop_fittings_03/city_shop_fittings_03_single.glb`
  and `city_shop_fittings_03_double.glb`.
- Each variant has four separately editable mesh objects, prefixed `single_` or
  `double_`: `recessed_reveal`, `rounded_face_casing`, `rear_stop`, `sloped_threshold`.
- Excluded `authoring_excluded/authoring_1m_reference` is an actual measured 1 m cube.
  Both variants share the assembly datum and overlap in the authoring scene; isolate
  their named collections when editing. Export selects exactly one variant at a time.

All production geometry was originally authored inside private pinned Blender by
`tools/asset_production/city_shop_fittings_03/author.py`: formed tapered jamb/header
reveal, softly rounded face casing, narrow rear leaf stop, and sloped satin threshold.
Applied bevels and weighted normals remain editable mesh geometry; source is not a
GLB renamed as a Blender file. No external meshes, image generation, textures, fonts,
paid services or asset libraries supplied production geometry. No attribution to an
external creator is required. Existing in-project exporter/check patterns from `.01`
were read and adapted into owned tooling; there is no live tool/source dependency.

The accepted smooth Petrol & Coral direction and commercial frontage references
inform restrained broad highlights and quiet slate/ivory hardware. Signal Row v03
and its asset breakdown require one `.03` + `.06` entrance assembly; Old Quay v03,
Crescents v02 and Terrace Ward v02 favour quieter warm entries, while Broadlot v01
uses broad entrance bands. These are style references, not dimensional evidence.
Shared neutral hardware leaves tenant graphics and bright district accents to their
owners. No building shell walls, glazed leaves, interiors, opening mechanics,
animation, collision or lighting behavior are included.

## Interface v1 — explicit reversible production dimensions

Metres. Origin is the centre of the opening on the **wall plane and finished floor**:
Blender `(0,0,0)`. +Y faces the street and +Z is up. Single glTF Y-up conversion maps
`(X,Y,Z)` to Godot `(X,Z,-Y)`: Godot -Z is street/front, +Y is up. Every exported mesh
and root has identity translation/rotation/unit scale; geometry carries its offsets.
This ground attachment datum intentionally does not centre the asymmetric depth.

| Contract | Single | Double |
| --- | --- | --- |
| Overall width × height × depth | 1.540 × 2.480 × 0.630 | 2.340 × 2.480 × 0.630 |
| Blender AABB minimum | (-0.770, -0.520, 0.000) | (-1.170, -0.520, 0.000) |
| Blender AABB maximum | (0.770, 0.110, 2.480) | (1.170, 0.110, 2.480) |
| Godot-axis AABB minimum | (-0.770, 0.000, -0.110) | (-1.170, 0.000, -0.110) |
| Godot-axis AABB maximum | (0.770, 2.480, 0.520) | (1.170, 2.480, 0.520) |
| Rear aperture width at leaf | 1.040 | 1.840 |
| Shell rough opening width | 1.420 | 2.220 |
| Future `.06` leaves | one, width 1.024 | two, width 0.908 each |
| Future leaf X intervals | [-0.512, 0.512] | [-0.912, -0.004] and [0.004, 0.912] |

Shared opening head is Blender Z=2.240. Threshold top is Z=0.020 at the leaf;
front nose drops to Z=0.004, then meets ground. Future static `.06` leaves occupy
Y=[-0.475,-0.430], Z=[0.030,2.232]: height 2.202 m, thickness 0.045 m,
front recessed 0.430 m from the facade. In Godot their Y=[0.030,2.232] and
Z=[0.430,0.475]. Nominal side and head gaps are 8 mm; bottom gap 10 mm; rear stop
front Y=-0.481 leaves 6 mm behind the leaf. Double meeting gap is 8 mm. The `.03`
stop overlaps the leaf outline by 8 mm nominally and has no centre mullion. `.06`
owns glazing, leaf stiles/rails and static handle geometry, **not a competing fixed
entrance frame**. Future hardware should stay within its leaf's X/Z envelope and
at or behind Y=-0.330 (100 mm maximum projection beyond the leaf front); hardware
fit still requires `.06` assembly inspection. Neither these intervals nor a stop
create a working hinge, seal, lock or physical passage contract.

The shell owns a plain rectangular wall opening, height 2.450 m from Z=0, with the
width above, and must keep the aperture/recess void clear to at least Y=-0.540.
Rear reveal outer width is 1.400 / 2.200 m and head 2.440 m: 10 mm jamb/head
installation gaps. Face casing covers the rough opening by 60 mm on each side and
30 mm above; its back is Y=0.010, leaving a deliberate 10 mm facade stand-off/shadow
gap, with the reveal crossing the wall plane. No wall, back panel or detailed
interior may occupy the leaf/reveal void. Thin shells must preserve the rear void;
this fitting is not a deep structural tunnel supplied by the shell.

Bounds tolerance ±1 mm per bound; source/export checks use stricter floating-point
limits. Nominal mounting translation tolerance ±2 mm, axes aligned and unit scale;
no corrective rotation/stretch. Casing/reveal/threshold intersections are intentional
manufactured assembly joins, not one merged watertight building. Keep unrelated
ordinary trim/fittings at least 50 mm outside visual bounds and reserve 100 mm front
installation clearance (streetmost point Y=0.210). Keep shell trim outside the casing
rather than overlaying a second frame. Reject incompatible bays or request a new
reviewed variant. Dimensions are authorized reversible choices, not building-code,
accessibility, player collision or actual gameplay clearance certification.

## Materials and density

Four opaque single-sided embedded Principled/glTF PBR materials, one slot per mesh:

| Mesh suffix | Material / sRGB reference | Metallic / roughness |
| --- | --- | --- |
| `recessed_reveal` | `surround_slate_petrol` / #405B68 | .25 / .46 |
| `rounded_face_casing` | `surround_warm_ivory` / #C8C2AD | .22 / .48 |
| `rear_stop` | `surround_dark_rebate` / #293B43 | .25 / .55 |
| `sloped_threshold` | `surround_satin_threshold` / #929D9F | .65 / .38 |

Swatches convert to linear base colors. No emission, alpha blending, UV-dependent
textures, normal maps or tangents. No separate material/texture files are needed.
Each variant: **2,312 triangles**, four meshes/four primitive surfaces, four materials,
one root; final GLB **41,872 bytes**. Broad-face bevel density gives smooth highlights
without decorative microgeometry. This count is measured, not an accepted device
budget. Rigs/clips/sockets/LOD are not applicable to this static scope; no speculative
LOD/performance framework was added.

## Checks, previews, and limits

Authoritative evidence directory: [`city_shop_fittings_03-evidence/`](city_shop_fittings_03-evidence/).

- `source_export_checks.json`: pin, exact membership, identity transforms, finite
  vertices, nondegenerate polygons, manifold/consistently wound closed component
  solids, positive signed volumes, triangle counts, bounds, materials and excluded
  metre fixture. Variant filtering prevents cross-export contamination.
- `glb_checks.json`: raw GLB triangle winding against finite unit normals,
  nondegenerate triangles, axis-converted numerical bounds, source triangle agreement,
  identity node transforms, opaque single-sided materials, no studios/lights/cameras,
  animations, skins or texture dependencies.
- `interface_checks.json`: saved-mesh ray probes at three leaf depths, four jamb
  heights and three header positions; measured 1.04/1.84 widths, 2.24 head, .02 sill,
  -.481 stop face, and leaf-envelope clearance arithmetic. These are source geometry
  checks, not Godot collision or an actual `.06` assembly test.
- `reexport_comparison.json`: both exports byte-identical in a fresh process opening
  the saved `.blend`; exact final bytes/SHA256. `reexports/` retains the compared files.
- `hero.png`, `rear_interface.png`, `front_elevation.png`, `measured_1m_comparison.png`
  expose the shape and scale. `interface_sheet.svg`/`.png` adds dimensioned elevation
  and an illustrative header/sill section with a dashed leaf datum, no leaf model.
- `unchanged_shop_scale_comparison.png` and `project_camera.png` use the existing
  `art/models/brackett_greybox/shop.glb` read-only, measured at 18 × 15 × 10 m. The
  fitting roots are temporarily 2 m in front of that shop's front plane; the shop
  lacks the required opening, so this is deliberately **not a mounted assembly**.
  `preview_checks.json` records unchanged input SHA, dimensions, positions and cameras.

Visual self-check: recessed jamb/header surfaces and contrasting threshold are clear
in hero/elevation/rear views; both widths retain consistent profiles. The straight-down
perspective 47 m / 42° vertical-FOV, north-up 1280×800 Blender view reduces the fittings
to small header/reveal strips. It does not establish useful in-game door readability;
actual shell mounting, roof occlusion and blue-hour engine lighting remain untested.
Studio uses Cycles CPU, four threads, 32 samples, AgX, neutral fill/daylight comparison.
No Godot process, live Blender session, private editor, shared world/prefab/project,
Git/index, service configuration or other source was accessed for mutation.

One owned fix cycle: initial casing/reveal/stop bottoms shared Z=.020. Revised casing
feet to Z=0, tucked reveal bottoms to Z=.014 into the sill, and lifted stop bottoms to
Z=.024, removing the common exposed base plane and grounding the outer casing.
Bounds and leaf dimensions remain unchanged. Initial source/author script, complete
logs/checks, exports and previews are retained under `initial/`; final geometry,
exports, clearance checks and previews were regenerated after the change.

All final author/export/raw-GLB/interface/reexport/preview jobs exit 0. Substantive
failures/diagnostics are retained without suppression:

- Requested `/usr/bin/blender5.2.2LTS` path is absent (127). `/usr/bin/blender` verifies
  5.2.2 LTS build `d13f752e3b9c`; glTF exporter 5.2.40 is asserted before authoring/export.
- `version.log` exits 0 but reports one unfreed memory block (0.000023 MB).
- Authoring logs deprecated `Material.use_nodes` and a sandbox-denied OpenImageIO
  desktop thumbnail cache write. `.blend` save and independent reopen succeed.
- Export/reexport log absent optional MeshOptimizer library. Compression is not used;
  raw payload geometry and deterministic comparison pass.
- Preview logs deprecated `World.use_nodes`. BlenderMCP addon registration messages
  are private CLI startup output; no live endpoint was called.
- First interface PNG conversion exits 1 because Python CairoSVG is absent. The
  full traceback and argv/exit are retained as `failed_cairosvg_*`; installed
  `/usr/bin/rsvg-convert` subsequently produces the inspected PNG with exit 0.

Model/source technical checks and explicit export checks are complete candidate
evidence. Engine import/`.import` metadata, linked prefab, inherited save/reopen,
`.03` + actual `.06` fit, shell mounting, collision/query/runtime/network, device
performance, gameplay camera readability and independent art/technical acceptance
remain **pending later stages**. No source-only READY or self-acceptance is claimed.

## Reproduction and exact inventory

From repository root:

```sh
python tools/asset_production/city_shop_fittings_03/run.py --preview
python tools/asset_production/city_shop_fittings_03/manifest.py
```

The runner applies process-local `ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy`,
`-b -noaudio -t 4 --python-exit-code 1`; no global settings change. `commands.json`
retains actual full argv/cwd/environment/start/exit for the final Blender pipeline.
The separately run drawing has `interface_sheet_command.json` and its raw log
(including renderer argv). Initial pipeline receipts live under `initial/`.
The runner regenerates source and outputs; saved-source verification can instead run
`export.py` in private Blender with the `.blend` loaded and `-- <scratch-directory>`.
No byte-identical `.blend` regeneration is claimed; saved-source GLB reexports are exact.

`manifest.json` is the exact expected relative file / byte-size / SHA256 inventory
of all owned deliverables, tools and retained evidence, excluding only the manifest
itself to avoid recursion. Check that manifest before integration. All owned Blender,
render and file-writing jobs are quiescent at handoff. Available for concrete findings.
