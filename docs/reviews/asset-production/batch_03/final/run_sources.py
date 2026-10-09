"""Run each frozen saved Blender file in a separate bounded CLI process."""
from pathlib import Path
import subprocess
import sys
OUT=Path(__file__).resolve().parent
ids=['city_shop_fittings_'+i for i in ('02','03','05','06','07','08')]+['city_small_shop_shells_01']
exits=[]
for ident in ids:
    source=Path('/tmp/batch03-final/frozen/art/source/models/environment')/ident/(ident+'.blend')
    args=[sys.executable,str(OUT/'run_check.py'),ident+'_source','/usr/bin/blender','-b','-noaudio','-t','4',str(source),'--python-exit-code','1','--python',str(OUT/'source_audit.py'),'--',ident]
    exits.append(subprocess.run(args).returncode)
assert not any(exits),exits
