# d02_domestic_details.04 — Small porch canopy

**Source/export, linked prefab and bounded headless checks delivered; independent
review and placement acceptance pending.** Production commissioned by Regner under
[the commission](commission.md) and the current per-asset production brief. Original
Blender construction by the commissioned worker on `lane/a-d02`; supervisor/reviewer
owns acceptance and world integration. No live Blender/Godot session was touched.

Family: [Domestic boundary and porch details](../d02_domestic_details.md).
Direction: [The Crescents](../../concepts/world-v1/stage-03-district-identities/README.md),
[selected revision 02](../../concepts/districts-v1/02-the-crescents-v02.png), and
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).
The production commission supersedes historical concept-only restrictions.

## Design and dimensions

A small wall-mounted lean-to canopy: one quiet sage-metal roof, ivory fascia,
a slate rear flashing and two simple diagonal slate brackets. The shallow roof
sheds away from the wall; the understated edge and open underside suit domestic
entrances rather than a commercial awning. No posts or boundary walls close the
approach. No brand, artwork, light, interior, working door, animation, destruction,
interaction or rooftop traversal is added. Original Blender geometry only; no
external meshes, downloads, textures or image-to-mesh construction.

The [straight wall](d02_domestic_details_01.md), [return](d02_domestic_details_02.md)
and [mailbox](d02_domestic_details_03.md) establish the family finish. This canopy
retains the mailbox's exact sage enamel `#526B65`, ivory `#D4CEBB` and slate `#58636B`
materials. These are quiet manufactured finishes, not a new bright roof accent.

Dimensions are **provisional authoring proposals**, consistent with the standing
rule, not measurements from concept images or approved home attachment clearances.
Bounds tolerance is 0.001 m; unit-normal tolerance is 0.0001.

| Contract | Metres, Godot local axes |
| --- | --- |
| Visual size X / Y / Z | 2.000 / 0.650 / 1.150 |
| Visual AABB | (-1.000, 2.600, -0.575) to (1.000, 3.250, 0.575) |
| Pivot | Ground-projected footprint centre (0,0,0); **no mesh contacts the ground** |
| Front / wall mounting plane | Front -Z; rear mounting faces at Z=+0.575 |
| Roof sheet | 2.000 wide; 1.150 projection; 0.075 vertical thickness |
| Roof height | Rear nominal top 3.230; front nominal top 3.000, softened edges |
| Flashing | 1.940 wide × 0.050 high × 0.080 deep; maximum height 3.250 |
| Wall plates | Centres X=±0.720; each 0.120 wide × 0.560 high × 0.050 deep |
| Lowest part / actor headroom | Wall plates at Y=2.600; 0.800 above a 1.800 m actor |
| Braces | Two 0.080 square struts, sloping from wall toward the front underside |
| Fascia | 0.120 front height; 0.100 side height; tucked inside the roof edge |

Nine closed parts are joined into one editable mesh. Small applied bevels and
weighted normals soften edges without tile noise or extra roof clutter. The ivory
front fascia laps the side ends with a small inset rather than coplanar faces.
Blender +Z maps to Godot +Y; Blender +Y/front maps to Godot -Z. All export members
have identity transforms and metre units. A non-export hidden-render 1 m reference
cube remains in the source. No attachment sockets, rigs or state variants are needed.

### Placement interface

Keep the prefab root on the local ground datum: **do not add a second 2.6 m lift**.
For a flat facade facing -Z at coordinate `wall_z`, place the canopy root at
`(entry_x, ground_y, wall_z - 0.575)`, with unit scale and matching facade yaw.
The rear plate faces and flashing back then meet the wall; the front projects
1.150 m from it. Rotate the whole prefab for other facades, without negative scale.

The delivered homes have 2.380 m high closed door leaves and 1.200–1.300 m widths;
the proposed 2.000 m canopy is a sensible starting envelope, not a certified fit.
Check chosen door surrounds, upper-window sills, courses and adjoining walls before
placement. This standalone asset does not require or author a home assembly. The
building continues to own its closed facade collider. Do not place this canopy as
a freestanding shelter, lower it below the overhead-only threshold, or extend it
across a foot-link mouth. Do not use its visual roof as a walkable surface.

## Source, export and materials

- Source: `art/source/models/environment/d02_domestic_details_04/d02_domestic_details_04.blend`.
- Collection: `export_d02_domestic_details_04`.
- Root / mesh: `D02DomesticDetails04` / `D02DomesticDetails04_Mesh`.
- GLB: `art/models/environment/d02_domestic_details_04/d02_domestic_details_04.glb`
  with its engine-normalized `.import`.
- Prefab: `scenes/prefabs/environment/d02_domestic_details_04.tscn`.
- Author/export/validator/render/receipt tools and engine check:
  `tools/asset_production/d02_domestic_details_04/`.

One mesh, three opaque Principled surfaces in actual exported order:

| Slot | Material | Roughness | Metallic |
| --- | --- | --- | --- |
| 0 | `crescents_sage_enamel` | 0.42 | 0.25 |
| 1 | `crescents_ivory_trim` | 0.55 | 0 |
| 2 | `crescents_slate_plinth` | 0.75 | 0 |

Original flat colors converted from sRGB to linear; backface culling enabled.
The validator compares all three exported material definitions to the mailbox's
actual GLB. No textures, embedded images, external remaps, shaders, skins or morphs.
Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; export loads
`tools/assets/blender/export_settings.json`, filters the named collection and disables
animations/skins. Studio objects never enter the source/export. Godot
**4.8.dev7.official.c971f93e7** imports scale 1, default automatic LODs and shadow
meshes. No repeated-placement or target-device performance budget is claimed.

## Prefab and collision

Saved `Visuals/Model` is an identity-transform linked imported instance, with no
material overrides or copied geometry. **No collider:** every visible part is above
2.5 m, matching the standing canopy/overhead exception. No floor, posts, invisible
wall, navigation, world IDs or gameplay code is added. A 1.8 m actor has 0.8 m
geometric clearance below the lowest metal. Actual house/porch clearance remains
placement review; the isolated clear-passage test is not evidence of an open door.

Live editor tools were prohibited and the windowed editor is unavailable. The
commissioned text fallback was loaded/packed/resaved by pinned headless Godot;
the second save was byte-stable. Prefab UID `uid://cgtjynslya47g`, model UID
`uid://12vok3h7brcg`, imported ancestry and saved node identities resolve. No separate
open editor synchronization is claimed.

## Evidence and reproduction

[Hero](d02_domestic_details_04-evidence/hero.png),
[side](d02_domestic_details_04-evidence/side.png),
[underside detail](d02_domestic_details_04-evidence/detail.png),
[gameplay overhead](d02_domestic_details_04-evidence/overhead_47m_42deg.png).
All four final compressed images were inspected. Close views show the single
sloping roof, quiet ivory edge and attached open brackets. The overhead roof spans
approximately **43 pixels**; it reads as a small, quiet rectangular entrance cover,
not a route cue. Bracket detail is not readable overhead and is not used to convey
interaction. Placed actor/combat occlusion under this opaque roof remains open.

These are isolated Blender Cycles CPU renders, 32 samples, AgX, **1280×720**, PNG
compression 95 plus six-bit RGB compression; each is below 400 KB. Overhead is
vertical-down perspective at 47 m / 42-degree vertical FOV, north at image top.
The standing 1280×720 evidence-size rule supersedes the older 1280×800 reference.
No image is an engine capture. Initial coplanar roof/fascia and fascia-corner faces
caused black artifacts; insets removed them. The flashing was deepened into the
roof and wall plates extended to its underside. All final views were rerendered
and inspected after those source corrections; retries stay scratch-only.

Run from repository root in Bash; all process calls are bounded:

```sh
N=d02_domestic_details_04
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="C:/tmp/ft/assets/$N"
mkdir -p "$S" "docs/assets/production/$N-evidence"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8

timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/author.py"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/render.py"
python "tools/asset_production/$N/record.py" --compress-renders
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  "art/source/models/environment/$N/$N.blend" \
  --python "tools/asset_production/$N/export.py" -- "$S/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/validate.py" -- "$S/reexport/$N.glb"

timeout 300 "$G" --headless --path . --import > "$S/import-initial.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "tools/asset_production/$N/check_prefab.gd" -- --normalize \
  > "$S/normalize-editor.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "tools/asset_production/$N/check_prefab.gd" \
  > "$S/prefab-final.log" 2>&1
"$(mise which gdstyle)" fmt --check "tools/asset_production/$N/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$N/check_prefab.gd"
python "tools/asset_production/$N/record.py"
python "tools/asset_production/$N/record.py" --verify
```

Tools follow the sibling patterns and reuse the shared export contract. The validator
reads the mailbox GLB for palette comparison without modifying it.
`production_checks.py` was not run, per owner decision 52.

## Validation results

[Final receipt](d02_domestic_details_04-evidence/validation.json),
[concise diagnostic log](d02_domestic_details_04-evidence/final.log),
[producer manifest](d02_domestic_details_04-evidence/manifest.json).

- **1,692 triangles, 864 Blender vertices, 982 GLB vertices; one mesh, three surfaces.**
- **Zero degenerate faces/triangles and zero non-manifold edges**; contiguous source
  winding, positive signed volume, outward binary triangle winding and unit normals.
- Source, actual binary GLB and imported Godot AABBs match the independent dimensions
  within 0.001 m. Export transforms are identity; the root is on projected ground,
  while the mesh minimum is Y=2.600 m. All three materials exactly match the mailbox.
- Fresh separate-process saved-source reexport is byte-identical: **44,696 bytes**,
  SHA-256 `51e2bc0bce7f2d0ad32c538caa69239e8b3e7d527ecc5bfb6b92645dd927bf72`.
- Final pinned import exits 0 with **no ERROR/SCRIPT ERROR lines**. Fresh runtime
  resolves all dependencies, opaque/back-culling surfaces, UIDs and linked ancestry.
- Three capsule queries under the centre and both braces are clear; the vertical
  ray is clear. The wrapper contains zero collision bodies and zero shapes.
- Production `ActorMotion.step`, r=0.35 m / h=1.8 m: centre and both brace-line
  passages pass 60 fixed ticks each in AUTHORITY and REPLAY, with identical endpoints.
  Each starts at Z=-2 and reaches Z=3.000000; X=0 or ±0.720 is retained. A physics-only
  test floor is outside the prefab and removed after checking.
- A 1.9×1.5×4.3 m car-sized test box passes under the isolated canopy and beside it.
  This is a no-hidden-collision sweep, **not** production driving or home access proof.
- Pinned `gdstyle fmt --check` and strict lint pass; function comments and spacing
  were checked. Producer manifest verifies the complete produced payload set.

Blender authoring reports known future-6.0 `use_nodes` deprecations. Import reports
the existing MCP 4.8 compatibility warning. Headless editor normalization proves
byte stability and exits 0 but emits scan-aborted/RID/ObjectDB shutdown diagnostics,
retained verbatim in `final.log`. Fresh runtime has no ERROR/WARNING lines. No
warnings or errors were broadly suppressed and no live owner process was accessed.

## Remaining acceptance

- Independent source/technical and art review at the committed candidate.
- World integrator: fit to chosen home facade/door/course/window geometry, matching
  yaw and ground datum, mounting contact, repeated plots and visible foot shortcuts.
- Gameplay/camera owner: native 47 m/42-degree visibility under opaque canopies,
  actual placed actor/combat/car movement and unobstructed walking alternatives.
- Network owner: actual separate-process world/session evidence when integrated;
  local authority/replay equivalence is not multiplayer transport acceptance.
- Device/performance owner: native materials/LODs, repeat-placement profiling,
  packaged dependencies and sustained Deck LCD/OLED evidence.

Earlier domestic-detail sibling handoffs were checked; none lists this canopy as
still pending, so no sibling document or manifest edit is needed. Shared queue/
progress, world scenes, project settings and historical receipts remain unchanged.
