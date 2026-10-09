# P0-TOOLING validation baseline repair

P0-TOOLING closes audit gap G5 without lowering lint or diagnostic thresholds. The
Windows baseline now has zero GDScript formatting/lint warnings, explicitly compiles
every discovered owned script, and discovers Python tests in tool subdirectories.

## Changes

- Split the three warned S07 driver declarations/functions without changing their
  order, thresholds, route ownership, waits, lifecycle checks, or receipt fields.
  Two pre-existing formatter failures in S07-ENV were removed with parameter grouping
  and existing saved-child lookup rather than suppressions.
- Added package markers for tool test directories. The S05 and S08 standalone offline
  checks now expose `unittest.TestCase` methods, and the S05 fakes account for Windows
  path, permission, and symlink behavior without launching an engine or opening a real
  endpoint.
- The compile mirror removes only the `MCPRuntimeServer` autoload and editor-plugin
  section. Other autoloads remain, as protected by a Python regression test.
- Mise pins Python 3.14.2 and invokes `python` on Windows and Linux. The single complete
  test command is `python -m unittest discover -s tools -p "*test*.py"`.
- GodotSteam `~lib*` generated import artifacts below `addons/godotsteam/` are ignored.

These repository-tool and documentation edits were made directly because no Godot MCP
editor was running. No saved scene hierarchy or serialized identity changed.

## Windows result

At the tested candidate, `python tools/script_checks.py` passed formatting, zero-warning
lint, compiler-mirror setup, and 82/82 explicit script compilations with Godot
`4.8.dev7.official.c971f93e7`. Complete Python discovery passed 29 tests, including S04,
S05 image, S07 comparator/driver, and S08 cadence tests. The isolated S07 guard script
also passed all 15 lifecycle expectations after the behavior-preserving splits.

The script check ran while seven `godot*` processes existed on the shared workstation;
that count labels the environment as contended, but no performance timing is claimed.
See [retained evidence](p0-tooling-evidence/README.md).

## Not verified on Linux

No Linux machine was available. The Mise Python pin is declared for both platforms, but
Linux installation, task resolution, script compilation, and complete unittest discovery
were not rerun there. No Godot gameplay, graphical, Blender, export, Steam, or network
acceptance is claimed by this tooling repair.
