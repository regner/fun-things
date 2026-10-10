# d09_storage.04 — Simple crate group

**Production source/export, reusable component and two linked arrangements delivered;
independent review, world placement and gameplay/device acceptance pending.** Commissioned
by Regner under [the production commission](commission.md) and current per-asset lane
brief, superseding the older concept-only restriction.

Producer: commissioned implementation specialist on `lane/a-storage`. Accepting owners:
independent art/technical reviewers, then world/gameplay/device owners. Original Blender
construction only; no downloads, real brands, external textures, image-to-mesh content or
runtime-generated render geometry. References: [storage family](../d09_storage.md),
[East Docks](../../concepts/districts-v1/east-docks.md),
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[streets](../../concepts/world-v1/stage-04-streets/README.md), and the earlier
[long container](d09_storage_01.md), [short container](d09_storage_02.md) and
[covered stack](d09_storage_03.md).

## Design and dimensions

One reusable closed crate design, not a unique crate for each placement. Broad blue
plywood panels sit inside muted timber battens, with two integral runners, four slate
corner shoes, one diagonal brace on each front/back face and a single small blank amber
side tab. A divided, recessed blue lid reads as a simple framed rectangle from above.
The timber matches the covered stack's supports; blue, slate and amber reuse the
container palette with a rougher, less metallic panel response.

Two saved arrangement variations reuse that same component: an orderly two-crate row
and a stepped three-crate group, two below with one aligned above the left crate. The
2.10 m maximum height stays below the 2.60 m container family. The crate framing is
purposefully simpler than container corrugation or the covered stack's cloth folds.
Storage remains a small, quiet loading-edge element, not a crane/warehouse landmark.
Actual district subordination is a placement gate, not proved by these isolated views.

All dimensions are **provisional authored choices**, not measurements from concept
imagery or an allocation of the district's gross 5.03 ha. No inventory, interior,
opening lid, cargo simulation, movable stack, destruction, rig, animation, sockets or
new traversal feature is introduced.

| Output / contract | Metres, Godot local coordinates |
| --- | --- |
| Single crate size X / Y / Z | **1.400 / 1.050 / 1.400** |
| Single crate AABB | **(-0.700, 0, -0.700) → (0.700, 1.050, 0.700)** |
| Pair size X / Y / Z | **2.880 / 1.050 / 1.400** |
| Pair AABB | **(-1.440, 0, -0.700) → (1.440, 1.050, 0.700)** |
| Default stepped trio size X / Y / Z | **2.880 / 2.100 / 1.400** |
| Default stepped trio AABB | **(-1.440, 0, -0.700) → (1.440, 2.100, 0.700)** |
| Component / arrangement root pivots | Ground-centred footprint at (0,0,0) |
| Pair component translations | (-0.740,0,0), (0.740,0,0) |
| Trio additional upper component | (-0.740,1.050,0) |
| Horizontal seam between crates | 0.080; not an actor passage |
| Integral support height | Y=0–0.120 |
| Frame outer top / panel top | Y=1.050 / 1.000 |
| Corner shoes / timber uprights | Y=0.120–0.290 / Y=0.290–1.050 |
| Blank side tab | 0.190 along Z × 0.130 high, on +X face |
| Bound / ground-datum tolerance | ±0.001 |

Metre units, applied static rotation/scale, root and mesh origins at ground zero. The
braced front faces Blender +Y / Godot -Z; the other braced face is opposite. The blank
tab is on +X. The trio is asymmetric in height but its footprint/pivot are centred.
Support runners seat on the lower crate's frame; no floating top crate. Support
appearance belongs to the crate rather than a separate pallet asset. Closed component
shells meet at intentional joints; the crate is not a Boolean-unioned volume.

## Source, export and materials

- Source: `art/source/models/environment/d09_storage_04/d09_storage_04.blend`.
- Named export collection: `export_d09_storage_04`.
- Root / mesh: `D09Storage04` / `D09Storage04_Mesh`.
- Single export: `art/models/environment/d09_storage_04/d09_storage_04.glb`, plus `.import`.
- Single-crate wrapper: `scenes/prefabs/environment/d09_storage_04_crate.tscn`.
- Two-crate row: `scenes/prefabs/environment/d09_storage_04_pair.tscn`.
- Default stepped trio: `scenes/prefabs/environment/d09_storage_04.tscn`.
- Author/export/validator, saved collision fixture, GDScript check and finalizer:
  `tools/asset_production/d09_storage_04/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. `export.py`
reads `tools/assets/blender/export_settings.json`, filters the named collection and
disables skins/animations. Only the root and single mesh export. Applied bevels and
weighted normals remain editable mesh data; author.py retains the parametric recipe.
Studio lights, camera, ground and linked preview copies remain outside the export.
The source mesh is hidden from studio rendering to avoid double-rendering its preview
copies; collection export has `use_visible=false`, and Godot checks its actual visible
import. This does not disable the runtime model.

The author imports the earlier long container's material, box/finish and studio helpers
read-only. The validator reuses the covered stack's binary-accessor reader. The engine
check extends its save/dependency/box/ActorMotion helpers, overriding asset-specific
checks and entrypoint. No sibling geometry or source is copied. These read-only tools
are listed with hashes in the manifest; saved source, GLB and runtime prefabs are
standalone. None of the earlier three handoffs listed this crate delivery as pending,
so no sibling doc/manifest or historical receipt was edited.

One mesh with four stable, opaque, back-culled Principled material slots:

| Surface, zero-based order | Linear RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `storage_support_timber` | (.230,.170,.105) | 0 / .72 |
| 1 `storage_crate_blue` | (.055,.135,.235) | .05 / .65 |
| 2 `storage_frame_slate` | (.055,.085,.120) | .45 / .43 |
| 3 `storage_crate_tab` | (.950,.520,.150) | .05 / .53 |

No textures, embedded images, transparency, emission, external remapping or imported-child
material overrides. The tab is a small blank accent, not selected copy, a gameplay ID,
essential overhead information or a freight-artwork face interface. Automatic Godot LOD
and shadow mesh generation retain their defaults. No polygon/performance budget was
supplied; this delivery does not accept repeated-placement cost or LOD transitions.

## Prefabs and collision

The component wrapper's `Visuals/Model` is an identity-transform imported GLB instance.
`Collision/Body/Shell` is a direct CollisionShape3D child of one StaticBody3D, with
BoxShape3D **(1.4,1.05,1.4)** at **(0,0.525,0)**, static-world layer **1**, mask **0**.
This simple solid envelope closes minor runner/brace/panel recesses without snagging
individual battens. The main blue panel is 0.08 m inside the envelope; runner recesses
are intentionally nontraversable. The collider does not exceed the component AABB.

Pair/trio roots contain two/three saved linked crate-prefab instances, translated only.
Each component retains its one collider, producing the minimal two/three-box compound.
There is no duplicated group GLB, runtime arrangement builder, copied mesh array or
editable-child override. In particular, the trio **does not** use its overall bounding
box as collision: the empty upper-right region remains empty. The 0.08 m lower seam
remains clear for rays but does not admit the 0.70 m diameter actor. Nine front/corner
rays, a seam capsule run, upper/notch rays and perimeter bypasses exercise those choices.

Final scene UIDs: crate `uid://bg3h73iyp2x12`, pair `uid://dwxyov60ys8lr`, trio
`uid://dx7b31suvgbl0`; GLB import `uid://bllyi70mspi13`. All three prefabs and the saved
fixture passed two byte-stable load/pack/save/reload roundtrips, plus a fresh-process
roundtrip preserving the previously saved bytes and identities. A final pinned import
and fresh-process load/physics check resolve dependencies and UIDs.

Per the brief, scenes were text-authored then normalized headlessly; the windowed editor
is unavailable and the owner's live sessions were not used. Headless import does not
synchronize any separate live editor. The group is static dressing/obstruction, not
approved rooftop access, stacking gameplay or world placement.

## Evidence and validation

[Trio hero](d09_storage_04-evidence/hero.png) ·
[pair side](d09_storage_04-evidence/side.png) ·
[single-crate detail](d09_storage_04-evidence/detail.png) ·
[47 m / 42° overhead](d09_storage_04-evidence/overhead_47m_42deg.png).

All four are isolated **Blender Cycles CPU, 32 samples, AgX, 1280×720** renders, not
Godot captures. Overhead: vertical down, north-up, Blender camera at (0,0,47), 42°
vertical perspective FOV. The current 720-pixel evidence cap supersedes the older
800-pixel request. It compares the trio at X=-3 and pair at X=3 with a 3.12 m gap;
those are evidence-only placements. PNG compression is maximum, with six significant
bits/channel; every render is under 321 KB. Background banding is evidence compression,
not a runtime texture.

The producer inspected all four final compressed images, plus the earlier short
container and covered-stack heroes. Both arrangements read as small framed blue blocks
overhead; timber divisions survive while side braces/tabs intentionally do not. The
trio height is clearest in the hero, not reliably inferable from a centred overhead
roof silhouette. No gameplay-critical information depends on distinguishing pair/trio
from above. Self-review widened the hero framing, moved the tab off a brace, seated
braces inside the intended envelope and removed coplanar shoe/upright overlap before
the final export. No final topology or engine-check failures remain.

Final values copied from [validation.json](d09_storage_04-evidence/validation.json):

- Per crate: **1,288 source vertices; 2,484 triangles; 1,656 exported vertices**,
  including normal/material splits; **1 mesh, 4 surfaces**.
- Pair: **4,968 triangles, 2 linked meshes, 8 surfaces**. Trio: **7,452 triangles,
  3 linked meshes, 12 surfaces**. Both share the same exported geometry resource.
- **0 degenerate source faces/triangles, 0 degenerate GLB triangles,
  0 non-manifold source edges**. Unit source/export normals pass.
- Maximum normal-length errors: source **1.6455304385e-7**, export **9.46456522e-8**.
- Source, binary GLB coordinates and engine component/arrangement bounds agree
  within 0.001 m. Pivots, applied transforms and one-time axis conversion pass.
- Fresh saved-source re-export is byte-identical: **71,212 bytes**, SHA-256
  `32f14cb00a9f3c2e32bd940bbc80e168c47add3d02448dd06bf1546be5686e25`.
- Nine front/corner rays hit at **Z=-0.7**; upper-crate collision blocks while
  the stepped notch, horizontal seams and space above each variant stay clear.
- Production `ActorMotion.step`, capsule **r=0.35 m, h=1.8 m**, 192 ticks per case:
  authority/replay contact both stop at **Z=-1.05077517032623** for each variant;
  side bypasses end at **Z=8.00001239776611**. Contact tolerance is 0.03 m behind
  the independent expected capsule plane Z=-1.05.
- Additional authority seam test stops at **Z=-1.04296267032623**, not through the
  0.08 m gap. This is a separate seam expectation, not a claim of flat-face contact.
- Provisional **1.8×1.5×4.4 m** car-box casts hit all three variants at safe fraction
  **0.35498046875**; bypass fractions all **1.0**. Actual driving/turning is untested.
- Pinned imports and final fresh-process checks exit 0 without ERROR/SCRIPT ERROR
  lines. GDScript format check and lint at 100 columns / zero warnings pass.

The first dimensional validation rejected a brace extending 0.0025 m outside its
intended footprint. It was corrected in source rather than weakening the bound test.
Final Blender author/export logs contain no errors; import emits the existing MCP
toolkit 4.8-versus-tested-4.7 warning. No addon edits or broad error suppression.
Scratch renders, retries and raw logs remain outside the repository. The concise
[final log](d09_storage_04-evidence/final-checks.log) and
[manifest](d09_storage_04-evidence/manifest.json) retain the final checks and hashes.

## Exact reproduction

Run from this worktree root in Bash. Do not regenerate over unrelated unsaved source
work. No live Blender/Godot session is needed or authorized.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/d09_storage_04/author.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/d09_storage_04/validate.py
# Validator reexports saved source to C:/tmp/ft/assets/d09_storage_04/reexport.
python tools/asset_production/d09_storage_04/finalize.py --compress-renders

timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_04/check.gd -- --normalize
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_04/check.gd -- --normalize --verify-stable
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_04/check.gd
"$GDSTYLE" fmt --check tools/asset_production/d09_storage_04/check.gd
"$GDSTYLE" --max-line-length 100 --max-warnings 0 tools/asset_production/d09_storage_04/check.gd
python tools/asset_production/d09_storage_04/finalize.py
```

No `tools/production_checks.py` run, per owner decision 52. The manifest hashes every
produced payload except itself and lists read-only reproduction dependencies. After
future source edits, refresh all receipt values in this handoff and the concise log,
then regenerate the manifest last.

## Remaining acceptance

- Independent art/technical review of this exact candidate.
- Saved district placement in sparse loading-edge groups, keeping the crane apron,
  service spur and ordinary footways open. These two local arrangements do not
  approve taller stacks, a container maze or overall freight-yard layout.
- Actual engine-camera appearance, actor/target occlusion, LOD transitions and
  repeated-pattern density in context.
- Actual vehicle driving/turning, network transport/admission/prediction and
  collision lifecycle checks in the integrated world.
- Packaged-platform/Deck and repeated-placement GPU/frame-time performance.

No register, progress, shared brief, world scene or earlier sibling output was changed;
no TODO or whole-city/full game-ready acceptance is marked complete.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
