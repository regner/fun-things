"""Bounded private Blender jobs, retained logs, fresh-process byte comparison."""
import os,subprocess,json,hashlib,datetime,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_roof_details_01-evidence'; T=Path(__file__).parent
E.mkdir(exist_ok=True); env=os.environ.copy(); env.update(ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy')
ledger=[]
def run(name,args):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (E/(name+'.log')).open('w') as log:
        try: result=subprocess.run(args,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT); code=result.returncode
        except FileNotFoundError as exc: log.write(str(exc)+'\n'); code=127
    ledger.append(dict(name=name,argv=args,cwd=str(R),environment_overrides={'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy'},started_utc=started,exit_code=code,raw_log=name+'.log'))
    (E/'commands.json').write_text(json.dumps(ledger,indent=2)+'\n')
    print(name,code,flush=True); return code
# Verify exact build even where distribution installs it under the plain binary name.
requested='/usr/bin/blender5.2.2LTS'
code=run('requested_binary_version',[requested,'-b','-noaudio','--version'])
exe=requested if code==0 else '/usr/bin/blender'
b=[exe,'-b','-noaudio','-t','4']
assert run('version',b+['--version'])==0
source=R/'art/source/models/environment/city_roof_details_01/city_roof_details_01.blend'
for name,args in [('author',b+['--python-exit-code','1','--python',str(T/'author.py')]),('export',b+[str(source),'--python-exit-code','1','--python',str(T/'export.py')]),('check_glb',[sys.executable,str(T/'check_glb.py')]),('reexport',b+[str(source),'--python-exit-code','1','--python',str(T/'export.py'),'--',str(E/'reexport.glb')]),('preview',b+[str(source),'--python-exit-code','1','--python',str(T/'preview.py')])]:
    if run(name,args): raise SystemExit(1)
a=R/'art/models/environment/city_roof_details_01/city_roof_details_01.glb'; b=E/'reexport.glb'
assert a.read_bytes()==b.read_bytes()
(E/'reexport_comparison.json').write_text(json.dumps(dict(byte_identical=True,sha256=hashlib.sha256(a.read_bytes()).hexdigest(),bytes=a.stat().st_size),indent=2)+'\n')
print('SAVED_SOURCE_REEXPORT_BYTE_IDENTICAL')
