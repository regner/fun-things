# d01_lighthouse.01 — Coastal lighthouse assembly

10 October 2026. **Source/export and linked prefab delivered; bounded technical checks pass.
Independent review, district placement and full gameplay/device acceptance remain pending.**
Production commissioned by Regner under decision 47 and the current common production brief,
which supersede the concept-only language in [the family brief](../d01_lighthouse.md) and the
historical [commission](commission.md). Original model, integration and self-review: commissioned
implementation specialist. Parent orchestration owns independent review and acceptance.

## Design and dimensions

An original traditional coastal lighthouse: slender ivory masonry taper, broad muted red upper
band, sealed arched base doorway, two narrow arched windows, flared gallery, circular metal
railing, octagonal warm-glazed lantern, dark petrol cap and finial. The Northpoint v04 concept,
[Northpoint identity](../../concepts/world-v1/stage-03-district-identities/README.md), street
hierarchy and selected district map were inspected. Smooth broad surfaces, sparse fittings and
quiet petrol metal follow Brackett rather than noisy weathering. No external geometry, downloaded
textures, brands, terrain, keeper's house, interior, stairs, beam or rotating-beacon behavior.

**All dimensions are provisional production proposals**, not measurements approved from the
concept image. Proposed height is 15 m to keep the coastal cue compact relative to the future
university clock tower; that relative hierarchy still requires the district integration review.

| Feature | Authored metres |
| --- | --- |
| Whole visual bounds, Godot X/Y/Z | min (-2.2, 0, -2.2), max (2.2, 15, 2.2) |
| Whole size | 4.4 wide × 15 high × 4.4 deep |
| Ground plinth | 4.10 m diameter, bottom Y=0, top Y=0.34 |
| Masonry shaft | radius 1.75 at Y=0.26, tapering to 1.156 at Y=10.80 |
| Red band | Y=8.35–10.45, part of the continuous closed shaft mesh |
| Gallery | maximum radius 2.2; rim Y=10.94–11.10 |
| Circular handrail | centre radius 2.10, Y=12.12, tube radius 0.05 |
| Lantern pane volume | octagonal radius 1.145; Y=11.45–13.22 |
| Roof | eave radius 1.50 at Y=13.34–13.43; finial ends at Y=15 |
| Sealed doorway | arch surround 1.34 wide, Y=0.25–2.71; door leaf 0.94 wide |

Envelope/datum acceptance tolerance is ±0.001 m. Ground-centred pivot at (0,0,0), metre units,
identity root/mesh transforms, Blender +Y doorway front → Godot -Z, Blender +Z → Godot +Y.
The tower has no attachment sockets, variants, rig, animation or destruction state.

## Source, export and materials

- Source: `art/source/models/environment/d01_lighthouse_01/d01_lighthouse_01.blend`.
- Named export collection: `export_d01_lighthouse_01`; root `D01Lighthouse01`, one child
  `D01Lighthouse01_Mesh`. All parts are editable closed solids joined into one static mesh;
  manufactured overlaps are intentional, not a boolean-unioned print mesh.
- Explicit output: `art/models/environment/d01_lighthouse_01/d01_lighthouse_01.glb` and its
  pinned-engine-generated `.import`. No prototype dependencies or embedded images.
- Reproducible construction, export, validation, rendering, physics/dependency check and manifest
  entrypoints: `tools/asset_production/d01_lighthouse_01/`.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
  `export.py` loads the shared `tools/assets/blender/export_settings.json`, narrows export to the
  named collection and disables skins/animations. Modifiers are applied before saving.
- Mesh normals keep broad radial surfaces smooth and end caps flat; weighted corner normals are
  retained on small beveled fittings. No studio geometry/camera/lights are saved in the source or GLB.

Exported material/surface order (all opaque, back-face culled Principled PBR):

| Slot | Name | Treatment |
| --- | --- | --- |
| 0 | `lighthouse_pale_stone` | Plinth, gallery and arch surrounds; roughness .73 |
| 1 | `lighthouse_ivory_masonry` | Main shaft/cornice; roughness .72 |
| 2 | `lighthouse_muted_red_band` | Broad quiet upper accent; roughness .57 |
| 3 | `lighthouse_petrol_metal` | Cap, gallery rails, lantern frame and door; metallic .45, roughness .40 |
| 4 | `lighthouse_warm_glazing` | Amber opaque illuminated glazing appearance; emission strength .65 |
| 5 | `lighthouse_door_window_recess` | Sealed dark inset faces; roughness .58 |

Actual exported RGB/PBR values are in `validation.json`. Opaque warm glazing avoids transparency
sorting and implies a lit lantern without a real light, physical lens or beam. No textures,
external materials or material overrides are required. Default Godot import LODs and shadow meshes
are retained; no measured LOD/device budget is claimed. This is a single landmark, not a repeated
street-fixture cost target.

## Prefab and collision

`scenes/prefabs/environment/d01_lighthouse_01.tscn` instances the explicit GLB at
`Visuals/Model` with identity transform. Saved scene/dependency UIDs and node IDs were normalized
by pinned headless Godot and survive two load/pack/save passes with identical bytes. No embedded
render mesh or runtime-authored node hierarchy exists. No live Blender/Godot editor session was
used: the brief prohibits those sessions and the windowed editor is unavailable, so the wrapper
was text-authored and headlessly normalized.

One `StaticBody3D` at `Collision/Body`, layer 1 / mask 0, has one direct cylinder shape:
**radius 2.05 m, height 10.8 m, centre (0,5.4,0)**. It blocks the freestanding tower and closed
doorway without decorative snag shapes. This is a conservative ground-access envelope: the upper
taper is narrower, while the ground foot/door define approach clearance. Gallery, rails, lantern
and roof are inaccessible overhead decoration beginning above 10.6 m, not playable decks;
there is no route, interior or climb system to reach them. Do not place adjacent elevated routes
against this prefab without a separately reviewed collision/access change.

Placement must keep the 4.4 m visual envelope landward of the continuous boardwalk, its open
seaward edge and clear landward approach. Reserve a provisional 8 × 8 m unobstructed landward
plot for review (tower plus approach margin); this is not saved placement or a new terrain pad.
No coastline, road, district boundary, boardwalk or other asset was changed.

## Evidence and actual validation

[Hero](d01_lighthouse_01-evidence/hero.png) · [Side](d01_lighthouse_01-evidence/side.png) ·
[Lantern detail](d01_lighthouse_01-evidence/detail.png) ·
[47 m / 42° overhead](d01_lighthouse_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender CPU Cycles renders at **1280×720**, 32 samples, AgX, PNG compression
95 followed by RGB 6-bit/channel compaction and compression 9. Each is below 400 KiB. They were
opened and visually inspected, including after the final source normal correction. The side-view
studio horizon and tight detail crop were corrected. These are **not engine captures**.

The exact vertical-down perspective overhead uses height 47 m, vertical FOV 42°, +Y at image top.
It shows the compact dark radial roof within its gallery ring, about 115 pixels across. At the
camera centre the roof/gallery self-occlude the red band, shaft and warm lantern; those read in
the oblique hero/side/detail only. No claim that elevation colors are reliable overhead wayfinding.
Actual off-centre Northpoint placement and gameplay-camera recognition remain a review gate;
no exaggerated beacon or terrain was added to bypass it.

`d01_lighthouse_01-evidence/validation.json` records:

- **18,500 triangles, 9,374 source vertices, 11,991 exported vertices, one mesh, six surfaces**.
- Zero degenerate source faces and zero non-manifold edges. All exported triangles have nonzero
  area, consistent normal/winding orientation and unit-length normals. All transforms applied.
- Source and actual binary GLB vertex bounds match the provisional dimensions/datum above.
- No cameras, images, skins or animations in the two-node GLB. **500,744 bytes**.
- Fresh independent-process re-export is **byte-identical** to the delivered GLB.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports and loads every dependency/UID, checks
  identity-linked mesh ancestry, measured bounds, six opaque back-culled surfaces and single
  cylinder filters/dimensions. No missing dependencies.
- Four physics rays confirm tower blocking through Y=10.7 and overhead-decoration exclusion at
  Y=11.3. Six production `ActorMotion.step` cases cover front/closed-entry blocking, rear blocking
  and a clear X=3 m bypass in both AUTHORITY and REPLAY modes, 120 ticks each, capsule r=.35/h=1.8.
  Stops Z=-2.416668 / +2.416668 m; bypass ends Z=6.000001 m. Maximum mode difference .000129457 m,
  under .001 m. This is local shared-rule coverage, **not a multiplayer transport test**.
- Final canonical production checks **PASS**: 203 script compilations plus formatting/lint,
  17 Python tests, 149 GUT tests / 6,768 assertions and the expected-negative diagnostic test.

`manifest.json` indexes SHA-256 and byte count for every final owned payload except itself.
`final.log` is the one concise retained command/diagnostic summary; large logs and failed attempts
remain outside the repository under `C:/tmp/ft/assets/d01_lighthouse_01/`.

## Exact reproduction commands

Run in Git Bash from the repository root. Python/Pillow are required by the manifest step.
All Blender and Godot invocations are bounded and isolated; do not contact live MCP sessions.

```sh
NID=d01_lighthouse_01
B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
G="$(mise which godot)"
D="$(mise which gdstyle)"
T="C:/tmp/ft/assets/$NID"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONUTF8=1
mkdir -p "$T" "docs/assets/production/$NID-evidence"

timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/export.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/export.py" -- "$T/reexport.glb"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/validate.py" -- "$T/reexport.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --editor --path . --script "res://tools/asset_production/$NID/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "res://tools/asset_production/$NID/check.gd"
timeout 30 "$D" check "tools/asset_production/$NID/check.gd"
timeout 30 "$D" fmt --check "tools/asset_production/$NID/check.gd"
# Must be a fresh, empty external output directory; use a new suffix on later runs.
timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$D" --output "$T/checks-reproduction"
timeout 300 "$G" --headless --path . --import
python "tools/asset_production/$NID/manifest.py" "$T/checks-reproduction"
```

Fresh `.blend` recreation may carry a new save timestamp; the strict byte comparison is the
re-export of the saved source, not the Blender container or stochastic studio image bytes.
Final shipped suite output is `checks-final`. The literal requested first production-check command
failed on the Windows shim/default cp1252 engine-version read; using absolute mise binaries and
`PYTHONUTF8=1` fixes that environment problem. An intermediate suite found CRLF-only formatting
in the new check script; pinned formatting corrected it and the complete suite then passed.
An early GLB triangle-normal assertion found cornice end-cap normal bleed: the source now uses
flat radial end caps and non-weighted radial surfaces, and every actual binary triangle passes.

Import logs contain the installed toolkit's Godot 4.8-versus-tested-4.7 warning. The headless
editor normalization assertions pass and exit 0, but that editor shutdown emitted scan-abort and
RID/ObjectDB leak diagnostics; it is not claimed diagnostic-clean. Final ordinary headless import
has only the toolkit version warning; final standalone model/physics validation is error/warning
free. No unrelated engine/plugin code was modified or broad errors suppressed.

## Remaining acceptance

- Independent exact-commit source/technical/art review is pending; self-inspection is not acceptance.
- World integrator: fit the actual coastal plot without changing the coastline/roads, maintain the
  boardwalk and landward approach, compare university/sports/lighthouse landmark hierarchy.
- Gameplay/art reviewers: actual Godot camera views at centre and edges, off-centre recognition,
  actor/target occlusion, boardwalk approach/clearance and car driving/turning/contact checks.
- Multiplayer owner: real-process authority/prediction/transport checks around placed collision.
- Device/performance owner: import LOD silhouettes, GPU/draw cost, packaged builds and sustained
  Deck LCD/OLED gameplay. No world placement, performance, dynamic light or production-readiness
  budget is accepted by the isolated renders or local physics checks.
