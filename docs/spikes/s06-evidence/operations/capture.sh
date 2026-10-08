#!/bin/bash
cd /home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam
python3 /tmp/s06-operations/stop_reexport.py
mkdir -p /tmp/s06-source-capture
XDG_CONFIG_HOME=/tmp/s06-source-user/config XDG_CACHE_HOME=/tmp/s06-source-user/cache timeout 55s blender --background -noaudio art/source/models/spikes/s06_intersection.blend --python tools/s06/capture_source.py -- /tmp/s06-source-capture/top.png > /tmp/s06-source-capture/blender.log 2>&1
result=$?
python3 -c 'import json,sys;from pathlib import Path;Path("/tmp/s06-source-capture/exit.json").write_text(json.dumps({"exit":int(sys.argv[1])})+"\n")' "$result"
python3 /tmp/s06-operations/host_inventory.py
