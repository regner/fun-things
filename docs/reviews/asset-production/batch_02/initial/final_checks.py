"""Finish distinct reference/calibration checks and verify sources remain unchanged."""
from run_checks import REVIEW, SNAPSHOT, run
import sys

run('reference-audit',[sys.executable,str(REVIEW/'reference_audit.py')])
run('calibration-source',['/usr/bin/blender','-b','-noaudio','-t','2',
    '--python-exit-code','1','--python',str(REVIEW/'calibration_source.py'),
    '--',str(REVIEW)],local_env={'ALSOFT_DRIVERS':'null','SDL_AUDIODRIVER':'dummy'})
