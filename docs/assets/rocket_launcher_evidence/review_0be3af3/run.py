import subprocess,sys,json,time,pathlib,os
root=pathlib.Path(__file__).parent
label=sys.argv[1]; cmd=sys.argv[2:]
t0=time.time()
env=os.environ.copy()
for k,v in {"XDG_DATA_HOME":"xdg/data","XDG_CONFIG_HOME":"xdg/config","XDG_CACHE_HOME":"xdg/cache"}.items():
 p=root/v;p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
with (root/(label+".log")).open("w") as f:
 p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env)
 with (root/"commands.jsonl").open("a") as j:j.write(json.dumps({"label":label,"cmd":cmd,"pid":p.pid,"parent":os.getpid(),"cwd":os.getcwd(),"started":t0})+"\n")
 time.sleep(0.2)
 def process_row(pid):
  try:
   base=pathlib.Path("/proc")/str(pid)
   return {"pid":pid,"cmdline":(base/"cmdline").read_bytes().replace(b"\0",b" ").decode(),"exe":str((base/"exe").resolve()),"children":[int(c) for c in (base/"task"/str(pid)/"children").read_text().split()]}
  except OSError:return {"pid":pid,"exited":True}
 owned=[]; pending=[p.pid]
 while pending:
  row=process_row(pending.pop());owned.append(row);pending.extend(row.get("children",[]))
 with (root/"commands.jsonl").open("a") as j:j.write(json.dumps({"label":label,"owned_process_tree":owned})+"\n")
 rc=p.wait()
with (root/"commands.jsonl").open("a") as j:j.write(json.dumps({"label":label,"exit":rc,"seconds":time.time()-t0})+"\n")
print(label,"exit",rc,"log",root/(label+".log"));sys.exit(rc)
