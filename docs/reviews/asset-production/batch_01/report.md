# Six-asset independent source/export review

**Verdict: pending a small source-calibration evidence gap; no P1/P2 source or export defect found.**
The delivered geometry, source/export freshness, material interfaces, retained payload
and broad visual treatment pass the bounded checks below. Five assets lack the retained
one-metre comparison required by the asset workflow. The wall light includes a reference.
This is a production **source/export-stage** review. No asset is declared READY, and no
final engine, gameplay, device, performance or world-placement gate is accepted here.

- Candidate: `390377dc6530e101eddcbf38b2946a1b235137c7`.
- Original base: `66400c26a01bf917dfe631af4762c2b444d9c48f`; verified ancestor.
- Branch: `art/register-production-20261009`.
- Workspace: `/home/regner/.paseo/worktrees/0u71f39f/asset-register-production`,
  `wks_59891ad7a05813e5`.
- Reviewer: independent clean-context Codex / GPT-6.1 Sol high, 9 October 2026.
- Producers: separately commissioned source specialists identified in each handoff.
  ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2` owns coordination;
  `150f00b5-9e62-44d8-b0aa-a456d2a88b8c` owns engine integration.
- Scope: exactly `city_lights.01`, `.02`, `.04`, `city_sign_supports.01`,
  `city_planting.01`, `.02`, their normalized-ID sources/outputs/tools/reports/evidence,
  batch source readback and rectangular-planter retention manifest.

## Observed defects

No blocking or substantive geometry/export/material/UV defect was established.
There is no observed scale mismatch, stale GLB, unresolved external art dependency,
degenerate export triangle, nonmanifold source edge or failed fresh export in this scope.
This statement has the coverage limits below; it is not exhaustive topology or runtime proof.

The normal-direction diagnostic deserves an explicit disposition. Both pedestrian-light
GLBs contain 144 corner occurrences on 96 `lantern_neck_mesh` triangles whose shading
normal opposes the triangle normal (minimum dot approximately -0.774). Saved-source
polygons 144–191 form the top flare at Blender Z=2.64–2.67 m. The follow-up locates every
affected triangle centroid inside `lower_shield`; the documented shield profile envelops
that flare. The exposed neck in the producer detail and fresh source render has no
established inversion. This is a buried smooth-normal artifact, **not an observed visible
asset failure**. It does not justify rejecting this intact assembly. If that component is
later exposed or reused separately, recheck its cap/side smoothing. Winding itself is
consistent and source volumes are positive. See `independent-interface-check.json` and
`independent-glb-check.json` for the raw measurements.

## Missing evidence and disposition

### G1 — P3: retained one-metre source comparison is absent for five assets

**Locations:**
`art/source/models/environment/city_lights_01/city_lights_01.blend`,
`city_lights_02/city_lights_02.blend`,
`city_sign_supports_01/city_sign_supports_01.blend`,
`city_planting_01/city_planting_01.blend`,
`city_planting_02/city_planting_02.blend`, and their scoped evidence directories.

**Contract:** `docs/assets.md:157`: “Use metres: Blender unit system Metric, unit scale 1,
with a 1 m measurement fixture.” The art-review scale lens also calls for comparison
with a dimensional reference rather than visual plausibility alone.

**Evidence:** full source-object inventories contain no dimensional fixture in these five
sources, their authoring scripts create none, and the supplied previews/check records do
not provide a comparison of these models with a one-metre fixture. All five nevertheless
have Metric/scale_length=1, unit export-root/static scale and measured source/export bounds
matching their records. This is **missing calibration evidence**, not a discovered wrong
unit or a demand to add runtime geometry. `city_lights_04` has an excluded
`reference_one_metre` CUBE empty with display size 0.5 and unit scale (one-metre span), so
it is outside this gap. Empty `dimensions=(0,0,0)` does not invalidate its display size.

**Impact:** formal unit-reference coverage for those five source handoffs is incomplete;
no demonstrated gameplay or visual impact. Their numeric bounds and source freshness pass.

**Smallest closure / owner:** source handoff owner, coordinated by ROOT/integrator, retains
one bounded isolated comparison placing the unchanged models beside a verified one-metre
reference with recorded tool version, source hashes and identity placement. A shared
comparison may cover all five; this review does not impose a new rule that a reference
must be embedded in each production `.blend`. Alternatively, the source owner can include
an excluded authoring reference in the next authorized source revision. Do not change
live editor or frozen sources just to service this review.

**Retest:** same reviewer inspects exact follow-up evidence/source identity, fixture size,
axis/placement and measured bounds. If sources change, refresh source manifests and
reexport all variants; verify unaffected GLB bytes and recheck affected ancestry at the
final exact engine candidate. Keep source-unit calibration pending until that receipt.

### G2 — provenance boundary, explicitly assessed; no substantive hash gap

`city_planting.01` has **no producer-supplied manifest**. The supplied
`docs/assets/production/batch_01-evidence/city_planting_01-retention-manifest.json`
is explicitly an **integrator** readback of the report-declared 23-file set. Independent
inspection verifies that exact set, every byte count/hash and the readback manifest hash.
This establishes retained immutable-candidate identity, not a retrospectively supplied
producer manifest or an independently certified original authorship timestamp. The saved
source also freshly reproduces its GLB byte-for-byte. With those corroborating facts,
there is no outstanding substantive source/export provenance mismatch at this candidate.
Preserve the distinction in downstream reports; no fabricated producer receipt is needed.

`city_lights.02` has 20 manifest-covered producer files plus two expressly integrator-owned
GLB `.import` sidecars. Those two are outside the producer set rather than missing
producer deliverables. Their candidate hashes are retained in
`candidate-scope-file-index.json`; their engine identity/settings validation remains pending.
The .01 manifest includes two observed importer sidecars; inclusion proves retained bytes,
not that the source specialist authored the imports.

## Independent checks and results

All inspection reads used an exact-candidate `git archive` scratch snapshot at
`/tmp/six-asset-review-390377d`. Fresh export jobs used separate copies at
`/tmp/six-review-jobs/<id>`. No authoring regeneration ran. The shared implementation,
index, source files, docs, live Blender/Godot and private integrator endpoint were not
mutated. Review writes are exclusively in this directory; no commits or subagents.
An initial read of the working scene contract was subsequently verified byte-for-byte
against candidate SHA256 `cec8e72f7be1d5d77a82f5a7910b3f67d10cf43efa278067427ab47057f8c9ff`.
The active shrub and uncommitted integration outputs were excluded.

**Pinned process:** fresh `/usr/bin/blender`, 5.2.2 LTS, build `d13f752e3b9c`, bundled
glTF 5.2.40, verified independently in process. Factory startup, bounded private CLI jobs,
process-local `ALSOFT_DRIVERS=null`, `SDL_AUDIODRIVER=dummy`, scratch cache; no connector.
The source inspected is opened from the saved `.blend`, never regenerated from author.py.

| Check | Actual outcome / retained evidence |
| --- | --- |
| Candidate/base and scoped changes | Base ancestor exit 0; 180 scoped candidate files indexed; exact diff, identity and archive route in `review-identity.json`, `scoped-changed-paths.stdout.log`, `candidate-scope-file-index.json` |
| Complete expected sets and readback | All 171 declared retained files exist with matching bytes/SHA256; six readback manifest hashes and counts match; only the two documented .02 importer sidecars lie outside a producer set; `independent-manifest-check.json` |
| Saved Blender sources | Six sources inspected independently, Metric/scale 1, named `export_<normalized_id>` collections and recorded roots, exact member hierarchies; all 35 mesh objects closed/consistent, positive volumes, finite positions, no loose vertices/edges or degenerate source triangles, unit finite corner normals; `independent-source-inspection.json` |
| Saved-source freshness | Six fresh export commands exit 0; all nine delivered GLBs reproduced byte-for-byte; `fresh-export-comparison.json` and per-ID `*-reexport.stdout.log` / `.stderr.log` |
| Export payload | Independent JSON/binary accessor decoding of all nine GLBs: finite coordinates/unit normals, no degenerate triangles, stable material names, declared meshes/roots, no cameras/lights/images/textures/skins/animations or compression extensions; `independent-glb-check.json` |
| Axes and bounds | Independent decoded vertex bounds with hierarchy translations match every declared model-space AABB within 0.001 m; max float deviation about 1.91e-7 m; all node scales/rotations identity; `independent-model-bounds.json` |
| Sign artwork interface | Carrier front only uses `sign_face` slot 0, rear/sides slot 1 `mount_metal`; outward +Y source face at Y=0.088 m; decoded UV0 orientation fits contract with max error 2.91e-8; upright TL/TR/BL/BR image inspected; source/GLB/interface JSONs |
| Planter interfaces | Round narrowest inscribed opening measured 1.238506 m diameter, 19.253 mm radial margin for radius 0.60 root; rectangular soil top Y=0.400000006 m; `independent-interface-check.json` |
| Preview inspection | Candidate studio hero/detail/UV/downward images and four district references inspected; six fresh source renders exit 0, with visual limitations stated below; `fresh-preview-settings.json`, `*-fresh-source.png` |
| Original diagnostics | All 41 scoped top-level producer text logs read; classified index `producer-diagnostic-index.json`; original raw logs remain immutable candidate evidence |
| Initial ancestry | Four candidate light01/02 wrappers reference explicit GLB PackedScenes at `Visuals/Model`, no embedded render meshes/editable imported children; static evidence only in `initial-ancestry-static.json` |

`commands.json` retains every substantive independent check argv, cwd, process-local
environment, exit and elapsed time. Every named job has raw stdout and stderr files,
including empty streams. Read-only preflight argv/exits are also in `review-identity.json`.

There were two reviewer tooling failures, neither an asset failure: the runner first
reached the payload job before its script existed (exit 2); the first executed parser
then assumed a wrapped manifest rather than the actual list/path-keyed schemas (exit 1).
One bounded code adaptation supports the inspected schemas and completed the check (exit 0).
Both original stderr streams remain retained. No unchanged failure was repeatedly retried.
Do not report those initial checks as successful.

The initial payload JSON intentionally records **raw mesh-local** coordinate bounds;
for the .02 service-cover mesh these extend below zero before its documented node
translation is applied. Use `independent-model-bounds.json` for true model-space bounds;
there is no exported ground penetration. This distinction is not a producer defect.

## Per-asset source/spec assessment

Dimensions below are authored production refinements with declared tolerances, not
measurements inferred from concept pixels and not gameplay-approved envelopes.

| Asset | Godot model-space min → max, metres | Triangles per output / surfaces | Source/export disposition |
| --- | --- | --- | --- |
| city_lights.01 | (-0.36, 0, -1.40) → (0.36, 6.20, 0.21) | 2,424 / 4; warm and cool | Geometry/material/export accepted; unit-reference receipt pending G1 |
| city_lights.02 | (-0.36, 0, -0.36) → (0.36, 3.00, 0.36) | 3,616 / 8; warm and cool | Geometry/material/export accepted; unit-reference receipt pending G1 |
| city_lights.04 | (-0.32, -0.23, -0.71) → (0.32, 0.305, 0) | 4,388 / 9; warm and cool | Accepted for bounded production source/export stage |
| city_sign_supports.01 | (-0.70, -0.50, -0.10) → (0.70, 0.50, 0) | 2,720 / 13 | Geometry/material/UV/export accepted; unit-reference receipt pending G1 |
| city_planting.01 | (-1.20, 0, -0.45) → (1.20, 0.60, 0.45) | 1,428 / 4 | Geometry/material/export accepted; unit-reference receipt pending G1 |
| city_planting.02 | (-0.90, 0, -0.90) → (0.90, 0.48, 0.90) | 3,456 / 3 | Geometry/material/export accepted; unit-reference receipt pending G1 |

Both standing lights have ground-centred foot/root origins. The ordinary pole's
asymmetric 1.40 m forward overhang is documented rather than mistakenly recentered.
The .02 service cover retains an intentional translation, with static rotation/scale
applied; the contract does not forbid documented component offsets. Wall light and panel
use documented wall-attachment-plane exceptions: root centred on rear contact plane,
all geometry projecting toward Godot -Z. Planters are ground-centred and symmetric.
All forward/up mappings match Blender +Y/+Z → Godot -Z/+Y without corrective scale/rotation.

Named export collections exclude studio floors/wall, cameras, lights and the .04
reference. Static modifiers are already applied. Runtime geometry remains linked to
editable Blender geometry rather than copied/generated engine meshes. Sources have no
linked libraries or external texture dependencies; only Blender viewer/render images
are present. `art/source/.gdignore` and production evidence `.gdignore` are committed empty
files. No naming suffix implies automatic collision import.

Flat opaque embedded metallic/roughness materials are appropriate to these untextured
props. Lamps retain declared warm/cool lens assignments and modest appearance-only
emission; no real light or shadow budget is proven or exported. Source PBR names/slots
match outputs. Planters share sage/pale rim/petrol foot language. Sign artwork remains
separate: a neutral replaceable face, correct image orientation and 61:41 aspect;
no district copy, texture or logo is baked into support geometry. No external runtime
material/texture is falsely promised, and no alpha/normal-map/channel interface is needed
for this delivery. Final Godot remap, filtering/culling and bloom are integration checks.

The rectangular soil's maximum mid-profile footprint is 2.015×0.515 m at source Z=0.39;
its **top** is correctly 2.01×0.51 m at Z=0.40 as documented. This is not an interface
mismatch. Safe planting rectangles/radii are assembly constraints, not tested gameplay
collision or compatibility with the excluded unfinished shrub/tree.

Sources/reports state original commissioned Blender construction. Editable sources,
construction recipes and absence of external models/images/libraries corroborate that
rights trail. Existing project district images are style references, not incorporated
third-party artwork. The diagnostic PNG is original disposable test artwork. No unknown
licensed font/model/texture dependency was found; this is a scoped provenance assessment,
not an independent legal certification of authorship.

## Visual judgment and limits

References inspected: accepted Petrol & Coral direction, Crescents v02, Signal Row v03,
Old Quay v03 and Glassward v01, corresponding identities/briefs and relevant asset
breakdowns. The immutable commission was read in full and overrides historical
concept-only restrictions. It does not turn illustrative district images into scale or
runtime acceptance evidence. Detailed prop dimensions remain declared refinements.

- Ordinary pole: quiet tapered shaft, broad rounded head, recessed lens and restrained
  hatch/foot. The manufactured arm seam is visible but does not conflict with broad smooth
  forms. The source underside view preserves lamp/lens separation.
- Pedestrian light: a distinct shorter radial cap/diffuser/shield silhouette, continuous
  broad lens and quiet pole. Fresh source head render matches the supplied design.
- Wall light: coherent cap/lens/shield family, smooth curved support and wall backplate.
  Supplied underside detail encloses the corrected bracket terminal; no exposed cap fault
  was established. Warm/cool lens color is localized rather than luminous hardware everywhere.
- Sign panel: simple smooth petrol frame, generous separate face and quiet mount hardware.
  The diagnostic reads upright and unmirrored. It supports district artwork replacement
  without duplicated geometry. Its face is strongly foreshortened in the source downward
  view; the record appropriately makes no mandatory gameplay-wayfinding readability claim.
- Rectangular and round planters: broad pale rims, quiet sage walls and recessed petrol
  feet form a coherent family. The trough retains a recessed soil insert; the round
  surround remains visibly open through its centre. No dense foliage/noisy textures were added.

No contract-based broad silhouette/palette discrepancy was found in those inspected views.
This accepts source form within this coverage, not arbitrary studio colors as calibrated
Petrol & Coral engine appearance. Placement density and actor contrast remain downstream.

Fresh review renders use 800×600/16-sample Cycles studio conditions. Four are useful new
views (.02 head, sign, both planters). The .01 render crops the top/foot because this
review changed aspect without reframing its saved camera; its full candidate hero and
underside were inspected instead. The .04 saved studio camera is intentionally saved at
the origin before author.py supplies render-specific camera poses; the review's generic
saved-camera render is black. That render is **not usable visual evidence and not an
asset defect**. Candidate hero/underside/scale previews and their explicit author.py camera
poses were inspected. These limitations are retained rather than concealed by repeated
render attempts. No fresh image is represented as native gameplay or engine proof.

The source 1280×800/47 m/42° downward references show small quiet lamp footprints and
clear planter rims at their illustrative scale. No actor/district or actual native
window accompanies those source views. The candidate's initial engine light capture
shows a central actor and four light heads with long shadows, while warm/cool differences
are subtle overhead. This is supplied **initial** integration evidence for .01/.02 only;
it cannot accept the six-asset final engine batch or motion/aim/occlusion.

## Handoff gates and required follow-up

| Gate/lens | Disposition and owner |
| --- | --- |
| Production authorization / direction | Accepted scope: immutable production commission supersedes draft concept-only wording; broad form/style follows accepted family direction |
| Source identity, complete retained set, rights trail | Accepted at exact candidate with explicit G2 integrator/producer distinction |
| Units / source reference | Pending G1 for five; wall-light reference accepted; numerical units, pivots, axes and bounds pass for all |
| Production model topology/material/UV/export freshness | Accepted within independent coverage; hidden neck shading observation recorded, no substantive failure established |
| Source visual form | Accepted within inspected studio/reference coverage; no actual camera/native/device acceptance implied |
| Rigs, animation, gameplay sockets, damage states | Not applicable: static intact ordinary props; no moving/attachment gameplay requested; wall anchors/planting interfaces documented |
| Textures/normal maps/alpha | Not applicable to flat-color runtime delivery; sign UV0 remains applicable and passes; external artwork future-owner gate |
| Explicit source LOD | Not required until measured need; triangle/surface counts are observations, not budgets or a performance pass |
| Godot import/material/normals/AABB/UID and dependencies | Pending exact final engine candidate, integrator; initial .01/.02 ancestry only. Existing UID warnings are an explicitly retained integration condition, not a source defect |
| Linked prefab/inherited save/reopen and identities | Pending final batch integration/review; current four initial wrappers are statically linked, not independently roundtripped in this review |
| Collision/movement/query/network | Pending integrator/gameplay reviewer if intentional collision is introduced; validate pole/base envelopes and round-surround opening through production movement/query APIs and affected separate-process checks |
| Native runtime camera / target/actor readability | Pending integrated 1280×800 vertical perspective fixed-yaw captures with recorded engine/render/lighting/camera and motion/aim states |
| Placement/route/derived-data | Pending world integrator; preserve selected district polygons, road ownership, saved transforms/IDs and refresh only affected derived data |
| Performance/device/exported platform | Pending measured repetition/load/cost on named desktop hardware and later applicable Deck LCD/OLED/native/Gaming Mode targets; no invented polygon, light, texture or draw-call budget |

The integrator's concurrent work and final candidate were deliberately not reviewed.
When resumed, this reviewer needs the exact final commit/base, actual changed delta,
new engine receipts and G1 evidence. Reassess source changes and their complete export
sets, then imported material/normal/axes/UIDs, saved ancestry/identity roundtrips and
bounded camera/collision checks appropriate to that delta. Full world/device/load proof
continues with its own owners. This report does not close a TODO or authorize placement.

## Evidence index

- `review-identity.json`, `candidate-scope-file-index.json`, `scoped-changed-paths.*.log`:
  exact candidate/base, archive provenance, all scoped candidate hashes and diff.
- `commands.json`, named `*.stdout.log` / `*.stderr.log`: check argv/exits/raw diagnostics.
- `independent-source-inspection.json`, `independent-glb-check.json`,
  `independent-model-bounds.json`, `independent-interface-check.json`: independent data.
- `independent-manifest-check.json`, `fresh-export-comparison.json`: complete retained set,
  byte/hash coverage and nine fresh exact reexports.
- `initial-ancestry-static.json`: four immutable initial saved light wrappers.
- `producer-diagnostic-index.json`: index of original scoped producer diagnostics;
  unaltered raw originals are available under the exact candidate paths it names.
- `fresh-preview-settings.json`, six `*-fresh-source.png`: fresh render results,
  including two explicitly inadequate views; no errors hidden.
- `run_checks.py`, `inspect_sources.py`, `inspect_payload.py`, `inspect_interfaces.py`,
  `inspect_world_bounds.py`, `render_sources.py`, `preflight.py`: review-only check sources.
- `artifact-index.json`: complete review artifact paths/bytes/SHA256, excluding its own hash.

All reviewer substantive successful jobs exited 0. Fresh exporter stdout retains the
optional MeshOptimizer-library diagnostic; the GLBs have no meshopt/compression extension,
reproduce byte-for-byte and decode successfully. This is an environment capability
notice, not a suppressed or unreported asset failure. Historical source failures,
audio-teardown exits (including .02 exit 130), thumbnail-cache errors, Blender 6.0
deprecations and producer checker/preview adaptation logs remain raw retained evidence.
They are not malformed production code and were not rejected merely for retention.
