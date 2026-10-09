# city_marina_docks.03 — Shore-to-pontoon gangway and landing connector

10 October 2026. **Source, export and linked walkable component delivered; independent
review and full world/gameplay acceptance pending.** Original Blender construction by
the commissioned implementation specialist, following the [commission](commission.md),
[marina brief](../city_marina_docks.md), [Old Quay concept](../../concepts/districts-v1/old-quay.md)
and Petrol & Coral direction. No downloads, external artwork or real brands.

## Design and approved provisional interfaces

An open-ended composite gangway with a gently sloped six-metre span between two
one-metre flat landings. Pale manufactured rails, a restrained pale deck edge,
dark underdeck stringers and small petrol landing shoes make it distinct from a
floating pontoon. Twenty-four broad deck boards retain the quiet material rhythm
of the [main pontoon](city_marina_docks_01.md) and [finger](city_marina_docks_02.md).
No lamps, ropes, cleats, dedicated corner bumpers, seawall or yacht geometry is duplicated.

The supervisor explicitly approved the following **provisional** dimensions and
walkable profile, plus simple collision along the visible side guards. This continues
.01/.02's water/deck contract and supersedes the family brief's non-walkable scenery
restriction. It is **not basin-fit or actual shore-height acceptance**. Measurements
are authored, not extracted from raster boat/dock concepts.

| Interface | Godot local metres |
| --- | --- |
| Root/pivot | (0, 0, 0), centred on the water datum |
| Overall footprint | 2.000 X × 8.000 Z; long axis Z |
| Pontoon landing | Z = -4..-3, standing surface Y = .500 |
| Ramp | Z = -3..3, rising from Y = .500 to 1.500; 9.462322° |
| Shore landing | Z = 3..4, standing surface Y = 1.500 |
| End join centres | (0, .500, -4), (0, 1.500, 4) |
| Pale deck edge | 2 cm above the walking surface; visual lip only |
| Visual AABB | min (-1, .250, -4), max (1, 2.483527, 4) |
| Measured visual size X/Y/Z | (2.000, 2.233527, 8.000) |
| Clear space between guard collision faces | 1.780 X |
| Root and mesh transforms | Identity; metres, applied modifiers, no negative scale |

Envelope/datum tolerance is ±.001 m; the expected nominal guard-rounded maximum
is Y=2.484. Blender +Z maps to Godot +Y; Blender +Y maps to Godot -Z. The pivot
is deliberately at water level, not the hardware bottom. No exported sockets,
rig or animation: these are documented planar interfaces, not runtime attachment APIs.

To butt the lower landing to an identity .01 main section end, place that main
section at **(0, 0, -8)** relative to this gangway. Its +Z end and this -Z end
meet at Z=-4, Y=.50. A real shore needs a matching Y=1.50 standing surface at
Z=4. Do not change the coastline, reclaim land or stretch the component to force a fit.
The owned fixture uses another .01 at **(0, 1, 8)** solely as an elevated technical
shore stand-in; this is not a proposed floating module height or production quay.

## Source, export and materials

- Source: `art/source/models/environment/city_marina_docks_03/city_marina_docks_03.blend`.
- Collection: `export_city_marina_docks_03`; root `CityMarinaDocks03`, child
  `CityMarinaDocks03_Mesh` (55 closed manufactured component islands joined as one mesh).
- Explicit export: `art/models/environment/city_marina_docks_03/city_marina_docks_03.glb`
  with committed `.glb.import` identity.
- Linked prefab: `scenes/prefabs/environment/city_marina_docks_03.tscn`.
- Reproducible tools and owned physics fixture: `tools/asset_production/city_marina_docks_03/`.

Five opaque Principled surfaces use exactly the earlier marina names and PBR values.
No textures, embedded images, Godot material remaps or external resource dependencies:

| Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `dock_deck_dark_composite` | .075, .090, .085 | 0 | .60 |
| `dock_deck_soft_variation` | .082, .098, .092 | 0 | .60 |
| `dock_edge_warm_pale` | .57, .59, .51 | .12 | .48 |
| `dock_float_petrol` | .018, .045, .051 | 0 | .54 |
| `dock_frame_metal` | .055, .075, .079 | .55 | .44 |

The inherited petrol material name is used on the landing shoes; no float or buoyancy
is implied. Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**.
The export loads the shared `tools/assets/blender/export_settings.json`, filters
only the named collection, disables skins/animation and converts Y-up once.
Source/export/render/validation follow the existing lane patterns; there is no shared
marina authoring library to import. Studio objects exist only in the unsaved render scene.
Default Godot generated LODs remain enabled; their transitions/cost are not accepted.

## Prefab, collision and bounded movement checks

`Visuals/Model` is an identity-transform imported scene instance with linked GLB
ancestry, not copied render mesh data. `Collision/Body` is static-world layer 1,
mask 0, with exactly three deliberate shapes:

- `Deck`: one **28-triangle closed ConcavePolygonShape3D**, a continuous .16 m-thick
  flat–slope–flat slab across the full 2 m width. A single convex hull would bridge
  over the change in slope instead of following the approved profile. Godot's
  clockwise face winding is retained; backface collision is not enabled.
- `GuardLeft` / `GuardRight`: one thin box per visible ramp-side rail, each local
  size (.100, .986394, 6.082763), centred at (±.940, 1.500, 0), X rotation
  **-9.462322°**. These follow the same rigid rail line as the model, approximating
  the rail/post envelope rather than generating snagging per-bar shapes.

The guard envelope intentionally blocks the gaps between rails. Bevels and the
2 cm deck lip do not add collision. The guard ends extend about .081 m into the
landings because the posts lean perpendicular to the slope; all landing exits
remain open. There are no invisible barriers around landing sides or ends.
The asset has no moving/tidal state, runtime geometry assembly or gameplay script.

Pinned Godot **4.8.dev7.official.c971f93e7** imported the asset. The prefab and
owned `walk_check.tscn` were loaded, packed, saved and reloaded twice after the final
collision correction, preserving exact bytes, scene UIDs and node identities.
Checks verify all dependency UIDs, identity model transform, five opaque/back-culled
surfaces and independently expected imported bounds. Direct scene text authoring plus
isolated headless normalization was required by the brief; live Blender/Godot MCP
sessions were not touched. This does not synchronize or certify a separate open editor.

The saved fixture uses production `ActorMotion` and the production-sized radius
.35 m / height 1.8 m capsule. The test does not inject vertical velocity or gravity:

- **11 support rays** check both external butt joins, both ramp breaks and three
  independently specified intermediate slope heights; all hit the correct upward face.
- **Two lateral rays** hit the guard inner faces at X=±.890; **four landing-side rays**
  remain clear.
- **144 production movement ticks per direction/mode** cross both landings, the
  entire ramp and both external joins, with a downward support query every tick.
  The 9.462° ramp is below the actor's default 45° floor angle.
- **36 ticks per side/mode** drive into each guard and stop at X=±.5390625 rather
  than passing through visible rails. Clear width is sufficient for the tested capsule.

| Traversal | Start | Measured destination |
| --- | --- | --- |
| Uphill | (0, .501, -5) | (.000014685, 1.500513196, 6.832562447) |
| Downhill | (0, 1.501, 5) | (0, .501001239, -7.002119064) |

AUTHORITY and REPLAY match for both traversals and both guard stops. Two separate
standalone headless runs reproduced those results without script warnings/errors
or leaked-resource errors. This is production movement/replay API coverage, **not
multiplayer transport/admission/prediction acceptance**. ActorMotion still has no
gravity/falling; dock-edge/water behavior, navigation, real quay approach and yacht
clearance remain integration work. No production movement/network code was changed.

## Evidence and validation

[Hero](city_marina_docks_03-evidence/hero.png) ·
[Side](city_marina_docks_03-evidence/side.png) ·
[Landing/guard detail](city_marina_docks_03-evidence/detail.png) ·
[47 m / 42° overhead](city_marina_docks_03-evidence/overhead_47m_42deg.png).
All four final images were visually inspected alongside earlier family evidence.
Pale edges and the open walkway read overhead; plank joints remain subordinate.
The higher rail changes the side silhouette without adding ropes or noisy fine detail.
The studio-lit composite reads as the same subdued grey-green as .01/.02.

These are isolated Blender Cycles/AgX captures, **not engine/water/placement images**.
The overhead is vertically downward, Blender +Y at image top, perspective vertical
FOV 42° at 47 m. All are **1280×720**, explicitly approved instead of the older
1280×800 figure. Render compression 95, then PNG level 9 with seven significant
RGB bits/channel trims review storage without paintover or geometry changes.
Image dimensions/byte sizes are recorded in validation.json. Hero/detail are about
576/608 KiB, above the ~400 KB target: a six-bit encoding trial met that target but
visibly banded studio shadows, so the cleaner seven-bit images are retained. Side
and overhead are about 416/384 KiB. The rejected encoding remains outside the repo.

[validation.json](city_marina_docks_03-evidence/validation.json) records:

- **10,340 triangles; 5,280 source vertices; 6,370 exported split vertices**.
- **One mesh, five surfaces**, zero degenerate source faces/export triangles,
  zero non-manifold source edges, consistent winding and unit-length normals.
- Binary GLB positions/normals/indices independently inspected, not just accessor bounds.
- Full flat/slope/flat composite profile, approved envelope and water-centred identity pivot.
- Separate-process fresh export **byte-identical** to the **270,832-byte GLB**.
- Full `production_checks.py` passed: pinned engine/GUT, owned-script style/lint and
  explicit compilation (including this new check), **14 Python tests**, **75/75 GUT
  tests / 2,041 assertions**, plus the intentional GUT-failure negative control.
  No pre-existing failures were ignored.
- Owned `check.gd` passes pinned gdstyle 0.3.0 with zero warnings.

[manifest.json](city_marina_docks_03-evidence/manifest.json) hashes every delivered
payload with SHA-256/byte counts, excluding itself to avoid recursion.
[final.log](city_marina_docks_03-evidence/final.log) is the concise retained receipt.
Raw logs, superseded test results and scratch exports remain outside the repository
under `C:/tmp/ft/assets/city_marina_docks_03/`.

Initial self-check corrections: inset/shortened rail uprights removed coplanar black
junction artifacts; the final source/export/renders were regenerated and inspected.
The first authored collision triangles used Blender-style rather than Godot's clockwise
winding; independent support/normal/movement tests detected it, and the saved collision
was reversed and successfully retested. A float-equality assertion and gdstyle findings
were corrected without relaxing the independent movement/height expectations.
Blender emits a `use_nodes` deprecation warning. Headless editor operations emit the
addon's engine-version warning and editor-shutdown RID/ObjectDB leak diagnostics,
as with earlier lane assets. Final standalone physics checks and the isolated full
production-check compiler/test mirror are clean. No vendor diagnostics were suppressed.

## Reproduction

Run from repository root in Bash; each Blender invocation is audio-disabled,
factory-startup, four-threaded and bounded to 900 seconds. Godot uses only the mise
pin. Never use live editor sessions. PNG compaction/manifest requires Pillow.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_marina_docks_03
S=C:/tmp/ft/assets/city_marina_docks_03
mkdir -p "$S"
for step in author export render; do
  timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
    --python-exit-code 1 --python "$T/$step.py" || exit $?
done
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/export.py" -- "$S/reexport.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" -- "$S/reexport.glb"
timeout 300 "$G" --headless --editor --path . --import
timeout 180 "$G" --headless --editor --path . --script "$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "$T/check.gd"
"$(mise which gdstyle)" --max-warnings 0 "$T/check.gd"
# Use a fresh output directory for a subsequent check run.
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks-reproduction"
python "$T/manifest.py" "$S/checks-reproduction"
```

## Remaining acceptance

Independent reviewer disposition is required. The world owner must fit modest
shore-connected clusters to the unchanged basin, preserve central open water and
the southern harbour/bridge entrance, match actual quay heights and yacht envelopes,
and resolve entry/fall-off/water behavior before gameplay placement. Engine-camera
actor contrast, repeated joining seams, blue-hour lighting, LOD transitions,
GPU/Deck/device costs, packaged builds and real-process multiplayer remain pending.
No world scene, shared brief, queue/progress, gameplay rule or other marina asset changed.
The component is delivered for review, not blanket whole-city production acceptance.
