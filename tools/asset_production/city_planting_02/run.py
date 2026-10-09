"""Run isolated Blender jobs with complete argv, diagnostics, exits and fingerprints."""
import os, subprocess, json, hashlib, datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_02-evidence'; T=R/'tools/asset_production/city_planting_02'
env=os.environ.copy(); env.update(ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy')
ledger=[{'argv':['/usr/bin/blender5.2.2LTS','-b','-noaudio','--version'],'exit_code':127,'diagnostic':'/usr/bin/bash: line 1: /usr/bin/blender5.2.2LTS: No such file or directory','resolution':'/usr/bin/blender verified exact build d13f752e3b9c'}]
def run(name,args):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (E/(name+'.log')).open('w') as log:
        result=subprocess.run(args,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
    ledger.append({'name':name,'argv':args,'cwd':str(R),'environment_overrides':{'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy'},'started_utc':start,'exit_code':result.returncode,'raw_log':name+'.log'})
    (E/'commands.json').write_text(json.dumps(ledger,indent=2)+'\n')
    if result.returncode: raise SystemExit(result.returncode)
    print(name, 'PASS',flush=True)
b=['/usr/bin/blender','-b','-noaudio','-t','4']
run('version',b+['--version'])
run('author',b+['--python-exit-code','1','--python',str(T/'author.py')])
source=R/'art/source/models/environment/city_planting_02/city_planting_02.blend'
run('export',b+[str(source),'--python-exit-code','1','--python',str(T/'export.py')])
run('check_glb',['python',str(T/'check_glb.py')])
run('reexport',b+[str(source),'--python-exit-code','1','--python',str(T/'export.py'),'--',str(E/'reexport.glb')])
out=R/'art/models/environment/city_planting_02/city_planting_02.glb'
assert out.read_bytes()==(E/'reexport.glb').read_bytes()
(E/'reexport_comparison.json').write_text(json.dumps({'byte_identical':True,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size},indent=2)+'\n')
print('SAVED_SOURCE_REEXPORT_BYTE_IDENTICAL',flush=True)
