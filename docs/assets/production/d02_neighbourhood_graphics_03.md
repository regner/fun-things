# d02_neighbourhood_graphics.03 — Corner-shop fascia art

**Artwork/material/linked-prefab candidate delivered; independent review and world acceptance
pending.** Producer: assigned implementation worker on `lane/a-d02g`. Commission:
[production commission](commission.md), current per-ID assignment and standing reuse rules.
Family: [Neighbourhood notice graphics](../d02_neighbourhood_graphics.md). Earlier siblings:
[watch notice](d02_neighbourhood_graphics_01.md) and
[parking request](d02_neighbourhood_graphics_02.md). Neither current handoff lists this fascia
as a pending delivery, so no sibling doc, manifest or historical receipt was changed.

## Design, provenance and scope

Provisional original fictional copy: **CORNER CUPBOARD / MILK. BREAD. LOCAL OPINIONS.**
One shopping bag with a bottle and loaf marks an ordinary local grocery; the neighbours'
unsolicited opinions supply the domestic joke. This is decoration, not a navigation cue,
shop interaction or gameplay inventory. Final copy/name selection remains owner-reviewed.

The family language is unchanged: warm ivory `#F6F1DC`, quiet blue `#526D86`, muted plum
`#635168`, one fine border, broad whitespace and smooth rounded-path lettering. More than
75% of the face is unprinted ivory. No neon, emission, official seals, real brands, downloaded
images, external fonts or generated image source. This is deliberately quieter than Signal
Row's commercial artwork. The original bag/groceries, composition and copy are owned here;
`author.py` reuses the watch notice's palette and project-owned path canvas/letter skeletons
from `d06_commercial_graphics_01/author.py` and `d06_commercial_graphics_02/author.py`.
An original K skeleton is added locally. Reuse changes only in-memory module data, never
sibling files. Python 3.14.2 / Pillow 12.3.0; 3× supersampling with one filtered reduction.
The committed Python recipe is the editable 2D source; there is no external rights dependency.

References inspected: accepted Petrol & Coral direction, approved stage-03 Crescents identity,
[The Crescents revision 02](../../concepts/districts-v1/the-crescents.md), map context and
stage-04 street hierarchy. No dimensions inferred from concept imagery. No world/sector,
road, gameplay, movement, collision, navigation or multiplayer code/data changed.

## Shared source, outputs and measured interface

**No duplicate Blender source, GLB, panel or coplanar decal mesh.** Under the standing reuse
rule, the existing accepted flat fascia supplies the required Blender-sourced face:

- Source: `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`.
- Collection/root: `export_city_shop_fittings_02` / `city_shop_fittings_02`.
- Export: `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb`.
- Base prefab: `scenes/prefabs/environment/city_shop_fittings_02.tscn`.
- Contracts: [fascia handoff](city_shop_fittings_02.md),
  [accepted integration conventions](batch_03-integration.md).

New outputs:

- Tools: `tools/asset_production/d02_neighbourhood_graphics_03/`.
- Runtime: `art/textures/environment/d02_neighbourhood_graphics_03/corner_cupboard_albedo.png`
  plus engine-normalized `.import`.
- Material: `art/materials/environment/d02_neighbourhood_graphics_03/corner_cupboard.tres`.
- Prefab: `scenes/prefabs/environment/d02_neighbourhood_graphics_03.tscn`.

`family_tools.py` retargets the existing watch-notice export/audit/finalization/inventory tools
in memory, with exact-match guards for the fascia-specific interface changes. `preview.py`
uses the existing hall-title fascia studio with this artwork, roughness and lean-render
settings. The owner's existing exporter and independent binary decoder supply all actual
geometry assertions; no exporter/geometry-validator copy or shared-file mutation. The
existing hardware export options are unchanged, preserving its accepted shared export
contract. All reused tools/source/model/import/prefab dependencies are hashed before/after
validation and checked again at finalization. Future dependency changes require rerunning
this asset's checks.

| Quantity | Inherited measurement / convention |
| --- | --- |
| Whole fascia Godot X/Y/Z | **3.200 / 0.800 / 0.140 m** |
| Godot AABB | min **(-1.600, -0.400, -0.140)**; max **(1.600, 0.400, 0)** |
| Pivot | Wall-contact centre **(0,0,0)**, not a ground origin |
| Front/up | Blender +Y/+Z → Godot -Z/+Y |
| Artwork face | **3.000 × 0.600 m**, Godot Z = **-0.128 m** |
| Safe content | Centred **2.940 × 0.540 m** |
| Aspect / texture density | **5:1**, about **666.7 texels/m** in both face axes |
| Bounds tolerance | Source/export **0.000001 m**; engine **0.001 m** |
| Suggested centre height | **3.800 m**, inherited provisional mounting proposal |

All source/export transforms and imported `Visuals/Model` remain identity. No corrective
scale, rotation, UV transform or replacement geometry. Face UV0 grows toward Blender -X
and +Z, with glTF flipped V storage; front-view screen-right is local -X. Copy reads upright
and unmirrored. The outer 20 texels remain uninterrupted ivory for safe rounded-face bleed.
Use one flat mounting bay at least 3.4 m wide, not wrapped around the wedge shop's corner;
the fascia is not a curved/corner carrier. Preserve the hardware's 0.10 m adjacent-fitting
gap and reserved installation volume. Actual shell placement is downstream.

## Material, saved prefab and collision

**2000 × 400 RGB**, opaque sRGB albedo, **59,790 bytes**; final texture SHA-256:
`5081ea1177e4ae2b20ad6b937f04e669d84e45ba518467103a6fcd2387b3c429`.
White multiplier, roughness **0.8**, metallic **0**, backface culling; no alpha, emission,
normal or ORM maps. Linear mipmapped filtering, clamp/no repeat. Lossless texture import,
explicit mipmaps and disabled automatic 3D-compression changes. Actual imported-image
mipmaps are checked, not only metadata. No embedded images in the unchanged shared GLB.

The wrapper inherits the complete base fascia and overrides exactly one property:

`Visuals/Model/city_shop_fittings_02/fascia_artwork_carrier:surface_material_override/0`

The original slot name is asserted as `fascia_artwork_face`; slot 1 `fascia_mount_metal`
and all other hardware surfaces remain untouched. No global material override, copied mesh
resource or runtime appearance script. This follows the authorized narrow **static artwork
editable-child face-slot override exception** in
[Prefabs](../../assets.md#prefabs-and-authored-placement).

After initial normalization, **two consecutive load/pack/save/reload cycles are byte-stable**,
including UID, unique IDs, imported ancestry and override. Final prefab SHA-256:
`c04a3c145a90808dd47c14cd57ed3b3c709adda1d8fd5330fba87d4832ea8d73`.
Saved carrier `unique_id=821284309`, parent ancestry
`PackedInt32Array(1650053803, 643402131)`. Scene/material UIDs are inline, texture UID is in
`.import`, and checker UID is in `.gd.uid`; this engine generates no separate `.tscn.uid`
or `.tres.uid` here. Later hardware reexports must recheck identity retention.

**Visual-only wall-mounted/above-head decoration**, matching the base hardware and standing
flush-face/overhead rule. The supporting facade owns actor/car blocking. Never place this as
a freestanding obstacle; it introduces no collider, interaction, physics state, interior,
rig, animation, socket, destruction or light. Mounting at the proposed 3.8 m centre leaves
its lowest geometry at 3.4 m, above the 1.8 m actor. That arithmetic is not a placement test.

Live editor/MCP mutation was forbidden. Text-authored resources were normalized with the
isolated pinned headless engine. No owner's live Blender/Godot/MCP session was accessed or
claimed synchronized. Existing project plugins start/stop local servers during headless
checks; no MCP requests were made.

## Evidence and measured validation

[Hero](d02_neighbourhood_graphics_03-evidence/hero.png),
[side](d02_neighbourhood_graphics_03-evidence/side.png),
[groceries/frame detail](d02_neighbourhood_graphics_03-evidence/detail.png),
[47 m / 42° overhead](d02_neighbourhood_graphics_03-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles CPU renders: **1280×720**, 24 samples, denoised, AgX, PNG
compression 100, display dithering disabled; each under 255 KB. Temporary studio lights and
camera are never saved/exported. All four final renders and the texture were opened and
inspected: quiet family colour balance, upright readable close-range copy, recognizable
grocery bag, clean frame seating and no mirrored UVs or clipping of intended safe content.
The detail deliberately crops the long title to show the icon and inset.

Overhead: vertical-down/north-up perspective from Blender **(0,10,47)** with **42° vertical
FOV**. The unscaled fascia is translated only to the inherited **3.8 m** mounting height;
no camera-facing tilt or enlargement. It reads as a tiny ivory strip: **neither title nor
bag is reliably readable at gameplay scale**. It is subordinate decoration, never essential
wayfinding. Increased texture resolution cannot reveal an edge-on face; architecture and
world placement must supply any required gameplay identity. No populated-world or target
renderer acceptance is implied by the Blender previews or texture-downsample test.

[validation.json](d02_neighbourhood_graphics_03-evidence/validation.json) records:

- Shared fascia: **836 source vertices, 1,072 exported vertices, 1,656 triangles,
  seven meshes, eight surfaces**. **Zero new geometry** introduced by this artwork.
- Zero degenerate source faces/exported triangles and non-manifold edges; positive solid
  volumes, consistent outward winding, unit source/export normals, metre units and identity
  transforms. Source/export bounds and all **28** front UV samples pass.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Fresh read-only
  saved-source reexport exactly matches the committed **45,616-byte** GLB:
  `4fd2106f09ef4a35edafbcf3a3a68ea94983e721fd84d852a406e2d26de6552f`.
- Pinned Godot **4.8.dev7.official.c971f93e7** full headless import and separate non-editor
  dependency check exit 0 with no ERROR/SCRIPT ERROR lines; runtime has no WARNING lines.
- Exact inherited hierarchy/transforms/mesh resources, one face-only override, measured
  bounds, actual mipmaps and two byte-stable save/reload cycles pass.
- Four Python tests pass: exact PNG reproduction/size, safe margins/quiet field, independent
  groceries/palette pixels and small-texture motif contrast proxy (not gameplay evidence).
- gdstyle **0.3.0** formatting and lint pass with zero warnings on the owned checker.

[manifest.json](d02_neighbourhood_graphics_03-evidence/manifest.json) fingerprints every new
payload except itself and uncommitted Python caches. Shared dependencies are fingerprinted
in validation rather than duplicated. [final.log](d02_neighbourhood_graphics_03-evidence/final.log)
retains concise commands/outcomes. Full scratch logs and reexports remain outside Git at
`C:/tmp/ft/assets/d02_neighbourhood_graphics_03/`.

## Exact reproduction

From the worktree root; no windowed or live editor:

```sh
N=d02_neighbourhood_graphics_03
S=C:/tmp/ft/assets/$N
mkdir -p "$S"
python tools/asset_production/$N/author.py
python -m unittest discover -s tools/asset_production/$N -p 'test_*.py' -v

timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8 \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/validate.py

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8 \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/preview.py

timeout 300 "$(mise which godot)" --headless --path . --import
timeout 60 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/$N/check_prefab.gd -- --normalize
cp "$S/prefab.json" "$S/roundtrips.json"
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 60 "$(mise which godot)" --headless --path . \
  --script res://tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" fmt --check tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/$N/check_prefab.gd
python tools/asset_production/$N/finalize.py
# Regenerate only after an intentional payload change; default verifies.
python tools/asset_production/$N/manifest.py --write
python tools/asset_production/$N/manifest.py
```

`validate.py` refreshes the source-only receipt. `finalize.py` combines fresh artwork tests,
runtime/normalization receipts and renders, rejecting stale prefab/dependency hashes.
No `tools/production_checks.py` run, per owner decision 52.

## Diagnostics and remaining acceptance

Initial artwork generation exposed a missing K glyph in the reused skeleton set; adding
an original local K fixed it. One initial pixel assertion assumed an unfiltered divider
colour; the 4-pixel antialiased stroke includes a small ivory contribution, so that sample
now has a bounded six-level tolerance while broad grocery colours remain exact. One
102-character checker line was split; final tests/format/lint pass. No geometry/export,
import or prefab assertion failed.

Headless **editor normalization** passes resource assertions and exits 0 but emits the
existing plugin-version warning, aborted-scan warning and editor shutdown RID/ObjectDB leak
diagnostics. It is not described as diagnostic-free. Full imports and the separate runtime
check are clean of errors. Blender emits the existing node-API deprecation warnings, with
no source/export/audio failure. No failed step is counted as a successful check.

Pending: independent technical/art review, final fictional copy/name selection, saved
flat-bay facade/world placement and clearance, actual populated gameplay-camera/renderer
visibility, packaged texture filtering and repeat-placement/Deck performance. Future shared
hardware/tool changes must recheck dependencies and saved override identities. No new
movement, collision, multiplayer or platform acceptance is claimed. No registry, progress,
shared brief, TODO, other asset file or world placement changed.
