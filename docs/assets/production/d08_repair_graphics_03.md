# d08_repair_graphics.03 — Service-warning face

10 October 2026. **Artwork/material/linked-prefab candidate delivered; independent review and
world/gameplay/device acceptance pending.** Producer: assigned lane worker, `lane/a-d08g`.
Authority: current per-record task and [production commission](commission.md), superseding the
historical concept-only restriction. Family: [repair graphics](../d08_repair_graphics.md).

## Design and provenance

**SERVICE AREA / MIND THE FIXES**: a broad dark warning triangle, ivory inset and separated
exclamation bar/dot beside two-line service copy. The `service_warning_patched` finish repaints
the lower joke strip in uneven ivory/old paint, retaining the same wording and warning symbol.
Both finishes use sparse chipped edges and sun-faded amber. Wear is explicitly drawn broad
shapes, not random noise, grime or dense scratches. Copy and colour remain **provisional
producer choices**, not final owner selection or a real-world safety-sign specification.

The palette, original rounded path lettering, two short cyan service strokes and lower copy
strip match the already-delivered [repair fascia .01](d08_repair_graphics_01.md) and
[depot panel .02](d08_repair_graphics_02.md), read and visually inspected before authoring.
The warm practical Ironreach identity remains less electric than Signal Row: no emission,
light nodes, neon rims, magenta flood or animation. This is optional service-frontage dressing,
not an essential hazard communication system, shop interaction, repair economy or navigation rule.

Original Python/Pillow construction, 3x supersampling followed by one Lanczos downsample.
No external fonts, downloaded art, real brands or generated meshes. The project-owned canvas,
palette and lettering are reused read-only from `.01/author.py`, tracing to the original
`d06_commercial_graphics_02/author.py` and `.01/author.py` letter skeletons. This record adds
original M/V glyphs, triangle/exclamation, layout and wear shapes; no Signal Row image is copied.
Python **3.14.2**, Pillow **12.3.0**. The current Ironreach revision-02 image was inspected for
context, not measured or used as production pixels. The selected irregular 5.81 ha district,
its working streets, repair courts, two-exit routes and boundary remain unchanged.

| Palette role | sRGB |
| --- | --- |
| Dark paint / lettering | `#263F43` |
| Sun-faded amber field | `#DCAE66` |
| Ivory warning inset / original copy | `#E9DFC1` |
| Restrained cyan service strokes | `#78ACA9` |
| Exposed old paint | `#B6A77E` |
| Repaint patch | `#DCCDA5` |

## Source, exports and material interface

**Hardware reuse exception:** family revision 02 selects the shared wall and low-panel hardware.
This wall-mounted warning uses `city_sign_supports.01`, as does the repair fascia. The standing
reuse rule prohibits a duplicate Blender/GLB carrier: no redundant per-ID `.blend`, GLB or
export script is delivered. The complete unchanged original source chain is:

- `art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend`
- Collection `export_city_sign_supports_01`, root `CitySignSupports01`, 12 mesh children.
- `art/models/environment/city_sign_supports_01/city_sign_supports_01.glb` and `.import`.
- `scenes/prefabs/environment/city_sign_supports_01.tscn`.
- [Hardware interface](city_sign_supports_01.md) / [prefab conventions](batch_01-integration.md).

`tools/asset_production/d08_repair_graphics_03/validate.py` reuses the existing wall-art audit,
which runs the hardware owner's saved-source validation/export and independent actual GLB
accessor decoder. Only scratch output destinations are redirected; original assertions and
shared `tools/assets/blender/export_settings.json` remain intact. No source, export, import,
base prefab or shared helper changes occur. Dependency hashes protect their final bytes.

Owned recipe: `tools/asset_production/d08_repair_graphics_03/author.py`.
Each of `service_warning` and `service_warning_patched` maps to:

- `art/textures/environment/d08_repair_graphics_03/<variant>_albedo.png` plus `.import`.
- `art/materials/environment/d08_repair_graphics_03/<variant>.tres`.

Textures: **1220 x 820 RGB**, opaque sRGB albedo, **61:41** aspect, UV0, no other maps or
embedded images. Materials: white multiplier, roughness **0.82**, metallic **0**, no emission,
backface culling, linear mipmapped filtering (engine default enum 3), clamp/no repeat,
identity UV scale/offset. Lossless imports with actual imported mipmaps enabled and automatic
3D compression changes disabled. Only front slot 0 `sign_face` changes; the carrier's rear/side
slot 1 `mount_metal`, frame, gasket, mounts and all other hardware materials remain original.

| Inherited measurement | Contract |
| --- | --- |
| Whole Godot X/Y/Z size | **1.400 x 1.000 x 0.100 m** |
| Godot AABB | min **(-0.700,-0.500,-0.100)**; max **(0.700,0.500,0)** m |
| Pivot | Wall-contact centre **(0,0,0)**; intentional non-ground exception |
| Artwork face | **1.220 x 0.820 m**, Godot **Z=-0.088 m**, corner radius **0.040 m** |
| Safe copy rectangle | Centred **1.140 x 0.740 m**; all primary copy and warning inside |
| UV orientation | U toward Blender -X, V toward +Z; top-left-origin PNG upright/unmirrored |
| Tolerances | Engine bounds **+/-0.001 m**; source/GLB coordinates **+/-0.000001 m** |
| Proposed mounting | Wall-contact centre **1.60 m** above ground, inherited proposal |

These are inherited **provisional authored dimensions**, not new placement approval. Blender
+Y/+Z maps to Godot -Z/+Y once, without corrective rotation, scaling, face tilt or billboarding.
Rig, clips, sockets, damage states and new LODs are not applicable. Existing hardware import
LOD settings remain unchanged; no cost budget or simplification improvement is claimed.

## Saved prefabs, collision and identities

- `scenes/prefabs/environment/d08_repair_graphics_03.tscn` — faded original.
- `scenes/prefabs/environment/d08_repair_graphics_03_patched.tscn` — uneven lower repaint.

Both inherit the unchanged wall-panel prefab. `Visuals/Model` remains the identity-transform
linked GLB instance. Exactly one saved override per variant:

`Visuals/Model/CitySignSupports01/artwork_carrier:surface_material_override/0`

This uses the **narrow saved editable-child face-slot exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement): static non-identity-sensitive
artwork, unchanged linked geometry, no copied meshes. The owned checker reuses the family's
hierarchy, face-slot and normalization helpers. Initial normalization plus **two byte-stable
load/pack/save cycles per variant**, including materials, prove unchanged serialized node
identities, inheritance paths and UIDs. Final scene/material hashes are in validation.json
and checked against actual payloads by the manifest tool. All transforms, child names/classes,
12 mesh resources, 13 surfaces and the one front-face override are asserted.

This is a shallow wall-mounted face, **visual-only**, not a freestanding obstacle. Mount the
complete prefab once on an opaque blocking facade; the facade owns collision. Do not stack it
over an existing carrier or use it as a standalone ground sign. Keep its **0.10 m** projection
away from passage clearances and place it where a service warning makes sense. No collision,
movement, navigation, authoritative state or multiplayer behavior is added or modified.

The task prohibits live editor sessions and the windowed editor is unavailable. Resources
were text-authored then loaded/packed/resaved only in isolated pinned headless Godot. No
separate open scene is claimed synchronized. Scene/material UIDs are inline, texture UIDs are
in `.import`, and the added GDScript `.uid` is retained; this pin emits no `.tscn.uid` or
`.tres.uid` sidecars here. No runtime-authored visible hierarchy or geometry.

## Evidence and validation

[Hero](d08_repair_graphics_03-evidence/hero.png),
[patched side](d08_repair_graphics_03-evidence/side.png),
[patched detail](d08_repair_graphics_03-evidence/detail.png),
[47 m / 42-degree overhead](d08_repair_graphics_03-evidence/overhead_47m_42deg.png).
These are isolated Blender renders, **1280 x 720**, Cycles CPU, 32 samples, AgX, PNG compression
95, dithering disabled; every image is below 250 KB. `preview.py` records exact cameras and
lighting matching the fascia evidence. Preview materials are temporary, never saved to source.

Self-inspected both runtime PNGs and all four renders. Close views show upright/unmirrored
copy, clear separation of exclamation bar/dot, clean inset seating, sparse edge chips and the
uneven repaint. Detail intentionally crops the upper panel border, not the warning or copy.
Overhead is vertical/north-up at Blender **(0,10,47)** with **42-degree vertical FOV**, panel
centre temporarily at **(0,0,1.6)**. The whole sign is roughly **27 x 6 pixels**, its vertical
face thinner: **warning symbol and wording are not reliably identifiable at gameplay height**.
It must not be the sole essential hazard/route cue. This geometric foreshortening is not fixed
by increasing texture resolution. No billboard tilt or enlarged hardware was used to fake
readability. These are not engine gameplay captures, roof-occlusion or district-lighting proof.

[validation.json](d08_repair_graphics_03-evidence/validation.json) records:

- Reused hardware: **1,380 source vertices, 1,792 GLB vertices, 2,720 triangles,
  12 meshes, 13 surfaces**. No new geometry.
- **Zero non-manifold edges, degenerate source faces and degenerate GLB triangles**;
  unit-length source/export normals, positive volume, outward winding, finite positions,
  metre units, applied transforms, wall datum, bounds, all **36** front UV samples and
  studio exclusion pass.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
  Fresh saved-source export is **byte-identical**, **75,768 bytes**, SHA-256
  `5f54105825e00bb73c038bed252910abec548ad1beb81603b2713c2c69796e0b`.
- Godot **4.8.dev7.official.c971f93e7**: complete dependencies load, unchanged hierarchy/mesh
  resources and transforms, inherited bounds, one face-only override per variant, real mipmaps,
  no added collision, four total stable scene/material roundtrip cycles pass.
- **Seven artwork tests pass**: exact PNG reproduction, independent palette/border samples,
  separated warning bar/dot, unchanged primary identity, preserved lower lettering silhouette
  under repaint, 61 x 41 front-facing warning contrast proxy, invalid-variant rejection.
  The front-facing proxy is not an overhead-readability test.
- Pinned **gdstyle 0.3.0** formatting and zero-warning lint pass for the added checker.
- Final full pinned import exits 0 with **no ERROR/SCRIPT ERROR**. Independent runtime load
  exits 0 without warning/error diagnostics. All shared dependencies remain byte-identical.

[manifest.json](d08_repair_graphics_03-evidence/manifest.json) hashes every produced payload
except itself and ignored Python caches, and records protected shared dependencies.
[final_checks.log](d08_repair_graphics_03-evidence/final_checks.log) retains concise results and
diagnostics. Scratch exports, intermediate receipts and full logs stay outside Git under
`C:/tmp/ft/assets/d08_repair_graphics_03/`.

## Exact reproduction

From the worktree root; all Blender/engine invocations are bounded:

```sh
N=d08_repair_graphics_03
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

Source validation refreshes the source/export receipt. After intentional reproduction, merge
scratch `normalized.json` as `godot_normalization` and `prefab.json` as `godot_load` into
validation.json; refresh test/check/render observations, then run
`python tools/asset_production/d08_repair_graphics_03/manifest.py --write` last. Default manifest
invocation verifies without writing. No `production_checks.py` run is required or claimed
for this unplaced asset (decision 52).

## Diagnostics and remaining acceptance

No failed authoring, geometry, export, artwork-test or lint steps occurred. Initial texture
imports used default no-mipmap settings; only owned sidecars were configured and reimported
before checks. Blender exits 0 with the existing material/world node future-deprecation warnings.

Headless editor normalization passes every assertion and byte comparison, exits 0, then emits
the existing scan-aborted warning and editor RID/ObjectDB shutdown leaks also documented by
the family. This is **not a clean editor exit claim**. Final full import has only the existing
MCP 4.8-versus-4.7 compatibility warning and no ERROR/SCRIPT ERROR. Independent non-editor load
is clean. The existing addon starts its own local listener automatically; no live-session/MCP
requests were sent, and no addon behavior was changed or suppressed.

Remaining: independent technical/art review, owner selection of provisional copy/palette,
saved wall placement and passage/vehicle/foot clearance, actual gameplay-camera/population
and roof-occlusion views, target renderer/mip behavior, repeated-placement performance,
packaged build and Deck checks. No movement, network or device acceptance is claimed.
Neither earlier sibling handoff contains a stale pending service-warning item; their docs,
manifests and historical receipts remain unchanged. The registry owns family progress.
