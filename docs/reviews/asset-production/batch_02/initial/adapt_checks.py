"""One bounded adaptation: serialize Blender arrays and report loose vertices."""
from run_checks import IDS, REVIEW, SNAPSHOT, run
import sys

for asset in IDS[1:]:
    run(asset+'-source-adapted', ['/usr/bin/blender','-b','-noaudio','-t','2',
        str(SNAPSHOT/f'art/source/models/environment/{asset}/{asset}.blend'),
        '--python-exit-code','1','--python',str(REVIEW/'source_audit.py'),
        '--',asset,str(REVIEW)],local_env={
            'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy'},timeout=300)
run('binary-audit-adapted',[sys.executable,str(REVIEW/'glb_audit.py')])
