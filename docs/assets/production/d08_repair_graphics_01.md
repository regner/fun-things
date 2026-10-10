# d08_repair_graphics.01 — Repair fascia art

10 October 2026. **Artwork/material/linked-prefab candidate delivered; independent review and
world/gameplay/device acceptance pending.** Producer: assigned lane worker, `lane/a-d08g`.
Authority: current per-record task and [production commission](commission.md), superseding the
historical concept-only restriction. Family: [repair graphics](../d08_repair_graphics.md).

## Design and provenance

**FIXED ENOUGH / NOISES COST EXTRA**: a large diagonal spanner in an ivory hexagonal badge,
two-line dark shop name on faded amber, two restrained cyan service strokes, and a dark lower
copy strip. The second `fixed_enough_patched` finish adds an uneven old-paint/ivory repaint over
COST EXTRA. Both retain chipped edge paint, the same shop identity and unchanged hardware.
Wear is sparse, explicitly drawn broad shapes, not random grime or fine texture noise.
Copy and colour tuning are provisional producer choices; no final naming approval is claimed.

The practical, warm, stubborn Ironreach identity remains less electric than Signal Row:
no emission, neon rim, magenta flood, real lights or animated graphics. The family revision-02
weathering instruction supplies the two finish variants, not another building/sign system.
No mechanic interaction, economy, road surface, placement or gameplay behavior is added.
The selected Ironreach map is the 5.81 ha irregular district, not the older M1 adjacency story;
its streets and repair courts are context only, not modified by this artwork delivery.

Original Python/Pillow construction, 3x supersampling then one Lanczos downsample. No external
fonts, downloaded images, real brands, generated meshes or attribution dependencies. The
project-owned smooth path canvas and letter skeletons are reused read-only from
`d06_commercial_graphics_02/author.py` and its `.01` dependency; the X glyph, spanner, layout,
paint wear and Ironreach palette are authored here. These are source-code references, not
copies of Signal Row artwork. Python 3.14.2 / Pillow 12.3.0.

| Palette role | sRGB |
| --- | --- |
| Dark paint / lettering | `#263F43` |
| Sun-faded amber field | `#DCAE66` |
| Ivory badge / original copy | `#E9DFC1` |
| Restrained cyan service strokes | `#78ACA9` |
| Exposed old paint | `#B6A77E` |
| Repaint patch | `#DCCDA5` |

## Source, exports and material interface

**Reuse exception:** the brief explicitly selects `city_sign_supports.01` wall-panel hardware.
The standing supervisor reuse rule prohibits a duplicate Blender/GLB carrier. This delivery
therefore supplies artwork/materials and two inherited prefabs, with no per-ID `.blend`, GLB
or redundant export script. The complete original source/export chain remains:

- `art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend`
- Collection `export_city_sign_supports_01`, root `CitySignSupports01`, 12 named mesh children.
- `art/models/environment/city_sign_supports_01/city_sign_supports_01.glb` and existing `.import`.
- `scenes/prefabs/environment/city_sign_supports_01.tscn`.
- [Source interface](city_sign_supports_01.md) / [accepted engine conventions](batch_01-integration.md).

All four shared resources and their geometry are unchanged. Existing hardware owner export
settings and independent binary decoder are reused by `validate.py`; fresh export writes
only to `C:/tmp/ft/assets/d08_repair_graphics_01/`. The shared explicit glTF export contract,
selection filter, Y-up conversion and studio exclusion remain intact.

Owned artwork recipe: `tools/asset_production/d08_repair_graphics_01/author.py`.
Each of `fixed_enough` and `fixed_enough_patched` maps to:

- `art/textures/environment/d08_repair_graphics_01/<variant>_albedo.png` plus `.import`.
- `art/materials/environment/d08_repair_graphics_01/<variant>.tres`.

Both PNGs are **1220 x 820 RGB**, opaque sRGB albedo, aspect **61:41**, UV0, no other maps or
embedded images. White material multiplier, roughness **0.82**, metallic **0**, no emission,
backface-culling, linear mipmapped filtering (engine default enum 3), clamp/no repeat,
identity UV scale/offset. Lossless texture imports, actual imported mipmaps enabled,
automatic detect-3D compression changes disabled. Only the existing front `sign_face` slot
is replaced; gasket, frame, mounts and carrier rear/sides keep their original materials.

| Inherited measurement | Contract |
| --- | --- |
| Whole Godot X/Y/Z size | **1.400 x 1.000 x 0.100 m** |
| Godot AABB | min **(-0.700,-0.500,-0.100)**; max **(0.700,0.500,0)** m |
| Pivot | Wall-contact centre **(0,0,0)**, deliberate non-ground exception |
| Artwork face | **1.220 x 0.820 m**, Godot **Z=-0.088 m**, 0.040 m rounded corners |
| Safe copy rectangle | Centred **1.140 x 0.740 m**; all important copy/icon inside |
| UV orientation | U toward Blender -X, V toward +Z; ordinary top-left PNG upright/unmirrored |
| Bounds tolerance | Engine +/-0.001 m; inherited source/GLB audit 0.000001 m |
| Mounting proposal | Wall-contact centre **1.60 m** above ground, inherited provisional proposal |

Although the register label is fascia art, this is the brief-selected wall-panel format,
not an invented wider fascia mesh. Mount a complete prefab once on a blocking facade;
do not stack it over another carrier or rescale it to fake camera readability. No ground
collision is added: this is a shallow wall-mounted face, and the host facade owns collision.
Keep the 0.10 m projection away from passage clearance. Rig, animation, sockets and new LODs
are not applicable. No new standalone obstacle, destructible state or navigation cue.

## Saved prefabs and identities

- `scenes/prefabs/environment/d08_repair_graphics_01.tscn` — faded original.
- `scenes/prefabs/environment/d08_repair_graphics_01_patched.tscn` — uneven repaint.

Both inherit the unchanged wall-panel prefab. `Visuals/Model` remains an identity-transform
linked GLB instance. Exactly one saved override per prefab:

`Visuals/Model/CitySignSupports01/artwork_carrier:surface_material_override/0`

This uses the **narrow saved editable-child face-slot exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement): static non-identity-sensitive
artwork on reused hardware, no copied geometry. `check_prefab.gd` reuses the existing
wall-panel slot/hierarchy checks and performs an initial normalization followed by **two
byte-stable load/pack/save cycles per variant**, including the material. Full-byte equality
protects serialized identities, inheritance paths and UIDs. The final hashes are recorded in
`validation.json` and checked again by the manifest tool. Hardware resource equality,
all node transforms/classes/counts, 12 mesh resources, 13 surfaces and one override are asserted.

The task prohibits live editor sessions and the windowed editor is unavailable. Text-authored
resources were loaded/packed/resaved only in isolated pinned headless Godot; no separately
open scene is claimed synchronized. Scene/material UIDs are inline, texture UIDs are in
`.import`, and the GDScript `.uid` is retained; the pin creates no `.tscn.uid` or `.tres.uid`.

## Evidence and validation

[Hero](d08_repair_graphics_01-evidence/hero.png),
[patched side](d08_repair_graphics_01-evidence/side.png),
[patched detail](d08_repair_graphics_01-evidence/detail.png),
[47 m / 42-degree overhead](d08_repair_graphics_01-evidence/overhead_47m_42deg.png).
These are **isolated Blender renders**, not Godot gameplay captures: 1280 x 720, Cycles CPU,
32 samples, AgX, PNG compression 95, dithering disabled to keep evidence lean. Exact cameras
and lighting are in `preview.py`; no studio mesh, source save or GLB mutation occurs.

Self-inspected both PNGs and all four final renders. Close views show upright/unmirrored
lettering, a recognizable open spanner, clean inset seating, sparse chipped edge paint and
the visibly uneven repaint. The evidence detail intentionally crops the upper panel.

Overhead is vertical/north-up, Blender camera **(0,10,47)**, **42-degree vertical FOV**, panel
centre temporarily at **(0,0,1.6)** with no billboard tilt or enlargement. The whole sign is
only roughly **27 x 6 pixels** and its face is thinner: **copy and spanner are not reliably
identifiable at gameplay height**. It supplies optional frontage colour/close-view humor,
not essential navigation. Roof occlusion and actual renderer readability remain placement
review tasks; no texture increase could remove this geometric foreshortening.

[validation.json](d08_repair_graphics_01-evidence/validation.json) records:

- Reused hardware: **1,380 source vertices, 1,792 GLB vertices, 2,720 triangles,
  12 meshes, 13 surfaces**. No new geometry.
- **Zero degenerate source faces/GLB triangles and zero non-manifold edges**;
  unit source corner/export normals, positive volume, outward winding, applied transforms,
  metre scale, all **36** front-face UV samples, axis bounds and studio exclusion pass.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**.
  Fresh saved-source export is **byte-identical**, **75,768 bytes**, SHA-256
  `5f54105825e00bb73c038bed252910abec548ad1beb81603b2713c2c69796e0b`.
- Godot **4.8.dev7.official.c971f93e7**: complete dependencies load, face-only overrides,
  unchanged mesh resources/hierarchy, inherited bounds, real mipmaps and four total stable
  scene/material roundtrip cycles pass. Independent non-editor load has no warning/error lines.
- **Five artwork tests pass**: exact PNG reproduction, independent border/badge/cyan samples,
  primary identity unchanged by repaint, front-facing 61 x 41 contrast proxy, invalid variant
  rejection. The front-facing mip proxy is explicitly not an overhead-readability test.
- Pinned **gdstyle 0.3.0** formatting and zero-warning lint pass on the added checker.
- Final pinned full import exits 0 with **no ERROR/SCRIPT ERROR**. Its existing addon-version
  warning is recorded, not suppressed. Shared dependencies remain byte-identical.

[manifest.json](d08_repair_graphics_01-evidence/manifest.json) hashes every produced payload
except itself and ignored Python caches. [final_checks.log](d08_repair_graphics_01-evidence/final_checks.log)
retains concise results/diagnostics. Scratch exports, intermediate receipts and full logs are
outside Git under `C:/tmp/ft/assets/d08_repair_graphics_01/`.

## Exact reproduction

From the worktree root (all engine/Blender invocations are bounded):

```sh
N=d08_repair_graphics_01
S=C:/tmp/ft/assets/$N
mkdir -p "$S"
export PYTHONIOENCODING=utf-8
python tools/asset_production/$N/author.py
python -m unittest discover -s tools/asset_production/$N -p 'test_*.py' -v
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/validate.py
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/preview.py
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/$N/check_prefab.gd -- --normalize
cp "$S/prefab.json" "$S/normalized.json"
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --path . \
  --script res://tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" fmt --check tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/$N/check_prefab.gd
```

The source validator refreshes the source/export receipt. After intentional reproduction,
merge scratch `normalized.json` as `godot_normalization` and `prefab.json` as `godot_load`
into validation.json before `python tools/asset_production/$N/manifest.py --write`.
Default manifest invocation verifies without writing. The accepted wall-art audit redirects
only legacy decoder output to scratch; all original source/export/binary assertions remain.
No `production_checks.py` run is claimed or required for this unplaced asset (decision 52).

## Diagnostics and remaining acceptance

One initial lint warning (11 locals) was resolved by separating resource normalization into
its own named helper; final lint/format pass. Initial renders were larger than the evidence
target; disabling render dithering retained the design and reduced every render below 400 KB.
Blender emits the known material/world node future-deprecation warnings and exits 0.

Headless editor normalization passes all assertions and exits 0, but its early shutdown
reports the existing scan-aborted warning and editor RID/ObjectDB leaks, as in the accepted
wall-art precedent. These are not called a clean editor exit. Final full import has only the
existing MCP 4.8-versus-4.7 compatibility warning, no ERROR/SCRIPT ERROR; independent runtime
load is clean. The project's existing addon starts its own local listener automatically;
no MCP/live-session requests were sent.

Remaining: independent technical/art review, owner selection of provisional copy/palette,
saved world placement with facade/route clearance and roof-occlusion review, actual gameplay
camera/population views, target renderer/mip behavior, repeated-placement performance,
packaged build and Deck checks. No gameplay collision/network behavior changed; no movement,
network or device acceptance is claimed. The registry owns other family deliveries; this
handoff does not enumerate unproduced siblings as pending work.
