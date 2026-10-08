#!/bin/bash
cd /home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam
python3 tools/s06/run.py --godot /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --output /tmp/s06-host-first > /tmp/s06-operations/host-first.stdout 2> /tmp/s06-operations/host-first.stderr
result=$?
python3 -c 'import json,sys;from pathlib import Path;Path("/tmp/s06-operations/host-first.exit.json").write_text(json.dumps({"exit":int(sys.argv[1])})+"\n")' "$result"
