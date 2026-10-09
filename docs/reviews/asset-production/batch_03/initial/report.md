# Batch03 independent source/export review — 9 October 2026

**Scoped verdict: rejected for correction of F1 (P2) and F2 (P3).** Five records
have no observed source/export defect with the coverage below. This is an independent
review of production source candidates, not production READY, engine import approval,
prefab/world acceptance or completion of a TODO. No implementation was changed.

## Findings

### F1 — P2: fascia exports all five materials double-sided despite its single-sided contract

**Location:** `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`,
materials `fascia_slate_petrol`, `fascia_warm_trim`, `fascia_recess`,
`fascia_artwork_face`, `fascia_mount_metal`; the corresponding GLB `materials[*].doubleSided`.
Reproduction owner code: `tools/asset_production/city_shop_fittings_02/author.py:21`.
Declared contract: `docs/assets/production/city_shop_fittings_02.md:83` and its
material-scope validation claim at line 108; `docs/assets.md` requires explicit
material scope and source/output agreement.

**Observed:** all five saved source materials have `use_backface_culling=false`;
all five actual GLB material records contain `"doubleSided": true`. This is also
present in the independently reopened, byte-identical fresh export. The producer's
successful material validation did not catch this mismatch. Other eight outputs
have opaque, single-sided materials as declared.

**Evidence:** `scratch-audit.json` → `sources.city_shop_fittings_02.materials`;
`glb-audit.json` → `city_shop_fittings_02.materials`; `glb.stdout/.stderr` (exit 1);
`city_shop_fittings_02.source.json` (fresh export hash and byte equality). No inference
about measured render cost or actual Godot appearance is made. The delivered
culling behavior differs from the integration/material contract; later material
remaps must not silently conceal an incorrect source setting.

**Minimal fix / owner:** the existing `.02` source worker should explicitly enable
backface culling for these five materials in the authoring helper and saved source,
save and reexport the one GLB, and make its raw material check assert this property.
Keep geometry, UVs, material names and slots unchanged. Update affected receipts,
manifest and exact candidate. Recheck actual source flags, raw GLB flags, byte-identical
saved-source export, UV contract and the unchanged shell scratch correspondence.
Return the exact changed candidate to this same reviewer. Do not fix only a future
Godot material or rewrite the declaration to hide the unintended setting.

### F2 — P3: lower inner door-ring bevel has a small pinched shading crease

**Location:** `.06` source meshes `single_leaf_1_stiles_rails`,
`double_leaf_1_stiles_rails`, `double_leaf_2_stiles_rails`, at the lower inner
glazing corners, on front and rear. Authoring treatment:
`tools/asset_production/city_shop_fittings_06/author.py:28–32`.

**Contract:** accepted smooth forms/continuous shading and the handoff's broad
manufactured bevel highlights. This is a local shading issue, not inverted geometry,
failed mating, nonmanifold topology or a proven gameplay readability fault.

**Observed:** eight small triangles per leaf have one or two shading corner normals
on the opposite side of the geometric triangle's hemisphere. Worst raw GLB dot is
about -0.25357. All normals remain finite/unit and each triangle's mean normal points
outward (minimum mean dot approximately +0.22797). Source edges are manifold and
consistently wound, connected volumes are positive, and no degenerate triangles
were found. Consequently the producer's *mean*-normal test at
`tools/asset_production/city_shop_fittings_06/check_glb.py:42–43` passes. Fresh
unaltered-source close renders expose the small pointed/pinched highlight at the
bottom corner; it is most apparent in the front view. The affected example triangle
area is about 0.000000787 m². This is deliberately minor: the close images magnify a
35 mm region to 800 pixels, and the normal-scale fitted frontage does not expose
this detail.

**Evidence:** `city_shop_fittings_06.source.json` records source triangle indices
106,117,130,141,298,309,322,333 for each ring; `glb-audit.json` records actual exported
positions, normals, areas and corner dots for each output; `door_front_inner_bevel.png`,
`door_rear_inner_bevel.png`, `render-readback.json` record fresh actual-source images
and cameras. The `.06` source audit exits 1 on these corner normals, making the
batch wrapper exit 1; no unrelated source topology failure is implied.

**Minimal fix / owner:** the existing `.06` source worker should correct the local
bevel corner shading/custom normals, or locally adjust the bevel corner triangulation
if needed, while preserving the leaf/body/handle bounds, mating datum and material
slots. Save and reexport both variants; compare the front/rear lower corners under
the retained close cameras and check raw corner normals, fresh export equality and
both `.03` mating assemblies. Refresh retained scratch assemblies only as evidence,
without changing `.03` or embedding fittings in the shell. No added geometry detail,
opening mechanic or new asset is requested.

## Exact scope, revisions and authority

Candidate **`028775618c4493ca672646e6e37fdc3c83e0e313`**; immediate parent / review
delta base **`10ddb64d16e6cb2f137923a31d3ca14991468f7d`**; original commission base
**`66400c26a01bf917dfe631af4762c2b444d9c48f`**. The candidate's actual first parent and
original-base ancestry were independently verified. Working HEAD matched the
candidate at freeze. Workspace: `/home/regner/.paseo/worktrees/0u71f39f/asset-register-production`,
branch supplied as `art/register-production-20261009`, workspace `wks_59891ad7a05813e5`.
ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2` owns coordination; integrator
`150f00b5-9e62-44d8-b0aa-a456d2a88b8c` owns Git and later engine integration.

Exactly seven IDs: `city_shop_fittings.02/.03/.05/.06/.07/.08` and
`city_small_shop_shells.01`. Their 465 frozen files equal the union of the seven
producer payload sets plus their seven manifests. Parent→candidate has **466 added
paths**: those 465 and `docs/assets/production/batch_03-evidence/source-readback.json`.
The complete original-base delta is retained for identity (1,736 paths), but other
batches/stages are excluded from this verdict. No baseline-wide acceptance is implied.

Reviewed from Git blob bytes and verified matching working bytes. Current source
buffers and two retained scratch assemblies were copied to `/tmp/batch03-independent`
without recopying historical packs. All historical expected files were hashed
directly from Git and compared with existing working files. `.01` canopy source/export
was read only as the immutable interface used by the existing shell assembly; it is
not an eighth reviewed ID. Seven untracked importer-owned `.import` sidecars are
explicitly excluded. Their existence does not establish import freshness or identity.

The raw commission, repository instructions, art-review skill, orchestration reviewer
contract, asset/art-direction/world-layout/scene contracts, S01 route, shared fitting
and shell briefs, district common contract, Signal Row v03/B05/F01–F06, Crescents v02,
Old Quay v03, Broadlot and graphics/parade interfaces were consulted. Historical
concept-only restrictions are superseded by the explicit immutable commission;
appearance/ownership constraints still apply. No new-ID dispatch, world/device
expansion, subagent, Git/index edit, shared-doc edit, source edit or live/private
editor endpoint was used. Sources were inspected only through isolated scratch
Blender CLI processes. The supplied model receipt is Codex/GPT-6.1-Sol high in
auto-review; no model change or new launch occurred.

## Independent coverage and record dispositions

`accepted` below means **bounded production-candidate source/export technical and
source-view review**, not import/prefab/placement/READY. Numerical dimensions are
reversible design choices from the handoffs, not an invented code/accessibility,
polygon/device or movement budget.

| Record | Source/export disposition | Measured output and applicable evidence |
| --- | --- | --- |
| `.02` fascia | rejected, F1 | 7 meshes, 1,656 triangles; 3.200×0.800×0.140 m; wall-plane centre pivot; one artwork face; fresh exact export; UV accepted independently of culling defect |
| `.03` surround | accepted | single/double each 4 meshes and 2,312 triangles; 1.540/2.340×2.480×0.630 m; one recess/reveal/casing/stop/threshold assembly per variant; both actual `.06` fits |
| `.05` display bay | accepted | 8 meshes, 1,368 triangles; 3.200×2.000×0.400 m; actual sleeve and shell hole/void fit; two opaque panes, no detailed interior |
| `.06` leaves | rejected for minor F2 rework | single 3 meshes/1,512 triangles; double 6 meshes/3,024; single/pair widths 1.024/1.824 m; height 2.202, total depth .123 m; no competing fixed frame; both mating variants pass |
| `.07` upper window | accepted | 11 meshes, 1,760 triangles; 4.800×1.600×.310 m; broad three-light rhythm; actual rear insertion geometry fits declared standalone opening envelope |
| `.08` blade sign | accepted | 16 meshes, 3,624 triangles; .200×1.160×.880 m; two separate side artwork slots, seating and bracket form consistent with the original elevation concept |
| shell `.01` | accepted | 30 meshes, 4,516 triangles, 8 markers; structure 6.400×14.000 m, complete visual bounds 6.400×5.050×14.340 m; true two-hole wall, distinct deep roof, unchanged mounted source copies |

All seven saved sources independently verify Blender **5.2.2 LTS / d13f752e3b9c**,
bundled glTF **5.2.40**, Metric/unit scale 1 and an excluded measured 1×1×1 m
source reference. Identity static mesh/root transforms and recorded mount-marker
translations agree with the pivot contracts. glTF maps source `(X,Y,Z)` to
`(X,Z,-Y)`, giving project +Y up/-Z facade front without corrective scale/rotation.
Literal per-output bounds match the stated handoffs to floating-point precision.
Source component volumes are positive, mesh edges closed/consistently wound, no
unused vertices, nonfinite geometry or degenerate triangles. Normals are finite/unit;
raw triangle mean-normal orientation is outward in all outputs, with the local
corner-normal exception F2. The mesh/marker member sets, variant filtering and one
identity output root match the saved sources. Reference cube/studio objects are absent
from exports. All **nine fresh saved-source GLBs are byte-identical** to the candidate;
the reexports are retained in this directory.

Saved sources have no external linked libraries or production image/packed-image
dependency. Startup materials and internal viewer handles are not exported. Raw GLBs
contain no images/textures, rigs, animations, studios/cameras or compression/extensions.
Source authorship scripts construct editable original geometry in Blender; inspected
source objects and retained provenance support the declared original authorship.
This is artifact/provenance-chain review, not an independent historical authorship
attestation. The source subtree's committed `.gdignore` is present and empty.

### Entrance and shell interfaces

The independent BVH probes use actual saved meshes and independently imported GLBs;
they do not call producer checks. Both modes measure `.03` apertures **1.040/1.840 m**,
head **2.240 m**, sill **.020 m**, side/head gaps **.008 m**, sill gap **.010 m**,
rear stop gap **.006 m** and double meeting gap **.008 m**. Nine depth/height side
samples per variant agree. No `.06` mesh intersects a `.03` mesh. There is one
entrance owner for fixed surround/stop/threshold, with leaf stiles/rails and static
pulls belonging to `.06`. No working opening mechanics are added.

Shell wall apertures actually measure entrance X `[1.240,2.660]`, height `[0,2.450]`,
and window X `[-2.470,.570]`, height `[.540,2.420]`. **323 independent rays per aperture
in each mode** encounter no wall or other shell obstruction through the required
rear voids (entrance Y=6.460, window Y=6.800 in Blender). `.05` and `.07` actual
behind-wall geometry has .020 m jamb/head/bottom/rear insertion gaps in their local
opening envelopes. Both `.05` panes are opaque; no shell back panel or detailed
interior blocks the display opening.

All eight shell marker names and world translations agree between source, raw GLB
and independent imported geometry. Actual mounts place the unchanged single entrance,
door, display bay, canopy reference and fascia at the shared wall plane. No unexpected
fitting/shell triangle intersections occur; only documented flush canopy/fascia wall
contacts are permitted. Window→canopy gap is approximately .100 m, canopy→fascia .160 m.
Nine roof-deck patch probes hit Z=4.300 m. Shell meshes remain within the structural
X pitch ±3.200 m and contain no duplicate leaf, glazing, casing, canopy or fascia.
This is static geometry/interface evidence, not actor clearance, join appearance,
weather seal or actual gameplay collision.

The retained mounted shell scratch has **56 matching current-source mesh signatures**;
the fitted `.03/.06` scratch has **17**. Signatures cover vertices, polygon membership,
material assignments, smooth flags, corner normals and UVs/material parameters. No
fitting mesh/material data was changed to make the source assembly fit. Source GLBs,
scratch source data and visual mounting remain distinct artifacts. The shell game
export has no embedded fittings, source dependency or runtime hierarchy writer.

### Signed artwork-interface review

**Signed PASS, `.02` geometry/UV0/artwork ownership:** actual front has 28 vertices,
26 triangles, full `[0,1]²` UV bounds; plane source Y=.128 / GLB Z=-.128. Source U
increases toward -X and V toward +Z, so outward viewers see left-to-right/upright
artwork. glTF V is image-down. Only `fascia_artwork_carrier` slot 0
`fascia_artwork_face` is the graphics interface; slot 1 retains back/side mount metal.
The current diagnostic TL/TR/BL/BR and arrows were visually inspected. This sign-off
does not waive F1 or approve a later engine material remap.

**Signed PASS, `.08` BOTH outward faces:** `face_positive_x` plane X=+.067/normal +X
has source U increasing with +Y; `face_negative_x` plane X=-.067/normal -X has U
increasing with -Y. Both source V values increase with +Z. Raw binary checks cover
all 36 vertices/34 triangles per face: correct positions, outward normals, UV formulas,
full face range and consistently oriented UV determinants after glTF's V flip. The
same artwork is upright and unmirrored from both outward sides; the two original
diagnostic renders confirm readable text and arrows. Face slot 0 materials
`blade_artwork_positive_x` and `blade_artwork_negative_x` are separately replaceable;
slot 1 is `blade_mount_metal`. District graphics owners supply future artwork/remaps.
No copied artwork mesh or packed diagnostic/tenant texture enters either game source
or export. Runtime resolution/filtering/emission remains graphics/integrator-owned.

### Independent visual judgment and calibration

Inspected actual current producer source renders, original dimensioned blade elevation,
both UV views, source measurement views, fitted entrances, window rear/opening views,
and Signal Row v03/Crescents v02/Old Quay v03 original raster references. The retained
`original_metre_sheet.png` is a contact sheet of the seven current metre images,
ordered `.02,.03,.05,.06,.07,.08,shell.01`; it is not measured geometry or a replacement
for the original files. Source audit measurements verify the physical metre references.

Fascia and blade use broad blank fields/quiet trim; `.05` is two broad dark lights,
`.07` has a wider central light and no dense grid; `.03/.06` form one recessed entry.
The shell's 6.4×14 m footprint, long roof folds, higher front parapet and restrained
plum/slate surfaces agree with Signal Row B05's narrow/deep ordinary shell. It does
not imitate a district landmark or add upper accommodation/interiors. Sparse rear
drainage does not displace the roof silhouette. Original reference art informs shape
and hierarchy only: no raster-derived dimensional acceptance or calibrated colour
claim is made. F2 is the only new visible local source-shading concern.

Fresh reviewer renders reopen the frozen `.06` source and verified saved shell
assembly without saving them. `fresh_mounted_overview.png` confirms the mounted form;
`fresh_mounted_calibrated_top.png` is actual Blender Cycles CPU, 32 samples, four
threads, native 1280×800, vertical-down fixed yaw, height47 m, vertical FOV42°,
position `(0,12,47)` in Blender. It uses neutral studio lighting/AgX, not district
engine lighting. Camera settings and source paths are in `render-readback.json`;
the source renderer leaves Blender clipping defaults unchanged rather than proving
the target engine clipping envelope. The roof dominates; the recessed door and
window faces are occluded and the fascia/canopy are small near-edge forms. This
supports an explicitly limited source observation, not gameplay readability acceptance.

## Actual checks, exits, diagnostics and preservation

Every substantive check is retained with literal argv/cwd/process-local environment,
UTC start/elapsed time/exit in `*.command.json`, separate raw `*.stdout` and `*.stderr`,
including **empty streams**. `run_check.py` is the capture harness. Check sources
are retained here; production tools were read but not run against shared outputs.
Scratch Blender uses `ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy -b -noaudio -t 4`,
owned `/tmp` cache and `--python-exit-code 1`. No connector/live endpoint was called.

| Check / actual command source | Exit | Meaning |
| --- | ---: | --- |
| `freeze` → `verify_freeze.py` initial version | 1 | Own inventory format assumption: some manifests are lists, others objects |
| `freeze_adapted` → same checker, one retained adaptation | 0 | All465 paths/byte sizes/SHA256/working bytes and per-record exact sets pass |
| `pin` → `/usr/bin/blender --version` | 0 | Exact5.2.2 LTS/d13f752e3b9c |
| individual `*_source` → `source_audit.py` in seven separate CLI processes | 0 except `.06`=1 | All9 exact reexports completed; `.06` corner-normal exception retained |
| `source_batch` → `run_sources.py` | 1 | Propagates the `.06` source audit failure; not a missing export |
| `glb` → `glb_audit.py` | 1 | F1 raw material scope fails; all decoded results are still retained; F2 corners separately recorded |
| `interfaces` → `interface_audit.py` | 0 | Both source/GLB variants, rear insertion, actual shell holes/void/mounts/intersections |
| `saved_assemblies` → `scratch_audit.py` | 0 | 56+17 complete current-source scratch mesh matches |
| `fresh_renders` → `render_readback.py` | 0 | Four fresh actual-source images, no source save |
| `measurement_sheet` → literal ImageMagick montage argv | 0 | Contact sheet of existing original metre renders |
| `contract_reads` | 0 | Full retained local contract reads |
| `source_provenance` | 0 | Literal source authoring/provenance search |
| `consumers` → rg including nonexistent `resources/` | 2 | Read-only discovery path error, empty matches; preserved, no unchanged retry |
| `consumer_tracked` → exact-commit `git grep` in tracked scenes/scripts/tests | 1 | No matches, normal grep no-match status; no existing runtime consumer established |
| `final_preservation` → `final_preservation.py` | 0 | All465 working and copied frozen buffers remain unchanged; exact HEAD/branch retained; tracked working diff empty |

The single bounded checker adaptation accepts the two actual manifest container
formats; `verify_freeze_before_adaptation.py` retains the failing check source.
No failed probe was repeated unchanged. F1/F2 failures were investigated using
distinct raw/source/image evidence rather than suppressing assertions.

Raw export stdout includes the absent optional MeshOptimizer library diagnostic.
No compression was requested; independent decoding and exact bytes still pass.
BlenderMCP registration/unregistration is startup output from private CLI processes,
not a live API call. The fresh render stderr retains the `World.use_nodes` future
deprecation warning. These diagnostics are not new geometry failures or engine/device
proof. The exporter succeeds even though the conservative source normal audit later
fails for F2. Do not summarize this packet as "all checks pass."

`frozen-file-index.json` is the **complete actual465-file byte/SHA256 index**, with
expected values, Git values, working values, per-record missing/extra results,
manifest hashes and exact parent/original-base deltas. `reference-file-index.json`
records the two immutable `.01` inputs. `context-file-index.json` records the readback,
contracts and inspected original PNGs. `review-file-index.json` hashes this review
packet (excluding itself). No historical producer evidence pack was recopied.

## Pending applicable gates and smallest next owners/checks

| Gate | Status / smallest bounded next action |
| --- | --- |
| `.02/.06` source corrections | Existing source workers correct F1/F2; integrator freezes the exact changed source delta; same reviewer dispositions it |
| Engine import, metadata/UIDs and dependencies | pending; integrator imports all9 outputs in the pinned owned Batch03 stage, preserves/commits engine-generated sidecars and inspects actual imported bounds, markers, slots/culling and dependencies |
| Linked prefab, socket adapter and inherited save/reopen | pending; integrator saves linked wrappers with identity model transforms and source-derived marker mappings, then compares base/inherited saved identities and reload results |
| Actual `.07/.08` shell mounting | pending; integrator checks the already-completed compatible shell/facade and actual declared hole or blade fitting envelope; retain pending if no compatible completed shell is available; no new-ID dispatch is requested |
| Actual engine camera, fixed district lighting/materials and occlusion | pending; owning art/engine stage captures final imports from native vertical47m/42° provisional gameplay and overview cameras, with recorded clipping/lighting/state; source neutral images do not close it |
| Deliberate collision, actual movement/query/multiplayer/placement | pending; owning gameplay/world stage validates the eventual saved collision/placement through production APIs and affected separate processes; source holes/gaps are not traversability evidence |
| Target device/performance | pending; owning target-validation stage measures the integrated candidate under its existing envelope; no budget, device access or test is invented here |
| Rigs, clips, animated bounds, VFX, normal maps, runtime textures | not applicable to these static opaque untextured source outputs; future district artwork has its own provenance/material gate |
| Explicit LOD or optimization system | not applicable without a demonstrated measured need; counts are observations only |

The review does not reopen historical stage decisions or authorize another world,
road-surface, device or model-production dispatch. On callback this same session
returns idle, preserving this packet for the exact final source/engine candidate
and delta review when explicitly supplied.
