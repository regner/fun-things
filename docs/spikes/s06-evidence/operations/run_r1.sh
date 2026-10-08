#!/bin/bash
cd /home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam
python3 tools/s06/run.py --content-only --godot /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --output /tmp/s06-r1-content > /tmp/s06-operations/r1-content.stdout 2> /tmp/s06-operations/r1-content.stderr
result=$?
python3 -c 'import json,sys;from pathlib import Path;Path("/tmp/s06-operations/r1-content.exit.json").write_text(json.dumps({"exit":int(sys.argv[1])})+"\n")' "$result"
#!/bin/bash
cd /home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam
python3 tools/script_checks.py --godot /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --gdstyle /home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle --output /tmp/s06-r1-checks > /tmp/s06-operations/r1-checks.stdout 2> /tmp/s06-operations/r1-checks.stderr
result=$?
python3 -c 'import json,sys;from pathlib import Path;Path("/tmp/s06-operations/r1-checks.exit.json").write_text(json.dumps({"exit":int(sys.argv[1])})+"\n")' "$result"
