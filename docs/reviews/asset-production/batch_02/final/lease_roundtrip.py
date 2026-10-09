"""Prepare/verify a bounded private-editor roundtrip against exact candidate bytes."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production'); OUT=Path(__file__).resolve().parent
C='10ddb64d16e6cb2f137923a31d3ca14991468f7d'
paths=['scenes/prefabs/environment/city_planting_04_compact.tscn',
 'scenes/prefabs/environment/city_planting_04_broad.tscn',
 'tests/fixtures/asset_production/batch_02_camera.tscn']
def original(p):return subprocess.check_output(['git','show',C+':'+p],cwd=ROOT)
def digest(data):return hashlib.sha256(data).hexdigest()
if sys.argv[1]=='prepare':
    assert json.loads((OUT/'host-editor-lease-guard.json').read_text())['verified']
    rows=[]; requests=[]
    for p in paths:
        data=original(p); assert data==(ROOT/p).read_bytes()
        rows.append(dict(path=p,bytes=len(data),before_sha256=digest(data)))
        for method,params in [('scene.open',{'file_path':'res://'+p}),('editor.save_scene',{}),
          ('scene.close',{'file_path':'res://'+p}),('scene.open',{'file_path':'res://'+p}),('editor.save_scene',{})]:
            requests.append(dict(method=method,params=params))
    requests.extend([dict(method='scene.open',params=dict(file_path='res://tools/asset_production/integration/inspector.tscn')),
      dict(method='game.stop',params={}),dict(method='node.call_method',params=dict(node_path='.',method_name='context'))])
    (OUT/'live-roundtrip-before.json').write_text(json.dumps(rows,indent=2)+'\n')
    (OUT/'live-roundtrip-requests.json').write_text(json.dumps(requests,indent=2)+'\n')
    print(json.dumps(dict(prepared_paths=paths,request_count=len(requests))))
else:
    requests=json.loads((OUT/'live-roundtrip-requests.json').read_text())
    results=[json.loads(x) for x in (OUT/'live-roundtrip.stdout').read_text().splitlines()]
    assert len(results)==len(requests)
    for request,response in zip(requests,results):
        assert request['method']==response['method']
        assert response['result']['result']['success'] is True
        if request['method']=='scene.close': assert response['result']['result']['unsaved_changes_discarded'] is False
    context=results[-1]['result']['result']['result']
    assert context['pid']==195352 and context['project']==str(ROOT)+'/' and context['engine']=='4.8-dev7 (official)'
    assert context['unsaved']=='PackedStringArray()'
    assert results[-2]['result']['result']['was_running'] is False
    before=json.loads((OUT/'live-roundtrip-before.json').read_text())
    for row in before:
        actual=(ROOT/row['path']).read_bytes()
        assert actual==original(row['path']) and digest(actual)==row['before_sha256']
        row['after_sha256']=digest(actual); row['candidate_byte_identical']=True
    result=dict(roundtrip_paths=before,final_context=context,runtime_stopped=True,
      final_selected_scene='res://tools/asset_production/integration/inspector.tscn',saved_diffs=[],lease='released')
    (OUT/'live-roundtrip-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
