# d09_cranes.01 — Larger dock crane

10 October 2026. **Source/export and bounded headless prefab checks delivered;
independent review, pair/placement and full gameplay acceptance pending.**
Production commissioned by Regner under the current asset-common brief, superseding
historic concept-only restrictions in [commission](commission.md) and the
[crane family brief](../d09_cranes.md). Original Blender author and technical
integrator: commissioned implementation specialist. Parent/reviewer owns acceptance;
world integration owns placement. No register/progress/shared-world edits.

## Design and dimensions

An original static pedestal jib crane: tall sealed petrol support, broad anchored
foot, amber slew ring and machinery house, asymmetric enclosed cab, rear weight,
open five-bay boom, A-frame, restrained axle joints, two hoist lines and a forged
J-hook. No rig, controls, freight simulation, interiors, access route, lighting nodes
or destruction states. The open boom preserves gaps rather than presenting a broad
solid roof over the apron. Rounded edges, broad windows and quiet dark machinery
follow Petrol & Coral and the liked [East Docks revision 02](../../concepts/districts-v1/east-docks.md).
No downloaded geometry, external artwork, real brands or image-to-mesh assets.

All dimensions are **provisional authored choices**, not measurements inferred from
the district concept. Family placement/clearance acceptance remains open.

| Item | Metres / convention |
| --- | --- |
| Whole Godot X/Y/Z visual size | **5.600 × 22.065357 × 22.044828** |
| Godot AABB minimum | **(-2.800, 0, -16.517328)** |
| Godot AABB maximum | **(2.800, 22.065357, 5.527500)** |
| Ground plinth | 5.600 × 0.800 × 5.600; centred at ground origin |
| Sealed pedestal | 3.200 × 8.600 × 3.200; bottom 0.800, top 9.400 |
| Slew ring | 5.000 diameter, height 9.850–10.350 |
| Main machinery house | 4.450 wide × 2.350 high × 4.650 long |
| Boom lower chord centreline | Blender (Y=1.250, Z=13.200) → (Y=15.500, Z=20.600) |
| Boom truss depth | 1.350 vertical; half-width tapers 0.840 → 0.540 |
| Hook/hoist | Fixed unloaded appearance; hook remains above 9.55 m |
| Pivot | Ground centre of plinth, **(0,0,0)**; not visual AABB centre |
| Forward | Blender +Y, exported Godot -Z: point the boom over water |
| Tolerances | Bounds/datum ±0.001 m; source-to-GLB bounds ±0.00001 m |

The plinth must remain entirely on existing land. Place the boom/hook over water,
not important overhead actor/vehicle sightlines. Retain a generous clear apron
between this asset and the later smaller crane, without inventing a public boardwalk
or landward promenade bypass. This asset does not change the shoreline, roads or
any saved district placement. Its size is well below the 47 m camera, but perspective
still enlarges the boom; actor-centred occlusion checks remain necessary.

### Family handoff

This is the first produced member; `d09_cranes.02` did not exist at authoring time.
The smaller member should retain the amber/petrol/slate palette, rounded cab/visor,
slew-ring, capped structural-member and static hook language, while changing its
silhouette and dimensions rather than being only a recolour. The author script's
material/box/beam/cylinder helpers are readable reusable construction recipes;
no new shared runtime system was introduced. No existing compatible crane hardware
was available to instance. Unequal-pair city-scale readability is **not yet tested**.

## Source, exports and materials

- Source: `art/source/models/environment/d09_cranes_01/d09_cranes_01.blend`.
- Named collection: `export_d09_cranes_01`; root `D09Cranes01`, mesh
  `D09Cranes01_Mesh`. Source is editable joined closed component shells;
  `author.py` retains parameterized construction and named manufacturing parts.
- Export: `art/models/environment/d09_cranes_01/d09_cranes_01.glb`, with its
  pinned-engine `.import` sidecar. Studio geometry, camera and lights never export.
- Tools: `tools/asset_production/d09_cranes_01/{author,export,validate,finalize}.py`
  and `check.gd`/`check_scene.tscn` for the asset-specific engine test.
- Prefab: `scenes/prefabs/environment/d09_cranes_01.tscn`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Export loads
`tools/assets/blender/export_settings.json`, filters the named collection and disables
animation/skins. Root and mesh have zero translation/rotation and unit scale;
metre units, applied modifiers/transforms, Blender +Z → Godot +Y exactly once.
No cameras, lights, rigs, clips, sockets, textures or embedded images in the GLB.

Five opaque, back-culled Principled material slots, in exported order:

| Slot | Name | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `crane_support_petrol` | (0.025, 0.075, 0.090) | 0.45 / 0.46 |
| 1 | `crane_joint_slate` | (0.115, 0.165, 0.185) | 0.55 / 0.40 |
| 2 | `crane_working_amber` | (1.000, 0.527, 0.102) | 0.12 / 0.42 |
| 3 | `crane_cab_glazing` | (0.026, 0.130, 0.170) | 0.25 / 0.23 |
| 4 | `crane_safety_ivory` | (0.920, 0.880, 0.710) | 0.05 / 0.48 |

Glazing is intentionally opaque: no interior or transparency/overdraw dependency.
No external material remaps or artwork. Godot import keeps automatic LOD generation,
shadow meshes and default compression; no bespoke LOD tuning or measured budget claim.

## Prefab and collision

Saved `Visuals/Model` is an identity-transform imported instance. No copied render
mesh, runtime-built hierarchy or visual corrective scale. One separate static body,
`Collision/PedestalBody`, uses world layer 1 / mask 0 and two simple boxes:

- `Plinth`: size (5.600, 0.800, 5.600), centre (0, 0.400, 0).
- `Pedestal`: size (3.340, 8.600, 3.340), centre (0, 5.100, 0).

The second envelope includes the lower collar and makes a conservative 0.07 m margin
around the narrower support walls. Tiny anchors/service-door trim are decoration,
not separate snag colliders. The plinth has a continuous solid top. There is no
open gantry passage, stair, platform access or implied climbable machinery deck.
Slew ring, cab, boom, stays and hook are above-head decoration and collision-free.

Headless load/pack/save/reload passed twice with stable bytes and registered scene,
model and script UIDs; scene node identities are retained. No live Blender or Godot
session was used. The mandated text-plus-headless workflow does **not** establish
synchronization with any separate open editor or a windowed visual review.

## Evidence and validation

[Hero](d09_cranes_01-evidence/hero.png) · [Side](d09_cranes_01-evidence/side.png) ·
[Cab/boom-heel detail](d09_cranes_01-evidence/detail.png) ·
[47 m / 42° overhead](d09_cranes_01-evidence/overhead_47m_42deg.png)

All four images are **isolated Blender Cycles CPU renders**, 32 samples, AgX,
1280×720, not Godot screenshots. Overhead is vertical-down perspective with 42°
vertical FOV, north-up, camera Blender (0, 6.7, 47); the horizontal translation frames
the asymmetric overhang without changing height/FOV or rotating the asset. Earlier
1280×800 guidance is superseded by the production brief's 1280×720 maximum.
PNG compression 9, six significant RGB bits/channel, no rescaling.

The producer inspected all four final renders. The cab, weight and A-frame separate
in the hero/side; the boom retains open gaps overhead, while the cab becomes a quiet
amber roof. Thin rigging is secondary detail, not essential gameplay information.
Inspection added missing boom end posts and removed the finite studio-floor horizon;
final source/export/renders were regenerated and rechecked. The narrow overhead
silhouette fills much of this calibrated frame: that is a placement/occlusion risk,
not proof of whole-city readability or pair spacing.

[validation.json](d09_cranes_01-evidence/validation.json) records exact measurements,
actual binary GLB accessor checks, engine results and check-layer summaries.
[manifest.json](d09_cranes_01-evidence/manifest.json) hashes every produced payload
with SHA-256, excluding itself. Scratch runs and full logs stay outside the repository.

- **8,588 triangles; 4,436 source vertices; 5,924 exported vertices; one mesh,
  five surfaces.** Source vertex and export vertex counts differ at surface/normal seams.
- **Zero degenerate faces/triangles, zero non-manifold edges.** Each structural piece
  is a closed shell; intentional seated hardware intersections are not Boolean-unioned.
- Unit-length source corner and actual exported normals pass within 0.00001.
- Ground pivot, literal dimensional envelope, axis conversion and absence of unexpected
  animations, textures and dependencies pass. **Fresh re-export is byte-identical**.
- Pinned Godot **4.8.dev7.official.c971f93e7** loads the prefab and matches visual bounds,
  five opaque back-culled surfaces, identity instance, dependency UIDs and two colliders.
- Actual `ActorMotion.step` with capsule radius 0.35 m / height 1.8 m, 120 ticks/case:
  both `AUTHORITY` and `REPLAY` stop at **(0, 0.001, -3.166664)** against the plinth;
  clear side bypass ends **(3.600, 0.001, 4.000001)**. Contact is before the independent
  -3.150 m plane and within the allowed 0.030 m conservative advancement gap.
  Base/tower rays hit the correct body; the 10 m-high ray is clear of gameplay collision.
- Final production checks pass all layers: owned GDScript formatting/lint/compilation,
  **17 Python tests**, **149 GUT tests / 6,768 assertions**, and expected-failure detection.
  This checkout did not need the historical fixture-failure exception.

Diagnostics: Blender's forward-looking `use_nodes` deprecation notices and the pinned
MCP addon's 4.8-versus-tested-4.7 import warning are existing tooling diagnostics.
Initial generic production-check invocation encountered the PATH `gdvm` shim and a
Windows cp1252 reader failure; UTF-8 alone did not fix empty version discovery.
Explicit mise-pinned tool paths passed. No project, addon or global PATH changes.

### Exact reproduction commands

Run from this worktree root in Bash. Each engine invocation is bounded; no live
MCP sessions or windowed editor are used. Use fresh check output directories on rerun.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TOOL=tools/asset_production/d09_cranes_01
SCRATCH=C:/tmp/ft/assets/d09_cranes_01

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOL/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOL/validate.py"
# validate.py opens the saved source, independently reexports to scratch and compares bytes.
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . --script "res://$TOOL/check.gd" -- --normalize
timeout 180 mise exec -- gdstyle "$TOOL/check.gd"
timeout 1800 env PYTHONUTF8=1 python tools/production_checks.py \
  --godot "$GODOT" --gdstyle "$(mise which gdstyle)" --output "$SCRATCH/checks-pinned"
python "$TOOL/finalize.py" --compress-renders
# Final import before manifest/commit retains any normalized own sidecars.
timeout 300 "$GODOT" --headless --path . --import
python "$TOOL/finalize.py" --checks "$SCRATCH/checks-pinned"
```

A fresh source reauthor may change `.blend` serialization; the strict byte contract
is **saved-source fresh GLB reexport**, which passes. Prefab normalization preserves
existing saved UIDs and is not an instruction to regenerate identities.

## Remaining acceptance

- Independent technical and art review; this delivery does not accept itself.
- Pair placement in the district (the smaller crane `.02` and its equal-camera pair view are
  delivered; see `d09_cranes_02.md`), city-scale readability and actor-centred occlusion.
- World-fit measurements: all base corners on existing land; boom toward water; no
  public boardwalk through the working apron; actor/target occlusion and car turning.
- Actual Godot visual/camera review, populated-city aim/readability and collision driving.
- Real multiplayer transport/admission/prediction tests. The authority/replay test is
  a bounded production-API physics check, not separate-process networking evidence.
- Packaged-platform and Deck LCD/OLED review, repeated-placement GPU/frame time,
  shadow/LOD behavior and sustained performance. No hardware budget was inferred.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
