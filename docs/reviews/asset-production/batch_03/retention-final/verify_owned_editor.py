import pathlib,json,os,subprocess
O=pathlib.Path(__file__).resolve().parent;root=str(pathlib.Path.cwd());launch=json.loads(pathlib.Path('/tmp/asset-register-production-editor/launch.json').read_text());pid=launch['pid'];assert pid==277464;p=pathlib.Path('/proc')/str(pid);cwd=os.readlink(p/'cwd');exe=os.readlink(p/'exe');args=(p/'cmdline').read_bytes().decode().split('\0')[:-1];assert cwd==launch['cwd']==root and args==launch['argv'];assert exe==args[0]=='/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot';assert args[1:]==['--editor','--path',root,'--lsp-port','22652','--rendering-method','gl_compatibility']
fds={str(fd):os.readlink(p/'fd'/str(fd)) for fd in [1,2]};target='/tmp/asset-register-production-editor/f3/editor-live.log';assert list(fds.values())==[target,target];assert not pathlib.Path(target).resolve().is_relative_to(pathlib.Path(root))
owned=[]
for fd in (p/'fd').iterdir():
 try:owned.append(os.readlink(fd))
 except FileNotFoundError:pass
sockets=[]
for f in ['tcp','tcp6']:
 for l in pathlib.Path('/proc/net/'+f).read_text().splitlines()[1:]:
  s=l.split();port=int(s[1].split(':')[1],16)
  if port in [22650,22651,22652]:sockets.append(dict(port=port,state=s[3],inode=s[9],owned=('socket:['+s[9]+']') in owned))
assert all(any(s['port']==port and s['state']=='0A' and s['owned'] for s in sockets) for port in [22650,22652]);assert not any(s['port']==22651 and s['state']=='0A' for s in sockets)
old=pathlib.Path('/proc/254275/stat');old_state=old.read_text().rsplit(')',1)[1].split()[0] if old.exists() else 'absent';assert old_state in ['absent','Z','X'];version=subprocess.run([exe,'--version'],capture_output=True,text=True);print(version.stdout,end='');print(version.stderr,end='',file=__import__('sys').stderr);assert version.returncode==0 and version.stdout.strip()=='4.8.dev7.official.c971f93e7'
r=dict(launch=launch,pid=pid,cwd=cwd,exe=exe,args=args,fd_targets=fds,log_outside_workspace_and_frozen_packs=True,sockets=sockets,runtime_port_closed=True,old_editor_state=old_state,old_os_exit='not observed',version=version.stdout.strip(),live_log_is_unsnapshotted_with_open_writers=True)
(O/'owned-editor-readback.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
