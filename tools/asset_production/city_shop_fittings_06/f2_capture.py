"""Capture one correction job, retaining both streams and literal invocation."""
import subprocess,os,json,sys,datetime,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_06-evidence/fix_f2'
name=sys.argv[1];args=sys.argv[2:];env=os.environ.copy();overrides=dict(ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy',ASSET_EVIDENCE_DIR=str(E));env.update(overrides)
start=time.monotonic();receipt=dict(argv=args,cwd=str(R),environment_overrides=overrides,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with (E/(name+'.stdout')).open('w') as out,(E/(name+'.stderr')).open('w') as err:
    code=subprocess.run(args,cwd=R,env=env,stdout=out,stderr=err).returncode
receipt.update(exit_code=code,elapsed_seconds=time.monotonic()-start,stdout=name+'.stdout',stderr=name+'.stderr');(E/(name+'.command.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(name,code);sys.exit(code)
