"""Isolated S02 physics/input/resource proof; no shared editor or network mutation."""
import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from script_checks import checked_command, engine_version, environment


def fingerprint(root):
    paths = list((root / 'tests/fixtures/s02').glob('*'))
    paths += list((root / 'art/models/spikes').glob('s02_*.glb.import'))
    paths += list((root / 'tools/s02').glob('*.uid'))
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.suffix in {'.tscn', '.uid', '.import'}}


def source_checks():
    assert (ROOT / 'art/source/.gdignore').exists()
    assert (ROOT / 'art/source/models/spikes/s02_kit.blend').exists()
    members = json.loads((ROOT / 'tools/s02/export_members.json').read_text())
    for collection in members:
        asset = collection.removeprefix('export_')
        assert (ROOT / f'art/models/spikes/{asset}.glb').exists()
        assert (ROOT / f'art/models/spikes/{asset}.glb.import').exists()
    for path in (ROOT / 'tests/fixtures/s02').glob('*.tscn'):
        text = path.read_text()
        assert not re.search(r'type="(?:ArrayMesh|BoxMesh|CylinderMesh|SphereMesh|CSG\w+)"', text)
        assert 'uid="uid://' in text, path
        for dependency in re.findall(r'path="res://([^"\n]+)"', text):
            assert (ROOT / dependency).exists(), (path, dependency)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = (args.output or Path(tempfile.mkdtemp(prefix='s02-checks-'))).resolve()
    assert not output.is_relative_to(ROOT), 'output must be outside checkout'
    output.mkdir(parents=True, exist_ok=True)
    assert not any(output.iterdir()), 'fresh evidence directory required'
    print('S02 evidence:', output, flush=True)
    version = engine_version(args.godot)
    source_checks()
    project = output / 'project'
    shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns(
        '.git', '.godot', 'builds', '__pycache__', '.venv', '.tools'))
    settings = (project / 'project.godot').read_text()
    for section in ('autoload', 'editor_plugins'):
        settings = re.sub(r'(?ms)^\[' + section + r'\]\n.*?(?=^\[|\Z)', '', settings)
    (project / 'project.godot').write_text(settings)
    (project / 'addons/.gdignore').touch()
    env = environment(output / 'user')
    command = [args.godot, '--headless', '--path', str(project)]
    before = fingerprint(ROOT)
    imported = checked_command(command + ['--editor', '--import'], output / 'import.log', env, 90)
    outcome = checked_command(command + ['--script', 'res://tests/fixtures/s02/check_s02.gd'],
                              output / 'outcomes.log', env, 40)
    logs = (output / 'outcomes.log').read_text()
    result_lines = [line.removeprefix('S02_RESULT ') for line in logs.splitlines()
                    if line.startswith('S02_RESULT ')]
    result = json.loads(result_lines[-1]) if result_lines else None
    unchanged = before == fingerprint(project)
    summary = {'engine': version, 'import': imported, 'outcomes': outcome,
               'saved_files_unchanged': unchanged, 'result': result}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (output / 'identities.json').write_text(json.dumps(before, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 0 if imported and outcome and unchanged and result and not result['failures'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
