"""Bounded addon-free import/development/sustained phases with a persistent total attempt ledger."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import time

from support import ROOT, ENGINE, command, environment, identity, save, stage, verify_engine

sys.path.insert(0, str(ROOT / "tools"))
from measurement_identity import measurement_identity  # noqa: E402



def main():
    """Use one import, at most two short groups and one sustained interval; never retry implicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('phase', choices=['import', 'development', 'sustained'])
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        raise ValueError('external output required')
    verify_engine()
    if args.phase == 'import':
        if output.exists():
            raise ValueError('fresh import output required')
        output.mkdir(mode=0o700)
        before = stage(output / 'project')
        save(output / 'staged-inputs.json', before)
        save(output / 'budget.json', {'import': 0, 'development': 0, 'sustained': 0})
    project = output / 'project'
    if (project / 'addons').exists() or '[autoload]' in (project / 'project.godot').read_text():
        raise RuntimeError('runtime closure must not initialize addons or autoloads')
    ledger = json.loads((output / 'budget.json').read_text())
    maximum = 2 if args.phase == 'development' else 1
    if ledger[args.phase] >= maximum:
        raise RuntimeError('total attempt budget exhausted')
    ledger[args.phase] += 1
    save(output / 'budget.json', ledger)
    phase = output / f'{args.phase}-{ledger[args.phase]}'
    phase.mkdir()
    staged_sources = list(json.loads((output / 'staged-inputs.json').read_text()))
    sources = ['tools/s07_driver/run.py', 'tools/s07_driver/support.py',
               'tools/measurement_identity.py', *staged_sources]
    save(phase / 'measurement-identity.json', measurement_identity(
        ROOT, sources, {**vars(args), 'output': output}))
    env = environment(phase / 'private')
    cap = {'import': 90, 'development': 120, 'sustained': 660}[args.phase]
    started = time.monotonic()
    receipts = []

    def invoke(name, extra):
        """Spend only the remaining group budget, reserving owned cleanup time for every child."""
        logs = phase / name
        remaining = cap - (time.monotonic() - started) - 6
        if remaining <= 0:
            raise RuntimeError('group absolute deadline')
        argv = [str(ENGINE), '--headless', '--path', str(project),
                '--log-file', str(logs / 'engine.log'), *extra]
        receipt = command(argv, project, env, logs, remaining)
        receipts.append(receipt)
        diagnostics = []
        for stream in ['stdout.log', 'stderr.log', 'engine.log']:
            for line in (logs / stream).read_text(errors='replace').splitlines():
                if any(marker in line for marker in ['SCRIPT ERROR:', 'ERROR:', 'WARNING:']):
                    diagnostics.append({'stream': stream, 'line': line})
        save(logs / 'diagnostics.json', diagnostics)
        if receipt.get('exit') != 0 or receipt.get('timeout') or diagnostics:
            raise RuntimeError(name + ' failed: inspect full streams/command')

    result = {'ok': False, 'phase': args.phase, 'cap_seconds': cap}
    try:
        if args.phase == 'import':
            invoke('import', ['--editor', '--import', '--quit'])
        else:
            if args.phase == 'development':
                for script in ['fixture', 'run', 'guards']:
                    invoke('compile-' + script, ['--check-only', '--script',
                           f'res://tests/fixtures/s07_driver/{script}.gd'])
                invoke('guards', ['--script', 'res://tests/fixtures/s07_driver/guards.gd'])
                shutil.copy2(project / 'guards.json', phase / 'guards.json')
            invoke('routes', ['--script', 'res://tests/fixtures/s07_driver/run.gd', '--',
                             '600' if args.phase == 'sustained' else '0'])
            for name in ['result.json', 'traversals.jsonl']:
                shutil.copy2(project / name, phase / name)
        before = json.loads((output / 'staged-inputs.json').read_text())
        changed = [name for name, value in before.items() if identity(project / name) != value]
        if changed:
            raise RuntimeError('runtime changed saved inputs: ' + str(changed))
        result['saved_inputs_unchanged'] = True
        result['ok'] = True
    except Exception as error:
        result['failure'] = repr(error)
    finally:
        result.update(elapsed_seconds=time.monotonic() - started, commands=receipts,
                      owned_children_reaped=all(r.get('reaped') for r in receipts))
        save(phase / 'phase.json', result)
    print(json.dumps(result))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
