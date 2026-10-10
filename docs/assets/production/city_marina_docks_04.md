# city_marina_docks.04 — Dock end/corner connector and edge bumper treatment

10 October 2026. **Source, exports and linked components delivered; independent review
and full world/gameplay acceptance pending.** Original Blender construction by the
commissioned implementation specialist, following the [commission](commission.md),
[marina brief](../city_marina_docks.md), [Old Quay concept](../../concepts/districts-v1/old-quay.md)
and Petrol & Coral direction. No downloads, external artwork or real brands.

## Design and approved provisional interfaces

A square composite connector with eight broad boards, restrained pale edging, a
rounded petrol float and simple underdeck bearers. One continuous rounded L-shaped
rubber bumper protects the two outside edges. A separate 1.5 m straight rubber
segment dresses exposed main/finger pontoon edges and end caps. The construction,
water datum and five base materials match [main .01](city_marina_docks_01.md),
[finger .02](city_marina_docks_02.md) and [gangway .03](city_marina_docks_03.md).
No ropes, cleats, lamps, yachts, railings or new gameplay systems are duplicated.

The supervisor explicitly approved these **provisional** dimensions and variants,
including a walkable slab and collision-free bumpers at/below deck height. This
continues the family walkable override of the original scenery-only brief. It does
not approve basin placement, boat envelopes or water gameplay. No measurements were
extracted from raster concepts. Envelope/datum tolerance is ±.001 m.

| Interface | Godot local metres |
| --- | --- |
| Connector root | (0, 0, 0), footprint-centred on water datum |
| Deck footprint / standing surface | 3.000 X × 3.000 Z / Y=.500 |
| Pale visual lip | Top Y=.520; visual only |
| Float bottom / top | Y=-.300 / .250 |
| Open joins | -Z centre (0,.500,-1.500), +X centre (1.500,.500,0) |
| Integrated bumper | Exposed -X/+Z edges; Y=.200..460; maximum .120 m outboard |
| Connector visual AABB | min (-1.620,-.300,-1.500), max (1.500,.520,1.620) |
| Connector visual size X/Y/Z | (3.120,.820,3.120) |
| Slab collider | Size (3,.160,3), centre (0,.420,0), top .500 |
| Separate bumper anchor | Edge centre at water datum; +Z faces out toward water |
| Separate bumper AABB | min (-.750,.200,-.020), max (.750,.460,.120) |
| Separate bumper size X/Y/Z | (1.500,.260,.140) |

Both exported roots/meshes have identity local transforms, metre units and applied
modifiers; no negative scale. Blender +Z maps to Godot +Y; Blender +Y maps to Godot
-Z. Water/edge anchors deliberately differ from geometry-bottom pivots. The bumper
insets 2 cm into the pale edge and ends 4 cm below the walking surface. No rig, clips
or exported sockets: these are documented static planar joins, not runtime APIs.

### Assembly examples (not world placements)

- For a full-width right-angle turn, leave the connector at identity; place .01 at
  **(0,0,-5.5)** with no rotation and another .01 at **(5.5,0,0)** with **+90° Y**.
  Slabs butt at Z=-1.5 and X=1.5 respectively. The integrated bumper occupies the
  two outside edges; do not connect another pontoon through an integrated bumper.
- For a terminal platform joined only on -Z, dress the unused +X edge with two
  separate bumpers at **(1.5,0,-.75)** and **(1.5,0,.75)**, both **+90° Y**.
  The two other exposed sides already carry the integrated L bumper.
- A .02 finger at identity takes one end bumper at **(0,0,3)**, identity rotation.
  A .01 main takes two at **(-.75,0,4)** and **(.75,0,4)**, identity rotation.
- Repetition pitch is 1.5 m along the bumper's local X. Rounded segment ends create
  intentional manufactured joints. Four segments cover a 6 m finger side. On an
  8 m main side, five centred segments cover 7.5 m, leaving .25 m at each end;
  this is selective edge dressing, not a seamless arbitrary-length rail. Do not
  stretch exports or add bumpers across walking joins to force a fit.

## Source, exports and materials

- Source: `art/source/models/environment/city_marina_docks_04/city_marina_docks_04.blend`.
- Connector: collection `export_city_marina_docks_04`, root `CityMarinaDocks04`,
  child `CityMarinaDocks04_Mesh`; export `art/models/environment/city_marina_docks_04/city_marina_docks_04.glb`.
- Separate edge: collection `export_city_marina_docks_04_bumper`, root
  `CityMarinaDocks04Bumper`, child `CityMarinaDocks04Bumper_Mesh`; export
  `art/models/environment/city_marina_docks_04/city_marina_docks_04_bumper.glb`.
- Committed `.glb.import` sidecars; linked wrappers
  `scenes/prefabs/environment/city_marina_docks_04.tscn` and
  `scenes/prefabs/environment/city_marina_docks_04_bumper.tscn`.
- Author/export/validate/render/manifest scripts and saved physics fixture:
  `tools/asset_production/city_marina_docks_04/`.

Six opaque Principled surfaces on the connector; only the rubber surface on the
separate bumper. No textures, embedded images, Godot remaps or external materials.

| Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `dock_deck_dark_composite` | .075, .090, .085 | 0 | .60 |
| `dock_deck_soft_variation` | .082, .098, .092 | 0 | .60 |
| `dock_edge_warm_pale` | .57, .59, .51 | .12 | .48 |
| `dock_float_petrol` | .018, .045, .051 | 0 | .54 |
| `dock_frame_metal` | .055, .075, .079 | .55 | .44 |
| `dock_bumper_petrol_rubber` | .018, .045, .051 | 0 | .80 |

The new rubber retains the family petrol hue but has a rougher nonmetallic finish.
Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export loads
`tools/assets/blender/export_settings.json`, filters each named collection, disables
skins/animation and applies Y-up conversion once. Lane authoring patterns are reused;
there is no shared marina geometry-authoring library. Studio objects and the separated
bumper presentation offset exist only in the unsaved evidence scene. No runtime render
geometry or authored hierarchy generation. Default Godot generated LODs remain enabled;
transition appearance and performance are not accepted.

## Prefabs, collision and bounded checks

Both wrappers retain `Visuals/Model` as identity-transform imported scene instances.
Only the connector has `Collision/Body/Deck`: a static-world layer 1, mask 0 box.
The continuous slab ignores plank seams, bevels and the 2 cm visual lip; float, frame
and bumpers add no snagging collision. No invisible edge barriers were introduced.

Pinned Godot **4.8.dev7.official.c971f93e7** imported both exports. Both wrappers and
owned `walk_check.tscn` were packed, saved and reloaded twice with byte-stable UIDs
and node identities. Dependency UID/path resolution, linked ancestry, imported bounds,
opaque/back-culled connector surfaces, separate bumper bounds and visual-only status
pass. Text-authored scenes plus isolated headless normalization were the mandated
fallback; no live editor/MCP session was touched. This does not certify synchronization
or an interactive roundtrip in another open editor.

The saved fixture contains the right-angle .01/connector/.01 assembly above, plus a
separate .02 end-bumper mounting example. Production `ActorMotion` uses the production
radius .35 m / height 1.8 m capsule, without injected vertical velocity or gravity:

- **11 support rays** hit Y=.50, including immediately before/on/after both joins,
  the outside deck corner and finger end.
- **Three outboard rays** through the visible integrated/standalone bumpers are clear,
  proving they add no walking floor outside the slab.
- **72 ticks per direction/mode** traverse six metres around the 90° turn, with a
  downward native `test_move` support assertion and deck-height assertion every tick.
- Forward destination: **(2.999999285,.500999987,-.000000551)**.
  Reverse destination: **(.000000551,.500999987,-2.999999285)**.
  AUTHORITY and REPLAY agree; clean separate-process repeats reproduce both outcomes.

This is component movement/replay coverage, **not multiplayer transport/admission/
prediction acceptance**. ActorMotion still has no gravity/falling. Water/fall-off,
shore entry, navigation, yacht clearance and real quay placement remain downstream.

## Evidence and validation

[Hero](city_marina_docks_04-evidence/hero.png) ·
[Side](city_marina_docks_04-evidence/side.png) ·
[Corner detail](city_marina_docks_04-evidence/detail.png) ·
[47 m / 42° overhead](city_marina_docks_04-evidence/overhead_47m_42deg.png).
All four final images were inspected and compared with the earlier family hero.
The pale square boundary reads overhead; plank seams and rubber remain subordinate,
not gameplay cues. Close views show a rounded continuous corner rather than intersecting
bumper bars. The separate strip is displayed offset 2.7 m in Blender X solely for
inspection, not as a mounted placement. Composite color matches the earlier quiet kit.

Isolated Blender Cycles/AgX captures, **not engine/water/world images**. All are
**1280×720**, approved instead of the old 1280×800 figure. Overhead is vertical-down,
Blender +Y at image top, 47 m height / 42° vertical perspective FOV. PNG compression
95, then level 9 with seven significant RGB bits/channel; final images 362–398 KiB.
No paintover or geometry changes were applied to images.

[validation.json](city_marina_docks_04-evidence/validation.json) records:

| Export | Triangles | Source vertices | Split GLB vertices | Meshes / surfaces | GLB bytes |
| --- | ---: | ---: | ---: | --- | ---: |
| Connector | 3,856 | 1,968 | 2,340 | 1 / 6 | 103,960 |
| Edge bumper | 188 | 96 | 115 | 1 / 1 | 6,124 |

Both have zero degenerate source faces/export triangles, zero non-manifold source
edges, consistent winding and unit-length normals. Binary positions/normals/indices
are inspected independently of accessor bounds. Approved envelopes and identity pivots
pass; both separate-process fresh exports are **byte-identical** to committed GLBs.
Full `production_checks.py` passes pinned engine/GUT checks, owned script formatting,
lint and explicit compilation, **14 Python tests**, **75/75 GUT tests / 2,041 asserts**,
and the intentional failing-GUT negative control. No pre-existing failures ignored.
Owned `check.gd` passes gdstyle 0.3.0 with zero warnings.

[manifest.json](city_marina_docks_04-evidence/manifest.json) hashes every delivered
payload except itself. [final.log](city_marina_docks_04-evidence/final.log) is the one
concise receipt. Raw logs and scratch exports are outside the repo under
`C:/tmp/ft/assets/city_marina_docks_04/`.

Self-check corrections: a validator string literal and a typed-array conditional in
the movement helper were fixed. The latter initially emitted script errors despite
exit 0; those runs were rejected, helper completion was independently asserted, and
final runtime logs were checked for errors as well as exit status. A small helper
extraction resolved gdstyle complexity warnings. Blender emits `use_nodes` deprecation;
headless editor normalization emits addon-version and shutdown RID/ObjectDB leak
diagnostics, as with .01–.03. Final standalone physics logs and the isolated full
production-check compiler/test mirror are clean. No diagnostics were suppressed.

## Reproduction

Run from repository root in Bash. Each Blender call is audio-disabled, factory-startup,
four-threaded and bounded to 900 seconds. Use only the mise-pinned Godot, never live
sessions. PNG compaction and manifest generation need Pillow.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_marina_docks_04
S=C:/tmp/ft/assets/city_marina_docks_04
mkdir -p "$S"
for step in author export render; do
  timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
    --python-exit-code 1 --python "$T/$step.py" || exit $?
done
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/export.py" -- "$S/reexport"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" -- "$S/reexport"
timeout 300 "$G" --headless --editor --path . --import
timeout 180 "$G" --headless --editor --path . --script "$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "$T/check.gd"
"$(mise which gdstyle)" --max-warnings 0 "$T/check.gd"
# Use a fresh output directory for subsequent production-check runs.
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks-reproduction"
python "$T/manifest.py" "$S/checks-reproduction"
```

## Remaining acceptance

Independent reviewer disposition is required. World integration must fit modest
shore-connected clusters to the unchanged basin, preserve central water and southern
entrance/bridge clearance, coordinate yachts and actual shore heights, and resolve
entry/water/fall-off before gameplay placement. Engine-camera actor contrast, blue-hour
lighting, joined appearance, LOD transitions, repeated GPU/Deck costs, packaged builds
and real-process multiplayer remain pending. No world, shared brief/queue/progress,
gameplay rule or earlier family asset changed. This delivery is for review, not blanket
whole-city production acceptance.
