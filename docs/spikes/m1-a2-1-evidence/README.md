# M1-A2.1 retained evidence

Evidence for the production foot command, ActorMotion, desktop input, player scene, and development
harness. Commands used the Mise-pinned Godot `4.8.dev7.official.c971f93e7`; every engine invocation
was bounded by `timeout`. Runner output originated outside the checkout under
`C:/tmp/ft/lanes/m1-a2-1/`.

| File | Result |
| --- | --- |
| `gut.log` | Focused `tests/unit/actors`: 13/13 tests, 120 assertions passed. |
| `harness-smoke.log` | Actual saved harness/player moved 0.500 m and exited successfully. |
| `style.log` | All 53 current project-owned GDScripts passed zero-warning lint. |
| `production-summary.json` | Canonical layers; known unreconciled asset-production failures remain. |
| `known-preexisting-failures.log` | Exact five fixture compile and three formatting failures from the brief. |

The known failures do not touch this row. All changed GDScripts pass focused zero-warning gdstyle,
the focused GUT run passes, and the harness log contains no `SCRIPT ERROR`, `ERROR`, or `WARNING`.
The Godot editor was unavailable; direct scene text authoring plus a pinned headless load/pack/save
roundtrip is recorded in the task record.
