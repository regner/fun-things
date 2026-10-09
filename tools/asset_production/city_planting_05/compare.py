"""Require saved-source exports to match both runtime GLBs byte-for-byte."""
from pathlib import Path
import hashlib, json
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_05-evidence'
rows=[]
for variant in ['short_tuft','spreading_clump']:
    name='city_planting_05_'+variant+'.glb'
    runtime=R/'art/models/environment/city_planting_05'/name
    scratch=E/'reexport'/name
    assert runtime.read_bytes()==scratch.read_bytes(),name
    rows.append({'runtime':str(runtime.relative_to(R)),'reexport':str(scratch.relative_to(R)),'byte_identical':True,'bytes':runtime.stat().st_size,'sha256':hashlib.sha256(runtime.read_bytes()).hexdigest()})
(E/'reexport_comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
print('SAVED_SOURCE_REEXPORT_BYTE_IDENTICAL',json.dumps(rows))
