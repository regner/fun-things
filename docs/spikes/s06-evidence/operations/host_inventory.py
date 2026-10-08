import os,json,datetime
from pathlib import Path
rows=[]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   exe=os.readlink(p/'exe'); args=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
   if 'godot' in exe.lower() or 'blender' in exe.lower(): rows.append({'pid':int(p.name),'exe':exe,'args':args,'cwd':os.readlink(p/'cwd')})
  except (OSError,PermissionError): pass
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host_processes':rows}
Path('/tmp/s06-operations/host-before.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
