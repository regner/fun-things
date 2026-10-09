import subprocess,os,json,pathlib,concurrent.futures,time
root=pathlib.Path.cwd();out=root/'docs/assets/production/batch_02-evidence/processes';private=pathlib.Path('/tmp/asset-register-production-editor/batch02');binary='/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
def run(label,port):
 folder=private/label
 for name in ['data','config','cache']:(folder/name).mkdir(parents=True,exist_ok=True)
 overrides={'XDG_DATA_HOME':str(folder/'data'),'XDG_CONFIG_HOME':str(folder/'config'),'XDG_CACHE_HOME':str(folder/'cache'),'GODOT_MCP_RUNTIME_PORT':str(port)};argv=[binary,'--headless','--path',str(root),'--script','res://tests/fixtures/asset_production/batch_02_process_probe.gd'];started=time.time()
 with (out/(label+'.stdout.log')).open('w') as stdout,(out/(label+'.stderr.log')).open('w') as stderr:
  proc=subprocess.Popen(argv,env=dict(os.environ,**overrides),stdout=stdout,stderr=stderr);code=proc.wait(timeout=60)
 row={'label':label,'pid':proc.pid,'argv':argv,'environment_overrides':overrides,'exit_code':code,'elapsed_s':time.time()-started}
 (out/(label+'.execution.json')).write_text(json.dumps(row,indent=2)+'\n');return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(lambda args:run(*args),[('process_a',22661),('process_b',22662)]))
print(json.dumps(rows));assert all(row['exit_code']==0 for row in rows)
