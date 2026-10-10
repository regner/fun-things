# d02_corner_shop.01 — Wedge-footprint shop shell

10 October 2026. **Source/export and bounded headless prefab candidate delivered;
independent review and world/gameplay/device acceptance pending.** Produced by the
commissioned implementation specialist on `lane/a-cshop`. The explicit production
task and [commission](commission.md) supersede the historical concept-only status
in [the family brief](../d02_corner_shop.md). Review/acceptance belongs to the
supervisor's independent reviewers; this is not a self-issued production-ready verdict.

## Design and dimensions

A modest two-storey shop with a broad street frontage tapering to a narrow rear,
quiet slate-blue roof, shallow curved cobalt eave, warm stucco, three paired upper
windows and restrained amber entrance accents. Actual accepted canopy, fascia,
surround, display and closed-door hardware is reused rather than rebuilt. The roof
responds to the Crescents' curved-road/wedge-garden idea without adding a road,
sidewalk, garden, procedural world placement or bespoke planting.

Read the family brief, Crescents revision 02/image and selected map context,
stage-03 district identities, stage-04 streets, art/source contracts, accepted
city_lights.01 tooling/evidence and Batch03 fitting interfaces before authoring.
Footprint 29 remains only the proposed site; no district/world scene was changed.
The district's 5.26 ha is not treated as this shop's allocation. All dimensions
below are **provisional authored choices**, not measurements from generated imagery.
Original Blender construction only; no downloads, real brands, external textures,
image-to-mesh geometry, interiors, working doors, destruction, rigs or animations.

| Measurement | Metres / contract |
| --- | --- |
| Bounding wall footprint | 12.800 wide × 9.000 deep; rear width 4.800 |
| Footprint area | 79.200 m², trapezoid rather than a rectangular building |
| Wall/collider height | 6.550; two-storey exterior only |
| Nominal roof plan before bevel | 13.300 wide; rear Z=4.750; curved front Z=-5.150 |
| Measured shell width × height × depth | 13.288225 × 7.180236 × 9.900000 |
| Shell Godot AABB | min (-6.644112, -0.000236, -5.150000); max (6.644113, 7.180000, 4.750000) |
| Full fitted visual envelope | same X/Y bounds; front Z=-5.600 from shared canopies, depth 10.350 |
| Pivot | (0,0,0), ground centre of bounding wall footprint |
| Front/up | Blender +Y/+Z → Godot -Z/+Y, one glTF conversion |
| Envelope/ground tolerance | ±0.001 m against rounded measured dimensions |
| Root/mesh transforms | Identity, metre units, no negative/corrective scale |

The roof's softened tips retract about 5.9 mm per side from its nominal pre-bevel
width. The Boolean/bevel wall ground is within 0.237 mm of zero; the collider ground
is exactly zero. This is inside the declared 1 mm datum tolerance. The roof front
curve has 24 broad spans, rising in plan by 0.400 m from its chord; it is not a
terrain slope. The roof centre stays quiet, with only one low rear seam. Roofs and
canopies are not walkable routes; no rooftop gameplay is introduced.

## Source, exports and materials

- Source: `art/source/models/environment/d02_corner_shop_01/d02_corner_shop_01.blend`.
- Collection: `export_d02_corner_shop_01`; root `D02CornerShop01`, mesh `D02CornerShop01_Mesh`.
- Explicit linked export: `art/models/environment/d02_corner_shop_01/d02_corner_shop_01.glb`.
- Import sidecar: adjacent `.glb.import`, UID `uid://rmd1q6w4h5p0`.
- Prefab: `scenes/prefabs/environment/d02_corner_shop_01.tscn`, UID `uid://64d2osnmp04f`.
- Parametric author/export, source/raw-GLB/fit validator, renderer, saved collision
  fixture, headless check and producer manifest: `tools/asset_production/d02_corner_shop_01/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export reads
`tools/assets/blender/export_settings.json`, explicitly selects the named collection
and excludes animations/skins. No studio, reference cube, camera or light exports.
A saved excluded `authoring_1m_reference` verifies metre units. Boolean recesses,
bevels and weighted normals are applied; the source retains editable geometry and
the author script retains the recipe. Closed trim components intentionally overlap
at manufactured joins; this is not one boolean-unioned volume for all decoration.

Seven opaque, back-culled embedded Principled surfaces, in actual export order:

| Slot | Material | sRGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `shop_warm_stucco` | `#B9B7A4` | 0 / .60 |
| 1 | `shop_petrol_plinth` | `#405B68` | 0 / .60 |
| 2 | `shop_cobalt_accent` | `#235FCC` | .15 / .42 |
| 3 | `shop_ivory_trim` | `#D6CFB7` | .12 / .48 |
| 4 | `shop_upper_opaque_glazing` | `#254957` | .22 / .28 |
| 5 | `shop_entry_amber` | `#FFC05A` | .05 / .45 |
| 6 | `shop_slate_blue_roof` | `#344D6C` | .18 / .50 |

Swatches convert to linear shader values. Upper windows are integral shell decoration,
not a new shared fitting variant. Glazing is opaque; no interior or transparency cost
is implied. No textures, embedded images, emission, real lights or material overrides.
Default engine LOD/shadow-mesh import remains enabled; no speculative custom LOD or
performance budget is claimed. No runtime script is attached to the prefab.

## Saved shared fitting mounts

All paths below are `res://` paths. All mounts have identity basis, unit scale and
only the listed Godot local XYZ translation. They are children of `Fittings` in the
saved prefab, not a runtime-authored hierarchy. The shell itself remains an identity
linked import at `Visuals/Model`.

| Mount | Source prefab / GLB path | Translation |
| --- | --- | --- |
| CanopyLeft | `scenes/prefabs/environment/city_shop_fittings_01.tscn` | (-3.6, 3.0, -4.5) |
| CanopyEntry | `scenes/prefabs/environment/city_shop_fittings_01.tscn` | (0, 3.0, -4.5) |
| CanopyRight | `scenes/prefabs/environment/city_shop_fittings_01.tscn` | (3.6, 3.0, -4.5) |
| Fascia | `scenes/prefabs/environment/city_shop_fittings_02.tscn` | (0, 3.8, -4.5) |
| Surround | `scenes/prefabs/environment/city_shop_fittings_03_single.tscn` | (0, 0, -4.5) |
| DisplayLeft | `art/models/environment/city_shop_fittings_05/city_shop_fittings_05.glb` | (-3.6, .48, -4.5) |
| DisplayRight | `art/models/environment/city_shop_fittings_05/city_shop_fittings_05.glb` | (3.6, .48, -4.5) |
| ClosedDoor | `art/models/environment/city_shop_fittings_06/city_shop_fittings_06_single.glb` | (0, 0, -4.5) |

**Supervisor-approved reuse choice:** display and door GLBs are linked directly as
visual-only imports. Their usual prefabs' colliders are intentionally omitted because
the single solid wedge collider supersedes them. Canopy/fascia/surround prefabs add
no collision. No copied geometry, editable-child overrides, sibling edits or carrier
exports were introduced. The fascia stays blank; neighbourhood graphics owns copy.

The front wall is one closed Blender solid with blind rectangular recesses: entrance
width 1.420 × height 2.450 from ground; displays width 3.040, heights .540–2.420,
centres X=±3.600. All recesses extend .650 behind facade Z=-4.500 to Z=-3.850,
exceeding the shared entrance's .540 and display's .200 rear-void requirements.
Independent source rays measure the rear plane; a pier ray measures the facade.
Actual imported shared display/door meshes have **zero shell-surface intersections**
at these transforms; dependency SHA-256 values are recorded in validation.json.
The surround's existing casing/reveal/leaf contract is unchanged. Canopy low edge
is 2.580 m, 0.100 m above the fittings; fascia bottom 3.400 leaves 0.160 m above the
canopy top. These are static fitted interfaces, not an operable doorway contract.

### Rear annex interface for d02_corner_shop.02

Rear wall centre is Godot `(0,0,4.5)`, width 4.800, facing +Z; plain closed wall with
no passage or door. Keep any annex at/beyond Z=4.5, no wider than the 4.8 m rear if
flush-mounted, and below the 6.55 m wall top. The roof overhang reaches Z=4.75;
low annex roof flashing may tuck beneath it. Do not scale/alter this shell to fit.
The annex remains its own optional family member and must own its separate collider.
Slate-blue roof, warm stucco and quiet petrol base are the shared family language.
No annex geometry or socket node is prebuilt here; placement remains saved-scene work.

## Validation and collision

[validation.json](d02_corner_shop_01-evidence/validation.json) records **6,292 triangles,
3,192 Blender vertices, 3,290 GLB vertices, one mesh and seven surfaces; 149,908-byte
GLB**. These counts describe the new shell export, not the reused fittings. Zero
degenerate source faces/export triangles and zero non-manifold source edges; closed
consistent winding, positive source volume, finite unit normals, identity transforms,
metre bounds and source/GLB coordinate conversion pass. Fresh saved-source reexport
is **byte-identical**, SHA-256
`80f5d0b905fe2e90778948a7d1b2501171af06ba12353e635a40b890870e096a`.

**Supervisor-approved collision exception:** one authored `ConvexPolygonShape3D`,
not render-mesh-derived collision and not a rectangular approximation. The four
Godot XZ corners `(-2.4,4.5), (2.4,4.5), (6.4,-4.5), (-6.4,-4.5)` are extruded
from Y=0 to Y=6.55: eight explicit saved points. One static body at `Collision/Body`,
layer 1 / mask 0, with a direct child shape. The convex solid includes the closed
frontage and its visual entrance recess: actors stop at the facade, not inside a
vestibule. No interiors or opening state is offered. Roof edges/canopies are overhead
visual-only; thin wall trims do not create snagging collision.

The saved owned fixture exercises production `ActorMotion.step` / `FootCommand`,
capsule r=.350 m / h=1.800 m, for 60 physics ticks per case in AUTHORITY and REPLAY:

- Right/left diagonal contacts: X=±4.720073, Z=.142254 m. No side-wall gap.
- Front/rear contacts: Z=±4.850256 m, at the intended closed-shell envelope.
- Clear route at X=5.400, Z=-1→4 reaches Z=3.999998 m, inside the rectangular AABB
  but outside the wedge. No invisible rectangular corner blocker.
- Rays hit both actual diagonal planes at X=±4.400; roof-height and clear-corner
  rays remain unblocked. All five mode-paired outcomes agree within 2 mm; measured
  maximum difference is under .008 mm. This is not network transport proof.

Pinned headless import, recursive dependency/UID checks, eight mount transforms,
one-collider count and imported bounds pass. Prefab and collision fixture are
loaded/packed/resaved/reloaded; second saves are byte-stable and preserve generated
UIDs/node identities. No inherited variant exists. Direct-file scene authoring followed
by headless save is the mandated fallback: the windowed editor is unavailable/crashing,
and owner live Blender/Godot sessions were never used. No claim of synchronizing an
unrelated open editor is made.

Canonical production checks pass **all layers**, with no failure exclusions: 218
script compile records, formatting/lint, 17 Python tests, 165 GUT tests / 6,918
assertions, and the intentional negative test correctly exits 1. Owned GDScript also
passes pinned gdstyle 0.3.0 directly. Full raw logs/retries are outside Git; the lean
[final log](d02_corner_shop_01-evidence/final.log) retains outcomes and diagnostics.

## Evidence and reproduction

[Hero](d02_corner_shop_01-evidence/hero.png), [side/rear](d02_corner_shop_01-evidence/side.png),
[entry detail](d02_corner_shop_01-evidence/detail.png),
[47 m / 42° overhead](d02_corner_shop_01-evidence/overhead_47m_42deg.png).
All are isolated Blender Cycles CPU / AgX renders of the shell and actual reused
hardware, 1280×720, 32 samples, PNG compression 95 followed by RGB seven-bit
compaction and PNG level 9. The overhead is true vertical-down perspective at
Blender `(0,0,47)`, 42° vertical FOV and fixed yaw; not a tilted view or engine capture.

Self-inspected all four final views. The broad trapezoid and curved blue roof lip
survive overhead while door/fascia details disappear beneath the roof, as expected.
The hero reads as a small ordinary shop, not a luminous civic landmark. Rear wall
is intentionally blank for the optional annex. Initial side-render plinth coplanarity
was corrected with a shallow outward trim offset, structural panel seams were removed
using a single Boolean-cut wall, and side/hero framing was widened to include the
roof. No final clipped overview or visible side-wall z-fighting remains. Studio views
do not establish populated blue-hour gameplay readability or road/garden placement.

Exact reproduction from worktree root (fresh output for production checks):

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T='tools/asset_production/d02_corner_shop_01'
S='art/source/models/environment/d02_corner_shop_01/d02_corner_shop_01.blend'
TMP='C:/tmp/ft/assets/d02_corner_shop_01'
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
mkdir -p "$TMP"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 "$S" --python-exit-code 1 --python "$T/export.py" -- "$TMP/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$TMP/reexport/d02_corner_shop_01.glb"
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

No byte-identical `.blend` regeneration is claimed; the saved-source GLB reexport is
strict. [manifest.json](d02_corner_shop_01-evidence/manifest.json) hashes every produced
source/export/import/prefab/tool/doc/evidence file, excluding itself only.

## Remaining acceptance

- Independent art/source/prefab review; no blanket READY or register/TODO closure.
- Optional rear annex [d02_corner_shop.02](d02_corner_shop_02.md) delivered its own
  source/export/prefab candidate on 10 October 2026. Its root at `(0,0,6.3)` mates
  with the rear interface above; independent review and district placement remain pending.
- Neighbourhood fascia artwork remains separate; blank shared fascia is intentional.
- World placement at the proposed triangular junction, road/garden relationship,
  real actor corner circulation, car impacts/turning, populated blue-hour gameplay
  camera/occlusion, real multiplayer transport/admission/prediction, packaging and
  sustained repeated-placement/Steam Deck performance remain downstream.
- No queue, shared progress/brief, project settings, world scene or sibling asset changed.
