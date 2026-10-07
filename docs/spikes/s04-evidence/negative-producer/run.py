from pathlib import Path
import json,sys,subprocess,difflib,hashlib
sys.path.insert(0,'tools')
from run_s04 import stage
from script_checks import environment,checked_command,DIAGNOSTIC
out=Path('/tmp/s04-negative-producer')
project=stage(out)
p=project/'tests/fixtures/s04/proof.gd'
before=p.read_text()
span=' or (\n\t\tnot match_state.rig.get_meta("input_enabled", false))'
assert before.count(span)==1
p.write_text(before.replace(span,''))
(out/'mutation.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),p.read_text().splitlines(True),fromfile='fixed-proof.gd',tofile='gate-omitted-proof.gd')))
godot='/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
env=environment(out/'user')
cmd=[godot,'--headless','--editor','--path',str(project),'--import','--quit']
assert checked_command(cmd,out/'import.log',env)
probe=[godot,'--headless','--path',str(project),'--script','res://tests/fixtures/s04/producer_probe.gd']
with (out/'probe.log').open('w') as log:
 result=subprocess.run(probe,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=15)
text=(out/'probe.log').read_text()
ok=result.returncode==1 and '"ok":false' in text and not DIAGNOSTIC.search(text)
receipt={'ok':ok,'expected_exit':1,'actual_exit':result.returncode,'runtime_diagnostics':bool(DIAGNOSTIC.search(text)),'commands':[cmd,probe],'only_mutation':'omit recurring input_enabled guard','fixed_source_sha256':hashlib.sha256(before.encode()).hexdigest(),'mutated_source_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
assert ok
