#!/usr/bin/env python3
"""Check the inert profile proposal against installed schemas and retained discovery."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

BASE = '11a4486ae6e912387ef4e2ffbce3b138c3b45f28'
ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'docs/workflows/p0-profiles-evidence'


def unique_object(pairs):
    """Reject duplicated JSON keys rather than accepting last-key precedence."""
    result = {}
    for key, value in pairs:
        assert key not in result, f'duplicate JSON key: {key}'
        result[key] = value
    return result


def git(*args):
    """Read Git evidence or run a nonmutating validation command."""
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True)


def heading_ids(text):
    """Collect Markdown heading anchors, including GitHub duplicate suffixes."""
    counts, anchors = {}, set()
    for line in text.splitlines():
        if not re.match(r'^#{1,6} ', line):
            continue
        title = re.sub(r'[`*_]', '', re.sub(r'^#+ ', '', line)).lower()
        slug = re.sub(r'[^\w\- ]', '', title).replace(' ', '-')
        count = counts.get(slug, 0)
        anchors.add(slug if count == 0 else f'{slug}-{count}')
        counts[slug] = count + 1
    return anchors


def main():
    """Verify schema/settings, evidence hashes, links and confined documentation scope."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema-root', type=Path, required=True,
                        help='Read-only extracted installed @getpaseo package directory')
    parser.add_argument('--base', default=BASE, help='Delivery base after authorized rebase')
    args = parser.parse_args()
    docs = [ROOT / 'TODO.md', *sorted((ROOT / 'docs/workflows').glob('p0-profiles-*.md'))]
    data = {p.name: json.loads(p.read_text(), object_pairs_hook=unique_object)
            for p in EVIDENCE.glob('*.json')}
    patch = data['proposed.patch.json']
    assert set(patch) == {'agentProfiles'}
    profiles = patch['agentProfiles']
    assert len({p['id'] for p in profiles}) == len(profiles) == 4
    discovered = data['discovery.json']
    assert discovered['profiles']['profiles'] == []
    provider = next(p for p in discovered['providers']['providers'] if p['id'] == 'codex')
    assert provider['enabled'] and provider['status'] == 'available'
    models = {m['id']: m for m in discovered['models']['models']}
    for p in profiles:
        assert set(p) == {'id', 'name', 'provider', 'model', 'modeId', 'thinkingOptionId',
                          'featureValues', 'notes'}
        assert p['provider'] == 'codex' and p['modeId'] == 'auto-review'
        assert p['modeId'] in {m['id'] for m in provider['modes']}
        assert p['thinkingOptionId'] in {o['id'] for o in models[p['model']]['thinkingOptions']}
        inspected = next(i for i in discovered['inspections'] if i['selectedModel'] == p['model'])
        features = {f['id']: f for f in inspected['features']}
        assert set(p['featureValues']) <= set(features)
        assert all(v is False for v in p['featureValues'].values())
        assert p['notes'].strip()
    source = data['schema-source.json']
    for item in source['sources']:
        p = args.schema_root / item['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], p
        lines = p.read_text().splitlines()
        for excerpt in item['excerpts']:
            assert '\n'.join(lines[excerpt['start_line']-1:excerpt['end_line']]) == excerpt['text']
    node = r'''
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
const root=process.argv[1], file=process.argv[2];
const {AgentProfileSchema}=await import(pathToFileURL(root+'/protocol/dist/agent-profile.js'));
const {MutableDaemonConfigPatchSchema}=await import(pathToFileURL(root+'/protocol/dist/messages.js'));
const patch=JSON.parse(readFileSync(file,'utf8'));
for (const p of patch.agentProfiles) AgentProfileSchema.parse(p);
MutableDaemonConfigPatchSchema.parse(patch);
console.log('PASS actual installed AgentProfileSchema and MutableDaemonConfigPatchSchema');
'''
    subprocess.run(['node', '--input-type=module', '-e', node, str(args.schema_root),
                    str(EVIDENCE / 'proposed.patch.json')], check=True, cwd=ROOT)
    links = 0
    for p in docs:
        raw = p.read_bytes()
        assert b'\r' not in raw and raw.endswith(b'\n'), p
        body = re.sub(r'(?ms)^```.*?^```[^\n]*', '', raw.decode())
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            target = target.split()[0].strip('<>')
            if re.match(r'^[a-z]+:', target):
                continue
            path, _, anchor = unquote(target).partition('#')
            destination = (p.parent / path).resolve() if path else p
            assert destination.is_file(), (p, target)
            if anchor:
                assert anchor in heading_ids(destination.read_text()), (p, target)
            links += 1
    before = git('show', f'{args.base}:TODO.md')
    after = (ROOT / 'TODO.md').read_text()
    profile_block = r'(?ms)^- \[ \] \*\*P0-PROFILES.*?(?=^### Documentation checkpoint follow-ups)'
    assert len(re.findall(profile_block, before)) == len(re.findall(profile_block, after)) == 1
    assert re.sub(profile_block, '', before) == re.sub(profile_block, '', after)
    assert re.findall(r'^- \[ \] \*\*([^ ]+)', before, re.M) == re.findall(
        r'^- \[ \] \*\*([^ ]+)', after, re.M)
    changed = set(git('diff', '--name-only', args.base).splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').splitlines())
    assert all(p == 'TODO.md' or p.startswith('docs/workflows/p0-profiles') for p in changed)
    git('diff', '--check', args.base)
    subprocess.run(['git', 'merge-base', '--is-ancestor', args.base, 'HEAD'], cwd=ROOT, check=True)
    assert not git('rev-list', '--merges', f'{args.base}..HEAD').strip()
    print(f'PASS {len(profiles)} supported inert bundles; source hashes/excerpts; '
          f'{links} local links/anchors; P0-only TODO delta; documentation scope/LF/whitespace')
    print('PASS base ancestry and zero merge commits; no runtime/configuration/launch proof')
    print('HEAD', git('rev-parse', 'HEAD').strip(), 'local-main',
          git('rev-parse', 'refs/heads/main').strip())


if __name__ == '__main__':
    main()
