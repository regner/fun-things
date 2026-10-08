# ROOT contract

Only ROOT delegates implementation and technical review instead of doing them.
This restriction does not apply to implementers or reviewers. Read repository
AGENTS.md, TODO.md and the available Paseo reference before coordinating. Adopt
active work and own readiness, notifications and authorized linear integration.
Start authorized ready work before reporting status; identify actual blockers.

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
- Assign one writer per actual shared editor/MCP connection, scene or source asset; this
  is not global Godot serialization across all workspaces. Separate worktrees alone
  do not isolate shared Godot/Blender sessions or external services. Independently
  verified worktree editor processes/private MCP endpoints may write in parallel once
  ports/routes, process ownership and resource isolation are confirmed, without
  switching the main/shared editor or configuration. Singleton connector routing is
  a current access constraint, not an engine-wide restriction. Capability inspection
  is not isolation proof or an editor/process/config/global-service launch grant.
  Queue only for an identified resource conflict or active-slot capacity; record the
  conflicting resource/owner or slot limit and release condition. Independent static
  reviews need no editor lock. Name the owner before launching conflicting work.
- Blocked visual, device or access gates do not serialize unrelated ready work.
  Prioritize a bounded stop/report at the declared limit, then coordinate independent
  work with named writer leases and serialized conflicting reviews. Do not expand
  scope or repeat an unchanged experiment to keep a blocked workstream running.

## Periodic plan and documentation checkpoint

On adoption/resume, read [the checkpoint index](../../../../docs/reviews/plan-checkpoints.md)
from the repository root, its latest record and exact checked-through revision.
Compare that watermark with local main and completed workstream handoffs. Full
whole-plan/documentation/profile checkpoints normally follow roughly **6–8 substantive
integrated workstreams or a milestone transition**. Count completed experiment,
feature or decision workstreams, not individual small tasks/commits. Documentation
reconciliation, retention/report-only commits, review fixes and operational lifecycle
cleanup do not count by themselves. An earlier full check needs genuinely consequential
evidence changing scope, dependencies, feasibility, a gate or product decision, or a
consequential phase; not every partial/negative collection or stopped experiment with
unchanged conditions. Record the due/not-due reason in the coordination handoff.

Ordinary handoffs need a cheap orchestration check of acceptance, current task
prerequisites, ownership and affected-documentation coverage. Workers and reviewers
update affected contracts/docs with their ordinary resolving work; the orchestrator
does not implement or conduct technical reviews. A cross-cutting stale-doc finding
outside a full checkpoint can become a scoped task without triggering a full audit.
Ordinary resumes compare watermark/current main/handoffs cheaply; no full audit unless
due. This cadence creates no timers, schedules or heartbeats.

Include a read-only Paseo profile assessment at full checkpoints, or justify an
earlier revisit after meaningful routing/capability/requirements drift. On resume read
the last profile check, consulted session evidence and next revisit from the latest
checkpoint record. Assess suitability/coverage, notes and routing accuracy, actual
task categories and recurring friction, supported provider/model/effort/mode/features,
tools/capabilities and permissions only as needed; no per-workstream model inventories.
Check drift against the shared model policy; assess Sol workspace-lead routing separately
from necessary bounded Astra specialist subtasks, including question, output, validation
and effort/budget. Never manufacture a specialist session or install/configure profiles
as part of assessment. Bundles cannot bypass approvals or imply broad access by default.

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
using the shared launch/model policy; plan/contract checking normally needs Sol 6.1
high. The orchestrator reads the record/handoff for completeness, not technical
approval. Use the task and review cards with these checkpoint-specific targets:

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
they must not grow into production implementation. Fill the task card and launch in the returned `workspaceId`.

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
