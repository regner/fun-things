import json,pathlib,subprocess,os
O=pathlib.Path(__file__).resolve().parent;root=str(pathlib.Path.cwd());s=pathlib.Path('/tmp/asset-register-production-editor');l=json.loads((s/'launch.json').read_text());pid=l['pid'];p=pathlib.Path('/proc')/str(pid);args=(p/'cmdline').read_bytes().decode().split('\0')[:-1];exe=os.readlink(p/'exe');cwd=os.readlink(p/'cwd');fds={os.readlink(f) for f in (p/'fd').iterdir() if f.exists()};sockets=[]
for fn in ['tcp','tcp6']:
 for line in pathlib.Path('/proc/net/'+fn).read_text().splitlines()[1:]:
  fields=line.split();port=int(fields[1].split(':')[1],16)
  if port in [22650,22651,22652]:sockets.append(dict(port=port,state=fields[3],inode=fields[9],owned=('socket:['+fields[9]+']') in fds))
v=subprocess.run([exe,'--version'],capture_output=True,text=True);print(v.stdout,end='');print(v.stderr,end='',file=__import__('sys').stderr)
r=dict(launch=l,pid=pid,args=args,exe=exe,cwd=cwd,version=v.stdout,version_exit=v.returncode,sockets=sockets)
(O/'editor-ownership.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
assert pid==254275 and cwd==root and l['cwd']==root and args==l['argv']
assert '4.8.dev7' in v.stdout and all(any(x['port']==port and x['owned'] and x['state']=='0A' for x in sockets) for port in [22650,22651,22652])
