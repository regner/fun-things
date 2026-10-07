---
name: gdscript-review
description: Review project-owned GDScript changes in Fun Things for gameplay correctness, multiplayer contracts, saved compatibility, style, and meaningful validation. Use for requested code reviews or focused subsystem audits; preserve vendor addon contracts.
---

# Project GDScript review

Review the requested diff or subsystem and its affected contracts. Produce actionable,
evidence-based findings; a review request alone does not authorize fixes. Keep scope
local and prefer the smallest correction that meets the current requirement.

## Establish the contract

Read [repository guidance](../../../AGENTS.md) and
[development](../../../docs/development.md). Consult
[the ratified product brief](../../../docs/design.md) for gameplay requirements,
[multiplayer](../../../docs/multiplayer.md) for session/replication changes, and
[assets](../../../docs/assets.md) for collision, identity or authored-scene changes.
Resolve these links relative to this skill directory.

Look for `docs/architecture.md`, `docs/scene-structure.md`, and
`docs/api-contracts.md` at the repository root. Read relevant sections when present;
if absent, report the missing contract coverage and use existing guidance plus
implementation evidence. Do not invent signatures, owners or measured budgets from
the illustrative plans in [TODO.md](../../../TODO.md). Current ratified requirements
take precedence over historical examples or proposals; surface unresolved conflicts
rather than quietly choosing a new rule.

Establish the review base and changed paths. Separate project-owned code from vendor
addons; inspect vendor boundaries as dependencies without applying project formatting
or proposing unrelated rewrites. Follow the changed state to its owner, callers,
signal listeners, RPC routes, resources, saved scenes and tests. Search for competing
implementations before recommending another rule or abstraction. Account for code
that is present but not exercised by the main scene.

## Trace behavior across boundaries

Use the relevant lenses below. Mark an unimplemented feature outside scope rather
than demanding every planned subsystem in a small change.

- **Ownership and simplicity:** identify the writer of each changed rule, transition
  and replicated field. Trace input collection into simulation, replication and
  presentation; HUDs and effects consume state. Check that standalone, host and
  prediction use equivalent rules and tuning owned by the responsible component.
  Flag duplicate rules, competing writers or unjustified machinery with a concrete
  consequence, not a speculative redesign.
- **Authority and admission:** follow remotely callable paths from the actual RPC
  sender to admitted session/entity/control ownership before mutation. Check exact
  types, finite numbers, allowed ranges and sequence/revision freshness. Clients
  submit intent; the authoritative process owns outcomes. Distinguish scene `owner`,
  driver/input ownership and Godot multiplayer authority. Inspect setup before tree
  entry, including child `_ready` and callbacks, so replicas cannot mutate gameplay.
  Host-local input should pass equivalent validation.
- **Lifecycle and ordering:** walk join, baseline hydration, control transfer,
  death/reset/respawn, disconnect, cancellation, teardown and retry as applicable.
  Required collision/lifecycle state precedes dependent movement or prediction.
  Commands, components, collision, presentation and histories must be consistent
  before observers receive completion. Check stale asynchronous callbacks and
  session/entity/component revisions; movement must not undo durable state.
- **Prediction and effects:** trace correction and bounded replay through the shared
  simulation path. Replay cannot apply authoritative damage, pickups or spawning, or
  repeat sounds/VFX. Baselines restore current state without replaying past events.
  Check event identity/deduplication and correction recovery when history is exhausted.
- **Bounded work:** inspect packet/batch sizes, request rates, queue/history lengths,
  per-tick work, timeouts, population/effect limits and cleanup. Reject invalid input
  before enqueueing or mutating; client elapsed time cannot grant simulation steps.
  Use the project's actual limits when defined and identify missing bounds without
  importing VCS's example numbers as requirements.
- **Compatibility and saved state:** compare public signatures, Inspector exports,
  serialized names, node paths, signals, resource/dependency UIDs, `.uid` sidecars and
  inherited overrides with their callers and saved values. Require a coordinated
  migration for intentional changes. Runtime code must preserve authored placement
  and linked imports. Collision changes need movement/query/network evidence.
- **Style and maintainability:** consult [gdstyle configuration](../../../gdstyle.toml)
  and [its pin](../../../.gdstyle-version). Manually check the repository's purpose
  comments, annotation attachment, two empty lines between functions, logical-block
  and export-group spacing, type hints, tabs/LF and 100-character target. Check named
  significant values, useful rationale and lint directives. Keep style findings
  distinct from behavior bugs and avoid behavior changes disguised as cleanup.

## Assess validation honestly

Discover checks from [mise.toml](../../../mise.toml), repository tools and affected
tests; do not assume planned task names are executable. Run appropriate available
read-only checks. Follow the repository editor workflow if verification requires
editor-managed mutations; preserve unsaved work and report limitations before a
direct-file fallback.

Use independent expected outcomes through production APIs, including negative
admission/stale-state cases when relevant. A test that repeats the implementation
formula or bypasses the admission path cannot prove that contract. Name the smallest
regression case for each substantive finding. Compilation, import, a screenshot and
a successful exit status establish different things; review runtime logs as well.
Only actual separate-process checks establish network behavior, and ENet evidence
does not certify Steam. Report absent tooling, tests, fixtures or contract documents
as validation gaps, separately from observed bugs. Do not claim checks ran when they
were unavailable or turn an environment failure into a gameplay defect.

## Report findings

Lead with the findings in descending severity. For each, provide:

- **Severity:** P0 release-blocking/catastrophic, P1 high-impact correctness or trust
  boundary failure, P2 other actionable bug/contract break, P3 low-impact style or
  maintenance issue. Explain context rather than promoting every concern to P0.
- **Location:** repository-relative path and the smallest useful line span; include
  caller/saved-data locations when they establish the failure.
- **Evidence and impact:** the concrete trigger, execution/data path and observable
  consequence; distinguish demonstrated behavior from static inference or uncertainty.
- **Fix and verification:** the smallest owner-level correction and an independent
  acceptance/regression case. Avoid merging unrelated problems into one finding.

End with checks actually run and their results, missing coverage and material open
questions. If no actionable issues were found, say so with the inspected scope and
limits; lack of runnable tests does not establish correctness.
