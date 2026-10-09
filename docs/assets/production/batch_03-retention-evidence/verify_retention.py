"""Verify exact frozen engine bytes, complete final review retention and live-log isolation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CANDIDATE = '1031a3e1e66a404f67fa1a3857c4888d05f10d1e'
ENGINE = ROOT / 'docs/assets/production/batch_03-evidence/engine-artifact-index.json'
review = ROOT / 'docs/reviews/asset-production/batch_03/final'
index = json.loads(ENGINE.read_text())
engine_rows = []
for row in index['files']:
    data = (ROOT / row['path']).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
    frozen = subprocess.check_output(['git','show',CANDIDATE+':'+row['path']],cwd=ROOT)
    assert data == frozen, row['path']
    engine_rows.append(row)
engine_blob = subprocess.check_output(['git','show',CANDIDATE+':'+str(ENGINE.relative_to(ROOT))],cwd=ROOT)
assert ENGINE.read_bytes() == engine_blob
assert len(engine_rows) == 299
engine_rows.append({'path':str(ENGINE.relative_to(ROOT)),'bytes':len(engine_blob),
                    'sha256':hashlib.sha256(engine_blob).hexdigest()})
rindex_path = review/'review-file-index.json'
rindex = json.loads(rindex_path.read_text())
assert len(rindex['files']) == 193
assert set(r['path'] for r in rindex['files']) == set(rindex['expected_paths'])
review_rows = []
for row in rindex['files']:
    data = (review/row['path']).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
    review_rows.append(dict(row,path=str((review/row['path']).relative_to(ROOT))))
assert len(rindex['self_exclusions']) == 5
for path in rindex['self_exclusions']:
    p = review/path
    data = p.read_bytes()
    review_rows.append({'path':str(p.relative_to(ROOT)),'bytes':len(data),
                       'sha256':hashlib.sha256(data).hexdigest(),'terminal_self_exclusion':True})
terminal = json.loads((review/'review-index-readback.json').read_text())
assert terminal['index_sha256'] == hashlib.sha256(rindex_path.read_bytes()).hexdigest()
expected = set(rindex['expected_paths']) | set(rindex['self_exclusions'])
actual = {str(p.relative_to(review)) for p in review.rglob('*') if p.is_file()}
assert expected <= actual
extras = sorted(actual-expected)
assert all(p.endswith(('.import','.gd.uid')) for p in extras)
isolation = json.loads((OUT/'isolation.json').read_text())
pid = isolation['current_launch']['pid']
assert os.readlink(f'/proc/{pid}/cwd') == str(ROOT)
assert os.readlink(f'/proc/{pid}/exe') == isolation['current_launch']['argv'][0]
assert Path(f'/proc/{pid}/cmdline').read_text().split('\0')[:-1] == isolation['current_launch']['argv']
fds = {str(n):os.readlink(f'/proc/{pid}/fd/{n}') for n in (1,2)}
assert all(p == isolation['live_log'] for p in fds.values())
assert not any(str(ROOT) in p for p in fds.values())
rows = [json.loads(s) for s in (OUT/'final-context.stdout.jsonl').read_text().splitlines()]
context = rows[1]['result']['result']['result']
assert context['pid'] == pid and context['unsaved'] == 'PackedStringArray()'
assert rows[2]['result']['result']['was_running'] is False
owned_socket_ids = set()
for fd in Path(f'/proc/{pid}/fd').iterdir():
    try:
        target = os.readlink(fd)
    except FileNotFoundError:
        continue
    if target.startswith('socket:['):
        owned_socket_ids.add(target[8:-1])
listeners = {}
for filename in ['tcp','tcp6']:
    for line in Path('/proc/net/'+filename).read_text().splitlines()[1:]:
        fields = line.split()
        if fields[3] == '0A':
            listeners[int(fields[1].split(':')[-1],16)] = fields[9]
assert listeners[22650] in owned_socket_ids and listeners[22652] in owned_socket_ids
assert 22651 not in listeners
old = Path(f"/proc/{isolation['old_launch']['pid']}/status")
assert not old.exists() or 'State:\tZ' in old.read_text()
assert subprocess.check_output(['git','diff','--name-only',CANDIDATE],cwd=ROOT) == b''
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT) == b''
summary = {'candidate':CANDIDATE,'complete_engine_expected_set':engine_rows,
    'engine_path_count':len(engine_rows),'all_engine_git_working_bytes_sha_match':True,
    'final_review_expected_set':review_rows,'review_payload_count':193,
    'review_terminal_self_exclusions':5,'review_index_sha256':terminal['index_sha256'],
    'all_review_bytes_sha_match':True,'unlisted_importer_metadata_not_staged':extras,
    'live_editor':{'pid':pid,'fds':fds,'ports':{'editor':22650,'runtime_stopped':22651,'lsp':22652},
                   'context':context,'runtime_listener_absent':True},
    'tracked_git_diff_empty':True,'git_index_empty':True,
    'scope':'F3 evidence retention only; no asset/scene/source changes or transferred downstream acceptance'}
(OUT/'retention-readback.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'engine_paths':300,'review_payloads':193,'terminal_receipts':5,
                  'live_editor_pid':pid,'runtime_stopped':True,'all_checks_passed':True}))
