# city_marina_docks.02 — Narrow finger-pontoon section

10 October 2026. **Source, export and linked walkable component delivered; independent
review and full world/gameplay acceptance pending.** Original Blender construction by
the commissioned implementation specialist. Production follows the [commission](commission.md),
[marina brief](../city_marina_docks.md), [Old Quay concept](../../concepts/districts-v1/old-quay.md)
and Petrol & Coral direction. No downloads, external artwork or real brands.

## Design and approved provisional dimensions

A narrow composite finger with fifteen broad transverse planks, a restrained pale
perimeter, one rounded petrol flotation body and simple metal underdeck bearers.
The materials, deck height, edge profile and plank rhythm match the earlier
[main pontoon](city_marina_docks_01.md). This is new Blender construction at its own
width/span, not a scaled imported main section. No lamps, ropes, cleats, dedicated
corner bumpers or yachts are duplicated from other register rows.

The supervisor explicitly approved this provisional 1.50 × 6.00 m finger, matching
.01's water/deck datums and **walkable slab** requirement. That family approval
supersedes the original brief's scenery-only restriction; it does not approve
basin placement, docking envelopes or shore access. Dimensions were not measured
from raster concepts.

| Interface | Godot local metres |
| --- | --- |
| Root/pivot | (0, 0, 0), footprint-centred on the water datum |
| Deck footprint | 1.500 X × 6.000 Z; long axis Z |
| Deck standing surface | Y = 0.500 |
| Pale visual edge top | Y = 0.520; 2 cm lip is visual only |
| Flotation bottom/top | Y = -0.300 / 0.250 |
| Whole visual AABB | min (-0.750, -0.300, -3.000), max (0.750, 0.520, 3.000) |
| Whole size X/Y/Z | (1.500, 0.820, 6.000) |
| End joins | (0, 0.500, -3.000), (0, 0.500, 3.000), rectangular butt interfaces |
| End-to-end repetition | Translate 6.000 m along local Z |
| Collision slab | 1.500 × 0.160 × 6.000, centred (0, 0.420, 0), top Y=.500 |

Envelope/datum tolerance is ±0.001 m. Metre units, identity root/mesh local transforms,
applied modifiers, no negative scale. Blender +Z maps to Godot +Y; Blender +Y maps
to Godot -Z. The pivot is at water level, deliberately not the flotation bottom.
No rig, clips or sockets: the joins are documented planar interfaces, not runtime
attachment APIs. The 1.26 m composite inset sits between pale visual edges; collision
is the approved full 1.50 m width, with no raised snagging edge colliders.

For a perpendicular branch on .01 at identity, place this finger at **(4.5, 0, 0)**
with **+90° Y rotation**. Its near end at world X=1.5 butts to the main side; both
slabs meet at Y=.50. The owned test also places a finger extension at (10.5, 0, 0)
with the same rotation, joining at X=7.5. This extended branch is a test fixture,
not a proposed marina layout. No connector tongue, seam cover or mooring hardware
is implied; .04 and .05 retain their separate scope.

## Source, exports and materials

- Source: `art/source/models/environment/city_marina_docks_02/city_marina_docks_02.blend`.
- Collection: `export_city_marina_docks_02`; root `CityMarinaDocks02`, child
  `CityMarinaDocks02_Mesh` (27 closed component islands joined as one mesh).
- Export: `art/models/environment/city_marina_docks_02/city_marina_docks_02.glb`
  and its committed `.glb.import`.
- Prefab: `scenes/prefabs/environment/city_marina_docks_02.tscn`.
- Reproducible author/export/validate/render and check tools:
  `tools/asset_production/city_marina_docks_02/`.

Five opaque Principled material surfaces, matching .01's names and PBR values;
no textures, embedded images, external material dependencies or Godot remaps:

| Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `dock_deck_dark_composite` | .075, .090, .085 | 0 | .60 |
| `dock_deck_soft_variation` | .082, .098, .092 | 0 | .60 |
| `dock_edge_warm_pale` | .57, .59, .51 | .12 | .48 |
| `dock_float_petrol` | .018, .045, .051 | 0 | .54 |
| `dock_frame_metal` | .055, .075, .079 | .55 | .44 |

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. The export
loads the shared `tools/assets/blender/export_settings.json` contract, filters the
named collection, disables skins/animations and converts Y-up once. Studio objects
exist only in the unsaved render scene. No prototype references or runtime-generated
render geometry. Godot's default generated LODs remain enabled; no device budget
or LOD transition acceptance is claimed.

## Prefab, collision and bounded checks

`Visuals/Model` is an identity-transform linked imported scene instance, not copied
mesh content. `Collision/Body/Deck` is the only collider: a static-world layer 1,
mask 0 box, separate from the decorative float, frame and perimeter. Its continuous
support deliberately ignores the 8 mm plank joints and 2 cm visual lip. No invisible
edge barriers or extra snagging shapes are added.

Pinned Godot **4.8.dev7.official.c971f93e7** imported the asset. The prefab and owned
`walk_check.tscn` were loaded, packed, saved and reloaded twice with byte-stable
saved UIDs/node identities and linked ancestry. Checks resolve all fixture/prefab
dependency UIDs and verify imported bounds within .001 m, five opaque back-culled
surfaces, identity model transform and the independently expected slab envelope.
Direct text authoring plus isolated headless normalization was the required fallback;
no live editor/MCP session was used or changed. This does not claim interactive
editor synchronization or an unrelated open-scene roundtrip.

The authored fixture contains .01 plus two rotated .02 instances and a production
`ActorMotion` body using the production-sized radius .35 m / height 1.8 m capsule.
Ten support rays (including immediately before, on and after both joins) hit Y=.50;
two rays outside the narrow finger's sides are clear. Each seam is traversed for
48 production movement ticks in AUTHORITY and REPLAY modes:

| Case | Start | Actual destination |
| --- | --- | --- |
| Main side → finger end | (0, .501, 0) | (3.999998331, .500999987, 0) |
| Finger end → extension end | (6, .501, 0) | (9.999996185, .500999987, 0) |

Both modes match and downward `test_move` confirms destination support. Two separate
standalone headless runs reproduce these results without script errors or leaked-resource
errors. This is component movement/replay coverage, **not multiplayer transport,
admission or prediction acceptance**. ActorMotion currently implements no gravity or
falling; water/fall-off, shore entry, navigation and basin safety remain integration work.

## Evidence and validation

[Hero](city_marina_docks_02-evidence/hero.png) ·
[Side](city_marina_docks_02-evidence/side.png) ·
[Detail](city_marina_docks_02-evidence/detail.png) ·
[47 m / 42° overhead](city_marina_docks_02-evidence/overhead_47m_42deg.png).
All four were visually inspected alongside .01's hero. The narrow outline and pale
perimeter read from overhead; plank seams are subordinate. Studio-lit composite
reads subdued grey-green, consistent with .01, not noisy timber. The close views
show rounded flotation, a restrained frame and closed manufactured edge joints.

These are isolated Blender Cycles/AgX views, not engine, water or placement captures.
Overhead is vertically down, Blender +Y at image top, perspective **42° vertical
FOV at 47 m**. All are **1280×720**, explicitly approved to supersede the older
1280×800 requirement. PNG compression 95 at render, then level 9 with seven
significant RGB bits/channel, preserves smooth gradients; final images are
approximately 371–472 KiB. No paintover or geometry edits were applied to images.

[validation.json](city_marina_docks_02-evidence/validation.json) records:

- **5,076 triangles; 2,592 source vertices; 3,123 exported split vertices**.
- **One mesh, five surfaces**, zero degenerate source faces/export triangles,
  zero non-manifold source edges, consistent winding and unit-length normals.
- Binary GLB positions, normals and triangle indices checked independently of
  declared accessor bounds; no images, skins, animations or extra nodes.
- Approved **1.50 × .82 × 6.00 m** visual envelope, deck .50 m, water-centred pivot.
- Separate-process fresh export **byte-identical** to the **135,408-byte GLB**.
- Full `production_checks.py` passed: pinned engine/GUT, owned-script formatting,
  lint and explicit compilation, **14 Python tests**, **75/75 GUT tests / 2,041 asserts**,
  and the intentional GUT-failure negative control. No pre-existing failures ignored.
- Owned `check.gd` passes pinned gdstyle 0.3.0 with zero warnings.

[manifest.json](city_marina_docks_02-evidence/manifest.json) lists SHA-256 and byte counts
for every delivered payload, excluding itself to avoid recursive hashing.
[final.log](city_marina_docks_02-evidence/final.log) is the concise retained receipt.
Raw logs and scratch exports remain outside the repository at
`C:/tmp/ft/assets/city_marina_docks_02/`.

Diagnostics: Blender emits a `use_nodes` deprecation warning but exits normally.
Godot import emits the addon's engine-version warning; editor normalization also
emits editor-shutdown RID/ObjectDB leakage diagnostics, as in .01. Saved-resource
checks complete successfully; final standalone physics runs contain no warnings/errors.
Initial owned gdstyle length/trailing-comma warnings were corrected before the passing
full checks. No broad suppression, vendor changes or repeated failing validation runs.

## Reproduction

Run from repository root with Bash; each Blender call is audio-disabled,
factory-startup, four-threaded and capped at 900 seconds. Use only the mise-pinned
Godot engine; do not use live editor sessions. Image compaction/manifest needs Pillow.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_marina_docks_02
S=C:/tmp/ft/assets/city_marina_docks_02
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
# Use a new output directory on subsequent production-check runs.
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks-reproduction"
python "$T/manifest.py" "$S/checks-reproduction"
```

## Remaining acceptance

Independent reviewer disposition is required. The world owner must fit modest
shore-connected clusters to the unchanged basin, preserve central water and the
southern harbour/bridge entrance, coordinate yachts and remaining marina components,
and resolve shore access and water/fall-off behavior before gameplay placement.
Actual engine camera/blue-hour lighting, actor contrast, visual joining seams,
LOD transitions, repeated-piece GPU/device/Deck costs, packaged builds and real-process
multiplayer remain pending. No world, shared brief, queue/progress, gameplay code or
other marina asset was modified. Full production/placement acceptance is not claimed.
