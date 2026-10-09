"""Run bounded private Godot camera captures of the three saved car previews."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = Path('/tmp/brackett-vehicle-production')
ENGINE = Path('/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot')
env = os.environ.copy()
env.update(XDG_CONFIG_HOME=str(STATE/'config'), XDG_DATA_HOME=str(STATE/'data'),
           XDG_CACHE_HOME=str(STATE/'cache'), GODOT_MCP_RUNTIME_PORT='21651')
assets = sys.argv[1:] or ['car_latch_a','car_crate_a','car_sable_a']
for asset in assets:
    for view, extra in [('game', []), ('inspection', ['--inspection']),
                        ('doors', ['--inspection','--doors-open'])]:
        name = asset + '_' + view
        command = [str(ENGINE), '--path', str(ROOT), '--display-driver', 'x11',
            '--rendering-method', 'gl_compatibility', '--max-fps', '60',
            '--resolution', '1280x800', '--quit-after', '300',
            '--log-file', str(STATE/'logs'/(name+'.engine.log')),
            'res://scenes/previews/city_cars/'+asset+'_preview.tscn',
            '--', '--vehicle-capture='+name, *extra]
        with (STATE/'logs'/(name+'.stdout.log')).open('w') as log:
            process = subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                                     stderr=subprocess.STDOUT, timeout=45)
        print(json.dumps({'capture':name, 'exit_code':process.returncode}), flush=True)
        if process.returncode:
            raise SystemExit(process.returncode)
