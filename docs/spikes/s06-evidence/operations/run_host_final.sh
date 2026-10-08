#!/bin/bash
cd /home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam
python3 tools/s06/run.py --godot /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --output /tmp/s06-host-final > /tmp/s06-operations/host-final.stdout 2> /tmp/s06-operations/host-final.stderr
result=$?
python3 -c 'import json,sys;from pathlib import Path;Path("/tmp/s06-operations/host-final.exit.json").write_text(json.dumps({"exit":int(sys.argv[1])})+"\n")' "$result"
python3 tools/s06/analyze.py /tmp/s06-host-final/project/s06-result.json --output /tmp/s06-host-final/geometry-analysis.json > /tmp/s06-host-final/analysis.stdout 2> /tmp/s06-host-final/analysis.stderr
