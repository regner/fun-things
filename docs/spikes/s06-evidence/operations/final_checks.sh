#!/bin/bash
cd /home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam
python3 tools/script_checks.py --godot /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --gdstyle /home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle --output /tmp/s06-all-checks > /tmp/s06-operations/all-checks.stdout 2> /tmp/s06-operations/all-checks.stderr
result=$?
python3 -c 'import json,sys;from pathlib import Path;Path("/tmp/s06-operations/all-checks.exit.json").write_text(json.dumps({"exit":int(sys.argv[1])})+"\n")' "$result"
mkdir -p /tmp/s06-host-reexport
XDG_CONFIG_HOME=/tmp/s06-source-user/config XDG_CACHE_HOME=/tmp/s06-source-user/cache timeout 45s blender --background -noaudio art/source/models/spikes/s06_intersection.blend --python tools/s06/export.py -- /tmp/s06-host-reexport > /tmp/s06-host-reexport/blender.log 2>&1
result=$?
python3 -c 'import json,sys;from pathlib import Path;Path("/tmp/s06-host-reexport/exit.json").write_text(json.dumps({"exit":int(sys.argv[1])})+"\n")' "$result"
