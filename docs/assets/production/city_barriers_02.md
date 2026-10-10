# city_barriers.02 — Landward-rail assembly reference

10 October 2026. **Saved assembly and bounded validation delivered; independent
review and world/gameplay/device acceptance pending.** Commissioned under the
[production commission](commission.md) and current per-asset common brief, which
supersede the earlier concept-only restrictions in [city_barriers](../city_barriers.md).
Producer: commissioned implementation specialist, branch `lane/a-barr2`.
Supervisor owns independent review and integration.

## Design and dimensions

This is an **assembly reference, not another rail model**. It selects the existing
straight/landward prefab from [city_quay_furniture.02](city_quay_furniture_02.md),
which is already produced and accepted in the source/export/prefab scope on `main`.
The original dark petrol tubes, slate shoes/caps, sparse amber collars and round
surface-mount flanges are reused without mesh, material or collision overrides.
No geometry, source model, texture, new interaction or world placement is added.

One standalone span demonstrates the landward hardstanding interface. Terminal
returns are separately assigned to `city_barriers.04`; this reference does not
invent replacement terminal hardware. The district concept's candidate use across
all nine districts does not authorize placements or close route/visibility gates.

All dimensions below **inherit the kit's provisional authored values**, not
measurements from concept art or newly approved infrastructure dimensions:

| Interface | Godot local metres |
| --- | --- |
| Installation datum / reference pivot | Ground-centred `(0, 0, 0)`, mounting surface Y=0 |
| Run direction | X axis; unit scale and identity rotation |
| Post centres | `(-1.5, 0, 0)` and `(1.5, 0, 0)` |
| Span connector spacing | 3.000 |
| Upper tube centre / diameter | Y=0.950 / 0.100 |
| Lower tube centre / diameter | Y=0.480 / 0.060 |
| Landward flange | Diameter 0.320, height 0.050 |
| Full AABB minimum | `(-1.660, 0, -0.160)` |
| Full AABB maximum | `(1.660, 1.060, 0.160)` |
| Full size, X/Y/Z | **3.320 × 1.060 × 0.320** |
| Bounds tolerance | ±0.001 |

The selected hardstanding must support both complete flange footprints. Do not
sink the round feet below the surface or use a root-scale correction. Blender +Z
maps to Godot +Y; Blender +Y maps to Godot -Z. No independent sockets or alternate
mounting datum are introduced.

**Do not chain complete reference prefabs at a shared post:** this doubles both
supports and collision envelopes. For a longer run, the kit owns span/post component
composition with one support per junction and one continuous collider per run.
Keep walking lines outside the 0.320 m installation depth; deliberately leave access
openings in authored world placement. This record does not establish their widths,
locations, removable states, destruction, climbing or impact response.

## Source, exports and materials

The complete reference is `scenes/prefabs/environment/city_barriers_02.tscn`.
It contains one identity-transform instance at `LandwardRail` of
`scenes/prefabs/environment/city_quay_furniture_02_straight_landward.tscn`.
That existing prefab retains its linked import at `Visuals/Model`, and its two
landward posts at `Visuals/Post0` and `Visuals/Post1`.

Source lineage, unchanged:

- `art/source/models/environment/city_quay_furniture_02/city_quay_furniture_02.blend`
- Collection `export_city_quay_furniture_02_straight` →
  `art/models/environment/city_quay_furniture_02/city_quay_furniture_02_straight.glb`
- Collection `export_city_quay_furniture_02_post_landward` →
  `art/models/environment/city_quay_furniture_02/city_quay_furniture_02_post_landward.glb`

Both GLBs retain their existing import sidecars. Root/mesh names and transforms,
source provenance, opaque Principled materials `quay_dark_metal`,
`quay_hardware_slate` and `quay_working_amber` remain kit-owned. No downloaded or
substitute geometry, duplicate `.blend`/GLB carrier, material override, embedded
image, texture, rig, animation or new LOD is required for this reference.
No per-reference `export.py` is needed: `validate.py` uses the shared
`tools/assets/blender/export_settings.json` to reexport the two reused collections
to scratch and compare bytes, never to overwrite accepted files.

`author.py` opens the original source without saving, reuses the source kit's
preview/aim helpers, links its unchanged mesh data into the existing Blender studio
and renders precisely one straight span and its two landward posts. The saved Godot
scene, not a runtime script, owns the deliverable composition.

## Prefab, collision and checks

The outer assembly adds **no second collider**. `LandwardRail/Collision/RailBody`
is the existing static body, layer 1 / mask 0. Its one box is 3.320 × 1.060 × 0.320 m,
centred at `(0, 0.530, 0)`. It deliberately fills the under-rail gaps and includes
the feet. The slim visual tubes are not a promise of physical crawl-through gaps.
Decoration remains separate from collision inside the reused prefab.

Pinned Godot **4.8.dev7.official.c971f93e7** checks:

- Reference, inherited test fixture and every dependency load with registered UIDs.
- Both owned scenes pack/save/reload/resave byte-identically; existing dependencies
  are never resaved. Scene UIDs and node identities are saved inline; the script's
  `.gd.uid` is retained.
- Exactly one unchanged landward prefab, three imported meshes, seven surfaces,
  correct post positions, identity import transforms and measured assembly bounds.
- Exactly one inherited static body/box; a ray at Y=0.5 hits the rail and a ray at
  Y=1.2 passes above it.
- The production `ActorMotion.step` runs 48 ticks for contact and bypass in both
  AUTHORITY and REPLAY, using the production radius 0.35 m / height 1.8 m capsule.
  Contact ends at Z=-0.511067390 m; unobstructed bypass at X=2.5 ends at
  Z=2.000000715 m. Authority/replay results match. Allowed precontact gap is 0.030 m;
  numeric tolerance is 0.00001 m. These are bounded physics tests, not multiplayer
  transport, actual car handling or placement acceptance.

The owned `check.gd` subclasses the kit's existing validation helpers instead of
copying bounds, topology or motion implementations. It overrides only the test
entrypoint, adding reference ancestry/identity checks and writing its own receipt.
The owned saved `check_scene.tscn` instances the kit's existing collision-only
floor/capsule fixture and the actual reference. No shared fixture files changed.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**:

| Geometry | Source vertices | Triangles | Export vertices | Meshes / surfaces |
| --- | --- | --- | --- | --- |
| Straight span, one instance | 64 | 120 | 128 | 1 / 1 |
| Landward post, each of two | 592 | 1,148 | 592 | 1 / 3 |
| **Assembled reference** | **1,248** | **2,416** | **1,312** | **3 / 7** |

Zero degenerate source faces, zero degenerate triangles and zero non-manifold
edges. Maximum source normal-length error **1.47e-7**. Both fresh dependency
exports are **byte-identical** to accepted GLBs; source bytes remain unchanged.
These are counts, not an accepted repeat-placement performance budget.

Repository production checks passed: owned-script style/format/compilation,
**17 Python tests**, **149 GUT tests / 6,768 assertions**, and the deliberate-failure
negative control (expected exit 1). Asset script independently passes gdstyle 0.3.0.
No known-failure exemptions were needed. Headless import reports only the existing
MCP toolkit warning that Godot 4.8 is newer than its tested 4.7; asset check logs
contain no errors or warnings. No broad diagnostic suppression was added.

## Evidence and reproduction

[Hero](city_barriers_02-evidence/hero.png),
[side](city_barriers_02-evidence/side.png),
[landward flange detail](city_barriers_02-evidence/detail.png),
[47 m / 42° overhead](city_barriers_02-evidence/overhead_47m_42deg.png).
All four were inspected: smooth quiet rails, visible round flange and no new busy
accents. At gameplay scale the rail reads as a thin line with two small feet; it
is not an oversized gameplay marker. Actual actor contrast and populated-engine
visibility remain untested.

These are isolated Blender Cycles CPU/32-sample, AgX, 1280×720 RGB renders, not
engine captures. Overhead: vertical-down perspective, 47 m above ground,
42° vertical FOV, Blender +Y image-up. PNGs use seven significant bits per channel
and maximum compression, **375,561–399,383 bytes each**. The current brief's
720-pixel maximum supersedes the older 800-pixel example.
[validation.json](city_barriers_02-evidence/validation.json) records measurements,
source/dependency hashes and test results;
[manifest.json](city_barriers_02-evidence/manifest.json) hashes every produced
payload except itself. Raw logs/reexports stay in scratch, not the repository.

The brief forbids live MCP/windowed editors. Prefab text was authored directly,
then normalized and reloaded in isolated headless Godot. No owner editor session
was touched; no open-editor synchronization is claimed.

Run from repository root in Git Bash:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
NID=city_barriers_02
SCRATCH="C:/tmp/ft/assets/$NID"
mkdir -p "$SCRATCH"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
python - <<'PY'
from pathlib import Path
from PIL import Image, ImageOps
for path in Path('docs/assets/production/city_barriers_02-evidence').glob('*.png'):
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
# The runner requires a fresh output directory; use a new suffix for a subsequent run.
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
```

## Remaining acceptance

- Supervisor: independent technical/art review of this committed reference.
- Layout/interface owners: approve provisional dimensions, hardstanding attachment
  and sparse placements; do not double supports by chaining standalone wrappers.
- World/art owners: actual access routes, feet/target visibility, engine lighting
  and populated gameplay-camera contrast. No district scene changed.
- Gameplay/network owners: actual vehicle contacts/turns and separate-process
  multiplayer transport/admission/prediction checks at selected placements.
- Device/performance owners: packaged builds, repeated-placement GPU/draw cost and
  Deck performance. Headless tests and Blender renders do not certify these gates.

No new model dependency or source/prefab blocker remains. No shared queue, progress,
brief, project setting, sibling asset or runtime gameplay code changed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
