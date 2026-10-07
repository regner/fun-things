---
name: paseo-orchestrator
description: Orchestrate Fun Things workstreams through Paseo, adopting active work, assigning TODO tasks to workers, collecting independent reviews, and integrating reviewed commits into local main. Use for project coordination rather than implementation or technical review.
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

Call Paseo `list_profiles` and read every profile's notes. Materialize a fitting
profile's provider/model, mode, thinking option and features into the launch call;
`create_agent` has no profile parameter. If none fits, say so and discover provider,
model and effort IDs with `list_providers`, `list_models` and, where needed,
`inspect_provider`. Do not guess IDs or silently accept a mismatched profile.

- Very simple tasks: GPT-6-Luna, **high**.
- More demanding tasks: GPT-6.1-Sol, **medium or high**, chosen for scope.
- Visual design, 3D modeling, spatial work and similarly demanding specialist work:
  escalate to GPT-6-Astra with an explicit suitable supported effort.
- No automatic ultra default. Carry this policy into every delegation prompt,
  including the worker's reviewers and other subagents. If a required model/effort
  is unavailable, report the limitation and request the missing choice instead of
  silently falling back. Adopted agents must honor the policy for subsequent work
  and delegation; coordinate any necessary model change safely.

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

Worker fixes actionable findings, reruns meaningful checks, and requests follow-up
review where changes warrant it. Review must cover the delivered revision: after
changes, obtain the reviewer's explicit disposition of the new revision and any
needed renewed checks. Orchestrator checks evidence, not implementation.

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
All your subagents/reviewers use GPT-6-Luna high for very simple work,
GPT-6.1-Sol medium/high for demanding work, GPT-6-Astra for visual/3D/spatial work.
Discover Paseo profile/provider/model/effort IDs; no silent mismatch or ultra default.
Obtain independent clean-context subagent review using the reviewer template in
.agents/skills/paseo-orchestrator/SKILL.md. Supply raw requirements and artifacts,
not your conclusions. Fix actionable findings, rerun meaningful checks and obtain
appropriate follow-up disposition for exact final HEAD. Never merge/archive/push.
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
.agents/skills/paseo-orchestrator/SKILL.md for any subagents. No merge/archive/push.
```
