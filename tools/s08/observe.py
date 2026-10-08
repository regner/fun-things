#!/usr/bin/env python3
"""Bounded addon-free saved-source probe/release; reuses narrow accepted S08/S03 logic."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from run_s08_linux import identity, write_json, launch, logs_clean, stop, ENGINE, ENGINE_SHA
from run_s03 import Proxy, POLL_SECONDS
BASE = 'ef730df936b5b159f0894033f5d01e2b7124386c'
HOST_CASES = ['provisional_rollback', 'authority_validation_and_expiry']
CLIENT_CASES = ['provider_substitution_late_cleanup', 'baseline_cancel_retry',
                'held_window_resync', 'subset_reorder_loss_recovery']
PROXY_EVENTS = ['armed', 'hold_subset_A', 'deliver_B_then_A', 'drop_subset_A',
                'refresh_subset', 'refresh_subset']


def environment(directory):
    """Isolate each child and clear MCP routing inherited from the host environment."""
    env = os.environ.copy()
    for key in list(env):
        if key.startswith('GODOT_MCP_'):
            del env[key]
    for key, folder in [('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'),
                        ('XDG_CACHE_HOME', 'cache'), ('XDG_RUNTIME_DIR', 'runtime'),
                        ('TMPDIR', 'tmp')]:
        target = directory / folder
        target.mkdir(mode=0o700, parents=True)
        env[key] = str(target)
    return env


def git_blob(path, revision=BASE):
    """Read exact committed candidate content."""
    return subprocess.check_output(['git', 'show', revision + ':' + path], cwd=ROOT)


def stage(task, revision=BASE, saved_entrypoint=False):
    """Mirror the exact card closure without copying editor caches or modifying inputs."""
    read_blob = lambda name: git_blob(name, revision)
    paths = [f'tests/fixtures/s01/{name}.tscn' for name in
             ['roundtrip', 'static_prefab', 'static_variant', 'rig_prefab']]
    paths += ['tests/fixtures/s01/fixture_identity.gd', 'tests/fixtures/s01/fixture_identity.gd.uid']
    paths += [f'art/models/spikes/s01_{name}.glb{suffix}'
              for name in ['static', 'rig'] for suffix in ['', '.import']]
    paths += [f'art/materials/s01_{name}.tres' for name in ['petrol', 'coral']]
    paths += ['art/textures/spikes/s01_palette.png', 'art/textures/spikes/s01_palette.png.import']
    s03 = [f'tests/fixtures/s03/{name}.tscn' for name in ['boot', 'entity', 'local_rig']]
    s03 += [f'tests/fixtures/s03/{name}.gd{suffix}' for name in
            ['entity', 'fake_transport', 'match', 'proof', 'replication', 'session', 'transport']
            for suffix in ['', '.uid']]
    actual_s03 = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', revision,
                                         'tests/fixtures/s03'], cwd=ROOT, text=True).splitlines()
    if set(s03) != set(actual_s03) or len(paths + s03) != 31:
        raise RuntimeError('accepted 31-file staged input closure differs from card')
    paths = paths + s03
    if saved_entrypoint:
        paths += ["tests/fixtures/s08/release_boot" + suffix
                  for suffix in [".tscn", ".gd", ".gd.uid"]]
    paths = sorted(paths)
    project = task / 'project'
    project.mkdir()
    manifest = []
    for name in paths:
        data = read_blob(name)
        if not name.startswith('tests/fixtures/s08/'):
            expected = git_blob(name, BASE)
            if name == 'tests/fixtures/s03/replication.gd':
                expected = expected.replace(
                    b'\tassert(match_state.apply_journal(participant, 70, match_state.durable_revision + 1))',
                    b'\tvar journal_applied: bool = match_state.apply_journal(\n\t\tparticipant, 70, match_state.durable_revision + 1\n\t)\n\tassert(journal_applied)')
            if data != expected:
                raise RuntimeError('candidate closure differs: ' + name)
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        uid = ''
        if name.endswith('.gd'):
            uid = read_blob(name + '.uid').decode().strip()
        elif name.endswith('.uid'):
            uid = data.decode().strip()
        elif name.endswith(('.tscn', '.tres', '.import')):
            found = re.search(r'uid="(uid://[^"]+)"', data.decode())
            uid = found.group(1) if found else ''
        elif name.endswith(('.glb', '.png')):
            uid = re.search(r'uid="(uid://[^"]+)"', read_blob(name+'.import').decode()).group(1)
        blob = subprocess.check_output(['git', 'rev-parse', revision + ':' + name], cwd=ROOT,
                                       text=True).strip()
        manifest.append({'path': name, 'revision': revision, 'blob': blob, 'uid': uid,
                         **identity(target)})
        if target.read_bytes() != data:
            raise RuntimeError('staged bytes differ: ' + name)
    write_json(task / 'staged-input.json', manifest)
    write_json(project / 's08_inputs.json', manifest)
    source_paths = ['art/source/models/spikes/s01_static.blend',
                    'art/source/models/spikes/s01_rig.blend',
                    'art/source/textures/spikes/s01_palette.png']
    write_json(task / 'source-links.json', [{'path': name, 'revision': revision,
        'blob': subprocess.check_output(['git', 'rev-parse', revision+':'+name], cwd=ROOT,
                                        text=True).strip(), 'bytes': len(read_blob(name)),
        'sha256': hashlib.sha256(read_blob(name)).hexdigest()} for name in source_paths])
    original = read_blob('project.godot').decode()
    settings = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', original)
    settings = settings.replace('config/icon="res://icon.svg"\n', '')
    main_scene = ("tests/fixtures/s08/release_boot.tscn" if saved_entrypoint
                  else "tests/fixtures/s03/boot.tscn")
    settings = settings.replace('[application]\n', '[application]\n'
        + 'run/main_scene="res://' + main_scene + '"\n')
    (project / 'project.godot').write_text(settings)
    if not saved_entrypoint:
        (project / 's08_receipt.gd').write_bytes((ROOT / 'tools/s08_receipt.gd').read_bytes())
    resources = [row['path'] for row in manifest if row['path'].endswith(('.tscn', '.gd'))]
    if not saved_entrypoint:
        resources += ['s08_receipt.gd']
    preset = ('[preset.0]\nname="S08 Linux"\nplatform="Linux"\nrunnable=true\n'
              'export_filter="resources"\nexport_files=PackedStringArray(' +
              ', '.join(json.dumps('res://' + p) for p in resources) + ')\n'
              'include_filter="s08_inputs.json"\nexclude_filter=""\n'
              'export_path=""\nencrypt_pck=false\nencrypt_directory=false\n'
              'script_export_mode=1\n[preset.0.options]\ncustom_template/debug=""\n'
              'custom_template/release=' + json.dumps(str(task/'custom_template/release')) +
              '\nbinary_format/architecture="x86_64"\nbinary_format/embed_pck=false\n'
              'debug/export_console_wrapper=0\ntexture_format/s3tc_bptc=true\n'
              'texture_format/etc2_astc=false\n')
    (project / 'export_presets.cfg').write_text(preset)
    scratch_paths = ['project.godot', 'export_presets.cfg', 's08_inputs.json']
    if not saved_entrypoint:
        scratch_paths.append('s08_receipt.gd')
    write_json(task / 'scratch-config.json',
               {name: identity(project/name) for name in scratch_paths})
    return project


def pck_manifest(task, saved_entrypoint=False):
    """Read the dev7 unencrypted PCK directory and verify all member hashes/extents."""
    folder = task/'export-folder'
    expected = {'FunThingsS08.x86_64', 'FunThingsS08.pck'}
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    write_json(task/'output-folder.json', [{'path':name, **identity(folder/name)}
                                         for name in sorted(actual)])
    if actual != expected:
        raise RuntimeError('unexpected/missing complete output-folder entries')
    executable = folder/'FunThingsS08.x86_64'
    elf = executable.read_bytes()[:64]
    if elf[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H',elf,18)[0] != 62:
        raise RuntimeError('export executable is not ELF64 x86_64')
    # The Linux exporter can alter its reserved PCK section even with external PCK.
    # Retain bytes and inspect any delta rather than assuming whole-file identity.
    template = task/'custom_template/release'
    a, b = template.read_bytes(), executable.read_bytes()
    changed = [i for i in range(min(len(a),len(b))) if a[i] != b[i]]
    write_json(task/'executable-template.json', {'template':identity(template),
        'executable':identity(executable), 'changed_byte_offsets':changed,
        'same_length':len(a)==len(b)})
    if a != b:
        raise RuntimeError('external-PCK executable differs from verified release template')
    data = (folder/'FunThingsS08.pck').read_bytes()
    magic, version, major, minor, patch, flags = struct.unpack_from('<6I',data)
    file_base, directory = struct.unpack_from('<QQ', data, 24)
    if magic != 0x43504447 or version != 4 or (major,minor,patch)!=(4,8,0) or flags != 2:
        raise RuntimeError('unexpected/encrypted PCK header')
    count = struct.unpack_from('<I',data,directory)[0]
    pos = directory+4
    entries = {}
    rows = []
    for _ in range(count):
        length = struct.unpack_from('<I',data,pos)[0]
        pos += 4
        name = data[pos:pos+length].rstrip(b'\0').decode()
        pos += length
        offset, size = struct.unpack_from('<QQ',data,pos)
        md5 = data[pos+16:pos+32].hex()
        entry_flags = struct.unpack_from('<I',data,pos+32)[0]
        pos += 36
        if entry_flags or name in entries or '..' in Path(name).parts:
            raise RuntimeError('unsafe/duplicate/encrypted PCK entry')
        start = file_base+offset
        payload = data[start:start+size]
        if len(payload)!=size or hashlib.md5(payload).hexdigest()!=md5:
            raise RuntimeError('PCK extent/hash mismatch: '+name)
        entries[name] = payload
        rows.append({'path':name, 'offset':start, 'bytes':size, 'md5':md5,
                     'sha256':hashlib.sha256(payload).hexdigest(), 'flags':entry_flags})
    write_json(task/'pck-members.json', {'version':version,'flags':flags,
               'file_base':file_base,'directory_offset':directory,'entries':rows})
    negatives = re.compile(r'(?i)(addons/|(?:^|/)(?:docs|captures|tools|source|credentials)/|'
                           r'\.blend$|\.gdextension$|\.(?:so|dll)$|steam_appid|\.mcp|\.git|'
                           r'tests/fixtures/(?!s01/|s03/' + ('|s08/' if saved_entrypoint else '') + r'))')
    leaked = [name for name in entries if negatives.search(name)]
    write_json(task/'exclusions.json', {'actual_pck_leaks':leaked,
               'scratch_addons_present':(task/'project/addons').exists(),
               'steam_environment_uninstalled_stopped':'not observed / gate OPEN'})
    if leaked:
        raise RuntimeError('PCK exclusions failed')
    mappings = []
    logical = json.loads((task/'staged-input.json').read_text())
    logical += [{'path':'s08_inputs.json'}]
    if not saved_entrypoint:
        logical.append({'path':'s08_receipt.gd'})
    for row in logical:
        if row['path'].endswith(('.uid','.import')):
            continue
        path = row['path']
        # PCK stores canonical resource-relative names, without res://.
        representations = []
        for suffix in ['', '.remap', '.import']:
            entry = path+suffix
            if entry not in entries:
                continue
            representations.append(entry)
            if suffix:
                text = entries[entry].decode()
                for target in re.findall(r'^path(?:\.[\w_]+)?="(res://[^"]+)"',text,re.M):
                    target = target[6:]
                    if target not in entries:
                        raise RuntimeError('missing remap payload: '+target)
                    representations.append(target)
        if not representations:
            raise RuntimeError('logical resource absent from pack: '+path)
        mappings.append({'logical_path':'res://'+path,'representations':representations})
    write_json(task/'logical-export-map.json', mappings)
    for name in ['project.binary','.godot/uid_cache.bin','.godot/global_script_class_cache.cfg']:
        if name not in entries:
            raise RuntimeError('required project/UID/script cache missing: '+name)
    cache = entries['.godot/global_script_class_cache.cfg'].decode()
    if 'Steam' in cache or 'MCP' in cache:
        raise RuntimeError('development/native class cache leak')
    write_json(task/'cache-inspection.json', {'class_cache':cache,
        'uid_cache_sha256':hashlib.sha256(entries['.godot/uid_cache.bin']).hexdigest(),
        'project_binary_sha256':hashlib.sha256(entries['project.binary']).hexdigest()})


def network(task, require_asset_receipts=False, env_factory=environment):
    """Reuse the actual S03 proxy schedule, launching only the exported runtime folder."""
    directory = task/'enet'
    directory.mkdir()
    folder = task/'export-folder'
    children, files, offsets, results, commands = [], [], {}, {}, {}
    proxy = None
    record = {'ok':False,'host_ready_before_client':False,'commands':commands,
              'asset_receipts':{}}
    deadline = time.monotonic()+25
    with (directory/'proxy.jsonl').open('w') as proxy_log:
        try:
            proxy = Proxy(24740,24741,proxy_log)

            def start(role, port):
                """Allocate one distinct exported child after the predecessor readiness."""
                logs = directory/role
                logs.mkdir()
                (logs/'engine.log').touch()
                env = env_factory(logs/'user')
                command = [str(folder/'FunThingsS08.x86_64'),'--headless','--log-file',
                           str(logs/'engine.log'),'--','--role='+role,'--port='+str(port)]
                commands[role] = {'argv':command,'cwd':str(folder), 'started_unix':time.time(),
                    'environment':{key:env[key] for key in env if key.startswith('XDG_')}}
                out, err = (logs/'stdout.log').open('wb'), (logs/'stderr.log').open('wb')
                files.extend([out,err])
                child = subprocess.Popen(command,stdout=out,stderr=err,env=env,cwd=folder)
                children.append(child)
                commands[role]['owned_pid'] = child.pid
                offsets[role] = 0
                write_json(logs/'command.json', commands[role])
                return child

            start('host',24740)
            client = None
            while time.monotonic()<deadline:
                proxy.poll()
                for role in list(commands):
                    with (directory/role/'stdout.log').open() as stream:
                        stream.seek(offsets[role])
                        while True:
                            previous = stream.tell()
                            line = stream.readline()
                            if not line.endswith('\n'):
                                offsets[role] = previous
                                break
                            offsets[role] = stream.tell()
                            if require_asset_receipts and line.startswith('S08 '):
                                receipt = json.loads(line[4:])
                                if role in record['asset_receipts'] or receipt.get('ok') is not True:
                                    raise RuntimeError(role+' asset receipt duplicate/failed')
                                if receipt.get('role') != role:
                                    raise RuntimeError(role+' asset receipt role mismatch')
                                record['asset_receipts'][role] = receipt
                                continue
                            if not line.startswith('S03 '):
                                continue
                            event = json.loads(line[4:])
                            if require_asset_receipts and role not in record['asset_receipts']:
                                raise RuntimeError(role+' S03 ran before asset receipt')
                            if event['event']=='ready' and role=='host':
                                if 'ready' in record:
                                    raise RuntimeError('duplicate host readiness')
                                record['ready'] = event
                                record['ready_observed_unix'] = time.time()
                            elif event['event']=='snapshots' and role=='host':
                                proxy.armed = True
                                proxy.record('armed')
                            elif event['event']=='result':
                                if role in results:
                                    raise RuntimeError('duplicate S03 result')
                                results[role] = event
                                if event.get('ok') is not True:
                                    raise RuntimeError(role+' S03 assertion failed')
                if 'ready' in record and client is None:
                    record['host_ready_before_client'] = True
                    client = start('client',24741)
                if len(results)==2 and all(c.poll() is not None for c in children):
                    break
                for role, child in zip(commands,children):
                    if child.poll() is not None and role not in results:
                        raise RuntimeError(role+' exited without result')
                time.sleep(POLL_SECONDS)
            else:
                raise RuntimeError('ENet combined 25s deadline')
            for role,child in zip(commands,children):
                if child.returncode != 0:
                    raise RuntimeError(role+' nonzero exit')
                logs_clean(directory/role)
                if results[role].get('steam_available') is not False:
                    raise RuntimeError('S03 native Steam absence assertion missing')
                expected = HOST_CASES if role=='host' else CLIENT_CASES
                if results[role].get('cases') != expected:
                    raise RuntimeError(role+' exact lifecycle cases missing')
            if require_asset_receipts and set(record['asset_receipts']) != {'host','client'}:
                raise RuntimeError('host/client asset receipts incomplete')
            if results['client']['movement_received'] != 5:
                raise RuntimeError('client ordered movement count mismatch')
            if not 0 < results['host']['baseline_bytes'] <= 8192:
                raise RuntimeError('host baseline bytes missing/out of bound')
            for field in ['max_held_bytes','max_movement_bytes']:
                if not 0 < results['host'][field] <= 1200:
                    raise RuntimeError(field+' missing/out of bound')
            if results['host']['user_dir']==results['client']['user_dir']:
                raise RuntimeError('host/client user directories overlap')
            if proxy.count!=5 or proxy.events != PROXY_EVENTS:
                raise RuntimeError('actual five-datagram schedule incomplete')
            record['ok'] = True
        except Exception as error:
            record['failure'] = repr(error)
        finally:
            stop(children)
            for role,child in zip(commands,children):
                commands[role].update(exit=child.returncode,child_reaped=child.poll() is not None)
                write_json(directory/role/'command.json',commands[role])
            for stream in files:
                stream.close()
            if proxy is not None:
                record['proxy_events'] = proxy.events
                record['proxy_count'] = proxy.count
                proxy.socket.close()
            record['proxy_closed'] = True
            record['all_children_reaped'] = all(c.poll() is not None for c in children)
            record['results'] = results
            write_json(directory/'result.json',record)
    if not record['ok']:
        raise RuntimeError('ENet STOP: '+record['failure'])


def probe_cache(task, project):
    """Filter owned editor caches to the exact saved closure, without an engine import."""
    mirror = Path('/tmp/s08-standard-555e0330/project')
    allowed = {'res://' + row['path'] for row in json.loads((task/'staged-input.json').read_text())}
    cache = project/'.godot'
    cache.mkdir()
    raw = (mirror/'.godot/uid_cache.bin').read_bytes()
    count = struct.unpack_from('<I', raw)[0]
    pos, rows, uid_rows = 4, [], []
    for _ in range(count):
        uid, size = struct.unpack_from('<QI', raw, pos)
        end = pos + 12 + size
        path = raw[pos+12:end].decode()
        if path in allowed:
            rows.append(raw[pos:end])
            uid_rows.append({'id': uid, 'path': path})
        pos = end
    if pos != len(raw):
        raise RuntimeError('UID cache has unparsed bytes')
    (cache/'uid_cache.bin').write_bytes(struct.pack('<I',len(rows)) + b''.join(rows))
    text = (mirror/'.godot/global_script_class_cache.cfg').read_text()
    classes = [item for item in re.findall(r'\{[^}]*\}',text)
               if re.search(r'"path": "([^"]+)"',item).group(1) in allowed]
    (cache/'global_script_class_cache.cfg').write_text('list=[' + ', '.join(classes) + ']\n')
    copied = []
    for path in project.rglob('*.import'):
        for name in re.findall(r'^path(?:\.[\w_]+)?="res://([^"]+)"',path.read_text(),re.M):
            target = project/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(mirror/name,target)
            copied.append({'path':name, **identity(target)})
    write_json(task/'probe-cache.json', {'uid_rows':uid_rows, 'class_cache':classes,
              'imported_payloads':copied, 'cache_files':[
                  {'path':str(p.relative_to(project)), **identity(p)}
                  for p in sorted(cache.rglob('*')) if p.is_file()]})


def rebind_templates(task):
    """Hash only the granted existing TPZ/members/template; no fetch or installation."""
    old = Path('/tmp/s08-observation-stpco415')
    tpz = old/'Godot_v4.8-dev7_export_templates.tpz'
    expected = {'bytes':1436879719,
        'sha256':'95c2677555b4f66c7eeca1a41368674703497e1907aad3fe56576423ca3c8cc6'}
    if identity(tpz) != expected:
        raise RuntimeError('existing exact TPZ identity differs')
    previous = json.loads((old/'acquisition/archive.json').read_text())
    rows = []
    with zipfile.ZipFile(tpz) as archive:
        version = archive.read('templates/version.txt').decode().strip()
        if version != '4.8.dev7':
            raise RuntimeError('template version differs')
        for name in ['linux_debug.x86_64','linux_release.x86_64',
                     'windows_debug_x86_64.exe','windows_release_x86_64.exe']:
            entry = 'templates/'+name
            with archive.open(entry) as stream:
                digest = hashlib.file_digest(stream,'sha256').hexdigest()
            rows.append({'path':entry,'bytes':archive.getinfo(entry).file_size,'sha256':digest})
    # Immutable accepted four-member hashes are independently declared below.
    expected_hashes = {
        'linux_debug.x86_64':(78405256,'8b2871a1e2f8baf482282422f7e64cd7cfcc713eb53d8db671025b041bb23eb9'),
        'linux_release.x86_64':(78376584,'c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695'),
        'windows_debug_x86_64.exe':(105650176,'c3287ae1c7fad6f6f2e0e09b0ebbb1321b49ec2423b74d513f12649e4c03bff6'),
        'windows_release_x86_64.exe':(111895040,'b538554df997ea699122d5b31f2ea8929301bcf3017e12dba664d85d351f60cd')}
    for row in rows:
        if (row['bytes'],row['sha256']) != expected_hashes[Path(row['path']).name]:
            raise RuntimeError('template member differs')
    template = old/'custom_template/release'
    if identity(template) != {'bytes':78376584,'sha256':expected_hashes['linux_release.x86_64'][1]}:
        raise RuntimeError('existing release template differs')
    (task/'custom_template').mkdir()
    shutil.copyfile(template,task/'custom_template/release')
    write_json(task/'template-rebind.json',{'tpz':expected,'version':version,'members':rows,
               'template':identity(task/'custom_template/release'),'old_archive_ok':previous['ok']})


def main():
    """Execute one distinct probe or the single ordered release phases; stop first failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['probe','release'],required=True)
    parser.add_argument('--revision',required=True)
    parser.add_argument('--taskdir',type=Path,required=True)
    args = parser.parse_args()
    task = args.taskdir.resolve()
    if not task.is_relative_to(Path('/tmp')) or task.exists():
        parser.error('fresh owned /tmp taskdir required')
    task.mkdir(mode=0o700)
    record = {'ok':False,'mode':args.mode,'input_revision':args.revision,'completed':[]}
    try:
        if identity(Path(ENGINE)) != {'bytes':151398728,'sha256':ENGINE_SHA}:
            raise RuntimeError('installed pinned engine differs')
        if args.mode == 'release':
            rebind_templates(task)
            record['completed'].append('template rebind')
        project = stage(task,args.revision,True)
        record['completed'].append('stage')
        if args.mode == 'probe':
            probe_cache(task,project)
            script = task/'api_probe.gd'
            script.write_bytes(git_blob('tools/s08/api_probe.gd',args.revision))
            result = launch(task,'api',[ENGINE,'--headless','--path',str(project),
                '--script',str(script)],60,project,environment)
            rows = [json.loads(line[8:]) for line in (result/'stdout.log').read_text().splitlines()
                    if line.startswith('S08_API ')]
            write_json(result/'result.json',rows)
            if len(rows)!=1 or rows[0].get('ok') is not True:
                raise RuntimeError('explicit API receipt incomplete/failed')
            record['completed'].append('explicit compilation/resource/public API probe')
        else:
            imported = launch(task,'import',[ENGINE,'--headless','--editor','--path',str(project),
                '--import','--quit'],60,project,environment)
            record['completed'].append('import')
            folder = task/'export-folder'
            folder.mkdir()
            launch(task,'export',[ENGINE,'--headless','--path',str(project),
                '--export-release','S08 Linux',str(folder/'FunThingsS08.x86_64')],120,project,environment)
            record['completed'].append('export')
            pck_manifest(task,True)
            record['completed'].append('package inspection')
            asset = launch(task,'asset',[str(folder/'FunThingsS08.x86_64'),'--headless',
                '--','--role=asset'],15,folder,environment)
            rows = [json.loads(line[4:]) for line in (asset/'stdout.log').read_text().splitlines()
                    if line.startswith('S08 ')]
            write_json(asset/'result.json',rows)
            if len(rows)!=1 or rows[0].get('ok') is not True or rows[0].get('role')!='asset':
                raise RuntimeError('asset receipt incomplete/failed')
            if rows[0]['executable_sha256'] != identity(folder/'FunThingsS08.x86_64')['sha256']:
                raise RuntimeError('runtime executable differs')
            record['completed'].append('asset')
            network(task,True,environment)
            record['completed'].append('ENet')
        record['ok'] = True
    except Exception as error:
        record['failure'] = repr(error)
    finally:
        write_json(task/'observation.json',record)
    print(json.dumps(record))
    return 0 if record['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
