# d03_community_graphics.01 — Community board face

10 October 2026. **Original artwork and bounded source/prefab checks delivered; independent
review and world acceptance pending.** Commissioned under [commission](commission.md) and
the current per-asset execution brief, superseding the historical concept-only status in
[community graphics](../d03_community_graphics.md). Producing owner: worker on `lane/a-d03g`,
responsible for art, integration, checks and visual self-review. Accepting owners: independent
art/technical reviewer and world/gameplay integrator; successful checks do not imply approval.

References: [Terrace Ward](../../concepts/districts-v1/terrace-ward.md), its
[asset breakdown](../../concepts/districts-v1/terrace-ward-assets.md), approved
[Stage 3 identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[Stage 4 streets](../../concepts/world-v1/stage-04-streets/README.md) and Petrol & Coral.
The earlier [short laundry frame](d03_laundry_frames_01.md), [cloth](d03_laundry_frames_03.md),
[circular paving](d03_court_graphics_01.md) and [small play graphic](d03_court_graphics_02.md)
informed the quiet domestic palette. Their current handoffs do not list this asset as pending.

## Design and dimensions

One multi-notice artwork set: a muted-teal civic header with two conversation bubbles above
three generously separated printed notice fields. A neighbours icon anchors the larger meeting
notice; a dusty-coral textile icon links the laundry notice to the delivered cloth family.
Original rounded monoline capitals, flat paper fields and broad gutters avoid distressed paper,
tiny faux copy, neon or commercial advertising. All notices belong in **one opaque image**;
there are no extra paper meshes, pins, glazing, lights, animation, interaction or gameplay IDs.

Authored provisional copy, not text accepted from a generated concept image:

- **SHARED SPACE. / INDIVIDUAL OPINIONS.**
- **COURT CHAT / ALL WELCOME**
- **LAUNDRY / SHARE THE LINE. / NOT THE SOCKS.**
- **TAKE A SEAT / LEAVE ROOM.**

Copy approval remains an art-review gate. No real brands, external fonts, downloaded artwork,
image-to-mesh or generated runtime geometry. `author.py` contains every original glyph path,
icon, color and layout coordinate and reproducibly draws the texture with Pillow **12.3.0**.

The saved prefab **inherits the existing [city_sign_supports.03 noticeboard](city_sign_supports_03.md)**.
The shared carrier is already produced on main. Its provisional dimensions are unchanged, not
inferred from concept imagery or newly chosen for this artwork. Godot local X/Y/Z, metres:

| Contract | Value |
| --- | --- |
| Whole carrier width / height / depth | 1.900 / 2.100 / .440 |
| Whole AABB minimum / maximum | (-.950, 0, -.220) / (.950, 2.100, .220) |
| Pivot / ground datum | Ground-centred between feet, (0,0,0) / Y=0 |
| Artwork width / height | 1.640 / 1.040, aspect 41:26 |
| Face bottom / top / front plane | Y=.900 / Y=1.940 / Z=-.071 |
| Safe-copy rectangle | 1.580 x .980; .030 m inset on every edge |
| Frame lip / recessed face clearance | .009 m |
| Envelope / coordinate tolerance | .001 m / .00001 m |

Metre units, identity root and mesh transforms; no corrective prefab scales or rotations.
Blender +Z maps to Godot +Y; Blender +Y is the front, Godot -Z. The carrier's front-view
screen-right direction is -X. Blender UV0 is U=(.82-X)/1.64, V=(Z-.90)/1.04;
glTF image V=0 is top, V=1 bottom. Binary UV/winding checks and the rendered lettering prove
upright, unmirrored application. Face corners are clipped by the inherited .022 m radius.
All copy/icons/notices fit inside the safe inset; only flat background extends to the frame.

## Sources, export, material and prefab

New runtime files:

- `art/textures/environment/d03_community_graphics_01/community_board_albedo.png` + `.import`.
- `art/materials/environment/d03_community_graphics_01/community_board.tres`.
- `scenes/prefabs/environment/d03_community_graphics_01.tscn`.
- Reproducible source/check tools: `tools/asset_production/d03_community_graphics_01/`.

**No duplicate `.blend` or GLB was created.** This is the standing reused-hardware exception:
artwork/material plus a saved prefab reuses the Blender-sourced face and existing collision.
The geometry provenance remains:

- Source: `art/source/models/environment/city_sign_supports_03/city_sign_supports_03.blend`.
- Collection/root: `export_city_sign_supports_03` / `CitySignSupports03`.
- Meshes: `CitySignSupports03_Hardware`, `CitySignSupports03_ArtworkCarrier`.
- Export: `art/models/environment/city_sign_supports_03/city_sign_supports_03.glb` + `.import`.
- Carrier prefab: `scenes/prefabs/environment/city_sign_supports_03.tscn`.

All those payloads remain byte-unchanged. `export.py` freshly opens the shared source and
delegates to its owner's exporter into **external scratch only**, using the shared
`tools/assets/blender/export_settings.json`. `validate.py` measures the source/GLB and reuses
the earlier court-graphic validator's pure binary-accessor decoder; it does not run or edit
that sibling validator. The dependency hashes are recorded in validation.json.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; Godot
**4.8.dev7.official.c971f93e7**. The original named export collection, Y-up conversion,
static/no-animation/no-skin settings and default automatic import LOD remain unchanged.
No new rig, socket, animation, destruction state or explicit LOD is required.

Only imported `CitySignSupports03_ArtworkCarrier` **surface 0, `sign_face`**, receives
`community_board.tres`. Surface 1 (`mount_metal`) and the hardware's three surfaces retain
original materials. The saved `surface_material_override/0` and single editable `Visuals/Model`
path use the authorized narrow static-artwork exception in [assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement).
No copied mesh data, whole-mesh override, runtime material writer or runtime scene composition.
The GLB instance remains at identity-transform `Visuals/Model` inside the inherited wrapper.

The PNG is **1640x1040 RGB8 sRGB**, 3x supersampled then Lanczos-reduced, approximately
**1000 texels/metre** on the face. Clamp, linear filtering with ten mip levels, lossless import,
no automatic 3D compression conversion. One full non-tiled face atlas, not a generic ground or
road-tool material. No alpha, emission, normal map, ORM or embedded GLB images. The opaque
StandardMaterial3D has white albedo multiplier, roughness **.84**, metallic **0**, back culling.
The preview uses corresponding Principled settings without saving the shared Blender source.
Imported RGB8 CPU data including mips is **6,822,117 bytes**, not GPU allocation or a device budget.

| Color region | sRGB |
| --- | --- |
| Teal / ivory / dusty coral | #587D7C / #CECDB8 / #B98377 |
| Ink / paper / pale notice | #294B50 / #E6E1CC / #C5D0C3 |

The first three swatches match the delivered court graphics; dusty coral also matches the
laundry towel. This face is deliberately quieter than a loud commercial destination.

## Collision and saved identities

This is a freestanding board, **not a visual-only obstacle**. It inherits exactly one existing
static body at `Collision/Body`, layer 1 / mask 0, and its `Shape` BoxShape3D: size
(1.90,2.10,.44), centre (0,1.05,0). The carrier owns the conservative envelope, including the
under-panel gap. Tests compare actual mesh/shape resource identities, transforms, filters and
all material surfaces against the pristine shared prefab; there is no new collision shape.
This artwork-only delivery does not repeat or recertify the carrier's historical ActorMotion
checks, car contact or real-process multiplayer. Keep boards away from passage mouths and
important actor/aim sightlines; this solid panel is not an underpass or walkable surface.

The execution brief prohibits live-owner editor access, so direct scene/material text authoring
was followed by pinned headless load/pack/save/reload normalization. Two complete post-normalization
roundtrips retain **exact bytes, node identities and UIDs**, and a fresh normalization process
also proves its initial files already stable. Two fresh runtime receipts agree. Dependency UIDs
resolve; scene/material UIDs are embedded, and the script's generated `.gd.uid` is committed.
Godot creates no scene `.uid` sidecar. No live session was touched; this workflow does not claim
a separate open editor was synchronized.

## Evidence and validation

[Hero](d03_community_graphics_01-evidence/hero.png),
[oblique side](d03_community_graphics_01-evidence/side.png),
[face detail](d03_community_graphics_01-evidence/detail.png),
[47 m / 42-degree overhead](d03_community_graphics_01-evidence/overhead_47m_42deg.png).
All four final isolated Blender Cycles CPU renders were inspected: 32 samples, AgX,
1280x720 RGB8 PNG, compression 95, no dithering, overlays or post-quantization. Each is below
400 KiB. The current 720-pixel evidence cap supersedes the older 800-pixel requirement.
The original saved board studio supplies its ground and lighting, excluded from the export.

Header, three notice fields, humour and domestic icons read upright in hero/detail, without
clipping behind the frame. The side view was widened after self-review to retain the complete
cap and feet; the face detail intentionally crops some frame. The calibrated overhead is true
vertical-down, north-up perspective at (0,0,47), **42-degree vertical FOV**. It shows only an
approximately 40-pixel cap strip: **the vertical artwork is edge-on and its copy is not readable**.
Do not use it as essential navigation or enlarge/tilt the shared carrier to fake overhead
legibility. These source-studio images are not Godot gameplay or populated-court acceptance.

Final [validation.json](d03_community_graphics_01-evidence/validation.json):

- Reused carrier: **2,636 triangles; 1,340 source vertices; 1,711 GLB vertices; two meshes;
  five surfaces**. Artwork adds zero triangles and overrides exactly one surface.
- Zero source non-manifold edges, zero source degenerate faces and GLB degenerate triangles;
  unit source/export normals, outward winding, finite positions, literal dimensions/pivot and
  upright face UVs pass. Shared source/export/import/prefab hashes remain unchanged.
- Fresh carrier source re-export and original PNG regeneration are **byte-identical**.
- **Five artwork tests**: reproduction, literal copy, 20 independent palette-region probes,
  all nine populated text regions and inherited 30-pixel safe margins pass.
- Final pinned headless import, two byte-stable normalization roundtrips and two fresh runtime
  load/dependency checks pass, with no `ERROR` or `SCRIPT ERROR` lines. Full actual mip chain,
  exact face-only override, unchanged imported mesh resources and inherited collider pass.
- Python syntax checks, `gdstyle fmt --check`, and lint at 100 characters / zero warnings pass.
  `production_checks.py` deliberately not run, per decision 52.

Final payload identities copied from the receipts:

| Payload | Bytes | SHA-256 |
| --- | ---: | --- |
| New albedo PNG | 112,772 | `e1dd1270d600a593e0768b706305954c70beae3d3de7745726c2ee5a5f74b782` |
| Unchanged shared GLB | 75,520 | `f6ed9b4bd732c2e46104cf52453641e6c6e212483dd27d26d33a683dfefbdd8c` |

[manifest.json](d03_community_graphics_01-evidence/manifest.json) hashes every produced file
except itself, plus the authorized carrier-status reconciliation. The current carrier handoff's
pending district-artwork item now links this delivery; only that document's hash/byte entry in
its manifest changed. Historical receipts and every carrier payload remain untouched.
[checks.log](d03_community_graphics_01-evidence/checks.log) records final passes and initial
findings: default no-mip import/automatic compression policy corrected in the owned sidecar;
one overlong constant wrapped; an exact-color text occupancy probe replaced with near-ink
occupancy to include antialiased thin strokes, preserving its >400-pixel threshold; side
framing widened. Blender emits its pinned `use_nodes` deprecation warning, and import the
existing toolkit engine-version advisory. No warning suppression or warning-free claim.

## Exact reproduction

From the worktree root in Git Bash, Python with Pillow 12.3.0. Preserve committed `.import`
metadata and UIDs. Never use the owner's live Blender/Godot sessions. Scratch renders, logs
and fresh exports stay outside Git. `record.py` runs last, after all checks and handoff updates.

```sh
NID=d03_community_graphics_01
T=tools/asset_production/$NID
S=C:/tmp/ft/assets/$NID
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
STYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
mkdir -p "$S"
python "$T/author.py"
python "$T/test_artwork.py" > "$S/artwork-check.log" 2>&1
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" > "$S/validate.log" 2>&1
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/preview.py" > "$S/preview.log" 2>&1
python -m py_compile "$T/author.py" "$T/export.py" "$T/preview.py" \
  "$T/validate.py" "$T/test_artwork.py" "$T/record.py" \
  && echo PYTHON_COMPILE_PASS > "$S/python-check.log"
"$STYLE" fmt --check "$T/check_prefab.gd" > "$S/format.log" 2>&1
"$STYLE" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd" > "$S/style.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-remap.log" 2>&1
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" -- \
  --normalize --verify-stable > "$S/roundtrip.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" \
  > "$S/prefab-check.log" 2>&1
cp "$S/prefab-check.json" "$S/prefab-first-process.json"
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" \
  > "$S/prefab-second-process.log" 2>&1
cmp "$S/prefab-first-process.json" "$S/prefab-check.json"
python "$T/record.py"
```

`validate.py` reopens the shared saved source and delegates to its original exporter in
`$S/reexport/`. For a standalone shared-carrier export without changing production files:

```sh
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/export.py" -- "$S/manual-reexport"
```

## Review round 1 — saved dependency identities

Addressed the P2 finding by serializing existing UIDs for the inherited carrier prefab, face material and material texture dependencies.
No identity was reallocated. Header UIDs, node `unique_id` values, ancestry, transforms,
material settings and collision are unchanged. The checker follows the delivered
entrance-number asset's headless fallback: after Godot saves, restore dependency UID
fields from the warm import cache, then inspect the actual serialized text. Every owned
prefab/material (and owned fixture, where present) must have a header UID, a resolving
`uid=` on each `[ext_resource]`, and `unique_id=` on every node. Runtime checking is read-only
and rejects absent or mismatched dependency UIDs before other checks.

The strengthened checker rejected the original missing fields and a deliberately mismatched
registered UID (exit 1); restored files pass normalization, two byte-stable supplemented
save/reload cycles, pinned import and two fresh runtime checks with identical receipts.
Source validation and fresh re-export were rerun; existing source, GLB, artwork and render
bytes remain unchanged. Renders were not regenerated because no visual input changed;
the reviewed four images remain the visual evidence. Artwork reproduction checks, where
applicable, Python compilation and pinned GDScript format/zero-warning lint pass.
`validation.json` records the serialized dependency map and negative-test observations;
`manifest.json` was regenerated last. The exact reproduction commands below/above remain
valid. No live editor was accessed or synchronized. Full world/gameplay/device acceptance
remains pending; independent review must confirm this P2 repair.

## Remaining acceptance

- Independent technical/art review at the committed candidate; provisional copy approval.
- World integrator: saved court-edge placement, open passage mouths and populated
  actor/target visibility; this supporting board must not obscure a walking choice.
- Visual/gameplay owners: actual Godot lighting/camera captures, moving-camera mip behavior,
  placement contact/query checks and any real-process multiplayer-world consequences.
- Build/performance owners: packaged dependencies, repeated-board texture/draw cost,
  automatic LOD appearance, sustained target-device performance and Deck readability.

No world scene, topology, registry, progress tracker, shared brief or TODO changed. This is an
importable tested artwork candidate, not full game-ready/world acceptance.
