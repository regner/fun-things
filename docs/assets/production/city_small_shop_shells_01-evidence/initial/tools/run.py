"""Run one private process, retaining full diagnostics and exact command receipts."""
import os, sys, json, subprocess, time
from pathlib import Path
R=Path(__file__).resolve().parents[3]
E=R/'docs/assets/production/city_small_shop_shells_01-evidence'
label=sys.argv[1]; argv=sys.argv[2:]
log=E/(label+'.log'); assert not log.exists(),log
patch={'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy','XDG_CACHE_HOME':str(E/'process_cache')}
start=time.time()
try:
    with log.open('w') as f:
        p=subprocess.run(argv,cwd=R,env={**os.environ,**patch},stdout=f,stderr=subprocess.STDOUT)
    code=p.returncode
except FileNotFoundError as exc:
    log.write_text(str(exc)+'\n'); code=127
receipt={'argv':argv,'cwd':str(R),'environment_overrides':patch,'start_unix':start,'duration_s':time.time()-start,'exit':code,'log':str(log.relative_to(R))}
(E/(label+'.command.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt)); sys.exit(code)
