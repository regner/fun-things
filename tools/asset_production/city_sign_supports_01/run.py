"""Run one owned command, retaining argv, combined output and exit status."""
import json, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
E = ROOT / 'docs/assets/production/city_sign_supports_01-evidence'
label, *argv = sys.argv[1:]
assert not (E / (label + '.log')).exists(), 'Use a fresh label; preserve failures.'
overrides = {'ALSOFT_DRIVERS':'null', 'SDL_AUDIODRIVER':'dummy', 'XDG_CACHE_HOME':str(E/'process_cache')}
env = dict(os.environ, **overrides)
start = time.time()
with (E / (label + '.log')).open('w') as stream:
    process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    try:
        status = process.wait(timeout=900)
        terminated = False
    except subprocess.TimeoutExpired:
        process.terminate()
        try: status = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill(); status = process.wait()
        terminated = True
record = dict(label=label, argv=argv, cwd=str(ROOT), pid=process.pid,
              environment_overrides=overrides,
              exit_status=status, seconds=time.time()-start, terminated_owned_process=terminated)
p = E / 'execution.json'
records = json.loads(p.read_text()) if p.exists() else []
records.append(record)
p.write_text(json.dumps(records, indent=2)+'\n')
print(json.dumps(record), flush=True)
sys.exit(status if status >= 0 else 1)
