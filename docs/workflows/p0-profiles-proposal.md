# P0-PROFILES requirements and proposed bundles

7 October 2026. **PROPOSED; documentation only; installation and representative
launch validation DEFERRED.** Worker implements directly on Sol 6.1 high in
`wks_674b9848da113179`, branch `p0-profiles-requirements-proposal`, starting local
main `11a4486ae6e912387ef4e2ffbce3b138c3b45f28`. This is one focused requirements/
proposal pass, not a new checkpoint. Examined checkpoint watermark remains
`35adb47042fe6b27c1653d38636f5eaf7d47578b`; research/rebase cannot advance it.

Raw user: “We should add a task to create paseo profiles. We shouldn't do it right
away though. We should do it in a little bit so that we can review recent sessions
to help identify our requirements. We should add a periodic review of profiles to
the orchestrator as well.” Later clarification: “Sol leads workspaces; Astra
handles targeted specialist subtasks.” Current policy is the
[orchestrator model policy](../../.agents/skills/paseo-orchestrator/SKILL.md#model-policy-workers-subagents-and-reviewers).

The [third assessment](../reviews/plan-check-2026-10-07-03.md#profile-assessment),
accepted checkpoint `814ac3a`, supplies readiness from accepted additional S02
implementation and independent code/spatial reviews. Earlier
[first](../reviews/plan-check-2026-10-07.md#profile-baseline) and
[second](../reviews/plan-check-2026-10-07-02.md#profile-assessment) assessments were
insufficient; their historical decisions remain intact. Accepted
[DOC4](../reviews/p0-doc4.md) at `11a4486` supplements bounded Sol medium work.
An empty inventory or elapsed time supplies neither readiness nor capability proof.

## Delivery rebase supplement

Accepted local main advanced from the starting base to
`ae48eb3dd498075bdd854119c5d124a8251dbbb1` before integration. The saved proposal
was rebased onto it without conflicts. Its [S03-R bounded technical record](../spikes/s03-r.md)
and [scoped independent review](../reviews/s03-r-b87f889.md) are accepted main
content; full S03-R, drawable/visible response, prediction, feel, Steam/Deck and
production gates remain open. All S03-R TODO/contracts/source/evidence are preserved.
The session sample below remains historical at its recorded capture/assessment;
no new S03-R metrics are incorporated as profile capability or launch validation.
The original [pre-rebase exact-final receipt](p0-profiles-final-0f10dbb.md) remains
historical; the same reviewer must explicitly dispose of the exact new HEAD.
Checkpoint watermark stays `35adb470`; this is scoped rebase reconciliation only.

## Requirements from the sample

[Evidence and coverage](p0-profiles-evidence.md) maps exact sessions and accepted
revisions to the following requirements. The root-provided sample is targeted;
S02 lead covers only recent 220 of 690 activities. No global history survey,
new editor/service inspection, or adoption of pending S03-R outcomes occurred.

- Keep a small reusable set by actual settings/scope, rather than one bundle per
  task title. Leads and non-specialist reviewers can share Sol settings; their
  prompts still establish different authority and clean-context requirements.
- Sol 6.1 medium/high leads workspaces, choosing effort by interacting scope and
  uncertainty. Workers implement directly; upstream root alone is orchestration-only.
  Avoid another coordinator or implementation lead layer. Sol medium/high handles
  broad/non-specialist delegation and review. Historical Astra leads do not establish
  current lead routing; Luna is confined to very simple delegated work/reviews.
- Use Astra only for a **necessary targeted visual/spatial/modeling specialist
  subagent** with a question, output, validation boundary and proportionate effort/
  task budget. Return findings to Sol for synthesis. Ordinary research, source/code,
  broad review, planning and orchestration remain Sol work even when maps/art appear.
- Require raw requirements, exact candidate/base and independent evidence for fresh
  clean-context review. A profile is launch configuration; notes are guidance, not
  an enforced role, system prompt, sandbox or resource lease.
- Preserve approvals and least necessary task access. An isolated doc worker needs
  worktree writes and temporary static checks; an isolated reviewer needs reads and
  scratch evidence, no authoring lease. Engine/socket/display/source work requires
  task-specific authorization and serialized ownership. Never make full access a
  default, invent tool grants or silently substitute a model/effort.
- Distinguish declared/effective metadata from demonstrated task capability. Retain
  output/log evidence and explicit missing proofs. No ultra or paid fast default;
  this sample contains no comparable cost/latency benchmark.

## Four proposed bundles

Exact inert [mutable patch body](p0-profiles-evidence/proposed.patch.json) includes
complete notes with use, exclusions, tradeoffs and role routing. All use provider
`codex`, mode `auto-review`, `plan_mode: false`. These values were discovered, not
inferred from labels. Roles share a bundle when settings match.

| Proposed ID | Model / effort | Use and demonstrated reason | Boundary / tradeoff |
| --- | --- | --- | --- |
| `fun-things-sol-medium` | `gpt-6.1-sol` / `medium` | Bounded known-contract workspace lead, delegated subtask or independent review; DOC4 six-guide correction/review. | Move uncertain or interacting code/contracts to high; no demonstrated speed/cost guarantee. |
| `fun-things-sol-high` | `gpt-6.1-sol` / `high` | Broader implementation, evidence/contracts/research, non-specialist review/delegation; S02 code, S07 research/review, DOC1/2 and this requirements stage. | Greater reasoning expenditure by scope; no extra permissions. Sol receives specialist synthesis. |
| `fun-things-luna-simple` | `gpt-6-luna` / `high` | Only very simple delegated corrections/reviews with objective evidence, demonstrated by DOC3 reviewer. `fast_mode: false`. | Never workspace lead, broad planning/research/code/review/orchestration or spatial work; unexpected scope returns to Sol. |
| `fun-things-astra-spatial` | `gpt-6-astra` / `high` | Necessary bounded spatial/modeling/visual subagent; S02 source/camera/placement review found target/tower overlap. `fast_mode: false`. | Explicitly excludes workspace/implementation leadership and broad planning/research/code/review/orchestration. Expense requires a named specialist question, not an art/map title. |

Astra high matches the demonstrated specialist session, not an automatic maximum.
For example: “At this exact S02 candidate, is TargetBlocked outside solid world
collision and readable from the blocked/clear camera poses?” Require annotated
captures, dimensions/source identity and findings; validate placement/query evidence
within the exact fixture, while human feel/native focus/Deck remain outside scope.
Start with one focused inspection and one affected-fix follow-up; stop/report missing
evidence. Sol rescoping is required for additional questions or a larger pass.
Budget is a task/prompt boundary: **the profile schema exposes no token/spend/time
cap**. Another supported effort needs explicit task justification and rediscovery;
no silent fallback or ultra. No Astra agent is used for this proposal or its review.

[Fresh discovery](p0-profiles-evidence/discovery.json) found zero profiles, so there
are no existing notes to read/update/retire. Codex is available; other discovered
providers are unavailable. Sol medium/high and Luna/Astra high are supported IDs.
`inspect_provider` exposes only plan mode for Sol 6.1, and plan/fast toggles for
Luna/Astra. Fast off avoids an unproved premium; plan off permits the authorized
worker to deliver docs/code rather than remaining planning-only. The schema accepts
arbitrary feature values, but this proposal uses only discovered feature IDs.
Metadata establishes support declarations only; all four bundles remain unlaunched.

## What profiles cannot solve

| Observed gap | Owner / separate required action |
| --- | --- |
| Project MCP authentication, stale endpoints/disconnection, unavailable Blender MCP | Discover tools and actual project state; resolve within a separately authorized operation. No credentials, servers, plugins or preapprovals in bundles. |
| Sandbox socket/display restrictions; host PID/network namespace differs from sandbox; later genuine editor exit | Verify at the appropriate authorized boundary. A missing sandbox PID cannot establish host exit; a mode label cannot grant host visibility or local-network access. Request only needed escalation, retain failed/successful receipts. |
| Shared Godot/Blender ownership and saved-scene synchronization | Root assigns one writer/lease; preserve unsaved work and save/refresh/reopen through existing workflow. Worktrees/profiles do not isolate the editor. Current S03-R lease is untouched. |
| Independent review / redundant coordination layers | Fresh context plus raw requirements and exact revision; direct implementation worker and scoped reviewers. Notes cannot force context isolation or erase inherited bias. |
| Unavailable Deck devices, distinct Steam accounts/routes, inaccessible graphical windows/human playtesting | Keep corresponding tests deferred/open; no renewed facility request or capability claim from viewport size, captures, IDs, metadata or synthetic events. |

Six-block M1, full Steam/Deck LCD/OLED/native 1280×800/60 FPS, physical input,
OS-focus, feel/readability, P0-GATE and production gates remain unchanged. S02 is a
technical fixture with current native focus incomplete; S07 is research/method only.
Pending S03-R code/measurements/prediction/visible response are not accepted here.

## Later authorized installation and validation

[Installed schema/source receipt](p0-profiles-evidence/schema-source.json) records
Paseo desktop `0.10.3` and exact packaged source hashes/excerpts. `AgentProfileSchema`
requires string `id`, `name`, `provider`; supports optional `model`, `modeId`,
`thinkingOptionId`, `featureValues`, `notes`, `icon`, `color`. There is deliberately
no system prompt; unknown passthrough fields confer no permission/tool behavior.
Omit cosmetics and unsupported custom grants. No profile-install MCP tool was found;
`list_profiles` is read-only and `create_agent` has no profile parameter.

The supported **later** API is connected `DaemonClient.patchDaemonConfig(patch)`;
wire message `{type: "set_daemon_config_request", requestId, config: patch}`.
Our JSON is only `patch = {agentProfiles: [...]}`, not a whole daemon configuration.
It maps to `daemon.agentProfiles` in `/home/regner/.paseo/config.json` under this
local Paseo home, **not** repository `paseo.json`, Codex config or a new profile file.
The store replaces this entire array and persists through its config store; use
Paseo's human configuration UI/connected client, preserving all other fields.
No supported `paseo profile install` command is established; CLI is absent on this
worker PATH. No direct-config write, connected client call, restart or installation
script is performed or shipped. Later re-resolve home/version/schema/API before use.

1. Root presents the concrete reviewed proposal to the user for the later explicit
   configuration decision. Then assign one configuration owner; re-read every live
   profile note, back up only the affected inventory safely, and re-discover provider/
   model/effort/mode/features and effective provider overrides. Halt if required IDs
   are unavailable or mode resolves to excess access; report, never silently fall back.
2. Reconcile any nonempty inventory by stable IDs/notes. Review the exact resulting
   array before one authorized patch; avoid clobbering unrelated profiles. Retain
   previous array for a scoped rollback through the same API. Read back with
   `list_profiles`; compare IDs, settings and complete notes. Do not alter provider,
   tool policy, MCP, sandbox roots, network, accounts or services as part of this patch.
3. Materialize each bundle in a later authorized `create_agent` call: `provider`
   becomes `codex/<model>`; copy `modeId` and `thinkingOptionId` into `settings`,
   `featureValues` into `settings.features`. Add task-specific raw prompt,
   `workspaceId` and `notifyOnFinish: true`; **no `profile` field**. A Sol workspace
   worker implements directly; spawn only the necessary delegated role. New task
   workspaces follow the existing worktree/local-main workflow, no extra coordinator.
4. Run bounded safe representative cases separately: Sol medium lead/review of a
   small known-evidence docs correction; Sol high implementation/technical review
   using an accepted isolated fixture; Luna high delegated localized link/claim
   review; Astra high necessary camera/placement/source specialist question under a
   Sol lead, preferably using existing captures/sources before any shared editor lease.
   Each case records requested and effective provider/model/effort/mode/features,
   role/prompt, output and independent expectations, retained logs, approval behavior
   and limits. Sol lead/reviewer role differences still need prompt/context checks
   although they share settings. Avoid launching extra title variants.
5. Verify effective `workspace-write`, `on-request`, `auto_review` and actual allowed
   roots/network/tool boundaries against overrides, not just mode metadata. Use a
   harmless isolated denied/outside-scope canary only if later explicitly authorized;
   approval machinery must remain active. Reviewers produce scratch reports without
   candidate edits, and specialists return scoped synthesis to Sol. Test failures or
   unavailable environments leave the corresponding capability unproved; retain
   receipts and a bounded follow-up. No real account/device/service mutation needed.
6. Obtain independent exact-final disposition after fixes. Record final inventory,
   launch outcomes, unsupported cases, rollback/retirement criteria and next revisit
   in the open P0-PROFILES task's resolving change. Only then consider closing the
   full task; configuration/readback alone is insufficient. Stop owned checks,
   save/quiesce writers and return all leases through existing orchestration.

Periodic review already belongs to the
[checkpoint workflow](../../.agents/skills/paseo-orchestrator/SKILL.md#periodic-plan-and-documentation-checkpoint).
No skill redesign, schedule or heartbeat is needed. Next revisit: normal checkpoint
after **accepted post-policy S03-R implementation and another necessary specialist
session**, or earlier meaningful provider/role/permission/feature drift, and always
before authorized installation. Compare both lead and specialist routes, recurring
friction, notes, effective settings and actual outcomes; create only scoped updates/
retirements. A later main rebase does not manufacture sample coverage or readiness.

## Validation and delivery

Static checks only: supported schema parse, JSON/unique IDs, source hashes, local
links/anchors, scoped TODO delta/history preservation, whitespace and linear Git
ancestry. [Checker](p0-profiles-evidence/check.py) and retained receipts accompany
review. No engine/gameplay/network/export/display/device tests, representative
profile launches, configuration/API writes, schedules or service changes occurred.
Fresh clean-context reviewer `/root/p0_profiles_review`, Sol 6.1 high, **ACCEPTED**
`ed4550d75eddc12f6b64abc9540226d172b46c87` with no actionable findings or fixes.
The [complete report](p0-profiles-review.md) is retained verbatim; the
[worker receipt](p0-profiles-evidence/worker-checks-ed4550d.txt) records actual static
checks at that substantive revision. This retention/TODO-status continuation still
requires explicit exact-final-HEAD disposition, retained in local
`refs/notes/paseo-orchestration` on the delivered HEAD before integration/archive.
P0-PROFILES remains open for the later authorized workflow above.
