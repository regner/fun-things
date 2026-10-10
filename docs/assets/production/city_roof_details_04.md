# city_roof_details.04 — Small pitched-roof chimney

10 October 2026. **Original source, explicit export, linked prefab and bounded validation delivered;
independent review, building attachment and gameplay/device acceptance pending.** Produced by the
assigned implementation specialist on `lane/a-roof`. The direct production assignment and
[commission](commission.md) supersede the historical concept-only status of the
[roof family brief](../city_roof_details.md). No register, shared brief, progress record, sibling
asset or world placement was changed.

## Design and provisional dimensions

A small upright coated chimney stack with a contained inclined apron, raised counterflashing,
broad coping and one tapered round pot. The pot has a real thick rim and recessed dark bore,
closed at its base; it is not a painted disk or an open/non-manifold tube. Broad forms, softened
edges and the exact quiet petrol/folded-metal/shadow palette of `.01`–`.03` keep it subordinate
to the building. No brick noise, neon, branding, smoke, fire, animation, interior, roof-access
mechanic or traversal is supplied.

Original Blender construction only; no downloaded meshes, external libraries, textures or
image-to-mesh process. Read the accepted art direction, district identities and Stage 4 street
context, inspected Old Quay v03 and the completed `.03` and accepted light handoffs. Intended
reuse is The Crescents and Old Quay; Terrace Ward remains a candidate. Placement is sparse,
not one fitting on every roof.

These are **reversible provisional production values**, not inferred concept-image dimensions
or an approved building interface. One fixed 30° roof interface is delivered; other pitches,
ridge-straddling and hipped corners are not silently claimed compatible.

| Interface | Metres / contract |
| --- | --- |
| Plan footprint X × Z | 1.30 × 1.50 |
| Height above centre roof datum | 1.96 |
| Nominal complete vertical extent | 2.393013; includes the downslope apron below the root |
| Measured Godot AABB | (-0.650000, -0.432330, -0.750000) → (0.650000, 1.960000, 0.750000) |
| Measured dimensions X / Y / Z | 1.300000 / 2.392330 / 1.500000 |
| Source/export acceptance tolerance | ±0.001 |
| Apron footprint / vertical thickness | 1.30 × 1.50 / .035 |
| Counterflashing footprint / top above roof plane | .96 × 1.08 / .22 |
| Stack footprint / level top | .76 × .80 / 1.30 |
| Coping footprint / thickness / top | 1.00 × 1.04 / .16 / 1.40 |
| Pot maximum outside diameter / top opening diameter | .55 / .35 |
| Pot top / recessed bore floor / recess depth | 1.96 / 1.416 / .544 |
| Proposed support patch in horizontal plan | 1.40 × 1.60, wholly within one 30° roof face |

Root and mesh origin are at **the centre of the inclined roof-contact plane**, not the lowest
point of the apron. Blender +Z maps once to Godot +Y; Blender +Y is uphill and maps to Godot
-Z. At identity yaw, the roof plane in Godot is `Y = -Z * tan(30°)`. Applied object transforms,
metre units, root/mesh identity and no corrective prefab rotation or scale. The 2 mm apron
edge bevel leaves the measured extreme .683 mm inside the nominal envelope; the broad contact
face remains on the intended plane. Independent source rays at Blender X=.56, Y=±.65 verify
the apron top at -0.340278 / +0.410278 m. A centre-down ray hits the recessed flue floor at
1.416 m, not the rim.

Mount upright at unit scale on a matching 30° roof face, orienting -Z uphill with yaw only.
Do not tilt the stack to fit a different pitch. No roof cut is required for this sealed
exterior decoration. Initial roof-edge/ridge clearance proposal is .50 m from the complete
flashing envelope, consistent with the sparse family intent; actual fit belongs to the
building owner. The flat-roof interface of sibling `.03` is unchanged. This contract does
not pre-empt `.05` or require it to use the same pitch.

## Source, export and materials

- Source: `art/source/models/environment/city_roof_details_04/city_roof_details_04.blend`.
- Collection: `export_city_roof_details_04`; root `CityRoofDetails04`, mesh
  `CityRoofDetails04_Mesh`. Source export collection has no studio geometry, lights or camera.
- Export: `art/models/environment/city_roof_details_04/city_roof_details_04.glb` and its pinned
  Godot-generated `.import` sidecar.
- Prefab: `scenes/prefabs/environment/city_roof_details_04.tscn`.
- Reproduction/assertions: `tools/asset_production/city_roof_details_04/`.

**1,224 source vertices, 2,428 triangles, one mesh, three surfaces.** Actual GLB vertex count
including splits is **1,295**. Six overlapping closed manufactured solids are joined into one
editable mesh; this is not a boolean-unified engineering volume. **Zero degenerate faces or
triangles, zero non-manifold edges**, consistent winding and unit-length source/export normals.
No live modifiers remain. No rigs, clips, sockets or runtime mesh generation.

| GLB surface / Principled material | sRGB swatch | Metallic / roughness |
| --- | --- | --- |
| 0 — `chimney_folded_metal` | `#314D50` | .30 / .55 |
| 1 — `chimney_shadow` | `#172B30` | .05 / .78 |
| 2 — `chimney_dark_petrol` | `#273F43` | .28 / .52 |

Opaque back-culled PBR, sRGB converted to linear; no emission, alpha, images or texture maps.
The plain coated stack and pot intentionally share one material. No external material remaps
or new shared palettes. Godot default automatic LOD generation stays enabled; no measured
performance budget or hand-authored LOD is claimed.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. `export.py` consumes the
existing shared `tools/assets/blender/export_settings.json`, limits the named collection and
disables skins/animation. Existing asset authoring/validation conventions were followed; no
shared geometry-helper module exists in `tools/assets/blender/`, so the small chimney-specific
construction remains local rather than adding a new shared framework.

Fresh-process export of the saved source is byte-identical to the **59,224-byte GLB**, SHA-256:
`0ef49c92a6ea344ca901490b59d47b96ea3b33b34e3d0efbf82c78019a520adb`.
The [producer manifest](city_roof_details_04-evidence/manifest.json) hashes every delivered file
except itself, including source, scripts, normalized scene/import metadata and this document.

## Prefab, collision and engine validation

`Visuals/Model` is the identity-transform linked GLB instance; no editable imported children,
material overrides, embedded mesh data, generated render hierarchy or gameplay scripts.
The wrapper has a saved scene UID and Godot-generated node identities. Imported bounds,
one mesh/three surfaces, opaque back-culling, model linkage and recursive resource/UID
resolution pass. Two headless pack/save/load rounds are byte-stable; a separate standalone
engine process loads the resulting resources without error/warning diagnostics.

**Visual-only, roof-mounted above-head decoration.** No collision body or shape is authored:
the family explicitly forbids rooftop traversal, and the standing production rule permits
purely above-head fittings. Keep **every point above 2.5 m world height** (at identity yaw,
root height at least 2.934 m; the evidence uses 8 m). The enclosing building owns roof and
route collision. This prefab must not be placed freestanding on a street or an accessible
roof; such a use would require a newly reviewed collider and gameplay checks. The test
asserts that this decoration has no collision objects; it does not prove a saved world
placement respects the height restriction.

Pinned Godot **4.8.dev7.official.c971f93e7** performs import, normalization and loading.
No movement, car-contact or network tests are claimed for this noncolliding fitting; no
physics, authority or replication code changed.

## Evidence and visual review

[Hero](city_roof_details_04-evidence/hero.png),
[side/profile](city_roof_details_04-evidence/side.png),
[pot and coping detail](city_roof_details_04-evidence/detail.png),
[47 m / 42° overhead](city_roof_details_04-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders, 32 samples/denoise, AgX, **1280×720**, PNG
compression 95 followed by evidence-only RGB six-significant-bit encoding/PNG level 9. No
runtime texture is altered by evidence compression. Individual images remain below 400 KiB.
This evidence-only quantization can band studio gradients; it is not a runtime shading effect.

Visually inspected all four. The first hero was too tightly framed; widened it. Replaced the
initial square flue floor whose corners showed outside the pot with a contained circular
floor, then reran source/export validation and all four renders. The close-view floor is
horizontal and deliberately below the lowest point, exposing the inclined attachment rather
than pretending this is a flat-footed prop. The profile reads as a vertical stack on a sloped
boot; coping and a single hollow pot carry recognition without small brickwork.

The overhead is **vertical-down, north-up, 47 m world height / 42° vertical FOV**, with the
chimney root at 8 m on a temporary matching 30° studio plane. The fitting occupies roughly
32–38 pixels of footprint height; the broad coping and dark opening remain distinguishable,
while fine bevels appropriately disappear. It does not become a bright roof marker. Studio
surfaces are not exported, committed as geometry or saved as building placement. This isolated
view is not proof of roof/building silhouette dominance in a district; actual production roof
contrast, repetition and off-centre perspective magnification remain placement review gates.

## Exact reproduction

Run Git Bash from this worktree with Pillow and the pinned tools available. Every Blender
call is isolated, factory-started, audio-disabled and bounded. Every direct engine invocation
is headless and bounded. The brief prohibits live/windowed editor use; the prefab was authored
as text then packed/resaved in a private headless process. This does not synchronize any
separate open editor, and no owner live session was touched.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_roof_details_04
S=art/source/models/environment/city_roof_details_04/city_roof_details_04.blend
X=C:/tmp/ft/assets/city_roof_details_04
mkdir -p "$X" docs/assets/production/city_roof_details_04-evidence
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy

timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 "$S" --python "$T/export.py" -- "$X/reexport"
timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$X/reexport/city_roof_details_04.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --editor --path . --script "res://$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" > "$X/check.log" 2>&1
timeout 30 "$(mise which gdstyle)" check "$T/check.gd"
# Use a fresh output directory on each canonical run.
PYTHONUTF8=1 timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$(mise which gdstyle)" --output "$X/checks-final"
python "$T/manifest.py" "$X/checks-final"
# Final pinned import normalizes any owned sidecars; refresh hashes afterward.
timeout 300 "$G" --headless --path . --import
python "$T/manifest.py" "$X/checks-final"
```

[validation.json](city_roof_details_04-evidence/validation.json) retains numeric source/export,
attachment/flue, camera, engine, render and canonical-check results.
[final.log](city_roof_details_04-evidence/final.log) is a concise command/diagnostic receipt.
Scratch exports, first renders and full logs stay outside Git in `C:/tmp/ft/assets/city_roof_details_04/`.

## Diagnostics and remaining acceptance

- Final owned GDScript format/lint/compilation and canonical checks pass: **17 Python tests,
  149 GUT tests / 6,768 assertions**, plus correct detection of the intentional failing test.
  No known-failure exemption was needed. An initial 101-character owned constant line failed
  the strict style gate; rounded the independent expected bound to six decimal places and
  reran successfully without relaxing its 1 mm tolerance.
- The first source validation found the 4 mm apron bevel reduced the extremum more than the
  1 mm tolerance; reduced that bevel to 2 mm, then regenerated and passed. No tolerance was
  widened. Final topology, winding, bounds and byte-identical reexport all pass.
- Blender reports `Material/World.use_nodes` deprecation notices. Its version-only probe
  reports one 0.000023 MB unfreed allocation. Final asset jobs exit 0.
- Headless import reports the existing MCP plugin Godot 4.8 compatibility warning. Headless
  editor normalization passes its assertions but emits renderer/text RID and ObjectDB leaks
  at shutdown. These are retained as diagnostics, not suppressed or claimed clean. Standalone
  asset loading has no error/warning diagnostics.

**Pending:** independent technical/art review at the exact commit; final building pitch/interface,
roof-edge clearances, district selection, actual engine gameplay-camera/roof silhouette and
repeated-placement review; packaged build, sustained GPU/frame pacing and Deck checks. Any
accessible placement must reopen collision and relevant movement/network checks. No whole-city
placement, final performance approval or blanket READY status is claimed.
