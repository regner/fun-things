"""Run isolated asset tools, retaining full output, argv, status and any owned termination."""
import json, subprocess, sys, time, signal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_lights_04-evidence'
label=sys.argv[1]; argv=sys.argv[2:]
start=time.time(); log=E/(label+'.log')
with log.open('w') as stream:
    proc=subprocess.Popen(argv,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    completion=None; terminated=False
    while proc.poll() is None:
        time.sleep(1)
        if 'CITY_LIGHTS_04_COMPLETE' in log.read_text(errors='replace'):
            completion=completion or time.time()
        if (completion and time.time()-completion>20) or time.time()-start>600:
            terminated=True; proc.send_signal(signal.SIGINT)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
    record={'label':label,'argv':argv,'cwd':str(ROOT),'pid':proc.pid,'exit_status':proc.returncode,'seconds':time.time()-start,'completed_marker':bool(completion or 'CITY_LIGHTS_04_COMPLETE' in log.read_text(errors='replace')),'terminated_owned_process':terminated,'log':str(log.relative_to(ROOT))}
p=E/'execution.json'; records=json.loads(p.read_text()) if p.exists() else []
records.append(record);p.write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(record))
sys.exit(0 if proc.returncode==0 else 1)
