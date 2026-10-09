"""Run isolated verification with bounded shutdown and compare both fresh GLBs."""
import os, subprocess, json, hashlib, signal, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_lights_01-evidence'
records=[]
def run(label,args,seconds=35):
    env=os.environ.copy(); env['ALSOFT_DRIVERS']='null'; env['SDL_AUDIODRIVER']='dummy'
    log=E/(label+'.log')
    with log.open('w') as stream:
        p=subprocess.Popen(args,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        timed_out=False
        try: code=p.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            timed_out=True; os.killpg(p.pid,signal.SIGTERM); code=p.wait(timeout=10)
    records.append({'argv':args,'exit_code':code,'timeout_terminated_owned_group':timed_out,'log':str(log.relative_to(ROOT)), 'environment_overrides':{'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy'}})
    return code
base=['/usr/bin/blender','-noaudio','--background','--threads','2','--python-exit-code','1']
run('validation_final',base+['--factory-startup','--python','tools/asset_production/city_lights_01/validate.py'])
with tempfile.TemporaryDirectory(prefix='city_lights_01_reexport_') as scratch:
    run('reexport',base+['art/source/models/environment/city_lights_01/city_lights_01.blend','--python','tools/asset_production/city_lights_01/export.py','--',scratch])
    results={}
    for variant in ('warm','cool'):
        name=f'city_lights_01_{variant}.glb'
        original=ROOT/'art/models/environment/city_lights_01'/name
        fresh=Path(scratch)/name
        assert fresh.is_file(),fresh
        a=hashlib.sha256(original.read_bytes()).hexdigest(); b=hashlib.sha256(fresh.read_bytes()).hexdigest()
        results[variant]={'production_sha256':a,'fresh_export_sha256':b,'byte_equal':original.read_bytes()==fresh.read_bytes()}
        assert results[variant]['byte_equal'], variant
    (E/'reproducibility.json').write_text(json.dumps(results,indent=2)+'\n')
(E/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps({'commands':records,'reproducibility':results},indent=2))
