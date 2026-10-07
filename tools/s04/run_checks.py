#!/usr/bin/env python3
"""Run the bounded saved car comparison and cut/fence probes in an isolated copy."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_s04 import stage
from script_checks import ROOT, checked_command, engine_version, environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    directory = (args.output or Path(tempfile.mkdtemp(prefix='s04-checks-'))).resolve()
    if directory.is_relative_to(ROOT):
        parser.error('output must be outside checkout')
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        parser.error('fresh empty output required')
    version = engine_version(args.godot)
    project = stage(directory)
    env = environment(directory / 'user')
    hashes = {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in project.rglob('*') if p.is_file()}
    commands = [[args.godot, '--headless', '--editor', '--path', str(project),
                 '--import', '--quit']]
    ok = checked_command(commands[0], directory / 'import.log', env)
    results = {}
    if ok:
        for name, arguments, marker in [
            ('body', ['res://tests/fixtures/s04/body_comparison.tscn'],
             '"event":"comparison_result"'),
            ('baseline', ['--script', 'res://tests/fixtures/s04/baseline_probe.gd'],
             'S04_BASELINE '),
            ('fence', ['--script', 'res://tests/fixtures/s04/pose_fence_probe.gd'],
             'S04_FENCE '),
            ('producer', ['--script', 'res://tests/fixtures/s04/producer_probe.gd'],
             'S04_PRODUCER '),
        ]:
            command = [args.godot, '--headless', '--path', str(project), *arguments]
            commands.append(command)
            log = directory / (name + '.log')
            passed = checked_command(command, log, env, timeout=35)
            text = log.read_text()
            results[name] = passed and marker in text and '"ok":true' in text
    unchanged = all(hashlib.sha256((project / p).read_bytes()).hexdigest() == digest
                    for p, digest in hashes.items())
    report = {'ok': ok and len(results) == 4 and all(results.values()) and unchanged,
              'version': version, 'results': results, 'source_unchanged': unchanged,
              'source_sha256': hashes, 'commands': commands}
    (directory / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['ok', 'results', 'source_unchanged']}))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
