"""Stage immutable peer GLBs for a temporary player-fit scene; never edit peer assets."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'art/models/characters/coral_courier/fit_check'
SPEC={
 'pistol':('2f1846e9d883bbd15a0bcda4f826170b55ea2b5c','art/models/weapons/pistol_coral_stub/pistol_coral_stub.glb'),
 'smg':('a05f22d','art/models/weapons/smg_wedgewire/smg_wedgewire_a.glb'),
 'launcher':('d8c7635','art/models/weapons/dock_thumper/dock_thumper_launcher_a.glb'),
}


def main():
    """Extract only declared GLBs; cleanup only these owned temporary files when requested."""
    if '--clean' in sys.argv:
        for name in SPEC:
            for suffix in ['.glb','.glb.import']:
                (STAGE/(name+suffix)).unlink(missing_ok=True)
        if STAGE.exists():STAGE.rmdir()
        (ROOT/'scenes/prefabs/player_character/fit_check.tscn').unlink(missing_ok=True)
        return
    STAGE.mkdir(exist_ok=True)
    receipt={}
    for name,(revision,path) in SPEC.items():
        revision=subprocess.check_output(['git','rev-parse',revision],cwd=ROOT,text=True).strip()
        data=subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT)
        (STAGE/(name+'.glb')).write_bytes(data)
        receipt[name]={'revision':revision,'path':path,'sha256':hashlib.sha256(data).hexdigest()}
    (ROOT/'docs/assets/player_character/evidence/weapon_dependencies.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Staged immutable fit references; refresh private editor, build/save the temporary fit scene.')


if __name__=='__main__':main()
