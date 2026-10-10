# city_traffic_fixtures.01 — Signal pole

10 October 2026. **Source/export, linked prefab and bounded headless checks complete;
independent review and world/gameplay acceptance pending.** Commissioned under the
[production commission](commission.md) and the per-asset common brief. The earlier
concept-only restriction in [traffic fixtures](../city_traffic_fixtures.md) is superseded
by this commission. No queue, shared brief, district or runtime gameplay logic changed.

Original author / technical integrator: commissioned implementation specialist, lane
`a-traffic`. Acceptance owner: supervising production lead and independent reviewer.
No live Blender/Godot editor session was accessed. Text-authored wrapper and test scene
were loaded, packed, saved and reopened in isolated pinned headless Godot because the
brief prohibits live MCP/windowed-editor use. This does not synchronize an open editor.

## Design and dimensions

A quiet petrol-metal tapered upright, flared cast ground shoe, restrained service hatch,
rounded short mast arm and downward mounting collar. No colored trim, lens, sign face,
traffic logic or signal head is included. The signal head remains `city_traffic_fixtures.02`;
road-sign support remains `.03`. The neutral material values follow the accepted street
light family. Ordinary broad highlights and a small silhouette keep this support from
competing with district landmark signs.

Original editable Blender construction; no downloads, image-to-mesh, real brands,
third-party mesh sources or runtime-generated render geometry. Design informed by the
approved [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), not dimensions
measured from their concept illustrations. No placement or junction requirement is implied.

**All dimensions below are provisional production choices**, not ratified street engineering:

- Godot X/Y/Z visual envelope: **0.440 × 4.540 × 1.750 m**.
- Visual AABB: minimum `(-0.220, 0, -1.530)`, maximum `(0.220, 4.540, 0.220)` m.
- Ground shoe maximum diameter 0.440 m; shoe height 0.300 m.
- Upright lower diameter 0.280 m, tapering to 0.180 m; elbow starts at height 4.130 m.
- Horizontal arm centre height 4.450 m, diameter 0.180 m. Arm points Blender +Y / Godot -Z.
- Mount collar underside height 4.200 m; maximum diameter 0.260 m; centre 1.400 m forward
  of the pole. Maximum forward visual reach is 1.530 m.
- Ground datum and root/mesh pivot `(0,0,0)` at the centre of the ground shoe, **not** the
  centre of the asymmetric whole-model AABB. Metres, applied rotations, unit scales.
- Envelope/ground acceptance tolerance ±0.001 m; source-to-export tolerance 0.00001 m.

### Signal-head handoff and road-tool interface

The pole is the carrier and owns the mount transform. Exported empty
`CityTrafficFixtures01/socket_signal_head` is at Blender `(0,1.400,4.200)` with identity
rotation and scale. Imported path beneath the prefab is
`Visuals/Model/CityTrafficFixtures01/socket_signal_head`; Godot position `(0,4.200,-1.400)`.
The saved public adapter is **`Sockets/SignalHead`**, also identity-oriented. The headless
check asserts the adapter exactly matches the source marker; a future source socket change
requires a coordinated adapter and sibling compatibility update, not a second hand-tuned datum.

For `.02`: use a **top-centred attachment pivot**, identity basis, Godot -Z front / +Y up;
geometry descends from the attachment, contacting the flat underside of the mounting collar.
Keep head depth below 1.700 m so all head geometry remains strictly above 2.500 m when mounted;
a roughly 1.2–1.35 m tall head would preserve generous head clearance. The collar presents a
0.240 m diameter underside. The carrier has no lens geometry or runtime control state.
The sibling owns its final envelope and any head-state contract. A saved composed assembly
may instance the unchanged pole/head prefabs; do not duplicate either carrier mesh.

The road tool may place the root at the saved sidewalk/ground datum, rotating about +Y so
local -Z projects toward the desired signal position. No automatic placement script or
junction policy was added. Reserve the measured footprint and overhang, plus the future
head envelope; resolve route/corner/vehicle clearances in actual placements.

## Source, exports and materials

- Source: `art/source/models/environment/city_traffic_fixtures_01/city_traffic_fixtures_01.blend`.
- Collection: `export_city_traffic_fixtures_01`.
- Root / mesh: `CityTrafficFixtures01` / `CityTrafficFixtures01_Mesh`, plus `socket_signal_head`.
- Export: `art/models/environment/city_traffic_fixtures_01/city_traffic_fixtures_01.glb` and
  engine-generated `.glb.import`.
- Linked wrapper: `scenes/prefabs/environment/city_traffic_fixtures_01.tscn`.
- Author, export, validation, engine check and evidence packaging scripts:
  `tools/asset_production/city_traffic_fixtures_01/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export reads
`tools/assets/blender/export_settings.json` with the explicit collection and static
animation/skin exclusions. Studio floor/cameras/lights never export. All modifiers are
applied before source save. The mesh comprises individually closed manufactured parts;
intentional hidden intersections at shoe/shaft, shaft/arm and arm/collar are not a fused
solid. The reported volume sums these closed components, not an engineering union volume.

Three stable opaque Principled slots, in order (RGB values are linear):

| Slot | Linear base RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `traffic_dark_metal` | .025, .075, .090 | .45 | .46 |
| `traffic_fixture_rim` | .070, .130, .150 | .50 | .42 |
| `traffic_service_recess` | .012, .025, .030 | .25 | .50 |

No textures, external material files, embedded images, emission, rig, animation, destruction
states or light nodes. Uniform color surfaces need no authored UVs. Godot retains default
mesh LOD generation and shadow meshes; no custom LOD or performance budget is claimed.

## Prefab and collision

`Visuals/Model` is an identity-transform linked GLB instance, not editable copied geometry.
Imported root is also identity. `Collision/PoleBody` is the only static body, with one
upright cylinder: radius **0.220 m**, height **4.130 m**, centre `(0,2.065,0)`, static-world
layer **1**, mask **0**. This deliberately conservative constant-width envelope covers the
shoe and excludes decorative snag points. The overhead elbow/arm/collar are visual-only.
There is no collision authored into the imported model and no new interaction behavior.

The owned saved `check_scene.tscn` contains the linked pole, collision-only floor and a
production `ActorMotion` capsule (radius .35 m, height 1.8 m). It is a test fixture, not a
new visible asset or world placement. `check.gd` checks dependency/UID resolution, source
socket mapping, actual mesh bounds/surfaces, collision filtering and save/reload byte stability.

## Evidence and reproduction

[Hero](city_traffic_fixtures_01-evidence/hero.png),
[side](city_traffic_fixtures_01-evidence/side.png),
[mount detail](city_traffic_fixtures_01-evidence/detail.png),
[47 m / 42° overhead](city_traffic_fixtures_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders at **1280×720**, 32 samples, AgX,
PNG compression 100, compacted to 7 significant RGB bits/channel. The overhead uses a
vertical-down perspective camera at 47 m, 42° vertical FOV, north/+Y at image top; the
720-pixel height follows the later lean-evidence instruction rather than historical 800.

Self-review inspected all four images. The broad tube/elbow reads cleanly in hero and side;
mount detail exposes the deliberately closed collar underside. At gameplay height the arm
is a small quiet stroke and the service hatch is intentionally subpixel. It is not intended
to read as a complete signal before the head sibling is attached. These are not engine
lighting, populated-city readability or final art acceptance captures.

From repository root in Git Bash (all scratch output remains outside the checkout):

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
N=city_traffic_fixtures_01
T="C:/tmp/ft/assets/$N"
mkdir -p "$T"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/author.py" > "$T/author.log" 2>&1
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/validate.py" > "$T/validate.log" 2>&1
# validate.py opens the saved source and fresh-exports to $T/reexport for strict byte comparison.
# To export the saved source independently without rebuilding it:
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background \
  --factory-startup "art/source/models/environment/$N/$N.blend" --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/export.py" -- "$T/reexport"
timeout 300 "$(mise which godot)" --headless --path . --import > "$T/import.log" 2>&1
timeout 180 "$(mise which godot)" --headless --path . \
  --script "res://tools/asset_production/$N/check.gd" -- --normalize > "$T/godot-check.log" 2>&1
timeout 30 "$(mise which gdstyle)" fmt --check "tools/asset_production/$N/check.gd"
timeout 30 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$N/check.gd"
# Checks output must not already contain a previous run.
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python "tools/asset_production/$N/finalize.py"
# After packaging, final import retains any engine-normalized metadata; then rehash.
timeout 300 "$(mise which godot)" --headless --path . --import > "$T/final-import.log" 2>&1
python "tools/asset_production/$N/finalize.py"
```

`validation.json` retains measured source/export/engine results and production-check summary.
`manifest.json` SHA-256 hashes every delivered file except itself. Large command logs,
intermediate exports and the isolated production-check mirror are scratch-only. The single
`final.log` is a concise final receipt, not a copy of raw diagnostic logs.

## Validation results

- **2,016 triangles; 1,024 source vertices; 920 source faces; 1,079 exported vertices;
  one mesh; three material surfaces.**
- Zero degenerate faces/triangles; zero non-manifold edges; positive closed-component volume.
- Max unit-normal length error: source `1.58e-7`, export `1.29e-7`.
- Source and actual GLB AABBs agree; ground, pivots, applied transforms and socket pass.
- Fresh saved-source re-export is **byte-identical** to the 49,908-byte GLB;
  SHA-256 `eecbbb6d7838edc735a547e737bca02248ccdcbc299e5acbc4dcca7089d97e83`.
- Godot **4.8.dev7.official.c971f93e7** import/load, linked ancestry, dependency UIDs,
  source socket mapping and wrapper/fixture save/reload pass.
- Low ray hits the pole; ray at 4.2 m clears the intentional non-colliding overhead region.
- Production `ActorMotion.step` passes 48 ticks per case per mode: contact stop approximately
  `(0,.001,-.58333)` m; clear bypass at X=.8 ends approximately `(.8,.001,2)` m.
  Authority/replay positions match. The contact envelope expectation is independently
  `.57 m` from pole centre, with .015 m tolerance for movement margin/tick behavior.
- Pinned gdstyle formatting/lint and explicit production script compilation pass.
- Full production checks **pass**: 17 Python tests, 149 GUT tests, 6,768 assertions,
  clean isolated import and expected failing diagnostic sentinel. No known failures waived.

Initial engine check assumed the source socket was directly under `Model`; inspection
showed the retained glTF root adds `CityTrafficFixtures01`. The check now uses the exact
imported path. Initial failed-run resource leaks arose from that interrupted check; final
checks exit cleanly without resource leaks. Blender prints its pinned-version `use_nodes`
API deprecation notices; normal output is retained, not suppressed. Project import emits
the existing MCP plugin's 4.8-versus-tested-4.7 compatibility warning; no missing-resource
or script error is present. The owned process may start the configured local plugin, but
no connector session or owner's live editor was contacted.

## Remaining acceptance

Independent technical/art review is required. The head sibling must demonstrate mounting
fit and combined appearance before any composed signal is accepted. No signal phase logic,
collision state transition, destructibility or automatic junction requirement is introduced.

Actual district placement, car swept clearance/impact tests, populated gameplay-camera
readability/aim occlusion, real separate-process transport/prediction behavior and packaged
Deck performance remain **pending**. Standalone authority/replay equality is not a multiplayer
transport test. No placement, runtime population or performance acceptance is inferred from
this source/import handoff, and no queue record or shared progress/TODO was marked complete.
