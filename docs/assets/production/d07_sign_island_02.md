# d07_sign_island.02 — Large restrained sign support

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay acceptance pending.** Commissioned implementation worker on `lane/a-d07`
owns original construction and bounded technical integration; supervisor/reviewer owns
acceptance, world integrator owns placement. The resumed production commission supersedes
the historical concept-only restriction. This is the static hardware, not selected copy.

Inputs: [family brief](../d07_sign_island.md),
[delivered circular base](d07_sign_island_01.md),
[Broadlot concept](../../concepts/districts-v1/broadlot.md),
[approved district identity](../../concepts/world-v1/stage-03-district-identities/README.md#broadlot--big-roofs-bigger-empty-spaces)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).
The concept review specifically calls its illustrated upright lime sign too prominent;
this delivery uses a broad, low, quiet monolith instead. No district parcel, traffic rule,
road geometry, building or saved city placement is changed.

## Design and provisional dimensions

One horizontal directory support with a broad slate casing, softened petrol mounting shoe,
thin petrol cap and **one flush lime cap sector**. The large blank front face is framed by
quiet hardware. No tower, giant advertising carpet, bolts, foliage, real brand, working
screen or invented interaction. The circular base remains a separate linked asset.

All dimensions are **provisional authored choices**, not measurements from the raster.
They implement the family requirement to read across open asphalt without becoming a tower.
District 07's 6.84 ha / 474.5 × 234.8 m gross bounds are context, not an allocation.

- Godot width / height / depth: **4.400 × 2.600 × 0.800 m**.
- Godot AABB: **(-2.2, 0, -0.4) → (2.2, 2.6, 0.4)**; tolerance ±0.001 m.
- Root and mesh pivot: **(0,0,0)**, centred on the mounting/ground-contact footprint.
- Blender +Z up / +Y front maps once to Godot +Y up / -Z front. Unit scale,
  applied rotation/scale; no compensating prefab transforms.
- Shoe: **4.4 × 0.24 × 0.8 m**, 0.06 m edge bevel.
- Casing: **4.2 × 2.26 × 0.56 m**, bottom Y=0.24, top Y=2.50; 0.06 m bevel.
- Cap: **4.2 × 0.10 × 0.60 m**, bottom Y=2.50, top Y=2.60; 0.025 m bevel.
  Its single lime top sector spans local X=1.14 to 1.80 m. It is a material region
  of the cap itself, not a coplanar overlay; the other top regions remain petrol.
- Front carrier: **3.84 × 1.84 m**, centred at Y=1.42; a closed 0.016 m-thick slab
  whose front plane is Z=-0.29. Side/rear slab faces stay petrol; only the front takes art.
- Four closed source components join into one mesh. The carrier embeds 0.006 m into
  the casing, deliberately avoiding a floating panel; no exposed coplanar surfaces.

### Family mounting contract

Place this support root at **(0,0.28,0)** relative to the
[`d07_sign_island_01.tscn`](../../../scenes/prefabs/environment/d07_sign_island_01.tscn)
base root, with identity rotation/scale. Its front (-Z) then matches the base's lime sector.
The combined top is **Y=2.88 m**. The 4.4 × 0.8 m foot's conservative corner radius is
**2.236068 m**, inside the sibling's **2.58 m** petrol deck radius by **0.343932 m**.
The full foot rests at the flat Y=0.28 deck; its bottom and the deck meet without a gap.
The base retains its own cylinder, while the support retains its own two-box compound.
Do not stack duplicate base instances or move the support down to road level inside the base.

This is a documented composition transform, not a new runtime socket API, auto-placement
rule or saved district arrangement. No source geometry from the sibling is duplicated.
The sibling's current handoff contains no stale pending asset item to resolve; it and its
manifest remain unchanged. Its assembled-support *occlusion review* is still a real
world/engine acceptance gate, not a claim that this hardware is unproduced.

## Source, exports and materials

- Source: `art/source/models/environment/d07_sign_island_02/d07_sign_island_02.blend`.
- Collection: **export_d07_sign_island_02**; root **D07SignIsland02**;
  mesh **D07SignIsland02_Mesh**.
- Export: `art/models/environment/d07_sign_island_02/d07_sign_island_02.glb` plus `.import`.
- Prefab: `scenes/prefabs/environment/d07_sign_island_02.tscn`.
- Parametric recipe, exporter, source/binary validator, engine checker and receipt writer:
  `tools/asset_production/d07_sign_island_02/`.

Original Blender construction only. No downloads, image-to-mesh, purchased geometry,
external fonts/textures, embedded images, prototype dependencies or generated runtime meshes.
Studio ground, lights and camera stay outside the named export collection. Applied bevels
and weighted normals are saved; glTF triangulates the editable source faces. No rig,
clips, destruction states, sockets, custom shaders, lights or authored LODs are required.
Default Godot import LOD/shadow settings remain; repeated-placement cost is not accepted.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**;
`export.py` loads the shared `tools/assets/blender/export_settings.json`, filters the
named collection, and disables animations/skins. No private replacement export contract.

Four opaque, back-culled Principled surfaces; actual source/GLB/Godot slot order:

| Slot | Material | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `sign_island_artwork_face` | .028, .067, .092 | .10 / .60 |
| 1 | `island_body_slate` | .24, .32, .36 | .05 / .65 |
| 2 | `island_deck_petrol` | .028, .067, .092 | .10 / .60 |
| 3 | `island_wayfinding_lime` | .48, .72, .16 | 0 / .50 |

Slots 1–3 match the delivered base palette exactly. Slot 0 is intentionally distinct
but initially petrol so later artwork can affect the front without recolouring hardware.
No emission, transparency, illumination behavior or essential copy is implied.

### Artwork carrier interface

The graphics consumer can reuse this prefab and override **surface 0 only** on
`Visuals/Model/D07SignIsland02/D07SignIsland02_Mesh`. This slot consists of exactly **one front source
quad / two exported triangles / four vertices**, at X=±1.92, Y=0.50..2.34, Z=-0.29.
The back, thickness, casing, cap and shoe do not share the artwork slot.

UV0 fills the rectangle at aspect **48:23**. Seen from the front (camera on local -Z,
looking +Z with +Y up), local +X is screen-left. In Blender, bottom-left is UV(0,0)
and top-right UV(1,1); the exporter converts image V so **Godot/glTF top-left is (0,0),
bottom-right (1,1)**. U=0 is local X=+1.92, U=1 is X=-1.92. Both source, raw GLB
and imported Godot vertices/UVs are asserted independently; ordinary non-flipped artwork
reads unmirrored. Use a clamped opaque face material; this delivery contains no texture.

No override is authored here. The graphics owner should reuse these unchanged Blender/GLB
bytes rather than create a duplicate carrier; if using the narrow saved editable-child
face override exception in [assets.md](../../assets.md#prefabs-and-authored-placement),
that consumer must retain its own two byte-stable save/reload roundtrips and identities.

## Prefab and deliberate collision

**Visuals/Model** is the identity-transform imported GLB instance. No embedded render mesh,
editable children, material override or runtime-built authored hierarchy. Pinned headless
Godot saved prefab UID **uid://c6ixrjw2dg7x1**, GLB UID **uid://yafqxb7cebgu** and stable
node identities. The TSCN carries its scene UID inline; the checker has its `.gd.uid` sidecar.

**Collision/Body** is one StaticBody3D, world layer **1**, mask **0**, with the minimal
**two-box compound** required to block a freestanding prop without inflating its full height:

| Shape | Size X/Y/Z (m) | Centre (m) |
| --- | --- | --- |
| `Foot` | 4.4 / 0.24 / 0.8 | (0, 0.12, 0) |
| `Casing` | 4.2 / 2.36 / 0.6 | (0, 1.42, 0) |

The boxes meet exactly at Y=0.24. The upper box contains the casing, face and cap;
it extends only 0.02 m beyond the broad casing front/back planes, and 0.01 m beyond
the carrier front. Edge bevels are deliberately ignored (at most 0.06 m per-axis at
shoe/casing corners). At Y>0.24 the wider shoe outline is clear rather than an invisible
tall blocker. No open passage, corner gap, duplicate ground plane or decorative snag collider.
The narrow cap is not a new walking route or roof gameplay surface. No traffic, navigation,
climbing, vehicle damage, destruction or authoritative state rule is added.

## Evidence and measured validation

[Hero](d07_sign_island_02-evidence/hero.png) ·
[Side](d07_sign_island_02-evidence/side.png) ·
[Cap/face detail](d07_sign_island_02-evidence/detail.png) ·
[Gameplay-camera overhead](d07_sign_island_02-evidence/overhead_47m_42deg.png).

All four final images were inspected. Isolated Blender Cycles CPU, 24 samples, denoised,
AgX, **1280×720**, RGB PNG compression **95**, no quantization or painted corrections;
each is below 400 KB. The side is slightly oblique to reveal thickness and the face edge.
The overhead is truly vertical-down perspective at **47 m / 42° vertical FOV**, north/+Y
up, fixed yaw. The support reads as an approximately 88-pixel-wide low bar with one lime
segment, not a tower. Its upright face is deliberately not readable in the exact centred
overhead view; orientation comes from the cap and circular-base silhouette, not tiny text.
These images show the support alone, not an assembled island or engine lighting acceptance.

[validation.json](d07_sign_island_02-evidence/validation.json) records:

- **640 triangles**, **328 source vertices**, **332 source faces**, **380 exported vertices**;
  **one mesh / four material surfaces**.
- **Zero degenerate faces/triangles**, **zero nonmanifold edges**, finite coordinates,
  unit-length source/export normals (maximum errors **1.51e-7 / 1.38e-7**).
- Positive signed component-volume sum **6.478212 m³**; this is not a boolean-union volume
  because the closed face slab intentionally embeds in the casing.
- Source, actual binary GLB positions and Godot AABB meet literal expected bounds within
  **1 mm**; source/GLB bounds map within **0.00001 m**. Mounting minimum is exactly zero.
- Fresh export from reopened source is **byte-identical**, **19,936 bytes**, SHA-256
  **919350aa89fdb7056f324bc8938f90909c81315df2918c2a3a81f558da69d231**.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports with **no ERROR/SCRIPT ERROR**.
  Headless editor pack/save/reload/resave is byte-stable, preserving scene/dependency UIDs.
  Fresh non-editor load proves linked ancestry, identity transforms, materials and UV0.
- **Eleven shape queries** pass: foot/casing interior and corners block; above the shoe,
  beyond the face/side, above the cap and below the foot remain clear.
- **Three front rays**, at X=-2/0/+2, all hit the continuous collider at Z≈-0.30.
- Real CharacterBody3D capsules (**radius 0.35 m / height 1.8 m**) using `move_and_collide`:
  ground-level stop **Z=-0.73095703125** against the shoe; raised capsule stop
  **Z=-0.650390625** against the casing; clear bypass at X=2.6 ends **Z=3**.
  These are isolated public-physics-API checks, not production ActorMotion/car/network tests.
- Owned GDScript check-only compilation, **gdstyle lint (100 columns, zero warnings)** and
  **gdstyle fmt --check** pass. No full-project production suite was run.

[final.log](d07_sign_island_02-evidence/final.log) retains the concise final check/diagnostic
receipt; [manifest.json](d07_sign_island_02-evidence/manifest.json) hashes all delivered
payloads except itself. Raw logs and scratch exports stay at `C:/tmp/ft/assets/d07_sign_island_02/`.

### Corrections and tooling limitations

The initial side framing cropped the model; expanding that camera's scale fixed it.
The front U direction was corrected before final source/export validation so future artwork
reads unmirrored. The first capsule assertion expected a casing hit but the wider low shoe
correctly stopped a ground-level capsule earlier. Separate ground and raised sweeps now
prove both blockers; geometry and collision were not altered to satisfy the test.
The artwork inspection helper was separated to satisfy gdstyle function/local limits.

Headless editor normalization exits 0 with passing assertions but retains the existing
pinned-engine/plugin shutdown RID/ObjectDB leak diagnostics, exactly enumerated in the
receipt. This is not described as a clean editor shutdown. Import emits the known Godot
4.8 MCP compatibility warning but no errors; fresh runtime and compile checks are error-free.
Blender author/export/validator exit 0 with only future-API deprecation notices.
No vendor code, engine pin, global project setting or live Blender/Godot session was changed.
Required CLI-only operation used direct-file authoring followed by headless normalization;
this does not claim that a separate open editor is synchronized.

## Exact reproduction

Run from repository root in Bash. Every Blender/Godot invocation is pinned and bounded.
Skip `author-final` when only refreshing receipts for unchanged source/export/renders.
Normalization must use `--editor`; the fresh runtime check does not save scenes.

```sh
set -e
NID=d07_sign_island_02
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="$(mise which gdstyle)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
run_check() {
  local name="$1" code=0
  shift
  "$@" > "$T/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$T/$name.exit"
  return "$code"
}
run_check author-final timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
run_check validate timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
run_check import-final timeout 300 "$G" --headless --path . --import
run_check prefab-normalize-final timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --normalize --output "$T/prefab-normalize-final.json"
run_check compile timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
run_check prefab-fresh timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh.json"
run_check gdstyle-lint timeout 60 "$S" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
run_check gdstyle-format timeout 60 "$S" fmt --check \
  "tools/asset_production/$NID/check_prefab.gd"
# Retain any final engine-normalized import/UID sidecars before commit.
run_check import-final timeout 300 "$G" --headless --path . --import
python "tools/asset_production/$NID/record.py"
```

`validate.py` reopens the source, reexports into scratch using the shared contract and
compares the actual bytes. `export.py` also accepts a scratch output directory after `--`
when run on the saved source in pinned Blender. `record.py` asserts final export hash/size,
scene UID/hash, command exits/diagnostics and render sizes, then regenerates the manifest last.

## Remaining acceptance

1. Independent art/technical review of this exact candidate; no producer self-acceptance.
2. Saved world placement/composition with the circular base, clear forecourt separation,
   actual ActorMotion/car/weapon queries and multiplayer/prediction collision checks.
3. Actual Godot gameplay-camera lighting, final artwork readability and assembled-island
   occlusion review. Upright sign text is not essential overhead information.
4. Import LOD appearance, packaged dependencies, repeated-instance cost and sustained
   target-device performance; headless physics and Blender renders do not establish these.
5. Existing pinned editor/plugin shutdown diagnostics remain a tooling limitation.

No queue, progress, shared brief, catalogue, sibling, world scene, project setting or TODO
was edited. No unproduced family sibling is tracked as a pending task in this handoff.
