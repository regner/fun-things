import subprocess,pathlib,sys,concurrent.futures,json
O=pathlib.Path(__file__).resolve().parent;binary='/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
def run(x):
 label,port=x;prefix='/tmp/batch03-final/'+label;argv=['env','XDG_DATA_HOME='+prefix+'/data','XDG_CONFIG_HOME='+prefix+'/config','XDG_CACHE_HOME='+prefix+'/cache','GODOT_MCP_RUNTIME_PORT='+str(port),binary,'--headless','--path','/tmp/batch03-final/project','--script','res://tests/fixtures/asset_production/batch_03_process_probe.gd']
 return subprocess.run([sys.executable,str(O/'run_check.py'),label,*argv],timeout=60).returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:r=list(pool.map(run,[('review_process_a',22871),('review_process_b',22872)]))
print(json.dumps(r));assert not any(r)
