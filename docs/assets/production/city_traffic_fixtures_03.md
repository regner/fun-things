# city_traffic_fixtures.03 — Small road-sign support

10 October 2026. **Source/export, linked prefab and bounded headless checks delivered;
independent review and world/gameplay acceptance pending.** Commissioned under the
[production commission](commission.md) and current per-asset common brief, superseding
the historical concept-only restriction in [traffic fixtures](../city_traffic_fixtures.md).
No sibling, queue, shared brief, progress record, road tool or gameplay logic changed.

Original author / technical integrator: commissioned implementation specialist, lane
`a-traffic`. Acceptance owner: supervising production lead and independent reviewer.
The brief prohibits live MCP/windowed-editor access. The text-authored wrapper and test
fixture were loaded, packed, saved and reopened in isolated pinned headless Godot; this
does not synchronize a separate open editor. No owner's live editor session was accessed.

## Design and dimensions

A small single-post road-sign carrier: slim petrol upright, flared cast shoe, subdued
metal collar/cap, two rear clamp bands and bridges, and a thin rounded-square blank plate.
The two metal materials exactly match the [signal pole](city_traffic_fixtures_01.md) and
[signal head](city_traffic_fixtures_02.md). The plate has a restrained neutral face rather
than district copy, emissive edging or regulatory artwork. No sign meaning, traffic rule,
interaction, damage state or automatic junction requirement is introduced.

Original editable Blender construction; no downloaded geometry, image-to-mesh, real brands,
third-party meshes or runtime-generated render geometry. The
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md) and
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) inform its quiet shared
fixture role, not inferred measurements. Candidate use across all nine districts remains
unconfirmed; this does not add the asset to Signal Row's starting set.

This compact elevated square road plate is distinct from the existing broad civic wall
panel, low twin-post panel, noticeboard and three-finger wayfinding post. Those remain
unchanged and should be reused for their existing roles. Future artwork for this road
support must reuse this carrier and its face-only material slot, not duplicate its model.

**All dimensions are provisional authored production choices**, permitted by the current
standing rules, not ratified engineering or placement envelopes:

| Quantity | Metres / contract |
| --- | --- |
| Godot X/Y/Z visual size | **0.700 × 3.250 × 0.280** |
| Godot AABB | min `(-0.350,0,-0.140)`, max `(0.350,3.250,0.140)` |
| Ground shoe | Maximum diameter 0.280; top 0.190 |
| Upright | Diameter 0.130; bottom 0.120, top 3.200 |
| Post cap | Diameter 0.136; top 3.220 |
| Plate | 0.700 square, 0.055 deep; bottom 2.550, top 3.250 |
| Plate depth | Godot Z=-0.135…-0.080; front toward local -Z |
| Outer corner radius | 0.045, six segments per quarter |
| Rear clamp centres | Heights 2.700 and 3.100; bridges 0.200 × 0.090 × 0.100 |
| Artwork face | 0.680 square, radius 0.035; bottom 2.560, top 3.240 |
| Artwork plane | Godot Z=-0.135, with a 0.010 m bevel back to the outer plate edge |
| Safe artwork rectangle | 0.600 square, centred at Godot `(0,2.900,-0.135)` |
| Numeric tolerance | Envelope/ground ±0.001; source/export coordinate/UV ±0.00001 |

Root and mesh origins are identity at `(0,0,0)`, centred on the **ground-contact shoe**,
not at the plate centre. Metre units, applied rotation/scale, no negative scales. Blender
+Z maps to Godot +Y; Blender +Y front maps to Godot -Z. No corrective prefab transforms.

### Road-tool and artwork interface

Place the prefab root on the saved ground/sidewalk datum; rotate about +Y so local -Z faces
the intended road approach. The root itself is the placement anchor; no additional mounting
socket is needed for this self-contained support. Reserve its foot and measured overhead
plate envelope, keeping it away from route mouths, vehicle lanes and important aim lines.
Actual road-tool integration, setbacks and swept clearances remain downstream.

`Visuals/Model/CityTrafficFixtures03/CityTrafficFixtures03_Mesh` surface **2** is exclusively
`road_sign_face`. Surfaces 0/1 own all metal, including the back and bevel. Future artwork
may replace only surface 2; it must not use a whole-mesh material override. There is no
runtime material writer or new appearance API in this delivery.

UV0 `UVMap` spans the face 0–1 with rounded corners clipping the image. Use an opaque sRGB
square image, white material multiplier and clamp rather than repeat. Blender UV is
`U=(0.340-X)/0.680`, `V=(Z-2.560)/0.680`; exported glTF V=0 at the top. Viewed from the front,
screen right is local -X, matching the existing civic carriers. Decoded GLB UV landmarks
independently check upright, nonmirrored orientation. Source UV boundary tolerance is
1e-6; the default Godot mesh compression requires a two-step 16-bit UV tolerance
`2/65535 ≈ 0.00003052` (observed boundary excursion approximately -0.000015).
Artwork resolution, filtering, mip review, content and readable sign meaning belong to the
artwork handoff. There is no text or symbol in this blank hardware delivery.

## Source, export and materials

- Source: `art/source/models/environment/city_traffic_fixtures_03/city_traffic_fixtures_03.blend`.
- Collection: `export_city_traffic_fixtures_03`.
- Root / mesh: `CityTrafficFixtures03` / `CityTrafficFixtures03_Mesh`.
- Export: `art/models/environment/city_traffic_fixtures_03/city_traffic_fixtures_03.glb`
  and adjacent pinned-engine `.glb.import`.
- Linked prefab: `scenes/prefabs/environment/city_traffic_fixtures_03.tscn`.
- Parametric author, export, source/binary validator, Godot checker/fixture and packaging:
  `tools/asset_production/city_traffic_fixtures_03/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. The exporter loads
shared `tools/assets/blender/export_settings.json`, selects only the named collection and
disables static animation/skin export. Cameras, lighting and studio plane never export.
All geometry modifiers are applied before saving. Manufactured components are individually
closed, joined into one mesh, with intentional concealed intersections rather than an
engineering boolean union. Volume is the sum of closed components, not a union volume.

Three stable opaque backface-culled Principled slots (base RGB values are linear):

| Surface | Material | RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `traffic_dark_metal` | .025, .075, .090 | .45 | .46 |
| 1 | `traffic_fixture_rim` | .070, .130, .150 | .50 | .42 |
| 2 | `road_sign_face` | .620, .660, .640 | 0 | .52 |

No textures, embedded images, external material resources, emission, rig, animation,
destruction states or light nodes. Hardware uses uniform colors; only the plate has a
meaningful artwork UV interface. Godot default automatic LOD generation, compression and
shadow meshes remain enabled. No bespoke LOD or platform performance budget is claimed.

## Prefab and collision

`Visuals/Model` is an identity-transform linked imported instance with no copied render
mesh, editable imported children or runtime-authored hierarchy. Imported root and mesh
remain identity. Scene and node identities are embedded in the normalized `.tscn`; the
engine generates the check script's `.gd.uid`, not an additional `.tscn.uid` sidecar.

`Collision/PoleBody/Shape` is the only collider: cylinder radius **0.140 m**, height
**2.500 m**, centre `(0,1.250,0)`, static-world layer **1**, mask **0**. The constant shoe-width
envelope deliberately simplifies the narrower shaft and avoids decorative snag points.
Above 2.5 m, the shaft/cap/clamps/plate are visual-only under the standing overhead rule;
plate bottom 2.550 m clears that threshold. No false full-width box blocks below the plate.

The owned saved `check_scene.tscn` instances the linked support, collision-only floor and
production `ActorMotion` capsule (radius 0.35 m, height 1.8 m). This is an isolated validation
fixture, not city placement or a new visible asset. It exercises production `ActorMotion.step`
for contact and clear bypass in authority/replay modes. No movement rule was reimplemented.

## Evidence and reproduction

[Hero](city_traffic_fixtures_03-evidence/hero.png),
[side/rear](city_traffic_fixtures_03-evidence/side.png),
[clamp/plate detail](city_traffic_fixtures_03-evidence/detail.png),
[47 m / 42° overhead](city_traffic_fixtures_03-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles CPU renders at **1280×720**, 32 samples, AgX, PNG compression
100, compacted to seven significant RGB bits/channel. The later lean-evidence limit takes
precedence over historical 1280×800. Overhead is vertical-down perspective at 47 m, 42°
vertical FOV, north/Blender +Y at image top.

Self-review inspected all four views. Hero shows the slim post and clean small square;
side/detail expose two discrete clamps, rounded edges and plain metal backing. From straight
overhead the plate is a tiny quiet edge, intentionally not a landmark. **Front-face artwork
cannot communicate readable instructions at that camera angle.** No enlarged overhead sign,
UI cue or traffic behavior is invented to compensate. These are not engine lighting,
populated-city readability or final art acceptance captures.

From repository root in Git Bash:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
N=city_traffic_fixtures_03
T="C:/tmp/ft/assets/$N"
mkdir -p "$T"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/author.py" > "$T/author.log" 2>&1
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/validate.py" > "$T/validate.log" 2>&1
# validate.py opens the saved source and fresh-exports to $T/reexport for byte comparison.
# Independent saved-source export, without rebuilding:
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background \
  --factory-startup "art/source/models/environment/$N/$N.blend" --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/export.py" -- "$T/reexport"
timeout 300 "$(mise which godot)" --headless --path . --import > "$T/import.log" 2>&1
timeout 180 "$(mise which godot)" --headless --path . \
  --script "res://tools/asset_production/$N/check.gd" -- --normalize > "$T/godot-check.log" 2>&1
timeout 30 "$(mise which gdstyle)" fmt --check "tools/asset_production/$N/check.gd"
timeout 30 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$N/check.gd"
# Output must be a fresh empty directory; retain earlier raw runs in scratch only.
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks-final"
python "tools/asset_production/$N/finalize.py"
timeout 300 "$(mise which godot)" --headless --path . --import > "$T/final-import.log" 2>&1
python "tools/asset_production/$N/finalize.py"
```

`validation.json` contains source/export/engine results, check summary and render sizes.
`manifest.json` SHA-256 hashes every delivered file except itself. Four lean PNGs and one
concise `final.log` are retained; raw logs, retries and intermediate exports stay in scratch.

## Validation results

- **1,428 triangles; 732 source vertices; 578 source faces; 800 exported vertices;
  one mesh; three material surfaces.**
- Zero degenerate source faces/export triangles; zero non-manifold edges; positive summed
  closed-component volume. Maximum normal-length errors: source `1.69e-7`, export `1.08e-7`.
- Actual binary/source AABBs agree; ground datum, applied transforms, root/mesh pivots,
  face-only material, front normals and upright UV landmark checks pass.
- Fresh saved-source export is **byte-identical** to the **37,340-byte** GLB;
  SHA-256 `bc40bd426b79d6515b37e37738adfbc189ac75114135aee7116be65360f5958f`.
- Godot **4.8.dev7.official.c971f93e7** import/load, dependency UIDs, identity-linked ancestry,
  actual surfaces/face UVs, static collision filtering and save/reload byte stability pass.
- Low ray hits the post; ray through the overhead panel is clear.
- `ActorMotion.step`: 48 fixed ticks per case per mode; contact approximately
  `(0,.001,-.500000)` m; X=.8 bypass reaches approximately `(.8,.001,2.000001)` m.
  Authority/replay endpoints match. Independent contact expectation is -.49 m, tolerance
  .015 m for collision margin/tick behavior; bypass endpoint independently expects Z=2.
- Pinned gdstyle formatting/lint and production script compilation pass.
- Full production checks pass: **17 Python tests, 149 GUT tests, 6,768 assertions**,
  isolated import and expected failing diagnostic sentinel. No known failures waived.

Initial validation exposed weighted normals spilling from the bevel onto the artwork face;
source front-loop normals were corrected, source/export/renders regenerated, and validation
passed. Source float UV boundaries needed the stated 1e-6 tolerance. The added actual-engine
UV check then measured default compression's approximately -0.000015 boundary excursion;
its tolerance now accounts for two 16-bit quantization steps without disabling compression.
These are corrected source/validation findings, not hidden errors. Blender prints its pinned
`use_nodes` API deprecation notices. Import reports the existing MCP 4.8-versus-tested-4.7
compatibility warning; final load checks contain no missing-resource, script or leak errors.
The isolated process may start the project's configured plugin; no live MCP connection was
made and no unrelated process was stopped.

## Remaining acceptance

Independent technical/art review is required. Actual district placement, artwork/sign meaning,
engine visual review, populated gameplay-camera/aim occlusion, vehicle swept clearance/impact,
real separate-process transport/admission/prediction, packaged builds and sustained Deck/GPU
performance remain **pending**. Standalone authority/replay equality is not network transport
proof. The blank support is delivered, not accepted traffic signage or a completed world
placement. No shared tracker/TODO was marked complete.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
