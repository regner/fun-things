"""Verify candidate completeness, retained diagnostics and unchanged comparison assets."""
import json,hashlib,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_05-evidence'; T=R/'tools/asset_production/city_planting_05'
expected={'city_planting_05_short_tuft.glb','city_planting_05_spreading_clump.glb'}
assert {p.name for p in (R/'art/models/environment/city_planting_05').glob('*.glb')}==expected
assert {p.name for p in (R/'art/source/models/environment/city_planting_05').glob('*')}=={'city_planting_05.blend'}
for p in T.glob('*.py'):compile(p.read_text(),str(p),'exec')
record=R/'docs/assets/production/city_planting_05.md'
for target in re.findall(r'\]\(([^)]+)\)',record.read_text()):
    if target=='city_planting_05-evidence/final_audit.json':continue  # Written below.
    assert (record.parent/target).resolve().exists(),target
ledger=json.loads((E/'commands.json').read_text())
assert len({r['name'] for r in ledger})==len(ledger)
for row in ledger:
    assert (E/row['raw_log']).is_file() and row['argv']
    if row['name'] not in {'requested_version','check_glb','final_audit'}:assert row['exit_code']==0,row['name']
receipted={row['raw_log'] for row in ledger}
logs={p.name for p in E.glob('*.log')}
assert receipted<=logs
# The runner writes this audit's receipt after its process exits.
unreceipted=logs-receipted
assert len(unreceipted)<=1 and all(n.startswith('final_audit') for n in unreceipted)
preview=json.loads((E/'preview_checks.json').read_text())
for row in preview['inputs']:
    p=R/row['path']; assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
assert abs(preview['camera']['vertical_fov_deg']-42)<.001
screens={k:v['gameplay_pixel_bounds_bottom_left'] for k,v in preview['measurements'].items()}
gaps={v:screens['courier'][0][0]-screens[v][1][0] for v in ['short_tuft','spreading_clump']}
assert min(gaps.values())>0
actor=preview['measurements']['courier']['blender_world_bounds_m']
assert 0<=actor[0][2]<.01 and 1.8<actor[1][2]<1.9
comparison=json.loads((E/'reexport_comparison.json').read_text())
for row in comparison:
    runtime=R/row['runtime']; scratch=R/row['reexport']
    assert runtime.read_bytes()==scratch.read_bytes()
    assert hashlib.sha256(runtime.read_bytes()).hexdigest()==row['sha256']
# Only task-specific Blender processes are relevant; other workers remain untouched.
ps=subprocess.check_output(['ps','-eo','pid,comm,args'],text=True)
owned=[line for line in ps.splitlines()[1:] if len(line.split(None,2))==3 and line.split(None,2)[1].startswith('blender') and 'city_planting_05/' in line]
assert not owned,owned
report={'result':'PASS','scope':'producer source/export handoff only','runtime_variants':sorted(expected),'all_owned_blender_writers_stopped':True,'comparison_assets_unchanged':True,'actor_render_geometry_bounds_blender_m':actor,'gameplay_actor_horizontal_gap_px':gaps,'measured_weed_pixel_extents':{v:[screens[v][1][i]-screens[v][0][i] for i in range(2)] for v in gaps},'scripts_compile':True,'report_links_exist':True,'raw_logs_have_command_receipts':True,'retained_nonzero_exits':{r['name']:r['exit_code'] for r in ledger if r['exit_code']},'pending':['Godot import','prefab/inherited save roundtrip','collision policy and movement','runtime camera','device/performance','independent acceptance']}
(E/'final_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('FINAL_AUDIT_PASS',json.dumps(report,indent=2))
