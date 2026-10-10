# d01_sports_surface.03 — Small court graphics

**Artwork, Blender carrier, export and linked prefab delivered; independent review and placement
acceptance pending.** Produced by the commissioned isolated asset-production worker on
`lane/a-d01`, 10 October 2026. Regner owns design selection; the production supervisor owns
independent review/integration. The [commission](commission.md) and current production instructions
supersede the concept-only status of the [family brief](../d01_sports_surface.md). Small courts
remain a **candidate district use**, not a restored allocation within the university plot.

## Design and provisional dimensions

Original, non-regulation racket-court-inspired artwork: broad warm-ivory boundary, paired long
sidelines, four central service boxes and a **painted transverse divider**, with quiet green
playing area and a darker green apron. The divider is not a net. No net, posts, hoops, equipment,
logos, lettering, sports mechanics, distressed texture or detailed stadium is supplied.

References inspected: [Northpoint revision 04](../../concepts/districts-v1/01-northpoint-v04.png),
[current district record](../../concepts/districts-v1/northpoint.md),
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[selected map fit](../../concepts/districts-v1/map-context.md#district-01).
The delivered [pavilion](d01_sports_pavilion_01.md), [oval track](d01_sports_surface_01.md) and
[field lines](d01_sports_surface_02.md), including their evidence, informed the quiet green/ivory
family treatment. Ivory `#F6F1DC` matches both earlier artwork sets; playing green `#326556` and
apron `#294E49` remain subdued. Broad paint covers **5.598395%** of the atlas; the rest stays quiet.

All dimensions below are **provisional authored choices** under the standing dimension rule,
not regulation measurements, dimensions inferred from generated imagery or accepted plot fit.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Carrier size X / Y / Z | 28 / 0 / 16, single-sided opaque finish |
| Carrier AABB minimum / maximum | (-14, .015, -8) / (14, .015, 8) |
| Painted boundary centre lines | 24 × 12; X=±12, Z=±6 |
| Apron | 2 from boundary centre to each outer edge; no raised border |
| Inner longitudinal sidelines | Z=±4.5, X=-12 to +12 |
| Service box end lines | X=±6, Z=-4.5 to +4.5 |
| Service centre line | Z=0, X=-6 to +6 |
| Painted transverse divider | X=0, Z=-6 to +6 |
| All stroke widths | .16, camera-readable rather than regulation paint |
| Pivot / supporting ground datum | (0,0,0), court centre projected to external terrain |
| Visual elevation | Y=.015, matching the family's 15 mm anti-z-fighting lift |
| Bounds / UV tolerance | .001 m / .000001 UV units |

Long axis X; +X east, -Z north, +Z south. Blender +Y maps to Godot -Z and Blender +Z to Godot +Y.
All production objects use identity transforms and metre units. This is a separate small-court
footprint, not an overlay for the field, a replacement main field, or a prescribed pavilion socket.
World integration chooses any eventual campus location without displacing the hall or consuming
walking routes by implication. None of the three earlier sibling handoffs lists a stale pending
asset item resolved here; their documents, manifests and historical receipts remain unchanged.

## Source, artwork, export and material

- Source: `art/source/models/environment/d01_sports_surface_03/d01_sports_surface_03.blend`.
- Collection `export_d01_sports_surface_03`; root `D01SportsSurface03`; child
  `D01SportsSurface03_Mesh`; mesh data `D01SportsSurface03_Geometry`.
- Export: `art/models/environment/d01_sports_surface_03/d01_sports_surface_03.glb` plus `.import`.
- Texture: `art/textures/environment/d01_sports_surface_03/small_court_albedo.png` plus `.import`.
- Material: `art/materials/environment/d01_sports_surface_03/small_court.tres`.
- Prefab: `scenes/prefabs/environment/d01_sports_surface_03.tscn`.
- Reproducible recipes/checks: `tools/asset_production/d01_sports_surface_03/`.

Original Blender construction and Python/Pillow drawing only: no downloads, external fonts,
purchased/generated-source models, image-to-mesh or real brands. `artwork.py` draws metre-space
strokes at 4× supersampling and downsamples with Lanczos; `author.py` creates the editable court
quad. No existing matching court hardware is available: the earlier field carrier is 52 × 26 m,
the oval is an open ring, and the shared grass swatch is not a world floor module. None is copied,
rescaled or given a new artwork override. The new 28 × 16 m carrier keeps this footprint authored
in Blender and the imported instance at identity; it is not a duplicate facade/panel carrier.

One Principled slot `small_court`, roughness .94, metallic 0, opaque, back-culled, no emission or
normal map. The source loads its committed PNG with a **relative unpacked path**. Export briefly
disconnects image color and restores it afterwards: **zero embedded GLB images**. Godot's saved
import maps the slot to the external material. No copied mesh, editable-child override, runtime
script, rig, animation, socket or alternate state is delivered.

Texture: **1792 × 1024 RGB8 sRGB**, **64 texels/metre**, one complete 28 × 16 m atlas. Blender
UV0 U=(X+14)/28, V=(Y+8)/16; exported image coordinates run east/+X and south/+Z. Opaque color
includes both the playing area and apron: this intentionally paints a court finish, unlike the
transparent field-line sibling. No transparency, alpha testing or sorting is required. Clamp,
linear mipmap filtering, full generated mip chain, lossless import and disabled automatic 3D
compression conversion. Not a generic tiled finish or road-tool input; another carrier must use
the same metre-space UV mapping. No material/texture from another asset is duplicated.

Imported RGB8 CPU image payload including mipmaps: **7,340,025 bytes**. This is not measured GPU
allocation or an accepted performance budget. Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF
exporter **5.2.40**; shared `tools/assets/blender/export_settings.json`, named-collection filter,
animations/skins disabled. Godot **4.8.dev7.official.c971f93e7**, unit-scale import and default
LOD/shadow meshes. Two triangles require no manual LOD asset; repetition/device cost is unprofiled.

## Prefab, ground and collision contract

`Visuals/Model` is an identity-transform linked GLB instance. **No CollisionObject3D, collider,
terrain floor, navigation or interaction node** is added. The standing flush-face exception
applies: there are no sidewalls, raised kerbs, rails, steps, deck or equipment. World terrain owns
continuous actor/car collision at Y=0. Place only over an existing flat collision-bearing plot;
do not treat this artwork prefab as a floor. Preserve the .015 m visual lift and review feet,
tyres and seams when placed. The dark apron is paint, not a physical barrier or approved runoff.

Godot gives the planar mesh a conservative .00001 m AABB thickness; source/GLB positions remain at
Y=.015 within the .001 m tolerance. No gameplay collision or state ownership changes occur, so no
new motion/network test is claimed. Supporting ground continuity remains world acceptance.

Direct-file/headless fallback was used because live sessions are prohibited and the windowed
editor is unavailable. No owner's live Blender/Godot session was touched. Pinned headless
load/pack/save normalized the new material/prefab; **two further fresh save/reload passes preserve
exact bytes, UIDs and node identities**. Two standalone runtime processes load the linked
resources and produce identical passing receipts, with no missing dependencies.

## Evidence and validation

[Hero](d01_sports_surface_03-evidence/hero.png) ·
[Side](d01_sports_surface_03-evidence/side.png) ·
[Line detail](d01_sports_surface_03-evidence/line_detail.png) ·
[47 m / 42° overhead](d01_sports_surface_03-evidence/overhead_47m_42deg.png).
All four final renders were inspected: **1280 × 720 RGB8 PNG**, compression 95, each below 400 KiB,
Cycles CPU 24 samples, AgX. Hero/side show the complete court/apron; detail shows broad clean
junctions without surface noise. The actual shared short-grass PNG is read-only on unexported
studio ground; it is not copied into the court asset or exported as geometry.

Overhead uses true vertical-down perspective at Blender **(0,0,47)**, north-up, **42° vertical FOV**.
The whole small court fits within approximately 64.1 × 36.1 m coverage. Sidelines, service boxes
and the darker apron remain distinct while the court stays a small quiet campus element. Other
views are orthographic evidence, not gameplay framing. These are isolated Blender observations,
not populated Godot lighting/actor visibility or moving-camera acceptance.

[validation.json](d01_sports_surface_03-evidence/validation.json) consolidates source/export,
artwork and engine receipts. [manifest.json](d01_sports_surface_03-evidence/manifest.json) hashes
every delivered payload except itself. [final.log](d01_sports_surface_03-evidence/final.log)
retains concise command results and exact normalization diagnostics.

- **2 triangles; 4 source/export vertices; one mesh; one surface.**
- Zero source degenerate faces/export degenerate triangles; unit-length upward normals.
- **Four intentional boundary/non-manifold edges**, one closed perimeter on a single-sided
  flush face; zero non-boundary non-manifold edges. No studio objects in the export.
- Final GLB **1,380 bytes**, SHA-256
  `6195e953d6fb6b2965399b87c0758bc41dae127774b68266916fc9ab3661376d`;
  fresh saved-source re-export byte-identical.
- Final PNG **9,283 bytes**, SHA-256
  `f957e9f993e68feaa35ade39cc1464ed7fdd4931bd8f92b524e3a8b8c8e438e2`;
  fresh Pillow reproduction byte-identical. Independent checks cover 13 paint, 7 green and
  6 apron landmarks, four separated transverse sideline runs, solid border and paint coverage.
- Final pinned import and two fresh runtime checks exit 0 with **no ERROR/SCRIPT ERROR lines**.
- Two material/prefab roundtrips preserve exact bytes and UIDs. Editor normalization exits 0 but
  emits the toolkit version warning, scan-abort and RID/ObjectDB shutdown leaks, matching the
  earlier family workflow. These are retained, **not presented as a clean editor-log pass**.
- Python syntax and GDScript formatting/zero-warning lint pass. No failed asset checks.
- No `production_checks.py` invocation (decision 52); no shared briefs, registry, project settings,
  world placement, gameplay code, TODOs or sibling files changed. No whole-game readiness claim.

## Exact reproduction

From repository root in Bash; Python 3 with **Pillow 12.3.0**, pinned Blender/Godot only. All
engine calls are bounded; scratch stays outside the checkout. `export.py` accepts an optional
output directory after `--` when run against the saved source. Retain existing import UIDs,
material remapping and mip settings. `record.py` runs last, after checks and handoff edits.

```bash
export PYTHONIOENCODING=utf-8
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d01_sports_surface_03
S=C:/tmp/ft/assets/d01_sports_surface_03
mkdir -p "$S"
python "$T/artwork.py"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py" > "$S/author.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" > "$S/validate.log" 2>&1
python "$T/check_artwork.py" > "$S/artwork-check.log" 2>&1
python -m py_compile "$T/author.py" "$T/export.py" "$T/validate.py" \
  "$T/artwork.py" "$T/check_artwork.py" "$T/record.py"
mise exec -- gdstyle fmt --check "$T/check_prefab.gd" > "$S/format.log" 2>&1
mise exec -- gdstyle --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd" \
  > "$S/style.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-remap.log" 2>&1
timeout 180 "$G" --headless --editor --path . --script "$T/check_prefab.gd" -- \
  --normalize > "$S/roundtrip.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" > "$S/prefab-check.log" 2>&1
cp "$S/prefab-check.json" "$S/prefab-first-process.json"
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" \
  > "$S/prefab-second-process.log" 2>&1
cmp "$S/prefab-first-process.json" "$S/prefab-check.json"
python "$T/record.py"
```

## Remaining acceptance

Independent technical/art review; owner acceptance of provisional motif, proportions and candidate
court use/plot fit; saved world placement over continuous collision-bearing ground preserving the
large field and walking routes; populated Godot lighting, actor contrast, moving mip/depth review;
real foot/car contacts; imported LOD, packaged builds, world multiplayer integration and sustained
Deck/performance checks. No sports mechanics, regulation facility or equipment is promised.
