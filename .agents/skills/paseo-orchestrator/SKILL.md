---
name: paseo-orchestrator
description: Coordinate Fun Things workstreams through Paseo, with bounded assignments, independent review, periodic plan checks and authorized linear integration. Use for project coordination rather than implementation or technical review.
---

# Paseo orchestrator

Choose the contract for the assigned role. ROOT's orchestration-only restriction
belongs to ROOT; a worker implements directly and a reviewer reviews directly.
No role acquires merge, archive, push, access or scope authority from this skill.

- ROOT: read [root contract](references/root.md) for adoption, checkpoint and integration.
- Implementer: read [implementer contract](references/implementer.md).
- Reviewer: read [reviewer contract](references/reviewer.md).

Use the [readable cards](references/cards.md) to assign work and communicate changes.
Pass immutable contract/evidence revisions and complete raw requirements separately;
do not paste procedural history into each prompt. Critical scope, acceptance,
resource ownership, budget and remaining gates stay explicit in the card.

Keep one compact coordination record for live ownership, workspace/base/candidate,
dependencies, review status, resource conflicts and next action. TODO items describe
outcome, dependency, owner role, remaining observable acceptance and evidence link.
Keep historical facts in dated records; a planned test or finished turn is no proof.

## Recovery and concurrency

A task's recovery envelope declares total effort/time and attempt limits across all
phases, owned resources, preservation duties, recoverable mistakes, phase-specific
acceptance and escalation triggers. Correct ordinary owned request/supervisor errors
within that authorized envelope, retain failures and report budget consumed. Do not
repeat unchanged experiments. A failed phase stays failed; a distinct authorized
phase may establish its own result without implying full acceptance.

Escalate new shared resources, access or scope, risk to saved/unsaved work, uncertain
identity/isolation, or exhausted total budgets. Missing authority remains a blocker.
This prospective rule does not waive historical STOPs or authorize current engine
retries. Resource discovery alone grants no process/editor/config/service mutation.

Locks protect actual shared resources, not every editor or reviewer. Independent
worktrees with verified private process/endpoint/project ownership can work in
parallel; worktrees alone do not prove isolation. Queue only for an identified
conflict or active-slot capacity, naming owner, blocker and release condition. Start
ready authorized work; use completion notifications and meaningful status changes.

### Model policy: workers, subagents and reviewers

For a new launch, use a current launch receipt supplied by ROOT or perform discovery:
call Paseo `list_profiles` and read every profile's notes. Match both task scope
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

A receipt records discovery source/time, profile choice (including none), verified
provider/model/effort/mode/features, workspace/base and parent ID/notification route.
An implementer need not repeat discovery already supplied for its launch. Recheck
for a new launch without a current matching receipt or meaningful capability/settings
drift. Verify effective launch settings; receipts never bypass approval.

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
and reruns affected meaningful checks. After a material fix, rebase or material
retention-tree change, obtain the SAME reviewer's compact explicit disposition of the exact new
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

ROOT returns specific evidence gaps to the worker; it does not perform technical
review to fill them.

## Periodic plan and documentation checkpoint

ROOT uses the [checkpoint contract](references/root.md#periodic-plan-and-documentation-checkpoint)
for cadence, profile assessment and exact examined watermarks. This routing section
preserves existing contract links; implementers follow their assigned task scope.

## Audit provenance

The [independent audit](../../../docs/workflows/orchestration-workflow-audit.md) is
retained verbatim. Its [public evidence ledger](../../../docs/workflows/orchestration-workflow-audit-evidence.json)
records source locators, snapshot limits and report integrity. Historical grants and
verdicts remain historical; the rules above govern prospective assignments.
