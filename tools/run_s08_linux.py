#!/usr/bin/env python3
"""One commissioned S08 observation, gated by preverified scratch templates; no retries."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import struct
import subprocess
import time

from run_s03 import Proxy, POLL_SECONDS
from script_checks import environment, ROOT

BASE = '93da622554e5739cf05bd2267d11b4c6745e4e2e'
ENGINE = '/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
ENGINE_SHA = '6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd'
DIAGNOSTIC = re.compile(r'(?i)(?:\b(?:SCRIPT ERROR|ERROR|WARNING)\s*:|\bWARNING\b)')
HOST_CASES = ['provisional_rollback', 'authority_validation_and_expiry']
CLIENT_CASES = ['provider_substitution_late_cleanup', 'baseline_cancel_retry',
                'held_window_resync', 'subset_reorder_loss_recovery']
PROXY_EVENTS = ['armed', 'hold_subset_A', 'deliver_B_then_A', 'drop_subset_A',
                'refresh_subset', 'refresh_subset']


def write_json(path, value):
    """Save a complete receipt with an intentional terminating newline."""
    path.write_text(json.dumps(value, indent=2) + '\n')


def identity(path):
    """Hash actual bytes rather than relying on filenames or prior metadata."""
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'bytes': path.stat().st_size, 'sha256': digest}


def git_blob(path):
    """Read only the accepted immutable input revision, including binary sources."""
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


def stop(children):
    """Gracefully interrupt actual owned handles, then terminate/kill and reap survivors."""
    for child in children:
        if child.poll() is None:
            child.send_signal(signal.SIGINT)
    deadline = time.monotonic() + 2
    for child in children:
        try:
            child.wait(timeout=max(0.01, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            child.terminate()
            try:
                child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=2)


def stage(task):
    """Mirror the exact card closure without copying editor caches or modifying inputs."""
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
    actual_s03 = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
                                         'tests/fixtures/s03'], cwd=ROOT, text=True).splitlines()
    if set(s03) != set(actual_s03) or len(paths + s03) != 31:
        raise RuntimeError('accepted 31-file staged input closure differs from card')
    paths = sorted(paths + s03)
    project = task / 'project'
    project.mkdir()
    manifest = []
    for name in paths:
        data = git_blob(name)
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        uid = ''
        if name.endswith('.gd'):
            uid = git_blob(name + '.uid').decode().strip()
        elif name.endswith('.uid'):
            uid = data.decode().strip()
        elif name.endswith(('.tscn', '.tres', '.import')):
            found = re.search(r'uid="(uid://[^"]+)"', data.decode())
            uid = found.group(1) if found else ''
        elif name.endswith(('.glb', '.png')):
            uid = re.search(r'uid="(uid://[^"]+)"', git_blob(name+'.import').decode()).group(1)
        blob = subprocess.check_output(['git', 'rev-parse', BASE + ':' + name], cwd=ROOT,
                                       text=True).strip()
        manifest.append({'path': name, 'revision': BASE, 'blob': blob, 'uid': uid,
                         **identity(target)})
        if target.read_bytes() != data:
            raise RuntimeError('staged bytes differ: ' + name)
    write_json(task / 'staged-input.json', manifest)
    write_json(project / 's08_inputs.json', manifest)
    source_paths = ['art/source/models/spikes/s01_static.blend',
                    'art/source/models/spikes/s01_rig.blend',
                    'art/source/textures/spikes/s01_palette.png']
    write_json(task / 'source-links.json', [{'path': name, 'revision': BASE,
        'blob': subprocess.check_output(['git', 'rev-parse', BASE+':'+name], cwd=ROOT,
                                        text=True).strip(), 'bytes': len(git_blob(name)),
        'sha256': hashlib.sha256(git_blob(name)).hexdigest()} for name in source_paths])
    original = git_blob('project.godot').decode()
    settings = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', original)
    settings = settings.replace('config/icon="res://icon.svg"\n', '')
    settings = settings.replace('[application]\n', '[application]\n'
        'run/main_scene="res://tests/fixtures/s03/boot.tscn"\n')
    (project / 'project.godot').write_text(settings)
    (project / 's08_receipt.gd').write_bytes((ROOT / 'tools/s08_receipt.gd').read_bytes())
    resources = [row['path'] for row in manifest if row['path'].endswith(('.tscn', '.gd'))]
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
    write_json(task / 'scratch-config.json', {name: identity(project/name) for name in
               ['project.godot', 'export_presets.cfg', 's08_receipt.gd', 's08_inputs.json']})
    return project


def logs_clean(directory):
    """Read every retained stream, including stderr and empty engine logs."""
    for name in ['stdout.log', 'stderr.log', 'engine.log']:
        if DIAGNOSTIC.search((directory/name).read_text(errors='replace')):
            raise RuntimeError(f'{directory.name}/{name} contains diagnostics')


def launch(task, phase, argv, budget, cwd):
    """Invoke one private phase with bounded owned-child cleanup and complete streams."""
    directory = task / phase
    directory.mkdir()
    (directory/'engine.log').touch()
    env = environment(directory/'user')
    command = argv + ['--log-file', str(directory/'engine.log')]
    record = {'argv': command, 'cwd': str(cwd), 'budget_seconds': budget,
              'environment': {key: env[key] for key in env if key.startswith('XDG_')},
              'started_unix': time.time()}
    write_json(directory/'command.json', record)
    with (directory/'stdout.log').open('wb') as out, (directory/'stderr.log').open('wb') as err:
        child = subprocess.Popen(command, stdout=out, stderr=err, env=env, cwd=cwd)
        try:
            record['owned_pid'] = child.pid
            record['exit'] = child.wait(timeout=budget)
        except subprocess.TimeoutExpired:
            record['timeout'] = True
        finally:
            stop([child])
            record['exit'] = child.returncode
            record['child_reaped'] = child.poll() is not None
            record['ended_unix'] = time.time()
            write_json(directory/'command.json', record)
    if record.get('timeout') or record['exit'] != 0:
        raise RuntimeError(phase + ' timeout/nonzero exit')
    logs_clean(directory)
    return directory


def pck_manifest(task):
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
    if magic != 0x43504447 or version != 3 or (major,minor,patch)!=(4,8,0) or flags != 2:
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
                           r'tests/fixtures/(?!s01/|s03/))')
    leaked = [name for name in entries if negatives.search(name)]
    write_json(task/'exclusions.json', {'actual_pck_leaks':leaked,
               'scratch_addons_present':(task/'project/addons').exists(),
               'steam_environment_uninstalled_stopped':'not observed / gate OPEN'})
    if leaked:
        raise RuntimeError('PCK exclusions failed')
    mappings = []
    logical = json.loads((task/'staged-input.json').read_text())
    logical += [{'path':'s08_receipt.gd'}, {'path':'s08_inputs.json'}]
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


def network(task):
    """Reuse the actual S03 proxy schedule, launching only the exported runtime folder."""
    directory = task/'enet'
    directory.mkdir()
    folder = task/'export-folder'
    children, files, offsets, results, commands = [], [], {}, {}, {}
    proxy = None
    record = {'ok':False,'host_ready_before_client':False,'commands':commands}
    deadline = time.monotonic()+25
    with (directory/'proxy.jsonl').open('w') as proxy_log:
        try:
            proxy = Proxy(24740,24741,proxy_log)

            def start(role, port):
                """Allocate one distinct exported child after the predecessor readiness."""
                logs = directory/role
                logs.mkdir()
                (logs/'engine.log').touch()
                env = environment(logs/'user')
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
                            if not line.startswith('S03 '):
                                continue
                            event = json.loads(line[4:])
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


def main():
    """Run the single ordered commission and freeze the first failed phase."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--taskdir',type=Path,required=True)
    args = parser.parse_args()
    task = args.taskdir.resolve()
    if not task.is_relative_to(Path('/tmp')) or (task/'observation.json').exists():
        parser.error('fresh commissioned /tmp taskdir required; no repeat observation')
    record = {'ok':False,'input_revision':BASE,'completed':[]}
    write_json(task/'observation.json',record)
    try:
        for name in ['download.json','archive.json']:
            if json.loads((task/'acquisition'/name).read_text()).get('ok') is not True:
                raise RuntimeError('STOP: artifact not verified')
        if identity(Path(ENGINE))['sha256'] != ENGINE_SHA:
            raise RuntimeError('STOP: installed engine changed')
        project = stage(task)
        record['completed'].append('stage')
        imported = launch(task,'import',[ENGINE,'--headless','--editor','--path',str(project),
                                         '--import','--quit'],60,project)
        if '4.8.dev7.official.c971f93e7' not in (imported/'stdout.log').read_text():
            raise RuntimeError('import runtime engine identity missing')
        record['completed'].append('import')
        folder = task/'export-folder'
        folder.mkdir()
        launch(task,'export',[ENGINE,'--headless','--path',str(project),
                             '--export-release','S08 Linux',str(folder/'FunThingsS08.x86_64')],
               120,project)
        record['completed'].append('export')
        pck_manifest(task)
        record['completed'].append('package inspection')
        asset = launch(task,'asset',[str(folder/'FunThingsS08.x86_64'),'--headless',
                                    '--script','res://s08_receipt.gd'],15,folder)
        rows = [json.loads(line[4:]) for line in (asset/'stdout.log').read_text().splitlines()
                if line.startswith('S08 ')]
        write_json(asset/'result.json',rows)
        if len(rows)!=1 or rows[0].get('ok') is not True:
            raise RuntimeError('asset receipt incomplete/failed')
        if rows[0]['executable_sha256'] != identity(folder/'FunThingsS08.x86_64')['sha256']:
            raise RuntimeError('runtime executable identity mismatch')
        record['completed'].append('asset')
        network(task)
        record['completed'].append('ENet')
        record['ok'] = True
    except Exception as error:
        record['failure'] = repr(error)
    finally:
        write_json(task/'observation.json',record)
    print(json.dumps(record))
    return 0 if record['ok'] else 1


if __name__=='__main__':
    raise SystemExit(main())
