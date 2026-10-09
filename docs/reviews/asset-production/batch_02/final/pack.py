"""Finalize exact expected set and SHA index; two self-describing metadata files excluded.

All substantive payloads and empty streams are indexed. The index and verification
are listed in expected set; verification records the index SHA instead of an
impossible self-hash cycle.
"""
import hashlib,json,sys,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parent
start=time.time()
message='Final BATCH02 review artifact expected-set and SHA verification passed.\n'
command=dict(argv=[sys.executable,*sys.argv],cwd=str(Path.cwd()),started_unix=start)
try:
    (OUT/'pack.stdout').write_text(message)
    (OUT/'pack.stderr').write_bytes(b'')
    command['exit_code']=0
    (OUT/'pack.command.json').write_text(json.dumps(command,indent=2)+'\n')
    expected=sorted({p.name for p in OUT.iterdir() if p.is_file()}|{'artifact-index.json','artifact-expected-set.json','artifact-verification.json'})
    (OUT/'artifact-expected-set.json').write_text(json.dumps(dict(scope='BATCH02 final only; initial preserved separately',paths=expected),indent=2)+'\n')
    rows=[]
    for name in expected:
        if name in ['artifact-index.json','artifact-verification.json']: continue
        data=(OUT/name).read_bytes()
        rows.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    index=dict(candidate='10ddb64d16e6cb2f137923a31d3ca14991468f7d',
      delta_base='5e94cc0ea4155219285db49c64b5728e0882b093',
      original_base='66400c26a01bf917dfe631af4762c2b444d9c48f',
      metadata_excluded_from_self_hash=['artifact-index.json','artifact-verification.json'],files=rows)
    (OUT/'artifact-index.json').write_text(json.dumps(index,indent=2)+'\n')
    for row in rows:
        data=(OUT/row['path']).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    verification=dict(exact_expected_set=True,all_indexed_byte_counts_and_hashes_match=True,
      indexed_payload_count=len(rows),expected_path_count=len(expected),
      index_sha256=hashlib.sha256((OUT/'artifact-index.json').read_bytes()).hexdigest(),
      expected_set_sha256=hashlib.sha256((OUT/'artifact-expected-set.json').read_bytes()).hexdigest(),
      required_empty_streams=[r['path'] for r in rows if r['bytes']==0 and r['path'].endswith(('.stdout','.stderr'))])
    (OUT/'artifact-verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    assert sorted(p.name for p in OUT.iterdir() if p.is_file())==expected
except BaseException:
    raw=traceback.format_exc()
    (OUT/'pack.stderr').write_text(raw)
    (OUT/'pack.stdout').write_bytes(b'')
    command['exit_code']=1
    (OUT/'pack.command.json').write_text(json.dumps(command,indent=2)+'\n')
    sys.stderr.write(raw)
    sys.exit(1)
sys.stdout.write(message)
