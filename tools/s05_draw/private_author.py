#!/usr/bin/env python3
"""Stage a bounded S05 mirror and reuse the accepted private author supervisor."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = '48aef3dbd133876743f504f94a1b788a26d5638f'
SETTINGS = Path('/tmp/s05-author-56eb6b28-run01/config/godot/editor_settings-4.8.tres')
MAX_BYTES = 8 * 1024 * 1024


def digest(data):
    """Bind stored bytes rather than trusting file names or role labels."""
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def closure():
    """Follow saved paths and project fixture class references, preserving sidecars."""
    tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE],
                                      cwd=ROOT, text=True).splitlines()
    classes = {}
    for name in tracked:
        if name.startswith('tests/fixtures/') and name.endswith('.gd'):
            match = re.search(r'^class_name\s+(\w+)', (ROOT / name).read_text(), re.M)
            if match:
                classes[match[1]] = name
    paths = set()
    pending = ['tests/fixtures/s05_effect/burst.tscn',
               'tests/fixtures/s05_effect/editor_harness.tscn']
    while pending:
        name = pending.pop()
        if name in paths:
            continue
        if name not in tracked:
            raise RuntimeError('dependency outside accepted tree: ' + name)
        paths.add(name)
        if name.endswith(('.gd', '.tscn', '.tres', '.import')):
            source = (ROOT / name).read_text()
            pending.extend(p for p in re.findall(r'res://([\w./-]+)', source)
                           if not p.startswith('.godot/'))
            pending.extend(path for symbol, path in classes.items()
                           if re.search(r'\b' + symbol + r'\b', source))
        for suffix in ['.uid', '.import']:
            if name + suffix in tracked:
                pending.append(name + suffix)
    paths.update(p for p in tracked if p.startswith('addons/godot_mcp_toolkit/'))
    return sorted(paths)


def prepare(run, legacy):
    """Create fresh private settings and byte-bound inputs without launching an engine."""
    run.mkdir(mode=0o700)
    state = run / 'author-state'
    project = state / 'project'
    project.mkdir(parents=True)
    settings = SETTINGS.read_bytes()
    if b'mcp_toolkit/performance/keep_editor_responsive_unfocused = false' not in settings:
        raise RuntimeError('successful private boost=false settings unavailable')
    target = state / 'config/godot/editor_settings-4.8.tres'
    target.parent.mkdir(parents=True)
    target.write_bytes(settings)
    rows = []
    total = 0
    for name in closure():
        data = (ROOT / name).read_bytes()
        expected = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
        if data != expected:
            raise RuntimeError('non-base input: ' + name)
        total += len(data)
        if total > MAX_BYTES:
            raise RuntimeError('minimal closure byte cap exceeded')
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append({'path': name, **digest(data)})
    legacy.save(state / 'inputs.json', rows)
    source = (ROOT / 'project.godot').read_text()
    source = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', source)
    source = source.replace('config/icon="res://icon.svg"\n', '')
    source += ('\n[autoload]\nMCPRuntimeServer="*res://addons/godot_mcp_toolkit/runtime/'
               'mcp_runtime_server.gd"\n\n[editor_plugins]\n'
               'enabled=PackedStringArray("res://addons/godot_mcp_toolkit/plugin.cfg")\n')
    (project / 'project.godot').write_text(source)
    (state / 'context.gd').write_text(legacy.PROBE)
    legacy.save(run / 'preparation.json', {'base': BASE, 'project': str(project),
        'closure_files': len(rows), 'closure_bytes': total, 'byte_cap': MAX_BYTES,
        'settings_source': str(SETTINGS), 'settings': digest(settings),
        'fresh_initializer': False, 'home_unchanged': True,
        'legacy_supervisor': digest((ROOT / 'tools/s05_effect/private_author.py').read_bytes())})
    return state


def main():
    """Use one established editor/SDK session with no initializer or shared registry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    if not run.is_relative_to(Path('/tmp')) or run.exists():
        parser.error('fresh /tmp run directory required')
    spec = importlib.util.spec_from_file_location('s05_accepted_author',
                                                ROOT / 'tools/s05_effect/private_author.py')
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    state = prepare(run, legacy)
    legacy.RUN, legacy.LOG, legacy.BASE, legacy.CONTINUE = state, run / 'author-log', BASE, True
    legacy.main()
    result = json.loads((legacy.LOG / 'lifecycle.json').read_text())
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
