"""Read the supplied private editor process without tokens, bridge calls or mutations."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production')
EXPECTED='/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
launch=json.loads(Path('/tmp/asset-register-production-editor/launch.json').read_text())
proc=Path('/proc')/str(launch['pid'])
result=dict(launch=launch,process_visible=proc.exists(),verified=False)
if proc.exists():
    result['cwd']=str((proc/'cwd').resolve())
    result['executable']=str((proc/'exe').resolve())
    result['argv']=[x.decode() for x in (proc/'cmdline').read_bytes().split(b'\0') if x]
    args=result['argv']
    result['verified']=(launch['pid']==195352 and result['cwd']==str(ROOT) and
        result['executable']==str(Path(EXPECTED).resolve()) and args[0]==EXPECTED and
        '--editor' in args and '--path' in args and args[args.index('--path')+1]==str(ROOT) and
        '--lsp-port' in args and args[args.index('--lsp-port')+1]=='22652' and
        launch['editor_port']==22650 and launch['runtime_port']==22651)
(OUT/'host-editor-lease-guard.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
