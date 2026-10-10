# city_traffic_fixtures.02 — Signal head

10 October 2026. **Source/export, linked prefabs and bounded headless checks complete;
independent review and world/gameplay acceptance pending.** Commissioned under the
[production commission](commission.md) and current per-asset common brief, superseding
the earlier concept-only restriction in [traffic fixtures](../city_traffic_fixtures.md).
No shared brief, queue, progress record, district or traffic logic changed.

Original author / technical integrator: commissioned implementation specialist, lane
`a-traffic`. Acceptance owner: supervising production lead and independent reviewer.
No live Blender/Godot editor session was accessed. The current brief prohibits live MCP
and windowed editor use, so text-authored wrappers were loaded, packed, saved and reopened
in isolated pinned headless Godot. This does not synchronize a separate open editor.

## Design and dimensions

A chunky three-lens municipal signal head: rounded petrol housing, restrained face rim,
recessed red/amber/green lenses, three thick upper sun visors, plain rear cover and a
small top mounting boss. Neutral metal values match the [signal pole](city_traffic_fixtures_01.md)
and accepted street-light family. No artwork, brands, luminous border or large backing
sign competes with district landmarks. The original geometry is constructed in Blender;
no downloads, image-to-mesh, third-party models or runtime-generated render meshes.

The [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) inform its quiet
shared-fixture role, not inferred measurements. Candidate use across the nine districts
remains unconfirmed; this does not add signals to Signal Row's starting set or every junction.

**Dimensions are provisional production choices**, fitted to the existing sibling contract:

- Head Godot X/Y/Z envelope: **0.500 × 1.320 × 0.540 m**.
- Head local AABB: minimum `(-0.250,-1.320,-0.380)`, maximum `(0.250,0,0.160)` m.
- Housing: 0.440 m wide, 1.240 m high, 0.320 m deep; rounded edges.
- Face frame: 0.500 m wide. Lens diameter 0.268 m; lens centres descend 0.320,
  0.700 and 1.080 m from the attachment. Upper visor outer radius 0.177 m.
- Top mounting boss maximum diameter 0.240 m, height 0.100 m; its bevel leaves a
  **0.228 m diameter flat contact disk** at the attachment plane.
- Root and mesh pivots: `(0,0,0)`, **top-centred attachment**, not ground-contact.
  All geometry descends below this plane. Blender +Y front maps to Godot -Z;
  Blender +Z maps to Godot +Y. Metre units; applied rotations and unit scales.
- Envelope/contact tolerance ±0.001 m; source-to-export bounds tolerance 0.00001 m.

### Mount and road-tool interface

The unchanged `.01` pole owns the attachment. Its source empty
`Visuals/Model/CityTrafficFixtures01/socket_signal_head` and public adapter
`Sockets/SignalHead` are identity-oriented at Godot `(0,4.200,-1.400)`.
Place the head root at that transform with no corrective rotation or scale.
Its flat top disk contacts the collar underside at 4.200 m; the measured head bottom
is **2.880 m above ground**, strictly above the 2.500 m overhead-only threshold.
The boss is contained within the carrier's 0.240 m diameter underside.

`city_traffic_fixtures_02_mounted.tscn` is a saved convenience composition of the unchanged
pole and head prefabs. It has a ground-centred root; `Head` is saved at the carrier datum.
The checker compares that placement against both the actual imported source marker and
public adapter, so a future sibling socket change cannot silently drift. No pole mesh is
copied into the head source/export, and no sibling file is changed.

Mounted combined visual bounds are approximately `(-.250,0,-1.780)` to
`(.250,4.540,.220)` m. Road-tool placement may rotate the assembly about +Y; local -Z
is the signal-facing direction. Reserve the full overhang and validate car, route,
aim and pedestrian clearances at actual placements. No placement algorithm or traffic
priority policy is added.

## Source, exports and materials

- Source: `art/source/models/environment/city_traffic_fixtures_02/city_traffic_fixtures_02.blend`.
- Collection: `export_city_traffic_fixtures_02`.
- Root / mesh: `CityTrafficFixtures02` / `CityTrafficFixtures02_Mesh`.
- Export: `art/models/environment/city_traffic_fixtures_02/city_traffic_fixtures_02.glb`
  and pinned engine `.glb.import`.
- Prefabs: `scenes/prefabs/environment/city_traffic_fixtures_02.tscn` and
  `city_traffic_fixtures_02_mounted.tscn`.
- Reproduction, validation and packaging tools: `tools/asset_production/city_traffic_fixtures_02/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export reads
`tools/assets/blender/export_settings.json` with the named collection and explicit static
animation/skin exclusions. Studio floor, cameras and lights never export. The source is
saved before rendering; the overhead render then appends the unchanged sibling pole only
for context, without saving it into this source or export. Source re-export needs no sibling.
Rebuilding the contextual overhead evidence requires the committed `.01` source.

All modifiers are applied before source save. Each manufactured component is closed;
intentional concealed intersections between the housing, face, boss, visors and lens
parts are not an engineering union. Reported volume sums closed component volumes.
No texture maps, embedded images, external material resources, rig, animation, destruction
states or light nodes. Flat material colors need no authored UV layout. Default Godot mesh
LOD generation and shadow meshes remain enabled; no custom LOD or ratified budget is claimed.

Six stable opaque Principled slots in order (base RGB values are linear):

| Slot | Base RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `traffic_dark_metal` | .025, .075, .090 | .45 | .46 |
| `traffic_fixture_rim` | .070, .130, .150 | .50 | .42 |
| `traffic_service_recess` | .012, .025, .030 | .25 | .50 |
| `signal_red_unlit` | .250, .022, .018 | .05 | .30 |
| `signal_amber_unlit` | .340, .170, .018 | .05 | .30 |
| `signal_green_unlit` | .018, .200, .065 | .05 | .30 |

**Static intact, unlit appearance only.** All three colored lens materials have zero
emission. Their color identifies the physical lenses, not three simultaneously active
traffic states. There is no phase API, timer, animation, authoritative signal rule or
runtime material writer. Any later operational signal system needs its own approved
state/presentation contract; separate lens slots do not implement or promise that system.

## Prefabs and collision

The head wrapper has an identity-transform linked imported instance at `Visuals/Model`,
with identity imported root and mesh, no editable imported children, no copied mesh data
and no material overrides. The mounted wrapper instances the two unchanged wrappers.

The head is **visual-only mounted hardware**, not a freestanding ground prop; it must not
be placed as an obstacle on the ground. At its supported mount every part is above 2.5 m.
The mounted composition retains exactly the pole's existing static cylinder and adds no
collider: radius .220 m, height 4.130 m, centre `(0,2.065,0)`, layer 1 / mask 0.
Decoration does not inflate the carrier's blocking envelope. No collision/lifecycle
state transition or new interaction is introduced.

## Evidence and reproduction

[Hero](city_traffic_fixtures_02-evidence/hero.png),
[side](city_traffic_fixtures_02-evidence/side.png),
[lens/visor detail](city_traffic_fixtures_02-evidence/detail.png),
[47 m / 42° mounted overhead](city_traffic_fixtures_02-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders at **1280×720**, 32 samples, AgX,
PNG compression 100, compacted to 7 significant RGB bits/channel. The later lean-evidence
limit supersedes the historical 1280×800 requirement. Overhead is vertical-down perspective
at 47 m, 42° vertical FOV, north/Blender +Y at image top, with the head at its actual mount.

Self-review inspected all four images. Hero and detail show broad lenses, rounded housing
and closed thick visors; side shows the restrained projection. The overhead silhouette is
a small quiet fixture at the end of the pole. **Individual front-facing lenses cannot be
read from straight overhead**; no signal-state communication from that camera is claimed.
Do not enlarge it into a landmark sign to compensate. Initial overhead studio lighting was
rebalanced for the mounted height; final evidence is retained, scratch renders are not.
These are not engine lighting or populated-city readability captures.

From repository root in Git Bash:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
N=city_traffic_fixtures_02
T="C:/tmp/ft/assets/$N"
mkdir -p "$T"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/author.py" > "$T/author.log" 2>&1
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/validate.py" > "$T/validate.log" 2>&1
# validate.py opens the saved source and fresh-exports into $T/reexport for strict comparison.
# Independent export from saved source, without rebuilding:
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background \
  --factory-startup "art/source/models/environment/$N/$N.blend" --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/export.py" -- "$T/reexport"
timeout 300 "$(mise which godot)" --headless --path . --import > "$T/import.log" 2>&1
timeout 180 "$(mise which godot)" --headless --path . \
  --script "res://tools/asset_production/$N/check.gd" -- --normalize > "$T/godot-check.log" 2>&1
timeout 30 "$(mise which gdstyle)" fmt --check "tools/asset_production/$N/check.gd"
timeout 30 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$N/check.gd"
# The output directory must not contain a previous check run.
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python "tools/asset_production/$N/finalize.py"
timeout 300 "$(mise which godot)" --headless --path . --import > "$T/final-import.log" 2>&1
python "tools/asset_production/$N/finalize.py"
```

`validation.json` records measured source/export/engine results and production-check summary.
`manifest.json` SHA-256 hashes every delivered file except itself. The four compressed
renders and one concise `final.log` are retained; raw logs, retries, intermediate exports
and the production-check mirror stay in scratch outside the checkout.

## Validation results

- **6,120 triangles; 3,088 source vertices; 2,892 source faces; 3,651 exported vertices;
  one mesh; six material surfaces.**
- Zero degenerate source faces/export triangles; zero non-manifold edges; positive
  summed closed-component volume. Maximum normal length error: source `1.59e-7`, export `1.14e-7`.
- Actual GLB/source bounds agree; applied transforms, top pivot, flat contact ring and axes pass.
- Fresh saved-source export is **byte-identical** to the 154,008-byte GLB;
  SHA-256 `4a0911819e2f1b98bcaff39461fdc1c45a53c7a67cc9a6c34b7d16b7f6070ea4`.
- Pinned Godot import/load, linked ancestry, five dependency/scene UIDs, actual material order,
  zero emission, backface culling, opaque surfaces and absence of head lights/collision pass.
- Both saved wrappers preserve bytes/UIDs across save/reload and a fresh import.
- Actual mounted minimum height `2.879999876` m; head matches source socket and public adapter.
- Low ray hits the retained pole collider; ray through the overhead head is clear.
  This is bounded query evidence, not actor/car movement or multiplayer transport validation.
- Pinned gdstyle formatting/lint and production script compilation pass.
- Full production checks **pass**: 17 Python tests, 149 GUT tests, 6,768 assertions,
  isolated import, and expected failing diagnostic sentinel. No known failures waived.

Initial style check flagged formatting and a 12-local-variable function; physics query checks
were split into a named helper and the final script is clean. Initial repeated normalization
exposed stale importer UID cache data for newly saved scenes. The owned normalizer now preserves
the saved header UID before consulting/registering cache state; a fresh import and hash check
confirmed both scenes unchanged. No previously accepted identity or sibling file was altered.
A packaging-script retry corrected Windows text encoding and escaped newlines before producing
the manifest; all four owned Python entry points now pass explicit AST parsing and the final
packager runs successfully. Blender prints the pinned `use_nodes` API deprecation notices.
Project import emits the existing MCP 4.8-versus-tested-4.7 warning; final load checks contain
no missing-resource, script or leak errors. No owner's live MCP connection was contacted.

## Remaining acceptance

Independent technical/art review is required. Dimensions and mounting are provisional; no
whole-city signal demand, phase behavior or district placement is accepted. Actual engine
visual review, populated gameplay-camera/aim occlusion, car swept clearance/impact, relevant
real separate-process transport/prediction, packaged builds and sustained Deck/GPU performance
remain **pending**. Pole movement checks belong to the sibling handoff and were not rerun or
represented as new movement evidence here. No shared tracker/TODO was marked complete.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
