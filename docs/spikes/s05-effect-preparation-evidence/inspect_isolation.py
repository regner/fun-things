"""Read installed source/launch metadata only; never connect, import server code or launch Godot."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '122978243dba25b3fb5d8d90fc50ffb1a468ecf5'
SERVER = Path('/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules/@npgamedev/godot-mcp-server')
ENGINE = Path('/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot')
repo_paths = [
    '.codex/config.toml', 'project.godot',
    'addons/godot_mcp_toolkit/docs/multi-instance.md',
    'addons/godot_mcp_toolkit/docs/advanced_configuration.md',
    'addons/godot_mcp_toolkit/transport/port_config.gd',
    'addons/godot_mcp_toolkit/security/auth.gd',
    'addons/godot_mcp_toolkit/registry/store/registry_paths.gd',
    'addons/godot_mcp_toolkit/paths/project_key.gd',
    'addons/godot_mcp_toolkit/paths/project_paths.gd',
    'addons/godot_mcp_toolkit/core/unfocused_sleep_controller.gd',
    'addons/godot_mcp_toolkit/core/autoload_registration.gd',
    'addons/godot_mcp_toolkit/core/plugin_composer.gd',
    'addons/godot_mcp_toolkit/commands/playtest/playtest_control.gd',
]
server_paths = ['package.json', 'README.md', 'dist/index.js', 'dist/registry.js',
                'dist/startup/portConfig.js', 'dist/startup/cliArgs.js',
                'dist/transport/tokenPath.js', 'dist/startup/configReload.js']
identities = []
for name in repo_paths:
    raw = (ROOT / name).read_bytes()
    old = subprocess.run(['git', 'show', BASE + ':' + name], cwd=ROOT,
                         capture_output=True, check=True).stdout
    assert raw == old
    blob = subprocess.run(['git', 'rev-parse', BASE + ':' + name], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout.strip()
    identities.append(dict(path=name, git_revision=BASE, git_blob=blob, bytes=len(raw),
                           sha256=hashlib.sha256(raw).hexdigest()))
for name in server_paths:
    raw = (SERVER / name).read_bytes()
    identities.append(dict(path=str(SERVER / name), bytes=len(raw),
                           sha256=hashlib.sha256(raw).hexdigest()))
engine_bytes = ENGINE.read_bytes()
parts = engine_bytes.split(b'\0')
needles = [b'--debug-server <uri>', b'--dap-port <port>', b'--lsp-port <port>',
           b'--log-file <file>', b'XDG_CONFIG_HOME', b'XDG_DATA_HOME', b'XDG_CACHE_HOME']
metadata = {}
for needle in needles:
    index = parts.index(needle)
    metadata[needle.decode()] = [item.decode('utf-8', errors='replace')
                                 for item in parts[index:index + 3]]
receipt = dict(base=BASE, project=str(ROOT),
               project_key_sha256_prefix=hashlib.sha256(str(ROOT).encode()).hexdigest()[:12],
               installed_server_version=json.loads((SERVER / 'package.json').read_text())['version'],
               sources=identities,
               engine=dict(path=str(ENGINE), bytes=len(engine_bytes),
                           sha256=hashlib.sha256(engine_bytes).hexdigest(),
                           literal_metadata=metadata),
               no_editor_or_connector_launch=True, no_registry_or_token_read=True,
               no_shared_app_or_process_query=True,
               result='Static isolation mechanisms supported; actual instance/routing/ports/drawability pending')
(HERE / 'isolation-source-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
