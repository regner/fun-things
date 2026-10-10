# city_lights.03 — Yard pole

10 October 2026. **Source/export and bounded headless prefab handoff complete;
independent review and full placement/gameplay acceptance pending.**
Commission: [production commission](commission.md), continued by the per-asset
production task. Family: [city_lights](../city_lights.md). The commission supersedes
the earlier concept-only restriction, not the family's readability constraints.
Original author and technical integrator: commissioned Codex implementation specialist.
Independent acceptance belongs to the production reviewer; no acceptance is inferred here.

## Design and dimensions

A taller tapered petrol mast with a flared cast shoe, quiet service hatch and a
short T crosshead carrying two broad, rounded downward-facing lamps. The twin
silhouette distinguishes working yards from the accepted single street pole and
short pedestrian fixture while retaining their palette and manufactured bevels.
It serves Broadlot parking, Ironreach repair courts and East Docks aprons;
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and the [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md)
remain placement context, not inferred dimensions or authored placements.

All dimensions below are **provisional authored values**, allowed by the current
production brief, not measured from concept art or approved clearance budgets.

| Feature | Metres |
| --- | --- |
| Whole visual width X / height Y / depth Z (Godot) | 2.900 / 8.400 / 1.440 |
| Visual AABB min → max (Godot) | (-1.450, 0, -1.160) → (1.450, 8.400, 0.280) |
| Ground shoe | Ø0.560; 0.420 high |
| Tapered mast | Ø0.340 lower; Ø0.180 upper; top 8.050 |
| Crosshead | 2.150 wide × 0.220 high × 0.220 deep |
| Each lower housing | 0.900 wide × 1.400 deep × 0.180 high |
| Lamp centre spacing | 2.000 |
| Each lens | 0.660 wide × 1.000 deep; lowest face Y=8.079 |
| Collision | One upright cylinder, radius 0.280, height 7.950 |

Envelope/ground tolerance is ±0.001 m; source-to-GLB axis-bound comparison tolerance
is 0.00001 m. Metre units; applied static transforms; root and mesh at identity.
The root is at the **ground-contact centre of the mast shoe**, not the centre of
its asymmetric lamp overhang. Blender +Y maps to Godot -Z (lamp forward), Blender
+Z to Godot +Y. No corrective rotation/scale is hidden in the prefab.

### Placement and mounting interface

Place the prefab root at the flat ground datum, rotate about Godot +Y to orient
the heads; Godot -Z points towards their forward overhang. The road tool may place
this linked fixture by that root/pivot without changing the road-surface owner.
No attachment sockets are required for a freestanding complete fixture. No separate
light emitters, light sockets or runtime placement scripts are introduced.

The single coarse mast collider follows the light-family cylinder convention:
`Collision/PoleBody/Shape`, centred at (0, 3.975, 0), static-world layer 1/mask 0.
It intentionally encloses the shoe and tapered mast with no hatch snag points.
The crosshead/lamps are overhead decoration, not walkable or solid beams; no
interior, breakable, animation or interaction state is invented. Keep the 2.9 m
wide overhead silhouette out of key actor sightlines and put shoes outside vehicle
turns, foot bypasses, crossings and parking exits. No yard spacing is accepted here.

## Source, exports and materials

- Source: `art/source/models/environment/city_lights_03/city_lights_03.blend`.
- Named collection: `export_city_lights_03`; root `CityLights03`, mesh `CityLights03_Mesh`.
- Explicit GLBs in `art/models/environment/city_lights_03/`:
  `city_lights_03_warm.glb` and `city_lights_03_cool.glb`, with pinned `.import` metadata.
- Prefabs: `scenes/prefabs/environment/city_lights_03.tscn` (warm) and
  `city_lights_03_cool.tscn`. Each has an identity-transform linked imported instance
  at `Visuals/Model`; collision is separate. No embedded/rebuilt render meshes.
- Parametric construction, export, validation, saved collision test and evidence
  finalizer: `tools/asset_production/city_lights_03/`.

Original Blender construction only: no downloads, real brands, purchased assets,
image-to-mesh, generated runtime meshes or prototype dependencies. Closed component
solids intersect at assembly joints intentionally; this is not a single Boolean union.
The two appearances share identical geometry and three hardware materials. Four
surfaces, in order: `pole_petrol`, `fixture_rim`, `service_recess`, `lens_warm` or
`lens_cool`. Opaque back-culled Principled materials; no textures or embedded images.
Petrol linear RGB (0.025, 0.075, 0.090), metallic 0.45, roughness 0.46 matches the
street pole. Warm lens RGB (0.95, 0.69, 0.32), cool (0.46, 0.78, 0.92), roughness 0.32,
emission strength 0.45. These values only affect appearance; **no real light nodes**
or illumination radius are delivered. Full exported PBR parameters are in validation.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**; shared
`tools/assets/blender/export_settings.json`, explicit named collection filter,
Y-up conversion, normals/UVs, no cameras/lights, no skins/animations/morphs. All
bevels are applied before source save. Studio camera, floor and softboxes are outside
the export collection. Automatic Godot import LOD defaults are retained; explicit
LODs/rigs/animation/textures are not needed for this static low-complexity fixture.
No repeated-placement performance budget has been measured.

## Evidence and reproduction

- [Hero](city_lights_03-evidence/hero.png)
- [Side](city_lights_03-evidence/side.png)
- [Underside/crosshead detail](city_lights_03-evidence/detail.png)
- [47 m / 42° overhead](city_lights_03-evidence/overhead_47m_42deg.png)
- [Numerical validation](city_lights_03-evidence/validation.json)
- [SHA-256 producer manifest](city_lights_03-evidence/manifest.json)
- [Concise execution record](city_lights_03-evidence/final.log)

All four renders were inspected by the producer. An initial underside support
covered part of each lens; the final rear-entry arm ends before the lens face.
The corrected detail shows both unobstructed broad lenses. The overhead view
retains a recognisable quiet twin-head silhouette with a large clear gap between
heads; emission faces point down, avoiding a pair of bright overhead beacons.
The true side view naturally overlaps the two parallel lamps. No staged comparison
actors or population were rendered, and these are **Blender evidence, not engine
camera or actor-occlusion acceptance**.

All PNGs are 1280×720, compressed at PNG level 9 after RGB 7-bit-channel posterization
for lean retention. The camera is vertical-down perspective, north-up, 47 m high,
42° vertical FOV. This uses the production brief's 720 px evidence-height limit,
not the older example's 1280×800 dimensions. Hero/detail use studio orthographic
cameras; isolated studio light pools are not this fixture's real illumination.

Run from the repository root (Git Bash on the commissioning machine):

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
ASSET=city_lights_03
SCRATCH=C:/tmp/ft/assets/$ASSET
mkdir -p "$SCRATCH"

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/$ASSET/author.py
# Opens saved source, verifies actual GLB accessors and fresh-exports to scratch.
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/$ASSET/validate.py
# Optional independent export of the saved named collection:
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 art/source/models/environment/$ASSET/$ASSET.blend \
  --python tools/asset_production/$ASSET/export.py -- "$SCRATCH/manual-reexport"

timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/$ASSET/check.gd -- --normalize
timeout 60 mise exec -- gdstyle fmt --check tools/asset_production/$ASSET/check.gd
timeout 60 mise exec -- gdstyle --max-line-length 100 --max-warnings 0 \
  tools/asset_production/$ASSET/check.gd
# The output folder must be fresh; archive earlier scratch checks before rerunning.
timeout 1800 python tools/production_checks.py --godot "$GODOT" \
  --gdstyle "$(mise which gdstyle)" --output "$SCRATCH/checks"
python tools/asset_production/$ASSET/finalize.py
# Import the compacted PNGs; retain any normalized sidecars, then refresh hashes.
timeout 300 "$GODOT" --headless --path . --import
python tools/asset_production/$ASSET/finalize.py
```

The exporter can be called independently as shown; validation performs that same
export from the saved source and compares complete GLB bytes. No live Blender or
Godot editor session was used. The prescribed text-authoring/headless pack-save
fallback normalized new scene UIDs and node IDs; headless import does not establish
synchronization with any separately open editor.

## Validation results

- **1,852 source vertices; 3,640 triangles; one mesh; four surfaces.**
- **2,092 exported vertices** per appearance (normal/UV splits), 3,640 triangles.
  Warm GLB 92,920 bytes; cool 92,924 bytes.
- **Zero degenerate source faces, zero degenerate source/export triangles,
  zero non-manifold source edges; unit-length source corner and GLB normals.**
- Bounds, ground datum, collection membership, no unintended nodes/dependencies,
  opaque/culling material flags and identity transforms pass.
- Both fresh exports from the committed source are **byte-identical** to delivery.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports both GLBs. Both saved wrappers
  load with all dependencies/UIDs resolved, correct bounds/materials and one collider.
  Repeated pack/save/reload is byte-stable, including separate process checks.
  The normalizer explicitly preserves header UIDs when a new headless cache lacks
  their registration; it does not generate replacement saved identities on rerun.
- Production `ActorMotion.step` checks use a saved radius **0.35 m**, height **1.8 m**
  capsule and collision-only floor. Across 48 ticks each, AUTHORITY and REPLAY stop
  identically at Z **-0.630208 m** on the mast; the X=0.95 m bypass reaches Z
  **2.000001 m**. Low ray hits the correct pole body; Y=8.2 m ray passes clear of
  the mast collider. This is local simulation equivalence, **not network transport**.
- Canonical checks: all **180** owned GDScripts explicitly compile; formatting/lint
  pass. **16/16 Python tests**, **149/149 GUT tests**, **6,768 assertions** pass;
  negative GUT control is correctly detected. The **overall command exits 1** solely
  because the cold compiler-mirror import exceeded the shared tool's internal
  30-second deadline. Subsequent GUT import passes. This limitation is retained,
  not ignored as a known fixture failure or presented as an overall pass.

The first canonical invocation resolved PATH's `.gdvm` wrapper, which returned no
version stdout and emitted non-cp1252 stderr, failing pin discovery. The bounded
rerun explicitly passed `mise which godot` and `mise which gdstyle`. Blender emits
its upstream `use_nodes` deprecation notices; the import plugin emits its known
Godot-4.8/latest-tested-4.7 warning. Final asset-specific checks have no script or
resource errors. Raw scratch diagnostics remain under `C:/tmp/ft/assets/city_lights_03/`,
not in the committed asset. No shared scripts, project settings, queue or progress
files were changed to mask these limitations.

## Remaining acceptance

Independent technical/art review; real engine gameplay-camera and populated-yard
occlusion; accepted world/road-tool placement; car driving/turning contacts; actual
separate-process multiplayer transport/prediction; exported-build/Deck and repeated
fixture performance remain pending. Real lights, shadow counts, illumination and
emission calibration require the lighting/performance owner. This handoff does not
mark the register ready, place yard poles, close shared TODOs or approve dimensions
for final traffic layouts.
