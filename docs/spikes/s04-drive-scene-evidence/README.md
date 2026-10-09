# S04 standalone drive evidence

Evidence captured on Windows 11 with pinned Godot `4.8.dev7.official.c971f93e7`, Forward+ / D3D12,
and an NVIDIA GeForce RTX 4070 Laptop GPU. Runner/user data was isolated below
`C:\tmp\ft\lanes\s04-drive`; no scratch project is retained here.

## Receipts

| File | Meaning |
| --- | --- |
| `drive.png` | Actual 1280×800 viewport from the windowed smoke after acceleration/turning; shows the saved track/car, fixed-north camera and tuning HUD. |
| `smoke-windowed.log` | Windowed saved-scene smoke: defaults, `+/-`, F12 save, speed rise, steering, braking and reset all passed; no engine/script warning or error diagnostics. |
| `smoke-headless.log` | Same public-API outcome without rendering. |
| `direct-window.log` | Direct `drive.tscn` launch for 120 frames; exit 0 and no warning/error/script diagnostics. |
| `s04-checks-result.json`, `s04-checks.log` | Existing isolated S04 body, baseline, pose-fence and producer cases all true; staged source remained unchanged. |
| `script-checks.log` | Post-rebase all-owned explicit compilation is true. Lint reports only the three accepted `tests/fixtures/s07_driver/` warnings. Formatting is false solely because current target `s08-enet-bandwidth` adds `tests/fixtures/s07_env/measure.gd` and `tools/s07_env/author_city.gd` with formatter drift; neither is lane-owned or changed here. |
| `focused-style.log` | All six changed/added GDScripts pass formatter and zero-warning lint checks. |
| `tool-tests.log` | All seventeen post-rebase repository Python tool tests pass. |
| `normalize.log` | Pinned-engine load/pack/resave receipt for the three hand-authored minimal scenes. |
| `import-initial.log`, `import-uids.log` | Required UID-generating import and final resource-UID registration scan. They exit 0 but retain known editor-plugin/version and shutdown-leak diagnostics, so neither is represented as a clean scene/runtime check. |

## Commands

The executable paths were resolved with `mise -C C:/GameDev/git/fun-things which ...` before use.
Fresh output directories were removed only when they belonged to this lane.

```sh
# Version and required UID import
timeout 30 godot --version
gdstyle --version
timeout 120 godot --headless --editor --path . --import --quit

# External one-use SceneTree script: load, instantiate, PackedScene.pack, ResourceSaver.save
timeout 60 godot --headless --path . --script C:/tmp/ft/lanes/s04-drive/normalize_scenes.gd

# Focused existing S04 behavior
timeout 300 python tools/s04/run_checks.py \
  --godot 'C:\Users\regner.blokandersen\AppData\Local\mise\installs\github-godotengine-godot-builds\4.8-dev7\godot.exe' \
  --output C:/tmp/ft/lanes/s04-drive/checks

# New smoke, once headless and once with a real window/capture
timeout 90 godot --headless --path . --script res://tests/fixtures/s04_drive/smoke.gd
timeout 90 godot --path . --resolution 1280x800 \
  --script res://tests/fixtures/s04_drive/smoke.gd -- \
  --capture=C:/GameDev/git/ft-lanes/s04-drive/docs/spikes/s04-drive-scene-evidence/drive.png

# Direct saved scene, bounded to 120 rendered frames
timeout 60 godot --path . --resolution 1280x800 --quit-after 120 \
  res://tests/fixtures/s04_drive/drive.tscn

# Repository checks
timeout 600 python tools/script_checks.py
gdstyle fmt --check tests/fixtures/s04/drive_rules.gd \
  tests/fixtures/s04/kinematic.gd tests/fixtures/s04_drive/*.gd
gdstyle --max-line-length 100 --max-warnings 0 tests/fixtures/s04/drive_rules.gd \
  tests/fixtures/s04/kinematic.gd tests/fixtures/s04_drive/*.gd
timeout 300 python -m unittest discover -s tools -p "test_*.py"
```

The first attempted S04-check invocation passed Git Bash's `/c/.../godot` path to native Windows
Python, which could not create that executable (`WinError 2`) before any fixture ran. The retained
result uses the Windows path returned directly by Mise. This invocation correction did not change
source or weaken a check.
