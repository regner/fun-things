# d07_trolley_shelter.02 — Single trolley

**Source/export and bounded headless prefab checks delivered; independent review and
world/gameplay acceptance pending.** Producer: commissioned implementation specialist.
The register production task and [commission](commission.md) supersede the historical
concept-only restriction in the [family brief](../d07_trolley_shelter.md).

## Design and dimensions

Original static retail trolley: tapered pale metal basket, sparse thick ribs, pressed
basket floor, dark petrol cantilever frame, four small rubber wheels and a broad coral
push handle. No brand, lettering, goods, child seat, coin mechanism or dense wire mesh.
The rear basket aperture is intentionally open for static nesting rather than modeling
an operable gate. This is dressing, not a shopping/pushing system or loose rigid body.

Original Blender construction only; no downloads, purchased/generated meshes, external
fonts, textures or image-to-mesh. Direction references: Petrol & Coral, approved
Stage 3 Broadlot identity and Stage 4 street hierarchy. The already-delivered
[short shelter](d07_trolley_shelter_01.md) supplies family palette, metre scale and datum;
its files are unchanged. Broadlot parking-row placements remain downstream.

Dimensions are **provisional authored choices**, not measurements inferred from concept
art. Envelope tolerance ±0.001 m; source/GLB coordinate comparison tolerance 0.00001 m.

| Contract | Metres, Godot local axes |
| --- | --- |
| Width X × height Y × depth Z | 0.680 × 1.080 × 1.050 |
| Visual AABB minimum / maximum | (-0.340, 0, -0.525) / (0.340, 1.080, 0.525) |
| Root and mesh origin | (0, 0, 0), ground-centred footprint |
| Front | Narrow basket nose at local -Z; Blender +Y maps to Godot -Z |
| Handle axis | X, centre (0, 1.045, +0.490), 0.070 diameter |
| Wheels | 0.190 diameter; ground contacts at Y=0 |
| Rear wheel centres | (±0.285, 0.095, +0.430) |
| Front wheel centres | (±0.215, 0.095, -0.430) |
| Basket upper rail centres | Rear X ±0.315 / Y 1.000 / Z +0.350; front X ±0.240 / Y 0.940 / Z -0.430 |
| Basket floor | Rear Y 0.530, front Y 0.660; 0.018 thick |

**Sibling handoff:** `.03` must compose existing `.02` imports/prefabs, not create another
trolley design or export. The rear aperture, rising floor, taper and rear-only basket
braces leave room for a leading basket to enter the trolley in front. A 0.45 m longitudinal
pitch is a provisional arrangement starting point, **not a tested nesting acceptance**;
`.03` owns final count, fitted arrangement and overlap review. Copies facing into the
shelter rear rotate 180° about Godot Y, while retaining the trolley's own -Z front.
Keep all copies inside the shelter's proposed X [-1,+1], Z [-1.30,+1.20], Y <1.50 region.
The one-box standalone collider deliberately fills the trolley; the assembly owner must
use a deliberate group collision envelope rather than assume visual nesting means a
walkable gap. No shelter or group placement is authored by this record.

## Source, exports and materials

- Source: `art/source/models/environment/d07_trolley_shelter_02/d07_trolley_shelter_02.blend`.
- Collection: `export_d07_trolley_shelter_02`.
- Root / mesh: `D07TrolleyShelter02` / `D07TrolleyShelter02_Mesh`.
- Export: `art/models/environment/d07_trolley_shelter_02/d07_trolley_shelter_02.glb`
  plus the pinned engine's `.import` sidecar.
- Prefab: `scenes/prefabs/environment/d07_trolley_shelter_02.tscn`.
- Tools: `tools/asset_production/d07_trolley_shelter_02/` contains author.py, export.py,
  validate.py, check.gd (+ UID) and record.py.

Blender 5.2.2 LTS (`d13f752e3b9c`), glTF exporter 5.2.40. Metric units, applied
rotation/scale, no negative scales. Closed manufactured mesh islands are joined into
one export mesh; intersecting manufactured joints are deliberate, not a boolean union.
Shared `tools/assets/blender/export_settings.json` is loaded directly. The author reuses
material/finish/studio helpers from sibling `.01/author.py`; validation reuses that
sibling's binary-accessor decoder. Those dependencies are read-only. No shared generic
production validator exists, so asset-specific assertions remain local.
Studio cameras, ground and lights are outside the named export collection.

Four opaque backface-culled Principled surfaces in stable slot order. Linear RGB:

| Slot | RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `trolley_frame_petrol` | (0.025, 0.075, 0.090) | 0.45 | 0.46 |
| `trolley_basket_metal` | (0.550, 0.640, 0.650) | 0.65 | 0.38 |
| `trolley_wheel_rubber` | (0.018, 0.028, 0.032) | 0 | 0.72 |
| `trolley_handle_coral` | (1.000, 0.168, 0.110) | 0.10 | 0.48 |

No embedded images, runtime textures, external materials, sockets, rigs, animations,
destruction states or manual LODs. Default Godot generated LODs and shadow meshes remain
enabled. Four surfaces are a measured count, not a ratified population performance budget.

## Prefab and collision

`Visuals/Model` is an identity-transform linked imported instance. No copied vertex data,
editable imported-child overrides, corrective rotations/scales or runtime hierarchy builder.
`Collision/TrolleyBody` is one static-world body, layer 1 / mask 0, with one direct-child
`Envelope` box: size (0.680, 1.080, 1.050), centre (0, 0.540, 0). This intentionally
fills basket, wheel and frame gaps to prevent snagging/passing through a freestanding
prop. It is not precision bullet-cover geometry or an accessible basket interior.

Only isolated headless Godot was used: the task prohibits live MCP/editor sessions and
reports the windowed editor unavailable. The wrapper was authored as text and normalized
by load/pack/resave, followed by byte-stable save/reload. Final geometry reexport retained
the same scene/dependency UIDs and node identities on a second double roundtrip. This is
saved-resource evidence, not synchronization of any separate open editor.

## Evidence and reproduction

[Hero](d07_trolley_shelter_02-evidence/hero.png),
[side](d07_trolley_shelter_02-evidence/side.png),
[handle/basket detail](d07_trolley_shelter_02-evidence/detail.png),
[47 m / 42° overhead](d07_trolley_shelter_02-evidence/overhead_47m_42deg.png).
All four final renders were visually inspected. Close views show the basket taper, wheel
stance, open rear and quiet family colours. Initial cap shading pinched; small handle,
wheel and hub bevels corrected it. Front basket support posts were replaced with rear
cantilever braces to avoid intruding into the receiving basket of a nested copy.

At actual overhead distance the trolley is a small pale tapered patch with a coral rear
edge; fine ribs correctly disappear. The floor retains the basket mass instead of relying
on subpixel wire. Standalone recognition is necessarily modest at this scale; shelter and
parking context, the nested group and engine lighting still need review. No enlarged
model, fake gameplay close-up or essential tiny lettering was used to claim readability.

Evidence is isolated Blender Cycles/AgX, CPU 32 samples, not engine captures. 1280×720
maximum, PNG compression 100 at render; record.py retains six significant bits/channel
with lossless PNG compression level 9 for lean review files. Overhead is vertical-down
perspective, 47 m height, 42° vertical FOV, Blender +Y at image top. Studio settings are
reused from `.01` and camera framing is in author.py.

From repository root in Git Bash (all engine invocations bounded):

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d07_trolley_shelter_02
S=C:/tmp/ft/assets/d07_trolley_shelter_02
mkdir -p "$S"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" -- --normalize
timeout 30 "$(mise which gdstyle)" check "$T/check.gd"
PYTHONUTF8=1 timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$(mise which gdstyle)" --output "$S/checks"
python "$T/record.py" --checks "$S/checks"
timeout 300 "$G" --headless --path . --import
python "$T/record.py" --checks "$S/checks"
```

The suite output directory must be fresh/empty for each new run. To export without
reauthoring, open the committed `.blend` with the same Blender CLI prefix and execute
`export.py -- C:/tmp/ft/assets/d07_trolley_shelter_02/reexport`. validate.py does exactly
that fresh-source export comparison; it does not use author.py to recreate the source.

## Validation results

[validation.json](d07_trolley_shelter_02-evidence/validation.json) records measured source,
actual binary GLB accessors, imported engine bounds and suite outcomes.
[manifest.json](d07_trolley_shelter_02-evidence/manifest.json) contains SHA-256 of every
produced payload except itself. [final.log](d07_trolley_shelter_02-evidence/final.log) is
the concise receipt; raw logs and scratch reexports remain outside the repository.

- **4,296 triangles; 2,240 source vertices; 3,550 exported vertices; one mesh / four surfaces.**
- Zero degenerate source faces, source/export triangles and non-manifold source edges.
  Unit-length source/export normals, maximum error below 0.000001.
- Imported bounds match 0.680 × 1.080 × 1.050 m; ground datum zero.
- Fresh export byte-identical: 143,548 bytes; SHA-256
  `ce51d11d469a69b0ab9f04ebcda2e10332f8bc4ce24e6872933d796a12434b25`.
- Pinned Godot 4.8.dev7.official.c971f93e7 passes dependency/UID resolution, identity
  imported instance, opaque material count, dimensions, one-box collision and stable
  double save/reload. No missing dependency or asset script errors.
- Four contact-plane rays hit X ±0.340 and Z ±0.525 at Y 0.600; a ray above at Y 1.200
  is clear. Capsule r=0.35 / h=1.8 passes three bypass and three overlap expectations.
  These are bounded public physics queries, not ActorMotion or car movement tests.
- gdstyle formatting/lint passes. Full production suite passes owned-script checks,
  **17 Python tests**, **149 GUT tests / 6,768 assertions**, and negative-test detection.
  No known-failure exception was needed. Windows Python uses UTF-8 and explicit
  mise-resolved binaries to avoid the sibling's previously diagnosed discovery issue.
- Import emits the existing MCP plugin's Godot 4.8-versus-4.7 support warning only;
  no live session was contacted and no project/plugin configuration was changed.

## Remaining acceptance

Independent art/technical review is pending. [The `.03` delivery](d07_trolley_shelter_03.md)
provides the fitted three-trolley group and group collision; the world integrator owns
sparse parking-row placement, actor/car bypass widths,
under-shelter occlusion and retail recognition in the actual fixed gameplay camera.
ActorMotion movement, car contact, weapon queries, authoritative/predicted multiplayer,
repeated-placement LOD/shadows, packaged builds and sustained Deck performance are **not
tested**. No district placement, register-ready status, content budget or broader gameplay
acceptance is claimed.
