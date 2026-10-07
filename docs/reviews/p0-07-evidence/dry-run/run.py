import os, subprocess, json, time, pathlib, sys
ROOT = pathlib.Path('/tmp/p0-07-review-irdbxx5x/reviewer')
env = os.environ.copy()
for key, name in [('XDG_DATA_HOME','xdg-data'),('XDG_CONFIG_HOME','xdg-config'),('XDG_CACHE_HOME','xdg-cache')]:
    env[key] = str(ROOT/name)
    (ROOT/name).mkdir(exist_ok=True)
label, deadline, cwd, *cmd = sys.argv[1:]
start=time.monotonic()
with (ROOT/(label+'.log')).open('w') as log:
    p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    timed_out=False
    try: code=p.wait(timeout=float(deadline))
    except subprocess.TimeoutExpired:
        import signal
        timed_out=True
        os.killpg(p.pid,signal.SIGKILL)
        code=p.wait()
record={'label':label,'command':cmd,'cwd':cwd,'deadline_seconds':float(deadline),'elapsed_seconds':time.monotonic()-start,'exit_code':code,'timed_out':timed_out,'environment':{k:env[k] for k in ['XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME']}}
(ROOT/(label+'.command.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
print((ROOT/(label+'.log')).read_text())
