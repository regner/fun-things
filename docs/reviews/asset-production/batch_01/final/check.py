"""Record bounded final-review commands without touching implementation or old evidence."""
import json,os,subprocess,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent
label=sys.argv[1];argv=sys.argv[2:];start=time.time()
env=os.environ.copy();env.update(GIT_OPTIONAL_LOCKS='0',ALSOFT_DRIVERS='null',SDL_AUDIODRIVER='dummy',XDG_CACHE_HOME='/tmp/six-final-review-cache')
assert not (OUT/(label+'.stdout.log')).exists(),label
with (OUT/(label+'.stdout.log')).open('w') as a,(OUT/(label+'.stderr.log')).open('w') as b:
 try:rc=subprocess.run(argv,stdout=a,stderr=b,env=env,timeout=180).returncode
 except subprocess.TimeoutExpired:rc='timeout'
path=OUT/'commands.json';rows=json.loads(path.read_text()) if path.exists() else []
rows.append(dict(label=label,argv=argv,cwd=str(Path.cwd()),environment_overrides={k:env[k] for k in ['GIT_OPTIONAL_LOCKS','ALSOFT_DRIVERS','SDL_AUDIODRIVER','XDG_CACHE_HOME']},exit=rc,elapsed_seconds=time.time()-start));path.write_text(json.dumps(rows,indent=2)+'\n');print(label,rc)
