# d03_laundry_frames.01 — Short frame

10 October 2026. **Source/export and bounded prefab checks delivered; independent review
and world acceptance pending.** Production commissioned under [commission](commission.md)
and the current per-asset execution brief; the earlier concept-only restriction is
superseded by that commission. Family: [communal laundry frames](../d03_laundry_frames.md).

Producing owner: commissioned implementation specialist (worker), responsible for original
Blender construction, export, prefab, tests and self-review. Accepting owners: independent
art/technical reviewer and the world/gameplay integrator; no acceptance is inferred.
Direction follows [Terrace Ward](../../concepts/districts-v1/terrace-ward.md), its
[asset breakdown](../../concepts/districts-v1/terrace-ward-assets.md), approved district
identities and Petrol & Coral. No other family deliveries preceded this asset in this lane.

## Design and dimensions

Two simple muted-teal metal T posts, dark foot sleeves and end caps, and three pale taut
laundry lines. Soft manufactured edges and broad proportions provide domestic character
without fine bolts, grime, simulated cloth or bright signage. The empty carrier is the
requested frame, not a duplicate of the separately registered hanging-cloth design.
All geometry is original Blender construction, with no downloaded meshes, textures,
brands or runtime-generated render geometry.

Dimensions are **provisional authored values**, permitted by the standing production
brief, not measurements inferred from the concept raster. Godot local X/Y/Z, metres:

| Item | Dimensions / position |
| --- | --- |
| Whole visual AABB | min (-1.950, 0, -0.660), max (1.950, 2.240, 0.660) |
| Whole size, width / height / depth | 3.900 × 2.240 × 1.320 |
| Post centres | X = -1.800 and +1.800, Z = 0 |
| Upright section | 0.140 × 0.140; from Y=0.040 to 2.160 |
| Ground shoes | 0.300 × 0.080 × 0.300; bottom Y=0 |
| Main crossarms | 0.180 × 0.160 × 1.300; centre Y=2.160 |
| Lines | 3.600 long, radius 0.014; centre Y=2.180 |
| Line positions | Z = -0.480, 0, +0.480; parallel to X |
| Pivot | Ground centre between the two shoes, (0,0,0) |

Numeric tolerances: envelope/ground ±0.001 m; source-to-GLB axis mapping ±0.00001 m.
Blender +Z maps to Godot +Y; Blender +Y maps to Godot -Z. Source root and mesh have
zero translation/rotation and unit scale. No corrective prefab transforms.

### Cloth attachment interface

For static cloth dressing, use a top attachment datum at Godot Y=2.180 on one of the
three listed Z axes. The line radius is 0.014 m; usable cloth span is X=-1.600..+1.600,
leaving end sockets clear. A cloth top-centre pivot can be translated along this span;
its hanging direction is -Y and its broad face runs along X. These documented coordinates
are the carrier contract, not runtime sockets or a cloth simulation API. Keep broad
cloth silhouettes restrained and court-edge placements away from movement mouths.
The frame adds no interaction, rig, animation, destruction state or laundry mechanic.

## Source, export and materials

- Source: `art/source/models/environment/d03_laundry_frames_01/d03_laundry_frames_01.blend`.
- Collection: `export_d03_laundry_frames_01`.
- Root / mesh: `D03LaundryFrames01` / `D03LaundryFrames01_Mesh`.
- Export: `art/models/environment/d03_laundry_frames_01/d03_laundry_frames_01.glb`
  plus its engine-normalized `.import`.
- Prefab: `scenes/prefabs/environment/d03_laundry_frames_01.tscn`.
- Reproduction and tests: `tools/asset_production/d03_laundry_frames_01/`.

One joined static mesh with three stable surface slots, in this order:

| Slot | Principled material | sRGB swatch | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `laundry_muted_teal_metal` | `#476D70` | 0.35 | 0.50 |
| 1 | `laundry_dark_fittings` | `#29474C` | 0.40 | 0.48 |
| 2 | `laundry_pale_line` | `#BBC4B6` | 0.10 | 0.68 |

Opaque, backface-culled, flat-color materials; no textures, embedded images or external
material dependency. The author converts sRGB swatches to linear Principled inputs.
Static modifiers are applied, weighted corner normals retained. Joined subparts are
closed intersecting manufactured components, not a boolean union. Studio plane,
one-metre reference, camera and lights stay outside the export collection.

Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**.
`export.py` uses `tools/assets/blender/export_settings.json`, the named collection,
Y-up conversion, normals/UV export, no cameras/lights, and disables skins/animations.
No explicit LOD is added; Godot's per-import automatic LOD default remains enabled.
Repeated-placement performance is unmeasured; no polygon or device budget is claimed.

## Prefab and collision

`Visuals/Model` is the identity-transform imported scene instance. No imported child
edits, copied vertex data or runtime-authored composition. A separate
`Collision/FrameBody` is one static-world body, layer 1 / mask 0, with three simple boxes:

| Shape | Centre X/Y/Z | Size X/Y/Z |
| --- | --- | --- |
| WestPost | (-1.800, 1.040, 0) | (0.300, 2.080, 0.300) |
| EastPost | (+1.800, 1.040, 0) | (0.300, 2.080, 0.300) |
| TopEnvelope | (0, 2.160, 0) | (3.784, 0.160, 1.320) |

Post boxes deliberately use the foot-shoe width continuously rather than snag-prone
stepped collision (at most 0.080 m margin from an upright face). The thin top box
simplifies both crossarms and the space between their taut lines. It is **not** a
solid wall/deck through the frame: the under-frame region is open with 2.080 m headroom
and 3.300 m between post envelopes. Upper aim/vehicle queries intentionally see that
simple top envelope, not individual line strands. It has no walkable-platform contract.
The 1.8 m actor can pass below it; this does not authorize placing laundry in a route.

Saved collision-only `check_scene.tscn` under the owned tool directory instances this
prefab, a flat test floor and the production `ActorMotion` capsule. No new visible test
geometry is generated. Both scenes pass two byte-identical load/pack/save cycles,
with their UIDs retained through `ResourceSaver.set_uid`. The GDScript `.uid` is committed;
scene UIDs are embedded in the TSCNs (Godot produces no scene `.uid` sidecars).

## Evidence and checks

[Hero](d03_laundry_frames_01-evidence/hero.png),
[end-on side](d03_laundry_frames_01-evidence/side.png),
[crossarm detail](d03_laundry_frames_01-evidence/detail.png),
[47 m / 42° overhead](d03_laundry_frames_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders, 32 samples, AgX, 1280×720,
PNG compression 95, no dithering. The overhead is vertical-down perspective,
north-up, 42° **vertical** FOV at 47 m; the later brief's 720-pixel height cap
supersedes the older 800-pixel evidence requirement.

Producer inspected all four final renders. The T profile and three pale lines are clear
at detail scale; overhead they form a quiet approximately 80×28-pixel footprint, with
slender lines intentionally subordinate to actors and later broad cloth. No dense
clutter or neon accents. End-on side is intentionally aligned with both posts.
Self-review corrected a clipped side framing and coplanar end-cap artifacts before
final export; no earlier render or backup source is retained in production paths.
These are not Godot gameplay captures or independent art acceptance.

Final [validation.json](d03_laundry_frames_01-evidence/validation.json):

- **2,652 triangles; 1,368 source vertices; 1,834 exported vertices; one mesh; three surfaces.**
- Zero source degenerate faces, zero non-manifold edges, zero degenerate GLB triangles.
  Source corner and actual exported binary normals are unit length within 0.0001.
- Literal envelope, ground, identity transforms and all 72 line vertices satisfy the
  documented mounting axes and radii. GLB bounds are independently decoded from buffers.
- Fresh saved-source re-export is byte-identical to the committed GLB.
- Headless import and final dependency/load/normalization checks exit 0 with no
  `ERROR` or `SCRIPT ERROR` lines. Actual linked bounds/materials and UIDs resolve.
- Production `ActorMotion` authority and replay each execute 48 ticks in four cases.
  Both posts stop at Z≈-0.500 m; centre passage and X=2.500 m bypass reach Z≈2.000 m.
  Authority/replay results match; five post/top/headroom ray expectations pass.
- `gdstyle fmt --check` and lint with line length 100 / zero warnings pass.
- `production_checks.py` deliberately not run, per decision 52.

Final payload identities copied from the validation receipt:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `.blend` | 139959 | `eb35c17111db8dad7ff77a2ffd9391eaeb158b42a7eabefa24eb77cad2e967db` |
| `.glb` | 77804 | `50f472e2f589631f7561df009d89aca5efd183807fd0943710a7754a22989bc9` |

[manifest.json](d03_laundry_frames_01-evidence/manifest.json) covers every produced
payload including this document, tools, import metadata and final evidence; only the
manifest itself is excluded. [checks.log](d03_laundry_frames_01-evidence/checks.log)
retains a concise final check summary and historical diagnostic classification.
An initial editor-mode normalization passed but emitted shutdown-only renderer/text RID
leak diagnostics. Final normalization uses the existing UID-preserving headless-runtime
pattern instead, and has clean logs. Initial lint found one overlong line, fixed before
final checks. No unrelated plugin or live editor was modified; scratch stays outside Git.

## Exact reproduction

Run from repository root in Git Bash; never use the owner's live Blender/Godot sessions.
The isolated CLI route is required by the execution brief; it does not synchronize any
separate open scene. Source authoring and direct TSCN composition were followed by the
pinned headless import and resource save/reload checks.

```sh
NID=d03_laundry_frames_01
TOOLS=tools/asset_production/$NID
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
mkdir -p C:/tmp/ft/assets/$NID

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/author.py"
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . --script "$TOOLS/check_prefab.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "$TOOLS/check_prefab.gd"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/validate.py"
"$GDSTYLE" fmt --check "$TOOLS/check_prefab.gd"
"$GDSTYLE" --max-line-length 100 --max-warnings 0 "$TOOLS/check_prefab.gd"
```

`validate.py` freshly opens the saved source and runs `export.py` into
`C:/tmp/ft/assets/d03_laundry_frames_01/reexport/`, then byte-compares. For a standalone export:

```sh
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  "art/source/models/environment/$NID/$NID.blend" --python-exit-code 1 \
  --python "$TOOLS/export.py" -- "C:/tmp/ft/assets/$NID/manual-reexport"
```

After any final modifications, repeat import/checks, update the handoff from the final
validation receipt and run `python "$TOOLS/record.py"` last to refresh payload hashes.

## Remaining acceptance

- Independent technical/art review at the committed candidate.
- World integrator: saved court-edge placement, movement-mouth and sightline clearance,
  final cloth dressing/occlusion review and actual gameplay-camera capture.
- Gameplay/network owners: actual car contact/turning, aim implications of the simplified
  upper envelope, and real separate-process multiplayer/transport/prediction checks.
  The bounded authority/replay fixture does not prove those systems.
- Build/performance owners: packaged import/LOD behavior, repeated-frame cost, sustained
  target-device performance and Deck readability.

No world scene, road topology, registry, shared brief or TODO was changed. This delivery
is an importable tested asset candidate, not whole-city placement or full game acceptance.
