#!/usr/bin/env python3
"""Offline literal cadence regression: inspect production source, never construct UDP resources."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check_consumer(source):
    """Require the existing owner, not a second service duration or a telemetry-only claim."""
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
               and node.module == 'run_s03']
    assert any(any(name.name == 'POLL_SECONDS' and name.asname is None
                   for name in node.names) for node in imports)
    sleeps = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute) and node.func.attr == 'sleep'
              and isinstance(node.func.value, ast.Name) and node.func.value.id == 'time']
    assert len(sleeps) == 1
    assert len(sleeps[0].args) == 1
    assert isinstance(sleeps[0].args[0], ast.Name) and sleeps[0].args[0].id == 'POLL_SECONDS'
    assert not sleeps[0].keywords


def main():
    """Check the independent literal20ms owner and reject the exact recorded10ms regression."""
    owner = ast.parse((ROOT / 'tools/run_s03.py').read_text())
    assignments = [node for node in owner.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == 'POLL_SECONDS'
                           for target in node.targets)]
    assert len(assignments) == 1
    assert ast.literal_eval(assignments[0].value) == 0.020
    source = (ROOT / 'tools/s08/lifecycle_diagnostic.py').read_text()
    check_consumer(source)
    negative = source.replace('time.sleep(POLL_SECONDS)', 'time.sleep(0.01)')
    assert negative != source
    try:
        check_consumer(negative)
    except AssertionError:
        print('PASS: literal20ms shared owner; recorded10ms regression rejected offline')
    else:
        raise AssertionError('accepted the wrong service cadence')


if __name__ == '__main__':
    main()
