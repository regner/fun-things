# d02_neighbourhood_graphics.01 — Watch notice

**Artwork/material/linked-prefab candidate delivered; independent review and world acceptance
pending.** Commission: [production commission](commission.md), current per-ID assignment and
standing artwork-reuse rules. Producer: assigned implementation worker on `lane/a-d02g`.
Family: [Neighbourhood notice graphics](../d02_neighbourhood_graphics.md). This is the lane's
first family delivery; no earlier sibling handoff required reconciliation.

## Design, provenance and scope

Provisional fictional copy: **NEIGHBOURHOOD WATCH / MOSTLY CURTAINS**. An original four-pane
window with parted curtains gives the joke a domestic visual counterpart. One fine border,
a generous ivory field, muted blue secondary lettering and plum headline/punchline keep it
quieter than Signal Row's saturated commercial signage. No warning chevrons, neon emission,
real organization marks, brands, downloaded imagery or external fonts.

| Family colour | sRGB |
| --- | --- |
| Warm ivory | `#F6F1DC` |
| Quiet blue | `#526D86` |
| Muted plum | `#635168` |

The recipe uses the existing original project-owned rounded-path canvas and letter skeletons
from `d06_commercial_graphics_01/author.py` and `d06_commercial_graphics_02/author.py`, with
original M/W paths added here. Their files remain unchanged. Palette/size/glyph extension is
in-memory only; this is reuse of drawing tools, not of commercial artwork. Smooth 3×
supersampling is filtered once into the final texture. Python 3.14.2 / Pillow 12.3.0.
The local `PALETTE`, `SIZE` and `create_artwork()` make the domestic family treatment explicit.
Copy remains subject to final owner selection, not a new accepted naming decision.

References: accepted Petrol & Coral direction; approved stage-03 Crescents identity;
[The Crescents revision 02](../../concepts/districts-v1/the-crescents.md); stage-04 streets and
exact district map context. No dimension is measured from concept imagery. No world,
road, sector, placement, collision, gameplay, navigation or multiplayer data changed.

## Source, output and shared carrier

Per standing reuse rules, **no duplicate Blender source, GLB or decal mesh is created**.
The existing accepted wall panel supplies the applied geometry:

- Source: `art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend`.
- Collection/root: `export_city_sign_supports_01` / `CitySignSupports01`.
- Export: `art/models/environment/city_sign_supports_01/city_sign_supports_01.glb`.
- Base prefab: `scenes/prefabs/environment/city_sign_supports_01.tscn`.
- Hardware contract: [wall-panel source handoff](city_sign_supports_01.md) and
  [accepted integration convention](batch_01-integration.md).

New outputs:

- Recipe: `tools/asset_production/d02_neighbourhood_graphics_01/author.py`.
- Texture: `art/textures/environment/d02_neighbourhood_graphics_01/watch_notice_albedo.png`
  and engine-normalized `.import`.
- Material: `art/materials/environment/d02_neighbourhood_graphics_01/watch_notice.tres`.
- Prefab: `scenes/prefabs/environment/d02_neighbourhood_graphics_01.tscn`.
- Own `export.py` is a read-only shared-source exporter adapter: existing owner assertions
  and settings are reused unchanged, output goes only to scratch, then bytes are compared.
  `validate.py` also executes the owner's independent binary decoder with its evidence
  destination redirected in memory using an exact-match guard. No geometry-validator copy.

### Measured inherited interface

| Quantity | Metres / convention |
| --- | --- |
| Whole Godot X/Y/Z | **1.40 / 1.00 / 0.10** |
| Godot AABB | min **(-0.70, -0.50, -0.10)**; max **(0.70, 0.50, 0)** |
| Pivot | Wall attachment centre **(0,0,0)**, not a ground-contact prop |
| Front | Blender +Y → Godot -Z; Blender +Z → Godot +Y |
| Artwork surface | **1.22 × 0.82**, at Godot Z = **-0.088** |
| Safe copy rectangle | **1.14 × 0.74**, centred |
| Artwork aspect | **61:41**, exactly matching the face |
| Bounds tolerance | Source/export **0.000001 m**; engine **0.001 m** |
| Suggested mounting centre | **1.60 m** above local ground, provisional placement choice |

All source/export local transforms and imported `Visuals/Model` remain identity. No
corrective scale, rotation, UV transform, replacement geometry or duplicate panel. UV0
uses Blender U=(0.610-X)/1.220 and V=(Z+0.410)/0.820; glTF stores flipped V. From the front,
screen-right is local -X. The texture reads upright/unmirrored. Forty texels of uninterrupted
ivory on all outer edges protect the rounded face/safe-copy rectangle.

## Material, saved prefab and collision

**1220 × 820 RGB**, opaque sRGB albedo, **57,986 bytes**; final SHA-256:
`dfa975c71734e5c81b0b9bd8f6c279ea87b91a7a3aeb2226a495458e69129d0a`.
White base multiplier; roughness **0.8**; metallic **0**; no alpha, emission, normal or ORM
maps. Linear mipmapped filtering, clamp/no repeat. Lossless texture import with mipmaps
explicitly enabled and automatic 3D compression changes disabled. Mipmaps are checked on
the actual imported image, not just the import settings text. No images embedded in GLB.

The wrapper inherits the complete base panel and changes exactly this property:

`Visuals/Model/CitySignSupports01/artwork_carrier:surface_material_override/0`

The original material name is asserted as `sign_face`; slot 1 `mount_metal` and every other
hardware surface remain unchanged. This follows the authorized narrow **static artwork
editable-child face-slot override exception** in [Prefabs](../../assets.md#prefabs-and-authored-placement).
No appearance script, global material override or embedded mesh resource. Two consecutive
load/pack/save/reload cycles after initial normalization preserve identical bytes, UID,
`unique_id` and ancestry. The imported carrier retains `unique_id=16194531`; its imported
parent ancestry remains `PackedInt32Array(728591687, 1891583522)`. Scene/material UIDs are
inline, texture UID is in `.import`, checker UID is in `.gd.uid`; no separate `.tscn.uid`
or `.tres.uid` is generated by this engine.

**Visual-only, wall-mounted decoration**, matching the base hardware and standing flush-face
rule. The mounting facade owns actor/car blocking; never place this as a freestanding
obstacle. It adds no collider or physics behavior. No interiors, interactions, animation,
rigs, sockets, destructibility or runtime lights. Placement must keep the 0.10 m projection
out of narrow passages and preserve facade-owned collision; none of that is accepted here.

Editor/MCP mutation was forbidden by the assignment. Text-authored resources were normalized
in isolated pinned headless Godot. No live Blender/Godot/MCP session was used or touched;
a separate open scene is not claimed synchronized. Existing project plugins start/stop their
own local server during headless checks; no MCP requests were made.

## Evidence and measured validation

[Hero](d02_neighbourhood_graphics_01-evidence/hero.png),
[side](d02_neighbourhood_graphics_01-evidence/side.png),
[face detail](d02_neighbourhood_graphics_01-evidence/detail.png),
[47 m / 42° overhead](d02_neighbourhood_graphics_01-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles CPU renders: **1280×720**, 24 samples, denoised, AgX, PNG
compression 100, display dithering disabled. Each is under 288 KB. Temporary neutral wall,
ground, lights and camera are evidence-only and never saved/exported. All final images were
opened and inspected: clean frame, readable upright close-range copy, clear parted curtains,
restrained ink colours, no clipped letters or UV mirroring. The initial punchline spacing
was reduced before delivery to leave balanced border clearance.

Overhead: vertical-down perspective from Blender **(8,9,47)**, **42° vertical FOV**, north-up;
no camera-facing tilt. Unscaled panel centre is at **(0,0,1.6)** on the temporary mounting
wall. It is a tiny, strongly foreshortened ivory strip; **neither copy nor curtain motif is
reliably readable at gameplay scale**. This is intentional subordinate decoration, not
text-dependent navigation or a gameplay cue. Increasing texture resolution cannot expose a
vertical face. No populated-world or target-renderer acceptance follows from these images.

[validation.json](d02_neighbourhood_graphics_01-evidence/validation.json) records:

- Shared panel: **1,380 source vertices, 1,792 exported vertices, 2,720 triangles,
  12 meshes, 13 surfaces**. No new geometry/triangles introduced by the artwork.
- Zero degenerate source faces/exported triangles, zero non-manifold edges, positive
  component volumes, consistent outward winding and unit-length source/export normals.
- Metre units, identity transforms, bounds and all **36** front UV samples pass.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**. Shared saved-source
  reexport is byte-identical to the committed **75,768-byte** GLB. Read-only dependency
  hashes/byte counts match before/after and again during final receipt assembly.
- Pinned Godot **4.8.dev7.official.c971f93e7** import and separate non-editor dependency
  check exit 0 with no ERROR/SCRIPT ERROR lines; runtime also has no WARNING lines.
- Exact inherited hierarchy/transforms/mesh resources, one face-only override, measured
  bounds, actual mipmaps and two byte-stable save/reload cycles pass.
- Four Python tests pass: exact texture reproduction, quiet safe margin, literal
  curtain/palette samples and a small-texture motif contrast proxy (not gameplay evidence).
- Owned GDScript formatting and lint pass gdstyle **0.3.0**, zero issues/warnings.

[manifest.json](d02_neighbourhood_graphics_01-evidence/manifest.json) contains SHA-256 and byte
counts for every produced file except itself/uncommitted Python caches. Shared dependencies
are fingerprinted in validation rather than duplicated. [final.log](d02_neighbourhood_graphics_01-evidence/final.log)
retains concise commands/outcomes. Full scratch logs/exports are outside Git under
`C:/tmp/ft/assets/d02_neighbourhood_graphics_01/`.

## Exact reproduction

From the worktree root; no windowed or live editor:

```sh
N=d02_neighbourhood_graphics_01
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

`validate.py` refreshes the source-only receipt; `finalize.py` adds fresh saved engine,
normalization, artwork-test and render results, rejecting stale prefab/dependency hashes.
No `tools/production_checks.py` run, per owner decision 52.

## Diagnostics and remaining acceptance

One initial normalization asserted on an incorrect explicit material filter value and timed
out at 180 seconds. Removed that value to use the engine's linear-mipmap default; corrected
normalization and runtime checks pass. Timeout shutdown emitted engine static-string/thread/
RID diagnostics; the failed attempt is not a successful check. No own process remains alive.
Successful headless **editor** normalization still emits the known plugin-version warning,
scan-aborted warning and editor shutdown RID/ObjectDB leaks; it passes all resource assertions
but is not described as diagnostic-free. Full import and non-editor dependency checks are
separate and clean of errors. Blender reports existing node-API deprecation warnings, no
source/export/audio failure. Initial dithered renders exceeded the evidence size target;
disabling final display dithering reduced them without changing artwork or geometry, and all
four replacement images were inspected.

Pending: independent technical/art review, final fictional copy selection, saved facade/world
placement and passage clearance, actual populated gameplay-camera/renderer visibility,
packaged texture filtering and repeat-placement/Deck performance. Any future hardware
hierarchy/reexport change must recheck the face override's identities. No new movement,
collision, network or platform acceptance is claimed; existing hardware/placement owners
retain those gates. No registry, progress, shared brief, TODO or other asset file was changed.
