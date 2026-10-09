#!/usr/bin/env python3
"""Stage one private S03 diagnostic author session using the accepted SDK supervisor."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = '233493abc7d2e3c106fb620105cfb766f542813b'
SEED = Path('/tmp/s05-author-56eb6b28-run01/config/godot/editor_settings-4.8.tres')


def identity(data):
    """Bind byte-exact private inputs, including the pre-existing settings seed."""
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    """Run one existing private author supervisor without an initialization retry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    if not run.is_relative_to(Path('/tmp')) or run.exists():
        parser.error('fresh private /tmp directory required')
    seed = SEED.read_bytes()
    if b'mcp_toolkit/performance/keep_editor_responsive_unfocused = false' not in seed:
        raise RuntimeError('existing boost=false seed unavailable; no initializer permitted')
    spec = importlib.util.spec_from_file_location('accepted_author',
                                                ROOT / 'tools/s05_effect/private_author.py')
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    state = run / 'state'
    project = state / 'project'
    project.mkdir(mode=0o700, parents=True)
    settings = state / 'config/godot/editor_settings-4.8.tres'
    settings.parent.mkdir(parents=True)
    settings.write_bytes(seed)
    if settings.read_bytes() != seed:
        raise RuntimeError('settings copy differs')
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
        'tests/fixtures/s03', 'addons/godot_mcp_toolkit'], cwd=ROOT, text=True).splitlines()
    rows = []
    for name in paths:
        data = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
        if (ROOT / name).read_bytes() != data:
            raise RuntimeError('non-base private author input: ' + name)
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append({'path': name, **identity(data)})
    legacy.save(state / 'inputs.json', rows)
    source = (ROOT / 'project.godot').read_text()
    source = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', source)
    source = source.replace('config/icon="res://icon.svg"\n', '')
    source += ('\n[autoload]\nMCPRuntimeServer="*res://addons/godot_mcp_toolkit/runtime/'
               'mcp_runtime_server.gd"\n\n[editor_plugins]\n'
               'enabled=PackedStringArray("res://addons/godot_mcp_toolkit/plugin.cfg")\n')
    (project / 'project.godot').write_text(source)
    # This is the unchanged, already committed context program, not authored gameplay.
    (state / 'context.gd').write_text(legacy.PROBE)
    legacy.save(run / 'preparation.json', {'base': BASE, 'seed_path': str(SEED),
        'seed_identity': identity(seed), 'copy_readback': True, 'home_unchanged': True,
        'legacy_source': identity((ROOT / 'tools/s05_effect/private_author.py').read_bytes()),
        'context_source': identity(legacy.PROBE.encode()), 'paths': paths})
    legacy.RUN, legacy.LOG, legacy.BASE, legacy.CONTINUE = state, run / 'log', BASE, True
    legacy.main()
    result = json.loads((legacy.LOG / 'lifecycle.json').read_text())
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
