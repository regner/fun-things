from pathlib import Path
import difflib,json,sys
sys.path.insert(0,str(Path.cwd()/'tools'))
from run_s05 import stage, records
from script_checks import checked_command,environment,engine_version
root=Path('/tmp/s05-negative-retirement'); root.mkdir()
project=stage(root)
p=project/'tests/fixtures/s05/damage.gd'
before=p.read_text(); after=before.replace('if shot.sequence <= shooter.sequence:', 'if shot.sequence <= shooter.sequence and not jobs.is_empty():')
assert after!=before
p.write_text(after)
(root/'mutation.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='damage-original.gd',tofile='damage-negative.gd')))
godot='/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
engine_version(godot)
commands=[[godot,'--headless','--editor','--path',str(project),'--import','--quit'],[godot,'--headless','--path',str(project),'--log-file',str(root/'engine.log'),'res://tests/fixtures/s05/boot.tscn','--','--role=api']]
env=environment(root/'user')
assert checked_command(commands[0],root/'import.log',env)
passed=checked_command(commands[1],root/'stdout.log',env,timeout=12)
failures=[r for r in records(root/'stdout.log') if r['event']=='failure']
report={'ok':not passed and any(r['message']=='retired ShotId rejected' for r in failures),'mutated_run_passed':passed,'failures':failures,'commands':commands}
(root/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
assert report['ok']
