# d01_sports_surface.01 — Oval track finish and lane graphics

**Artwork, Blender carrier, export and linked prefab delivered; independent review and placement
acceptance pending.** Produced by the commissioned isolated asset-production worker on
`lane/a-d01`, 10 October 2026. Regner owns design selection; the production supervisor owns
independent review/integration. The [commission](commission.md) and current production instructions
supersede the concept-only status of the [family brief](../d01_sports_surface.md).

## Design and provisional dimensions

An original quiet warm oval with **six ivory lanes**, one broad finish bar and six compact
hand-drawn lane numbers. No chequerboards, logos, staggered race starts, equipment, stadium detail,
sports rules or real brands. The large green centre remains completely open: this asset paints
only the track ring, not the infield or its markings. The restrained terracotta `#AB735F` and warm
ivory `#F6F1DC` complement the slate/field-green/mint language of the delivered
[crescent pavilion](d01_sports_pavilion_01.md) and Northpoint campus.

References inspected: [current Northpoint concept](../../concepts/districts-v1/northpoint.md),
[revision 04 image](../../concepts/districts-v1/01-northpoint-v04.png),
[approved identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[selected map fit](../../concepts/districts-v1/map-context.md#district-01), and the pavilion's
current handoff/overhead evidence. All dimensions below are **provisional authored choices**,
consistent with the roughly 80 × 45 m concept context, not measurements taken from imagery,
regulation dimensions or an approved sports-plot allocation.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Outer oval size X / Y / Z | 80 / 0 / 45, single-sided artwork |
| Visual AABB minimum / maximum | (-40, .015, -22.5) / (40, .015, 22.5) |
| Pivot / supporting ground datum | (0,0,0), plot centre projected to external ground |
| Artwork elevation | Y=.015, intentional 15 mm anti-z-fighting lift above supporting ground |
| Stadium arc centres | X=-17.5 and +17.5, Z=0; 35 m straight portions |
| Outer / inner radii | 22.5 / 15.9; total artwork band 6.6 |
| Open infield bounding box X / Z | 66.8 / 31.8; **rounded ends, not a clear rectangle** |
| Curvature | 128 segments per semicircle, two straight quads |
| Boundary line centres | Seven nested radii 16.02 through 22.38, 1.06 m spacing |
| Paint width / edge margin | .14 / .12 from geometry boundary to nearest paint centre |
| Finish | X=9, south straight Z=16.02 to 22.38, .24 m stroke |
| Numerals | Six original paths, .48 × .68 m cells, .105 m stroke, immediately west of finish |
| Numeric envelope / UV tolerance | .001 m / .000001 UV units |

Long axis is X; +X east, -Z north, +Z south. Blender +Y maps to Godot -Z, Blender +Z
to Godot +Y. Roots and mesh transforms are identity, metre units. The open infield is the stadium
whose distance from the X-axis segment [-17.5,+17.5] is less than 15.9 m. Use that shape, not just
its bounding box, when fitting later artwork or ground. There is no fixed pavilion mounting socket
or placement relationship. The pavilion's current handoff contains no stale pending item resolved
by this delivery and is unchanged.

## Source, artwork, export and material

- Blender source: `art/source/models/environment/d01_sports_surface_01/d01_sports_surface_01.blend`.
- Collection `export_d01_sports_surface_01`; root `D01SportsSurface01`, mesh
  `D01SportsSurface01_Mesh`, mesh data `D01SportsSurface01_Geometry`.
- Export: `art/models/environment/d01_sports_surface_01/d01_sports_surface_01.glb` plus `.import`.
- Texture: `art/textures/environment/d01_sports_surface_01/oval_track_albedo.png` plus `.import`.
- Material: `art/materials/environment/d01_sports_surface_01/oval_track.tres`.
- Prefab: `scenes/prefabs/environment/d01_sports_surface_01.tscn`.
- Recipes/checks: `tools/asset_production/d01_sports_surface_01/`.

Original parametric Blender construction and reproducible Python/Pillow artwork only. No external
fonts, purchased/downloaded models, image-to-mesh, generated-source images or brand references.
`artwork.py` owns the drawn numeral paths and stadium strokes; `author.py` owns the editable ring.
The ring is new artwork carrier geometry; no existing sports-track carrier was available. The
shared 4 m grass swatch is not duplicated or enlarged into a second carrier.

One opaque Principled material slot: `oval_track`. Roughness .94, metallic 0, no emission, no
alpha or normal map. The source loads the committed PNG through a **relative, unpacked** image
path. Export temporarily disconnects the image and restores it afterwards; there are **zero
embedded GLB images**. Godot's saved import remaps the slot to the external material by UID,
with a fallback resource path. No imported-child override or copied mesh resource is used.

The atlas is **4096 × 2304 RGB8 sRGB**, an equal-density plan at **51.2 texels/metre**. UV0 covers
one 80 × 45 m footprint: Blender U=(X+40)/80, V=(Y+22.5)/45; exported image coordinates run east
and south. Clamp, linear mipmap filtering, generated full mip chain, lossless import, no automatic
3D compression conversion, no tiling. The opaque atlas outside the ring is unused and cannot fill
the open centre because no triangles exist there. Reusing this material on another mesh requires
the same footprint/UV mapping; it is not a generic tiled running-track texture or road-tool input.
The imported CPU image payload including mipmaps is **37,748,721 bytes** (RGB8), not a measured
GPU allocation or accepted budget. Repetition/packaging/device cost remains unprofiled.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; shared
`tools/assets/blender/export_settings.json`, explicit collection filter, animations/skins disabled.
Godot **4.8.dev7.official.c971f93e7**; unit-scale import, default generated LODs/shadow meshes.
No manual LODs, sockets, rigs, animation, alternate states, runtime scripts or sports mechanics.

## Prefab, ground and collision contract

`Visuals/Model` is an identity-transform instance of the imported GLB. The wrapper contains
**no CollisionObject3D, collider, gameplay floor, navigation or interaction nodes**. This is the
standing flush-decal exception, not a freestanding slab: there are no sidewalls, raised kerbs,
barriers, steps or deck. Supporting world terrain owns continuous actor/car collision at Y=0.
Place only over an existing flat, collision-bearing plot and retain the authored .015 m visual
lift; do not use this prefab alone as a walkable floor. Infield/world grass comes from the shared
[short-grass material](city_ground_finishes_04.md), not a ground mesh delivered here.

Godot gives the planar imported mesh a conservative .00001 m AABB thickness; the source/GLB
positions all remain at Y=.015. The checker permits that engine padding within the .001 m bound.
No collision changes or gameplay ownership transitions occur, so no new motion/network test is
claimed. Actual placement still needs ground continuity, seam, tyre/foot contact and depth review.

The authorized direct-file/headless fallback was used; no owner's live Blender/Godot session was
accessed. The prefab and external material were loaded/packed/saved with the pinned headless editor.
**Two fresh save/reload passes after initial normalization preserve exact bytes, node identities
and UIDs.** A subsequent import retains engine-normalized sidecars and two fresh runtime processes
load the prefab with identical passing receipts and no missing dependencies.

## Evidence and validation

[Hero](d01_sports_surface_01-evidence/hero.png) ·
[Side](d01_sports_surface_01-evidence/side.png) ·
[Finish detail](d01_sports_surface_01-evidence/finish_detail.png) ·
[47 m / 42° overhead](d01_sports_surface_01-evidence/overhead_47m_42deg.png).
All four final images were inspected. Each is 1280 × 720 RGB8 PNG, compression 95, under 400 KiB;
Cycles CPU, 24 samples, AgX, no post-processing. Studio green is an unexported flat backdrop, not
a second field asset or delivered grass model. Hero/side show the whole smooth oval with a quiet
open centre; detail verifies six distinct numbers and one finish bar. Broad lane boundaries and
numbers remain distinguishable in the calibrated overhead.

The gameplay reference is true vertical-down perspective at Blender **(9,-18,47)**, north-up,
**42° vertical FOV**. Its approximately 64.1 × 36.1 m coverage intentionally shows the south
finish and curve, **not the entire 80 × 45 m oval**. Hero is an orthographic whole-asset overview,
not a falsely labelled gameplay camera. These are isolated Blender observations, not populated
Godot lighting, moving-camera shimmer or actor visibility acceptance.

[validation.json](d01_sports_surface_01-evidence/validation.json) records source, exported accessors,
PNG checks, engine receipts, rendering and diagnostics. [manifest.json](d01_sports_surface_01-evidence/manifest.json)
hashes every delivered payload except itself; [final.log](d01_sports_surface_01-evidence/final.log)
retains concise command outcomes and normalization diagnostics.

- **516 triangles, 516 source/export vertices, one mesh, one surface.**
- Zero source degenerate faces and GLB degenerate triangles; unit-length upward normals.
- **516 intentional boundary/non-manifold edges**, exactly two closed 258-edge perimeters on the
  open decal. **Zero non-boundary non-manifold edges.** No loose branches, unclosed perimeter
  ends, exported studio geometry or triangles filling the infield.
- Final GLB: **20,880 bytes**, SHA-256
  `6b05673596b4af2f4591a3cac8c1371dd4e4d3c67149d1e6e3ed0903a7f856e8`;
  saved-source fresh re-export byte-identical.
- Final PNG: **724,108 bytes**, SHA-256
  `9dd59aa09d557ccae25adcb194ef9fd4a50d080a8fdf31e6ed6be05b710b18f9`;
  fresh Pillow reproduction byte-identical. Independent pixel checks find seven separated
  ivory boundary runs, even spacing, six numeral regions, south-only finish and quiet solid fill.
- Final import and two fresh runtime checks exit 0 with **no ERROR/SCRIPT ERROR lines**.
- Two prefab/material roundtrips preserve bytes and UIDs. Editor normalization exits 0 but reports
  the toolkit's version warning, scan-abort and RID/ObjectDB shutdown leaks. These diagnostics
  are retained, **not presented as a clean editor-log pass**.
- Initial checker compared the engine's display string to CLI version formatting; corrected to
  separately validate display version and commit hash. Initial bounded-await lint annotation
  used incorrect directive syntax; final format and zero-warning lint pass. Pillow's initial
  deprecated pixel iterator was replaced before final checks.
- No `production_checks.py` invocation (decision 52). No world, registry, shared brief or sibling
  paths changed; no completed TODO or final gameplay/device acceptance claimed.

## Exact reproduction

From the repository root in Bash; Python 3 with **Pillow 12.3.0**. Use the pinned tools only.
All engine calls are bounded, scratch stays outside the checkout. `validate.py` opens the saved
source and re-exports to scratch before comparing bytes. `export.py` also accepts a directory
following `--` when run against that saved source. Keep existing import/scene identities.
`record.py` runs last, after checks and handoff changes, so receipt hashes describe final bytes.

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d01_sports_surface_01
S=C:/tmp/ft/assets/d01_sports_surface_01
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
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" \
  > "$S/prefab-check.log" 2>&1
cp "$S/prefab-check.json" "$S/prefab-first-process.json"
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" \
  > "$S/prefab-second-process.log" 2>&1
cmp "$S/prefab-first-process.json" "$S/prefab-check.json"
python "$T/record.py"
```

## Remaining acceptance

Independent technical/art review; owner acceptance of provisional size/lane count and sports-plot
fit; saved world placement over continuous flat ground, with a readable open field and perimeter
walking routes; populated Godot lighting, actor contrast, depth separation and moving-camera mip
review; actual foot/car approach and contact observations; imported LOD, packaged-platform,
multiplayer-world integration and sustained Deck/performance checks. The artwork supplies no
sports mechanics and this handoff does not claim whole-city or gameplay readiness.
