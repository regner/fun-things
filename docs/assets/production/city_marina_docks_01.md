# city_marina_docks.01 — Main floating-pontoon section

10 October 2026. **Source, export and linked walkable component delivered; independent
review and full world/gameplay acceptance pending.** Original Blender construction by
the commissioned implementation specialist. Production follows the [commission](commission.md),
[marina brief](../city_marina_docks.md), [Old Quay concept](../../concepts/districts-v1/old-quay.md)
and Petrol & Coral direction. No downloaded geometry, external artwork or real brands.
No earlier marina assets existed in this lane.

## Design and approved provisional family contract

A quiet composite deck with twenty broad transverse planks, restrained pale perimeter,
two rounded dark petrol flotation bodies and simple metal underdeck bearers. No ropes,
cleats, lamps, corner bumpers or yacht geometry are duplicated from other register rows.
The broad rectangular outline and pale edge remain legible in the inspected overhead;
plank joints are subordinate, not required gameplay information. Studio lighting makes
the dark composite read as a subdued grey-green rather than a bright timber texture.

The family brief left measurements and walking undecided. The supervisor approved the
following provisional component dimensions during this task, **not basin-fit approval**, and
explicitly superseded the brief's non-walkable scenery restriction with a walkable slab:

| Interface | Godot local metres |
| --- | --- |
| Root | (0, 0, 0), centred on the water datum, not flotation bottom |
| Deck footprint | 3.000 X × 8.000 Z; long axis Z |
| Deck standing surface | Y = 0.500 |
| Pale visual edge top | Y = 0.520; 2 cm lip is visual only |
| Flotation bottom | Y = -0.300; top Y = 0.250 |
| Whole visual AABB | min (-1.500, -0.300, -4.000), max (1.500, 0.520, 4.000) |
| Whole size | X/Y/Z = (3.000, 0.820, 8.000) |
| End joins | (0, 0.500, -4.000) and (0, 0.500, 4.000); rectangular butt interfaces |
| Next main module | Translate 8.000 m along Z; no corrective rotation or scale |
| Collision | 3.000 × 0.160 × 8.000 box centred (0, 0.420, 0) |

Numeric envelope/datum tolerance is ±0.001 m. Blender +Z is Godot +Y;
Blender +Y maps to Godot -Z. Both root and mesh have identity local transforms,
applied static modifiers, metre units and water-centred pivots. No sockets or rig
are exported: these are documented planar joins, not runtime attachment APIs.

The following marina rows should reuse this water/deck datum and palette: .02 fingers,
.03 shore gangway/landing, .04 end/corner/bumper and .05 cleats. Widths and spans of
those components are their own scope; do not infer basin/yacht clearance from this
section. The supervisor also requires .02–.04 walkable decks, with .03 a ramp within
ActorMotion's floor angle; .05 may remain visual-only. This document records the new
family handoff without modifying the shared brief or queue.

## Source, exports and materials

- Editable source: `art/source/models/environment/city_marina_docks_01/city_marina_docks_01.blend`.
- Named collection: `export_city_marina_docks_01`; root `CityMarinaDocks01`,
  child `CityMarinaDocks01_Mesh` (34 closed component islands joined as one mesh).
- Explicit export: `art/models/environment/city_marina_docks_01/city_marina_docks_01.glb`,
  with committed `.glb.import`. No prototype or machine-local resource dependencies.
- Linked prefab: `scenes/prefabs/environment/city_marina_docks_01.tscn`.
- Reproducible tooling: `tools/asset_production/city_marina_docks_01/`.

Five opaque Principled material surfaces; no textures, embedded images or Godot remaps:

| Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `dock_deck_dark_composite` | .075, .090, .085 | 0 | .60 |
| `dock_deck_soft_variation` | .082, .098, .092 | 0 | .60 |
| `dock_edge_warm_pale` | .57, .59, .51 | .12 | .48 |
| `dock_float_petrol` | .018, .045, .051 | 0 | .54 |
| `dock_frame_metal` | .055, .075, .079 | .55 | .44 |

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
The exporter loads `tools/assets/blender/export_settings.json`, selects only the
named collection, disables animation/skins and applies the standard Y-up conversion.
Studio geometry/lights/cameras exist only in the unsaved evidence render scene.
No runtime render-mesh generation, procedural node assembly, animation, tides,
buoyancy, mooring simulation or additional light family. Default Godot generated
LODs remain enabled; actual LOD transitions and repeat-placement cost need profiling.

## Prefab, collision and bounded checks

`Visuals/Model` is an identity-transform imported scene instance, not copied mesh
content. `Collision/Body/Deck` is the sole collision shape, separate from visuals:
static-world layer 1, mask 0. Continuous box support intentionally ignores the
8 mm plank seams and the 2 cm visual lip. Floats, frame and trim create no extra
snagging shapes. No edge-blocking rail or invisible boundary was added.

Headless Godot **4.8.dev7.official.c971f93e7** imported the GLB; the wrapper and
owned two-section fixture were loaded, packed, saved and reloaded twice with
byte-stable saved UIDs/node identities and linked ancestry. Dependency checks
resolve every saved UID/path, and measured imported bounds agree within 0.001 m.
No live editor/MCP session was touched; direct text authoring plus isolated headless
normalization was the commissioned fallback. This does not synchronize an unrelated
open editor or claim an interactive editor roundtrip.

`tools/asset_production/city_marina_docks_01/walk_check.tscn` is an authored test-only
fixture containing two linked main pontoons at Z=0 and Z=8 and a production
`ActorMotion` body with the production-sized radius .35 m / height 1.8 m capsule.
`check.gd` verifies six down-rays at deck/interior/end/seam samples hit Y=.50,
one outside-edge ray is clear, and 48 production movement ticks cross the seam
from Z=2 to **Z=6.000001907**, at **Y=.500999987**. AUTHORITY and REPLAY outcomes
match; a downward `test_move` confirms support at the destination. Two independent
standalone headless runs reproduced these results. This is movement/replay API
coverage, **not multiplayer transport/admission/prediction acceptance**.

Current ActorMotion does not implement gravity or falling. Water/fall-off behavior,
shore entry, yacht gaps, navigation and safety boundaries belong to later integration.
The slab is walkable once an actor is placed on it; these checks do not make the
basin a supported gameplay area or solve entry from a differently elevated quay.

## Evidence and validation

[Hero](city_marina_docks_01-evidence/hero.png) ·
[Side](city_marina_docks_01-evidence/side.png) ·
[Detail](city_marina_docks_01-evidence/detail.png) ·
[47 m / 42° overhead](city_marina_docks_01-evidence/overhead_47m_42deg.png).
All four were visually inspected. They are isolated Blender Cycles/AgX renders,
not engine screenshots or water/placement evidence. Overhead is vertically down,
Blender +Y at image top, perspective vertical FOV 42°, camera Z=47 m.
All images are **1280×720**, explicitly approved to supersede the earlier 1280×800
figure. PNG compression is 95 at render, then compression level 9 with seven
significant RGB bits per channel; approximately 373–415 KiB each. The initial global
palette trial caused visible shadow banding and was discarded; the final encoding
preserves smooth gradients. No labels, paintover or geometry edits were applied.

[validation.json](city_marina_docks_01-evidence/validation.json) records:

- **6,392 triangles; 3,264 source vertices; 3,933 exported split vertices**.
- **One mesh, five surfaces**, zero degenerate source faces/export triangles,
  zero non-manifold source edges, consistent winding and unit-length normals.
- Actual binary GLB positions/normals/indices checked independently of accessor bounds.
- Exact approved 3 × .82 × 8 m visual bounds, deck .50 m, root water datum zero.
- Fresh separate-process export **byte-identical** to the committed **169,224-byte GLB**.
- Full `production_checks.py` passed: pinned engine/GUT, owned-script formatting,
  lint and explicit compilation, **14 Python tests**, **75/75 GUT tests / 2,041 asserts**,
  and the intentional GUT-failure negative control. No known failures were ignored.
- Owned `check.gd` also passes pinned gdstyle 0.3.0 with zero warnings.

[manifest.json](city_marina_docks_01-evidence/manifest.json) contains SHA-256 and byte
counts for every delivered payload (excluding itself to avoid recursive hashing).
[final.log](city_marina_docks_01-evidence/final.log) is the one concise retained
command/result receipt. Raw command logs and scratch exports remain outside the
repository under `C:/tmp/ft/assets/city_marina_docks_01/`.

Diagnostics: Blender prints a `use_nodes` deprecation warning, with all commands
exiting normally. Headless editor normalization emits addon version-warning and
editor-shutdown RID/ObjectDB leakage diagnostics. An initial attempt to run
non-tool ActorMotion inside the editor failed; it was corrected by separating
editor serialization from standalone runtime physics, and checking helper completion.
The final standalone checks have **no script errors, warnings or leaked-resource
errors**. Full production checks pass in their isolated compiler/test mirror.

## Reproduction

Run from repository root using Bash. Each Blender invocation below is factory-startup,
audio-disabled, four-threaded and bounded to 900 seconds. Godot uses only the mise pin.
Python image compaction/manifest requires Pillow. Do not use the owner's live sessions.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_marina_docks_01
S=C:/tmp/ft/assets/city_marina_docks_01
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

Independent reviewer disposition remains required. World owner must fit shore-connected
clusters to the unchanged basin, preserve central water/harbour entrance/bridge clearance,
coordinate yacht sizes and other marina components, and resolve water/fall-off and
shore access before gameplay placement. Actual engine camera/blue-hour lighting,
actor contrast, repeated-piece seams, LOD transitions, sustained GPU/device/Deck costs,
packaged builds and real-process multiplayer checks remain pending. No world scene,
shared queue/progress/brief, gameplay rule or production resource outside this ID changed.
