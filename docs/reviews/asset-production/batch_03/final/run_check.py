"""Retain literal argv, separate raw streams and actual exits for isolated checks."""
import datetime
import json
import os
import pathlib
import subprocess
import sys
import time

OUT = pathlib.Path(__file__).resolve().parent
label, *argv = sys.argv[1:]
assert label and argv
assert not (OUT / (label + '.command.json')).exists(), label
env = dict(os.environ, ALSOFT_DRIVERS='null', SDL_AUDIODRIVER='dummy',
           XDG_CACHE_HOME='/tmp/batch03-final/cache')
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
t0 = time.monotonic()
with (OUT / (label + '.stdout')).open('wb') as stdout, (OUT / (label + '.stderr')).open('wb') as stderr:
    try:
        p = subprocess.run(argv, stdout=stdout, stderr=stderr, env=env)
        code = p.returncode
    except OSError as error:
        stderr.write((repr(error) + '\n').encode())
        code = 127
(OUT / (label + '.command.json')).write_text(json.dumps(dict(
    argv=argv, cwd=os.getcwd(), started_utc=start, elapsed_s=time.monotonic()-t0,
    environment_overrides={k:env[k] for k in ('ALSOFT_DRIVERS','SDL_AUDIODRIVER','XDG_CACHE_HOME')},
    exit_code=code), indent=2)+'\n')
print(json.dumps({'label':label,'exit_code':code,'elapsed_s':time.monotonic()-t0}))
sys.exit(code)
