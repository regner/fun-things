# city_shop_fittings.01 — short shop canopy

Source/export candidate, 9 October 2026. Produced by this assigned Codex worker;
acceptance remains with ROOT and the integrator. Commission `commission.md` at
`2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661` supersedes the concept-only restriction.
No production READY claim. Model/source and explicit export checks pass; engine
import, linked prefab, save/reopen, actual facade mounting, collision/query/runtime,
multiplayer, device/performance and independent art acceptance remain pending.

## Design and source mapping

Original editable Blender meshes: broad descending metal canopy, rolled nose rim,
continuous rear mounting/flashing rail and two tapered underside cantilever gussets.
No external mesh, texture or generated image is used as production geometry.
The original geometry was constructed inside a private pinned Blender process with
`tools/asset_production/city_shop_fittings_01/author.py`. Four semantic meshes remain
separately editable; bevel and weighted normals are applied. Intentional assembly
intersections join the components visually; this is not a watertight building shell.

- Source: `art/source/models/environment/city_shop_fittings_01/city_shop_fittings_01.blend`
- Collection: `export_city_shop_fittings_01`; identity empty root `city_shop_fittings_01`.
- Explicit export: `art/models/environment/city_shop_fittings_01/city_shop_fittings_01.glb`.
- Meshes: `formed_canopy`, `rolled_front_rim`, `wall_mount_rail`, `paired_tapered_gussets`.
- Excluded collection `authoring_excluded` retains `authoring_1m_reference`, exactly
  1 × 1 × 1 m. Preview cameras, lighting and temporary comparison assembly are
  unsaved and excluded from export. No textures, rigs, clips, sockets or LODs.

Signal Row v03 and its facade breakdown call for restrained short awnings beneath
quiet blue roofs, with tenant graphics separate. Crescents v02 favours muted slate
and plum, warm domestic detail and little neon. Old Quay v03 favours quieter warm
shop-homes and selected canopy use. This shared slate-petrol top, small ivory rim
and dark supports serve all three without copying an incidental neon sign or
expanding into their building shells. These images establish style, not dimensions.
No duplicate domestic porch or entertainment-hall canopy is supplied. Source sizes
below are reversible asset-specific choices authorized by this commission.

## Metre interface and tolerance

Attachment pivot is the centre of the rear wall-contact rail, on the facade plane;
it is deliberately an attachment datum, not a ground origin. Blender +Y projects
outward, +Z is up; export converts once to Godot -Z outward, +Y up. All exported
objects have identity rotation, scale and translation; geometry is expressed about
the shared attachment pivot. No corrective root scaling or rotations are required.

| Measurement | Contract |
| --- | --- |
| Blender AABB | min (-1.600, 0.000, -0.420), max (1.600, 1.100, 0.240) m |
| Godot-axis AABB | min (-1.600, -0.420, -1.100), max (1.600, 0.240, 0.000) m |
| Width / height / projection | 3.200 / 0.660 / 1.100 m |
| Bounds acceptance tolerance | ±0.001 m per bound; checks use stricter numerical thresholds |
| Wall contact rail | X ±1.520 m; Blender Y 0–0.070 m; Z ±0.240 m |
| Support centres | X ±1.150 m; width 0.110 m each |
| Mounting surface | Flat vertical wall at Blender Y=0 / Godot Z=0; ±0.002 m placement tolerance |
| Reserved fitting volume | X ±1.700, Blender Y -0.020–1.200, Z -0.520–0.340 m |
| Suggested ground placement | Pivot 3.000 m above local finished ground; lowest fitting 2.580 m |
| Opening/sign separation | Keep opening head at or below 2.480 m and other signs/trim ≥0.100 m outside visual bounds |

The reserved volume is an installation check, not generated collision. Flat contact
requires a flat bay at least 3.4 m wide; do not stretch a shell, alter its opening or
force the canopy over curved/corner frontage. Reject incompatible bays or return a
concrete alternative size to this owner. Rail backside meets the wall without
intentional penetration; no fastener holes, wall recesses or structural loads are
claimed. Brackets stay within the projection; no ground supports obstruct the route.
Ground headroom is arithmetic only, subject to downstream movement/physics testing.
There is no weather, opening, animation, lighting or physics behavior.

## Materials and density

Three opaque, single-sided Principled/glTF PBR materials, sRGB swatches converted
to linear base colors: `canopy_slate_petrol` #405B68 (metallic .25, roughness .46),
`canopy_warm_ivory_rim` #C8C2AD (.22, .48), `canopy_dark_mounts` #293B43 (.35, .55).
No emission, alpha, images, UV dependency or tangents. Flat paint and broad highlights
match the smooth manufactured direction. Material variants can be reviewed later
without another mesh. 1,212 triangles, four meshes/primitive surfaces, three materials;
this is a measured count, not a ratified device budget. No speculative LOD tooling.

## Validation, evidence and reproduction

Authoritative evidence: `city_shop_fittings_01-evidence/`. `source_export_checks.json`
and `glb_checks.json` report applied transforms, finite positions, manifold consistently
wound closed component solids with positive signed volumes, nondegenerate faces and
triangles, finite unit normals and triangle-winding agreement, exact collection/node
membership, axis-converted bounds and material/studio exclusion. `reexport_comparison.json`
records byte-identical export in a fresh process from the saved source. Full command
arguments/environment/exits are in `commands.json`; unfiltered logs accompany them.
`manifest.json` lists exact deliverable file bytes and SHA256, excluding itself.

`hero.png`, `attachment_side.png` and `measured_1m_comparison.png` expose the rolled
profile, mounting rail/gussets and retained metre reference. `unchanged_shop_scale_comparison.png`
and `project_camera.png` use the existing greybox `art/models/brackett_greybox/shop.glb`
read-only at its measured 18 × 15 × 10 m size. The canopy is temporarily translated
to the front plane at 3 m above ground; no reference geometry or materials change.
`preview_checks.json` retains reference hashes/bounds, transforms and views. Project
camera is straight down, fixed yaw, perspective 47 m / 42° vertical FOV, 1280 × 800;
it is a Blender calibration comparison, not a Godot camera or readability acceptance.

Reproduce from repository root:

```sh
python tools/asset_production/city_shop_fittings_01/run.py
python tools/asset_production/city_shop_fittings_01/manifest.py
```

Runner uses process-local `ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy`, `-b -noaudio -t 4`
and `--python-exit-code 1`. Requested `/usr/bin/blender5.2.2LTS` was absent (exit 127);
`/usr/bin/blender` verified exactly 5.2.2 LTS build `d13f752e3b9c` and glTF 5.2.40
before any source authoring. No global config/service or live connector was accessed.
The installed BlenderMCP addon logs registration/unregistration in private CLI jobs;
no shared live endpoint is used. Exporter reports absent optional MeshOptimizer
library; compression is unused, complete raw exports and all payload checks pass.
Blender logs `use_nodes` future deprecation warnings; they are retained, not suppressed.

One owned fix cycle addressed overlapping coplanar nose/rim surfaces: inset the
canopy skin 12 mm in depth at its nose, lift its lower return 15 mm and shorten its
width 20 mm each side. The rim retains the declared outer bounds and now caps the
ends without coincident exposed planes. Initial logs and hero are retained under
`initial/`; final source, exports and previews were rebuilt and rechecked. This is
an original production candidate awaiting independent inspection, not self-acceptance.

Visual self-check: the roof-centred project camera completely occludes this low
canopy behind the perspective-expanded 10 m greybox roof. That observed limitation
is retained as `project_camera_roof_centred_occluded.png`; source geometry was not
changed to defeat it. Final `project_camera.png` uses the same straight-down 47 m /
42° camera centred at Blender (0,12) over the street. Actual gameplay occlusion
policy remains downstream. The underside view was widened from 55 to 45 mm lens
to retain the full mounting silhouette; `attachment_reframe.log` records that exit.

Additional retained environment diagnostics: `version.log` exits 0 but reports one
unfreed memory block (0.000023 MB). `author.log` reports an OpenImageIO failure to
write Blender's desktop thumbnail under `/home/regner/.cache/thumbnails/large/`;
the sandbox denied that incidental cache output. The requested `.blend` save,
fresh-process reopen, topology audit and byte-identical GLB reexport all succeed.
No thumbnail/cache permission escalation or global configuration change was made.
All final author/export/check/reexport/preview jobs exit 0; the missing requested
binary probe is the sole nonzero command (127), followed by the verified pin fallback.
