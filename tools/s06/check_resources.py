"""Check new S06 ancestry/UIDs and immutable base bytes without modifying shared resources."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE='096469f25db2617858d49f88860991c1c84c222e'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uid(path):
    if path.suffix=='.gd':return path.with_suffix('.gd.uid').read_text().strip()
    if path.suffix=='.glb':path=Path(str(path)+'.import')
    match=re.search(r'uid="(uid://[^"]+)"',path.read_text())
    assert match,path
    return match[1]


def check(base=BASE):
    paths=[*ROOT.glob('tests/fixtures/s06/*'),*ROOT.glob('tools/s06/*.gd')]
    ids={};dependencies=[]
    for path in paths:
        if path.suffix not in ['.tscn','.tres','.gd']:continue
        identity=uid(path)
        assert identity not in ids,(identity,path,ids.get(identity))
        ids[identity]=str(path.relative_to(ROOT))
        if path.suffix not in ['.tscn','.tres']:continue
        text=path.read_text()
        assert not re.search(r'type="(?:ArrayMesh|BoxMesh|CylinderMesh|SphereMesh|CSG\w+)"',text),path
        for block in re.findall(r'\[ext_resource [^\]]+\]',text):
            target=re.search(r'path="res://([^"]+)"',block)
            expected=re.search(r'uid="([^"]+)"',block)
            assert target and expected,(path,block)
            actual=ROOT/target[1]
            assert actual.exists() and uid(actual)==expected[1],(path,actual,expected[1])
            dependencies.append({'scene':str(path.relative_to(ROOT)),'target':target[1],'uid':expected[1]})
        if path.suffix=='.tscn':
            assert all('unique_id=' in block for block in re.findall(r'\[node [^\]]+\]',text)),path
    for side in ['west','east']:
        path=ROOT/f'art/models/spikes/s06_{side}.glb'
        data=path.read_bytes();magic,version,total=struct.unpack_from('<III',data)
        assert magic==0x46546c67 and version==2 and total==len(data)
        length,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
        gltf=json.loads(data[20:20+length])
        assert not gltf.get('images') and not gltf.get('extensionsUsed') and not gltf.get('skins')
        assert not gltf.get('animations')
        expected=json.loads((ROOT/'tools/s06/export_members.json').read_text())['export_s06_'+side]
        assert sorted(node['name'] for node in gltf['nodes'])==expected
    files=subprocess.check_output(['git','ls-tree','-r','--name-only',base],cwd=ROOT,text=True).splitlines()
    preserved=0
    for name in files:
        if name=='TODO.md':continue
        path=ROOT/name
        original=subprocess.check_output(['git','show',base+':'+name],cwd=ROOT)
        assert path.is_file() and path.read_bytes()==original,name
        preserved+=1
    source=ROOT/'art/source/models/spikes/s06_intersection.blend'
    assert source.exists() and (ROOT/'art/source/.gdignore').exists()
    return {'base':base,'preserved_original_files_except_TODO':preserved,
            'new_resource_uids':ids,'dependencies':dependencies,
            'source_sha256':sha(source),'exports':{side:sha(ROOT/f'art/models/spikes/s06_{side}.glb')
            for side in ['west','east']},'scope':'new S06 static resources, no broad production discovery'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--base',default=BASE)
    args=parser.parse_args();result=check(args.base)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
