# city_planting.04 — small broad-canopy tree

9 October 2026. **Source/export verified; engine integration and independent acceptance pending.**
Producer: assigned city_planting.04 specialist. ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2` owns dispatch/integration. Input commission read
at immutable baseline `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`.
No READY or independent-review claim.

Two original reusable trees: compact/upright and broader/rounder. Five smooth,
asymmetrically profiled foliage masses form each crown, above a gently bent,
flared trunk with four fused branch forks. The compact tree has a raised leader;
the broad tree spreads its shoulders and lowers the dome. Geometry carries the
variation; materials are shared. No individual leaves, dense textures, wind,
growth, rig, animation or placement-specific models.

References read: AGENTS.md, assets workflow, accepted art direction, city_planting
brief, district common contract, approved district identities and Signal Row
breakdown/reference v03. The Signal Row image was visually inspected; its dense
foliage is simplified deliberately. Existing .01/.02 planter and .03 shrub reports
and local scripts were used read-only. `reference_inputs.json` fingerprints these
inputs. Original local Blender authorship; no downloaded art, image-derived mesh,
paid generators, external textures or linked libraries. Export/check/runner methods
adapt city_planting_03 tools. Historical concept-only restrictions are superseded
by the production commission; concept imagery does not ratify exact dimensions.

## Source, variants and interface

Source: `art/source/models/environment/city_planting_04/city_planting_04.blend`.
Master collection `export_city_planting_04` contains child export collections
`export_city_planting_04_compact` and `export_city_planting_04_broad`. Each contains
its identity root `city_planting_04_<variant>`, one `*_sculpted_trunk` mesh and five
`*_crown_{leader,west,east,front,back}` meshes. Both variants occupy the same datum;
the broad collection starts hidden for editing. Toggle the collections to compare.
The exporter enables each collection and selects only that variant. Editable
studio cameras/lights/floor stay in `studio_do_not_export`.

Explicit outputs:

- `art/models/environment/city_planting_04/city_planting_04_compact.glb`
- `art/models/environment/city_planting_04/city_planting_04_broad.glb`

Metres, Metric scale 1; ground-centred planting pivot at zero. Every exported
root/mesh has identity local and world transforms, no remaining modifiers. Blender
+Y front/+Z up converts to Godot -Z/+Y. Slight crown asymmetry around the planting
pivot is intentional. No sockets needed for a static plant.

| Measurement, metres | Compact/upright | Broad/rounder |
| --- | ---: | ---: |
| Godot X/Y/Z dimensions | 1.998589 / 3.596365 / 1.847576 | 2.772049 / 3.317199 / 2.441693 |
| Godot minimum | (-0.908597, 0, -0.953385) | (-1.288243, 0, -1.238169) |
| Godot maximum | (1.089992, 3.596365, 0.894191) | (1.483806, 3.317199, 1.203524) |
| Lowest foliage | 2.165928 | 2.125254 |
| Max trunk radius below surround rim | 0.197217 | 0.197698 |
| Minimum radial gap to surround clear core | 0.422033 | 0.421552 |
| Source vertices | 9,656 | 9,721 |
| Export triangles | 19,282 | 19,418 |
| GLB bytes | 278,900 | 281,264 |

Bounds tolerance **0.001 m**; source/GLB axis conversion actually compared at
0.00001 m. These are reversible production proposals, not inferred image dimensions.
The compact spread is about the 1.80 m surround diameter; the broad spread extends
about half a metre farther each side. Both are substantially taller than the .03
0.67 m shrub and retain its quiet jade family. The .01 2.40 m trough is a shrub
interface, not the intended tree surround.

**Round .02 assembly:** align both ground pivots at `(0,0,0)`, with no lift or scale.
The open ring is 0.48 m high, with conservative inscribed clear diameter 1.2385 m.
The tree stays within radius 0.198 m through the entire rim-height volume; triangle
edges crossing that plane are included in the test. No soil is supplied or assumed.
A later raised soil assembly must explicitly revisit ground contact and clearances.

Forks begin around 1.6 m; foliage begins above 2.12 m. This creates a clear lower
silhouette, not a guarantee that actors can pass underneath. Opaque crowns still
hide actors directly below them in a vertical camera. Keep trunks/overhang away
from shortcuts, entrances, bridge access and critical corners. Proposed actor
centre spacing of 2.6 m is demonstrated in one static near-centre camera fixture;
edge-of-frame perspective, movement, other actor poses and crowded placements
remain integrator checks. No automatic cutaway/fade is introduced.

## Geometry, materials and visual evidence

Six meshes / six export primitives / three opaque, single-sided embedded PBR
materials per variant. Five crown shells intentionally overlap; each is closed,
but they are not a Boolean foliage union. Trunk forks are unified meshes. Smooth
shading and one applied crown subdivision preserve broad contours at hero range.
Density is recorded rather than treated as a ratified performance budget; LOD and
instancing decisions await integration measurements.

| Slot 0 assignment | sRGB | Roughness |
| --- | --- | ---: |
| leader/west/front: `tree_quiet_jade` | #42694A | .87 |
| east/back: `tree_soft_sage` | #4D704D | .87 |
| trunk: `tree_warm_umber` | #5B4D37 | .93 |

Colors are converted to linear shader inputs, metallic zero. No textures, UVs,
tangents, external materials, animation or collision are needed for this static
color-only source. No runtime mesh generation; Blender authors the saved meshes.

Evidence in [city_planting_04-evidence](city_planting_04-evidence/):
[compact hero](city_planting_04-evidence/compact_hero.png),
[broad hero](city_planting_04-evidence/broad_hero.png), and each variant's
`*_project_camera.png`. Heroes are 1100×900 oblique orthographic, 4.9 m frame.
Native references are 1280×800, vertical-down perspective, 47 m height / 42° vertical
FOV. Cycles CPU four threads, 32 samples, AgX, broad area lights and slate floor.
These are Blender studio views, not Godot/runtime captures.

`pair_surround_actor_hero.png` and `pair_surround_actor_project_camera.png` reuse
the existing round planter and coral_courier GLBs read-only, at tree X=-2.5/+2.5 m
and actor offset Blender (0,-2.6,0). `assembly_preview.json` records input hashes,
camera assertions and actual projected vertex bounds. At 2.6 m the conservative
actor/tree bounds separate by 14.43 px (compact) and 7.23 px (broad), exceeding the
5 px fixture threshold. Trees span about 47 px and 65 px respectively. No shared source, prefab
or placement is saved. High branching and restrained crown size support this
example; they cannot prove visibility across a city.

## Checks, diagnostics and reproduction

Private `/usr/bin/blender` is the installed exact authorized build: **5.2.2 LTS,
d13f752e3b9c**, glTF **5.2.40**, asserted inside author/export scripts. The supplied
`/usr/bin/blender5.2.2LTS` path is absent. No shared connector/editor was controlled.
Only process-local `ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy`, supported `-noaudio`
and four render threads were used.

**PASS:** both final saved-source exports and independent binary GLB checks.
Source audit checks finite coordinates, unit normals, positive volume, consistent
closed edges, nondegenerate faces, identity transforms, membership and planter
clearance. Binary audit checks actual positions/indices/unit normals, every triangle
area, bounds/axes, materials, exact nodes and studio/animation/texture exclusion.
`source_export_checks.json` and `glb_checks.json` retain the measured values.

**PASS:** each GLB reexported from the saved .blend in a fresh process, byte-identical
(`reexport_checks.json`, `reexport_comparison.json`, retained scratch GLBs):

- Compact SHA256 `7e1a678453324fc9843e9941ddf9c3fad30e19d6f206d11ee404932cc525708e`
- Broad SHA256 `b02f3594925972cf4002811042b606734fbc8a5c7f1d9ed5c719022809b1130b`

One correction cycle refined crown contours and repaired remesh/decimation debris.
Initial topology failure was first misdiagnosed as an open tip: hole filling did
nothing, and explicit cap creation failed because the quad already existed. Further
inspection established a tiny disconnected quad inside each crown, plus two nearly
zero-area compact trunk faces. The isolated quads were removed and degenerate edges
dissolved at 0.000001 m. Full failed logs, original scripts and initial sources are
retained in `initial_attempt/` and named diagnostic logs. Final audits pass without
suppressing exceptions. Initial author/diagnostic processes overlapped; their ledger
race is disclosed in reconstructed exact argv/exit receipts in `commands.json`.
Subsequent jobs ran sequentially.

The first actor-spacing test at 2.3 m failed the conservative 5-pixel projected
bounds-gap threshold (broad tree: 0.579929 px). The retained initial spacing images
and log show this failure. The unsaved comparison was revised to 2.6 m; this changes
the proposed placement clearance only, not source/export geometry.

Other retained diagnostics: future `Material.use_nodes` deprecation; OpenImageIO
cannot write an external desktop thumbnail (actual .blend/PNGs saved and reopened);
optional MeshOptimizer unavailable (uncompressed exports pass); version invocation
reports one 23-byte unfreed block. BlenderMCP startup/shutdown registration messages
are addon initialization, not live connector usage. No global config changed. The first final PNG audit could not import Pillow;
`final_audit_initial.log` retains that failure. The final dependency-free audit uses
PNG signature/chunk CRC and zlib payload checks instead; no package was installed.

Routine saved-source export and validation from repository root:

```bash
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy /usr/bin/blender -b -noaudio -t 4 \
  art/source/models/environment/city_planting_04/city_planting_04.blend \
  --python-exit-code 1 --python tools/asset_production/city_planting_04/export.py
python tools/asset_production/city_planting_04/check_glb.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy /usr/bin/blender -b -noaudio -t 4 \
  art/source/models/environment/city_planting_04/city_planting_04.blend \
  --python-exit-code 1 --python tools/asset_production/city_planting_04/export.py \
  -- /tmp/city_planting_04_reexport
cmp art/models/environment/city_planting_04/city_planting_04_compact.glb /tmp/city_planting_04_reexport/city_planting_04_compact.glb
cmp art/models/environment/city_planting_04/city_planting_04_broad.glb /tmp/city_planting_04_reexport/city_planting_04_broad.glb
```

`author.py` reconstructs the source; `repair_tips.py` performs the documented cleanup
after reconstruction. Routine reexport does neither. `preview_saved.py` renders the
final saved source; `assembly_preview.py` creates the unsaved comparison.
`commands.json` retains actual argv, exits and complete raw logs. `manifest.json`
contains exact producer-owned path/byte/SHA256 payloads, excluding only itself and
Python cache. Import metadata belongs to the integrator.

Godot import/UIDs, linked prefab/inherited save-reopen, collision/movement/query/network,
actual runtime actor/camera/material validation, Deck/device performance, placement
and independent technical/art acceptance remain **pending**. No shared docs,
project, prefab, world or Git/index changes were made. Owned writers are quiescent
at handoff; available for concrete review findings.
