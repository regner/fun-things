# city_barriers.04 — Rail-terminal assembly reference

10 October 2026. **Saved assembly and bounded validation delivered; independent
review and world/gameplay/device acceptance pending.** Commissioned under the
[production commission](commission.md) and current per-asset common brief, which
supersede the concept-only restrictions in [city_barriers](../city_barriers.md).
Producer: commissioned implementation specialist on `lane/a-barr2`. Supervisor
owns independent review and integration.

## Design and dimensions

This is an **assembly reference, not another post model**. It selects the existing
landward terminal/return prefab from [city_quay_furniture.02](city_quay_furniture_02.md),
already produced and accepted in the bounded source/export/prefab scope on `main`.
It matches the round-flange hardstanding mount selected by the preceding
[landward-rail reference](city_barriers_02.md). Neither sibling nor source kit was
changed. No substitute geometry, additional post, new material or world placement
is introduced.

The reused closed hairpin ends the two-height rail with a rounded return. Dark
petrol metal, slate shoe/cap and one narrow amber collar preserve the quiet family
language. This is low-rail terminal hardware, **not** the tall chain-link terminal
or bracing system assigned to `city_barriers.06`. District-wide candidate use does
not authorize fence layouts, access restrictions, removable/destructible states,
climbing or new interactions.

All dimensions **inherit the kit's provisional authored values**, not measurements
from concept images or newly approved infrastructure dimensions:

| Interface | Godot local metres |
| --- | --- |
| Reference pivot / mounting datum | Ground-contact post centre `(0, 0, 0)`, Y=0 |
| Upper/lower attachment ends | `(0, 0.950, 0)` / `(0, 0.480, 0)` |
| Return direction / outer reach | +X / **0.535** from post centre |
| Hairpin centreline radius | 0.235 |
| Landward flange | Diameter 0.320, height 0.050 |
| Post height | 1.060 |
| Full AABB minimum | `(-0.160, 0, -0.160)` |
| Full AABB maximum | `(0.535, 1.060, 0.160)` |
| Full size, X/Y/Z | **0.695 × 1.060 × 0.320** |
| Envelope tolerance | ±0.001 |

The pivot is **not the asymmetric footprint centre**. The flange rests on the
mounting surface; root scale and rotation are identity. Blender +Z maps to Godot
+Y and Blender +Y maps to Godot -Z. The reference adds no alternate socket/datum.
Quay square-plate and deck rectangular-plate variants remain kit-owned; this
landward reference does not silently select either of those mounting interfaces.

### Joining and clearance contract

Incoming rails approach the supporting post from -X. Both attachment heights agree
with `city_barriers.02`'s straight span; the terminal then projects +X beyond the
post. For the opposite end, rotate the **whole authored terminal assembly** 180°
around Y, never mirror/negative-scale or rotate the imported model to correct axes.

**Do not butt complete standalone wrappers at a shared post.** In particular, do
not simply put this reference at X=+1.5 beside a complete `city_barriers.02` instance:
that doubles the final post and overlaps collision. A saved longer assembly must
use the kit's linked components with one support per junction, replacing the last
span support with the terminal support, and one continuous simple collision envelope
per run. Existing standalone references remain useful interface examples, not a
runtime rail-construction API.

Reserve the full +0.535 m return reach, including below the visible tube. A pair of
opposing returns consumes **1.070 m** of the distance between post centres before
any clear opening remains. The kit's test-only 1.400 m opening is a prior bounded
sample, not a placement delivered or a newly approved route width here. Keep feet
and returns outside the chosen walking/vehicle lines, support the full round flange
on hardstanding, and leave intentional access gaps in authored world placement.
Actual route widths, turn paths and street sections remain layout-owner gates.

## Source, exports and materials

Deliverable: `scenes/prefabs/environment/city_barriers_04.tscn`. Its only child,
`RailTerminal`, is an identity-transform instance of
`scenes/prefabs/environment/city_quay_furniture_02_end_landward.tscn`.
The existing prefab retains its primary import at `Visuals/Model` and its single
landward post import at `Visuals/Post0`, both at identity transforms.

Unchanged source lineage:

- `art/source/models/environment/city_quay_furniture_02/city_quay_furniture_02.blend`
- `export_city_quay_furniture_02_end` →
  `art/models/environment/city_quay_furniture_02/city_quay_furniture_02_end.glb`
- `export_city_quay_furniture_02_post_landward` →
  `art/models/environment/city_quay_furniture_02/city_quay_furniture_02_post_landward.glb`

Kit root/mesh names, original Blender provenance, metre units, import sidecars and
material slots are preserved. Materials are opaque Principled `quay_dark_metal`,
`quay_hardware_slate` and `quay_working_amber`; the return uses only dark metal.
No material overrides, textures, embedded images, new `.blend`/GLB carrier, animation,
rig, collision mesh, runtime geometry or extra LOD is required for this reference.

Owned tools in `tools/asset_production/city_barriers_04/`:

- `author.py` opens the accepted source without saving, reuses the source kit's
  preview/aim helpers and links unchanged source meshes into the existing studio.
  It renders only this reference's return and one landward post.
- `export.py` reads the shared `tools/assets/blender/export_settings.json` and
  fresh-exports just the two dependency collections to scratch, never over accepted
  files. Collection filters, Y-up conversion and static export rules stay shared.
- `validate.py` reuses the kit's actual topology/accessor/normal validator, redirecting
  only its scratch-export lookup. It also checks the asymmetric assembled bounds,
  sums instance counts and proves the source file remains byte-identical. Imported
  tool bytecode is disabled to avoid writing into the dependency's directory.
- `check.gd` subclasses the kit's engine checker; the saved `check_scene.tscn`
  instances its existing collision-only floor/capsule fixture and this reference.
  No shared fixture, source, brief or runtime script is changed.

## Prefab, collision and validation

The outer reference adds **no collider**. The inherited
`RailTerminal/Collision/RailBody` is the sole static body, layer **1**, mask **0**,
with one **0.695 × 1.060 × 0.320 m** box centred at `(0.1875, 0.530, 0)`.
It deliberately fills the spaces below and inside the return as well as covering
the mounting foot; visual gaps are not physical crawl-through openings. Decoration
and blocking remain separate in the existing prefab.

Pinned Godot **4.8.dev7.official.c971f93e7** establishes:

- Reference, inherited fixture and recursive dependencies load with registered UIDs.
- Both owned scenes pack/save/reload/resave byte-identically. Scene UIDs and node
  identities are retained inline; the script's `.gd.uid` is committed. Existing
  dependencies are not resaved.
- One unchanged terminal prefab, two imported meshes/four surfaces, the single post
  at the origin, identity imported transforms and the expected asymmetric bounds.
- One inherited body/box; low ray blocked, Y=1.2 ray clear. An extra low ray at
  X=0.520, Y=0.2 hits the return envelope; rays at X=-0.170 and X=0.545 clear both
  ends of the footprint. These checks catch an incorrectly centred terminal box.
- Production **`ActorMotion.step`**, radius **0.35 m**, height **1.8 m**, runs **48
  ticks** per contact and bypass in AUTHORITY and REPLAY. Both modes agree:
  X=0.2 contact stops at **Z=-0.511067390 m**; X=2.5 bypass reaches
  **Z=2.000000715 m**. Precontact gap is limited to 0.030 m with 0.00001 m numeric
  tolerance. These are bounded actor/query results, not car or network acceptance.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**:

| Geometry | Source vertices | Triangles | Export vertices | Meshes / surfaces |
| --- | --- | --- | --- | --- |
| Terminal return | 304 | 604 | 336 | 1 / 1 |
| Landward post | 592 | 1,148 | 592 | 1 / 3 |
| **Complete reference** | **896** | **1,752** | **928** | **2 / 4** |

**Zero degenerate faces/triangles and zero non-manifold edges.** Maximum normal
length error: source **1.47e-7**, export **9.71e-8**. Both fresh GLBs are
**byte-identical** to the accepted dependencies. Source remains unchanged. These
counts do not establish an accepted repeated-placement performance budget.

Repository production checks passed: owned-script style/format/compilation,
**17 Python tests**, **149 GUT tests / 6,768 assertions**, and the intentional-failure
negative control (expected exit 1). Owned GDScript passes **gdstyle 0.3.0** with no
warnings. Initial two line-length warnings were corrected before the final run.
No known-failure exemptions were needed. Import emits the existing MCP toolkit
Godot-4.8-versus-tested-4.7 warning; final asset-check and Blender logs have no
errors/warnings. No diagnostic suppression was added.

## Evidence and reproduction

[Hero](city_barriers_04-evidence/hero.png),
[side](city_barriers_04-evidence/side.png),
[closed return detail](city_barriers_04-evidence/detail.png),
[47 m / 42° overhead](city_barriers_04-evidence/overhead_47m_42deg.png).
All four were inspected: rounded closed return, seated flange/collar and consistent
quiet materials. Overhead it reads as a tiny post with a short projecting line,
not an oversized marker; the curved return is a close-view detail. Actual actor
contrast and populated-engine visibility remain open.

These are isolated Blender Cycles CPU/32-sample, AgX, **1280×720 RGB** renders,
not Godot captures. Overhead is vertical-down perspective, height **47 m**, vertical
FOV **42°**, Blender +Y image-up. PNGs use seven significant bits per channel and
maximum compression, **344,003–377,048 bytes** each. The current 720-pixel cap
supersedes the older example's 800-pixel view.
[validation.json](city_barriers_04-evidence/validation.json) records measurements,
dependency hashes and checks; [manifest.json](city_barriers_04-evidence/manifest.json)
hashes every produced payload except itself. Raw logs and fresh exports stay in
`C:/tmp/ft/assets/city_barriers_04/`, not the repository.

The brief prohibits live MCP/windowed editor operations. The prefab was text-authored,
then normalized and reloaded in isolated headless Godot. No owner editor session
was touched and no synchronization of an independently open scene is claimed.

Run from repository root in Git Bash:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
NID=city_barriers_04
SCRATCH="C:/tmp/ft/assets/$NID"
mkdir -p "$SCRATCH"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py already invokes export.py and compares both fresh exports.
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
python - <<'PY'
from pathlib import Path
from PIL import Image, ImageOps
for path in Path('docs/assets/production/city_barriers_04-evidence').glob('*.png'):
    with Image.open(path) as image:
        ImageOps.posterize(image.convert('RGB'), bits=7).save(
            path, optimize=True, compress_level=9)
PY
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script "res://tools/asset_production/$NID/check.gd" -- --normalize
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script "res://tools/asset_production/$NID/check.gd"
timeout 60 "$(mise which gdstyle)" check "tools/asset_production/$NID/check.gd"
# The runner requires a fresh output directory; choose a new suffix for repeat runs.
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
```

## Remaining acceptance

- Supervisor: independent technical/art review at the committed reference.
- Layout/interface owners: approve provisional dimensions, hardstanding mount and
  component-level joining; one support per junction and full return reach reserved.
- World/art owners: actual access routes, feet/target visibility, populated gameplay
  camera and engine lighting. No district scene or road-tool placement changed.
- Gameplay/network owners: actual vehicle contacts/turns and separate-process
  multiplayer transport/admission/prediction at chosen placements.
- Device/performance owners: packaged builds, repeated-placement draw cost and Deck
  performance. Headless tests/Blender images do not close these gates.

No source/dependency/prefab blocker remains. No shared queue, progress, brief,
project setting, sibling asset or runtime gameplay code was changed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
