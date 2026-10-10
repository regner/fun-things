# city_roof_details.03 — Roof access housing

10 October 2026. **Original source, explicit export, linked prefab and bounded checks delivered;
independent review and world/gameplay/device acceptance pending.** Produced by the assigned
implementation specialist on `lane/a-roof`. The direct production assignment and
[common commission](commission.md) supersede the historical concept-only restriction in the
[roof family brief](../city_roof_details.md). No shared brief, register, progress record or world
placement was changed.

## Design and provisional dimensions

A compact sealed rooftop stair-head housing: shallow rear-falling drip cap, continuous flashing
and raised curb, fixed access-door face with broad kick plate, quiet pull, and one three-blade
side intake. Original Blender construction; no downloads, external model libraries, generated
runtime meshes, textures, artwork or brands. No interior, opening, roof-access mechanic, rig,
clips, sockets, smoke or destruction state is supplied.

Read the accepted art direction, district identities and Stage 4 street context. Inspected the
accepted roof-shape sheet and the existing roof vent/enclosure handoffs. This housing preserves
their sparse functional forms and exact dark-petrol/folded-metal/shadow palette. The shape is
intentionally ordinary and subordinate to the supporting building; there is no bright roof trim.
District reuse is still a candidate, not a requirement to place one on every roof.

The following are **reversible provisional production dimensions**, not measurements inferred
from a concept image or newly approved building interfaces:

| Interface | Metres / contract |
| --- | --- |
| Nominal Godot width X / height Y / depth Z | 3.20 / 2.85 / 3.80 |
| Measured Godot AABB | (-1.600000, 0, -1.900000) → (1.600000, 2.849323, 1.900000) |
| Source/export numeric tolerance | ±0.001 |
| Flashing footprint / thickness | 3.20 × 3.80 / 0.04 |
| Raised curb footprint / top | 3.04 × 3.64 / 0.24 |
| Main housing footprint | 2.90 × 3.50 |
| Folded cap footprint | 3.12 × 3.72 |
| Cap nominal rear / front top | 2.71 / 2.85; small edge bevel reduces measured maximum |
| Fixed door face width / height | 1.10 / 2.08; lower edge 0.26 |
| Minimum proposed level support patch | 3.30 × 3.90 |
| Roof-contact datum | Root and mesh origin at centre of flashing underside, Y=0 |

Metre units and applied identity transforms. Blender +Y is the door/front, mapped once by glTF
to Godot -Z; Blender +Z maps to Godot +Y. Keep the imported model at identity: do not correct
scale or axes in the wrapper. All fittings stay within the flashing plan envelope.

Mount on a **level roof** at unit scale, with no roof cut. A pitched roof needs a separately
owned level adapter; do not tilt this flat flashing to fit. Suggested initial visual clearance
is 0.50 m from its envelope to parapets/edges, matching `.01`/`.02`; this is not an accepted
safety or traversal clearance. Final attachment and district use belong to the building owner.
No `.04` or `.05` output existed earlier in this sequential lane; their roof-pitch interfaces
are not pre-empted here.

## Source, export and materials

- Source: `art/source/models/environment/city_roof_details_03/city_roof_details_03.blend`.
- Collection: `export_city_roof_details_03`; root `CityRoofDetails03`, mesh
  `CityRoofDetails03_Mesh`. No studio geometry, cameras or lights in the source export.
- Export: `art/models/environment/city_roof_details_03/city_roof_details_03.glb`, with pinned
  Godot-generated `.import` sidecar.
- Prefab: `scenes/prefabs/environment/city_roof_details_03.tscn`.
- Reproduction and assertions: `tools/asset_production/city_roof_details_03/`.

**1,344 source vertices, 2,632 triangles, one mesh, three surfaces**; actual GLB vertices
including material/normal splits: **1,582**. Fourteen overlapping closed manufactured solids
remain editable in the joined source mesh. They are not a boolean-unified engineering building.
Zero degenerate faces/triangles and zero non-manifold edges. Source and exported normals are
unit length; GLB triangle winding agrees with normals. No live modifiers remain.

| GLB surface / material | sRGB swatch | Metallic / roughness |
| --- | --- | --- |
| 0 — `roof_access_folded_metal` | `#314D50` | .30 / .55 |
| 1 — `roof_access_shadow` | `#172B30` | .05 / .78 |
| 2 — `roof_access_dark_petrol` | `#273F43` | .28 / .52 |

Opaque, back-culled Principled PBR, with sRGB converted to linear like `.01`/`.02`. No emission,
alpha, texture maps, embedded images or external material remapping. Textures are unnecessary
for these broad solid colors. Godot's default per-import LOD generation remains enabled; no
hand-authored LOD or measured performance budget is claimed.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, exporter **5.2.40**. `export.py` reads the shared
`tools/assets/blender/export_settings.json`, restricts to the named collection and disables
skins/animations. No project-wide setting or shared tool was changed. Author/export/validation
and fixture patterns follow the accepted light and service-prop examples, with asset-specific
literal geometry, bounds and contact expectations.

Fresh-process reexport of the saved source is byte-identical to the **69,616-byte GLB**:
`79c6bfa44909ea903752f36ff3d8acf34036448746879629e63bf562e294047e` (SHA-256).
The [producer manifest](city_roof_details_03-evidence/manifest.json) hashes every delivered file
except itself, including generated import metadata, scripts, saved scenes and this record.

## Prefab, collision and bounded engine evidence

`Visuals/Model` is an identity-transform instance of the GLB, not editable copied geometry.
A separate `Collision/Body/Shape` contains **one BoxShape3D**, size `(3.04, 2.72, 3.64)` at
`(0, 1.36, 0)`, static layer 1 / mask 0. This conservative shell/curb envelope obeys the standing
production rule that a freestanding structure must block a contacting actor; it does not create
rooftop traversal. The thin flashing lip and above-head cap overhang are decoration. The closed
door is not independently collidable or interactive. Supporting buildings retain their own roof
and route collision. Do not use this collider as a walkable-roof contract.

Pinned Godot **4.8.dev7.official.c971f93e7** imported the GLB and loaded all transitive dependencies
and serialized UIDs. Prefab and saved test fixture were packed/resaved headlessly, then loaded
and saved again byte-stably. Imported bounds, one mesh/three surfaces, back-culling, opaque
materials, source-linked identity and one-body/one-box collision all pass.

The owned `physics_check.tscn` uses a collision-only test floor and production `ActorMotion`
with the actual radius **0.35 m**, height **1.8 m** capsule. It contains no generated render meshes.
`check.gd` exercises three solid/overhead rays and six movement cases: front, clear side and rear,
each in `AUTHORITY` and `REPLAY`. Independent expected contacts are ±2.171 m with 0.02 m tolerance.
For 120 steps per movement case, both modes yield:

- Front stop Z **-2.170900106 m**; rear stop Z **2.170900106 m**.
- Clear-side route at X=2.0 ends at Z **6.000000954 m**.
- Rays at Y=.2/1.2 hit front Z=-1.82; the Y=2.9 ray clears the housing.
- A second fresh standalone engine process produces an identical complete receipt.

These are bounded production-motion/query and separate-process equivalence checks, **not**
multiplayer transport/admission, car handling, rooftop gameplay or actual district acceptance.
No gameplay simulation code was changed.

## Evidence and visual review

[Hero](city_roof_details_03-evidence/hero.png),
[side](city_roof_details_03-evidence/side.png),
[door detail](city_roof_details_03-evidence/detail.png),
[47 m / 42° roof context](city_roof_details_03-evidence/overhead_47m_42deg.png).
All are isolated Blender Cycles CPU renders, 32 samples/denoise, AgX, **1280×720**, PNG compression
95 followed by evidence-only RGB six-significant-bit encoding and PNG level 9. No imagegen or
render-to-mesh process is used. These are not Godot captures.

The first hero framing was widened so the cap and flashing have breathing room; the geometry
did not change. The initial seven-bit hero exceeded the evidence size gate; six-bit encoding
reduced the final files to 229–274 KB each. This evidence-only quantization can band studio
gradients; source/export shading is unchanged. Visually inspected all four final views.
The door, cap fall, curb and sparse
louver rhythm read in close views; small hardware disappears overhead as intended.

The overhead is vertical-down, north-up, **47 m world height / 42° vertical FOV**, using the
unchanged `art/models/brackett_greybox/shop.glb` as a read-only scale reference. The shop is
18×15×10 m at its original transform/materials; the housing is translated to Blender `(3,2,10)`
for this temporary render only. Hash equality and measured reference bounds are asserted.
The housing footprint is **4.50%** of that roof area. The broad building outline remains the
stronger shape; actual dark production roof material response and tower-edge magnification
still require placement review. This temporary reference composition is never exported or
saved as a world placement.

## Exact reproduction

Run Git Bash from this worktree with the pinned tools and Pillow installed. Every Blender
process is factory-started, bounded and audio-disabled; no live Blender/Godot session is used.
Editor-managed files were authored as text then normalized only in private headless processes
because the brief prohibits live/windowed editor use. This does not synchronize any separate
open editor.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_roof_details_03
S=art/source/models/environment/city_roof_details_03/city_roof_details_03.blend
X=C:/tmp/ft/assets/city_roof_details_03
mkdir -p "$X" docs/assets/production/city_roof_details_03-evidence
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy

timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 "$S" --python "$T/export.py" -- "$X/reexport"
timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$X/reexport/city_roof_details_03.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --editor --path . --script "res://$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" > "$X/check.log" 2>&1
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" > "$X/check-second-process.log" 2>&1
timeout 30 "$(mise which gdstyle)" check "$T/check.gd"
# This output directory must be fresh; use a new directory for subsequent reproductions.
PYTHONUTF8=1 timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$(mise which gdstyle)" --output "$X/checks-utf8"
python "$T/manifest.py" "$X/checks-utf8"
# Import the final compact PNG bytes, then refresh hashes of normalized sidecars.
timeout 300 "$G" --headless --path . --import
python "$T/manifest.py" "$X/checks-utf8"
```

[validation.json](city_roof_details_03-evidence/validation.json) retains numeric geometry,
materials, camera/reference, engine, movement, render and canonical-check receipts.
[Final check log](city_roof_details_03-evidence/final.log) is concise; scratch renders and full
logs remain outside the repository under `C:/tmp/ft/assets/city_roof_details_03/`.

## Checks, diagnostics and remaining acceptance

- Pinned owned GDScript lint/format/compilation passed. Canonical production checks passed:
  **17 Python tests, 149 GUT tests / 6,768 assertions**, including expected detection of the
  intentional failing diagnostic test. No known-failure exemption was needed.
- Initial default-environment canonical invocation failed during Windows cp1252 subprocess
  decoding, before engine verification. Re-running with `PYTHONUTF8=1` and explicit
  mise-resolved engine/gdstyle paths passed. No repository tooling was patched around it.
- Blender source/export/render jobs passed; `Material/World.use_nodes` deprecation notices
  are retained as pin diagnostics. The version-only probe reported one 0.000023 MB unfreed
  allocation; it is not treated as a geometry failure.
- Headless import passed with the existing MCP plugin's Godot 4.8 compatibility warning.
  Headless editor normalization passed all assertions but emitted renderer/text RID and
  ObjectDB shutdown-leak diagnostics. Both standalone asset checks passed without error or
  warning diagnostics. These editor diagnostics are recorded, not suppressed or called clean.

**Pending:** independent technical/art review at the exact commit; actual level-roof mounting,
district selection, production roof contrast and fixed-camera occlusion; car contacts where
placement permits them; real network transport/authority checks; packaged build, repeated-scene
cost, sustained GPU/frame pacing and Deck checks. No whole-city placement or blanket READY
claim is made. The register and other lane assets remain untouched.
