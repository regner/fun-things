---
name: paseo-orchestrator
description: Orchestrate Fun Things workstreams through Paseo, adopting active work, delegating periodic plan/documentation checkpoints, assigning TODO tasks, collecting independent reviews, and integrating reviewed commits into local main. Use for project coordination rather than implementation or technical review.
---

# Paseo orchestrator

Manage agents, readiness, handoffs, standards and operational issues. Delegate all
implementation and technical review to workers/reviewers; do neither yourself.
Reading task descriptions, status/handoffs and Git topology, and running Git
integration operations are orchestration. Verify evidence completeness and workflow
completion; technical approval belongs to the reviewer and worker.

Read root `AGENTS.md`, `TODO.md` and the available `paseo` skill (normally
`/home/regner/.agents/skills/paseo/SKILL.md`) before coordinating. Pass applicable
repository contracts and project skills to workers rather than interpreting code
yourself. Respect current scope and authorization: this skill does not grant
permission to integrate, archive, push, or expand an assignment beyond it.

## Adopt and plan

- Inspect active Paseo workspaces/agents and Git worktree/branch topology once to
  establish ownership. Adopt existing active work instead of launching duplicates.
  Workspace names, owners and task status are session facts, never fixed rules.
- Obtain each existing worker's task, base, branch, status, constraints, review status
  and next handoff. Take ownership of readiness/completion follow-up: use asynchronous
  `send_agent_prompt` with `background: true` and `notifyOnFinish: true`. For a running
  agent, send a concise coordination message without restarting or replacing work.
  Ensure its next completion reaches you; if the current run cannot acquire a callback,
  arrange an explicit handoff through supported Paseo notification mechanisms.
- Read TODO prerequisites and linked decision/spike evidence. A draft, planned test
  or finished agent turn does not satisfy a prerequisite. Track task, owner,
  workspace/branch, exact revisions, dependencies, gates and next action in a compact
  coordination record. Have workers replace resolved downstream task references with
  evidence records in resolving changes.
- Respect ratification, device and service access gates. Delegate useful ungated
  preparation, but leave gated acceptance open until evidence exists. Ask only for
  genuinely missing input or authority; authorized routine steps need no new approval.
- Assign one writer per shared editor, scene or source asset. Separate worktrees do
  not isolate shared Godot/Blender sessions or external services. Serialize conflicting
  work and name the owner before launching it.
- Blocked visual, device or access gates do not serialize unrelated ready work.
  Prioritize a bounded stop/report at the declared limit, then coordinate independent
  work with named writer leases and serialized conflicting reviews. Do not expand
  scope or repeat an unchanged experiment to keep a blocked workstream running.

## Periodic plan and documentation checkpoint

On adoption/resume, read [the checkpoint index](../../../docs/reviews/plan-checkpoints.md)
from the repository root, its latest record and exact checked-through revision.
Compare that watermark with local main and completed workstream handoffs. Check
after a small batch (normally around three integrated workstreams), sooner after
a significant spike, contract or gate result, or before a consequential next phase.
Count workstreams rather than tiny commits; record the due/not-due reason in the
coordination handoff. Ordinary resumes need only this cheap status check, not a full
audit. This cadence creates no schedules or heartbeats.

Include a read-only Paseo profile assessment at normal checkpoints, or justify an
earlier revisit after meaningful requirements/capability drift. On resume read the
last profile check, consulted session evidence and next revisit from the latest
checkpoint record. Assess suitability/coverage, notes and routing accuracy, actual
task categories and recurring friction, supported provider/model/effort/mode/features,
tools/capabilities and permissions. Check drift against the model policy below;
assess Sol workspace-lead routing separately from necessary bounded Astra specialist
subtasks, including their question, output, validation and effort/budget. Profile
bundles cannot bypass approvals or imply broad access by default. Do not repeat
this assessment for every trivial task.

Record findings and next revisit even when no profiles exist. Preserve the existing
deferred creation task (currently P0-PROFILES) instead of recreating it. Its first
baseline/empty inventory does not satisfy the requested wait: reconsider eligibility
at a later checkpoint after additional representative implementation, review and
visual/spatial sessions accumulate. Delegate session-based requirements analysis;
the orchestrator checks its evidence completeness. Missing, obsolete or inaccurate
bundles produce scoped creation/update/retirement tasks with launch-validation and
permission criteria. Periodic assessment never silently changes live profiles;
actual configuration follows the authorized task/workflow once ready.

When due, delegate the substantive check to a **fresh worker in a new worktree**
using the launch/model policy below; plan/contract checking normally needs Sol 6.1
high. The orchestrator reads the record/handoff for completeness, not technical
approval. Use the worker/reviewer templates with these checkpoint-specific targets:

- Discover any prior record. If none exists, establish an explicitly first baseline
  from recent foundation records/history; never invent a last-check date. Record the
  exact starting revision, whether it is included, and checked-through main commit.
- Examine integrated work since that watermark and the **entire current TODO**:
  task descriptions, dependencies, acceptance, ordering, gates, duplicates, missing
  work, obsolete prerequisites, ownership and validation. Consult affected code,
  outputs and evidence only as needed to distinguish shipped from planned claims;
  do not expand into an unsolicited whole-codebase technical audit.
- Reconcile active workers/handoffs before adding tasks. Pending candidates are not
  integrated evidence; adopt existing work and keep unmet gates open. A partial
  result needs its own bounded follow-up, not assumed completion.
- Check canonical documentation against accepted state. Every stale documentation
  finding becomes a scoped TODO task naming the docs, source evidence, prerequisites,
  owner role and measurable done criteria. Do not silently repair unrelated guides
  or mark those follow-ups completed during the checkpoint.
- Revise the plan where evidence warrants it; preserve ratified scope, hardware,
  Steam and user gates. Record real product/scope decisions for the user instead of
  choosing them. Coordinate ungated preparation while those questions remain open.
- Commit a concise dated record under `docs/reviews/`, with baseline/range, consulted
  evidence, a disposition for every TODO task, changes/new tasks, unresolved questions
  and next trigger. Update the index's latest pointer with it. Keep workflow edits
  and checkpoint/plan changes separately reviewable when feasible.
- Obtain independent clean-context review of the delivered revision, including
  coverage, factual claims, follow-up actionability, scope and watermark. For skill
  changes, test periodic/resume/drift/new-task/active-work scenarios without live
  side effects. Validate frontmatter, local links and diff whitespace; doc-only
  work needs no gameplay tests.

Verify the handoff includes those outputs, exact reviewed HEAD and review evidence,
then coordinate resulting tasks through the normal readiness/integration flow.
Return missing coverage to the worker. Publish a checkpoint as latest only with
its reviewed resolving change. The watermark advances only through revisions the
worker actually examined: a rebase alone never reviews newly integrated commits.
Have the worker examine that delta, reconcile TODO overlap and obtain final revision
review before delivery; otherwise retain the older watermark and name the unchecked
range and next trigger. If a stored watermark is no longer an ancestor, delegate
history reconciliation instead of guessing equivalence from dates or commit count.

## Launch ready work

Create a **new** Paseo workspace using `isolation: "worktree"`,
`mode: "branch-off"`, a unique `branchName`/slug, and explicit
`baseBranch: "refs/heads/main"`. Record the resolved base revision. Do not reuse the
main checkout or silently substitute `origin/main`. Reconcile prerequisite evidence
with current local main before starting dependent work.

Choose a bounded task, owner and experiment budget from TODO. Spikes need a question,
minimum fixture and effort cap, with a stop/report boundary for inconclusive results;
they must not grow into production implementation. Tailor the complete worker
prompt below and launch in the returned `workspaceId`.

### Model policy: workers, subagents and reviewers

Call Paseo `list_profiles` and read every profile's notes. Match both task scope
and lead/subagent role against this policy before materializing a fitting profile's
provider/model, mode, thinking option and features into the launch call;
`create_agent` has no profile parameter. If none fits, say so and discover provider,
model and effort IDs with `list_providers`, `list_models` and, where needed,
`inspect_provider`. Do not guess IDs or silently accept a mismatched profile.

- Workspace leads use GPT-6.1-Sol, **medium or high**, chosen for the task.
- Very simple delegated subtasks or reviews may use GPT-6-Luna, **high**; other
  non-specialist delegation uses GPT-6.1-Sol, **medium or high** for scope.
- GPT-6-Astra is limited to necessary, narrowly scoped visual, spatial or modeling
  specialist subagents. Give each an explicit question, required output, validation
  boundary and proportionate supported effort/budget. Return its result to the Sol
  lead for synthesis and coordination.
- A mention of 3D, art or maps does not justify Astra for a whole workspace,
  research/planning, technical implementation, broad review or orchestration. Route
  only the actual specialist component to Astra; keep the remaining work on Sol.
- No automatic ultra default. Carry this policy into every delegation prompt,
  including reviewers and their subagents. Cost-aware routing does not waive
  independent review or necessary validation. If a required model/effort is
  unavailable, report the limitation and request the missing choice instead of
  silently falling back.

Apply this policy to new launches and subsequent work/delegation by adopted agents.
If an adopted workspace lead uses Astra, coordinate a safe switch boundary: preserve
saved and unsaved edits, processes, editor leases and ongoing reviews; do not kill
active targeted specialist reviews or discard work. Update the lead's runtime model
and effort in the same workspace/session, verify effective settings, then resume.

Use asynchronous `create_agent` and `send_agent_prompt` with
`notifyOnFinish: true` (also `background: true` for sends). Continue useful
coordination while agents run; use notifications instead of repeatedly polling
running agents. A notification is a status transition, not proof of completion.
Persist through authorized operational issues. Do not create schedules/heartbeats
unless a task needs one and authorization covers it; ordinary active coordination
requires neither.

## Independent review and handoff

Every completed workstream needs independent subagent review with **clean context**,
without the implementer's inherited conversation. Use a fresh Paseo agent with only
the supplied prompt/artifacts, or collaboration spawn with `fork_turns: "none"` and
explicit model/effort. Follow the same model policy. Supply raw requirements, base
ref/revision, branch, exact candidate HEAD, contracts/skills, affected scope and
validation targets. Provide no implementer conclusions or suggested verdict.

Use one proportionate independent review/fix cycle. Worker fixes actionable findings
and reruns affected meaningful checks. After a material fix, rebase or retention-tree
change, obtain the SAME reviewer's compact explicit disposition of the exact new
HEAD/base and actual delta, with renewed checks where needed. Prior approval never
transfers to a different candidate. Orchestrator checks evidence, not implementation.

Retain the complete substantive/final reports, actual check sources, argv/exits,
full diagnostics, failures and required empty streams durably. Verify the complete
expected path set, stored/decoded bytes and hashes against actual source/readback;
checking only included entries cannot reveal omitted required payloads. Preserve
prior payload dictionaries and history. Store meaningful new actual evidence;
reference immutable old notes, sources and evidence by reachable Git revision/blob,
bytes and SHA rather than recursively copying old packs. Keep packaging proportionate;
never shorten reports or broadly filter manifest-required paths.

A metadata-only note/report storage step without candidate/tree/base changes does
not automatically require another reviewer acknowledgement or report-only commit/
review cycle. Worker/orchestrator verifies actual complete expected-set/hash/readback
and returns concrete gaps for correction. Material changed evidence or a concrete
unresolved review condition still requires appropriate SAME-reviewer disposition.

Require a handoff containing:

- Workspace/branch and exact committed HEAD; task/scope and completed TODO items.
- Independent reviewer identity, model/effort, verdict and exact reviewed revision;
  findings, fixes and follow-up disposition, with accessible review evidence.
- Validation commands/results and retained logs/artifacts; distinguish runtime
  diagnostics, unavailable checks and constraints. Never claim unsupported tests.
- Evidence records and downstream prerequisite updates. Completed TODO items are
  removed **with their resolving commits**; do not close tasks missing gated
  acceptance. Partial work leaves explicit actionable remaining tasks.
- Clean Git status, saved editor/source work, unresolved constraints and confirmation
  that writers are quiescent for integration.

Return specific evidence gaps to the worker. Do not perform technical review yourself
to fill them.

## Local integration, then archival

Only integrate/archive within the user's authorized scope. No remote push is implied.
Keep history linear; never create merge commits.

1. Freeze relevant writers and obtain acknowledgments that work is saved and no
   process will mutate candidate or main during integration. Identify main's worktree
   using `git worktree list --porcelain`. Check worker and main status including
   untracked files and absence of in-progress Git operations. Require both clean.
   If dirty or unsaved, preserve everything and coordinate with its owner; never
   reset, clean, stash, overwrite or archive work to bypass preflight.
2. Record current local `refs/heads/main` and delivered worker HEAD. Rebase the worker
   branch onto current local main in the worker worktree. Delegate conflicts,
   resulting code changes, technical review and checks to the worker. Never resolve
   implementation conflicts yourself. Resume with a clean updated handoff, exact new
   HEAD and reviewer/check evidence for the rebased result.
3. Recheck writer freeze, clean status, current main and candidate HEAD. If main moved,
   repeat rebase and evidence reconciliation safely. Verify ancestry with
   `git merge-base --is-ancestor <current-main-head> <delivered-head>` and inspect Git
   topology for a linear, merge-commit-free integration range. Failures return to the
   worker or operational owner; do not force integration.
4. In main's worktree, confirm the checked-out branch is `main`, then integrate the
   exact approved revision with `git merge --ff-only <delivered-head>`. Recheck main
   HEAD/status and verify it contains delivered HEAD with
   `git merge-base --is-ancestor <delivered-head> refs/heads/main`. Verify the recorded
   old-main-to-new-main range is linear with no merge commits. If verification fails,
   preserve the workspace and investigate; do not archive.
5. Record old main, delivered/reviewed HEAD, new main and verification evidence.
   Only after confirmed integration and no uncommitted/unsaved work, archive via
   Paseo `archive_workspace`, never manual directory removal. Archival may remove an
   owned worktree and its agents/terminals: retain handoff/review/log evidence in
   committed records or another durable location before archival.

If authorization covers only worker delivery, report the handoff and leave integration
and archival to the owning orchestrator.

## Worker prompt template

```text
Implement this Fun Things workstream in workspace {id}, worktree {path}, branch
{branch}, based on refs/heads/main at {base_revision}. You own {task/scope}.
Raw requirements/TODO text: {requirements}.
Prerequisites and evidence: {records/revisions}. Gates: {ratification/device/service}.
Budget/stop boundary: {experiment cap}; exclusions: {out_of_scope}.
Writer ownership: {editor/scene/source allocations and serialized access}.
Read AGENTS.md, {applicable docs} and {applicable skills}; preserve their contracts.
Implement, validate with {acceptance targets}, inspect runtime logs, and commit.
Remove completed TODO items with resolving commits and update evidence/downstream
references; leave gated or incomplete acceptance explicit.
You lead this workspace on GPT-6.1-Sol medium/high, chosen for the task. Very simple
subtasks/reviews may use GPT-6-Luna high; other non-specialist delegation uses Sol
medium/high. Use Astra only for necessary bounded visual/spatial/modeling specialist
subagents with an explicit question, output, validation boundary and proportionate
supported effort/budget; return results to you for synthesis/coordination. A mention
of 3D/art/maps does not route whole research/planning, implementation or broad review
to Astra. Cost-aware routing preserves independent review and needed validation.
Discover Paseo profile/provider/model/effort IDs; no silent mismatch or ultra default.
Obtain independent clean-context subagent review using the reviewer template in
.agents/skills/paseo-orchestrator/SKILL.md. Supply raw requirements and artifacts,
not your conclusions. Fix actionable findings, rerun meaningful checks and obtain
appropriate follow-up disposition for exact final HEAD. Never merge/archive/push.
Use one proportionate review/fix cycle; after material fix/rebase/retention-tree change,
ask the SAME reviewer for compact exact-new-HEAD/base delta disposition. Preserve full
reports/check sources/argv/exits/diagnostics/failures/required empty streams and prior
payloads; verify complete expected sets and actual stored/decoded hashes/readback.
Use immutable reachable old Git refs instead of recursive note/source copies. A
metadata-only storage step with unchanged candidate/tree/base creates no automatic
second acknowledgement or report-only commit/review cycle; return concrete gaps.
Stop at blocked visual/device/access budgets; unrelated ready work can proceed with
named writer leases and review serialization. No repeated unchanged experiments.
Return exact committed HEAD, scope/TODO status, reviewer identity/model/effort,
verdict/reviewed revision and evidence, fixes, commands/results/logs, constraints,
clean Git status and saved/quiescent writer confirmation. Retain evidence durably.
Use asynchronous delegation with notifyOnFinish true; await notifications.
```

## Reviewer prompt template

```text
Independently review {task} with clean context. Do not inherit the implementer's
conversation. Requirements: {raw_requirements}. Base: {ref} at {base_revision}.
Candidate: {branch} at {exact_HEAD}; affected scope: {paths/subsystems}.
Read AGENTS.md, {contracts} and {review/domain skills}. Validation targets:
{acceptance criteria, required checks and gates}. Inspect evidence independently;
distinguish unavailable checks from verified outcomes. Do not make implementation
edits or live service/device mutations unless separately tasked; preserve unsaved
work and coordinate exclusive editor access. Use isolated checks where needed.
Return evidence-based findings with severity, file locations and violated contracts,
exact reviewed revision, checks/log evidence and verdict/constraints. Do not accept
unsupported test claims or close unmet gates. Follow model policy in
.agents/skills/paseo-orchestrator/SKILL.md: workspace leads use Sol 6.1 medium/high;
very simple delegated reviews/subtasks may use Luna 6 high. Broad reviews use Sol;
Astra handles only necessary bounded visual/spatial/modeling specialist subagents,
with explicit question/output/validation and proportionate supported effort/budget,
returning results to the Sol lead. A 3D/art/map mention alone does not justify Astra.
Discover fitting role/scope profiles and supported model/effort IDs; no silent
mismatch or ultra default. Cost-aware routing preserves review/validation obligations.
Retain complete substantive/final reports and meaningful actual source/argv/exit/raw
streams/diagnostics/failures/required empty streams, with explicit expected sets and
hashes. Use reachable immutable old Git refs without recursive historical copies.
After material fix/rebase/retention-tree change, give compact exact-new-HEAD/base
delta disposition as the SAME reviewer. Metadata-only storage with unchanged
candidate/tree/base creates no automatic acknowledgement/report-only review cycle;
identify concrete missing expected payloads or material evidence changes instead.
Blocked visual/device/access gates preserve their stop boundary and do not block
unrelated ready work; named writer leases and conflicting-review serialization apply.
No merge/archive/push.
```
