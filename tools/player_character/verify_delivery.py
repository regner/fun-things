"""Verify saved-source exports and a fresh, isolated player asset import profile."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'docs/assets/player_character/evidence'
GODOT=(os.environ.get('GODOT') or shutil.which('godot') or
       '/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot')
BLENDER=(os.environ.get('BLENDER') or shutil.which('blender') or
         'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe')


def run(command,log,env):
    """Retain diagnostics and fail the bounded command without suppressing errors."""
    with log.open('w') as out:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=60)
    assert result.returncode==0,(command,log,result.returncode)
    assert 'SCRIPT ERROR:' not in log.read_text(),log


def copy_tree(profile,relative):
    """Copy only owned runtime families into the fresh profile; omit temporary fit dependencies."""
    target=profile/relative;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/relative,target,ignore=shutil.ignore_patterns('fit_check','fit_check.tscn'))


def main():
    """Check two saved production sources, then import and exercise their actual Godot APIs."""
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    state=Path(tempfile.mkdtemp(prefix='brackett-player-verify-'))
    env=os.environ|{'ALSOFT_DRIVERS':'null','BLENDER_USER_CONFIG':str(state/'blender'),
                   'XDG_CONFIG_HOME':str(state/'config'),'XDG_DATA_HOME':str(state/'data'),
                   'XDG_CACHE_HOME':str(state/'cache')}
    outputs=[]
    for asset in [
        {
            'name':'coral_courier',
            'source':'art/source/models/characters/coral_courier/coral_courier.blend',
            'export':'art/models/characters/coral_courier/coral_courier.glb',
            'collection':'export_coral_courier',
            'animated':False,
        },
        {
            'name':'shared_humanoid_player_motion_v1',
            'source':('art/source/models/characters/shared_humanoid/'
                      'shared_humanoid_player_motion_v1.blend'),
            'export':('art/models/characters/shared_humanoid/'
                      'shared_humanoid_player_motion_v1.glb'),
            'collection':'export_shared_humanoid_player_v1',
            'animated':True,
        },
    ]:
        temporary=state/(asset['name']+'.glb')
        command=[BLENDER,'--background','--threads','2','-noaudio',asset['source'],
                 '--python-exit-code','1','--python','tools/player_character/reexport.py',
                 '--',asset['collection'],str(temporary)]
        if asset['animated']:command+=['--animations']
        run(command,EVIDENCE/(asset['name']+'_reexport.log'),env)
        data=(ROOT/asset['export']).read_bytes()
        assert data==temporary.read_bytes(),asset['export']
        outputs.append({'source':asset['source'],'export':asset['export'],'byte_identical':True,
                        'sha256':hashlib.sha256(data).hexdigest()})
    (EVIDENCE/'source_freshness.json').write_text(json.dumps(outputs,indent=2)+'\n')
    run([BLENDER,'--factory-startup','--background','--threads','2','-noaudio',
         '--python-exit-code','1','--python','tools/player_character/audit_player_source.py'],
        EVIDENCE/'source_audit.log',env)
    profile=state/'profile';profile.mkdir()
    (profile/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Player asset clean profile"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    for relative in ['art/models/characters/coral_courier','art/models/characters/shared_humanoid',
                     'art/animations/characters/shared_humanoid','scenes/prefabs/player_character']:
        copy_tree(profile,relative)
    for relative in ['art/models/spikes/s02_ground.glb','art/models/spikes/s02_ground.glb.import',
                     'art/models/characters/s13_humanoid.glb','art/models/characters/s13_humanoid.glb.import',
                     'tools/player_character/check_shared_rig.gd','tools/player_character/check_shared_rig.gd.uid',
                     'tools/player_character/check_player_asset.gd','tools/player_character/check_player_asset.gd.uid',
                     'art/source/.gdignore']:
        target=profile/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
    for relative in ['art/source/models/characters/shared_humanoid',
                     'art/source/models/characters/coral_courier']:
        for source in (ROOT/relative).glob('*.json'):
            target=profile/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
    run([GODOT,'--headless','--path',str(profile),'--editor','--import','--quit','--lsp-port','0','--dap-port','0',
         '--debug-server','tcp://127.0.0.1:0'],EVIDENCE/'clean_import.log',env)
    run([GODOT,'--headless','--path',str(profile),'--script','res://tools/player_character/check_player_asset.gd'],
        EVIDENCE/'asset_check.log',env)
    run([GODOT,'--headless','--path',str(profile),'--script','res://tools/player_character/check_shared_rig.gd'],
        EVIDENCE/'rig_final_check.log',env)
    for filename in ['clean_import.log','asset_check.log','rig_final_check.log']:
        text=(EVIDENCE/filename).read_text()
        assert 'ERROR:' not in text and 'WARNING:' not in text,filename
    report={'profile':str(profile),'engine':subprocess.check_output([GODOT,'--version'],text=True).strip(),
            'source_exports':'byte-identical','clean_import':'pass','player_api_checks':'pass',
            'rig_check':'pass','scope':'asset-only profile; full-project gameplay/plugins/device performance excluded'}
    (EVIDENCE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
