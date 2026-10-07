"""Independent finite review checks; writes only to this fresh review directory."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import itertools
import json
import re
import shutil
import subprocess

ROOT = Path.cwd()
OUT = Path('/tmp/s03-s-compatibility-review')
BASE = '04f16d332636200e71e74862f64282224774d077'
HEAD = '64825b51e92e9b5f0eb94a5be5dda1f57cdb0f66'
PREP = '6a012de162b0d65cdf0c77b2914788ad56fbecf1'

def git(*args):
    return subprocess.check_output(['git', *args], timeout=15)

assert git('rev-parse', 'HEAD').decode().strip() == HEAD
assert git('rev-parse', 'refs/heads/main').decode().strip() == BASE
assert not git('status', '--porcelain=v1', '--untracked-files=all')
assert not git('rev-list', '--merges', BASE+'..'+HEAD)
assert git('rev-list', '--count', BASE+'..'+HEAD).strip() == b'1'
subprocess.run(['git','merge-base','--is-ancestor',BASE,HEAD], check=True, timeout=15)
diff = git('diff', BASE, HEAD)
(OUT/'candidate.diff').write_bytes(diff)
subprocess.run(['git','diff','--check',BASE,HEAD],check=True,timeout=15)
changed = git('diff','--name-only',BASE,HEAD).decode().splitlines()
allowed = {'TODO.md','docs/spikes/s03-s.md','docs/spikes/s03-s-compatibility.md',
           'tools/probe_s03_s_compatibility.py'}
assert len(changed) == 20
assert all(p in allowed or p.startswith('docs/spikes/s03-s-compatibility-evidence/')
           for p in changed)
before = git('ls-tree','-r',BASE).decode().splitlines()
after = set(git('ls-tree','-r',HEAD).decode().splitlines())
preserved = [x for x in before if x.split('\t')[1] not in changed]
assert all(x in after for x in preserved)
for row in preserved:
    path = row.split('\t')[1]
    assert (ROOT/path).read_bytes() == git('show',BASE+':'+path), path
old = git('show',BASE+':TODO.md').decode()
new = (ROOT/'TODO.md').read_text()
start = '- [ ] **S03-S —'
end = '- [ ] **S03-R —'
assert old.split(start)[0] == new.split(start)[0]
assert old.split(end)[1] == new.split(end)[1]
assert len(re.findall(r'^- \[ \] \*\*',new,re.M)) == 27
assert 'full S03-S remains OPEN' in new.split(start)[1].split(end)[0]
prep_doc = git('show',PREP+':docs/spikes/s03-s.md')
assert (ROOT/'docs/spikes/s03-s.md').read_bytes().startswith(prep_doc)
prep_paths = git('ls-tree','-r','--name-only',PREP,'docs/spikes/s03-s-evidence',
                 'docs/reviews/s03-s-preparation-review.md').decode().splitlines()
assert all((ROOT/p).read_bytes() == git('show',PREP+':'+p) for p in prep_paths)
native = json.loads((ROOT/'docs/spikes/s03-s-evidence/provenance.json').read_text())
for row in native['native']:
    assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256']
assert len(native['native']) == 22
for path in changed:
    data = (ROOT/path).read_bytes()
    assert b'\r' not in data and data.endswith(b'\n')
    if path.endswith('.json'):
        json.loads(data)
    if path.endswith('.py'):
        ast.parse(data, filename=path)
assert json.loads((OUT/'probe.json').read_text()) == json.loads(
    (ROOT/'docs/spikes/s03-s-compatibility-evidence/probe.json').read_text())
print('PASS exact frozen HEAD/base, clean status, one linear commit, 20 scoped paths')
print(f'PASS {len(preserved)} unaffected base mode/blob entries and working bytes')
print(f'PASS 27 TODO blocks; all bytes outside S03-S unchanged; {len(prep_paths)} accepted preparation paths retained')
print('PASS all 22 native hashes; JSON/LF/newline/Python AST; exact probe reproduction')

spec = importlib.util.spec_from_file_location('bounded_probe', ROOT/'tools/probe_s03_s_compatibility.py')
module = importlib.util.module_from_spec(spec)
# Suppress import bytecode writes in the original checkout.
exec(compile((ROOT/'tools/probe_s03_s_compatibility.py').read_bytes(),
             str(ROOT/'tools/probe_s03_s_compatibility.py'),'exec'), module.__dict__)
cases = 0
alphabet = [(lane,n) for lane in (2,3) for n in (1,2,3)]
for count in range(5):
    for trace in itertools.product(alphabet, repeat=count):
        actual = module.ordered(list(trace))
        # Independent prefix-record expectation and lane erasure invariance.
        expected = [row for i,row in enumerate(trace) if all(
            earlier[0] != row[0] or earlier[1] < row[1] for earlier in trace[:i])]
        assert actual == expected
        for lane in (2,3):
            projected = [row for row in trace if row[0] == lane]
            assert [row for row in actual if row[0] == lane] == module.ordered(projected)
        cases += 1
print(f'PASS {cases} finite traces: duplicates/reordering/loss prefixes and independent stream projection')

# Reproduce failure on independent mutated scratch bytes; no candidate writes.
bad = OUT/'mutated-sources'
shutil.copytree(OUT/'sources',bad)
path = bad/'godotsteam.cpp'
path.write_bytes(path.read_bytes()+b'\n')
result = subprocess.run(['python3',str(ROOT/'tools/probe_s03_s_compatibility.py'),
                         '--source-dir',str(bad)],capture_output=True,text=True,timeout=15)
(OUT/'negative-hash.stdout').write_text(result.stdout)
(OUT/'negative-hash.stderr').write_text(result.stderr)
assert result.returncode != 0 and 'AssertionError: godotsteam.cpp' in result.stderr
assert not result.stdout
print(f'PASS modified-source guard: exit {result.returncode} before emitting interpreted facts')

selected = json.loads((OUT/'registration/registration-selected.json').read_text())
committed = json.loads((ROOT/'docs/spikes/s03-s-compatibility-evidence/registration-selected.json').read_text())
for key in selected:
    if key != 'commands':
        assert selected[key] == committed[key],key
for name in ('version','registration'):
    assert (OUT/'registration'/f'{name}.log').read_bytes() == (
        ROOT/'docs/spikes/s03-s-compatibility-evidence'/f'{name}.log').read_bytes()
assert selected['auto_init'] is False and selected['max_channels'] == 4
assert selected['version'] == '4.23'
for name in ('sendMessages','sendMessageToConnection'):
    assert not any(a['name'] == 'lane' for a in selected['methods'][name]['args'])
print('PASS fresh registered method/signal/virtual/getter projection and logs identical excluding scratch command paths')

for operation in ('rebase-merge','rebase-apply','MERGE_HEAD','CHERRY_PICK_HEAD','index.lock'):
    assert not Path(git('rev-parse','--git-path',operation).decode().strip()).exists()
assert not git('status','--porcelain=v1','--untracked-files=all')
receipt = {'head':HEAD,'base':BASE,'clean':True,'scoped_paths':changed,
           'preserved_base_entries':len(preserved),'prep_paths':prep_paths,
           'native_hashes':22,'finite_traces':cases,'negative_exit':result.returncode,
           'registration_only':True,'native_delivery':False,'native_lifecycle':False}
(OUT/'audit-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS final clean HEAD/base and no Git operation/lock')
