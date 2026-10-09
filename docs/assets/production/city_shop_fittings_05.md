# city_shop_fittings.05 — display-window glazing and frame bay

Source/export candidate, 9 October 2026, for ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2`.
Requested per-asset Astra MEDIUM commission; produced by this assigned worker.
Commission `commission.md` at `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`
supersedes the historical concept-only restriction. **Not production READY.**
Source/export checks pass after one owned interface fix. Independent acceptance,
Godot import/linked prefab/save-reopen, collision/query/runtime/multiplayer,
actual-shell placement and device/performance gates remain pending.
The frozen six-asset engine candidate and all shared editor/project files were untouched.

## Deliverables and provenance

- Editable source: `art/source/models/environment/city_shop_fittings_05/city_shop_fittings_05.blend`.
- Collection/root: `export_city_shop_fittings_05` / `city_shop_fittings_05`.
- Explicit game export: `art/models/environment/city_shop_fittings_05/city_shop_fittings_05.glb`.
- Reproduction tools: `tools/asset_production/city_shop_fittings_05/`.
- Authoritative evidence: [city_shop_fittings_05-evidence/](city_shop_fittings_05-evidence/).

Original meshes authored inside private pinned Blender: continuous stepped insertion
sleeve and rounded face flange, narrow ivory inlay, paired glazing gaskets, two large
opaque tinted panes, one centre mullion and a sloped folded sill. Eight separately
editable mesh objects, applied profiles/bevels/weighted normals. No external meshes,
images, textures, fonts, generators or libraries supply production geometry. Existing
`.01`/`.02` exporter, decoder, profile and receipt patterns were adapted read-only into
owned tools. Source is original Blender geometry, not a renamed imported GLB.

Read AGENTS.md, assets.md, art-direction.md, city_shop_fittings.md and the raw commission;
inspected Signal Row v03, Crescents v02 and Old Quay v03 text and images. Their broad
shop glazing, smooth hardware, quiet slate/petrol and warm trim guide appearance;
no generated-image dimensions were treated as measurements. `.01` canopy, `.02`
fascia and `.03` entrance reports were read-only interface references. This is a
window with two broad lights and a sill, distinct from the separate flat fascia
artwork face. Opaque teal suggests a dark interior without shop content or expensive
transparency. No tenant artwork/text, detailed interiors, animation, opening mechanics,
wall/structural trim, collision or runtime behavior is included.

## Measured interface v1

Metres. Pivot `(0,0,0)` is bottom centre at the facade plane. Blender +Y street/front,
+Z up maps once through glTF to Godot -Z front, +Y up: `(X,Y,Z) → (X,Z,-Y)`.
All exported objects/root have zero translation/rotation and unit scale; geometry
contains the offsets. This attachment pivot intentionally sits above finished ground
when mounted. No corrective prefab scale/rotation is required.

| Measurement | Contract |
| --- | --- |
| Width × height × total depth | 3.200 × 2.000 × 0.400 m |
| Blender AABB | min (-1.600,-0.180,0.000), max (1.600,0.220,2.000) |
| Godot-axis AABB | min (-1.600,0.000,-0.220), max (1.600,2.000,0.180) |
| Shell rough opening | X [-1.520,1.520], Z [0.060,1.940]; 3.040 × 1.880 m |
| Insertion sleeve envelope | X ±1.500, Z [0.080,1.920], rear Y=-0.180 |
| Installation clearance | nominal 20 mm per jamb/head/bottom; rear void to Y≤-0.200 |
| Face flange | outside opening; back Y=0.012, front Y=0.090 |
| Ivory inlay front | Y=0.099; no structural shell trim |
| Glazing | two 1.438 × 1.708 × 0.075 m units; X centres ±0.750, Z centre 1.000 |
| Glazing depth | Y [-0.040,0.035]; front recessed 55 mm behind frame face |
| Mullion | maximum width 0.076 m, height 1.780 m; front Y=0.090 |
| Sill | X ±1.600, Y [0.012,0.220], Z [0,0.085]; sloping nose |
| Suggested pivot height | 0.480 m above local finished floor; fitting top 2.480 m |
| Placement tolerance | ±2 mm translation; axes aligned, unit scale |
| Bounds tolerance | ±1 mm per bound; automated checks use stricter limits |

Shell owns the rectangular hole and structure. Keep its wall out of the declared
aperture and reserve at least 0.200 m rear depth; do not place this in front of a
solid uncut wall. The 12 mm face stand-off is intentional. Rounded outer corners
leave at least 60 mm nominal flange coverage beyond the square opening. Shell trim
and unrelated fittings remain ≥0.100 m outside the window's visible bounds; reserve
front depth to Y=0.320 and flat frontage width ≥3.400 m. Reject incompatible curved,
corner or undersized frontages rather than stretching this candidate.

At suggested mounting, the top aligns with `.03`'s 2.480 m entrance casing. `.01`
at its proposed 3.000 m pivot has lowest geometry 2.580 m, leaving 100 mm above
this bay; `.02` at 3.800 m has lowest geometry 3.400 m. These are arithmetic
compatibility checks, not a tested combined storefront. No other asset is embedded
or modified. Assembly joints intentionally intersect; the separate component solids
are closed, but the fitting is not a single fused volume or engineered weather seal.

## Materials and density

Five embedded opaque, single-sided Principled/glTF PBR materials; sRGB swatches
converted to linear base colours. Each named mesh has one material slot (index 0).

| Mesh | Material / sRGB | Metallic / roughness |
| --- | --- | --- |
| formed_perimeter, centre_mullion | window_slate_petrol / #405B68 | .25 / .46 |
| ivory_perimeter_inlay | window_warm_ivory / #C8C2AD | .22 / .48 |
| left_glazing_gasket, right_glazing_gasket | window_dark_gasket / #23333B | 0 / .72 |
| left_opaque_glazing, right_opaque_glazing | window_opaque_tint / #345D64 | .18 / .24 |
| sloped_sill | window_satin_sill / #929D9F | .65 / .38 |

No transmission, alpha blending, emission, textures, UV dependency or tangents.
No separate material/texture files are needed. No rigs, clips or sockets; LOD is
not authored without a demonstrated requirement. **1,368 triangles, eight meshes /
eight primitive surfaces, five materials; GLB 29,560 bytes.** These are actual
counts, not approved performance budgets.

## Verification, fix and reproduction

`source_export_checks.json` checks exact membership, applied transforms/modifiers,
finite coordinates, nondegenerate faces, manifold consistently wound solids and
positive signed volume for each connected component. `glb_checks.json` independently
decodes the binary positions/normals/indices, checks finite unit normals, winding
agreement, nondegenerate triangles, exact names/material count/opaque scope, axis
conversion and bounds. Both source and export match the declared metre bounds;
export triangle counts match source. `interface_checks.json` verifies every rear
vertex fits the shell opening with ≥20 mm nominal clearance (0.1 mm numerical margin).
Profiles are straight between these vertices, so no curved/interpolated rear geometry
escapes the checked envelope. `final_audit.json` proves **byte-identical saved-source
reexport in a fresh process**, including matching audit reports.

The source retains an excluded exact 1 × 1 × 1 m `authoring_1m_reference` in
`authoring_excluded`. Its measured width/height ratios are 3.2 and 2.0. Export membership
excludes this reference and all cameras/lights. Studio fixtures are unsaved.
`hero.png`, `rear_attachment.png`, `measured_1m_comparison.png`, `attachment_opening.png`
and `project_camera.png` show the final object, scale and an original temporary
Blender shell-aperture jig. No borrowed shell geometry is changed. Preview receipts
record transforms, aperture and camera. Straight-down fixed-yaw 47 m / 42° vertical
perspective at 1280 × 800 is Blender calibration only. The window occupies a small
edge-of-frame region; the two lights remain a broad dark strip, with fine inlay detail
lost. Roof occlusion and actual Godot readability remain untested.

One meaningful owned fix: the initial sill extended behind the wall below the shell
opening. `initial_interface.log` exits 1 and lists the offending vertices. The sill's
rear heel now starts at Y=0.012, keeping all sill geometry in front of the shell;
opening metadata was aligned to Z=0.060. Final source/GLB/checks and all previews were
rebuilt. Initial source, GLB, author script, checks and views remain under `initial/`.

All substantive subprocess argv, process-local environment, durations and exit statuses
are in `execution.json`; complete unfiltered logs sit alongside. The requested
`/usr/bin/blender5.2.2LTS` path is absent (127). `/usr/bin/blender` is the exact
5.2.2 LTS build `d13f752e3b9c`, glTF 5.2.40, asserted before authoring/export.
Jobs use `-b -noaudio -t 4 --python-exit-code 1`, `ALSOFT_DRIVERS=null`,
`SDL_AUDIODRIVER=dummy` and an owned process-local cache. No shared/live editor,
service, global configuration, Git/index or out-of-scope asset writes were used.
Optional MeshOptimizer library absence is logged as ERROR; compression is unused,
raw payload checks pass. Material/World `use_nodes` future-deprecation warnings and
private BlenderMCP addon registration messages are retained. The version probe logs
one unfreed 0.000023 MB memory block while exiting 0. No diagnostics were suppressed.
The initial shell intrusion and absent requested binary are the only nonzero jobs;
all final production/export/validation/preview jobs exit 0.

Reproduce from repository root using `run.py <fresh_log_label> <argv...>` (it refuses
to overwrite earlier logs). Exact author/export/check/reexport/preview argv are in
the receipt. For saved-source reproduction:

```sh
python tools/asset_production/city_shop_fittings_05/run.py verify_again /usr/bin/blender -b -noaudio -t 4 art/source/models/environment/city_shop_fittings_05/city_shop_fittings_05.blend --python-exit-code 1 --python tools/asset_production/city_shop_fittings_05/export.py -- docs/assets/production/city_shop_fittings_05-evidence/reexport_city_shop_fittings_05.glb
python tools/asset_production/city_shop_fittings_05/final_audit.py
python tools/asset_production/city_shop_fittings_05/manifest.py --verify
```

`manifest.json` is the exact expected path/byte/SHA256 inventory, excluding only
itself. Reproduction that changes receipts requires regenerating the manifest.
Final visual self-inspection found smooth broad framing, two quiet opaque panes and
no obvious inverted surfaces; this is self-review, not independent art acceptance.
All owned writers are quiescent at delivery; available for concrete downstream fixes.
