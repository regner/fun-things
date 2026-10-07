import gzip, hashlib, json, math, re, subprocess, tarfile
from pathlib import Path

ROOT=Path('/tmp/s04-independent-review/candidate')
OUT=ROOT.parent
E=ROOT/'docs/spikes/s04-evidence'

def raw(p):
    data=p.read_bytes()
    return gzip.decompress(data) if p.suffix=='.gz' else data

def rows(p):
    return [json.loads(l[4:]) for l in raw(p).decode().splitlines() if l.startswith('S04 ')]

def p95(vals):
    return sorted(vals)[math.ceil(len(vals)*.95)-1]

manifest=json.loads((E/'raw-manifest.json').read_text())
for row in manifest:
    data=raw(E/row['path'])
    assert len(data)==row['original_bytes'],row['path']
    assert hashlib.sha256(data).hexdigest()==row['raw_sha256'],row['path']
print('PASS raw receipt count/hash/bytes',len(manifest))

profiles={}
for name in ['baseline','normal','adverse']:
    path=E/'canonical'/name
    host=rows(path/'host/stdout.log.gz'); client=rows(path/'client/stdout.log.gz')
    proxy=[json.loads(l) for l in raw(path/'proxy.jsonl.gz').decode().splitlines()]
    for role in ['host','client']:
        a=raw(path/role/'stdout.log.gz'); b=raw(path/role/'engine.log.gz')
        assert a==b
        assert not re.search(rb'ERROR:|SCRIPT ERROR:|WARNING:',a)
    sim=[r for r in host if r['event']=='simulation']
    app=[r for r in client if r['event']=='apply']
    lookup={(r['pose']['entity'],r['pose']['tick']):r for r in sim}
    errors=[]; ages=[]; jumps=[]; prev={}
    for r in app:
        p=r['pose']; s=lookup.get((p['entity'],p['tick']))
        if s is None: continue
        errors.append(math.dist(r['position'],s['pose']['position']))
        ages.append(r['wall_ms']-s['wall_ms'])
        if p['entity'] in prev and s['local_tick']<600:
            jumps.append(math.dist(prev[p['entity']],r['position']))
        prev[p['entity']]=r['position']
    pulses=[r for r in client if r['event']=='input' and r['index']<=20]
    responses=[]
    for pulse in pulses:
        def changed(frame):
            if pulse['turn']:
                return abs((frame['yaw']-pulse['yaw']+math.pi)%(2*math.pi)-math.pi)>math.radians(.2)
            return abs(math.dist(frame['pose']['velocity'],[0,0,0])-math.dist(pulse['velocity'],[0,0,0]))>.05
        candidates=[r for r in app if r['entity']==2 and
            pulse['time_ms']<=r['time_ms']<pulse['time_ms']+500 and
            r['pose']['sequence']>=pulse['sequence_floor'] and changed(r)]
        assert candidates,pulse
        responses.append(candidates[0]['time_ms']-pulse['time_ms'])
    assert len(responses)==20
    assert not [r for r in client if r['event']=='render']
    # Observe held acknowledgements are simulation outcomes, never one sequence per tick.
    repeated=sum(a['pose']['entity']==b['pose']['entity'] and a['pose']['sequence']==b['pose']['sequence']
        for entity in [1,2] for a,b in zip([r for r in sim if r['pose']['entity']==entity],
                                        [r for r in sim if r['pose']['entity']==entity][1:]))
    assert repeated>100
    durable=[]
    for r in sim:
        assert r['phase']=='post_move_and_slide'
        if r['time_ms']-r['receipt_ms']>267:
            assert r['held']=={'throttle':0.0,'steer':0.0,'brake':0.0,'handbrake':False}
    res=next(r for r in client if r['event']=='resync_applied')
    first=next(r for r in app if r['entity']==2 and r['pose']['control']==2)
    observed=dict(response_p95_ms=p95(responses),response_count=len(responses),
       snapshot_age_p95_ms=p95(ages),snapshot_age_max_ms=max(ages),
       matching_tick_samples=len(errors),matching_tick_install_error_max_m=max(errors),
       update_jump_p95_m=p95(jumps),repeated_held_sequence_intervals=repeated,
       drops=sum(r['event']=='drop' for r in proxy),
       resync_producer_event_ms=res['time_ms'],first_control2_applied_ms=first['time_ms'])
    stored=json.loads((path/'result.json').read_text())
    assert stored['exits']==[0,0]
    measured=stored['measurements']
    assert observed['response_p95_ms']==measured['response_p95_ms']['physics_ms']
    for k in ['snapshot_age_p95_ms','snapshot_age_max_ms','matching_tick_samples',
              'matching_tick_install_error_max_m','update_jump_p95_m']:
        assert observed[k]==measured[k],k
    mismatches=[]
    for p,digest in stored['source_sha256'].items():
        target=ROOT/p
        if p=='project.godot':continue # intentional isolated profile strips addons.
        assert target.exists(),p
        if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            mismatches.append(p)
    observed['candidate_vs_measured_mismatches']=mismatches
    profiles[name]=observed
    print(name,json.dumps(observed))

for name in ['canonical','api']:
    with tarfile.open(E/name/'tested-fixtures.tar.gz') as archive:
        members=[m for m in archive if m.isfile()]
        assert all(not m.name.startswith('/') and '..' not in Path(m.name).parts for m in members)
        print(name,'tested archive entries',len(members))

for asset in ['s04_car','s04_track']:
    data=(ROOT/f'art/models/spikes/{asset}.glb').read_bytes()
    size=int.from_bytes(data[12:16],'little'); model=json.loads(data[20:20+size])
    assert model['asset']['version']=='2.0'
    assert not any(model.get(k) for k in ['images','animations','skins','extensionsUsed'])
    node_names=[n.get('name') for n in model['nodes']]
    print(asset,'nodes',node_names,'meshcount',len(model['meshes']))

(OUT/'raw-audit.json').write_text(json.dumps(profiles,indent=2)+'\n')
