"""Independent frozen docs review: Git/file/AST reads only, no project imports."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

BASE = '8b6dc3083fcb875febe778e362da1182ac4d67d1'
HEAD = '0ce40d951969f415843c0ee0361a447e68617119'
ROOT = Path.cwd()
SCOPE = {'README.md', 'TODO.md', 'docs/development.md', 'docs/assets/s02_kit.md',
         'docs/reviews/p0-doc5.md'}

def git(*args):
    return subprocess.check_output(['git', *args]).decode()

def tree(revision):
    return dict((row.split('\t')[1], row.split('\t')[0])
                for row in git('ls-tree', '-r', revision).splitlines())

assert git('rev-parse', 'HEAD').strip() == HEAD
assert git('rev-parse', 'refs/heads/main').strip() == BASE
assert not git('status', '--porcelain=v1', '-uall')
assert git('rev-list', '--parents', BASE + '..' + HEAD).strip() == HEAD + ' ' + BASE
subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, HEAD], check=True)
subprocess.run(['git', 'diff', '--check', BASE, HEAD], check=True)
a, b = tree(BASE), tree(HEAD)
changed = {p for p in a.keys() | b.keys() if a.get(p) != b.get(p)}
assert changed == SCOPE, changed
preserved = len(a.keys() - changed)
for name in a.keys() - changed:
    assert a[name] == b[name], name
print(f'PASS exact frozen HEAD/base, clean status, direct sole parent and whitespace; {preserved} mode/blob entries preserved')

expected = {'P0-PROFILES', 'S02', 'S03-S', 'S03-R', 'S04', 'S05', 'S06', 'S07', 'S08',
            'P0-GATE', 'M1-A1', 'M1-A2', 'M1-A3', 'M1-A-GATE', 'M1-B1', 'M1-B2',
            'M1-B3', 'M1-B4', 'M1-C1', 'M1-C2', 'M1-C3', 'M1-C4', 'M1-D1',
            'M1-D2', 'M1-D3', 'M1-D4', 'M1-GATE'}
old = git('show', BASE + ':TODO.md')
new = (ROOT / 'TODO.md').read_text()
pattern = r'^- \[ \] \*\*([A-Z0-9-]+) —'
oldids, newids = re.findall(pattern, old, re.M), re.findall(pattern, new, re.M)
assert len(oldids) == 28 and len(newids) == 27
assert set(oldids) == expected | {'P0-DOC5'} and set(newids) == expected
starts = lambda text: list(re.finditer(pattern, text, re.M))
def block(text, identifier):
    start = next(m.start() for m in starts(text) if m[1] == identifier)
    end = re.search(r'^- \[ \] |^#{1,3} ', text[start + 1:], re.M)
    return text[start:start + 1 + end.start()] if end else text[start:]
for identifier in expected - {'P0-GATE'}:
    assert block(old, identifier) == block(new, identifier), identifier
assert block(old, 'P0-GATE').replace('P0-DOC5 discovery/consumer reconciliation,',
    '[P0-DOC5 discovery/consumer reconciliation](docs/reviews/p0-doc5.md),') == block(new, 'P0-GATE')
print('PASS explicit 27 remaining task IDs and full blocks; only DOC5 removal and resolving gate reference')

linklog=[]
def anchors(text):
    result=set(); duplicates={}
    fenced=False
    for line in text.splitlines():
        if re.match(r'^\s*(```|~~~)', line):
            fenced=not fenced
        if fenced:
            continue
        match=re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match:
            continue
        heading=re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', match[1])
        slug=re.sub(r'[^\w\s-]', '', heading.lower()).replace(' ', '-')
        count=duplicates.get(slug, 0); duplicates[slug]=count+1
        result.add(slug + (f'-{count}' if count else ''))
    return result
for name in sorted(SCOPE):
    path=ROOT/name; data=path.read_bytes()
    assert b'\r' not in data and data.endswith(b'\n'), name
    assert all(line.rstrip() == line for line in data.splitlines()), name
    for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', data.decode()):
        if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target):
            continue
        destination, _, fragment=unquote(target).partition('#')
        resolved=(path.parent/destination).resolve() if destination else path
        assert resolved.exists(), (name,target)
        if fragment:
            assert fragment in anchors(resolved.read_text()), (name,target)
        linklog.append(f'{name}: {target} OK')
Path('/tmp/p0-doc5-independent-review/links.log').write_text('\n'.join(linklog)+'\n')
print(f'PASS {len(linklog)} local Markdown destinations/anchors; all five files LF/final-newline/trailing-whitespace')

receipt=json.loads((ROOT/'docs/spikes/s03-r-evidence/editor/original-preservation-final.json').read_text())
assert len(receipt['paths']) == 82
for row in receipt['paths']:
    data=(ROOT/row['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
    assert data == subprocess.check_output(['git','show',receipt['accepted_main']+':'+row['path']]), row['path']
print('PASS all original 82 immutable paths match recorded SHA256 and accepted-main bytes')

def scene(name):
    text=(ROOT/name).read_text()
    resources={m[2]:m[1] for m in re.finditer(r'\[ext_resource [^\n]*path="res://([^"]+)" id="([^"]+)"\]', text)}
    nodes={}
    for declaration in re.findall(r'^\[node ([^\n]+)\]', text,re.M):
        values=dict(re.findall(r'(\w+)="([^"]*)"', declaration))
        path=values.get('parent', '.')+'/'+values['name']
        instance=re.search(r'instance=ExtResource\("([^"]+)"\)',declaration)
        nodes[path]=resources[instance[1]] if instance else None
    return resources,nodes
bootres,bootnodes=scene('tests/fixtures/s03_r/boot.tscn')
assert bootnodes['./Boot']=='tests/fixtures/s03/boot.tscn'
assert scene('tests/fixtures/s03_r/actor.tscn')[1]['./Actor']=='tests/fixtures/s02/actor.tscn'
mapping={'Ground':'ground','WestCorner':'low','EastCorner':'low','NearTower':'near','TallTower':'tall'}
for node,asset in mapping.items():
    prefab='tests/fixtures/s02/'+asset+'_prefab.tscn'
    assert bootnodes['View/Match/CityRoot/'+node]==prefab
    assert scene(prefab)[1]['Visuals/Model']=='art/models/spikes/s02_'+asset+'.glb'
for node in ('Host','Client'):
    assert bootnodes['View/Match/Bodies/'+node]=='tests/fixtures/s03_r/actor.tscn'
actor=scene('tests/fixtures/s02/actor.tscn')[1]
assert actor['PresentationAnchor/Visuals/Model']=='art/models/spikes/s02_actor.glb'
assert actor['PresentationAnchor/WeaponMount/Model']=='art/models/spikes/s02_pistol.glb'
assert 'Sockets/Muzzle' in actor
assert not any('_target' in p or '_smg' in p or '_launcher' in p for p in bootres.values())
exports=json.loads((ROOT/'tools/s02/export_members.json').read_text())
assert len(exports)==9
for asset in ('ground','low','near','tall','actor','pistol'):
    assert 'export_s02_'+asset in exports
    for suffix in ('.glb','.glb.import'):
        assert (ROOT/('art/models/spikes/s02_'+asset+suffix)).exists()
print('PASS saved S03/S02 inheritance, five CityRoot instances, both bodies, actor/pistol/muzzle ancestry and six mapped exports')

runner=ast.parse((ROOT/'tools/run_s03_r.py').read_text())
options={}
for node in ast.walk(runner):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='add_argument':
        flag=ast.literal_eval(node.args[0]); options[flag]={kw.arg:ast.unparse(kw.value) for kw in node.keywords}
assert set(options)=={'--godot','--port','--proxy-port','--deadline','--windowed','--profiles','--output'}
assert options['--port']['default']=='24900'
assert options['--proxy-port']['default']=='24901'
assert options['--deadline']['default']=='45'
assert options['--windowed']['action']=="'store_true'"
constants={node.targets[0].id:ast.literal_eval(node.value) for node in runner.body
           if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name)
           and node.targets[0].id in {'PROFILES','MAX_QUEUE','MAX_POLL','BLACKOUT_SECONDS'}}
assert constants=={'PROFILES':{'baseline':(0,0,0),'normal':(75,30,0.02),'adverse':(125,50,0.05)},
                  'MAX_QUEUE':1024,'MAX_POLL':128,'BLACKOUT_SECONDS':1.0}
assert 'spike:s03-r' not in (ROOT/'mise.toml').read_text()
Path('/tmp/p0-doc5-independent-review/runner-ast.json').write_text(json.dumps({'options':options,'constants':constants},indent=2)+'\n')
print('PASS static AST exact seven flags/defaults, impairment profiles/proxy bounds and absent Mise task; project tooling never imported')

for profile,expected_p95 in [('baseline',69),('normal',235),('adverse',365)]:
    analysis=json.loads((ROOT/f'docs/spikes/s03-r-evidence/{profile}/analysis-owned-entity.json').read_text())
    assert analysis['response_p95_ms']=={'physics_ms':expected_p95,'rendered_frame_ms':None}
    assert analysis['prediction_correction']=='not measured: no predicted state'
    if profile=='adverse':
        assert [round(row['observed_delay_ms'],2) for row in analysis['recovery']]==[220.12,415.32]
fixed=json.loads((ROOT/'docs/spikes/s03-r-evidence/fix-adverse/result.json').read_text())['measurements']
assert fixed['response_p95_ms']=={'physics_ms':366,'rendered_frame_ms':None}
assert [round(row['observed_delay_ms'],2) for row in fixed['recovery']]==[124.71,493.79]
print('PASS accepted analysis fidelity: 69/235/365, 220.12/415.32 and separate 366/124.71/493.79; rendered null, no prediction')

for operation in ('rebase-merge','rebase-apply','MERGE_HEAD','CHERRY_PICK_HEAD','REVERT_HEAD','BISECT_LOG','index.lock'):
    assert not Path(git('rev-parse','--git-path',operation).strip()).exists(), operation
assert git('rev-parse','HEAD','refs/heads/main').splitlines()==[HEAD,BASE]
assert not git('status','--porcelain=v1','-uall')
print('PASS final clean/frozen SHA/base and no Git operation/index lock; all checks static')
