"""Private jobs with full argv/log/exit receipts and saved-source byte reexports."""
import os, subprocess, json, hashlib, datetime, sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]; T=Path(__file__).parent
E=R/'docs/assets/production/city_shop_fittings_03-evidence'
E.mkdir(exist_ok=True)
env=os.environ.copy(); env.update(ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy')
ledger=[]
def run(name,args):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (E/(name+'.log')).open('w') as log:
        try: code=subprocess.run(args,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        except FileNotFoundError as exc: log.write(str(exc)+'\n'); code=127
    ledger.append(dict(name=name,argv=args,cwd=str(R),environment_overrides={'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy'},started_utc=started,exit_code=code,raw_log=name+'.log'))
    (E/'commands.json').write_text(json.dumps(ledger,indent=2)+'\n'); print(name,code,flush=True)
    return code
requested='/usr/bin/blender5.2.2LTS'
code=run('requested_binary_version',[requested,'-b','-noaudio','--version'])
exe=requested if code==0 else '/usr/bin/blender'; b=[exe,'-b','-noaudio','-t','4']
assert run('version',b+['--version'])==0
source=R/'art/source/models/environment/city_shop_fittings_03/city_shop_fittings_03.blend'
steps=[('author',b+['--python-exit-code','1','--python',str(T/'author.py')]),('export',b+[str(source),'--python-exit-code','1','--python',str(T/'export.py')]),('check_glb',[sys.executable,str(T/'check_glb.py')]),('check_interface',b+[str(source),'--python-exit-code','1','--python',str(T/'check_interface.py')]),('reexport',b+[str(source),'--python-exit-code','1','--python',str(T/'export.py'),'--',str(E/'reexports')])]
if '--preview' in sys.argv: steps.append(('preview',b+[str(source),'--python-exit-code','1','--python',str(T/'preview.py')]))
steps.append(('interface_sheet',[sys.executable,str(T/'interface_sheet.py')]))
for name,args in steps:
    if run(name,args): raise SystemExit(1)
comparisons=[]
for v in ('single','double'):
    a=R/('art/models/environment/city_shop_fittings_03/city_shop_fittings_03_'+v+'.glb')
    b=E/'reexports'/a.name
    assert a.read_bytes()==b.read_bytes()
    comparisons.append(dict(variant=v,byte_identical=True,sha256=hashlib.sha256(a.read_bytes()).hexdigest(),bytes=a.stat().st_size))
(E/'reexport_comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n')
print('SAVED_SOURCE_REEXPORTS_BYTE_IDENTICAL')
