# d01_sports_surface.02 — Field line graphics

**Artwork, Blender carrier, export and linked prefab delivered; independent review and placement
acceptance pending.** Produced by the commissioned isolated asset-production worker on
`lane/a-d01`, 10 October 2026. Regner owns design selection; the production supervisor owns
independent review and integration. The [commission](commission.md) and current production
instructions supersede the concept-only status of the [family brief](../d01_sports_surface.md).

## Design and provisional dimensions

Original warm-ivory field lines on transparent ground: one broad rectangular boundary, halfway
line, centre circle/spot and two nested pairs of end boxes. This is a **non-regulation,
football-inspired campus graphic**, not a sports-rules implementation. No goals, nets, equipment,
logos, advertising, yard numbers, extra pitch colours, distressing or fine stadium detail. More
than 96% of the carrier remains unpainted, preserving Northpoint's large quiet green shape.

References inspected: [Northpoint revision 04](../../concepts/districts-v1/01-northpoint-v04.png),
[current district record](../../concepts/districts-v1/northpoint.md),
[approved identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and the delivered
[crescent pavilion](d01_sports_pavilion_01.md) and [oval track](d01_sports_surface_01.md), including
their evidence. Warm ivory `#F6F1DC` matches the track. Reuse
[shared short grass](city_ground_finishes_04.md) on the supporting world surface; this asset does
not paint a replacement green rectangle or duplicate that material/texture.

All dimensions below are **provisional authored choices** under the standing dimension rule,
not regulation dimensions, measurements inferred from generated imagery or an approved plot fit.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Carrier size X / Y / Z | 52 / 0 / 26, single-sided horizontal artwork |
| Carrier AABB minimum / maximum | (-26, .015, -13) / (26, .015, 13) |
| Painted boundary centre lines | 50 × 24; X=±25, Z=±12 |
| All line widths | .18, including boundary, halfway, circle and boxes |
| Centre circle / spot | Radius 3.5 / .15, centred at (0,0) in plan |
| Outer end boxes | 6 deep × 12 wide; inner edges X=±19, sides Z=±6 |
| Inner end boxes | 2 deep × 6 wide; inner edges X=±23, sides Z=±3 |
| Pivot / supporting ground | (0,0,0), plot centre projected onto external terrain |
| Paint plane | Y=.015, matching track's intentional 15 mm anti-z-fighting lift |
| Bounds / UV tolerance | .001 m / .000001 UV units |

Long axis X; +X east, -Z north, +Z south. Blender +Y maps to Godot -Z and Blender +Z to Godot +Y.
Roots and mesh objects have identity transforms and metre units. No hidden scaling or corrective
rotation is required. Align field and oval origins/yaw over the same flat ground: the track's
open stadium has arc centres X=±17.5 and radius 15.9. **All four carrier corners fit inside that
rounded opening with a minimum .367775 m clearance**; convexity ensures the whole carrier fits,
not merely its bounding box. Paint has additional transparent margin. This is geometric family
compatibility, not a saved world placement or a new placement socket/API.

Neither earlier sibling's current handoff lists a pending asset item this delivery resolves;
both sibling documents and their manifests remain unchanged.

## Source, artwork, export and material

- Source: `art/source/models/environment/d01_sports_surface_02/d01_sports_surface_02.blend`.
- Collection `export_d01_sports_surface_02`; root `D01SportsSurface02`; child
  `D01SportsSurface02_Mesh`; mesh data `D01SportsSurface02_Geometry`.
- Export: `art/models/environment/d01_sports_surface_02/d01_sports_surface_02.glb` plus `.import`.
- Texture: `art/textures/environment/d01_sports_surface_02/field_lines_albedo.png` plus `.import`.
- Material: `art/materials/environment/d01_sports_surface_02/field_lines.tres`.
- Prefab: `scenes/prefabs/environment/d01_sports_surface_02.tscn`.
- Parametric construction/artwork, export and checks: `tools/asset_production/d01_sports_surface_02/`.

Original Blender construction and reproducible Python/Pillow artwork only. No external fonts,
downloads, purchased/generated-source models, image-to-mesh or real brands. `artwork.py` draws
metre-space strokes at 4× supersampling, then downsamples with Lanczos; `author.py` builds the
editable single-quad paint carrier. No existing field-face hardware was available: the oval ring
has no centre faces, and the shared 4 m grass swatch is a material-review sample, expressly not a
world floor module. Neither is duplicated or stretched to create this carrier.

One Principled slot, `field_lines`, roughness .94, metallic 0, no emission or normal map. Source
links the committed PNG by a **relative unpacked path**, including its alpha channel. Export
briefly disconnects image color/alpha and restores both afterwards: **zero embedded GLB images**.
Godot's saved import remaps the slot to the external material. No runtime scripts, copied mesh,
editable imported-child overrides, rigs, animation, sockets or alternate states.

Texture: **2048 × 1024 RGBA8**, sRGB ivory RGB with straight linear alpha coverage. UV0 is one
52 × 26 m atlas, **39.384615 texels/metre**; Blender U=(X+26)/52, V=(Y+13)/26. Exported image
coordinates run east/+X and south/+Z. Transparent border surrounds the centred field. Uniform
ivory RGB remains even in transparent pixels to avoid dark filtering fringes. The atlas is not a
generic tiling material or road-tool input. Use matching metre-space UVs on any other carrier.

Godot uses backface culling, **alpha scissor .5**, lossless texture import, linear mip filtering,
clamp, full generated mip chain with **alpha-test coverage preservation at .5**, and disabled
automatic 3D compression conversion. Alpha testing avoids blending/sorting an opaque-looking lawn
rectangle; only paint writes depth. No alpha-to-coverage/MSAA assumption or global renderer setting
is introduced. Blender evidence uses the Principled alpha input, not an engine shader capture;
engine aliasing, distant mip behaviour and grazing-angle depth still need visual review.
The imported RGBA8 CPU image payload including mips is **11,184,812 bytes**; this is not a measured
GPU allocation or approved budget. The 1,352 m² quad incurs alpha-test work even where clear;
repeated-placement overdraw/packaging/device profiling remains pending.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; shared
`tools/assets/blender/export_settings.json`, named collection filtering, static animations/skins
disabled. Godot **4.8.dev7.official.c971f93e7**, unit-scale import and default generated LOD/shadow
meshes. Two triangles require no manual LOD asset; no performance budget is claimed accepted.

## Prefab, supporting ground and collision

`Visuals/Model` is an identity-transform linked GLB instance. **No collider, physics body,
terrain floor, navigation or interaction node** is added: this is the standing flush-face
exception, with no thickness, slab, curb, fence or equipment. The world surface owns continuous
actor/car collision at Y=0 and carries the shared short-grass material. Keep its existing 4 m
repeat UV density rather than stretching the grass across the field. Do not use the artwork
prefab as a floor or overlay a second grass-swatch collider beneath it.

Godot pads the planar mesh's AABB height by .00001 m; source/GLB vertices stay at Y=.015, within
.001 m tolerance. This visual-only delivery changes no gameplay collision or state ownership, so
new motion/network tests are not claimed. Actual terrain continuity, feet/tyres, walking routes
and plot seams remain placement acceptance.

The authorized direct-file/headless fallback was used because live sessions are prohibited and
the windowed editor is unavailable. No owner's live Blender/Godot session was accessed. The new
prefab/material were loaded, packed and saved with the pinned headless editor. **Two further fresh
save/reload passes preserved exact bytes, node identities and UIDs**; two standalone runtime
processes produced identical passing receipts and resolved every dependency.

## Evidence and validation

[Hero](d01_sports_surface_02-evidence/hero.png) ·
[Side](d01_sports_surface_02-evidence/side.png) ·
[End-box detail](d01_sports_surface_02-evidence/line_detail.png) ·
[47 m / 42° overhead](d01_sports_surface_02-evidence/overhead_47m_42deg.png).
All four final images were inspected. **1280 × 720 RGB8**, PNG compression 95, each below 400 KiB;
Blender Cycles CPU, 24 samples, AgX. Hero/side show the complete quiet layout; detail shows clean
line joins and the shared grass visible through the clear face. The actual shared grass PNG is
used read-only on unexported studio ground, not copied or exported into a new grass asset.

Overhead is true vertical-down perspective at Blender **(0,0,47)**, north-up, **42° vertical FOV**;
the whole field fits its approximately 64.1 × 36.1 m coverage. Boundary, centre circle and paired
boxes remain distinct. Other views are orthographic evidence, not gameplay framing. These are
isolated Blender observations, not populated Godot lighting/actor or moving-camera acceptance.

[validation.json](d01_sports_surface_02-evidence/validation.json) consolidates actual source/export,
artwork and engine receipts. [manifest.json](d01_sports_surface_02-evidence/manifest.json) hashes
every delivered payload except itself; [final.log](d01_sports_surface_02-evidence/final.log) retains
concise checks and the normalization diagnostics.

- **2 triangles; 4 source/export vertices; one mesh; one surface.**
- Zero source degenerate faces/export degenerate triangles; unit-length upward normals.
- **Four intentional boundary/non-manifold edges**, one closed perimeter on a single-sided
  flush face. Zero non-boundary non-manifold edges; no studio geometry in the export.
- Final GLB **1,380 bytes**, SHA-256
  `49a1d57ddfe85a098a8a21c868b2ab7afaaf4a401dc633d872a293ea3bc2f1bd`;
  fresh saved-source export is byte-identical.
- Final PNG **25,756 bytes**, SHA-256
  `0f91f255a53deea59f0b31e965e80f0dc8605001bc721adfb00b723d3dc012b2`;
  fresh Pillow reproduction is byte-identical. Independent checks cover 16 painted and 11 clear
  landmarks, transparent borders, uniform ivory RGB, two transverse boundary runs and **3.475475%**
  painted coverage at half alpha. The remaining **96.524525%** stays clear.
- Final pinned import and two fresh runtime checks exit 0 with **no ERROR/SCRIPT ERROR lines**.
- Two scene/material roundtrips preserve bytes and UIDs. Editor normalization exits 0 but emits
  the toolkit's existing version warning, scan-abort and RID/ObjectDB shutdown leaks. Diagnostics
  are retained and **not presented as a clean editor-log pass**.
- Owned Python syntax checks and GDScript format/zero-warning lint pass. No failing asset checks
  required correction; the formatter normalized the newly authored check before lint.
- No `production_checks.py` invocation (decision 52). No shared brief, registry, world, sibling,
  project setting, gameplay code or TODO changes. No final whole-game readiness claim.

## Exact reproduction

From repository root in Bash; Python 3 with **Pillow 12.3.0**, pinned Blender/Godot only. All engine
calls are bounded and scratch files remain outside the checkout. `export.py` accepts an optional
output directory after `--` when run against the saved source. Existing import UIDs/remapping and
mipmap settings must be retained. `record.py` runs last after handoff edits and all final checks.

```bash
export PYTHONIOENCODING=utf-8
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d01_sports_surface_02
S=C:/tmp/ft/assets/d01_sports_surface_02
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

Independent technical/art review; owner acceptance of provisional field proportions and plot fit;
saved world placement over continuous collision-bearing shared grass, preserving walking routes;
populated Godot lighting, actor contrast, alpha-edge/mip motion and grazing depth review; real
foot/car contacts; imported LOD, packaged builds, world multiplayer integration and sustained
Deck/performance checks. Sports mechanics and equipment are outside this artwork delivery.
