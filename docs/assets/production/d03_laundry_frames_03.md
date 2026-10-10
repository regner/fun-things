# d03_laundry_frames.03 — Two restrained hanging-cloth shapes

10 October 2026. **Source/export and bounded prefab checks delivered; independent review
and world acceptance pending.** Commissioned under [commission](commission.md) and the
current per-asset production brief, superseding the family's earlier concept-only status.
Family: [communal laundry frames](../d03_laundry_frames.md). Direction:
[Terrace Ward](../../concepts/districts-v1/terrace-ward.md), its asset breakdown, approved
Stage 3 identities and Stage 4 streets, and Petrol & Coral.

Producing owner: commissioned worker specialist, responsible for original Blender
construction, export, prefab integration, tests and visual self-review. Accepting owners:
independent art/technical reviewer and world/gameplay integrator; no acceptance is inferred.
This delivery uses the earlier [short frame](d03_laundry_frames_01.md) unchanged.

## Design and dimensions

Two broad, static folded shapes: a warm-grey wide sheet with two shallow drape waves,
and a narrower dusty-coral towel with one wave. A short rear return folds each piece over
the line rather than ending as a floating rectangle. Subtle hem bands, soft edges and
quiet opaque colors imply domestic laundry without fabric noise, logos or tiny pegs.
No downloads, generated-image meshes, cloth simulation, wind, rigs, animation, interaction,
destruction or new gameplay rules. All new visible geometry is original Blender construction.

Dimensions below are **provisional authored values**, not measurements inferred from the
concept raster. Godot local X/Y/Z in metres; values rounded to four decimals:

| Component | AABB minimum | AABB maximum | Width / height / depth |
| --- | --- | --- | --- |
| Sheet | (-0.7101, -1.0404, -0.1719) | (0.7101, 0.0241, 0.1714) | 1.4202 / 1.0645 / 0.3433 |
| Towel | (-0.3801, -0.8005, -0.1558) | (0.3801, 0.0241, 0.1554) | 0.7601 / 0.8246 / 0.3112 |

Both pivots are the **top-centre mounting line axis**, at (0,0,0), not ground-contact
pivots: this implements the frame's documented attachment interface. Broad faces span X;
cloth hangs down -Y. Blender +Z maps to Godot +Y and Blender +Y to Godot -Z. Source roots
and mesh objects have zero translation/rotation and unit scale. No corrective prefab
transforms. Bounds tolerance is 0.001 m; source/GLB mapping tolerance is 0.00001 m.

The authored mid-surface wraps a 0.020 m radius semicircle. Applied solidification gives
0.008 m stylized thickness and closed topology, so both sides remain visible with normal
backface culling. Minimum measured shell-edge distance to the mounting axis is 0.015615 m
for both variants (rounded), clearing the frame's 0.014 m line radius. The rear return
hangs approximately 0.25 m; the long front drops nominally 1.04 m / 0.80 m respectively.
The thickness is an intentional small-scale readability choice, not simulated textile mass.

### Mounting and placement contract

Use the existing frame's line axes: **Y=2.180; Z=-0.480, 0, +0.480**; usable cloth span
X=-1.600..+1.600. Translate the component root to the line axis; do not rotate/scale its
imported `Visuals/Model`. Keep its entire width within that usable span. Both source studio
and saved `check_scene.tscn` demonstrate one quiet two-piece arrangement on the outer line:

| Instance | Godot root position |
| --- | --- |
| Sheet | (-0.620, 2.180, -0.480) |
| Towel | (+0.780, 2.180, -0.480) |

The actual engine AABBs leave a **0.309848 m** gap between cloths; lowest cloth is
**1.139586 m** above ground. Both fit inside the frame's width/depth and stay clear of the
middle line. This is a mounting example, not permission to occupy a walking route. Place
laundry at court edges, away from movement mouths and important aim/camera sightlines.
Do not blanket all three lines or turn repeated cloth into a dense overhead canopy.

## Source, exports and materials

- Source: `art/source/models/environment/d03_laundry_frames_03/d03_laundry_frames_03.blend`.
- Authoring scene: `ClothSources`. Separate saved evidence scene: `Studio_MountedCloths`.
- Collections: `export_d03_laundry_frames_03_sheet` and `export_d03_laundry_frames_03_towel`.
- Roots: `D03LaundryFrames03Sheet` / `D03LaundryFrames03Towel`; mesh child names append `_Mesh`.
- Exports: `art/models/environment/d03_laundry_frames_03/d03_laundry_frames_03_{sheet,towel}.glb`
  with engine-normalized `.import` sidecars.
- Prefabs: `scenes/prefabs/environment/d03_laundry_frames_03_{sheet,towel}.tscn`.
- Reproduction/check tools: `tools/asset_production/d03_laundry_frames_03/`.

Each component is one closed mesh with two stable material slots:

| Component | Slot 0: body / sRGB swatch | Slot 1: hem / sRGB swatch |
| --- | --- | --- |
| Sheet | `laundry_sheet_body` / `#CCC9B5` | `laundry_sheet_hem` / `#AEB1A3` |
| Towel | `laundry_towel_body` / `#B98377` | `laundry_towel_hem` / `#9C746B` |

All use opaque Principled base colors, roughness 0.88, metallic 0, backface culling,
no emission. The author converts sRGB to linear material inputs. No texture dependencies,
embedded images, external materials or unsupported procedural shaders. No explicit LOD;
Godot automatic import LOD remains enabled. No repeat-placement/device budget is claimed.

The studio instances both export collections and **links**, rather than duplicates, the
existing frame's `export_d03_laundry_frames_01` collection. Its saved relative library path
is `//../d03_laundry_frames_01/d03_laundry_frames_01.blend`; keep that sibling source for
studio reproduction. The cloth GLBs do not contain or depend on frame geometry. Cameras,
lights, ground and one-metre reference are studio-only and excluded from both exports.
Existing frame source, GLB and prefab hashes are recorded as dependencies, not new output.

Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**.
`export.py` loads `tools/assets/blender/export_settings.json`, selects each named collection,
exports Y-up/normals/UVs, and disables animation/skins. All static modifiers are applied.

## Prefab and collision

Each wrapper retains its linked imported scene at identity-transform `Visuals/Model`.
No copied vertex data, editable-child overrides or runtime-authored hierarchy. The two
components are **soft hanging decoration, not freestanding rigid props or barriers**;
they add no collider. The existing short frame remains responsible for its posts and
three-box static compound. The mounting fixture proves exactly one existing frame body,
three existing shapes, and zero added cloth collision objects. No collision or movement
rule was changed, and no new physics acceptance is claimed.

The two wrappers and saved mounting fixture pass two byte-stable load/pack/save cycles
after first normalization. Scene UIDs and node identities survive; UIDs are embedded in
TSCNs (Godot produces no scene `.uid` sidecars). The check script's generated `.uid` is
retained. Final engine dependency traversal resolves the linked resources and their UIDs.
The headless import following first normalization is required to register newly saved
scene UIDs in a fresh runtime process.

## Evidence and validation

[Hero](d03_laundry_frames_03-evidence/hero.png),
[end-on side](d03_laundry_frames_03-evidence/side.png),
[fold/hem detail](d03_laundry_frames_03-evidence/detail.png),
[47 m / 42-degree overhead](d03_laundry_frames_03-evidence/overhead_47m_42deg.png).
All four isolated Blender Cycles CPU images use 32 samples, AgX, 1280x720, PNG compression
95 and no dithering; each is below 262 KB. The overhead is vertical-down, north-up,
47 m height, 42-degree **vertical** perspective FOV. The standing 720-pixel evidence cap
supersedes the older 800-pixel requirement. The side view intentionally crops the carrier
feet to inspect the complete cloth profile and its folded return.

Producer inspected all four final images. The two soft muted patches read as domestic
laundry in the hero/detail; their differing width, drop and fold count distinguish them
without color alone. In the calibrated overhead they occupy narrow roughly 28-pixel and
15-pixel-wide bands inside the existing approximately 80x28-pixel carrier footprint.
The rest of the frame stays open and quiet. This is intentionally subordinate dressing,
not an overhead gameplay identifier. These are not Godot gameplay captures or independent
art acceptance; populated court visibility remains a placement gate.

Final [validation.json](d03_laundry_frames_03-evidence/validation.json):

| Output | Source vertices | Exported vertices | Triangles | Meshes / surfaces |
| --- | ---: | ---: | ---: | ---: |
| Sheet | 1,452 | 1,584 | 2,900 | 1 / 2 |
| Towel | 1,100 | 1,200 | 2,196 | 1 / 2 |
| Set total | 2,552 | 2,784 | 5,096 | 2 / 4 |

- Zero degenerate source faces, zero non-manifold edges and zero degenerate GLB triangles.
- Source corner normals and decoded binary GLB normals are unit-length within 0.0001.
- Literal envelope, mounting pivot, transform, finite coordinates and line clearance pass.
- Both fresh saved-source re-exports are **byte-identical** to the committed GLBs.
- Pinned Godot headless import and final load/dependency/mounting checks exit 0, with no
  `ERROR` or `SCRIPT ERROR` lines. Actual imported bounds, materials and UIDs resolve.
- Both prefabs and the saved fixture pass two stable roundtrips; no frame payload changed.
- `gdstyle fmt --check` and lint with line length 100 / zero warnings pass.
- `production_checks.py` was deliberately not run, per decision 52.

Final payload identities copied from the validation receipt:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `.blend` | 164991 | `7d07eda7a8012974219a8d97adc737fc65ba7710a0c0dd544aafed0512e7d413` |
| `_sheet.glb` | 57416 | `965eb1f767c051c14efa6a2e4e3009e1d82f3fa7d8f018673d00988bf05cd4f7` |
| `_towel.glb` | 43976 | `af7edf7b6bada7db6dcdb7629b6edf0fb645ebaf91040fe3a57578b3b30cb03b` |

[manifest.json](d03_laundry_frames_03-evidence/manifest.json) hashes every produced payload,
excluding itself, plus the authorized sibling-status reconciliation. The concise
[checks.log](d03_laundry_frames_03-evidence/checks.log) distinguishes final passes from
initial diagnostics: one lint line was shortened; fresh scene UID checks required an
import after normalization; Blender normalized a relative library separator on Windows,
so validation compares normalized separators while retaining the exact relative dependency.
Initial scratch logs are outside the repository; none of those failed attempts is a pass.
Blender's pinned API emits future-removal `use_nodes` deprecation warnings, not export errors.

## Exact reproduction

Run from repository root in Git Bash. Isolated CLI/direct-file authoring is required by
the current brief because live Blender/Godot editor sessions must not be touched. Scene
text was subsequently loaded/packed/resaved headlessly. This does not synchronize any
separate open editor; no owner editor was used or modified.

```sh
NID=d03_laundry_frames_03
TOOLS=tools/asset_production/$NID
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
mkdir -p C:/tmp/ft/assets/$NID

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/author.py"
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . --script "$TOOLS/check_prefab.gd" -- --normalize
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . --script "$TOOLS/check_prefab.gd"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$TOOLS/validate.py"
"$GDSTYLE" fmt --check "$TOOLS/check_prefab.gd"
"$GDSTYLE" --max-line-length 100 --max-warnings 0 "$TOOLS/check_prefab.gd"
```

`validate.py` freshly opens the saved source and exports to
`C:/tmp/ft/assets/d03_laundry_frames_03/reexport/` before comparison. Standalone re-export:

```sh
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  "art/source/models/environment/$NID/$NID.blend" --python-exit-code 1 \
  --python "$TOOLS/export.py" -- "C:/tmp/ft/assets/$NID/manual-reexport"
```

After any final change, repeat the affected checks and pinned import, update this handoff
from the final validation receipt, then run `python "$TOOLS/record.py"` last. The source
`.blend` hash may change on fresh authoring; byte-identical re-export is measured from the
committed saved source, not a claim of byte-identical Blender file reconstruction.

## Remaining acceptance

- Independent technical/art review at the committed candidate.
- World integrator: saved court-edge placements, unblocked movement mouths, actor/aim
  visibility and actual gameplay-camera captures with the delivered cloth shapes.
- Gameplay/network owners: any later placement's contact/query/transport consequences;
  this visual-only component delivery does not re-certify the frame's gameplay behavior.
- Build/performance owners: packaged dependencies, automatic LOD appearance, repeated
  cloth cost, sustained device performance and Deck readability.

The earlier frame handoff's remaining cloth-review item now links this delivery, and only
that current document's manifest entry was refreshed; historical receipts are unchanged.
No world scene, road topology, registry, progress tracker, shared brief or TODO was changed.
