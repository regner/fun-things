# d05_civic_graphics.01 — Hall fascia art

10 October 2026. **Artwork/material and linked prefabs delivered; bounded checks pass.
Independent review, final copy selection and world/device acceptance remain pending.**
Produced by the isolated production worker on `lane/a-d05` under the current common
brief and [commission](commission.md). Parent/reviewer owns acceptance. Family:
[Harbour civic graphics](../d05_civic_graphics.md).

## Design and provenance

**OFFICE OF / TEMPORARY PERMANENCE** uses the brief's candidate fictional copy. An
original civic seal combines a pediment, three piers and two calm harbour lines inside
an elongated octagonal border. Broad ivory capitals and muted amber details sit on a
quiet slate field: civic humour, not commercial neon. No emission, light nodes, real
brands, downloads, external fonts or generated images. Copy remains provisional.

All lettering paths and emblem strokes are original and reproducible in
`tools/asset_production/d05_civic_graphics_01/author.py`, using Python 3.14.2 / Pillow
12.3.0. The script supersamples continuous paths at 3x and downsamples once; this is
not bitmap-grid lettering. References inspected: Petrol & Coral, approved Stage 3
Old Quay identity, Stage 4 streets, Old Quay breakdown/v03 references, shared fascia
contract, and the delivered harbour hall/canopy. No raster measurements were inferred.

Family graphic grammar for reuse: **slate #344953**, **ivory #F6F1DC**, **amber #E9B96E**,
broad clean lettering, quiet perimeter and no luminous saturation. This hall owns its
municipal seal; the source recipe requires no separate font/license payload. Artwork
is decorative identity, not essential text-dependent navigation or a civic interaction.

## Source, material and reused carrier

The standing **reuse rule** is binding: accepted shared fascia hardware already supplies
this face. There is deliberately **no duplicate per-ID .blend, GLB, panel or export.py**.
The original 2D source is `author.py`; the Blender source/export chain remains:

- Source: `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`.
- Collection/root: `export_city_shop_fittings_02` / `city_shop_fittings_02`.
- Export: `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb`.
- Hardware contract: [city_shop_fittings.02](city_shop_fittings_02.md).
- `validate.py` calls the existing hardware exporter and independent GLB decoder,
  writing their receipts/reexport only to external scratch. No dependency is saved.
  The accepted exporter settings are unchanged; no new geometry/export policy is added.

Runtime artwork: `art/textures/environment/d05_civic_graphics_01/hall_fascia_albedo.png`
plus its pinned-engine `.import`. **2000 x 400 RGB**, opaque sRGB albedo, **46,874 bytes**.
SHA-256: `d532dc4e9ada028f3c349493a58671db3da2b2d27eaaf6774678764945f8e805`.
No other channels/maps or embedded images are needed.

Material: `art/materials/environment/d05_civic_graphics_01/hall_fascia.tres`.
White albedo multiplier, metallic 0, roughness 0.56, back-culling, opaque, no emission,
linear mipmapped filtering, clamp/no repeat. Texture import is lossless, mipmaps on,
automatic 3D compression changes disabled. Godot owns the saved material/texture UIDs.

### Dimensions and attachment

Inherited hardware measurements (Godot metres; tolerance +/-0.001 m):

| Interface | Contract |
| --- | --- |
| Whole fascia X/Y/Z | **3.200 x 0.800 x 0.140** |
| Local AABB | min **(-1.600, -0.400, -0.140)**, max **(1.600, 0.400, 0)** |
| Pivot | Wall-contact centre `(0,0,0)`, not a ground pivot |
| Artwork plane | 3.000 x 0.600, Godot Z=-0.128, 5:1 UV aspect |
| Safe content | Centred 2.940 x 0.540; outer 20 px margins remain slate |
| UV0 | U grows toward Blender -X; V toward +Z; glTF flips V storage |
| Forward/up | Blender +Y/+Z converts once to Godot -Z/+Y |

No transforms or UVs are changed; the front lettering is upright and unmirrored.
No rig, clips, sockets, new LOD, collision, navigation or runtime artwork writer.

## Saved prefab, override and mounting reference

`scenes/prefabs/environment/d05_civic_graphics_01.tscn` has an identity-transform
linked GLB at `Visuals/Model`. Its sole override is:

`Visuals/Model/city_shop_fittings_02/fascia_artwork_carrier: surface_material_override/0`

Slot 0 is checked against `fascia_artwork_face`. Slot 1 remains `fascia_mount_metal`;
all seven imported mesh resources, other surfaces and transforms remain unchanged.
No copied vertex data, global material override or duplicate coplanar face is saved.
This uses the authorized **static artwork face-slot editable-child exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement). The linked GLB
is unchanged. After initial normalization, **two full save/reload cycles preserve
exact scene bytes, node identities and UIDs**, for both delivered scenes. A subsequent
import and two independent runtime processes preserve those hashes and resolve UIDs.

`scenes/prefabs/environment/d05_civic_graphics_01_hall_preview.tscn` is a mounting
reference, **not district placement**. It only instances the existing hall/canopy and
this fascia: hall at identity, canopy at `(0,3.85,-9)`, fascia at `(0,4.95,-9)`.
The fascia mounting height is a **provisional production choice**, compatible with
the delivered central bay: bottom Y=4.55, top Y=5.35, canopy top Y=4.25, gap **0.30 m**;
hall fascia bottom Y=5.76 leaves **0.41 m** above the sign. Wall contact stays Z=-9.
The 3.2 m fitting fits centrally inside the 8 m canopy and 6.6 m lintel bay.

Visual-only above-head/flush fitting: no collider is added. The reference preserves
exactly the hall's existing one static body/three collision shapes; those still own
blocking. No collision dimensions or gameplay outcome rules change. Do not place a
second blank fascia under this prefab. Existing hall/canopy sources, GLBs, prefab
identities and historical evidence remain untouched.

The two hall handoffs' **current Remaining acceptance items only** now point here,
and their manifests refresh only those doc hashes/byte counts, under the standing
sibling-status exception. No shared brief, tracker, queue/progress/TODO or world changes.

## Evidence and validation

[Hero](d05_civic_graphics_01-evidence/hero.png) ·
[Side](d05_civic_graphics_01-evidence/side.png) ·
[Mounted detail](d05_civic_graphics_01-evidence/mount_detail.png) ·
[47 m / 42-degree overhead](d05_civic_graphics_01-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU/32-sample AgX renders, **1280 x 720**,
RGB8 PNG compression 95, no dithering; each below 400 KiB. All were visually inspected.
Hero/side show the correct face direction, full copy and unchanged recessed hardware.
Mounted detail shows a quiet civic sign above the canopy, without trim intersection.
The corrected overhead framing includes the entire hall; its roof **fully occludes
the fascia at this centred vertical-down camera**. The fascia is not a gameplay-scale
landmark cue. The existing roof/canopy must carry orientation; no oversized/tilted
sign or extra roof geometry was invented to fake readability. These are not Godot
screenshots, actor visibility evidence or world/camera acceptance.

Final [validation.json](d05_civic_graphics_01-evidence/validation.json) records:

- Blender **5.2.2 LTS**, build `d13f752e3b9c`, exporter **5.2.40**.
- Reused hardware: **836 source vertices / 1,072 GLB vertices / 1,656 triangles**;
  **7 meshes / 8 surfaces**, 5 hardware materials.
- **Zero degenerate source faces/exported triangles; zero non-manifold edges**;
  consistently wound closed solids, unit-length corner/exported normals, applied
  transforms/metre units, and 28 verified front UV boundary samples.
- Independent source/GLB and Godot AABBs match the inherited contract.
- Saved-source reexport **byte-identical**, **45,616 bytes**, SHA-256
  `4fd2106f09ef4a35edafbcf3a3a68ea94983e721fd84d852a406e2d26de6552f`.
- Three Python tests pass: deterministic PNG bytes/format, safe margins/quiet field,
  and independent asymmetric lettering/emblem colour landmarks (8/255 antialias tolerance).
- Pinned Godot **4.8.dev7.official.c971f93e7** import: no ERROR/SCRIPT ERROR.
  Two fresh runtime checks agree exactly: linked meshes, face-only override, mipmaps,
  dependencies/UIDs, mounting clearance and unchanged collider count.
- Both scenes pass two save/reload cycles with three identical SHA-256 snapshots each.
  GDScript lint (`--max-line-length 100 --max-warnings 0`) and format check pass.

[manifest.json](d05_civic_graphics_01-evidence/manifest.json) hashes all new payloads,
including this doc, tests, import metadata, validation and four renders; excludes only
itself and uncommitted Python cache. Shared dependencies are hashed in validation,
not copied into this payload. [final.log](d05_civic_graphics_01-evidence/final.log)
retains concise checks and actual final diagnostics. Scratch/retry logs remain outside
Git at `C:/tmp/ft/assets/d05_civic_graphics_01/`.

## Exact reproduction

From the worktree root in Git Bash (do not use a live editor):

```sh
NID=d05_civic_graphics_01
P="$(pwd -W)"
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
export PYTHONIOENCODING=utf-8
python "tools/asset_production/$NID/author.py"
python -m unittest discover -s "tools/asset_production/$NID" -p 'test_*.py' -v \
  > "$T/tests-final.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$P/tools/asset_production/$NID/validate.py" > "$T/validate.log" 2>&1
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$P/tools/asset_production/$NID/preview.py" > "$T/preview-final.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$T/import-first.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/normalize-final.log" 2>&1
cp "$T/prefab.json" "$T/roundtrips.json"
timeout 300 "$G" --headless --path . --import > "$T/import-final.log" 2>&1
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" > "$T/load-final.log" 2>&1
cp "$T/prefab.json" "$T/load-first.json"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" > "$T/load-second.log" 2>&1
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd" \
  > "$T/fmt-final.log" 2>&1
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd" > "$T/lint-final.log" 2>&1
python "tools/asset_production/$NID/record.py"
python "tools/asset_production/$NID/manifest.py" --write
python "tools/asset_production/$NID/manifest.py"
```

`record.py` rejects script errors, missing markers, differing runtime receipts or
stale scene snapshots. `manifest.py` without `--write` verifies rather than rewriting.
No `tools/production_checks.py` run (owner decision 52). Editor-managed text fallback
is expressly required by the common brief; it was normalized headlessly. No owner's
live Blender/Godot/MCP session was accessed or claimed synchronized.

## Diagnostics and remaining acceptance

Initial exact-colour test hit antialiasing on a 5 px line endpoint; changed only that
expectation to a bounded colour tolerance. A helper grew one line past gdstyle's
50-line limit; extracted the normalization routine and reran lint. Initial UID
registry assertion ran before the editor scanned newly saved resource headers;
normalization now checks saved UIDs, and the post-import runtime check requires full
registry resolution. No failed run is counted as a passing receipt. The first overhead
cropped the far roof edge; camera XY was centred and renders regenerated/inspected.

Final normalization exits 0 with stable scenes but retains the known pinned-editor
scan-abort/RID/ObjectDB shutdown leaks and addon compatibility warning. It is **not a
clean editor log**. Final import has only that compatibility warning; both fresh
runtime logs have no ERROR/WARNING/SCRIPT ERROR. Blender's node-API deprecation
warnings are retained in external logs. No global settings or error suppression added.

Pending: independent art/technical review; final copy selection; district placement,
actual Godot lighting/filtering and gameplay-camera/roof occlusion review; populated
world movement/aim/vehicle checks and target-device packaging/performance/Deck tests.
This unplaced decorative asset claims no multiplayer or full-world acceptance.
