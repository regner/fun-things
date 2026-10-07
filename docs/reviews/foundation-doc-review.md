# Independent review — P0-DOC1 and P0-DOC2

Verdict: **ACCEPT** for the requested documentation reconciliation. No actionable findings (P1/P2/P3), violated acceptance criteria, or required fixes were found in the exact candidate below. This verdict closes documentation work only; it does not supply new technical, gameplay, asset, Steam, hardware, or production acceptance.

## Reviewed identity and scope

- Reviewer: fresh Codex reviewer, requested GPT-6.1-Sol / high, auto-review mode; no profile configured. No subagents used.
- Worktree: `/home/regner/.paseo/worktrees/0u71f39f/foundation-doc-reconciliation`.
- Branch: `foundation-doc-reconciliation`.
- Base: local `refs/heads/main` at `8f512779356464b33de06138e18c962d12bfab10`.
- Exact reviewed candidate: `24c878572a2edc478ff6aeeda9ac95298cdb17a1`.
- Separate resolving commits: `deb8d081e8223ee0abb1467e8615d539dc7affc3` (P0-DOC1), then `24c878572a2edc478ff6aeeda9ac95298cdb17a1` (P0-DOC2).
- At initial and final checks, the worktree was clean, HEAD matched the candidate, and local main matched the supplied base. Main is an ancestor of candidate; the two-commit range contains no merge commits. The candidate therefore already includes current local main. No rebase or other Git mutation was performed by the reviewer.

The review began with the raw user requirements, `AGENTS.md`, and `.agents/skills/paseo-orchestrator/SKILL.md`. It independently read the entire current TODO, the raw P0-DOC task blocks from `git show <base>:TODO.md`, checkpoint index/documentation findings, all six named affected guides, both new completion records and all four `foundation-doc-evidence/` files. It also read canonical design/development/multiplayer/scene contracts and accepted S01/S03 records, then inspected retained JSON evidence and relevant source assertions. No implementer conversation or suggested verdict was inherited.

## Findings

None. Severity, defect location, and violated criterion are not applicable. The following acceptance assessment records the locations and evidence supporting that disposition.

## Acceptance assessment

| Requirement | Independent assessment and locations |
| --- | --- |
| P0-DOC1: existing compiler/resource tooling versus future CI/production coverage | `docs/guidance-sources.md:48` enumerates actual fixture tooling and keeps manual purpose-comment/spacing review, preserving formatter wrapper, CI and broader production coverage with M1-D1. All seven task names resolve to the inspected `mise.toml` commands. `tools/script_checks.py` confirms explicit compilation of each discovered owned script in a fresh dependency mirror, including unused scripts, with named vendor/hidden/`.gdignore` exclusions. No import-only or whole-project compatibility claim was introduced. |
| P0-DOC1: focused source fingerprints/reexport tooling | `docs/assets.md:101` correctly identifies the two committed Blender sources, scratch export validation, default byte comparison, fingerprint output and explicit `--install` route. `tools/s01/reexport.py` validates both outputs before installation and copies only GLBs, preserving import sidecars. `tools/check.py` and `tools/s01/clean_import.py` substantiate the focused source/resource/identity and isolated failure-probe scopes. Manual catalogue and future general automation remain explicit. |
| P0-DOC1: historical observations and current-status supplements | `docs/reviews/p0-06.md:103` and `docs/spikes/s01.md:220` link subsequent combined acceptance and final result/compilation records. Both base documents remain exact byte prefixes of their candidate versions: original dry-run/experiment observations were preserved. The S01 supplement explicitly reconciles the historical three-script count and missing runner with current ten-script evidence. |
| P0-DOC1: rejected route and unproved limits | The rejected direct imported-child identity churn, accepted wrapper-level appearance route, full-project plugin/editor diagnostics, unchanged engine pin, and unproved Steam/Deck/gameplay/production-art cases remain explicit in S01 and its supplement, P0-06, and the asset guide. Focused clean import and ENet success are not generalized to those cases. |
| P0-DOC2: active proof and production acceptance owners | `docs/api-contracts.md:515` separates runtime ownership, accepted minimum evidence, bounded spike decisions and full M1 implementation/acceptance. Every revised limit row and all 18 contract-test rows (`docs/api-contracts.md:582`) were checked against S03 omissions and the entire TODO. Completed S03 is evidence, not an owner of future work. Full admission/failure/rollback, native cleanup, resync, lifecycle/collision, batching/actions, rate/flood/stall, tombstone/future-state and capacity cases have active downstream owners. |
| P0-DOC2: reset ownership | The limit row at `docs/api-contracts.md:537`, test row at `docs/api-contracts.md:596`, and architecture summary at `docs/architecture.md:200` map reset to M1-A2 coordinator, M1-B3 combat/seats/rockets/chains/wreck work, M1-C3 population and M1-D3 driving/firing/joining acceptance. These match the existing active task text. S03 explicitly implements no reset. |
| P0-DOC2: 12-car bounded feasibility versus sustained load | `docs/api-contracts.md:543`, `docs/api-contracts.md:594` and `docs/architecture.md:206` assign bounded 12-car chain feasibility despite eight visual slots to S05, production chain implementation to M1-B3 and sustained capacity/adverse load to M1-D3. TODO S05 retains this bounded extension; sustained/joining cases remain production work. |
| P0-DOC2: settled subset-refresh result and historical review | `docs/architecture.md:181` labels the original advisor's pending proof as historical; `docs/architecture.md:187` links the subsequent native reordering/loss result and describes only the settled minimum. Production codecs/capacity/adverse-profile convergence remain M1-A2/D3; passive replica-body/physics-phase decisions remain S04 followed by M1-B1/D3. |
| Preserve provisional values, policy and gates | All limit name/value/scope columns are unchanged from base. The diff contains no API shape or code change. Canonical brief policies remain intact, including parked abandoned cars, retained peers on reset, shared standalone rules, one authoritative gameplay writer, seated-fire policy still requiring S04/P0-GATE confirmation, and physical Deck/real Steam requirements. Every other active task block is byte-identical except P0-GATE's intended prerequisite replacement; its acceptance text is unchanged. P0-PROFILES stays DEFERRED/ineligible. S02/S03-S/S03-R/S04/S05/S06/S07/S08 and P0-GATE remain open. |
| Closure, downstream references, history and scope | Each P0-DOC item is removed with its respective resolving commit. `TODO.md:182` and `TODO.md:331` use concise evidence records. Remaining repository Markdown mentions of open P0-DOC tasks are in preserved checkpoint history, not live prerequisite allocations. Both new raw-requirement files exactly reproduce the base task blocks. Checkpoint index and record are byte-identical to base, retaining checked-through `3b50a915d06f7ad383a4d6dc70403729918c0268`. Only the 13 authorized documentation/evidence paths changed. |

## Evidence cross-check

- Recomputed all four S01 Blender-source/GLB SHA256 values in `docs/spikes/s01-evidence/fingerprints.json`; all match current bytes.
- Recomputed all 17 fixture SHA256 values in `docs/spikes/s03-evidence/reviewed-fix-result.json`; all match current bytes. That retained result and both child results report success, distinct user directories/PIDs, absent Steam, and the complete native hold/reorder/drop/refresh schedule.
- `reviewed-fix-compilation.json` has ten successful owned-script records, exactly matching current discovery under the inspected exclusion rules. This is retained acceptance evidence, not a new compilation run.
- Read S03 proof/session/match/replication assertions for provisional rollback, immutable health 75 cut plus health 70 journal, pre-admission rejection, consumed held input/expiry, exhausted sequence window, fresh resync deadline, injured-marker/entity retention, old held/ack fences, per-entity movement freshness and five received movement RPCs. These support the revised minimum claims without extending them to equipment/seats/reset/collision/discrete actions/floods/capacity.
- Inspected `tools/run_s03.py` native proxy scheduling, isolated staging, child startup/readiness/results, error/warning checks and bounded child-only cleanup. Read committed canonical host/client/proxy logs. The fixture is marker/sample-only with saved placeholder rig and empty CityRoot, consistent with the documentation's limitations.

## Checks and retained review artifacts

Executed only static/read-only repository checks and wrote review files only in `/tmp/foundation-doc-review-N0nFbf`.

- `git status --short` / `git status --porcelain=v1`, `git rev-parse HEAD refs/heads/main`.
- `git log`, `git show` and `git diff` against the exact supplied base/candidate, including individual TODO resolving commits.
- `git merge-base --is-ancestor <base> <candidate>` and merge-range inventory.
- `git diff --check <base> <candidate>`: passed.
- `python3 /tmp/foundation-doc-review-N0nFbf/check_review.py`: passed. The script checks exact candidate/topology/scope, per-commit task removal, raw requirements, other task text/status preservation, historical/checkpoint preservation, provisional value preservation, local links/headings/LF/whitespace, retained hashes/result/compilation/discovery, and seven actual task commands. It does not import project Python or invoke engine/tooling tasks.
- Local documentation checks: 16 Markdown files, 240 local links/heading anchors, no missing target/heading or LF/trailing-whitespace issue.

Durable review files:

- `/tmp/foundation-doc-review-N0nFbf/review.md` — this full report.
- `/tmp/foundation-doc-review-N0nFbf/check_review.py` — independent static checker.
- `/tmp/foundation-doc-review-N0nFbf/checks.txt` — passing check output.

## Limitations and final disposition

This was one focused documentation/evidence/source inspection pass. No new Godot, gameplay, compiler, asset import/reexport, editor roundtrip, Blender, real-process network, hardware, export, Steam, service or profile proof ran. External links were not network-verified. Existing result records establish only their previously accepted fixture scope; raw temporary run directories were not used to infer additional acceptance. No repository edits, shared editor/native/service operations, merge/archive/push or profile changes occurred.

**Final disposition: ACCEPT `24c878572a2edc478ff6aeeda9ac95298cdb17a1` for P0-DOC1 and P0-DOC2.** No changes are required by this review. Any later candidate change or main movement requires an appropriate exact-revision disposition; this review does not advance the checkpoint watermark.
