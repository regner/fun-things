# Actual review command ledger

Paths and commands are literal. Diagnostics and interpretation are in REPORT.md.

## diff

Exit: 0; duration: 0.003 seconds. Log: `diff.log`.

```sh
git diff --name-status 504486494f5ce21e9ffa5e58eed4373f8ba7d286 0be3af33d6c9cab30cffca1aed748875b9a36373
```

## processes

Exit: 0; duration: 0.004 seconds. Log: `processes.log`.

```sh
ps -eo pid,ppid,lstart,args
```

## versions-blender

Exit: 0; duration: 0.203 seconds. Log: `versions-blender.log`.

```sh
/usr/bin/blender --version
```

## versions-godot

Exit: 0; duration: 0.022 seconds. Log: `versions-godot.log`.

```sh
/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --version
```

## archive

Exit: 0; duration: 0.553 seconds. Log: `archive.log`.

```sh
bash -c 'git archive 0be3af33d6c9cab30cffca1aed748875b9a36373 | tar -x -C "$1"' review /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot
```

## prepare

Exit: 0; duration: 0.025 seconds. Log: `prepare.log`.

```sh
python3 /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/tools/rocket_launcher/prepare_clean.py /tmp/dock-thumper-review-0be3af3-i14mvols/project
```

## reexport

Exit: 124; duration: 90.012 seconds. Log: `reexport.log`.

```sh
timeout 90 /usr/bin/blender --background --factory-startup -noaudio /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/art/source/models/rocket_launcher/dock_thumper_a.blend --python /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/art/source/models/rocket_launcher/reexport_dock_thumper.py -- /tmp/dock-thumper-review-0be3af3-i14mvols/fresh
```

## import

Exit: 0; duration: 2.707 seconds. Log: `import.log`.

```sh
timeout 90 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --editor --import --editor-port 23650 --debug-server tcp://127.0.0.1:23651
```

## freshness

Exit: 0; duration: 0.027 seconds. Log: `freshness.log`.

```sh
python3 /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/tools/rocket_launcher/check_files.py /tmp/dock-thumper-review-0be3af3-i14mvols/fresh
```

## style

Exit: 0; duration: 0.003 seconds. Log: `style.log`.

```sh
/home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle check tests/fixtures/rocket_launcher/preview.gd tools/rocket_launcher/capture_check.gd --no-color --max-warnings 0
```

## headless

Exit: 0; duration: 0.242 seconds. Log: `headless.log`.

```sh
timeout 30 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --max-fps 60 --quit-after 900 --script res://tools/rocket_launcher/capture_check.gd
```

## import-host

Exit: 0; duration: 2.091 seconds. Log: `import-host.log`.

```sh
timeout 60 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --editor --import --editor-port 23650 --debug-server tcp://127.0.0.1:23651
```

## source-inspection

Exit: 0; duration: 0.559 seconds. Log: `source-inspection.log`.

```sh
timeout 60 /usr/bin/blender --background --factory-startup -noaudio /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/art/source/models/rocket_launcher/dock_thumper_a.blend --python /tmp/dock-thumper-review-0be3af3-i14mvols/inspect_blender.py -- /tmp/dock-thumper-review-0be3af3-i14mvols/source-inspection.json
```

## capture

Exit: 0; duration: 3.551 seconds. Log: `capture.log`.

```sh
timeout 60 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --max-fps 60 --resolution 1280x800 --quit-after 900 --script res://tools/rocket_launcher/capture_check.gd -- --capture
```

## source-inspection-final

Exit: 2; duration: 0.592 seconds. Log: `source-inspection-final.log`.

```sh
timeout 45 /usr/bin/blender --background --factory-startup -noaudio --python-exit-code 2 /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/art/source/models/rocket_launcher/dock_thumper_a.blend --python /tmp/dock-thumper-review-0be3af3-i14mvols/inspect_blender.py -- /tmp/dock-thumper-review-0be3af3-i14mvols/source-inspection.json
```

## reexport-host

Exit: 0; duration: 0.711 seconds. Log: `reexport-host.log`.

```sh
timeout 45 /usr/bin/blender --background --factory-startup -noaudio --python-exit-code 2 /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/art/source/models/rocket_launcher/dock_thumper_a.blend --python /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/art/source/models/rocket_launcher/reexport_dock_thumper.py -- /tmp/dock-thumper-review-0be3af3-i14mvols/fresh-host
```

## editor-roundtrip

Exit: 124; duration: 45.061 seconds. Log: `editor-roundtrip.log`.

```sh
timeout 45 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --editor --editor-port 23650 --debug-server tcp://127.0.0.1:23651
```

## editor-roundtrip-graphical

Exit: 0; duration: 5.165 seconds. Log: `editor-roundtrip-graphical.log`.

```sh
timeout 30 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --editor --editor-port 23650 --debug-server tcp://127.0.0.1:23651
```

## mesh-check

Exit: 124; duration: 20.006 seconds. Log: `mesh-check.log`.

```sh
timeout 20 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --script res://tools/independent_mesh_checks.gd
```

## mesh-check-final

Exit: 0; duration: 0.201 seconds. Log: `mesh-check-final.log`.

```sh
timeout 20 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --script res://tools/independent_mesh_checks.gd
```

## compile-preview

Exit: 0; duration: 0.201 seconds. Log: `compile-preview.log`.

```sh
/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --check-only --script res://tests/fixtures/rocket_launcher/preview.gd
```

## compile-capture

Exit: 0; duration: 0.201 seconds. Log: `compile-capture.log`.

```sh
/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --check-only --script res://tools/rocket_launcher/capture_check.gd
```

## editor-roundtrip-final

Exit: 0; duration: 3.847 seconds. Log: `editor-roundtrip-final.log`.

```sh
timeout 30 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --path /tmp/dock-thumper-review-0be3af3-i14mvols/project --editor --editor-port 23650 --debug-server tcp://127.0.0.1:23651
```

## prepare-final

Exit: 0; duration: 0.201 seconds. Log: `prepare-final.log`.

```sh
python3 /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/tools/rocket_launcher/prepare_clean.py /tmp/dock-thumper-review-0be3af3-i14mvols/clean-final
```

## freshness-host

Exit: 0; duration: 0.201 seconds. Log: `freshness-host.log`.

```sh
python3 /tmp/dock-thumper-review-0be3af3-i14mvols/snapshot/tools/rocket_launcher/check_files.py /tmp/dock-thumper-review-0be3af3-i14mvols/fresh-host
```

## clean-import-final

Exit: 0; duration: 2.294 seconds. Log: `clean-import-final.log`.

```sh
timeout 30 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/clean-final --editor --import --editor-port 23650 --debug-server tcp://127.0.0.1:23651
```

## diff-check

Exit: 2; duration: 0.201 seconds. Log: `diff-check.log`.

```sh
git diff --check 504486494f5ce21e9ffa5e58eed4373f8ba7d286 0be3af33d6c9cab30cffca1aed748875b9a36373
```

## clean-check-final

Exit: 0; duration: 0.247 seconds. Log: `clean-check-final.log`.

```sh
timeout 20 /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --headless --path /tmp/dock-thumper-review-0be3af3-i14mvols/clean-final --max-fps 60 --quit-after 900 --script res://tools/rocket_launcher/capture_check.gd
```

## glb-inspection

Exit: 0; duration: 0.201 seconds. Log: `glb-inspection.log`.

```sh
python3 /tmp/dock-thumper-review-0be3af3-i14mvols/inspect_glb.py
```
