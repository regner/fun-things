# d09_storage.03 — Low covered stack

**Production source/export, linked prefab and bounded checks delivered; independent
review, world placement and gameplay/device acceptance pending.** Commissioned by
Regner under [the production commission](commission.md) and the current per-asset
lane brief, superseding the older concept-only restriction.

Producer: commissioned implementation specialist, branch `lane/a-storage`.
Accepting owners: independent art/technical reviewers, then world/gameplay/device
owners. Original Blender construction only; no downloads, real brands, external
textures, image-to-mesh content or runtime-authored geometry. References:
[storage family](../d09_storage.md), [East Docks](../../concepts/districts-v1/east-docks.md),
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and the earlier
[long](d09_storage_01.md) / [short](d09_storage_02.md) container deliveries.

## Design and dimensions

One low, orderly freight load: four closed slate packs in two layers, timber
separators and an upper packed load, carried on three timber runners and five
cross bearers. A restrained blue tarpaulin covers the upper contents, with broad
shallow folds, a closed thin hem and slightly lifted skirt centres. Two dark
webbing bands run over the cover to four small buckles with blank amber tabs.
This is a distinct covered-stack silhouette, not another corrugated container.

The blue, slate and sparse amber use the earlier containers' linear color values;
cloth and webbing deliberately have nonmetallic, rougher responses. The quiet
14.72 m² footprint and 1.65 m height stay below the 2.6 m container family. This
supports the brief's subordinate storage role, not acceptance of an arrangement
beside warehouses/cranes. No interior, inventory, removable cover, cloth physics,
movable stack, opening state, destruction, rig, animation or sockets are introduced.

Dimensions are **provisional authored choices**, not measurements from generated
concept imagery or an allocation of the district's 5.03 ha.

| Contract | Metres, Godot local coordinates |
| --- | --- |
| Visual size X / Y / Z | **3.200 / 1.650 / 4.600** |
| Visual AABB minimum | **(-1.600, 0, -2.300)** |
| Visual AABB maximum | **(1.600, 1.650, 2.300)** |
| Root / mesh pivot | (0,0,0), ground-centred footprint |
| Long axis | Z; Blender Y maps once to Godot -Z |
| Pallet support height | 0–0.240 |
| Each lower/upper freight pack | 3.020 wide × 0.430 high × 2.120 long |
| Two pack-layer centres | Y=0.470 and 0.965; Z=±1.080 |
| Cover footprint | 3.140 × 4.520 |
| Cover upper surface / thickness | Maximum Y=1.636; 0.012 vertical thickness |
| Cover lower skirt edge | Upper surface Y=0.680–0.820 |
| Webbing width / band centres | 0.130 along Z; Z=±1.400 |
| Bound / ground-datum tolerance | ±0.001 |

Metre units, applied static rotation/scale and identity roots. Ground runners
contact Y=0; no corrective wrapper transform. The model is symmetric and has no
functional front. Pallet/support appearance belongs to this assembly, not a new
reusable pallet record. Small fork recesses and pack seams are not traversable
openings. Closed component shells meet at intentional joints; the assembly is
not a Boolean-unioned watertight volume.

## Source, exports and materials

- Source: `art/source/models/environment/d09_storage_03/d09_storage_03.blend`.
- Export collection: `export_d09_storage_03`.
- Root / mesh: `D09Storage03` / `D09Storage03_Mesh`.
- Export: `art/models/environment/d09_storage_03/d09_storage_03.glb` plus `.import`.
- Linked wrapper: `scenes/prefabs/environment/d09_storage_03.tscn`.
- Author/export/validator, saved physics check scene, GDScript check and finalizer:
  `tools/asset_production/d09_storage_03/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
The export script reads `tools/assets/blender/export_settings.json`, filters the
named collection and disables skins/animations. Studio camera, lights and ground
stay outside the export. Bevels and weighted normals are applied before save;
source meshes remain editable, and author.py retains the parametric recipe.
The closed drape and webbing are originally constructed mesh grids, with real
thickness and closed edge faces, not downloaded cloth or runtime geometry.

`author.py` reuses the earlier long container's material, box/mesh finishing and
studio helpers read-only. Covered-load construction belongs to this member; it
does not reuse or modify the container mesh. Saved source and GLB are standalone;
only source regeneration requires the earlier author.py. Its SHA-256 is a manifest
read-only dependency. Neither sibling handoff had a stale pending item resolved
by this delivery, so no earlier sibling files or historical receipts were edited.

One mesh, five opaque back-culled Principled surfaces in stable order:

| Surface | Linear RGB | Metallic / roughness |
| --- | --- | --- |
| `storage_support_timber` | (.230,.170,.105) | 0 / .72 |
| `storage_cargo_slate` | (.240,.300,.340) | .10 / .65 |
| `storage_cover_blue` | (.055,.135,.235) | 0 / .83 |
| `storage_webbing_slate` | (.055,.085,.120) | 0 / .82 |
| `storage_tie_amber` | (.950,.520,.150) | .05 / .53 |

No textures, embedded images, transparency, emission, material remapping or
freight-artwork face contract. The tiny blank amber tabs are buckle accents,
not signage, selected copy, runtime IDs or essential overhead information.
Default Godot automatic LOD and shadow meshes remain enabled. No numerical mesh
budget was supplied; repeated-placement cost and LOD transitions remain unmeasured.

## Prefab and collision

`Visuals/Model` is an identity-transform imported GLB instance with one mesh and
five surfaces. No copied mesh arrays, imported-child overrides or runtime node
construction. `Collision/Body/Shell` is a direct CollisionShape3D child of one
StaticBody3D: BoxShape3D **(3.2,1.65,4.6)** at **(0,0.825,0)**, static-world layer
**1**, mask **0**. The single solid envelope matches the full assembly bounds and
closes pallet recesses, pack seams and small tie hardware without snag points.
It deliberately fills the cover's rounded/tapered upper shoulders; it is not
triangle collision. No collider extends outside the full visual AABB and no
corner gap or actor-sized passage is left in this nontraversable stack. No roof
access or separately authored walkable surface is introduced.

Godot scene UID `uid://d2xdwgvw7mina`; model import UID `uid://b87uqbo7xj1i4`.
Two byte-stable load/pack/save/reload roundtrips preserve scene bytes and node
identities. A separate fresh-process roundtrip also preserves the original saved
bytes. Final pinned import and a fresh-process check resolve dependencies/UIDs.
The brief authorized text-authored scenes normalized headlessly: the unavailable
windowed editor and owner's live sessions were not used. Headless checks do not
synchronize a separate live editor.

## Evidence and validation

[Hero](d09_storage_03-evidence/hero.png) ·
[side](d09_storage_03-evidence/side.png) ·
[cover/buckle detail](d09_storage_03-evidence/detail.png) ·
[47 m / 42° overhead](d09_storage_03-evidence/overhead_47m_42deg.png).

All four are isolated **Blender Cycles CPU, 32 samples, AgX, 1280×720**, not Godot
captures. Overhead is vertically down, north-up at Blender (0,0,47), 42° vertical
perspective FOV. The current 720-pixel evidence cap supersedes the older 800-pixel
request. PNGs use six significant bits/channel and maximum compression, each
under 300 KB. Background banding is evidence compression, not runtime texture.

The producer inspected all four final images and the short-container hero.
The covered rectangle and two bands remain legible overhead; the cloth rather
than corrugation differentiates this member. The pack seam and pallet read in
closer views, while the small warm buckle tabs remain subordinate. Self-review
lowered the straps onto the cover and relaxed the hem centres before the final
export. Actual district scale hierarchy, repeated-pattern density, actor occlusion
and renderer appearance remain placement/engine-camera review responsibilities.

Final values from [validation.json](d09_storage_03-evidence/validation.json):

- **2,240 source vertices; 4,356 triangles; 2,688 exported vertices** including
  normal/material splits. **1 mesh, 5 surfaces**.
- **0 degenerate source faces/triangles, 0 degenerate GLB triangles,
  0 non-manifold source edges**. Unit source/export normals pass.
- Maximum normal-length error: source **2.5285411098e-7**,
  export **1.1546034572e-7**.
- Source, actual binary GLB positions and engine AABB agree within 0.001 m.
- Fresh source re-export is byte-identical: **117,188 bytes**, SHA-256
  `59ef8f579a9b76fb1d66ed2bfc98af87441dda2cba2dadaa2481294c233df683`.
- Three front rays (centre and near both corners) hit the saved body at Z=-2.3;
  a ray at Y=1.8 clears above the covered stack.
- Production `ActorMotion.step`, capsule **r=0.35 m, h=1.8 m**, 192 ticks per case:
  authority/replay both stop at **Z=-2.66666054725647**; side bypass at X=2.1 ends
  at **Z=8.00001239776611**. Contact is within the independent 0.03 m tolerance
  behind the expected capsule contact plane Z=-2.65. No networking claim follows.
- Provisional **1.8×1.5×4.4 m** car-box cast hits the front (safe fraction
  **0.27496337890625**); bypass at X=2.6 clears (**1.0**). This is not actual
  driving/turning or vehicle-controller acceptance.
- Pinned imports and fresh-process checks exit 0 without ERROR/SCRIPT ERROR lines.
  GDScript format check and lint at 100 columns / zero warnings pass.

Final Blender author/export logs contain no errors. Import emits the existing
MCP toolkit 4.8-versus-tested-4.7 warning. No addon changes or broad error
suppression. Scratch/iteration logs remain outside the repository. A concise final
[check log](d09_storage_03-evidence/final-checks.log) and final
[producer manifest](d09_storage_03-evidence/manifest.json) retain current evidence.

## Exact reproduction

Run from the worktree root in Bash. Do not regenerate source over unrelated
unsaved Blender work. No live editor is needed or authorized.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/d09_storage_03/author.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/d09_storage_03/validate.py
# Validator reexports saved source to C:/tmp/ft/assets/d09_storage_03/reexport.
python tools/asset_production/d09_storage_03/finalize.py --compress-renders

timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_03/check.gd -- --normalize
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_03/check.gd -- --normalize --verify-stable
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_03/check.gd
"$GDSTYLE" fmt --check tools/asset_production/d09_storage_03/check.gd
"$GDSTYLE" --max-line-length 100 --max-warnings 0 tools/asset_production/d09_storage_03/check.gd
python tools/asset_production/d09_storage_03/finalize.py
```

No `tools/production_checks.py` run: owner decision 52 keeps unplaced-asset checks
bounded. The manifest hashes every produced payload except itself; shared export
settings and the earlier sibling's authoring helpers are read-only dependencies.
After any future source change, copy changed receipt numbers into this handoff,
refresh the concise log, then regenerate the manifest last.

## Remaining acceptance

- Independent art/technical acceptance of this exact candidate.
- Saved district placement in sparse low groups at loading edges; preserve the
  open crane apron, service spur and ordinary street footways. This prop does
  not accept a taller stack, container maze or district freight arrangement.
- Actual engine-camera appearance, actor/target occlusion and LOD transitions in
  context; isolated source renders do not accept whole-district readability.
- Actual vehicle driving/turning, network transport/admission/prediction and
  collision lifecycle implications in the integrated world.
- Packaged-platform/Deck and repeated-placement GPU/frame-time performance.

No register/progress/shared brief/world scene was changed, no TODO was closed,
and no whole-city or full game-ready acceptance is claimed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
