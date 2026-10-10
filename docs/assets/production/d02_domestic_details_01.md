# d02_domestic_details.01 — Short garden-wall run

**Source/export, linked prefab and bounded headless checks delivered; independent
review and placement acceptance pending.** Production commissioned by Regner under
[the commission](commission.md) and the current per-asset production brief. Original
Blender construction by the commissioned worker on `lane/a-d02`; supervisor/reviewer
owns acceptance and world integration. No live Blender/Godot session was touched.

Family: [Domestic boundary and porch details](../d02_domestic_details.md).
Direction: [The Crescents](../../concepts/world-v1/stage-03-district-identities/README.md),
[selected revision 02](../../concepts/districts-v1/02-the-crescents-v02.png), and
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).
The production commission supersedes historical concept-only restrictions.

## Design and dimensions

A short low rendered boundary with a quiet slate plinth and four chunky ivory
coping stones. The shallow weathered cap profile, softened corners and broad
material bands make a domestic wall rather than a traffic barrier. No brick noise,
bright accent strip, gate, interior, animation, destruction or interaction is added.
Palette matches the delivered `d02_house_family_01`: warm render `#ACA69E`, ivory
trim `#D4CEBB`, slate plinth `#58636B`. These are original flat-color materials, not
sampled textures. No downloaded/purchased mesh, external artwork or image-to-mesh.

All dimensions below are **provisional authoring proposals**, not measurements from
concept imagery or approved plot placement. They follow the standing dimension rule.

| Contract | Metres, Godot local axes |
| --- | --- |
| Whole visual size X / Y / Z | 3.200 / 0.940 / 0.360 |
| Whole visual AABB | (-1.600, 0, -0.180) to (1.600, 0.940, 0.180) |
| Render core | 3.200 long, 0.260 thick; Y=0.140 to 0.800 |
| Continuous plinth | 3.200 long, 0.300 thick; Y=0 to 0.140 |
| Coping | 0.360 deep; Y=0.800 base, 0.910 outer shoulder, 0.940 crest |
| Coping rhythm | Four nominal 0.800 spans; three 0.006 internal joints |
| Origin | Ground-centred footprint at (0,0,0) |
| Straight module interfaces | X=-1.600 and X=1.600, centreline Z=0 |
| Numeric tolerance | 0.001 for bounds/datum; normals within 0.0001 of unit length |

A straight repetition may translate roots by exactly 3.200 m along X, without
scaling; the box ends meet with no collision gap. This is a section/interface
contract, not authored placement. Wall ends have no projecting post or end cap.
Maintain the same coping profile/materials for compatible domestic boundaries.
Return junctions and home setbacks are placement/assembly review, not proven here.
No sockets are required for a static run. Blender +Z maps to Godot +Y, Blender +Y
to Godot -Z; the symmetric wall runs along +X. All export members have identity
transforms, unit scale and metre units; a hidden non-export 1 m cube is retained.

## Source, exports and materials

- Source: `art/source/models/environment/d02_domestic_details_01/d02_domestic_details_01.blend`.
- Collection: `export_d02_domestic_details_01`.
- Export root: `D02DomesticDetails01`; child: `D02DomesticDetails01_Mesh`.
- GLB: `art/models/environment/d02_domestic_details_01/d02_domestic_details_01.glb`
  with its engine-normalized `.import`.
- Prefab: `scenes/prefabs/environment/d02_domestic_details_01.tscn`.
- Reproducible source/export/validation/render/receipt scripts:
  `tools/asset_production/d02_domestic_details_01/`.

One static mesh, three exported surfaces, in actual order:

| Slot | Material | Roughness | Metallic |
| --- | --- | --- | --- |
| 0 | `crescents_warm_render` | 0.65 | 0 |
| 1 | `crescents_slate_plinth` | 0.75 | 0 |
| 2 | `crescents_ivory_trim` | 0.55 | 0 |

Opaque Principled materials, sRGB swatches converted to linear values in the author
script, backface culling enabled. No textures, embedded images, custom shaders,
external material resources or remaps are needed. Six closed components are joined
into one editable mesh; bevel and weighted-normal modifiers are applied before save.
Blender/glTF triangulates at export. No skeletal rig, clips, morphs or state variants.

Blender **5.2.2 LTS** build `d13f752e3b9c`, glTF exporter **5.2.40**. Export loads the
shared `tools/assets/blender/export_settings.json` contract, selects the named
collection, and disables animation/skin output. Studio and metre fixture never
export. Godot **4.8.dev7.official.c971f93e7** imports default automatic LODs/shadow
meshes at scale 1. No LOD or repeat-placement performance budget is claimed.

## Prefab and collision

Saved wrapper has identity-transform imported `Visuals/Model` and separate
`Collision/Body/Wall`: one static box **3.200 × 0.940 × 0.360 m**, centred at
(0,0.470,0), world layer 1 / mask 0. The box intentionally spans coping joints and
softened bevels. Its maximum 0.050 m per-side expansion over the render core avoids
snagging under the cap; there is no whole-plot or passage collider. No navigation,
destructibility, world IDs, runtime geometry composition or gameplay code changes.

The wall blocks capsule/car envelopes but is deliberately below actor head height.
It is not a walkable deck or climb/vault mechanic. Place **short** runs beside plots,
not across shortcuts, and leave explicit gaps at foot-link mouths. No placement,
shortcut visibility or actual driving route is accepted by this isolated asset.

Text authoring was the commissioned fallback: live editor tools were prohibited,
and the windowed editor is unavailable. The owned prefab was loaded/packed/resaved
with pinned headless Godot; a second reload/save was byte-stable. Saved prefab UID
`uid://dfbodilgmskfj`, GLB UID `uid://cx3djln4pgrvi`, imported ancestry and all node
identities resolve. No separate open editor is claimed synchronized.

## Evidence and reproduction

[Hero](d02_domestic_details_01-evidence/hero.png),
[side](d02_domestic_details_01-evidence/side.png),
[coping detail](d02_domestic_details_01-evidence/detail.png),
[gameplay overhead](d02_domestic_details_01-evidence/overhead_47m_42deg.png).
All four are **isolated Blender Cycles CPU** renders at 1280×720, 32 samples, AgX,
PNG compression 95 followed by six-bit RGB compression. Overhead uses vertical-down
perspective, 47 m height, 42° vertical FOV, Blender +Y/north at image top. This is the
standing evidence-size exception to the older 1280×800 reference, not an engine capture.

All final images were inspected after compression. The short pale coping reads as
an approximately 66-pixel low boundary at the reference camera; small joints remain
close-view detail, not essential gameplay information. Close views show quiet warm
render, a darker plinth and broad coping highlights. An initial coplanar core/plinth
end-face artifact was removed before final export; studio lighting was changed to
avoid a bright local pool washing out the overhead silhouette. Old renders/retries
remain scratch-only, not committed evidence.

Run from repository root in Bash (all process calls are bounded):

```sh
N=d02_domestic_details_01
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="C:/tmp/ft/assets/$N"
mkdir -p "$S" "docs/assets/production/$N-evidence"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8

timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/author.py"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/render.py"
python "tools/asset_production/$N/record.py" --compress-renders
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  "art/source/models/environment/$N/$N.blend" \
  --python "tools/asset_production/$N/export.py" -- "$S/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/validate.py" -- "$S/reexport/$N.glb"

timeout 300 "$G" --headless --path . --import > "$S/import-initial.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "tools/asset_production/$N/check_prefab.gd" -- --normalize \
  > "$S/normalize-editor.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "tools/asset_production/$N/check_prefab.gd" \
  > "$S/prefab-final.log" 2>&1
"$(mise which gdstyle)" fmt --check "tools/asset_production/$N/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$N/check_prefab.gd"
python "tools/asset_production/$N/record.py"
python "tools/asset_production/$N/record.py" --verify
```

The asset-specific checks follow existing production tooling patterns and reuse the
shared export-settings contract; no general repository checker was added or copied.
`production_checks.py` was deliberately not run, per owner decision 52.

## Validation results

[Final receipt](d02_domestic_details_01-evidence/validation.json),
[concise diagnostic log](d02_domestic_details_01-evidence/final.log),
[producer manifest](d02_domestic_details_01-evidence/manifest.json).

- **1,256 triangles; 640 Blender vertices; 640 GLB vertices; one mesh; three surfaces.**
- **Zero degenerate faces/triangles, zero non-manifold edges**, contiguous source
  winding, positive signed volume, outward binary triangle winding and unit normals.
- Binary GLB accessors, source and imported Godot AABBs match the independent bounds
  above within 0.001 m; ground minimum is exactly zero. Export transforms are identity.
- Fresh separate Blender-process reexport is byte-identical: **24,352 bytes**, SHA-256
  `19e91ce155a7b0a587ff81be195ac4b4f55271f98b8391c318fc1a5c25231c02`.
- Headless import exits 0 with **no ERROR/SCRIPT ERROR** lines; prefab dependencies,
  opaque/back-culling materials, UIDs, linked mesh resource and collision shape pass.
- Seven capsule overlap/clearance probes pass, including both ends and both bypasses.
  Front ray hits Z=-0.180000067 m at Y=0.5 m.
- Production `ActorMotion.step` passes front/rear/end stops and right bypass over
  60 fixed ticks in both AUTHORITY and REPLAY modes, with identical endpoints.
  Front/rear stop Z=±0.531250 m, end stop X=1.950522 m; bypass reaches Z=3.000000 m.
  Literal expected contacts use the r=0.35 m / h=1.8 m production capsule and 0.025 m
  solver tolerance. Test-only physics bodies/floor are invisible validation probes.
- A 1.9 × 1.5 × 4.3 m car-sized test box is blocked frontally and passes at X=3 m.
  This is a swept-envelope check, **not** production car driving/turning evidence.
- Pinned `gdstyle fmt --check` and strict lint pass; function-comment and spacing
  rules were checked. Bare `gdstyle` was initially absent from PATH, then resolved
  through `mise which gdstyle` without installing or modifying tooling.

Blender reports its known future-6.0 `use_nodes` deprecations. Import reports the
existing MCP plugin 4.8 compatibility warning. Headless editor normalization exits 0
and proves byte stability, but its shutdown emits scan-aborted/RID/ObjectDB leak
messages; exact diagnostics remain in `final.log`, not suppressed. The separate
fresh runtime check has no ERROR/WARNING lines. No owner live session was accessed.

## Remaining acceptance

- Independent source/technical and art review at the committed candidate.
- World integrator: fit to chosen home plots, review placed return junctions, actual
  gaps, curved streets, shortcut visibility and repetition; do not stretch module
  scales. The [wall return delivery](d02_domestic_details_02.md) now supplies matching
  end profiles and bounded straight/return seam checks; placed junction review remains open.
- Gameplay/camera owner: native 47 m/42° actor/combat visibility and actual car movement
  around placed boundaries; preserve walking alternatives and clearance.
- Network owner: actual separate-process transport/admission/prediction/lifecycle
  evidence if this static prefab enters a replicated world. Local authority/replay
  equivalence is not network acceptance.
- Device/performance owner: native material/LOD appearance, repeat-placement profiling,
  packaged import/dependency behavior and sustained Deck LCD/OLED checks.

No family siblings, shared queue/progress, world scenes, production settings or
historical receipts were modified. This is the first delivery in this family lane;
there was no earlier sibling pending item to reconcile.
