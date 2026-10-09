"""Disable only connector autoload/editor plugin in isolated exact candidate copy."""
import hashlib,json,re
from pathlib import Path
p=Path('/tmp/batch02-final-10ddb64/snapshot/project.godot')
before=p.read_bytes(); text=before.decode()
text=re.sub(r'(?ms)^\[autoload\]\n.*?(?=^\[)', '[autoload]\n\n', text)
text=re.sub(r'(?ms)^\[editor_plugins\]\n.*?(?=^\[)', '[editor_plugins]\n\n', text)
p.write_text(text)
out=Path(__file__).resolve().parent
(out/'scratch-project-original.godot').write_bytes(before)
(out/'scratch-project.godot').write_bytes(p.read_bytes())
print(json.dumps(dict(path=str(p),before_sha256=hashlib.sha256(before).hexdigest(),
    after_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),changes=['disable MCPRuntimeServer autoload','disable editor MCP plugin'],scope='isolated resource/physics checks, not full-project connector compatibility')))
