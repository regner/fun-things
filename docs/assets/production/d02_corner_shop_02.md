# d02_corner_shop.02 — Small rear annex

10 October 2026. **Source/export and bounded headless prefab candidate delivered;
independent review and world/gameplay/device acceptance pending.** Produced by the
commissioned implementation specialist on `lane/a-cshop`. The explicit task and
[commission](commission.md) supersede the optional/concept-only production status
in [the family brief](../d02_corner_shop.md), not the requirement for review. This
handoff does not select a district placement or issue a blanket READY verdict.

## Design and dimensions

A small one-storey rear store volume, subordinate to the
[delivered wedge shop](d02_corner_shop_01.md). Warm stucco, quiet petrol base,
ivory high-window trim, opaque dark glazing and a slate-blue mono-pitch roof match
the sibling's exact material swatches. A narrow cobalt rear drip edge carries the
shop accent; three broad roof seams distinguish the annex from the main curved
roof without adding clutter. No extra shopfront, branded sign, canopy, external
entrance, interior, operating door, destruction, rig or animation is introduced.
High rear windows are integral shell decoration, like the sibling's upper windows;
no shared retail fitting carrier is duplicated. The main shop retains its accepted
shared glazed door/display, canopy and fascia hardware unchanged.

Read the family brief, district revision 02 and exact map context, stage-03 district
identities, stage-04 streets, shared district contract, source/export rules,
city_lights.01 source/evidence and Batch01–03 prefab conventions before production.
The Crescents' curved street/roof/garden relationship remains the main shop's job;
the annex must not compete with it. Footprint 29 is still only a proposed site.
No road, garden, terrain, world placement, layout data or shared brief was changed.
Original Blender construction only: no downloaded geometry, external artwork,
textures, real brands or generated runtime render meshes.

All dimensions below are **provisional authored values**, not measured from imagery.

| Measurement | Metres / contract |
| --- | --- |
| Wall footprint | 4.400 wide × 3.600 deep; area 15.840 m² |
| Wall top | Slopes from approximately 3.100 at attachment to 2.816 at outer rear |
| Whole visual width × height × depth | 4.700 × 3.390 × 3.815 |
| Godot AABB | min (-2.350, 0, -1.800); max (2.350, 3.390, 2.015) |
| Roof slope | .300 rise over 3.800 depth; approximately 4.51°, not a walkable ramp |
| Roof/body relation | Sloped wall top meets the eave underside; no open roof-wall gap |
| Roof overhang | .150 each side; approximately .215 beyond outer rear wall |
| Windows | Two 1.660 × .640 outer frames, lower frame height 1.980 |
| Pivot | Ground centre of bounding wall footprint, (0,0,0) |
| Axes | Blender +Y/+Z → Godot -Z/+Y; -Z is the hidden attachment face |
| Transforms | Root and joined mesh identity; metres, no negative/corrective scale |
| Source/export bounds tolerance | ±.001 m; source/GLB axis conversion checked |

### Sibling attachment interface

For a main-shop instance at identity, place the annex root at Godot **(0,0,6.3)**
with identity basis and unit scale. Its local Z=-1.8 face then meets the sibling's
closed rear wall at Z=4.5. Wall width 4.4 leaves .2 m on each side of the sibling's
4.8 m rear; roof width 4.7 leaves .05 m per side. All annex geometry stays at/beyond
the joining plane. The low flashing tops at 3.39 m, well below the 6.55 m shop wall
and its rear roof overhang. The sibling's tiny base trim can be concealed at this
closed joint; no passage or internal access contract is implied.

The annex owns its collider. No shell scaling, cutouts or modifications are needed.
`tools/asset_production/d02_corner_shop_02/collision_check.tscn` saves this exact
attachment using both real prefabs, plus a detached test copy and an invisible
physics floor/actor probe. It is a test fixture, not a production assembly or world
placement. The side evidence render shows the same attachment with the unchanged
shop and actual shared fitting GLBs, loaded read-only and never saved into annex
source/export geometry.

## Source, exports and materials

- Source: `art/source/models/environment/d02_corner_shop_02/d02_corner_shop_02.blend`.
- Collection `export_d02_corner_shop_02`; root `D02CornerShop02`; mesh `D02CornerShop02_Mesh`.
- Export: `art/models/environment/d02_corner_shop_02/d02_corner_shop_02.glb`.
- Adjacent `.glb.import`: UID `uid://b5yobea3kc7dy`.
- Prefab: `scenes/prefabs/environment/d02_corner_shop_02.tscn`, UID `uid://bngypubf538ba`.
- Author/export/validate/render/check/manifest tooling and saved fixture:
  `tools/asset_production/d02_corner_shop_02/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export uses
`tools/assets/blender/export_settings.json` and the explicit named collection,
with skins/animations excluded. The saved one-metre reference cube is excluded
from export. Studio cameras/lights/ground and sibling geometry exist only in the
isolated render process. Bevels and weighted normals are applied; editable mesh
geometry and the parametric original authoring recipe are committed. Closed trim
components intentionally overlap at manufactured joins; the full decorative mesh
is not one boolean-unioned solid.

Six embedded opaque Principled materials in actual export order, no textures/images:

| Slot | Material | sRGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `shop_warm_stucco` | `#B9B7A4` | 0 / .60 |
| 1 | `shop_petrol_plinth` | `#405B68` | 0 / .60 |
| 2 | `shop_ivory_trim` | `#D6CFB7` | .12 / .48 |
| 3 | `shop_upper_opaque_glazing` | `#254957` | .22 / .28 |
| 4 | `shop_slate_blue_roof` | `#344D6C` | .18 / .50 |
| 5 | `shop_cobalt_accent` | `#235FCC` | .15 / .42 |

Swatches are converted from sRGB to linear shader values, exactly as in the sibling.
Materials backface-cull; glazing is opaque. No material remapping, editable-child
overrides, emission or real lights. Default Godot automatic LOD and shadow-mesh import
remain enabled; custom LOD and performance budgets are not justified by evidence.
Sockets and animations are not applicable to this static closed building addition.

## Validation and collision

[validation.json](d02_corner_shop_02-evidence/validation.json): **3,132 triangles,
1,600 source vertices, 1,600 GLB vertices, one mesh, six surfaces, 55,228-byte GLB**.
Zero degenerate source faces/export triangles, zero non-manifold source edges;
consistent winding, positive source volume, finite unit-length normals, applied
transforms, ground datum and raw binary GLB bounds all pass. Fresh saved-source
export is byte-identical, SHA-256
`6b120db4113f4542350569fa9a2f0a7ce9f29adbdf791523d869f36d025f7d69`.
No byte-identical `.blend` regeneration is claimed.

Prefab `Visuals/Model` is an identity-transform linked import. `Collision/Body` is
one static body, layer 1 / mask 0, with one direct `Envelope` BoxShape3D child:
**size (4.4,2.8,3.6), centre (0,1.4,0)**. It covers the complete ground footprint
without claiming a walkable roof. The upper sloped wall/eave/roof are above head
height; trim/window projections remain visual decoration and do not snag actors.
There is no runtime script or authored visible primitive in the prefab.

Pinned headless import and recursive dependency/UID loading pass. Prefab and fixture
load/pack/save/reload a second time byte-identically, preserving generated UIDs and
node identities. No inherited variant exists. Scene text plus pinned headless
normalization is the mandated fallback because the windowed editor is unavailable;
no owner live Blender/Godot session was used or claimed synchronized.

The saved fixture exercises production `ActorMotion.step` / `FootCommand`, capsule
r=.350 m / h=1.800 m, for 60 physics ticks per case in AUTHORITY and REPLAY:

- Attached right/left side contacts X=±2.550781 at Z=6.300000 m.
- Attached outer rear contact Z=8.450530 m.
- Standalone attachment-face contact Z=-2.166668 m. The pinned box contact stops
  conservatively 16.7 mm outside nominal capsule tangency. The test permits at most
  20 mm conservative skin and rejects penetration; an independent ray verifies the
  actual collision plane is exactly Z=-1.800 within 1 mm. This is not a mesh offset.
- Both joint-side bypasses at X=±2.8 travel from Z=4.5 to Z=9.500001, without snags.
- Ten side/joint rays at Z=4.49, 4.50, 4.51, 6.30 and 8.09 hit both closed bodies'
  expected planes. The exact joining plane has no ray gap. An above-roof ray clears.
- Mode-paired final positions agree within 2 mm (largest observed difference .878 mm,
  vertical only). These checks do not establish network transport or car handling.

Canonical production checks pass **all layers without exclusions**: 219 owned-script
compile records, formatting/lint, 17 Python tests, 165 GUT tests / 6,918 assertions,
and the intentional negative test exits 1 as required. Owned GDScript separately
passes pinned gdstyle 0.3.0 with zero warnings. Final runtime physics logs contain
no ERROR/SCRIPT ERROR/WARNING. Editor normalization emits the existing MCP pin
warning and renderer/text/Canvas/ObjectDB shutdown leaks after successful assertions;
these are retained as editor-process diagnostics, not suppressed or called clean.
The lean [final log](d02_corner_shop_02-evidence/final.log) records corrections and
outcomes; raw logs remain outside Git.

## Evidence and reproduction

[Hero](d02_corner_shop_02-evidence/hero.png),
[side/rear attachment context](d02_corner_shop_02-evidence/side.png),
[window/eave detail](d02_corner_shop_02-evidence/detail.png),
[47 m / 42° overhead](d02_corner_shop_02-evidence/overhead_47m_42deg.png).
All four self-inspected: the final hero is unclipped, the low roof reads distinctly
below the main shop, and the small quiet footprint/three seams survive overhead.
The side image shows the real sibling attachment, not a substitute shell. Broad
window/eave details are intentionally absent from the true overhead read. Studio
views do not prove populated blue-hour gameplay visibility or district road fit.

Isolated Blender Cycles CPU / AgX, 32 samples, 1280×720, PNG compression 95 followed
by RGB seven-bit compaction/level-9 PNG. Overhead is vertical-down perspective at
Blender (0,0,47), fixed yaw and 42° vertical FOV; not a tilted or engine capture.

Exact commands from worktree root (use a fresh output directory for checks):

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T='tools/asset_production/d02_corner_shop_02'
S='art/source/models/environment/d02_corner_shop_02/d02_corner_shop_02.blend'
TMP='C:/tmp/ft/assets/d02_corner_shop_02'
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
mkdir -p "$TMP"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 "$S" --python-exit-code 1 --python "$T/export.py" -- "$TMP/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$TMP/reexport/d02_corner_shop_02.glb"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --editor --path . --script "res://$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "res://$T/check.gd"
"$(mise which gdstyle)" fmt --check "$T/check.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$TMP/checks-fresh"
python "$T/manifest.py" "$TMP/checks-fresh"
python "$T/manifest.py" --verify
```

[manifest.json](d02_corner_shop_02-evidence/manifest.json) hashes every produced
payload except itself, including the explicitly requested sibling current-handoff
link/hash refresh. Historical receipts are unchanged. Source/export assets of the
sibling are read-only; its producer manifest still verifies independently.

## Remaining acceptance

- Independent art/source/prefab review and final asset acceptance remain pending.
- Optional annex placement/design selection remains with the district/world owner;
  the delivery does not require it to be placed at footprint 29.
- World circulation, car impacts/turns, populated blue-hour camera/occlusion, actual
  multiplayer transport/admission/prediction, packaging and sustained repeated-use /
  Steam Deck performance remain downstream. No rooftop or interior gameplay.
- No queue, shared progress/brief, project settings, world scene or historical receipt
  was changed. Only the task-authorized sibling current handoff and its manifest hash
  were refreshed; no unfinished TODO or register item was marked complete.
