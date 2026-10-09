# city_sign_supports.01 — Flat wall panel hardware

9 October 2026. Source specialist producer; ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2`
owns dispatch and downstream integration. Source/export candidate delivered for review;
no engine, prefab, collision, gameplay, performance or production-ready claim.
Commission: [raw user commission](commission.md), overriding historical concept-only
restrictions. This record covers exactly `.01`; no other support or district artwork.
Workspace `wks_59891ad7a05813e5`, supplied branch `art/register-production-20261009`,
base `66400c26a01bf917dfe631af4762c2b444d9c48f`, baseline
`2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`. No Git/index mutation performed.

## Deliverable and ownership

- Editable original [Blender source](../../../art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend).
- Linked [GLB](../../../art/models/environment/city_sign_supports_01/city_sign_supports_01.glb).
- [Authoring](../../../tools/asset_production/city_sign_supports_01/author.py),
  [source validation/export](../../../tools/asset_production/city_sign_supports_01/export.py),
  [independent binary validation](../../../tools/asset_production/city_sign_supports_01/check_glb.py),
  [previews](../../../tools/asset_production/city_sign_supports_01/preview.py),
  [diagnostic PNG generator](../../../tools/asset_production/city_sign_supports_01/make_uv_diagnostic.py),
  [logged command runner](../../../tools/asset_production/city_sign_supports_01/run.py).
- [Exact producer file manifest](city_sign_supports_01-evidence/manifest.json), with byte
  lengths and SHA256 for every deliverable/evidence file except the manifest itself
  (self-hashing exclusion stated in the manifest).

Original geometry, bevel/profile construction, mounting details and UVs authored in
Blender for this task. No downloaded meshes, textures, fonts, logos or unknown-rights
content. Existing project concept PNGs are visual references only. The external UV
quadrant/arrow test image is an original diagnostic, never runtime artwork or a source
material dependency. District artwork remains owned by its separate rows.

## Reference response and reversible dimensions

Read AGENTS.md, docs/assets.md, docs/art-direction.md, commission, city_sign_supports
brief, approved district identities, current district queue/common contract, current
Signal Row/Old Quay briefs, map-context and historical world layout. Visually inspected
current `06-signal-row-v03.png`, `05-old-quay-v03.png`, and exact
`06-signal-row-map.png`. Their quiet dark masses, broad bright graphic areas and small
frontage details inform the panel; their illustrative image dimensions were not measured.
The exact district map, not the older six-block plan, owns placement context. No parcel,
road, wall or saved placement was changed.

The shallow rounded petrol frame and restrained metal mounts support a generous
replaceable face. Broad highlights follow the smooth stylized direction, without neon
hardware, fine grime, a shop-fascia silhouette, arbitrary copy or duplicate district art.
All values below are producer proposals, reversible in the source script, pending
layout/art acceptance; they are not inferred from generated concepts.

| Quantity | Proposed measurement and rationale |
| --- | --- |
| Overall width × height × projection | **1.40 × 1.00 × 0.10 m**; civic/poster scale, modest shallow frontage projection |
| Godot local AABB | min `(-0.70,-0.50,-0.10)`, max `(0.70,0.50,0)` m, tolerance 0.000001 m |
| Blender local AABB | min `(-0.70,0,-0.50)`, max `(0.70,0.10,0.50)` m |
| Pivot | Centre of sign on wall attachment plane; an explicit wall-mounted exception to ground-centred props |
| Mount plane | Blender Y=0 / Godot Z=0; all geometry projects toward Blender +Y / Godot -Z |
| Outer plan corner radius | 0.090 m; broad smooth silhouette with eight segments per quarter |
| Frame opening | 1.24 × 0.84 m, 0.045 m corner radius; frame provides 0.08 m cardinal border |
| Artwork face | 1.22 × 0.82 m, 0.040 m corner radius; about 71% of outer rectangular area |
| Face depth | Blender Y=0.088 / Godot Z=-0.088; recessed 0.012 m from front lip |
| Face safe copy rectangle | 1.14 × 0.74 m centred; stays within the rounded-corner clipping boundary |
| Mount rails | Two 1.10 × 0.10 m rails, centred at Z=±0.28 m in Blender; 0.022 m depth |
| Wall pads | Four 0.13 × 0.085 m pads at X=±0.46, Z=±0.28, spanning Y=0–0.012 m |
| Rear shell | Back begins Y=0.025; concealed rails/pads fill the wall stand-off |
| Suggested review height | Pivot 1.60 m above local ground gives lower/upper edges 1.10/2.10 m; placement proposal only |

Metre units; static transforms applied, all object local transforms identity, root at
origin. Blender +Z up/+Y forward converts once through glTF to Godot +Y up/-Z forward.
No corrective prefab rotation/scale is required. In a front-on view, screen-right is
Blender/Godot **-X**; the artwork UVs account for this, so external images are not mirrored.
Keep the panel on an existing opaque facade away from passage mouths. A 0.10 m visual
projection is not a clearance or collider decision. No collision, navigation, sockets,
rig, animation, interaction, damage states or LODs are supplied. ROOT/integration owns
those decisions if needed; costs and repetition density remain unmeasured.

## Source/export contract

Collection `export_city_sign_supports_01`, root `CitySignSupports01`, exactly these
12 mesh children, all included in the declared export member set:

`rounded_frame`, `rear_shell`, `face_gasket`, `artwork_carrier`,
`mount_rail_lower`, `mount_rail_upper`, `wall_pad_lower_left`,
`wall_pad_lower_right`, `wall_pad_upper_left`, `wall_pad_upper_right`,
`release_tab_left`, `release_tab_right`.

The frame is a closed profiled ring, not four disconnected box strips. Rear shell and
carrier are closed rounded solids; pads, rails and release tabs have applied bevels.
Weighted normals are applied on the hardware. Separate interlocking solids are deliberate;
manifold checks are per mesh, not a boolean-unioned watertight assembly requirement.
Total **2,720 triangles**, 12 mesh nodes, 13 material primitives. Density comes from
rounded silhouettes and bevels; this is not a ratified triangle/draw-call budget.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF **5.2.40**, verified in-process.
Explicit export options: GLB; selection limited to validated collection members;
Y-up conversion; normals and UVs; material export; no cameras/lights/extras/animations/
skins/morphs/tangents; no export-time modifier application (all already applied).
No studio objects, texture dependencies or external libraries in source/export.
Studio geometry is created temporarily by preview.py and never saved/exported.

## External artwork interface

`artwork_carrier` has **slot 0 `sign_face`**, assigned only to the front face, and
**slot 1 `mount_metal`**, assigned to rear/sides. In this GLB, its mesh has primitive 0
for `sign_face` and primitive 1 for `mount_metal`; integrations should resolve by slot
name rather than rely on all-file material index ordering.

Hardware uses `support_petrol`, `recess_gasket`, `mount_metal`; front uses `sign_face`.
Opaque Principled PBR, no emission/alpha textures. Exact exported linear colors,
roughness and metallic factors are in [decoded checks](city_sign_supports_01-evidence/glb_checks.json).
Blender defaults export these materials as double-sided; the independent winding checks
still verify outward normals. Engine culling/material remapping is pending integration.

UV0 is `UVMap`. Front rectangular domain is 0–1, rounded corners clip the image naturally.
Blender mapping: U=(0.610-X)/1.220, V=(Z+0.410)/0.820. glTF flips stored V per its image
convention. A normal top-left-origin PNG reads correctly: diagnostic TL/TR/BL/BR and
upward arrow were visually inspected. Image aspect **61:41** (e.g. 1220×820 diagnostic).
Safe-copy UV inset is about 0.03279 in U and 0.04878 in V. Do not repeat the texture;
clamp at borders and preserve aspect. Resolution/filtering/mip/compression decisions
belong to the actual artwork/material owner and its engine review.

Replace **only `sign_face`** with the external district material. For a textured material,
use white base color multiplier and opaque sRGB albedo on UV0. Hardware and carrier sides
remain unchanged; replacing artwork never requires a new mesh. The source carries a
neutral gray-green placeholder, not approved district art. No runtime texture or material
file is duplicated here. The preview attaches an external diagnostic image without saving
that assignment and restores the original slot before the gameplay-down render.

## Validation and visual findings

[Source checks](city_sign_supports_01-evidence/source_checks.json) and saved-source
[reexport checks](city_sign_supports_01-evidence/reexport_source_checks.json) pass:
metre units, pinned versions, exact collection membership, applied transforms,
closed/manifold/consistent mesh edges, positive volume, finite coordinates/unit corner
normals, no degenerate faces or triangles, expected bounds and front UV mapping.

The [independent decoder](city_sign_supports_01-evidence/glb_checks.json) reads JSON and
binary accessors without Blender or importing author/export code. It checks actual
positions (not accessor bounds alone), unit normals and triangle winding, welded-edge
manifoldness, positive volume, material membership, all 36 artwork-boundary UV samples,
identity node transforms/hierarchy and absence of cameras/lights/skins/animations/textures.
Saved-source export is **byte-for-byte identical**, 75,768 bytes, SHA256
`5f54105825e00bb73c038bed252910abec548ad1beb81603b2713c2c69796e0b`.

Inspected [hero](city_sign_supports_01-evidence/hero.png),
[detail](city_sign_supports_01-evidence/detail.png),
[rear](city_sign_supports_01-evidence/rear.png),
[UV interface](city_sign_supports_01-evidence/uv_interface.png), and
[gameplay-down](city_sign_supports_01-evidence/gameplay_down.png).
Hero/detail show smooth broad highlights, a clear inset gasket and generous face;
rear shows two consistent concealed rails/four pads. Diagnostic artwork reads upright
and unmirrored; this demonstrates a material interface, not district artwork acceptance.

The gameplay-down image is a **Blender source preview**, 1280×800, vertical perspective,
42° vertical FOV, 47 m above a notional ground plane, north-up. The test facade is
7 × 4 × 3 m, panel centre 1.60 m above ground, camera offset 8 m right/9 m forward.
The panel is a small, strongly foreshortened strip; copy cannot be claimed readable.
At directly overhead alignment a vertical wall face tends to edge-on. This hardware
must not become mandatory gameplay wayfinding without an independently visible cue.
This is not a Godot capture, approved placement, calibrated district lighting, runtime
visibility, occlusion, collision or target-device performance test. Exact cameras and
render settings are in [preview settings](city_sign_supports_01-evidence/preview_settings.json).

## Failures, fix cycle and reproducibility

Full process argv/environment/PID/exit/timing records:
[execution.json](city_sign_supports_01-evidence/execution.json); same labels name raw logs.
`--help` confirmed `-noaudio` before authoring. Audio overrides were process-local
`ALSOFT_DRIVERS=null`, `SDL_AUDIODRIVER=dummy`. No global audio configuration or unrelated
process was changed or terminated.

- `author_01` exit 1: lower release tab reached -0.5005 m versus -0.5000 m contract.
  One owned geometry correction moves its centre from -0.496 to -0.494 m. Failed script
  and failed .blend retained. The same run's optional thumbnail write to the default
  user cache was blocked; subsequent processes use owned evidence `process_cache`.
- `author_02` exit 0: corrected bounds and all source/export assertions pass.
- Initial optional Pillow diagnostic generator failed because Pillow is absent. Exact
  failed command/output retained in `uv_pillow_failure.log`; replaced with standard-library
  PNG writer, `diagnostic_01` exit 0; no environment/package changes.
- `previews_01` exit 1 at missing diagnostic PNG, after producing hero/detail/rear.
  `previews_02` exit 0 after the diagnostic existed. Second run also explicitly uses
  factory startup; the first run logged BlenderMCP addon registration/unregistration
  from local startup preferences, but no live tools/session operations were called.
- `reexport_01` exit 0; scratch GLB retained for direct byte comparison.
- `glb_checks_01` exit 1: checker incorrectly required exact nonnegative U despite
  float32 rounding at the edge. Original checker retained; `glb_checks_02` exit 0
  applies the same 1e-6 numeric tolerance to U as V. No source/output mutation for this.
- Blender reports the known `Material.use_nodes` future-deprecation warning; it is
  retained, not suppressed. Successful reruns have no new error diagnostics.

To reproduce, run from workspace root (fresh log labels are required by run.py):

```sh
python tools/asset_production/city_sign_supports_01/run.py reproduce_export /usr/bin/blender -b -noaudio --factory-startup art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend --python-exit-code 1 --python tools/asset_production/city_sign_supports_01/export.py -- docs/assets/production/city_sign_supports_01-evidence/reexport_city_sign_supports_01.glb docs/assets/production/city_sign_supports_01-evidence/reexport_source_checks.json
python tools/asset_production/city_sign_supports_01/run.py reproduce_check python tools/asset_production/city_sign_supports_01/check_glb.py
```

All owned Blender processes completed and returned exit status; no writer is left
running. [Final audit](city_sign_supports_01-evidence/final_audit.json) records process
and file checks. Source tree is covered by existing `art/source/.gdignore`; evidence
by existing production `.gdignore`. No shared docs, prefab, project/world, Git/index,
engine imports or live editor writes were made. Engine import sidecars, source-linked
prefab, scene save/reload, material remap, placement/clearance and device/runtime
acceptance remain downstream and pending. Source/visual independent acceptance is
also pending ROOT's review; this report is producer evidence.
