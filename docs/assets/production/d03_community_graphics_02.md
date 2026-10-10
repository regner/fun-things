# d03_community_graphics.02 — Entrance-number set

10 October 2026. **Original artwork, Blender carrier and bounded prefab checks delivered;
independent review and world acceptance pending.** Commissioned under [commission](commission.md)
and the current per-asset execution brief, superseding the historical concept-only restriction
in [community graphics](../d03_community_graphics.md). Producer: worker on `lane/a-d03g`, owning
original art/source, integration, tests and visual self-review. Accepting owners: independent
art/technical reviewer and world/gameplay integrator. Successful checks do not imply acceptance.

References: [Terrace Ward](../../concepts/districts-v1/terrace-ward.md), its
[asset breakdown](../../concepts/districts-v1/terrace-ward-assets.md), approved
[Stage 3 identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[Stage 4 streets](../../concepts/world-v1/stage-04-streets/README.md) and Petrol & Coral.
The preceding [laundry frame](d03_laundry_frames_01.md), [cloth](d03_laundry_frames_03.md),
[circle](d03_court_graphics_01.md), [play markings](d03_court_graphics_02.md) and
[community board](d03_community_graphics_01.md) establish the quiet domestic family palette.
Their current handoffs and the entrance-bay handoff contain no stale pending item for this
asset; no sibling document or evidence manifest needed a status edit.

## Design and approved carrier decision

Four original **01, 02, 03 and 04** number faces: large warm-ivory monoline numerals on muted
teal, with one small dusty-coral corner stroke. A thin dark edge and softly rounded corners
make a modest residential plaque, deliberately unlike loud commercial fascia art. Numerals
1–4 reuse the preceding court graphic's original path definitions; zero is an original new
rounded path. No external font, brand, downloaded image, image-to-mesh, grime or neon.

The family brief names a set but gives no count or literal copy. **Four two-digit options are
a provisional small set**, not a complete ten-digit alphabet, arbitrary-number generator,
district allocation or approved numbering scheme. One prefab defaults to 01; four committed
materials supply face-only selection. Numbers are decorative artwork, **never saved gameplay
identities, addresses used by code, interactions, wayfinding requirements or network state**.

The delivered [entrance bay](d03_apartment_family_08.md) has a .67 m blank pier but no isolated
number-face material slot. The existing 1.4 m city wall panel does not fit. The supervisor
explicitly rejected scaling that hardware and authorized **one original full-scale minimal
Blender plaque**, approximately .56 x .40 x .03–.04 m, with a dedicated face slot, visual-only
mounting, no sibling geometry changes and explicit saved identities. This delivery implements
that direction. It is not a duplicate or scaled export of shared sign hardware.

## Provisional dimensions and mounting

Godot local X/Y/Z in metres, with numeric bounds tolerance .001 m and coordinate/UV tolerance
.000001. Dimensions are authored provisional values, not inferred from a concept raster.
Blender +Y front maps to Godot -Z; Blender +Z maps to Godot +Y. Root and mesh have identity
transforms, metre units and no corrective scale/rotation.

| Contract | Value |
| --- | --- |
| Whole plaque width / height / depth | .560 / .400 / .032 |
| Local AABB minimum / maximum | (-.280,-.200,-.032) / (.280,.200,0) |
| Pivot | Centre of wall-contact back plane, (0,0,0), not ground contact |
| Back / front face planes | Z=0 / Z=-.032 |
| Outer rounded-corner radius | .018; four segments per quarter-circle |
| Front/back bevel depth and inset | .003 / .003; flat front radius .015 |
| Full face UV rectangle | .560 x .400; geometry clips rounded corners and .003 inset |
| Safe copy inset | .020 m on every side (10 texels) |
| Nominal numeral box / stroke | .124 x .206 / .022 |
| Mount relative to unrotated entrance bay | (.785,1.850,-6.000), unit scale, zero rotation |
| Mounted AABB | (.505,1.650,-6.032) / (1.065,2.050,-6.000) |
| Left/right pier edges and clearance | X=.450 / 1.120; .055 m on both sides |

The plaque sits between the warm portal and stair-core surround, below the head brow and
above the floor ribbon. Its backing contacts the existing flat structural wall exactly; it
adds no gap, arbitrary offset, external step or door obstruction. The front projects only
32 mm. The saved mounting example is `tools/asset_production/d03_community_graphics_02/check_scene.tscn`:
one unchanged entrance prefab and one plaque at this transform. This is a review fixture,
not an authored world placement. Apply any whole-building rigid transform to both together;
never scale the carrier. The original closed doors remain closed facade decoration.

## Source, export, artwork and material contract

- Source: `art/source/models/environment/d03_community_graphics_02/d03_community_graphics_02.blend`.
- Collection: `export_d03_community_graphics_02`.
- Root / mesh / mesh data: `D03CommunityGraphics02`, `D03CommunityGraphics02_Mesh`,
  `D03CommunityGraphics02_Geometry`.
- Export: `art/models/environment/d03_community_graphics_02/d03_community_graphics_02.glb`
  and its committed `.import`.
- Four PNGs: `art/textures/environment/d03_community_graphics_02/entrance_{01,02,03,04}_albedo.png`
  and their committed `.import` metadata.
- Four materials: `art/materials/environment/d03_community_graphics_02/entrance_{01,02,03,04}.tres`.
- Single prefab: `scenes/prefabs/environment/d03_community_graphics_02.tscn`, default 01.
- Recipes/checks: `tools/asset_production/d03_community_graphics_02/`.

`author.py` builds a single closed original rounded plaque with four profile rings and no
applied runtime modifiers. `artwork.py` reproducibly draws the four faces in Pillow **12.3.0**,
4x supersampled then Lanczos-reduced. Reused original numeral paths, material construction
helper and pure binary-accessor decoder are imported read-only from the preceding court
asset's tools rather than privately duplicated. Their dependency hashes are in validation.json.

One mesh, two stable surfaces:

| Slot | Blender material | Runtime use |
| --- | --- | --- |
| 0 | `entrance_number_face` | `entrance_01.tres` default, or 02/03/04 face-only material |
| 1 | `entrance_plaque_edge` | Original dark edge, bevel and back; never override |

Face: roughness .84, metallic 0, opaque/back-culled, no emission, alpha, normal map or ORM.
Edge: roughness .60, metallic 0, sRGB **#294B50**. Face palette: teal **#587D7C**, ivory
**#CECDB8**, coral **#B98377**, matching the court/community artwork and dusty-coral cloth.
Blender converts fallback swatches to linear Principled values. Godot uses white texture
multipliers. No real lights, rig, animation, sockets, physics state or destruction design.

Each texture is **280x200 RGB8 sRGB**, approximately **500 texels/metre**, one non-tiled face.
UV0 in Blender: U=(.28-X)/.56, V=(Z+.20)/.40. In exported image coordinates, U runs from
screen left to right when viewed from the front, and V from top to bottom. Binary winding/UV
checks and all renders establish upright, unmirrored numerals. Blank margins protect copy
from the rounded corner clipping and bevel.

Clamp, linear mipmap filtering, eight generated mip levels, lossless import, no automatic 3D
compression conversion. Four imported RGB8 textures total **895,704 CPU bytes including mips**;
this is not measured GPU allocation or an accepted device budget. The source stores an unpacked
relative link to the committed 01 PNG. Export temporarily disconnects and restores that link:
**zero embedded GLB images**. No generic tiled-paving/road-tool compatibility is claimed.
No explicit LOD; per-import automatic LOD generation remains enabled and requires visual review.

Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. The exporter loads
`tools/assets/blender/export_settings.json`, filters the named collection, converts axes once,
exports normals/UVs and disables animation/skins. The hidden one-metre reference is excluded.
Pinned Godot **4.8.dev7.official.c971f93e7**. No shared source/export/prefab was modified.

## Prefab, variant selection, collision and identities

The original imported model remains at identity-transform `Visuals/Model`. The single saved
editable-child override targets only
`Visuals/Model/D03CommunityGraphics02/D03CommunityGraphics02_Mesh`, surface 0. To select 02,
03 or 04, assign the corresponding committed material to that **surface override only** in a
saved instance/variant. Do not replace the mesh or apply a whole-mesh material override.
There is no runtime number selector, dynamic text system or extra prefab per number.

This follows the authorized narrow static-artwork override exception in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement): two complete post-normalization
save/reload cycles prove byte-stable scenes/materials and unchanged identities/UIDs. A fresh
normalization process also preserves its initial bytes; two fresh runtime receipts agree.
All four face choices are exercised against the actual imported mesh, leaving its resource
identity and edge material unchanged. No copied vertex data or runtime-authored hierarchy.

The plaque is **flush wall-mounted decoration**, not a freestanding obstacle. It has zero
collision bodies/shapes. The unchanged bay owns one existing static core box (6,3.2,12),
centred at (0,1.6,0); the fixture proves no duplicate wall collider. This adds no movement,
query or multiplayer rule and does not recertify the bay's historical gameplay evidence.

The brief forbids live-owner editor access, so direct source/scene/material text authoring
was followed by pinned headless import and load/pack/save/reload checks. The owned checker
preserves inline UIDs and explicitly retains dependency UIDs where the runtime saver would
omit them. **Every saved ext_resource has a resolving `uid=`, every header a UID, and every
saved node a `unique_id`.** Scene/material UIDs are embedded; Godot creates no scene UID
sidecar. The generated check-script `.gd.uid` is committed. This does not synchronize or
claim inspection of a separate open editor; no live session was touched.

## Evidence and measured checks

[Mounted hero](d03_community_graphics_02-evidence/hero.png),
[oblique side](d03_community_graphics_02-evidence/side.png),
[four-number detail](d03_community_graphics_02-evidence/detail.png),
[47 m / 42-degree overhead](d03_community_graphics_02-evidence/overhead_47m_42deg.png).
All four final isolated Blender renders were inspected: Cycles CPU, 32 samples, AgX,
1280x720 RGB8 PNG, compression 95, no dithering/post-quantization. Each is below 286 KB.
The standing 720-pixel evidence cap supersedes the older 800-pixel requirement.

Hero and side show upright copy, domestic scale and the clear pier fit. The detail shows all
four options in a temporary isolated swatch layout; those review copies are not separate
exports, world placements or geometry in the saved source. Preview loads the unchanged
entrance-bay source/studio and appends the new plaque only in the isolated process, never
saving either source. All source/dependency hashes remain unchanged.

The overhead is true vertical-down, north-up perspective at (0,0,47), **42-degree vertical
FOV**. The building top dominates and **occludes the small vertical plaque**; no number is
readable. This is an honest placement-scale limitation, not grounds for enlarging or tilting
the plaque. Never make these numerals essential navigation. These are source-studio images,
not populated Godot gameplay, moving-camera, visibility or independent art acceptance.

Final [validation.json](d03_community_graphics_02-evidence/validation.json):

- **156 triangles; 80 source / 280 exported vertices; one mesh / two surfaces.**
- Zero non-manifold edges, zero source degenerate faces and zero binary GLB degenerate triangles.
  Positive closed source volume, finite positions, unit source/export normals and outward winding.
- Literal AABB, wall-back pivot, identity transforms, one front polygon and upright UV mapping pass.
- Fresh saved-source GLB re-export and all four original PNG reproductions are **byte-identical**.
- Three independent artwork tests cover reproduction, literal palette/margin probes and distinct
  populated numeral regions/landmarks with a shared leading zero.
- Final pinned import, two byte-stable resource roundtrips and two fresh runtime checks exit 0
  without `ERROR`/`SCRIPT ERROR` lines. Explicit UIDs/node identities and imported mips pass.
- All four face-only options retain the same mesh and edge; mounted .055 m pier clearances pass.
- Python syntax, `gdstyle fmt --check` and 100-character/zero-warning lint pass.
  `production_checks.py` deliberately not run, per decision 52.

Final payload identities copied from the validation receipt:

| Payload | Bytes | SHA-256 |
| --- | ---: | --- |
| `.blend` | 100,488 | `f3a6145195ec3d2f845ddb96df890662755ac71355e5680af95a881e4b3e2a44` |
| `.glb` | 12,148 | `7a1fe35d2ec318d4b07b09689b02b92e57e5d0f4dda46f3ac8c10d07ff753e4a` |

[manifest.json](d03_community_graphics_02-evidence/manifest.json) hashes every produced file
except itself. [checks.log](d03_community_graphics_02-evidence/checks.log) retains concise final
results and initial corrected findings: an in-memory PNG reproduction needed an explicit
format; two lint allocation-in-loop warnings were fixed by extracting scene repacking and
reusing the import-config object. An initial shell payload truncated the test file, which was
completed before execution. Blender emits its pinned `use_nodes` future-removal warning;
Godot import emits the existing toolkit version advisory. No diagnostics were suppressed,
no failed step is counted as passing, and warning-free import is not claimed.

## Exact reproduction

From the worktree root in Git Bash, Python with Pillow 12.3.0. Preserve committed import
sidecars and identities. No live Blender/Godot sessions. Scratch and raw logs stay outside Git.
`record.py` runs last after final checks and any handoff changes.

```sh
NID=d03_community_graphics_02
T=tools/asset_production/$NID
S=C:/tmp/ft/assets/$NID
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
STYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
mkdir -p "$S"
python "$T/artwork.py"
python "$T/test_artwork.py" > "$S/artwork-check.log" 2>&1
# Reauthor only when intentionally changing source; saved-source validation is below.
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/author.py" > "$S/author.log" 2>&1
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" > "$S/validate.log" 2>&1
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/preview.py" > "$S/preview.log" 2>&1
python -m py_compile "$T"/*.py && echo PYTHON_COMPILE_PASS > "$S/python-check.log"
"$STYLE" fmt --check "$T/check_prefab.gd" > "$S/format.log" 2>&1
"$STYLE" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd" > "$S/style.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-before-roundtrip.log" 2>&1
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

Reauthoring may change Blender container bytes; update handoff hashes from the final receipt
before recording. For an unchanged source, skip `author.py`. `validate.py` reopens that source,
re-exports to scratch and compares the complete GLB. Standalone saved-source export:

```sh
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  "art/source/models/environment/$NID/$NID.blend" --python-exit-code 1 \
  --python "$T/export.py" -- "$S/manual-reexport"
```

## Remaining acceptance

- Independent technical/art review at the committed candidate; provisional four-number set,
  copy and dimensions approval.
- World integrator: saved entrance placements, actual roof/actor occlusion and court-mouth
  clearance, without treating decorative numbers as gameplay identities or navigational cues.
- Visual/gameplay owners: populated Godot lighting, moving-camera mip behavior and any later
  placement's actual contact/query/network consequences.
- Build/performance owners: packaged dependencies, repeated-placement/texture cost, automatic
  LOD appearance, sustained target-device performance and Deck readability.

No world scene, road topology, registry, progress tracker, shared brief, sibling payload or
TODO changed. This is an importable tested artwork candidate, not full game/world acceptance.
