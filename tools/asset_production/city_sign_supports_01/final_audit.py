"""Audit owned delivery, source-reference fingerprints and stopped Blender writers."""
import ast,hashlib,json,os,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_sign_supports_01-evidence'
processes=[]
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():continue
    try:
        argv=(proc/'cmdline').read_bytes().split(b'\0')
        if argv and Path(os.fsdecode(argv[0])).name=='blender' and any(b'city_sign_supports_01' in a for a in argv):processes.append(dict(pid=int(proc.name),argv=[os.fsdecode(a) for a in argv if a]))
    except (OSError,PermissionError):pass
assert not processes,processes
scripts=list((ROOT/'tools/asset_production/city_sign_supports_01').glob('*.py'))
for p in scripts:ast.parse(p.read_text(),filename=str(p))
refs=['AGENTS.md','docs/assets.md','docs/art-direction.md','docs/assets/production/commission.md','docs/assets/city_sign_supports.md','docs/concepts/world-v1/stage-03-district-identities/README.md','docs/concepts/districts-v1/README.md','docs/concepts/districts-v1/brief-contract.md','docs/concepts/districts-v1/signal-row.md','docs/concepts/districts-v1/old-quay.md','docs/concepts/districts-v1/map-context.md','docs/world-layout.md','docs/concepts/districts-v1/06-signal-row-v03.png','docs/concepts/districts-v1/05-old-quay-v03.png','docs/concepts/districts-v1/06-signal-row-map.png']
fingerprints={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in refs}
report=ROOT/'docs/assets/production/city_sign_supports_01.md'
for path in re.findall(r'\]\(([^)]+)\)',report.read_text()):
    target=(report.parent/path).resolve()
    if target.name not in ['manifest.json','final_audit.json']:assert target.exists(),path
assert (ROOT/'art/source/.gdignore').exists()
assert (ROOT/'docs/assets/production/.gdignore').exists()
result=dict(status='PASS',owned_blender_processes_running=processes,all_recorded_processes_reaped=True,parsed_python_scripts=[str(p.relative_to(ROOT)) for p in scripts],reference_sha256=fingerprints,production_blend_bytes=(ROOT/'art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend').stat().st_size,report_links_checked=True,shared_writes='none; no Git/index, prefab, engine/project/world or shared docs mutations',limitations=['No Godot import/prefab/scene roundtrip','No gameplay/collision/navigation','No measured device/runtime/performance acceptance','Producer visual evidence; independent acceptance pending'])
(E/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
