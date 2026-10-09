"""Run private jobs; preserve full diagnostics and actual argv/exits in an append ledger."""
import os, sys, json, subprocess, datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_05-evidence'
env=os.environ.copy(); env.update(ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy')
name=sys.argv[1]; args=sys.argv[2:]
ledger_path=E/'commands.json'
assert not (E/(name+'.log')).exists(), 'Use a fresh diagnostic name; never erase failures'
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (E/(name+'.log')).open('w') as log:
    try:
        result=subprocess.run(args,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
        code=result.returncode
    except OSError as e:
        log.write(repr(e)+'\n'); code=127
receipt={'name':name,'argv':args,'cwd':str(R),'environment_overrides':{'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy'},'started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':code,'raw_log':name+'.log'}
(E/(name+'.command.json')).write_text(json.dumps(receipt,indent=2)+'\n')
ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else []
ledger.append(receipt)
ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
print(name,'exit',code)
sys.exit(code)
