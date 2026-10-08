"""Inspect without generic extraction; authorize only the required release member."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import struct
import zipfile

root = Path(__file__).parent
assert json.loads((root/'acquisition/download.json').read_text())['ok'] is True
record = {'ok':False, 'archive_members':[], 'required_members':[]}
try:
    with zipfile.ZipFile(root/'Godot_v4.8-dev7_export_templates.tpz') as z:
        seen = set()
        for item in z.infolist():
            p = PurePosixPath(item.filename)
            mode = item.external_attr >> 16
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in item.filename
            assert item.filename not in seen and not stat.S_ISLNK(mode)
            assert not item.flag_bits & 1
            seen.add(item.filename)
            record['archive_members'].append({'path':item.filename, 'bytes':item.file_size,
                'compressed_bytes':item.compress_size,'crc32':f'{item.CRC:08x}', 'mode':mode})
        version = z.read('templates/version.txt')
        record['version_hex'] = version.hex()
        assert version.decode().strip() == '4.8.dev7'
        for name in ['linux_debug.x86_64','linux_release.x86_64',
                     'windows_debug_x86_64.exe','windows_release_x86_64.exe']:
            name = 'templates/'+name
            with z.open(name) as f:
                h=hashlib.sha256()
                size=0
                prefix=b''
                while chunk:=f.read(1024*1024):
                    h.update(chunk)
                    size+=len(chunk)
                    if len(prefix)<4096:
                        prefix=(prefix+chunk)[:4096]
            if 'linux_' in name:
                assert prefix[:6]==b'\x7fELF\x02\x01'
                assert struct.unpack_from('<H',prefix,18)[0]==62
                architecture='ELF64 little-endian AMD x86-64'
            else:
                assert prefix[:2]==b'MZ'
                pe=struct.unpack_from('<I',prefix,60)[0]
                assert prefix[pe:pe+4]==b'PE\0\0'
                assert struct.unpack_from('<H',prefix,pe+4)[0]==0x8664
                assert struct.unpack_from('<H',prefix,pe+24)[0]==0x20b
                architecture='PE32+ AMD64'
            record['required_members'].append({'path':name,'bytes':size,
                'sha256':h.hexdigest(),'architecture':architecture})
        target=root/'custom_template/release'
        target.parent.mkdir()
        with z.open('templates/linux_release.x86_64') as f, target.open('xb') as out:
            while chunk:=f.read(1024*1024):
                out.write(chunk)
        target.chmod(0o755)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==record['required_members'][1]['sha256']
        record['extracted_only']=str(target)
    engine=Path('/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot')
    with engine.open('rb') as f:
        engine_sha=hashlib.file_digest(f,'sha256').hexdigest()
    record['installed_engine']={'path':str(engine),'bytes':engine.stat().st_size,'sha256':engine_sha}
    assert engine_sha=='6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd'
    record['ok']=True
except Exception as error:
    record['failure']=repr(error)
finally:
    (root/'acquisition/archive.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='archive_members'},indent=2))
raise SystemExit(0 if record['ok'] else 1)
