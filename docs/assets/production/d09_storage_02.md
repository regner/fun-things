# d09_storage.02 — Short container

**Production source/export, linked prefab and bounded checks delivered; independent
review, world placement and gameplay/device acceptance pending.** Commissioned by
Regner under [the production commission](commission.md) and the current per-asset
lane brief, superseding the older concept-only restriction.

Producer: commissioned implementation specialist, branch `lane/a-storage`.
Accepting owners: independent art/technical reviewers, then world/gameplay/device
owners. Original Blender construction only; no downloads, real brands, generated
image-to-mesh content, external textures or runtime-authored geometry. References:
[storage family](../d09_storage.md), [East Docks](../../concepts/districts-v1/east-docks.md),
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and the earlier
[long container delivery](d09_storage_01.md).

## Design and dimensions

One compact blue/slate freight container, half the long container's length with
unchanged cross-section, eight corner castings, perimeter frame, closed paired
end doors, four locking bars and two small blank amber identification faces.
Continuous trapezoidal corrugation and smooth manufactured edges use the earlier
sibling's original Blender construction recipe. The short member is **rebuilt at
6 m**, not uniformly scaled or made by clipping the long GLB. Door hardware,
corner dimensions and material values remain the same; fold count follows length.
The quiet low mass is subordinate to warehouses and amber crane landmarks.

Dimensions are **provisional authored choices**, not measurements from generated
concept art or approval of a district arrangement. Its 15 m² footprint is not an
allocation of the 5.03 ha district. No interior, opening doors, movable stack,
cargo inventory, rig, sockets, animation or destruction state is introduced.

| Contract | Metres, Godot local coordinates |
| --- | --- |
| Visual size X / Y / Z | **2.500 / 2.600 / 6.000** |
| Visual AABB minimum | **(-1.250, 0, -3.000)** |
| Visual AABB maximum | **(1.250, 2.600, 3.000)** |
| Root / mesh pivot | (0,0,0), ground-centred footprint |
| Closed door front | -Z; Blender +Y converts once to Godot -Z |
| Long-axis direction | Z; Blender Y |
| Side corrugated face height | Y=0.200–2.400 |
| Side / roof corrugation | 12 folds across 5.640 m, pitch 0.470, depth 0.045 |
| Closed door leaves | Each 1.055 wide × 2.200 high |
| Corner castings | 0.240 × 0.240 × 0.240 |
| Bound / ground-datum tolerance | ±0.001 |

Metre units, applied static rotation/scale, identity roots and no corrective
wrapper rotation or scale. Corners contact ground at Y=0. The raised belly is
closed geometry, not a crawl space. Manufactured shells meet at intentional
intersecting joints; this is not a Boolean-unioned watertight assembly.

### Family and artwork interface

`author.py` imports `tools/asset_production/d09_storage_01/author.py` read-only and
calls its `build_container(length=6.0)` recipe. That sibling owns the family
cross-section, folded-panel, corner-post and end-door construction; no duplicate
primitive library is added. The source .blend and exported GLB are standalone;
only regenerating this source needs the earlier recipe. Its hash is recorded as
a read-only manifest dependency. No earlier sibling files were edited: its
current Remaining acceptance section had no stale short-container pending item.

The **1.400 × 0.460 m** outward quad on each included identification backing uses
`storage_id_face`, surface **3** (zero based). Quad centres are
**(±1.230, 1.960, -1.650)**, outward normals ±X; Y range **1.730–2.190**,
Z range **-2.350–-0.950**. UV0 fills 0–1 per quad, upright and left-to-right from
outside either side. Backing and edges use the steel slot. Validation checks the
actual GLB face coordinates, outward normals, four artwork triangles and unit UV
corners. The faces keep the long member's size and end-relative offset, allowing
the same artwork scale on both lengths.

This is a carrier for [freight graphics](../d09_freight_graphics.md), not selected
copy, new artwork, essential overhead wayfinding or a gameplay ID. The prefab has
no imported-child overrides. Later artwork can use the documented face-slot-only
reuse exception in [assets](../../assets.md#prefabs-and-authored-placement), with
its own byte-stable roundtrip evidence and no duplicate carrier geometry.

## Source, exports and materials

- Source: `art/source/models/environment/d09_storage_02/d09_storage_02.blend`.
- Export collection: `export_d09_storage_02`.
- Root / mesh: `D09Storage02` / `D09Storage02_Mesh`.
- Export: `art/models/environment/d09_storage_02/d09_storage_02.glb` plus `.import`.
- Linked wrapper: `scenes/prefabs/environment/d09_storage_02.tscn`.
- Author/export/validator, saved physics check scene, GDScript check and finalizer:
  `tools/asset_production/d09_storage_02/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
The owned export script loads `tools/assets/blender/export_settings.json`, filters
the named collection and disables skins/animations. Studio cameras, lights and
ground stay outside the export. Source meshes remain editable; author.py retains
the parametric recipe entrypoint. Bevels and weighted normals are applied before
save. The source-specific validators follow the earlier container's bounded checks.

One mesh, four opaque back-culled Principled surfaces, in this stable order:

| Surface | Linear RGB | Metallic / roughness |
| --- | --- | --- |
| `storage_body_blue` | (.055,.135,.235) | .25 / .48 |
| `storage_frame_slate` | (.055,.085,.120) | .45 / .43 |
| `storage_hardware_steel` | (.240,.300,.340) | .65 / .37 |
| `storage_id_face` | (.950,.520,.150) | .05 / .53 |

No textures, embedded images, emission, transparency or material remapping.
Default Godot automatic LOD and shadow meshes remain enabled. Fold bevels and
closed cap strips account for most density. No numerical triangle budget was
supplied; repeated-placement cost and LOD transitions remain unmeasured.

## Prefab and collision

`Visuals/Model` is an identity-transform imported GLB instance, with one mesh and
four surfaces. No copied mesh arrays, imported-child edits or runtime hierarchy
construction. `Collision/Body/Shell` is a direct CollisionShape3D child of one
StaticBody3D: BoxShape3D **(2.5,2.6,6)** at **(0,1.3,0)**, static-world layer **1**,
mask **0**. The single solid envelope closes small corrugation/frame recesses
without snagging on individual bars. It matches the complete visual bounds, with
no corner gaps or external protruding collider. Main side recesses are at most
0.10 m inside it; rear steel at most 0.13 m inside it. The closed box does not
introduce an interior or rooftop traversal feature.

Godot scene UID `uid://dxo4oar28nrqj`; model import UID `uid://cewl65j3t8eug`.
Two byte-stable load/pack/save/reload roundtrips preserve complete scene bytes and
node identities. A separate fresh-process normalization also preserves the exact
previously saved bytes. A subsequent pinned import and fresh-process check resolve all
dependencies and UIDs. Per the brief, scene text was authored directly and
normalized headlessly. The unavailable windowed editor and owner's live sessions
were not used; headless checks do not synchronize those sessions.

## Evidence and validation

[Hero](d09_storage_02-evidence/hero.png) ·
[side](d09_storage_02-evidence/side.png) ·
[door detail](d09_storage_02-evidence/detail.png) ·
[47 m / 42° overhead](d09_storage_02-evidence/overhead_47m_42deg.png).

All are isolated **Blender Cycles CPU, 32 samples, AgX, 1280×720** renders, not
Godot captures. Overhead: vertical down, north up, Blender position (0,0,47),
42° vertical perspective FOV. The current 720-pixel evidence cap supersedes the
older 800-pixel request. PNGs use six significant bits/channel and maximum
compression (each under 320 KB); runtime materials are not color-reduced.

The producer inspected all four final images and the long sibling's hero. The
short rectangle, shared folded steel rhythm and end hardware read coherently with
the long member. Overhead the broad roof remains a quiet, small storage mass;
labels are intentionally not overhead-readable. Studio background banding is
evidence compression, not asset texture. In-context subordination and actor
occlusion are still placement-review responsibilities.

Final numbers from [validation.json](d09_storage_02-evidence/validation.json):

- **6,856 source vertices; 13,476 triangles; 7,762 exported vertices** including
  normal/material splits. **1 mesh, 4 surfaces**.
- **0 degenerate source faces/triangles, 0 degenerate GLB triangles,
  0 non-manifold source edges**. Unit-length source/export normals pass.
- Maximum normal-length error: source **1.55685926594984e-7**,
  export **1.27434467200871e-7**.
- Source bounds, actual binary GLB positions and engine AABB agree within 0.001 m.
- Fresh source re-export is byte-identical: **333,324 bytes**, SHA-256
  `590469bcc6db39bda4cf46c131edca349d0f2d357aebe1e26a9c568b242e5be0`.
- Three front rays (centre and near both corners) hit the saved body at Z=-3;
  the ray above the roof clears.
- Production `ActorMotion.step`, capsule **r=0.35 m, h=1.8 m**, 192 ticks per case:
  authority/replay both stop at **Z=-3.35025358200073**; clear side bypass at X=2
  ends at **Z=8.00001239776611**. This is not network transport evidence.
- Provisional **1.8×1.5×4.4 m** car-box cast hits the front (safe fraction
  **0.23992919921875**); bypass at X=2.3 clears (**1.0**). Actual driving/turning
  and vehicle-controller acceptance are not claimed.
- Pinned imports and fresh-process checks exit 0 with no ERROR/SCRIPT ERROR lines.
  GDScript format check and lint at 100 columns / zero warnings pass.

During initial authoring, re-normalizing new scenes before refreshing their UID
cache assigned new scene UIDs. A full import registered the final identities;
the extra `--verify-stable` fresh-process roundtrip now asserts unchanged input
bytes, not merely stability between saves in one process. No previously committed
resource was changed. Blender emits forward-looking `use_nodes` deprecation notices; import emits the
existing MCP toolkit 4.8-versus-tested-4.7 warning. No addon changes or broad error
suppression. Scratch logs remain outside the repository. A concise final
[check log](d09_storage_02-evidence/final-checks.log) and final
[producer manifest](d09_storage_02-evidence/manifest.json) retain current evidence.

## Exact reproduction

Run from the worktree root in Bash. Do not regenerate source over unrelated
unsaved Blender work. No live editor is needed or authorized.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/d09_storage_02/author.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/d09_storage_02/validate.py
# Validator opens the saved source and reexports to C:/tmp/ft/assets/d09_storage_02/reexport.
python tools/asset_production/d09_storage_02/finalize.py --compress-renders

timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_02/check.gd -- --normalize
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_02/check.gd -- --normalize --verify-stable
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_02/check.gd
"$GDSTYLE" fmt --check tools/asset_production/d09_storage_02/check.gd
"$GDSTYLE" --max-line-length 100 --max-warnings 0 tools/asset_production/d09_storage_02/check.gd
python tools/asset_production/d09_storage_02/finalize.py
```

No `tools/production_checks.py` run: owner decision 52 keeps unplaced-asset
validation bounded. The manifest hashes every produced payload except itself;
shared export settings and the earlier sibling's authoring recipe are read-only
dependencies. If a future source changes, refresh this handoff's receipt values
and final log from the final validation receipt, then regenerate the manifest last.

## Remaining acceptance

- Independent art/technical acceptance of this exact candidate.
- Saved district placement in sparse low groups at loading edges, keeping the
  open crane apron, service spur and ordinary street footways clear. No stack
  height or container-maze arrangement is approved by this ground-level prop.
- Actual engine-camera appearance, actor/target occlusion and LOD transitions in
  context; source renders do not accept whole-district readability.
- Actual vehicle driving/turning, network transport/admission/prediction and
  collision lifecycle implications in the integrated world.
- Packaged-platform/Deck and repeated-placement GPU/frame-time performance.

No register/progress/shared brief/world scene was changed, no TODO was closed,
and no whole-city or full game-ready acceptance is claimed.
