"""Copy-only, registration/getters-only isolated Godot check; no Steam init/send."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

repo = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
scratch = Path(sys.argv[1]).resolve()
godot = Path(sys.argv[2]).resolve()
assert scratch.is_relative_to(Path('/tmp')) and not scratch.exists()
scratch.mkdir(parents=True)
project = scratch / 'project'
shutil.copytree(repo / 'addons/godotsteam', project / 'addons/godotsteam')
(project / 'project.godot').write_text(
    'config_version=5\n[application]\nconfig/name="S03-S compatibility registration"\n'
    '[steam]\ninitialization/processes/auto_init=false\n')
shutil.copyfile(evidence / 'registration.gd.txt', project / 'probe.gd')
# Seed only this copied project's extension discovery list. No editor/import run.
(project / '.godot').mkdir()
(project / '.godot/extension_list.cfg').write_text('res://addons/godotsteam/godotsteam.gdextension\n')
env = dict(os.environ)
for key in ['DATA', 'CONFIG', 'CACHE']:
    path = scratch / ('xdg-' + key.lower())
    path.mkdir()
    env['XDG_' + key + '_HOME'] = str(path)
commands = []
for name, options in [('version', ['--version']),
                      ('registration', ['--headless', '--path', str(project),
                                        '--script', 'res://probe.gd'])]:
    command = [str(godot), *options]
    result = subprocess.run(command, env=env, cwd=project, capture_output=True,
                            text=True, timeout=30)
    (scratch / (name + '.log')).write_text(result.stdout + result.stderr)
    commands.append({'command': command, 'returncode': result.returncode, 'timeout_s': 30})
    assert result.returncode == 0, name
    assert 'ERROR:' not in result.stdout + result.stderr, name
assert 'S03_S_REGISTRATION_ONLY_COMPLETE' in (scratch / 'registration.log').read_text()
assert '4.8.dev7.official.c971f93e7' in (scratch / 'version.log').read_text()
raw = json.loads((project / 'registration.json').read_text())
assert raw['auto_init'] is False and raw['godotsteam_version'] == '4.23'
methods = {m['name']: m for m in raw['steam_methods']}
selected = ['sendMessageToConnection', 'sendMessages', 'configureConnectionLanes',
            'receiveMessagesOnConnection', 'receiveMessagesOnPollGroup',
            'getConnectionRealTimeStatus', 'getConnectionInfo', 'closeConnection',
            'connectP2P', 'createListenSocketP2P', 'setConnectionUserData',
            'createLobby', 'joinLobby', 'leaveLobby']
projection = {'kind': 'registration/API presence only; no native delivery/lifecycle',
              'engine': raw['engine'], 'version': raw['godotsteam_version'],
              'auto_init': raw['auto_init'], 'max_channels': raw['max_channels'],
              'methods': {name: methods[name] for name in selected},
              'peer_extension_methods': raw['MultiplayerPeerExtension'],
              'signals': [s for s in raw['steam_signals']
                          if s['name'] in ['network_connection_status_changed',
                                           'lobby_created', 'lobby_joined']],
              'commands': commands}
(scratch / 'registration-selected.json').write_text(json.dumps(projection, indent=2) + '\n')
manifest = json.loads((repo / 'docs/spikes/s03-s-evidence/provenance.json').read_text())
for entry in manifest['native']:
    assert hashlib.sha256((repo / entry['path']).read_bytes()).hexdigest() == entry['sha256']
print('PASS: copied registration/getters, exact engine, all 22 accepted native hashes preserved')
