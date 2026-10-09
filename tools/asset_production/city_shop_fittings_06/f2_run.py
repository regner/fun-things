"""One F2 correction pipeline; additive evidence, separate raw streams, no Git/editor."""
import sys,subprocess,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[3];T=Path(__file__).parent;E=R/'docs/assets/production/city_shop_fittings_06-evidence/fix_f2'
source=R/'art/source/models/environment/city_shop_fittings_06/city_shop_fittings_06.blend'
b=['/usr/bin/blender','-b','-noaudio','-t','4'];cap=[sys.executable,str(T/'f2_capture.py')]
def job(name,args):
    subprocess.run(cap+[name]+args,cwd=R,check=True)
def blend(name,script,load=None,tail=[]):
    job(name,b+([str(load)] if load else [])+['--python-exit-code','1','--python',str(T/script)]+tail)
job('pin',b+['--version'])
blend('author','author.py')
blend('export','export.py',source)
job('raw_glb',[sys.executable,str(T/'check_glb.py')])
blend('reexport','export.py',source,['--',str(E/'reexports')])
comparisons=[]
for v in ['single','double']:
    p=R/('art/models/environment/city_shop_fittings_06/city_shop_fittings_06_'+v+'.glb');fresh=E/'reexports'/p.name
    assert p.read_bytes()==fresh.read_bytes()
    comparisons.append(dict(variant=v,byte_identical=True,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(E/'reexport_comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n')
blend('assembly','assembly.py',source)
blend('scratch_correspondence','f2_readback.py')
shutil.copy2(E/'fitted_comparison.blend',E.parent/'fitted_comparison.blend')
blend('close_renders','f2_close_render.py',source,['--',str(E)])
blend('previews','preview.py',E/'fitted_comparison.blend')
print('F2_PIPELINE_COMPLETE')
