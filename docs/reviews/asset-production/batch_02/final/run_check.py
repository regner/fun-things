"""Retain exact process arguments and both raw streams for independent final review."""
import json, os, subprocess, sys, time
from pathlib import Path
OUT = Path(__file__).resolve().parent
name, cwd, *argv = sys.argv[1:]
env = dict(os.environ)
overrides = json.loads(env.pop('REVIEW_ENV', '{}'))
env.update(overrides)
start = time.time()
p = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(OUT / (name + '.stdout')).write_bytes(p.stdout)
(OUT / (name + '.stderr')).write_bytes(p.stderr)
(OUT / (name + '.command.json')).write_text(json.dumps(dict(argv=argv, cwd=cwd,
    environment_overrides=overrides, exit_code=p.returncode, started_unix=start,
    elapsed_seconds=time.time()-start), indent=2)+'\n')
print(json.dumps(dict(check=name, exit=p.returncode, stdout_bytes=len(p.stdout), stderr_bytes=len(p.stderr))))
print(p.stdout.decode(errors='replace')[-16000:])
print(p.stderr.decode(errors='replace')[-3000:])
sys.exit(p.returncode)
