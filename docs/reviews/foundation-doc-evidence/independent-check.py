from pathlib import Path
import hashlib, json, re, subprocess, tomllib, urllib.parse
root = Path('/home/regner/.paseo/worktrees/0u71f39f/foundation-doc-reconciliation')
base = '8f512779356464b33de06138e18c962d12bfab10'
head = '24c878572a2edc478ff6aeeda9ac95298cdb17a1'
def git(*args):
    return subprocess.check_output(['git', *args], cwd=root, text=True)
def original(path):
    return git('show', base + ':' + path)
changed = git('diff', '--name-only', base, head).splitlines()
assert all(p == 'TODO.md' or p in {'docs/api-contracts.md', 'docs/architecture.md', 'docs/assets.md', 'docs/guidance-sources.md', 'docs/reviews/p0-06.md', 'docs/reviews/p0-doc1.md', 'docs/reviews/p0-doc2.md', 'docs/spikes/s01.md'} or p.startswith('docs/reviews/foundation-doc-evidence/') for p in changed)
assert git('rev-parse', 'HEAD').strip() == head
assert git('rev-parse', 'refs/heads/main').strip() == base
assert not git('status', '--porcelain')
assert not git('rev-list', '--merges', base+'..'+head).strip()
subprocess.run(['git','merge-base','--is-ancestor',base,head],cwd=root,check=True)
subprocess.run(['git','diff','--check',base,head],cwd=root,check=True)
print('PASS clean exact candidate, local-main ancestor, two linear resolving commits, allowed doc-only paths, diff whitespace')
commits = git('rev-list','--reverse',base+'..'+head).splitlines()
assert len(commits)==2
for i, c in enumerate(commits, 1):
    doc = git('show', c+':TODO.md')
    assert bool(re.search(r'^- \[ \] \*\*P0-DOC1',doc,re.M)) is False
    assert bool(re.search(r'^- \[ \] \*\*P0-DOC2',doc,re.M)) is (i==1)
    assert 'TODO.md' in git('diff-tree','--no-commit-id','--name-only','-r',c).splitlines()
print('PASS each task removed with its own resolving commit')
old = original('TODO.md'); new = (root/'TODO.md').read_text()
def tasks(text):
    return {m.group(1): m.group(0).rstrip() for m in re.finditer(r'^- \[ \] \*\*([^ ]+).*?(?=\n- \[ \]|\n##|\Z)',text,re.M|re.S)}
a=tasks(old); b=tasks(new)
assert set(a)-set(b)=={'P0-DOC1','P0-DOC2'} and not set(b)-set(a)
for k in b:
    if k!='P0-GATE': assert a[k]==b[k],k
assert a['P0-GATE'].split('  Done when:')[1] == b['P0-GATE'].split('  Done when:')[1]
for name in ('p0-doc1','p0-doc2'):
    requirement=(root/f'docs/reviews/foundation-doc-evidence/{name}-requirements.txt').read_text().rstrip()
    assert requirement==a[name.upper()],name
for p in ('docs/reviews/plan-checkpoints.md','docs/reviews/plan-check-2026-10-07.md'):
    assert original(p)==(root/p).read_text(),p
for p in ('docs/spikes/s01.md','docs/reviews/p0-06.md'):
    assert (root/p).read_text().startswith(original(p)),p
print(f'PASS other {len(b)} active task blocks/statuses and P0-GATE acceptance unchanged; raw requirements exact; checkpoint bytes and historical S01/P0-06 retained')
p='docs/api-contracts.md'
def table_prefix(text):
    section=text.split('## Provisional limits and failure codes')[1].split('Chunk sizes')[0]
    return [line.rsplit('|',2)[0] for line in section.splitlines() if line.startswith('|')]
assert table_prefix(original(p))==table_prefix((root/p).read_text())
print('PASS every provisional-limit name/value/scope column unchanged')
mds=[p for p in changed if p.endswith('.md')]+['docs/design.md','docs/development.md','docs/multiplayer.md','docs/scene-structure.md','docs/spikes/s03.md','docs/reviews/plan-check-2026-10-07.md','docs/reviews/plan-checkpoints.md']
def unfenced(s):
    return re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', s)
def anchors(path):
    counts={}; output=set()
    for line in unfenced(path.read_text()).splitlines():
        match=re.match(r'^#{1,6}\s+(.*?)\s*#*$',line)
        if not match: continue
        s=match.group(1).lower().replace('`','')
        s=re.sub(r'[^\w\- ]','',s).replace(' ','-')
        n=counts.get(s,0); counts[s]=n+1
        output.add(s+(f'-{n}' if n else ''))
    return output
links=0; errors=[]
for p in mds:
    path=root/p; raw=path.read_bytes()
    assert b'\r' not in raw,p
    assert not any(line.rstrip(b' \t')!=line for line in raw.splitlines()),p
    for m in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)',unfenced(raw.decode())):
        target=m.group(1)
        if re.match(r'[a-zA-Z][\w+.-]*:',target):continue
        links+=1
        parsed=urllib.parse.urlsplit(target)
        dest=(path.parent/urllib.parse.unquote(parsed.path)).resolve() if parsed.path else path
        if not dest.exists(): errors.append((p,target,'missing path'))
        elif parsed.fragment and dest.suffix=='.md' and urllib.parse.unquote(parsed.fragment) not in anchors(dest): errors.append((p,target,'missing heading'))
assert not errors,errors
print(f'PASS {len(mds)} Markdown files, {links} local links/heading anchors, LF/trailing whitespace')
fingerprints=json.loads((root/'docs/spikes/s01-evidence/fingerprints.json').read_text())
for name,row in fingerprints.items():
    for label, p in [('source',f'art/source/models/spikes/{name}.blend'),('export',f'art/models/spikes/{name}.glb')]:
        assert hashlib.sha256((root/p).read_bytes()).hexdigest()==row[label+'_sha256'],p
result=json.loads((root/'docs/spikes/s03-evidence/reviewed-fix-result.json').read_text())
assert result['ok'] and all(r['ok'] for r in result['results'].values())
assert len(result['fixture_sha256'])==17
for p,h in result['fixture_sha256'].items():assert hashlib.sha256((root/p).read_bytes()).hexdigest()==h,p
comp=json.loads((root/'docs/spikes/s03-evidence/reviewed-fix-compilation.json').read_text())
assert len(comp)==10 and all(r['ok'] for r in comp)
# Discover without importing repository Python (no bytecode/cache side effects).
import os
found=[]
for directory,children,files in os.walk(root,followlinks=False):
    relative=Path(directory).relative_to(root).as_posix()
    if '.gdignore' in files or relative in {'addons/godot_mcp_toolkit','addons/godotsteam'}:
        children[:]=[]; continue
    children[:]=sorted(n for n in children if not n.startswith('.') and not (Path(directory)/n).is_symlink())
    found += [(Path(directory)/n).relative_to(root).as_posix() for n in files if n.endswith('.gd') and not n.startswith('.')]
assert sorted(found)==sorted(r['script'] for r in comp)
print('PASS 4 S01 source/export hashes, 17 S03 fixture hashes, successful retained result, ten-script compilation matching current discovery; no runtime rerun')
config=tomllib.loads((root/'mise.toml').read_text())
for task,command in {'gdstyle:check':'python3 tools/script_checks.py --style-only','gdscript:check':'python3 tools/script_checks.py','resources:check':'python tools/check.py resources','s01:clean':'python tools/s01/clean_import.py','s01:reexport':'python tools/s01/reexport.py','spike:s03':'python3 tools/run_s03.py','tools:check':"python3 -m unittest discover -s tools -p 'test_*.py'"}.items():
    assert config['tasks'][task]['run']==command,task
print('PASS all seven documented mise task commands match actual targets (source scopes inspected independently)')
print('ALL STATIC CHECKS PASSED')
