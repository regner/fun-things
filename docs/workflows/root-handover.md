# Fun Things continuation handover

Prepared 8 October 2026; current repository state refreshed 9 October 2026. This
document transfers repository context to a new coding agent. It is not a new experiment grant, technical acceptance or plan checkpoint.
No particular agent platform or delegation tool is required to read it.

## Prompt for the receiving agent

> Read `docs/workflows/root-handover.md` completely, then read `AGENTS.md`,
> `TODO.md`, the linked requirements and the
> [8 October owner decisions](../reviews/owner-decisions-2026-10-08.md). Verify actual
> Git HEAD and preserve unexpected work. Continue through the current parent-created
> lane queue; do not revive superseded experiment recommendations or push remotely.

## Current repository state — 9 October 2026

- The integration branch is `main` at `406b9b6` (`docs: record quiet S17 host tick
  measurement`) when this handover was refreshed. Verify actual HEAD rather than assuming it
  stayed there. The old `s08-enet-bandwidth` branch is deleted.
- The commissioned foundation lanes through S17, including S03-P, S04-P, S04-T,
  P0-TOOLING/P0-TOOLING-2 and the audit gap tasks, are integrated. The S17-only
  [quiet record](../spikes/quiet-remeasure-2026-10-09.md) is integrated, and the refreshed
  [P0-GATE packet](../reviews/p0-gate-packet-2026-10-09.md) reconciles its result, all
  deliberately retained contended measurements, residual risks, owner decisions and human
  checks.
- Development is on Windows 11. Use the Mise-pinned Godot
  `4.8.dev7.official.c971f93e7`; the owner decided to stay on this pin for now.
- Orchestration uses pi subagents in parent-created Git worktrees under
  `C:\GameDev\git\ft-lanes`. Parent launches use three-hour child timeouts and keep-awake
  coverage. Child lanes must never stop unrelated processes. Every windowed runner must use
  the exact 60 FPS guard in `tools/window_safety.py`; uncapped rendering is withdrawn on this
  laptop after two GPU device removals.
- The [8 October owner decisions](../reviews/owner-decisions-2026-10-08.md) govern controls,
  prediction, vehicles, explosion presentation, UI, environment scaling, initial ENet
  scope, desktop targets, engine pin, profiles and the completeness tasks authorized by
  instruction 12. Decisions 13–19, recorded in the gate packet, restrict quiet reruns to
  S17, make S10/S17 the first production acceptance work, set capped 60 FPS with
  p95 ≤16.7 ms / p99 ≤20 ms, define dead-driver coast-to-abandoned behavior, remove
  GodotSteam in a separate lane, select host-current-time hit verdicts with view-tick-ready
  fire intents, and accept S03-P's ordered bounded M1 input queue. The
  [P0 audit](../reviews/p0-readiness-audit-2026-10-08.md) supplies historical gap rationale;
  the packet records the current integrated disposition.
- World concept work is separately commissioned and stage-gated at Stage 1; use the
  [world concept handover](world-concept-handover.md). It does not authorize production
  scenes or later concept stages before owner approval.
- Do not push. Parent orchestration owns lane review, integration and cleanup.

On adoption, inspect Git status, HEAD, worktrees and operation markers. Preserve any
unexpected saved or unsaved work rather than resetting, cleaning, stashing or deleting
it to match this snapshot. Historical temporary files may be absent; do not assume
an old temporary path remains usable.

## Required reading

Read these fully before proposing or starting the next task:

1. `AGENTS.md`, `TODO.md`, `docs/plans/task-requirements.md`.
2. `docs/development.md` and `docs/multiplayer.md` for affected implementation and
   validation conventions; `docs/assets.md` before asset/editor-managed work.
3. `docs/reviews/owner-decisions-2026-10-08.md` and the active lane brief.
4. The owning spike, contract, callers, saved data and tests for that lane.
5. Historical checkpoint and experiment records only when the active task depends
   on them; they do not supersede the owner decisions.

Inspect relevant callers, saved data, contracts and tests before implementation.
This handover is not a substitute for the precise experiment card or raw requirements.
Do not turn adoption into an unsolicited full-codebase audit.

## Historical accepted work (before the current lane queue)

| Delivery | Integrated revision | Actual outcome |
| --- | --- | --- |
| Ninth plan checkpoint | `85282adddd8182a6f31b2c80e4419d1d406b3bb2` | Static plan review through `2d545725`; P0 OPEN; one documentation follow-up identified. |
| S08 source-first diagnosis | `07a7e5bd9e135aa76a8dbe493c9d3192618e14f4` | Supported native/API ownership paths, competing unknowns and one unexecuted diagnostic card; no cause, fix or runtime credit. |
| P0-DOC14 reconciliation | `244089785b0d106451160acd89859c6977d30956` | Eight discovery documents reconciled, explosion-carrier catalogue entry added, DOC14 removed as completed; other tasks preserved. |
| S07 representative preparation | `ca61520488e0756ae54e27e3615add76fbef1c98` | 15-row readiness matrix, eight proposed preparation slices, unexecuted measurement proposal and separate user decisions; S07/TODO remains OPEN. |

All were independently reviewed at their exact delivered revisions and integrated
locally with linear history. Material fixes and rebases returned to the same reviewer.
Complete reports, actual check sources/commands/diagnostics, failures and required empty
streams were retained; integration verified evidence readback and saved cleanliness.

### Historical evidence access without session history

Committed records and their ledgers are the starting point. Additional complete
review/check packages exist as local Git objects attached through Git notes. Notes
and auxiliary objects are not necessarily available in an ordinary clone. If moving
to another checkout, verify evidence availability; do not invent missing historical
results or assume permission to push them.

Original immutable package blobs can be read using `git cat-file blob <hash>`:

| Package | Original blob | Payload format / report selector |
| --- | --- | --- |
| S08 diagnosis | `9e67ce5deef20b0017662a4fa712a6687a0b702c` | 72 payloads/11 required empties; plain-text objects at `payloads["review/report.md"]` and `payloads["review/final-report.md"]`. |
| DOC14 corrected original | `2c92e87e64e71918436bb39b655c5fabbd258d67` | 166 payloads/44 declared empties; full initial and corrected reports at `payloads["review-initial/report.md"]` and `payloads["review-final/report.md"]`. |
| DOC14 rebase | `e1b561b5bf34e8a4a87a14d396c6261a0b85d709` | 65 additive payloads/18 declared empties; report at `payloads["review/report.md"]`, plain text. |
| S07 preparation | `ffcb4f354089b4366998e4444e033e7ead7615e2` | 52 payloads/10 required empties; `payloads["review/initial/report.md"]` and `payloads["handoff.json"]`, base64 rows. |

Later integration receipts augmented the attached notes while preserving all original
fields and payloads. An original immutable blob and the current attached note are
therefore different snapshots, not contradictory evidence. Inspect the actual schema
and encoding, select needed fields, decode, and verify byte counts/SHA-256. Avoid
printing giant encoded packages or parsing a truncated tool read as complete JSON.
Read every chunk or use a local full-file parser.

The committed S07 evidence binds 115 source records and the historical 186-input
inventory, with two later S03 telemetry changes explicitly distinguished. Its four
early static-check failures and retrieval errors remain retained. It made no gameplay,
fixture, performance, hardware or graphical claim.

## Current lane order — refreshed 9 October 2026

The earlier foundation queue is complete and historical. The S17-only quiet measurement and
owner decisions 13–19 are reconciled in the packet. Review it and record the P0-GATE
disposition; do not begin M1 merely because the executable foundation lanes integrated.
Under decision 14, the remaining human reviews and open production choices are not additional
foundation prerequisites. If P0-GATE passes, begin with S10 behavior/budget and S17 production
host-budget acceptance, then use the packet's other recommended starts and the ordered
[M1 production plan](../plans/m1-production-plan.md). Linux S08 confirmation and P0-PROFILES
remain non-blocking.

## Historical prior recommendation: S08 diagnostic — superseded

The text below records the prior recommendation only. Do not treat it as current
direction or authorization. The user previously requested a handover instead of
approving that runtime work.

Two questions remain distinct:

1. Where does the original saved-main held-input/resync sequence first stall, and
   what is the actual close/deadline ordering?
2. What native registration/lifetime sequence explains the release-only
   `tree_exited` diagnostics?

Read-only repository/adoption/readiness inspection is appropriate. Before telemetry
edits, staging/package mutation, engine execution or process/socket creation, obtain
an explicit bounded commission covering those phases and private resources. The
existing source-only card itself grants none of those operations.

The **full committed card** owns the details. Important boundaries:

- Bind the original **34-file S08/S01/S03 closure**, cached inputs, package/template
  and saved-main identities from the immutable standard/handoff records. **STOP if
  inputs are unavailable or different**. Do not regenerate historical caches or
  silently substitute minimal S03.
- Additive telemetry and a derived package need their own authorized preparation
  envelope, exact frozen source/package hashes and inverse delta before launch.
  Preserve original statements, values, waits/RPCs, assets, UIDs, hierarchy and saved
  main transition. A derived package is not byte-identical to the historical PCK.
  Instrumentation overhead is disclosed, not assumed timing-neutral.
- Preserve original **20 ms UDP servicing**, its owner/constants, datagram bounds,
  stale-held deadlines, arming/input/fault/event schedule and gameplay timing. No
  faster independent polling thread, deadline extension or proxy rewrite.
- One RELEASE host/client set observes held-send/validation/result/resync edges,
  close reasons/deadlines and public native-slot state. Do not presume a common
  cause or promise a fix. Public connection lists cannot reveal all native comparator
  bytes/function identities; that limitation may remain after the observation.
- Proposed absolute **30 s runtime/setup/cleanup/readback** budget: live client
  handoff by +4 s, work/observation ends by +20 s, all cleanup finishes by +30 s.
  No fresh per-child cleanup allowance. Package preparation requires a separate
  explicit envelope, not hidden runtime setup outside the clock.
- Preserve literal cut75/admission/journal70/held/resync/subset expectations, actual
  traffic, separate clock domains, strict errors/warnings, full streams and actual
  reap/closure receipts. Successful gameplay exits do not imply clean diagnostics.
- One attempt, then stop/report. No automatic second set, DEBUG rerun, native build/
  repair, pin change or retry. Another attempt needs changed conditions and authority.

A bounded result may identify the first missing edge and remaining unknowns without
fixing the problem. Do not close original-main20ms, clean-release or full S08 unless
required evidence actually passes. Missing authority or original inputs is a concrete
blocker, not permission to improvise another execution route.

## Historical failures and limits

### S08

Measured minimal-S03 DEBUG/RELEASE matrices passed gameplay under **unplanned 10 ms**
servicing. Scheduling/grant compliance FAILED. Strict RELEASE diagnostics FAILED:
**2 host / 6 client `tree_exited` errors**. Original saved S08 main/assets were not
rerun or fixed. Restored 20 ms helper source is offline-only/unexecuted.

Object connect/disconnect use the base comparator; custom bind delegates to the
underlying comparator. Bound versus unbound spelling alone is **not** a demonstrated
identity defect or justified fix. Native cache ownership is source-supported; actual
failed comparator/lifetime mechanism remains unknown. Client IDLE does not prove it
closed first. Never subtract independent host/client elapsed clocks directly.

### S05 and graphical access

Finite authoritative chain outcomes and eight Blender-linked cosmetic slots exist.
The sole disabled-VSync image attempt failed at endpoint-binding **proof** before
live/late launch. No workload PNG or effective-VSync evidence exists; attempt consumed,
no identical retry. This is not a demonstrated native bind or rendering fault.

Stopped S02 drawability observation produced 2112×1320, not required 1280×800;
native focus was false and input suspended. Full positive criteria FAILED. No usable
physical-input/focus/scanout route was established for automated work. Resume stopped
experiments only with changed conditions and explicit authority.

### S07

The accepted sustained simulation driver completed **57 traversals**, 19 per route,
36,461 samples over 608.639614 actual seconds for 600 declared seconds. Do not repeat
that historical experiment. It proves no graphical calibration or capacity. Earlier
author supervision failed; an interrupted development review lacks final exit/reap
receipts. Do not reconstruct them from present PID absence.

The new plan exposes real missing content, AI, gameplay lifecycle, four-rig encoding/
journal/reset and graphical telemetry. Empty, duplicate or proxy workloads cannot
qualify. There is no mandate to finish M1 before P0, and no waiver of R's requirements.

C0 comparator-driver preparation is independent of larger R preparation, but still
needs a new bounded implementation commission. C1–C7 and D1–D4 are proposed slices/
decisions, not automatically authorized launches. Representative content/counts/
diversity, final envelopes and budgets require the user's decisions. None was chosen.

### Product, platform and ordering gates

- Steam public API/interface and upstream research are accepted; actual Steam
  testing, native integration, external route/accounts and device acceptance are
  deferred. Lobby or ENet proof is not actual Steam gameplay proof.
- S02/S04 camera/control/feel/final dimensions and S05 policy choices still need user
  review. Driver death is decided: coast under neutral input, then leave an abandoned parked
  car. Representative production budgets and Windows/Linux target-device proof are absent.
- **P0-GATE remains OPEN. M1 is not authorized to start.**
- Configuration changes and tool setup remain outside this handover's authority.
  No vendor repair, renderer/pin/transport choice, device/account acquisition or
  remote push is implied.

## Workflow requirements

Apply `AGENTS.md` and the relevant owning contracts. For each future commission:

1. Name one owner, exact base, affected paths, complete raw authority, observable
   acceptance, private resources, total effort/attempt/cleanup limits and stop rules.
2. Separate implemented behavior from proposals, source inspection from execution,
   and partial evidence from full acceptance. Ordinary recoverable mistakes stay
   within the grant; retain failures. Do not repeat unchanged stopped experiments.
3. Preserve saved IDs, UIDs/sidecars/imports, source/export links, authored placement
   and single gameplay/state ownership. Discover suitable editor tools before
   editor-managed changes. If unavailable, explain the fallback and real saved/
   unsaved synchronization plan. Import alone is not editor synchronization.
4. Obtain independent clean-context review of raw requirements and exact HEAD/base
   before acceptance. The same reviewer should assess material fixes or rebases.
   If the new environment cannot provide independent review, disclose that limitation
   and agree a review route instead of claiming it happened.
5. Keep review/retention proportionate: complete reports, actual sources/argv/cwd/
   exits/full diagnostics/failures/required empty streams, independently declared
   expected paths and source/stored/decoded hashes/readback. Reference old evidence
   instead of copying recursive packs. Metadata-only storage does not need another
   report-only commit or review acknowledgement on an unchanged candidate.
6. Integrate only authorized accepted work: saved/quiescent writers, clean main and
   worker including untracked/no operations; rebase onto current local main if needed;
   review the exact rebased delta; verify ancestry/linear history; fast-forward the
   exact approved revision and recheck. Never force integration or create merge commits.
   Remove temporary worktrees only after delivery evidence is durable and all work saved.
7. Remove completed TODO items with their resolving change; leave partial gates open.
   Reread all tasks/requirements after integration and preserve actionable prerequisites.
   In particular, district assembly needs approved road/building/prop subsets, not the
   entire art catalogue; minimap work can follow player simulation with final district
   alignment later. All M1 tasks still follow P0-GATE.

No platform-specific model or agent launch recipe is required. Use reasoning effort
proportionate to complexity: routine documentation/source planning succeeded at medium;
native lifetime diagnosis warranted higher effort. Do not make high effort a default
merely because a task mentions maps, 3D or review.

## Checkpoint cadence and first action

Latest accepted checkpoint examined through
`2d5457250701ebf93ef6e90f0e82ec9f384fd530`, not its own unseen storage commit.
Since then there are at most **two substantive source-preparation streams**: S08
diagnosis and S07 preparation. Documentation reconciliation, review fixes, rebases,
retention and this handover do not independently count. A full checkpoint was not due:
normal cadence is roughly 6–8 substantive streams, or earlier consequential scope/
gate/milestone change. Never advance the examined watermark solely due to a rebase.

After reading and verifying current state, explain the finite S08 diagnostic scope and
obtain the missing approval for telemetry/package preparation and private runtime
resources. Alternatively, let the user explicitly select another task. **Do not start
any S07 slice, S08 run, native repair or configuration change merely to “continue.”**
