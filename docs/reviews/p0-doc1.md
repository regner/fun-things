# P0-DOC1 — current foundation tooling reconciliation

7 October 2026. Worker: Codex. Base: local `refs/heads/main` at
`8f512779356464b33de06138e18c962d12bfab10`, branch `foundation-doc-reconciliation`.
Budget: one focused documentation pass plus fixes; no new technical proofs.
[Raw task requirements](foundation-doc-evidence/p0-doc1-requirements.txt).

Updated guidance provenance and the asset catalogue tooling statement; supplemented
P0-06 and S01 without rewriting their original experiments. Commands/scopes were
checked against `mise.toml`, `tools/script_checks.py`, `tools/check.py`,
`tools/s01/reexport.py`, `tools/s01/clean_import.py` and `tools/run_s03.py`.
Accepted inputs are [S01](../spikes/s01.md#evidence-and-reproduction) and
[combined P0-03/S03 validation](../spikes/s03.md#integration-validation), including
its [final compilation](../spikes/s03-evidence/reviewed-fix-compilation.json) and
[result](../spikes/s03-evidence/reviewed-fix-result.json).

Completion means current claims name implemented fixture tooling while CI,
preserving formatter and broader production checks remain M1-D1. It preserves the
rejected imported-child override, full-project diagnostics and unproved
Steam/Deck/gameplay cases. Static evidence/command inspection and local link/heading
and whitespace checks validate documentation only; no engine, Blender, network,
hardware or service checks were rerun. The [independent report](foundation-doc-review.md) and
[check output](foundation-doc-evidence/independent-checks.txt) retain review of the
resolving candidate; exact final-revision disposition accompanies the handoff. The first checkpoint's history and checked-through
`3b50a915d06f7ad383a4d6dc70403729918c0268` watermark remain unchanged.
