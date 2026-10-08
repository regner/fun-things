"""Offline final receipts and PCK UID cache readback; no runtime replay."""
from pathlib import Path
import json,struct,hashlib,shutil
root=Path.cwd();e=root/'docs/spikes/s08-standard-editor-evidence';task=Path('/tmp/s08-addon-free-555e0330-release01');pck=(task/'export-folder/FunThingsS08.pck').read_bytes()
manifest=json.loads((task/'pck-members.json').read_text());entry=next(r for r in manifest['entries'] if r['path']=='.godot/uid_cache.bin')
raw=pck[entry['offset']:entry['offset']+entry['bytes']];count=struct.unpack_from('<I',raw)[0];pos=4;rows=[]
for _ in range(count):
 uid,size=struct.unpack_from('<QI',raw,pos);end=pos+12+size;path=raw[pos+12:end].decode();rows.append({'id':uid,'path':path});pos=end
assert pos==len(raw)
probe=json.loads((e/'addon-free-probe/probe-cache.json').read_text());expected={r['path']:r['id'] for r in probe['uid_rows']};actual={r['path']:r['id'] for r in rows}
assert expected==actual
(task/'uid-cache-decoded.json').write_text(json.dumps({'ok':True,'rows':rows,'exact_probe_UID_paths_and_IDs_match':True,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n')
d=e/'addon-free-release';d.mkdir()
for f in task.iterdir():
 if f.is_file():shutil.copyfile(f,d/f.name)
for phase in ['import','export','asset','enet']:
 shutil.copytree(task/phase,d/phase,ignore=lambda path,names:['user'] if 'user' in names else [])
for suffix in ['stdout','stderr']:shutil.copyfile(Path(str(task)+'.supervisor.'+suffix),d/('supervisor.'+suffix))
summary={'source_revision':'21b77cbbe92eae98bccba04a15e972bf8816027a','authoring_shutdown':'STRICT_STOP; preserved five RID ERRORs and Canvas/CanvasItem/ObjectDB170 warnings','addon_free_probe':{'ok':True,'checks':106,'child':566755,'exit':0},'release_asset':{'ok':True,'checks':172,'resources':22,'pck_members':48},'exported_ENet':{'ok':False,'host_pid':567114,'host_exit':1,'host_S08_before_S03':True,'failure':'case deadline in ACTIVE','client_created':False,'proxy_datagrams':0,'proxy_events':[],'all_children_reaped':True,'proxy_closed':True},'full_S08':'OPEN; partial bounded result only','unavailable_claims':['drawability/input/feel','Steam uninstalled/stopped/native transport','Deck/Windows/device/performance/production acceptance']}
(e/'bounded-outcomes.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'UIDcache_rows':count,'copied_files':len(list(d.rglob('*')))}))
