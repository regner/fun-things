# S17 quiet remeasurement evidence

- `summary.json`: compact pooled timings, budgets, per-seed context, and interpretation.
- `result.json`: unchanged runner's complete pooled result and command list.
- `measurement-identity.json`: repository, source, invocation, and effective-parameter binding.
- `precondition.txt`: pre-launch process, power, battery, CPU, and worktree receipt.
- `post-run-ac-status.json`: explicit post-run `PowerOnline` clarification.
- `runner.log`: compact command output.
- `seed-*.log`: complete short runtime logs for all three measured processes.

Raw per-tick seed JSON remains outside the repository under
`C:/tmp/ft/lanes/quiet-pass/s17/run/`; its pooled summaries are retained here without adding
about 3.5 MiB of redundant samples. `SHA256SUMS` binds every retained evidence file other
than itself.
