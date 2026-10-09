"""Bounded independent review jobs, exclusively in scratch and review output."""
import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
ROOT=Path('/tmp/six-asset-review-390377d')
OUT=Path(__file__).resolve().parent
IDS=['city_lights_01','city_lights_02','city_lights_04','city_sign_supports_01','city_planting_01','city_planting_02']
commands=[]
def run(label,argv,cwd=ROOT,timeout=120):
    start=time.time()
    env=os.environ.copy();env.update(ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy',XDG_CACHE_HOME='/tmp/six-review-cache')
    with (OUT/(label+'.stdout.log')).open('w') as stdout,(OUT/(label+'.stderr.log')).open('w') as stderr:
        try: code=subprocess.run(argv,cwd=cwd,env=env,stdout=stdout,stderr=stderr,timeout=timeout).returncode
        except subprocess.TimeoutExpired:code='timeout'
    commands.append(dict(label=label,argv=argv,cwd=str(cwd),environment_overrides={k:env[k] for k in ['ALSOFT_DRIVERS','SDL_AUDIODRIVER','XDG_CACHE_HOME']},exit=code,elapsed_seconds=time.time()-start))
    (OUT/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');print(label,code,flush=True)
    return code
run('blender-version',['/usr/bin/blender','--version'])
run('independent-source-inspection',['/usr/bin/blender','-b','--factory-startup','-noaudio','--threads','2','--python-exit-code','1','--python',str(OUT/'inspect_sources.py')])
comparisons=[]
for aid in IDS:
    job=Path('/tmp/six-review-jobs')/aid
    for path in ['art/source/models/environment/'+aid,'art/models/environment/'+aid,'tools/asset_production/'+aid,'docs/assets/production/'+aid+'-evidence','tools/s01']:
        dst=job/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(ROOT/path,dst,dirs_exist_ok=True)
    args=[]
    if aid=='city_lights_01':args=['--',str(job/'art/models/environment'/aid)]
    elif aid=='city_lights_04':args=['--',str(job/'art/models/environment'/aid)]
    elif aid=='city_sign_supports_01':args=['--',str(job/'art/models/environment'/aid/(aid+'.glb')),str(job/'docs/assets/production'/ (aid+'-evidence')/'review-reexport.json')]
    rc=run(aid+'-reexport',['/usr/bin/blender','-b','--factory-startup','-noaudio','--threads','2',str(job/'art/source/models/environment'/aid/(aid+'.blend')),'--python-exit-code','1','--python',str(job/'tools/asset_production'/aid/'export.py')]+args,cwd=job)
    for glb in (ROOT/'art/models/environment'/aid).glob('*.glb'):
        new=job/'art/models/environment'/aid/glb.name
        comparisons.append(dict(asset=aid,path=str(glb.relative_to(ROOT)),original_sha256=hashlib.sha256(glb.read_bytes()).hexdigest(),fresh_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),byte_identical=glb.read_bytes()==new.read_bytes(),export_exit=rc))
(OUT/'fresh-export-comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n')
run('independent-manifest-and-glb',['python3',str(OUT/'inspect_payload.py')])
