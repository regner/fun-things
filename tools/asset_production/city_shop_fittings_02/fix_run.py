"""Additive F1 command capture with separate raw stdout/stderr and bounded private jobs."""
import datetime,json,os,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_02-evidence/f1_culling'
E.mkdir(exist_ok=True);label,*argv=sys.argv[1:]
assert not (E/(label+'.command.json')).exists()
overrides=dict(ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy',XDG_CACHE_HOME=str(E/'process_cache'),PYTHONDONTWRITEBYTECODE='1')
t=time.time();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (E/(label+'.stdout')).open('w') as out,(E/(label+'.stderr')).open('w') as err:
    p=subprocess.run(argv,cwd=R,env=dict(os.environ,**overrides),stdout=out,stderr=err,timeout=600)
receipt=dict(argv=argv,cwd=str(R),environment=overrides,start_utc=start,elapsed_seconds=time.time()-t,exit_status=p.returncode)
(E/(label+'.command.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));sys.exit(p.returncode)
