"""Independently read every frozen Git blob and compare producer sets and working bytes."""
import hashlib
import json
import pathlib
import subprocess

CANDIDATE = '028775618c4493ca672646e6e37fdc3c83e0e313'
PARENT = '10ddb64d16e6cb2f137923a31d3ca14991468f7d'
BASE = '66400c26a01bf917dfe631af4762c2b444d9c48f'
OUT = pathlib.Path(__file__).resolve().parent
SCRATCH = pathlib.Path('/tmp/batch03-independent')
SCRATCH.mkdir(exist_ok=True)

def git(*argv):
    return subprocess.check_output(['git', *argv])

def blob(path):
    return git('show', CANDIDATE+':'+path)

def sha(data):
    return hashlib.sha256(data).hexdigest()

readback_path = 'docs/assets/production/batch_03-evidence/source-readback.json'
readback = json.loads(blob(readback_path))
frozen = set(readback['exact_frozen_paths'])
assert len(frozen) == len(readback['exact_frozen_paths'])
index, record_results, union = {}, [], set()
for rec in readback['records']:
    ident = rec['id']
    path = f'docs/assets/production/{ident}-evidence/manifest.json'
    data = blob(path)
    manifest = json.loads(data)
    entries = manifest['files']
    expected = {e['path']:e for e in entries}
    assert len(expected) == len(entries)
    actual = {}
    for p,e in expected.items():
        b = blob(p)
        w = pathlib.Path(p).read_bytes()
        actual[p] = dict(path=p, bytes=len(b), sha256=sha(b),
                         working_bytes=len(w), working_sha256=sha(w),
                         expected_bytes=e['bytes'], expected_sha256=e['sha256'],
                         expected_matches=(len(b)==e['bytes'] and sha(b)==e['sha256']),
                         working_matches=(b==w))
    index.update(actual)
    index[path] = dict(path=path, bytes=len(data), sha256=sha(data),
                       working_matches=pathlib.Path(path).read_bytes()==data,
                       expected_manifest_sha256=rec['manifest_sha256'],
                       expected_matches=sha(data)==rec['manifest_sha256'])
    union.update(expected)
    union.add(path)
    owned_roots = [f'art/source/models/environment/{ident}/',
                   f'art/models/environment/{ident}/', f'tools/asset_production/{ident}/',
                   f'docs/assets/production/{ident}-evidence/']
    tree_paths = git('ls-tree','-r','--name-only',CANDIDATE).decode().splitlines()
    observed = {p for p in tree_paths if any(p.startswith(r) for r in owned_roots)}
    observed.add(f'docs/assets/production/{ident}.md')
    missing = sorted((set(expected)|{path})-observed)
    extra = sorted(observed-(set(expected)|{path}))
    record_results.append(dict(id=ident, expected_count=len(expected),
        expected_count_matches=len(expected)==rec['producer_payload_count'],
        missing=missing, extra=extra, all_hashes_match=all(e['expected_matches'] for e in actual.values()),
        all_working_match=all(e['working_matches'] for e in actual.values())))
    # Freeze only current source/output buffers, not historical packs.
    for p in expected:
        if p.startswith('art/'):
            target = SCRATCH / 'frozen' / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob(p))
    for name in ('mounted_frontage_scratch.blend', 'fitted_comparison.blend'):
        p=f'docs/assets/production/{ident}-evidence/{name}'
        if p in expected:
            target=SCRATCH/'frozen'/p
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(blob(p))
summary = dict(candidate=CANDIDATE,parent=PARENT,original_base=BASE,
    actual_head=git('rev-parse','HEAD').decode().strip(),
    actual_parent=git('rev-parse',CANDIDATE+'^').decode().strip(),
    original_base_is_ancestor=subprocess.run(['git','merge-base','--is-ancestor',BASE,CANDIDATE]).returncode==0,
    frozen_count=len(frozen), union_count=len(union),
    frozen_minus_manifests=sorted(frozen-union), manifests_minus_frozen=sorted(union-frozen),
    parent_delta=git('diff','--name-status',PARENT,CANDIDATE).decode().splitlines(),
    original_base_delta=git('diff','--name-status',BASE,CANDIDATE).decode().splitlines(),
    records=record_results,
    untracked=git('ls-files','--others','--exclude-standard').decode().splitlines())
(OUT/'frozen-file-index.json').write_text(json.dumps(dict(summary=summary,files=[index[k] for k in sorted(index)]),indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('parent_delta','original_base_delta','untracked')},indent=2))
assert frozen==union
assert all(x['expected_matches'] and x['working_matches'] for x in index.values())
assert all(not r['extra'] and not r['missing'] and r['expected_count_matches'] for r in record_results)
# Read-only interface .01, needed to check the existing shell assembly, is not a reviewed ID.
ref='city_shop_fittings_01'
for prefix,ext in [('art/source/models/environment','blend'),('art/models/environment','glb')]:
    p=f'{prefix}/{ref}/{ref}.{ext}'
    target=SCRATCH/'frozen'/p
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(blob(p))
(OUT/'reference-file-index.json').write_text(json.dumps([dict(path=p,bytes=len(blob(p)),sha256=sha(blob(p))) for p in [f'art/source/models/environment/{ref}/{ref}.blend',f'art/models/environment/{ref}/{ref}.glb']],indent=2)+'\n')
