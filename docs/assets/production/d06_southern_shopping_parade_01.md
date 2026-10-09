# d06_southern_shopping_parade.01 — Continuous long building shell and roof

**Source/export and bounded linked-prefab candidate. Independent review and final
production/world acceptance remain pending.** Production is commissioned by the
current asset-register task and [common commission](commission.md), superseding the
historical concept-only restriction in the [family brief](../d06_southern_shopping_parade.md).
Original author and technical integrator: commissioned isolated production worker.
Supervisor approved the provisional 18 × 60 m, approximately 5.4 m, one-storey envelope
and six standard fitting stations on the primary side during this run. This is not
an owner-selected final parcel, tenant count or bridge-clearance acceptance.

## Design and ownership

One uninterrupted blue/slate roof pan, continuous parapet and head courses, muted
plum walls, six west-facing paired door/window recesses, and restrained structural
piers make one long building rather than six touching pavilions. Two quiet roof folds
run its full length. No roof equipment, tenant signs, luminous accents or additional
pavilions are baked into the shell. The service side is intentionally quiet and solid.

References read and visually inspected: Signal Row v03 and its exact map extract,
Stage 3 district identities, Stage 4 street context, Petrol & Coral direction and the
accepted city_lights.01 handoff. The shared small-shop-shell .01 interface supplies
literal mount and opening dimensions. Reference images are style only, not measured
geometry. Everything visible in this asset is original editable Blender construction;
no downloads, real brands, textures, image-to-mesh, copied model or runtime geometry.

- **Member .01 (this delivery):** continuous shell/roof, fitting datums, closed recess
  backers and one solid exterior-only collider.
- **Member .02:** reference assembly using existing city_shop_fittings prefabs, not
  duplicate door/window/fascia/canopy meshes. Shared fitting collisions must be
  disabled in fitted variants; this shell owns the entire blocked footprint.
- **Member .03:** distinctive north-end facade within this same building, not another
  shell or a bridge landing building. The north end is a plain wall in this delivery.
- Commercial graphics retain tenant identity. No interiors, working doors, rooftop
  traversal, destruction, rigs, animations, navigation or placement are supplied.

## Metres, orientation and family interface

Blender +Y is geographic north, mapping to Godot -Z; +Z maps to Godot +Y.
Primary frontage faces **west (-X)**, not north. Root and mesh transforms are identity,
with geometry offsets baked in. Origin `(0,0,0)` is the ground-centred structural
footprint; all structural ground contact is at Y=0 in Godot.

| Measurement | Metres |
| --- | --- |
| Structural width east-west × length north-south | 18.000 × 60.000 |
| Main facade planes | Godot X=-9.000 west, +9.000 east |
| Ground / continuous wall top / roof pan top | 0 / 5.250 / 5.130 |
| Continuous roof underside / coping top | 4.950 / 5.400 |
| Full Godot visual AABB min | (-9.045, 0, -30.035) |
| Full Godot visual AABB max | (9.040, 5.400, 30.035) |
| Full visual size X/Y/Z | 18.085 × 5.400 × 60.070 |
| Maximum structural trim projection | 0.045 west, 0.040 east, 0.035 at either end |
| Bounds acceptance tolerance | ±0.001 per bound; source/export comparison 0.00001 |
| Exterior solid box size / centre | (18, 5.25, 60) / (0, 2.625, 0) |

Six station centres run north to south, Godot Z = **-25, -15, -5, 5, 15, 25**.
Each hosts a centred 6.4 m interface at 10 m pitch, leaving 3.6 m between fitting
station edges. `west_bay_01` is the northmost west station; `east_bay_01` is opposite.
Both station families have their origins at ground level on the wall plane.
Their local -Z points outward: west -X, east +X. Local +X runs north on the west side,
south on the east side. Never mirror fittings or add corrective root scale.

Actual imported path below prefab root:
`Visuals/Model/D06SouthernShoppingParade01/west_bay_01`.
The corresponding `west_bay_01_mount_*` children carry the standard local transforms:

| Child suffix | Station-local Godot translation | Existing consumer |
| --- | --- | --- |
| `mount_entrance_single` | (1.950, 0, 0) | city_shop_fittings.03 single surround |
| `mount_door_single` | (1.950, 0, 0) | city_shop_fittings.06 single closed leaf |
| `mount_display_window` | (-0.950, 0.480, 0) | city_shop_fittings.05 |
| `mount_canopy` | (-0.950, 3.000, 0) | city_shop_fittings.01 |
| `mount_fascia` | (-0.950, 3.800, 0) | city_shop_fittings.02 |

These are authored source empties retained through GLB import, not runtime placement
code. Use the marker transforms as the fitting placement writer. Identical names
with the appropriate side and station number cover all twelve frames.

The west wall has actual standard apertures in station-local horizontal u / height h:
window u[-2.470,0.570], h[0.540,2.420]; entry u[1.240,2.660], h[0,2.450].
Wall thickness is 0.280 m. The aperture insertion space remains clear through 0.540 m;
opaque backing starts 0.600 m behind the west face. This backer is a dark closed
recess, **not a duplicated pane/door and not a playable interior**. 972 source ray
probes verify all six pairs through the insertion envelope. Surround/window/canopy
fit dimensions inherit the shared-shell contract; actual all-fitting assembled
intersection review belongs to .02, not a claim made by these empty-shell probes.

East stations preserve mounting planes, heights and rhythm only: the rear is solid
plum wall without insertion holes, and no rear fitting is included or accepted.
Surface-mounted fascia/canopy placement is possible; inset doors/windows would
require an explicitly coordinated shell variant, not a silently obstructed assembly.

`north_facade_datum` is a root child at Godot `(0,0,-30)` with identity axes and -Z
outward, below the same imported `D06SouthernShoppingParade01` root. The wall spans
X[-8.72,8.72] between long walls, height 0–5.25; its outer surface is Z=-30.
Member .03 can use the full 18 m end width but must respect the solid shell and
preserve the ground forecourt. No bridge sockets, roof landing or forecourt mesh.

## Map-fit candidate, not placement

The read-only checker uses the exact frozen `brackett_greybox/authoring_plan.json`
district polygon and carriageway triangles, retaining its SHA-256 in validation.
An **unplaced** candidate centre at concept-map east/south `(528,499)` m, corresponding
to Godot `(-102,0,144)` at zero yaw, fits the southern strip:

- Entire visual footprint lies inside district 06 and overlaps no frozen carriageway;
  closest carriageway gap is **8.416 m**.
- A separate **3 m west walking band**, after a **1.2 m fitting-installation reservation**,
  remains inside the district with no road overlap (minimum road gap **5.897 m**).
- A **3 m east walking band** also fits (minimum road gap **7.614 m**).
- North reserve **18 × 9.965 m** remains inside the district, clear of frozen roads
  (minimum gap **7.679 m**). It is a ground forecourt candidate, not bridge engineering.

No scene, road, boundary or saved identity was changed. IDs
`brackett/district_06/building_0001`, `building_0008` and `building_0005` still exist
unchanged. Their later consolidation/migration belongs to the world integrator.
These checks are against frozen carriageways, not current road-tool sidewalks,
vehicle sweeps, navigation, final bridge access or movement clearance acceptance.

## Source, export, materials and prefab

- Source: `art/source/models/environment/d06_southern_shopping_parade_01/d06_southern_shopping_parade_01.blend`.
- Collection: `export_d06_southern_shopping_parade_01`.
- Root / mesh: `D06SouthernShoppingParade01` / `D06SouthernShoppingParade01_Mesh`.
- Export: `art/models/environment/d06_southern_shopping_parade_01/d06_southern_shopping_parade_01.glb` and committed `.import`.
- Prefab: `scenes/prefabs/environment/d06_southern_shopping_parade_01.tscn`.
- Tools: `tools/asset_production/d06_southern_shopping_parade_01/`.

The one mesh contains closed semantic components, not a boolean-fused building.
All static modifiers are applied. A named one-metre reference, studio ground, lights
and camera stay outside the export collection. Export uses the shared
`tools/assets/blender/export_settings.json`, pinned **Blender 5.2.2 LTS** build
`d13f752e3b9c`, glTF exporter **5.2.40**, with static animations/skins disabled.
No embedded images, external textures or unused material resources are required.

Five opaque back-culling Principled surfaces, with sRGB swatches converted to linear:

| Material | Swatch | Metallic / roughness |
| --- | --- | --- |
| `parade_muted_plum_render` | #81777C | 0 / .70 |
| `parade_dark_coping_recess` | #334950 | .20 / .55 |
| `parade_slate_plinth` | #4A5358 | 0 / .70 |
| `parade_warm_structural_trim` | #BBB6A8 | 0 / .70 |
| `parade_quiet_blue_roof` | #405B68 | .12 / .65 |

The prefab instances the imported GLB at identity `Visuals/Model`, retaining model
UID `uid://ru0vf0cfypuj` and prefab UID `uid://cjhrw3fdflgkg`. One separate
`Collision/Body/SolidFootprint` box uses layer 1/mask 0. Recesses are intentionally
blocked by this solid exterior envelope; trim/roof coping adds no snag colliders.
No navigation, behavior script, embedded replacement mesh or live/editor session mutation.
Automatic import LOD generation remains at the engine default; transitions and
repeated-placement performance are not accepted by this handoff.

## Evidence, measurements and reproduction

[Hero](d06_southern_shopping_parade_01-evidence/hero.png),
[side](d06_southern_shopping_parade_01-evidence/side.png),
[bay detail](d06_southern_shopping_parade_01-evidence/bay_detail.png),
[47 m / 42° overhead](d06_southern_shopping_parade_01-evidence/overhead_47m_42deg.png).
All four were personally inspected by the producer. Cycles CPU, 24 samples, AgX,
1280×800 isolated Blender views: **not native engine visual acceptance**.

The calibrated overhead camera is vertically down, north-up, at `(-6,0,47)` in
Blender, 42° vertical perspective FOV. At roof height the vertical frustum covers
only about 32 m of this 60 m building, so the overhead intentionally shows the centre
crop; hero/side show the complete silhouette. The quiet continuous roof reads well;
recessed frontage is hidden from directly overhead and must not carry essential
wayfinding. Tenant differentiation awaits fittings/graphics, not added roof clutter.

Final geometry: **4,004 triangles; 2,060 source vertices; 2,736 exported split vertices;
one mesh; five surfaces; 75 exported nodes** (root, mesh, twelve station frames,
sixty fitting markers and north datum). **Zero degenerate faces/triangles, zero
nonmanifold edges, unit-length source/export normals, positive triangle/normal
alignment.** Actual decoded GLB bounds match source axis conversion; exact named
membership excludes the studio. GLB **100,740 bytes**, fresh saved-source re-export
**byte-identical**. `validation.json` records these results, map fit and engine checks;
`manifest.json` hashes every produced payload except itself.

Pinned Godot **4.8.dev7.official.c971f93e7** loaded the imported model and prefab,
verified all materials, actual bounds, identities and northmost west mount orientation.
Seven independent physics shape probes and a west-facing ray passed. Headless editor
pack/save/reload is byte-stable. A subsequent fresh runtime load/query exits zero
without warnings/errors. This is not actual player/car handling or multiplayer proof.

Exact reproduction from repository root (Git Bash; scratch output is external):

```sh
NID=d06_southern_shopping_parade_01
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
SCRATCH="C:/tmp/ft/assets/$NID"
mkdir -p "$SCRATCH"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/validate.py"
python "tools/asset_production/$NID/check_map_fit.py"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --path . --script "res://tools/asset_production/$NID/check_prefab.gd" -- --output "$SCRATCH/prefab-fresh-final.json"
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks-fresh"
```

The last command requires a fresh output directory. Map checking uses Shapely (as
existing greybox tools do). `record.py` assembles retained final scratch receipts
and writes the lean manifest after reviewing all outputs; `record.py --verify`
checks the complete deliverable set/hashes without modifying anything.

## North-corner seam repair during member .03 production

The .03 close assembly render exposed coplanar end caps in this source: the northmost
west structural pier and both head courses ended exactly at the north wall plane.
The supervisor explicitly authorized a separate minimal .01 repair and downstream
.02 evidence refresh. Their north ends now stop at Blender Y=29.998 instead of 30:
a **2 mm recess**, with no change to the approved total envelope, roof, collision,
pivot, fitting stations or saved prefab/GLB UIDs. This does not widen .03 to hide a fault.

Three new literal source-ray regression cases at X=-8.85/Z=2, X=-8.85/Z=4.55 and
X=8.85/Z=4.55 verify that the visible north cap is the plum wall, never competing
warm trim. Source topology, raw GLB and byte-identical saved-source reexport pass;
all four source renders, import, prefab roundtrip and runtime physics were rerun.
The .02 reference's original fit checker and four renders also pass; its saved scenes
are byte-unchanged. All refreshed renders were inspected. The close .03 view confirms
the black corner stripe is gone. Production checks pass at the repaired family state.
Counts and bounds above are unchanged; payload size/hash and manifests are refreshed.

Exact repair checks use the reproduction commands above plus .02's documented checker,
validator and renderer. Fresh shared production-check receipt for this repair:
`C:/tmp/ft/assets/d06_southern_shopping_parade_03/checks-family-fix/`.
This is bounded source/visual repair, not independent acceptance or world placement.

## Diagnostics and remaining acceptance

Production checks **PASS**: all discovered owned GDScripts compile and pass pinned
format/lint; Python **9/9**; GUT **23/23, 196 assertions**; intentional negative-control
failure correctly detected. No inherited failure was suppressed.

Initial normalization lacked `@tool`, so editor-mode script execution timed out;
the checker was corrected to run as a tool and never await runtime physics in editor
mode. Runtime-only saves initially omitted UIDs; editor normalization and a subsequent
filesystem import established and verified both UIDs. Initial two lint warnings were
fixed. Blender logs contain only API deprecation notices. Headless editor normalization
exits zero but emits known scan-thread/RID/ObjectDB shutdown diagnostics and the toolkit
4.8 compatibility warning; these are retained in `final.log`, not claimed clean.
Fresh runtime checks and the independent production-check mirror are clean. No owner's
live Blender or Godot MCP session was used or touched.

Pending: independent technical/art review; .02 fitted assembly; .03 north treatment;
owner final proportions/tenant choice; current road-tool and bridge landing fit; world
identity consolidation/placement; native gameplay-camera/readability; actual movement,
aim and multiplayer implications; packaged builds, sustained profiling and Deck checks.
No queue, shared progress/brief, project setting, TODO or saved placement was changed.
