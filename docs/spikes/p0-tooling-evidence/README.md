# P0-TOOLING retained validation evidence

Windows 11, Python 3.14.2, Godot `4.8.dev7.official.c971f93e7`, and gdstyle 0.3.0.
Commands ran from the repository root with long Python and Godot invocations bounded by
`timeout`. The full script check was contended (`godot*` process count: 7); these are
correctness checks, not timing measurements.

| Evidence | Result |
| --- | --- |
| `script-checks-console.log` | Exit 0: formatting, lint and compilation all true. |
| `formatting.log`, `style.log` | No formatting changes required and zero lint warnings. |
| `compiler-setup.json`, `compiler-import.log`, `compiler-import.engine.log.gz` | Isolated import/setup passed without diagnostics. |
| `scripts.json`, `compilation.json` | 82 discovered owned scripts; 82 explicit compiles passed. |
| `unit-tests.log`, `post-rebase-unit-tests.log` | Complete `*test*.py` discovery passed 29 tests before and after rebase. |
| `post-rebase-script-checks-console.log` | Post-rebase formatting, lint, setup and 82/82 compilation passed. |
| `s07-guards/guards.json` | All 15 behavior/lifecycle expectations passed. |
| `s07-guards/import.log`, `s07-guards/*.log.gz` | Isolated import and guard execution exited 0 without diagnostics. |

Commands:

**9 October 2026 supplement:** the `git check-ignore` invocation below is a historical
receipt. Owner decision 17 removed both `addons/godotsteam/` and its `~lib*` ignore rule,
so this invocation is no longer expected to pass on the current tree.

```sh
timeout 300s python tools/script_checks.py \
  --output C:/tmp/ft/lanes/p0-tooling/script-checks-pre
timeout 300s python -m unittest discover -s tools -p "*test*.py" -v
timeout 90s godot --headless --editor \
  --path C:/tmp/ft/lanes/p0-tooling/s07-guards/project --import --quit
timeout 90s godot --headless \
  --path C:/tmp/ft/lanes/p0-tooling/s07-guards/project \
  --script res://tests/fixtures/s07_driver/guards.gd
git check-ignore -v --no-index addons/godotsteam/~libgodotsteam.dll \
  addons/godotsteam/win64/~libgodotsteam.dll
git diff --check
```

No Linux machine was available; Linux task resolution and both green baseline commands
remain unverified there. Direct text editing was used because the Godot editor/MCP tools
were unavailable; no scene hierarchy was edited.
