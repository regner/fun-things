from pathlib import Path
import os,json,sys,datetime
worktree='/home/regner/.paseo/worktrees/0u71f39f/s05-authoritative-chain-fixture'
rows=[];refs=[]
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:
  args=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\0') if x]
  cwd=os.readlink(p/'cwd');exe=os.readlink(p/'exe');comm=(p/'comm').read_text().strip()
  ppid=int((p/'status').read_text().split('PPid:\t')[1].splitlines()[0])
  if args and Path(args[0]).name.lower() in ['godot','blender']:
   rows.append({'pid':int(p.name),'ppid':ppid,'command':args,'cwd':cwd,'exe':exe})
  if cwd==worktree or cwd.startswith(worktree+'/'):
   refs.append({'pid':int(p.name),'ppid':ppid,'comm':comm,'exe':exe,'cwd':cwd,
    'engine_or_blender': bool(args and Path(args[0]).name.lower() in ['godot','blender'])})
 except (OSError,PermissionError,IndexError):pass
receipt={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid_namespace':os.readlink('/proc/self/ns/pid'),'net_namespace':os.readlink('/proc/self/ns/net'),'authoring_processes':rows,'worktree_cwd_refs':refs}
Path(sys.argv[1]).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'authoring_processes':rows,'worktree_cwd_ref_count':len(refs)}))
