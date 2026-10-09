import pathlib,json,hashlib
O=pathlib.Path(__file__).resolve().parent
terminal=['review-file-index.json','review-index-readback.json','index_review.command.json','index_review.stdout','index_review.stderr']
files=sorted(p for p in O.rglob('*') if p.is_file());importer=[p for p in files if p.suffix=='.import'];expected=[p for p in files if str(p.relative_to(O)) not in terminal and p not in importer]
def row(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(O)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
r=dict(scope='Narrow additive SAME-reviewer F3 packet only; older payloads referenced in verified-file-index.json',expected_paths=[str(p.relative_to(O)) for p in expected],files=[row(p) for p in expected],self_exclusions=terminal,importer_owned_sidecars_excluded=[row(p) for p in importer])
p=O/'review-file-index.json';p.write_text(json.dumps(r,indent=2)+'\n');raw=p.read_bytes();read=json.loads(raw)
assert set(read['expected_paths'])=={e['path'] for e in read['files']}
for e in read['files']:assert row(O/e['path'])==e
checks=dict(index_bytes=len(raw),index_sha256=hashlib.sha256(raw).hexdigest(),payload_count=len(expected),payload_set_complete=True,all_payload_bytes_sha_match=True,terminal_receipts_self_excluded=terminal,importer_exclusions=len(importer))
(O/'review-index-readback.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
