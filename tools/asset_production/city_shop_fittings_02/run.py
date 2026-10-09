"""Run an owned subprocess with complete combined diagnostics and argv/exit receipts."""
import json, os, subprocess, sys, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_shop_fittings_02-evidence'
label,*argv=sys.argv[1:]
assert not (E/(label+'.log')).exists(), 'Keep old diagnostics; use a fresh label'
env_overrides={'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy','XDG_CACHE_HOME':str(E/'process_cache'),'PYTHONDONTWRITEBYTECODE':'1'}
start=time.time(); pid=None; terminated=False
with (E/(label+'.log')).open('w') as stream:
    try:
        process=subprocess.Popen(argv,cwd=ROOT,env=dict(os.environ,**env_overrides),stdout=stream,stderr=subprocess.STDOUT)
        pid=process.pid
        try: status=process.wait(timeout=900)
        except subprocess.TimeoutExpired:
            terminated=True; process.terminate()
            try: status=process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); status=process.wait()
    except OSError:
        traceback.print_exc(file=stream); status=127
record=dict(label=label,argv=argv,cwd=str(ROOT),pid=pid,environment_overrides=env_overrides,exit_status=status,seconds=time.time()-start,terminated_owned_process=terminated)
p=E/'execution.json'; records=json.loads(p.read_text()) if p.exists() else []; records.append(record)
p.write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(record));sys.exit(status if status>=0 else 1)
