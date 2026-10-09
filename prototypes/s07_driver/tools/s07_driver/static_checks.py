"""Run scoped offline validation with complete command receipts; never launches Godot."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from support import ROOT, command, save

GDSTYLE = '/home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle'


def main():
    """Check actual scripts/style, preservation, offline counterexamples and authored whitespace."""
    output = Path(tempfile.mkdtemp(prefix='s07-final-static-'))
    evidence = ROOT / 'docs/spikes/s07-sustained-driver-evidence'
    base = '3f5fb4067c5ce5fca721f54d42165a833e4c884c'
    import os
    env = os.environ.copy()
    commands = [
        ('format', [GDSTYLE, '-c', 'gdstyle.toml', 'fmt', '--check', 'tests/fixtures/s07_driver']),
        ('lint', [GDSTYLE, '-c', 'gdstyle.toml', 'tests/fixtures/s07_driver']),
        ('preservation', [sys.executable, 'tools/s07_driver/check_resources.py',
                          str(evidence / 'preservation-final.json'), '--base', base]),
        ('offline-tests', [sys.executable, 'tools/s07_driver/test_offline.py']),
        ('python-compile', [sys.executable, '-m', 'py_compile',
                            *[str(p.relative_to(ROOT)) for p in sorted((ROOT / 'tools/s07_driver').glob('*.py'))]]),
        ('whitespace', ['git', 'diff', '--check', base, '--', 'TODO.md',
                        'docs/spikes/s07-run-cards.md', 'docs/spikes/s07-sustained-driver.md',
                        'tools/s07_driver', 'tests/fixtures/s07_driver']),
    ]
    results = []
    for name, argv in commands:
        receipt = command(argv, ROOT, env, output / name, 30)
        logs = {n: (output / name / n).read_text() for n in ['stdout.log', 'stderr.log', 'engine.log']}
        results.append({'name': name, 'command': receipt, 'complete_streams': logs})
    record = {'base': base, 'results': results, 'ok': all(r['command'].get('exit') == 0 for r in results),
              'initial_runtime_source_ref': subprocess.check_output(['git', 'rev-parse',
                  'refs/evidence/s07-driver/runtime-source'], text=True).strip()}
    save(evidence / 'static-checks.json', record)
    print(json.dumps({'ok': record['ok'], 'commands': len(results), 'source': str(output)}))
    return 0 if record['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
