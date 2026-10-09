# BATCH02 independent SOURCE/EXPORT review

9 October 2026. **Scoped verdict: pending calibration evidence.** The independently
checked source geometry, export correspondence, retention and source-form lenses
are accepted for integration. No P0–P3 source/export defect requiring correction was
found. This does not accept the complete production handoff: the specific metre
comparison gap below and all engine/prefab/world/device gates remain pending.
No blanket READY status is warranted.

## Exact scope and independence

Candidate: `5e94cc0ea4155219285db49c64b5728e0882b093`.
Immediate parent: `784dfc33a47f481ee43441c36a0280793e02de77`.
Original base: `66400c26a01bf917dfe631af4762c2b444d9c48f`.
Branch: `art/register-production-20261009`; workspace `wks_59891ad7a05813e5`.
Reviewer: this fresh clean-context session; supplied launch receipt is
Codex / GPT-6.1-Sol / high / auto-review. No implementer conversation, conclusions,
suggested verdict, subagents or shared Blender/Godot session were used.

Exactly six stable IDs: `city_planting.03/.04/.05`, `city_roof_details.01/.02`,
`city_shop_fittings.01`. Their six Blender sources, eight explicit GLBs, per-ID
tools/reports/evidence/material contracts and batch source-readback are reviewed.
Frontage `.02/.03/.05/.06/.07` are excluded. Earlier batch01 assets are immutable
interface/scale references only; this report does not reaccept them.

The exact candidate was extracted with `git archive` into
`/tmp/batch02-review-5e94cc0/snapshot`. Every scoped payload's extracted bytes also
match its candidate Git blob independently. The parent delta is **342 additions,
zero modifications/deletions**: 335 manifest payloads, six manifests and
`batch_02-evidence/source-readback.json`. The reviewed six-ID delta from original
base is the same addition set. Other original-base changes belong to prior work.
The active worktree contains unrelated concurrent integration/frontage work and is
not the review input. No Git/index/shared documentation/source/output edits occurred.

Read contracts: candidate AGENTS.md, art-review skill, orchestrator reviewer
contract, immutable production commission, assets/art-direction/world-layout/scene
contracts, S01 bounded route, product validation envelope and TODO gates. Read the
three family briefs and relevant Signal Row/Ironreach/Glassward/Broadlot/Old Quay/
Crescents/Northpoint context and breakdowns. The production commission supersedes
the briefs' historical concept-only restrictions. Reference images are style
evidence, not calibrated dimensions or a requirement to reproduce incidental detail.

## Findings and the smallest pending check

**No actionable defect found with the coverage below.** Missing evidence is not
reported as wrong geometry.

**Pending C1 — complete the metre-reference comparison.** `docs/assets.md`,
“Units, axes, origins and export scope”, requires a 1 m measurement fixture and a
dimensional/front/up comparison. All six sources are Metric/unit scale 1; actual
source and decoded GLB bounds agree, and fresh exports are exact. However:

- Shrub `.03` and tree `.04` have no retained metre fixture in their own sources.
  Shrub `.03` does have a useful shared unchanged-GLB comparison against the actual
  1 m rod in `.05`'s `scale_comparison_hero.png` and receipt. Its GLB hash matches
  this candidate. This closes that bounded source visual comparison, without
  inventing a fixture inside the shrub source.
- Weed `.05` retains an actual 0.035 × 0.035 × 1.000 m rod, with a visible
  comparison of both weed variants, shrub and unchanged Courier.
- Roof `.01/.02` each retain an actual 1 × 1 × 1 m cube, excluded from export and
  hidden in their final previews. Their shop comparisons use the unchanged
  18 × 15 × 10 m greybox, not a visible 1 m comparison.
- Canopy `.01` retains an actual 1 m cube, and its measured comparison visibly
  includes it. The reference cube's placement beside the canopy is authoring
  evidence, not a ground-pivot contract for the wall-mounted fitting.

Smallest owner/check: integrator `150f00b5-9e62-44d8-b0aa-a456d2a88b8c` can supply
ONE shared, source-linked, unchanged-source metre/front/up calibration comparison
covering the tree variants and roof fittings, plus source/import numerical readback
and exact hashes. Extend it to all eight outputs to keep the final batch mapping
unambiguous. Retain actual camera/settings/logs and identify the 1 m fixture's
Blender provenance. No source remake, arbitrary scale correction or extra LOD system
is requested. The same reviewer should assess that evidence at the exact final
engine candidate/delta. Until then C1 is pending, not a geometry rejection.

Two non-defect observations are retained honestly. The compact tree's
`compact_sculpted_trunk` has one isolated vertex without faces, at Blender
approximately `(0.0499998, 0.4750000, 2.7000072)`. It is inside the crown envelope,
has no rendered/exported triangle and changes neither bounds nor fresh-export
correspondence. No visible/topological solid failure or necessary cleanup is inferred.
Also `.04/assembly_preview.py:screen_bounds` includes imported meshes without a
render-visibility filter. Its actor rectangle is therefore a conservative
all-imported-geometry bound, not the Courier's actual rendered silhouette. The
positive separation remains a conservative static example; its 5 px test and
2.6 m layout do not ratify gameplay spacing or universal actor visibility.

## Independent checks and measurements

All new Blender work used private CLI processes, pin **5.2.2 LTS,
`d13f752e3b9c` / glTF 5.2.40**, two bounded threads,
`ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy`, `-noaudio`. The live shared resources
remained with the integrator. Sources were opened read-only; selections, lights,
cameras and preview visibility were changed only in memory. Sources were never
saved. Fresh GLBs and eight independent source renders are in this directory.

| Output | Decoded X/Y/Z size, m | Triangles | Fresh export |
| --- | --- | ---: | --- |
| Shrub `.03` | 1.083529 / 0.670000 / 0.690894 | 4,932 | Exact, 70,556 bytes |
| Tree `.04` compact | 1.998589 / 3.596365 / 1.847576 | 19,282 | Exact, 278,900 bytes |
| Tree `.04` broad | 2.772049 / 3.317199 / 2.441693 | 19,418 | Exact, 281,264 bytes |
| Weed `.05` tuft | 0.560000 / 0.260000 / 0.420000 | 1,170 | Exact, 24,200 bytes |
| Weed `.05` spreading | 1.000000 / 0.200000 / 0.620000 | 1,950 | Exact, 36,044 bytes |
| Roof vent `.01` | 2.600000 / 0.760000 / 1.600000 | 3,536 | Exact, 68,384 bytes |
| Roof enclosure `.02` | 3.200000 / 1.550000 / 2.200000 | 6,180 | Exact, 116,664 bytes |
| Shop canopy `.01` | 3.200000 / 0.660000 / 1.100000 | 1,212 | Exact, 25,620 bytes |

`source_audit.py` independently reads collection membership, root/child ancestry,
identity transforms, closed/consistently wound edges and positive volume of each
face-bearing island; finite positions and every triangulated face area. It records
all source objects, properties, images and libraries. No external linked libraries
or texture dependencies are present. Source construction scripts contain local
mesh/profile/blade construction and explicit original authorship; no downloaded
model or concept-image mesh import is observed. Rights/provenance are accepted
as original project work within this inspectable evidence, not a forensic claim
about unobservable author activity.

`glb_audit.py` independently decodes buffer views/accessors, actual indices,
positions/normals, scene roots and every primitive. All eight exports are byte
identical to their saved-source fresh exports. Export node sets equal their named
root plus the source members; tree/weed variants are isolated correctly. No studio,
fixture, camera/light, animation, skin, texture, external buffer or required
extension leaks into these GLBs. All node transforms are identity. Source +Z up /
+Y front converts once to GLB +Y up / -Z front. Source and binary AABBs agree within
0.00001 m and match each handoff's declared 0.001 m bounds tolerance.

All decoded triangle areas are nonzero, normals finite/unit, and triangle normals
agree with their shading normals. Face-bearing source components are consistently
closed and outward. Intersections between foliage masses or manufactured parts are
intentional assembly overlap; no watertight union is required for decoration.
Colour-only PBR slots/values match source materials. Shrub is intentionally
double-sided as documented; other outputs are single-sided. All are opaque, with
no UV/texture/normal-map requirement for these flat-colour materials. No external
material or texture directory is required merely to create empty paths.

Independent interface clipping uses decoded triangle intersections, not just
vertices or producer formulas. Shrub below its 0.20 m local rim plane occupies
X `[-0.409115,0.417154]`, Z `[-0.166360,0.154442]`; two shrubs at X ±0.48 fit the
immutable trough's 1.90 × 0.40 m reserved planting rectangle at Y +0.40.
Whole shrub radius is below 0.60 m, compatible with the round surround's reserved
ground core. Compact/broad tree radius through Y 0.48 is
0.197217/0.197698 m, well inside that same 0.60 m reservation. This does not add
soil, authorize lifting the tree, or establish actor passage underneath foliage.

Both roof flashings have actual planar contact geometry at Y=0, inside the
documented outer envelope. Level support patches ≥2.70 × 1.70 and
≥3.30 × 2.30 m and the proposed roof-edge margins remain installation constraints;
pitched roofs need separately reviewed adapters. The canopy projects toward -Z
from the wall at Z=0, with an actual planar mounting back. Its lowest point is
Y=-0.42; a 3 m pivot gives arithmetic 2.58 m headroom. The reserved 3.4 m flat bay,
opening/sign separation and facade flatness remain actual-shell checks. Greybox
comparison does not prove future frontage fit or movement clearance.

## Source-form visual disposition

Viewed candidate district references and useful producer heroes, assembly, detail,
metre/greybox comparisons, native-resolution Blender camera studies and the retained
canopy roof-centred occlusion image. Also generated and inspected eight independent
800 × 650 oblique source previews. These fresh renders show only each declared
export's authored geometry with temporary review lighting; they are not engine or
gameplay captures. Input image locators/hashes are retained in the reference index.

Shrub's five overlapping quiet lobes read as low planting rather than dense leaf
noise. Tree variants differ by crown geometry and height, retaining a simple trunk
and large rounded masses; no individual leaves or invented wind/growth behavior.
Weeds are low broad solid blades with visible gaps, distinctly separate from the
filled shrub crown and appropriate for sparse Ironreach margins. Their small
native-camera marks do not establish visibility against every ground material.

Roof vent/enclosure are broad subdued manufactured forms with real sparse louvers
and contained flashing. In the 18 × 15 m greybox comparison, roof silhouette remains
dominant; this is a bounded example, not proof for every future roof. Canopy is a
short restrained projection with a rolled rim, rear rail and two underside supports.
Its front/underside/rear views expose the intended attachment structure. No observed
source silhouette or detail discrepancy violates the accepted broad/smooth language.
AgX/Cycles colours do not calibrate Godot materials under final district lighting.

Opaque foliage necessarily covers objects directly below its crown in a vertical
camera. The tree/actor separation preview demonstrates one sparse arrangement;
entrances, shortcuts, corners, camera edges and crowd layouts remain placement
review. The canopy's roof-centred example is visibly occluded by the taller greybox
roof; its street-centred view shows the fitting. This disclosed perspective behavior
requires downstream occlusion/placement checks, not a source enlargement or gameplay
collision change to force visibility.

## Retention, failures and boundaries

Complete candidate-set check, independently derived from tree prefixes rather than
only enumerated manifest entries: `.03` 37, `.04` 68, `.05` 81, roof `.01` 50,
roof `.02` 48, canopy `.01` 51 payloads. Zero duplicates, omitted/extra payloads,
byte/hash mismatches or changed/removed parent-owned payloads. All six manifest
hashes/counts match batch source-readback. All 53 recorded input hashes checked
match candidate inputs. Original failure sources/logs/images and payload dictionaries
remain accessible at the exact candidate blobs; they are indexed, not recopied.
The readback's unlisted shrub import sidecar describes an integration working file,
not a tracked source candidate import. No engine acceptance is inferred from it.

Raw `git diff --check` exits 2 solely on 18 trailing-whitespace lines in retained
Blender version logs. Preserve these raw diagnostics; this is not an authored
implementation style failure. Reverse consumer search exits 1 with empty streams:
no six-ID saved scene/script/material/texture/catalogue consumers exist in candidate.
Source/output handoffs map these files; prefab/catalogue integration is pending.

Reviewer tooling initially failed on Blender `IDPropertyArray` JSON serialization,
and on treating the compact trunk's zero-face isolated vertex as a solid. The initial
source script, exact argv/exits/full stdout/stderr, and dependent binary check's
missing-JSON failure are retained. ONE bounded adaptation converts metadata arrays
and explicitly records zero-face components; every face-bearing island must still
have positive volume and every rendered triangle must pass. All five affected
source checks and the binary audit then exit 0. This was reviewer tooling recovery,
not an asset fix. The untouched first shrub check remains its successful receipt.

New Blender logs retain the optional missing MeshOptimizer library message; no
compression extension is used and fresh uncompressed exports match exactly.
Pin/version diagnostics and installed BlenderMCP registration messages are retained;
no live connector was called. Empty stderr streams are actual retained empty files.
Producer failures are historical, retained and distinguished from this independent
result. No additional source retry or engine trial was undertaken.

| Lens/handoff | Status and boundary |
| --- | --- |
| Complete retention / original source provenance | Accepted, six-ID exact candidate |
| Editable source geometry / declared exports / freshness | Accepted, eight outputs |
| Source-form style and material-slot contract | Accepted within inspected source views |
| Numerical metres / datum / axes / bounds | Accepted source/GLB arithmetic; C1 visual calibration pending |
| Full production SOURCE/EXPORT handoff | Pending C1; no observed source defect |
| Godot imports/sidecars / wrappers / inherited identity roundtrip | Pending integrator's exact engine batch |
| Actual runtime shading / native camera / occlusion | Pending integrator and actual relevant placements |
| Decoration/collision separation | Source contains visual meshes only; engine no-collision/query behavior pending |
| Movement/network/world fit and saved placement | Pending affected owning integration tasks; no source-only certification |
| Rig/skins/clips / gameplay sockets / opening/wind/growth/destruction | Not applicable: static decorative family contracts request none |
| UVs/maps/alpha VFX | Not applicable: opaque flat PBR and closed solids, no textured interface |
| Extra LOD framework | Not applicable until measured need; existing import LOD settings still require engine inspection |
| Measured performance / target devices | Pending; density is recorded, no arbitrary budget or Deck pass |

This reviewer is available for the exact final engine candidate/base/delta and C1
follow-up. Initial evidence remains separately under `initial/`; later disposition
belongs under `final/`. No engine/private editor resource, source output or Git
writer remains owned by this review.

## Evidence entry points

- [Independent binary results](binary-audit.json), [source fixture readback](calibration-source.json).
- [Complete candidate payload index](candidate-payload-index.json), [retention result](retention-check.json).
- [Reference audit](reference-audit.json), [shared immutable input index](shared-input-index.json).
- [Actual check sources and execution mapping](execution-check-sources.json), individual `*.command.json`, `*.stdout`, `*.stderr`.
- [Review artifact index](artifact-index.json), [expected set](artifact-expected-set.json), [pack verification](artifact-verification.json).
