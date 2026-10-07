# First plan and documentation checkpoint

Date: 7 October 2026. Worker: Codex, Sol 6.1 high. Budget: one focused
planning/documentation pass and fixes. No gameplay, asset, editor or live service
changes. This is a plan/evidence consistency check, not a whole-codebase audit.

## Baseline and watermark

No prior periodic plan-check record was found in tracked `docs/`, `TODO.md`, project
skills or recent history (search: checkpoint, last checked, checked-through,
plan review/check). Existing spike/decision/review records are completion evidence,
not a previous whole-plan check. This establishes the **first baseline**.

Historical starting point included: P0-01 ratification at
`445bf9a0ac637601560633e569b52f3279025ffe`, with earlier milestone planning at
`09eea8c3e989e618586c2c69c07a91e965616cad` supplying context. Examined integrated
foundation range: `09eea8c3e989e618586c2c69c07a91e965616cad..3b50a915d06f7ad383a4d6dc70403729918c0268`
(left endpoint excluded; P0-01 and all subsequent foundation changes included).
Checked-through main revision: `3b50a915d06f7ad383a4d6dc70403729918c0268`.
The orchestrator reported verified P0-07 integration/archival; the worker then read
its accepted delta and records and rebased onto this exact local main without conflicts.
The additional examined range is
`0436db7f0ab2dbe0ef07311f6cb10ebf1b7b2e07..3b50a915d06f7ad383a4d6dc70403729918c0268`;
it is included because it was examined, not merely because the branch was rebased.
The checkpoint's own plan/skill changes are reviewed separately at candidate HEAD;
that candidate is not a claim that later main changes have been examined.

## Evidence consulted and accepted state

Read all of [TODO](../../TODO.md), [repository guidance](../../AGENTS.md),
[README](../../README.md), [design](../design.md), [architecture](../architecture.md),
[scene contracts](../scene-structure.md), [API contracts](../api-contracts.md),
[development](../development.md), [assets](../assets.md),
[multiplayer](../multiplayer.md), [guidance provenance](../guidance-sources.md),
[art direction](../art-direction.md), [world layout](../world-layout.md),
[catalogue](../asset-catalogue.md), [P0-05](../decisions/p0-05-asset-workflow.md),
[P0-06](p0-06.md), [S01](../spikes/s01.md) and [S03](../spikes/s03.md).
Consulted the orchestration/Paseo/skill-creator instructions and foundation history
(commit subjects/range and changed-path inventory) to trace accepted versus planned work.

- P0-01 scope is ratified; P0-02 is a reviewed contract draft; P0-04 is accepted
  concept direction with explicit actual-camera/production-art deferrals. P0-05 is
  a workflow specification, P0-06 a review workflow with an isolated dry run.
  Those tasks remain removed. Historical observation sections retain their original context.
- S01's two neutral Blender/GLB fixtures, linked wrappers and wrapper-level inherited
  material route are accepted at the recorded bounded scope. All four source/export
  SHA256 values in [fingerprints](../spikes/s01-evidence/fingerprints.json) match
  current bytes. Read [summary](../spikes/s01-evidence/summary.json) and accepted
  before/after identity evidence. No fresh Blender/Godot operation ran here.
- S03 and combined P0-03 minimum tooling are complete. Read the
  [fixed result](../spikes/s03-evidence/reviewed-fix-result.json),
  [ten-script compilation](../spikes/s03-evidence/reviewed-fix-compilation.json)
  and integration/limitation ledger. All 17 retained fixture fingerprints match.
  Inspected saved Boot/local-rig composition and targeted proof/session/replication
  assertions for resync deadlines and native subset recovery. The rig is a placeholder;
  markers do not prove gameplay/collision. No fresh network/engine test ran.
- Inspected `mise.toml`, `project.godot`, `tools/script_checks.py` and
  `tools/s01/reexport.py`: commands and focused fingerprints exist, root main scene
  remains unset, and editor/native plugins remain configured. S01's full-project
  import errors and S03's headless thumbnail diagnostic are retained limitations,
  not a clean root export/Steam result. Compatibility ownership stays S03-S/S08.
- P0-07 is now accepted/integrated at `3b50a915d06f7ad383a4d6dc70403729918c0268`.
  Read its full changed-path inventory, TODO/asset-guide changes,
  [completion](p0-07.md), [dry run](p0-07-dry-run.md), art-review skill,
  [skill validation](p0-07-evidence/skill-validation.json) and
  [preservation/command audit](p0-07-evidence/dry-run/final_audit.json). Also read
  the fresh final Astra/high review at `/tmp/p0-07-final-review-j4DpW7/review.md`
  (durably retained at the accepted commit in `refs/notes/paseo-orchestration`).
  Final reviewer `a97eb9e9-d06d-4d6a-960f-be73415482fe` accepted the exact revision;
  independent dry-run reviewer `e9e165ea-8e16-4a77-b7f0-c314d0a4860f` rejected the
  intentionally flawed temporary prefab, demonstrating useful findings. That is
  skill completion, not production art acceptance. No visual/spatial evaluation
  was rerun by this checkpoint. Its P0-GATE evidence replacement and S03/P0-03
  completion paragraphs survive the rebase; it added no gameplay/source mutations.
- Production M1 systems, Steam traffic/tester installation and physical Deck proofs
  are still unimplemented/unverified. No acceptance is inferred from a worker turn,
  concept PNG, source pin, loopback result or recorded app/depot ID.

## Documentation findings

Canonical documents are intentionally left for the following **open** TODO work.
These findings require status/ownership reconciliation, not a new gameplay design.

| Finding and source | Disposition / measurable follow-up |
| --- | --- |
| `docs/guidance-sources.md`, Adaptation decisions: compiler/resource checks described as future; accepted S01/S03/P0-03 and `mise.toml` now supply focused implementations. | P0-DOC1: enumerate existing scope and reserve broader CI/production checks for M1-D1. |
| `docs/assets.md`, Files/catalogue: authoring-source fingerprints/export tools deferred without acknowledging `tools/s01/reexport.py` and committed S01 fingerprints. General catalogue automation remains future. | P0-DOC1: add the scoped S01 exception/evidence, preserving the manual catalogue and future broader automation. |
| `docs/reviews/p0-06.md` after-rebase paragraph and S01 closing limitation still leave P0-03 future/open. Their historical run descriptions are valid; a current-status supplement is missing after combined acceptance at `ece3ef1`. | P0-DOC1: link later acceptance without rewriting original dry-run/experiment observations or claiming new tests. P0-05 already has a subsequent-S01 supplement and needs no duplicate task. |
| `docs/architecture.md` closing advisor summary still says snapshot reordering remains S03 proof work, although its preceding S03 decision and results settle tiny subset refresh. | P0-DOC2: clarify historical review versus settled minimum, retain capacity/body proofs. |
| `docs/api-contracts.md` limits/test-owner rows still allocate unproved closing/action/reset/lifecycle/future-state/tombstone and full seat work to completed S03 or spike-only owners. S03's explicit omissions and TODO's production tasks establish the remaining work. | P0-DOC2: map remaining acceptance to active tasks; distinguish spike specification from production suite, without changing limits or promising full proof from S03. |

No other current canonical guide was found to falsely claim shipped production
behavior. Art/city dimensions, budgets, pin choices and reference images are already
labeled provisional. Historical P0-05 and original P0-06 dry-run observations are
not reclassified as failed proofs. Later spikes must still reconcile affected docs.

## Entire TODO disposition

Every active task at the examined base is covered below, along with added tasks.
“Retain” means descriptions/acceptance/dependencies remain relevant at their recorded
scope; it does not mean ready, assigned or accepted. All M1 tasks retain P0-GATE.
Named implementers are assigned when work starts; Regner still owns device/access
and scope approval. The previously active P0-07 worker has handed off and its workspace was archived
by the orchestrator; no duplicate implementation or pending acceptance remains.

| Task | Disposition, dependency/gate and validation assessment |
| --- | --- |
| P0-07 | Completed in accepted `3b50a915d06f7ad383a4d6dc70403729918c0268`; resolving removal and P0-GATE evidence reference preserved. Prior worker/workspace handed off and archived by orchestrator; no duplicate. Unfinished camera/movement/load/device acceptance remains with spikes. |
| P0-PROFILES | New, deferred and ineligible now; later session-evidence readiness check, then reviewed permission-respecting launch bundles. Not a P0-GATE prerequisite. |
| P0-DOC1 | New, ungated documentation worker task; exact docs/evidence/done criteria above and in TODO. Complete before P0-GATE reconciliation. |
| P0-DOC2 | New, ungated contract-documentation task; depends on accepted S03 ledger and task allocation. Can run with DOC1; full proof remains downstream. |
| S02 | Retain: ratified foot/camera feel and towers; actual-camera/weapon captures and actor envelope. Early S08 before handheld acceptance; desktop fixture preparation can proceed. |
| S03-S | Retain with stale “alongside S03” wording replaced by accepted boundary reuse. Regner owns access; distinct accounts/networks, real Steam peer/route and native cleanup required. |
| S03-R | Retain: actual S02 controller; ENet can start early, Steam evidence required before final decision. Measured response/convergence, independent of car prediction. |
| S04 | Retain: S02/S03 boundary, finish with Steam; Blender car/actual camera/body response and seated resync. Specify full seat matrix for M1-B1, not an expanded production spike. Seated firing policy still a P0-GATE feel decision. |
| S05 | Clarify bounded 12-car chain-capacity feasibility already required by API contract/designed V3, alongside near/far three-car case. S04 minimal damage/vehicle fixture; record queues/peaks/off-camera completion with eight visual slots. Sustained loads/join races remain M1-B3/D3. |
| S06 | Replace closed S01 prerequisite with evidence. Retain S02/S04 dimensions, one two-sector intersection, routes/minimap/stale bake and host recovery specification. |
| S07 | Replace closed S01 prerequisite with evidence. Retain S02/S06/S05 loads, LCD graphical listen-server measurement and Mobile/Forward+ comparison; offscreen simulation remains active. |
| S08 | Replace closed S01 prerequisite with evidence. Preserve early engine/input/template stage before S02 Deck acceptance and complete S03-S export/access stage; Regner device access, LCD/OLED Gaming Mode and Windows/Linux proof remain gates. |
| P0-GATE | Replace closed S01 reference; add DOC1/DOC2 before guide reconciliation. Retain remaining spikes, reviewed skills, user ratification, measured budgets and independent Steam feasibility/access. Profiles remain deferred outside this gate. |
| M1-A1 | Clarify already-ratified Standalone entry and in-match leave/settings/host-reset UI, including dead host. Retain S03-S/S08 providers, full admission/cancellation/failure/invite flow; no new product feature. |
| M1-A2 | Explicit owner for existing Match reset: retained peers, initial player state, new revision hydration/input fence and unchanged placement. Extend same transition as dynamic owners arrive; retain A1/S02/S03-R simulation/respawn/replication. |
| M1-A3 | Retain: local settings/API decisions, defaults/corruption/save behavior and controls; parallel with A1/A2 after foundation gate. |
| M1-A-GATE | Add shell host/standalone-reset acceptance with peers retained. Retain exported real processes, offline/settings and both transport lifecycles before B. |
| M1-B1 | Retain A-GATE/S04, one authoritative car/driver owner, full seat/death/disconnect/exit matrix and stopping. Replace “if selected” return-to-traffic with the ratified parked policy; changing it requires a recorded product decision. |
| M1-B2 | Retain A-GATE/combat decisions, ratified three weapons/loadout, health/respawn/late joins, stale-command rejection and authoritative shots. |
| M1-B3 | Add explicit integration of seats/combat/rockets/chains/wreck cleanup into A2's single Match reset; retain B1/B2/S05 exactly-once destruction and current-state hydration. |
| M1-B4 | Retain B2/B3 event contracts, bounded feedback and licensed audio; windowed walking/driving/shooting chain slice, replay dedup and readability/cost. |
| M1-C1 | Retain P0-GATE and approved family-specific pipeline/camera/envelopes; custom Blender sources, shared rig, two car silhouettes, catalogue/handoff and art review. |
| M1-C2 | Retain accepted C1 subsets/S06/S07; authored six-block saved sectors, preserved placement, actual clearance/seam/camera validation and refreshed data. |
| M1-C3 | Add population/reset registration and initial-descriptor/cap/AI cleanup under Match. Retain A2/B1/B2/S06/C2 route fixture, host intent, blocked/junction/stuck recovery and offscreen authority. |
| M1-C4 | Tighten marker wording to ratified local controlled entity; any extra marker is a product decision. Retain S06/A2/C2 road-derived seam/late-join/HUD alignment and bounded data lifetime. |
| M1-D1 | Retain accepted foundation tooling prerequisite; grows with production. CI, broader coverage and preserving formatter remain future, meaningful independent contracts required. |
| M1-D2 | Retain B4 and C1–C4, both skills, windowed controller/camera/feel/audio evidence and user disposition of defects/scope. |
| M1-D3 | Make reset while driving/firing/joining, retained peers and old-work rejection explicit under production APIs. Retain A/B/C+D1, both transports, floods/host stalls/collision/capacity and actual named-hardware budgets. |
| M1-D4 | Retain D1–D3/S08; exact exports/exclusions, existing private Steam app/branch/tester route and actual install/update/play across networks. No public release/certification. |
| M1-GATE | Add already-ratified host/standalone reset to user acceptance. Retain D4, custom art/district/gameplay/audio/HUD, ENet/Steam/offline/targets and current docs. |

No completed S01/S03/P0-03/P0-01/02/04/05/06 item was re-added. The parallel table
now points to accepted S01/S03 evidence instead of launching their completed spikes.
Early S08/access preparation can proceed before S02 handheld acceptance; S03-R/S04
may start ENet observations but cannot close Steam response gates. S05/S06 need
actual actor/car envelopes; S07 needs representative city/effects; all production
remains behind P0-GATE. No cycle was introduced by the documentation follow-ups.

## Profile baseline

First read-only check: 7 October 2026. Paseo `list_profiles` returned
`profiles_count=0`; `list_models(provider="codex")` exposed Sol 6.1 with supported
medium/high effort and the model families in the user's policy. No configuration
was created, edited or retired. The initial tool output was not saved; a
[fresh read-only corroborating snapshot](plan-check-evidence/profile-snapshot.json)
was captured at 19:39:34 UTC on the same date during independent review. This
corroborates the empty inventory and model efforts, without reconstructing the
original call. No claim that all providers/modes/features were
validated; those are part of later requirements and launch-bundle work.

Existing S01/S03 implementation evidence, P0-06 review records and current task
constraints give initial context, not eligibility for immediate profile creation.
P0-PROFILES must wait for **additional** representative implementation/review/
visual-spatial sessions. At a later checkpoint, collect raw prompts/settings,
actual categories, tool/capability/permission gaps and repeated operational friction;
then assess suitability, notes/routing, availability and policy drift. Preserve this
single deferred task when the inventory is still empty. Changes to existing profiles
in future require scoped authorized configuration/update/retirement tasks, not
silent mutation during assessment. Next profile revisit: normal next checkpoint
with additional session evidence, or justified earlier capability/requirements drift;
creation still requires the later readiness evidence.

## Changes, questions and next trigger

Concrete changes: two open documentation tasks, one deferred profile task, closed
prerequisite cleanup, explicit standalone/reset ownership and acceptance, bounded
S05 burst proof, and minimap scope wording. Canonical guides were not silently fixed.
The orchestration skill now delegates periodic whole-plan/doc/profile assessments
and keeps exact records; it does not acquire implementation/review authority.

No new product decision is made here. Existing questions remain owned: Regner's
Deck/access details and installed versions (S08), Steam tester entitlement/native
integration/route (S03-S/S08), engine/template/renderer (S07/S08), measured budgets
and foot/car feel (spikes/P0-GATE), and seated firing confirmation (S04/P0-GATE).
Changing controls, relaxing 60 FPS, expanding markers, resuming abandoned traffic AI
or adding deferred features still needs a recorded user decision. Known editor/native
errors need named compatibility evidence in S03-S/S08, not broad suppression or
an unsolicited vendor-fix implementation. No duplicate workstream is assigned here.

Next plan checkpoint: around three additional integrated workstreams after this
watermark, sooner for a significant spike/contract/gate result or before P0-GATE/M1.
A tiny bookkeeping commit alone does not trigger a full re-audit. On resume compare
main/handoffs to the watermark and record due/not-due; rebasing cannot silently
advance it. Profile revisit/readiness follows the evidence condition above.

Validation: skill-creator `quick_validate.py` passes with cached PyYAML supplied via
`PYTHONPATH` (default Python lacks it; no dependency installed). Local-link/heading
validation and task-disposition coverage check pass using `/tmp/plan-check-links.py`;
`git diff --check` passes for this workflow/plan delta. Source hashes were checked
as recorded above. The [independent clean-context review](plan-check-review-2026-10-07.md)
accepted `ef54f461ab5cbb4442c97d6d5f818687f4502605` with no actionable findings.
Reviewer `/root/plan_checkpoint_review` used Sol 6.1 high and both
[raw user requirements](plan-check-evidence/raw-requirements.txt).
[Twelve read-only scenario decisions](plan-check-evidence/scenarios.md) cover periodic/
resume/drift/new-task/active-work and deferred/later-ready profile behavior;
[check summary](plan-check-evidence/summary.json),
[task coverage](plan-check-evidence/task-coverage.json),
[topology](plan-check-evidence/git-checks.json),
[fingerprint results](plan-check-evidence/source-evidence-hashes.json) and
[frontmatter log](plan-check-evidence/frontmatter.log) retain supporting evidence.
That report describes its exact reviewed candidate; final retention-change revision
disposition accompanies the handoff. No findings required gameplay or guide fixes.
Limits: static history/doc/targeted source and retained evidence inspection only;
no new visual/spatial assessment, engine/network/asset test, physical hardware,
Steam service action or profile configuration. Shared editors and services untouched.
