"""Resume only unattempted runtime phases after a retained offline analyzer correction."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'tools'))
from run_s08_linux import launch, network, write_json, identity

task=Path(__file__).parent
initial=json.loads((task/'observation.json').read_text())
assert initial['completed']==['stage','import','export']
assert initial['failure']=="RuntimeError('unexpected/encrypted PCK header')"
assert not (task/'asset').exists() and not (task/'enet').exists()
assert (task/'logical-export-map.json').is_file()
folder=task/'export-folder'
record={'ok':False,'input_revision':initial['input_revision'],
        'completed':initial['completed']+['package inspection'],
        'retained_analyzer_failure':'analyzer-initial-failure.json',
        'analyzer_correction':'exact source PACK_FORMAT_VERSION_V4; no engine repeat'}
try:
    asset=launch(task,'asset',[str(folder/'FunThingsS08.x86_64'),'--headless',
                              '--script','res://s08_receipt.gd'],15,folder)
    rows=[json.loads(line[4:]) for line in (asset/'stdout.log').read_text().splitlines()
          if line.startswith('S08 ')]
    write_json(asset/'result.json',rows)
    if len(rows)!=1 or rows[0].get('ok') is not True:
        raise RuntimeError('asset receipt incomplete/failed')
    if rows[0]['executable_sha256'] != identity(folder/'FunThingsS08.x86_64')['sha256']:
        raise RuntimeError('runtime executable identity mismatch')
    record['completed'].append('asset')
    network(task)
    record['completed'].append('ENet')
    record['ok']=True
except Exception as error:
    record['failure']=repr(error)
finally:
    write_json(task/'observation.json',record)
print(json.dumps(record))
raise SystemExit(0 if record['ok'] else 1)
