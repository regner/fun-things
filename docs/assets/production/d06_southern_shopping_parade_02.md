# d06_southern_shopping_parade.02 — Repeatable storefront bay interface

**Saved interface-reference candidate; independent review and final production/world
acceptance remain pending.** Commissioned isolated production worker, following the
current per-ID task and [commission](commission.md). This supersedes the historical
concept-only restriction in the [family brief](../d06_southern_shopping_parade.md).

## Design and ownership

A repeatable five-fitting storefront is composed six times along the existing
[continuous parade shell](d06_southern_shopping_parade_01.md). One quiet slate-blue
roof and plum structural wall remain uninterrupted. Each station has one recessed
single entrance, an opaque two-light display window, short canopy and blank fascia.
All visible geometry and materials reuse the existing Blender-authored assets.
**No new mesh, GLB, Blender source, material, texture, tenant artwork or building
variant is commissioned by this interface reference.**

Read the accepted Petrol & Coral direction, Stage 3 Signal Row identity, Stage 4
street context, Signal Row v03 district/map references, the family brief, shared
fitting handoffs and batch 01–03 integration conventions. Personally inspected the
Signal Row v03 image, the prior shell detail and city_lights.01 quality reference.
Concept images guide style only; dimensions and mounts come from the delivered
shell and fitting contracts, not image measurement.

- `.01` still owns shell geometry, openings, roof, source mounting markers and the
  solid exterior collision envelope. Its files are unchanged.
- `.02` owns these two saved composition scenes, interface documentation and checks.
- `.03` retains the north-end facade treatment. Its north datum remains untouched
  at `Shell/Visuals/Model/D06SouthernShoppingParade01/north_facade_datum` in the full
  reference. No second shell, bridge landing or forecourt mesh is introduced.
- District commercial graphics own tenant identity and cyan/magenta/warm panel
  differentiation. Blank shared fascia materials are intentional interface placeholders,
  not delivered artwork or accepted wayfinding.

No live Blender/Godot session was used. The supplied workflow prohibits those sessions
and reports the windowed editor unavailable: direct text scene authoring was followed
by isolated pinned headless editor pack/save/reload. This does not synchronize any
separate open editor and does not claim native visual/gameplay acceptance.

## Saved resources and provenance

| Owned scene | Contract |
| --- | --- |
| `scenes/prefabs/environment/d06_southern_shopping_parade_02_bay.tscn` | Reusable fitting-only bay, wall/floor origin, local -Z outward, no active collision |
| `scenes/prefabs/environment/d06_southern_shopping_parade_02.tscn` | One identity shell plus six linked bay instances; ground-centred reference assembly |

Scene UIDs: bay `uid://bi2mydn1p1q82`; full reference `uid://crisdyjpa2ee1`.
Godot-generated node IDs and inherited `parent_id_path` values are preserved.
Every fitting still owns an identity-transform `Visuals/Model` imported GLB instance.
Only the fitting wrappers' collision shapes are overridden; imported model children
are not editable. There is no runtime construction/placement script or copied mesh.

Existing prefab → GLB → source mapping (all under the corresponding environment
folder; exact paths and SHA-256 values are in `validation.json`):

| Prefab/GLB basename | Source family and selected collection | Reused geometry |
| --- | --- | --- |
| `d06_southern_shopping_parade_01` | same family, `export_d06_southern_shopping_parade_01` | Whole continuous shell |
| `city_shop_fittings_03_single` | `city_shop_fittings_03`, `variant_single` | Entrance surround |
| `city_shop_fittings_06_single` | `city_shop_fittings_06`, `variant_single` | Closed glazed leaf |
| `city_shop_fittings_05` | same family, `export_city_shop_fittings_05` | Display window |
| `city_shop_fittings_01` | same family, `export_city_shop_fittings_01` | Canopy |
| `city_shop_fittings_02` | same family, `export_city_shop_fittings_02` | Fascia frame/carrier |

Sources are `art/source/models/environment/<family>/<family>.blend`; exports are
`art/models/environment/<family>/<basename>.glb` with their existing `.import` files;
prefabs are `scenes/prefabs/environment/<basename>.tscn`. Their original authorship,
materials and export/reexport contracts remain in their own handoffs. No dependencies
were reauthored, saved or reexported. New-source `author.py` / `export.py` and new-GLB
byte-identical reexport are **not applicable** to this no-extra-mesh record. Its source
of authored placement is the two saved scenes, and repeatability is checked through
byte-stable engine save/reload plus immutable dependency hashes.

The tooling is narrowly interface-specific: `check_prefab.gd` checks actual production
PackedScenes and exports a scratch transform receipt; `validate.py` audits original
sources and fits the actual GLBs using those engine-measured transforms; `render.py`
uses that validated scratch assembly and the existing shell studio. It does not
introduce a competing authoring plan or a private generic export framework.

## Metres and bay interface

The full reference retains `.01`'s provisional structural **18 × 60 m** footprint,
**5.4 m** height and ground-centred origin `(0,0,0)`. These dimensions and six stations
were approved provisionally for `.01`, not selected as final parcel/tenant design.
North is Godot -Z. Main facade X=-9 faces west (-X). Bay local +X runs north; local
-Y is down; local -Z points outward. Unit scale throughout; do not mirror/stretch.

`WestBays/WestBay01` through `WestBay06` are north-to-south at
`(-9,0,-25)`, `(-9,0,-15)`, `(-9,0,-5)`, `(-9,0,5)`, `(-9,0,15)`, `(-9,0,25)`.
Each matches the corresponding actual imported `.01` `west_bay_0N` marker, including
its orientation. The **6.4 m station width and 10 m pitch** remain unchanged.

Within each reusable bay, these node translations match the shell's named
`west_bay_0N_mount_<suffix>` children exactly (±1 mm verification tolerance):

| Node / suffix | Bay-local Godot translation | Bounds/role |
| --- | --- | --- |
| `Entrance` / `entrance_single` | (1.95,0,0) | Single surround, 1.54 × 2.48 × .63 m |
| `Door` / `door_single` | (1.95,0,0) | Closed leaf, 1.024 × 2.202 × .123 m |
| `Window` / `display_window` | (-.95,.48,0) | 3.2 × 2 × .4 m display bay |
| `Canopy` / `canopy` | (-.95,3,0) | 3.2 m wide, 1.1 m outward projection |
| `Fascia` / `fascia` | (-.95,3.8,0) | 3.2 × .8 m carrier, .14 m projection |

The shell owns the bay-local rough openings: display u[-2.47,.57], height[.54,2.42];
entry u[1.24,2.66], height[0,2.45]. Its .28 m wall and recess remain unchanged.
Entry insertion space must remain clear to .54 m behind the wall; `.01`'s opaque
backer starts .60 m behind it. The display requires .20 m rear clearance. Actual
inserted geometry fits both holes without intersecting shell trim/backers. This is
closed exterior presentation, **not an interior or traversable doorway**.

Actual visible separation: window top to canopy bottom **.100 m**; canopy top to
fascia bottom **.160 m**. Canopy bottom is **2.580 m** above ground. Broad .01 piers
and head courses remain clear. Fascia/window widths are fixed: differing tenant
widths, shutters, double doors and upper windows are not silently fitted into these
single openings. East frames remain unpopulated because the east wall is solid.

The full fitted visual Godot AABB is **(-10.100,0,-30.035) → (9.040,5.400,30.035)**,
size **19.140 × 5.400 × 60.070 m**, tolerance ±.001 m per bound. The canopy is the
westernmost surface: 1.100 m from the wall, within `.01`'s 1.200 m installation
reservation. Keep the separately reserved walking band beyond that volume; the
reference adds no roads, sidewalks or ground collision. Current road-tool/bridge
clearance and final parcel fit still belong to placement review.

For graphics, reuse each `Fascia/Visuals/Model` imported `fascia_artwork_carrier`
material slot 0 `fascia_artwork_face` only. The 3.000 × .600 m face is 5:1, local
Z=-.128, with centred 2.940 × .540 m safe content. Preserve the existing UV orientation
and back/sides material; do not add another coplanar sign body. Graphics material
remapping remains downstream, not an invented runtime API here.

## Collision and evidence

`Shell/Collision/Body/SolidFootprint` is the **only active collider**, unchanged
18 × 5.25 × 60 m box centred at (0,2.625,0), layer 1/mask 0. All six leaf and twelve
pane shapes are disabled through saved wrapper overrides. Canopies, fascia and
surrounds add no collision. The fitting-only `_bay` scene is **not** a freestanding
solid building or interactive door prefab: it must be used with the compatible shell.

Validation of real saved resources, not just declared arithmetic:

- All six bay transforms and 30 fitting transforms match actual shell markers.
- **10,812 inserted GLB vertices** fit the literal rough openings and rear envelope.
- **Zero unintended shell/fitting surface intersections**. The checker identifies
  **288 triangle-pair wall contacts** only where canopy/fascia rails touch the flat
  facade and their triangles remain wholly exterior; penetration is not ignored.
- **60 cross-fitting pair checks**, zero surface intersections, including each
  actual surround/closed-leaf combination.
- Reused source meshes have **zero nonmanifold edges, zero degenerate faces and
  unit-length normals**. Imported GLBs have zero degenerate triangles and unit normals.
- Repetition-weighted whole assembly: **55,244 triangles; 27,908 source vertices;
  30,000 exported split vertices; 157 mesh instances; 167 surfaces; 31 GLB instances**.
  One fitting-only bay: **8,540 triangles, 26 meshes, 27 surfaces**. These are counts,
  not draw-call or target-device performance acceptance; six copies share resources.
- Six real physics rays at closed entries hit the shell at X=-9, never a fitting
  body. Five exterior capsule samples (.35 m radius, 1.8 m height) remain clear,
  including under a canopy, both side routes and north/south exterior samples.
  These bounded static queries do not establish actual player/car movement.
- Both owned scenes pass engine pack/save/reload byte stability. A fresh runtime
  load/check passes without warnings/errors; all dependency files remain unchanged.

[Hero](d06_southern_shopping_parade_02-evidence/hero.png),
[side](d06_southern_shopping_parade_02-evidence/side.png),
[bay detail](d06_southern_shopping_parade_02-evidence/bay_detail.png),
[overhead](d06_southern_shopping_parade_02-evidence/overhead_47m_42deg.png).
All four were personally inspected: continuous quiet roof, six coherent shop
stations, smooth shared hardware, recessed closed leaf and blank artwork carrier.
No obvious floating fitting or colliding trim was observed. The 1280×800 Cycles CPU
renders use 24 samples/AgX and actual GLBs at engine-measured scene transforms.

Overhead is vertically down, north-up, at Blender (-6,0,47), **42° vertical FOV**.
As with `.01`, the 60 m building exceeds the roughly 32 m roof-height vertical
frustum, so this is an intentional centre crop. Canopy noses are visible but the
roof hides doors and fascia faces. Essential gameplay wayfinding must not depend on
those faces. These are isolated Blender evidence, not native Godot visual acceptance.

## Reproduction and checks

From repository root, Git Bash; all scratch outputs are outside the worktree:

```sh
NID=d06_southern_shopping_parade_02
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
SCRATCH="C:/tmp/ft/assets/$NID"
mkdir -p "$SCRATCH"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --path . --script "res://tools/asset_production/$NID/check_prefab.gd"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/validate.py"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/render.py"
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks-fresh"
python "tools/asset_production/$NID/record.py" --verify
```

Production-check output must be fresh. `record.py` collects the final `checks/`,
`prefab.json`, `normalize.json`, `geometry.json` and normalization diagnostics into
lean retained evidence; `--verify` checks the complete produced file set and every
hash without mutation. Dependencies are checked against the retained validation.

Pinned Blender **5.2.2 LTS**, build **d13f752e3b9c**; Godot
**4.8.dev7.official.c971f93e7**. Production checks **PASS**: owned GDScript compilation
and pinned gdstyle; Python **9/9**; GUT **23/23, 196 assertions**; negative control
correctly detects its intentional failure. No inherited failures were suppressed.

Initial owned faults were caught and corrected: row/column sign confusion in the
handwritten bay rotation (marker and bounds tests rejected it), a renderer syntax
typo, and an initially over-strict intersection check rejecting intentional flush
mount-rail contacts (now narrowly classified by actual triangle coordinates).
Four initial GDScript lint warnings were corrected. Full scratch logs stay external;
`final.log` retains concise outcomes and unfiltered final editor diagnostics.
Headless editor shutdown emits the known scan/RID/ObjectDB diagnostics and toolkit
4.8 compatibility warning despite exit 0; runtime and production checks are clean.
The standalone Blender version probe reports one tiny unfreed block at exit; final
geometry validation and all four rendering jobs exit 0.

## Dependency refresh after the north-corner repair

During member .03 production, its close render exposed coplanar north-end trim caps
in the .01 shell. The supervisor authorized .01's **2 mm north trim-cap recess** and
this dependent evidence refresh in a separate family repair commit. See [.01's repair
record](d06_southern_shopping_parade_01.md#north-corner-seam-repair-during-member-03-production).
No .02 scene, transform, mesh or material was edited. Both saved scenes remain byte-unchanged.

The existing engine reference checker, pack/save/reload, source/actual-GLB fit checker,
four renders and production checks were rerun at the repaired dependency state. All
pass with the same bounds, counts, 10,812 insertion vertices, 60 cross-fitting checks
and 288 intentional flush contacts reported above. All four refreshed renders were
inspected; .03's close assembly confirms the black corner stripe is gone. Validation
and producer manifests now hash the repaired .01 source/export rather than retaining
obsolete dependency hashes. Fresh shared check receipt:
`C:/tmp/ft/assets/d06_southern_shopping_parade_03/checks-family-fix/`.

## Remaining acceptance

Independent technical/art review; tenant graphics;
owner final proportions and tenant selection; native gameplay-camera readability,
actual movement/aim/vehicle and multiplayer checks; current road-tool walking and
bridge approach fit; saved world identity consolidation/placement; packaged builds,
repeated-placement profiling, sustained performance and Deck checks remain pending.
No shared brief, register/queue/progress, TODO, project setting, road, world placement
or other family member was changed. This is a checked interface candidate, not a
blanket READY declaration for the building or the district.

## Review round 1 — sibling-delivery status

Removed the completed .03 north treatment from the pending list (P3), including the
matching `validation.json` entry and its `record.py` producer to prevent regeneration
of stale status. Independent review and all downstream acceptance gates remain pending.
Only status documentation/evidence and its producer changed; source, exports, saved
scenes and renders are unchanged, so export/render/import and geometry checks are
unaffected. Refreshed affected manifest entries and reran all three members'
`record.py --verify` checks, including immutable dependency hashes.

Round-1 check command:
`timeout 1800 mise exec -- python tools/production_checks.py --output C:/tmp/ft/assets/d06_southern_shopping_parade_02/checks-review-round-1`.
Result: **PASS**, owned compilation/format/lint, Python **9/9**, GUT **23/23** with
**196 assertions**, intentional negative control detected. Reviewed logs contain no
ERROR/WARNING diagnostics. A separate Python AST/JSON check confirms the producer
and retained pending lists match the seven remaining downstream gate groups.
