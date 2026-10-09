"""Private bounded jobs; preserve full diagnostics and actual argv/exit status."""
import os, subprocess, json, hashlib, datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_04-evidence'; T=R/'tools/asset_production/city_planting_04'
env=os.environ.copy(); env.update(ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy')
ledger=json.loads((E/'commands.json').read_text()) if (E/'commands.json').exists() else []
def run(name,args):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    assert not (E/(name+'.log')).exists(), 'Preserve previous run before repeating'
    with (E/(name+'.log')).open('w') as log: result=subprocess.run(args,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
    ledger.append({'name':name,'argv':args,'cwd':str(R),'environment_overrides':{'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy'},'started_utc':start,'exit_code':result.returncode,'raw_log':name+'.log'})
    (E/'commands.json').write_text(json.dumps(ledger,indent=2)+'\n')
    print(name,result.returncode,flush=True)
    if result.returncode:raise SystemExit(result.returncode)
b=['/usr/bin/blender','-b','-noaudio','-t','4']; source=R/'art/source/models/environment/city_planting_04/city_planting_04.blend'
if __name__=='__main__':
    run('version',b+['--version'])
    run('author',b+['--python-exit-code','1','--python',str(T/'author.py')])
    run('repair_tips',b+[str(source),'--python-exit-code','1','--python',str(T/'repair_tips.py')])
