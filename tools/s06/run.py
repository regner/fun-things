"""Isolated bounded S06 body/topology proof, fingerprints, raw logs and independent geometry."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from script_checks import checked_command,engine_version,environment


def fingerprints(root):
    paths=list((root/'tests/fixtures/s06').glob('*'))
    paths+=list((root/'art/models/spikes').glob('s06_*'))
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot',required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--content-only',action='store_true')
    args=parser.parse_args()
    output=(args.output or Path(tempfile.mkdtemp(prefix='s06-'))).resolve()
    assert not output.is_relative_to(ROOT)
    output.mkdir(parents=True,exist_ok=True)
    assert not any(output.iterdir()),'fresh external output required'
    print('S06 evidence:',output,flush=True)
    version=engine_version(args.godot)
    project=output/'project';project.mkdir()
    for spike in ['s02','s03','s04','s06']:
        shutil.copytree(ROOT/'tests/fixtures'/spike,project/'tests/fixtures'/spike)
    models=project/'art/models/spikes';models.mkdir(parents=True)
    for spike in ['s02','s04','s06']:
        for path in (ROOT/'art/models/spikes').glob(spike+'_*'):
            if path.is_file():shutil.copy2(path,models/path.name)
    settings=(ROOT/'project.godot').read_text()
    for section in ['autoload','editor_plugins']:
        settings=re.sub(r'(?ms)^\['+section+r'\]\n.*?(?=^\[|\Z)','',settings)
    settings=re.sub(r'^config/icon=.*\n','',settings,flags=re.M)
    (project/'project.godot').write_text(settings)
    # Editor-only harnesses reference immutable editor bridges; retain dependencies for import.
    shutil.copytree(ROOT/'tools/s01',project/'tools/s01')
    shutil.copytree(ROOT/'tools/s02',project/'tools/s02')
    shutil.copytree(ROOT/'tools/s04',project/'tools/s04')
    shutil.copytree(ROOT/'tools/s06',project/'tools/s06')
    env=environment(output/'user')
    before=fingerprints(project)
    commands=[]
    cmd=[args.godot,'--headless','--path',str(project)]
    command=cmd+['--editor','--import','--quit','--log-file',str(output/'import.engine.log')]
    commands.append(command)
    imported=checked_command(command,output/'import.log',env,60)
    command=cmd+['--script','res://tests/fixtures/s06/proof.gd','--log-file',str(output/'proof.engine.log')]
    if args.content_only:command+=['--','--content-only']
    commands.append(command)
    outcomes=checked_command(command,output/'proof.log',env,75) if imported else False
    unchanged=before==fingerprints(project)
    result_path=project/'s06-result.json'
    result=json.loads(result_path.read_text()) if result_path.exists() else None
    summary={'engine':version,'import':imported,'outcomes':outcomes,
             'saved_files_unchanged':unchanged,'commands':commands,
             'result_available':result is not None,'source_fingerprints':before}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['source_fingerprints']}))
    return 0 if imported and outcomes and unchanged and result and not result['failures'] else 1


if __name__=='__main__':
    raise SystemExit(main())
