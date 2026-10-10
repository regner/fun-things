# d09_cranes.02 — Smaller dock crane

10 October 2026. **Source/export and bounded headless prefab checks delivered;
independent review, world placement and full gameplay acceptance pending.**
Production commissioned by Regner under the current asset-common brief, superseding
the historic concept-only restrictions in [commission](commission.md) and the
[crane family brief](../d09_cranes.md). Original Blender author and technical
integrator: commissioned implementation specialist. Parent/reviewer owns acceptance;
world integration owns placement. No register, shared brief or world scene edits.

## Design and dimensions

A compact static pedestal jib crane, sharing the [larger sibling](d09_cranes_01.md)'s
amber/petrol/slate palette, rounded enclosed cab, roof visor, slew ring, rear weight,
restrained axle joints, two static hoist lines and J-hook. The shorter sealed pedestal,
shallower boom angle, **three-chord triangular boom** and four open structural bays
produce a lower, shorter silhouette; this is not a uniform scale or recolour of the
larger four-chord crane. At 13.518 m it is approximately 61.3% of its sibling's height.
Broad smooth highlights and sparse details follow Petrol & Coral and the liked
[East Docks revision 02](../../concepts/districts-v1/east-docks.md).

Original Blender construction only: no downloaded assets, image-to-mesh, real brands,
textures, rig, animation, crane controls, freight simulation, interiors, climbable
access, lights or destruction states. The family helper script and hook recipe are
reused read-only; no shared tooling or sibling output was modified.

All dimensions below are **provisional authored values**, not measurements inferred
from concept images. World layout and clearance acceptance remain open.

| Item | Metres / convention |
| --- | --- |
| Whole Godot X/Y/Z visual size | **4.400 × 13.517714 × 15.823863** |
| Godot AABB minimum | **(-2.200, 0, -11.813863)** |
| Godot AABB maximum | **(2.200, 13.517714, 4.010)** |
| Ground plinth | 4.400 × 0.650 × 4.400; centred at ground origin |
| Sealed pedestal | 2.600 × 5.000 × 2.600; bottom 0.650, top 5.650 |
| Amber slew ring | 3.900 diameter, height 5.950–6.350 |
| Main machinery house | 3.400 wide × 1.800 high × 3.500 long |
| Boom lower centreline | Blender (Y=1.000, Z=8.500) → (Y=11.000, Z=12.400) |
| Triangular boom section | 1.000 vertical depth; half-width tapers 0.750 → 0.450 |
| Hook/hoist | Fixed unloaded appearance; all suspended hardware above 5.500 m |
| Pivot | **(0,0,0)** ground centre of plinth, not asymmetric visual AABB centre |
| Forward | Blender +Y → Godot -Z; point the boom over water |
| Tolerance | Bounds/datum ±0.001 m; source/export mapping ±0.00001 m |

Keep every plinth corner on existing land, with the boom/hook over water and away
from important overhead actor/vehicle sightlines. Retain generous apron between
cranes; do not add a public boardwalk or landward promenade bypass through the working
quay. This delivery changes no shoreline, roads, district allocations or placements.

## Source, exports and materials

- Source: `art/source/models/environment/d09_cranes_02/d09_cranes_02.blend`.
- Collection: `export_d09_cranes_02`; root `D09Cranes02`, mesh `D09Cranes02_Mesh`.
  Editable joined closed component shells; `author.py` retains named manufacturing
  parts and parameterized construction. Root and mesh have identity transforms.
- Export: `art/models/environment/d09_cranes_02/d09_cranes_02.glb`, with pinned-engine
  `.import` sidecar. One mesh, five material surfaces, no images or external textures.
- Tools: `tools/asset_production/d09_cranes_02/{author,export,validate,finalize}.py`,
  `check.gd`/`.uid` and `check_scene.tscn` for the bounded asset-specific engine test.
- Prefab: `scenes/prefabs/environment/d09_cranes_02.tscn`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Metre units,
applied transforms/modifiers, ground pivot, Blender +Z → Godot +Y exactly once.
Export loads the shared `tools/assets/blender/export_settings.json`, filters the
named collection and disables animations/skins. No cameras, studio floor/lights,
sibling geometry, rig, clips or sockets are exported.

`author.py` imports the larger sibling's material/closed-shell/beam/cylinder/hook
helpers from `tools/asset_production/d09_cranes_01/author.py`; it does not run that
script's authoring entry point. Both assets retain the same five opaque, back-culled
Principled materials in the same exported order:

| Slot | Material | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `crane_support_petrol` | (0.025, 0.075, 0.090) | 0.45 / 0.46 |
| 1 | `crane_joint_slate` | (0.115, 0.165, 0.185) | 0.55 / 0.40 |
| 2 | `crane_working_amber` | (1.000, 0.527, 0.102) | 0.12 / 0.42 |
| 3 | `crane_cab_glazing` | (0.026, 0.130, 0.170) | 0.25 / 0.23 |
| 4 | `crane_safety_ivory` | (0.920, 0.880, 0.710) | 0.05 / 0.48 |

Glazing is intentionally opaque with no interior/transparency dependency. No external
material remaps or artwork. Import retains automatic LOD generation, shadow meshes
and default compression. No bespoke LOD or measured platform budget is claimed.

## Prefab and collision

Saved `Visuals/Model` is an identity-transform imported instance, not embedded mesh
data or a corrective scale. Separate `Collision/PedestalBody` is one StaticBody3D on
world layer 1 / mask 0 with a minimal two-box compound:

- `Plinth`: size (4.400, 0.650, 4.400), centre (0, 0.325, 0).
- `Pedestal`: size (2.700, 5.000, 2.700), centre (0, 3.150, 0).

The pedestal envelope includes its lower collar, with a 0.05 m conservative margin
around the narrower support walls. Service-door trim and anchor heads do not add
snag colliders. The plinth is continuously solid; there is no gantry opening, stair,
walkway, deck access or implied interior. Above-head ring, machinery, boom, stays and
hook remain visual-only. No runtime hierarchy builder or gameplay code was added.

The requested production workflow prohibits live MCP/editor sessions and the windowed
editor is unavailable. Therefore this prefab was authored as text, then loaded,
packed, saved and reloaded by the pinned headless engine. Two save/reload passes are
byte-stable, with registered model/scene/script UIDs and saved node identities.
This proves saved-state resource integrity, **not** synchronization with an owner's
separate open editor or a windowed visual review. No live sessions were touched.

## Evidence and validation

[Hero](d09_cranes_02-evidence/hero.png) · [Side](d09_cranes_02-evidence/side.png) ·
[Cab/boom-heel detail](d09_cranes_02-evidence/detail.png) ·
[47 m / 42° unequal-pair overhead](d09_cranes_02-evidence/overhead_47m_42deg.png)

All four are isolated Blender Cycles CPU renders: 32 samples, AgX, 1280×720, PNG
compression 9 with six significant RGB bits/channel. They are not Godot captures.
The standing 1280×720 maximum supersedes the earlier 1280×800 example. Each PNG is
under 334 KB. Producer inspected all four final views, including the compacted files:
rounded masses and static hoist remain legible in hero/side, cab panes/visor separate
in detail, and open triangular boom gaps survive in the overhead.

### Family camera comparison

The overhead places the **unchanged larger source on the left** at Blender (-12,0,0)
and this smaller crane on the right at (12,0,0), both unit scale and zero rotation.
Camera is vertical-down at (0,6.7,47), 42° vertical FOV, fixed north-up yaw. Their
base centres are 24 m apart, leaving **19 m of empty ground between plinths**. The
smaller crane reads distinctly lower/shorter while retaining family materials and
cab/mast language. Perspective naturally shows off-centre side faces and separates
the elevated hoist from its projected boom tip. Thin cables are secondary detail.

This is an **illustrative studio spacing**, not a district placement, measured land
fit, city-scale visibility or actor/target occlusion acceptance. The larger boom
approaches the frame top; both must remain away from important gameplay sightlines.
The sibling collection is appended only after the smaller source is saved/exported;
the pair is never saved into either production source or exported GLB. Read-only
reproduction dependency hashes are recorded separately in the manifest.

### Measured results

[validation.json](d09_cranes_02-evidence/validation.json) contains actual source and
binary GLB measurements, engine receipt, production checks and camera conditions.
[manifest.json](d09_cranes_02-evidence/manifest.json) hashes every produced payload
with SHA-256, excluding itself; scratch runs and raw logs remain outside the repo.

- **8,528 triangles; 4,408 source vertices; 5,882 exported vertices; one mesh,
  five surfaces.** Surface and normal seams explain the different vertex counts.
- **Zero degenerate faces/triangles and zero non-manifold edges.** Structural members
  are closed shells with intentional seated intersections, not a Boolean union.
- Unit-length source/export normals within 0.00001; maximum errors approximately
  1.56e-7 and 1.29e-7. Ground pivot, literal envelope, scope and axis conversion pass.
- **Fresh saved-source reexport is byte-identical** to the committed 244,456-byte GLB.
  SHA-256: `386c3dae850b6d6c1d1fee5c13c5720c74951d75ac5631afd2c1125c2ba19573`.
- Pinned Godot **4.8.dev7.official.c971f93e7** loads all prefab dependencies, matches
  visual bounds, five opaque back-culled surfaces and the two deliberate colliders.
- Actual `ActorMotion.step`, capsule radius 0.35 m / height 1.8 m, 120 ticks per case:
  both `AUTHORITY` and `REPLAY` stop at **(0, 0.001, -2.550779)** against the plinth;
  clear apron-side bypass ends **(3.000, 0.001, 4.000001)**. Contact remains outside
  the independent -2.550 m plane, within the allowed 0.030 m advancement gap.
  Base/tower rays hit the correct body; the 6 m-high overhead ray stays clear.
- Production checks pass every layer: owned GDScript formatting/lint/compilation,
  **17 Python tests**, **149 GUT tests / 6,768 assertions**, and expected-failure
  detection. No historical fixture exception was needed in this checkout.

Diagnostics are limited to the existing Blender `use_nodes` deprecation notices and
MCP addon's 4.8-versus-tested-4.7 import warning. Production checks use explicit pinned
tool paths and UTF-8, following the larger sibling's Windows shim workaround. No
unrelated project/plugin changes or diagnostic suppression were needed.

### Exact reproduction commands

From this worktree root in Bash; every engine call is bounded and isolated. Use a
fresh empty check output directory on rerun. Full authoring recreates the four views;
only the saved-source GLB reexport, not `.blend` serialization, has a byte contract.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TOOL=tools/asset_production/d09_cranes_02
SCRATCH=C:/tmp/ft/assets/d09_cranes_02

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOL/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOL/validate.py"
# validate.py opens the saved source, reexports to scratch and compares exact bytes.
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . --script "res://$TOOL/check.gd" -- --normalize
timeout 180 mise exec -- gdstyle "$TOOL/check.gd"
timeout 1800 env PYTHONUTF8=1 python tools/production_checks.py \
  --godot "$GODOT" --gdstyle "$(mise which gdstyle)" --output "$SCRATCH/checks"
python "$TOOL/finalize.py" --compress-renders
# Final pinned import before manifest and commit retains normalized own sidecars.
timeout 300 "$GODOT" --headless --path . --import
python "$TOOL/finalize.py" --checks "$SCRATCH/checks"
```

## Remaining acceptance

- Independent technical/art review; this delivery does not accept itself.
- Actual engine-camera appearance, whole-city pair readability, actor/target occlusion.
- All base corners on existing land, over-water booms and generous open apron in the
  saved district; no public boardwalk/bypass through the freight area.
- Actual car driving/turning and populated-city movement/query checks.
- Real multiplayer transport/admission/prediction; the authority/replay test is a
  bounded production-API physics test, not separate-process network evidence.
- Packaged-platform and Deck LCD/OLED review, repeated-placement GPU/frame time,
  shadows/LOD and sustained device performance. No platform budget was inferred.
