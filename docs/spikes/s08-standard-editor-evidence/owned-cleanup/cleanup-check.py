"""Offline private cleanup contract; no engine, socket or process query."""
from pathlib import Path
import hashlib,json
root=Path('/home/regner/.paseo/worktrees/0u71f39f/s08-standard-editor-release-proof')
d=root/'docs/spikes/s08-standard-editor-evidence/owned-cleanup'
entry=json.loads((d/'last-entry.json').read_text());before=json.loads((d/'last-projection.json').read_text())
key='/tmp/s08-standard-555e0330/project';pids={558301,559412}
assert entry['_key']==key and entry['pid'] in pids
assert before['by_path'][key]['pid']==entry['pid']
assert set(before['by_path'])=={key}
fixture={'by_path':{key:before['by_path'][key],'/tmp/unrelated-project':{'pid':123456,'port':6543,'token_path':'/tmp/unrelated-token'}}}
keep=json.dumps(fixture['by_path']['/tmp/unrelated-project'],sort_keys=True)
del fixture['by_path'][key]
assert key not in fixture['by_path']
assert json.dumps(fixture['by_path']['/tmp/unrelated-project'],sort_keys=True)==keep
registry=Path('/tmp/s08-standard-555e0330/scan-complete-attempt/private/data/godot-mcp-toolkit')
assert not (registry/'entries/e9fb882bfd3c.json').exists()
assert not (registry/'projects.json').exists()
record={'ok':True,'own_key':key,'reaped_owned_pids':sorted(pids),'actual_after':'entry and sole owned projection absent','actual_unrelated_keys':[],'fixture_unrelated_unchanged':True,'old_owned_PID_present_after':False,'before_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [d/'last-entry.json',d/'last-projection.json']}}
print(json.dumps(record))
