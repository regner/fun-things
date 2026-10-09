"""Isolated asset-profile clean import, checks and deliberate failure probes for S01."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('checks', ROOT / 'tools/check.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def run(command, log, env, expected_failure=None):
    with log.open('w') as output:
        result = subprocess.run(command, env=env, stdout=output, stderr=subprocess.STDOUT,
                                timeout=120, check=False)
    text = log.read_text(errors='replace')
    if expected_failure:
        assert result.returncode != 0 and expected_failure in text, (log, text)
    else:
        unknown = [line for line in text.splitlines() if re.match(
            r'^(?:SCRIPT ERROR:|ERROR:|WARNING:)', line)]
        assert result.returncode == 0 and not unknown, (log, result.returncode, unknown)
    print('PASS', log)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--logs', type=Path, default=ROOT / 'builds/s01-clean')
    args = parser.parse_args()
    args.logs.mkdir(parents=True, exist_ok=True)
    binary = checks.godot_binary(os.environ.copy())
    with tempfile.TemporaryDirectory(prefix='s01-clean-') as temporary:
        clean = Path(temporary) / 'project'
        shutil.copytree(ROOT, clean, ignore=shutil.ignore_patterns(
            '.git', '.godot', '.mcp.json', '.tools', '.venv', '__pycache__', 'builds'))
        env = os.environ.copy()
        for key in ('XDG_DATA_HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME'):
            env[key] = str(Path(temporary) / key.lower())
        env['GODOT_MCP_EDITOR_PORT'] = '6565'
        env['GODOT_MCP_RUNTIME_PORT'] = '6585'
        command = [binary, '--headless', '--path', str(clean)]
        # Isolate the asset proof from development/Steam plugins; retain renderer/physics settings.
        project = clean / 'project.godot'
        configuration = project.read_text()
        for section in ('autoload', 'editor_plugins'):
            configuration = re.sub(r'(?ms)^\[' + section + r'\]\n.*?(?=^\[|\Z)', '', configuration)
        project.write_text(configuration)
        (clean / 'addons/.gdignore').touch()
        run(command + ['--editor', '--import'], args.logs / 'clean-asset-import.log', env)
        checks.source_links(clean)
        text = run(command + ['--script', 'tests/fixtures/s01/check_s01.gd'],
                   args.logs / 'clean-resources.log', env)
        assert 'S01_RESULT checks complete; failures=0' in text
        before = {str(p.relative_to(clean)): p.read_bytes() for p in checks.owned_files(clean)
                  if p.suffix in ('.tscn', '.tres', '.uid', '.import')}
        for path, contents in before.items():
            assert (ROOT / path).read_bytes() == contents, 'clean import changed identity/settings: ' + path
        # Corruption is confined to an isolated test copy, never an open authoring scene.
        scene = clean / 'tests/fixtures/s01/roundtrip.tscn'
        original = scene.read_text()
        cases = [
            ('wrong-id', 's01/roundtrip/statica', 'wrong/id', 'StaticA authored world_id'),
            ('wrong-placement', '-3, 0, 0)', '-4, 0, 0)', 'StaticA authored position'),
            ('duplicate-id', 's01/roundtrip/staticb', 's01/roundtrip/statica', 'StaticB distinct world_id'),
        ]
        for name, old, new, expected in cases:
            assert old in original
            scene.write_text(original.replace(old, new, 1))
            run(command + ['--script', 'tests/fixtures/s01/check_s01.gd'],
                args.logs / (name + '.log'), env, expected)
            scene.write_text(original)
        variant = clean / 'tests/fixtures/s01/static_variant.tscn'
        original_variant = variant.read_text()
        petrol = (clean / 'art/materials/s01_petrol.tres').read_text()
        coral_uid = re.search(r'uid="(uid://[^"]+)"', original_variant.split('type="Material"')[1]).group(1)
        petrol_uid = re.search(r'uid="(uid://[^"]+)"', petrol).group(1)
        variant.write_text(original_variant.replace(coral_uid, petrol_uid))
        run(command + ['--script', 'tests/fixtures/s01/check_s01.gd'],
            args.logs / 'wrong-material-uid.log', env, 'inherited coral override')
        variant.write_text(original_variant)
        rig_import = clean / 'art/models/spikes/s01_rig.glb.import'
        original_import = rig_import.read_text()
        marker = '"idle": {'
        index = original_import.index(marker)
        rig_import.write_text(original_import[:index] + original_import[index:].replace(
            '"settings/loop_mode": 1', '"settings/loop_mode": 0', 1))
        run(command + ['--editor', '--import'], args.logs / 'bad-loop-import.log', env)
        run(command + ['--script', 'tests/fixtures/s01/check_s01.gd'],
            args.logs / 'wrong-loop.log', env, 'idle loop mode')
        rig_import.write_text(original_import)
        source = clean / 'art/source/models/spikes/s01_static.blend'
        source.unlink()
        try:
            checks.source_links(clean)
        except FileNotFoundError:
            print('PASS missing Blender source rejected')
        else:
            raise AssertionError('missing source accepted')
        broken = clean / 'tests/fixtures/s01/unused_broken.gd'
        broken.write_text('extends Node\nfunc broken( -> void:\n\tpass\n')
        assert broken in list(checks.owned_files(clean))
        run(command + ['--check-only', '--script', 'tests/fixtures/s01/unused_broken.gd'],
            args.logs / 'unused-script.log', env, 'Parse Error')
        (args.logs / 'summary.json').write_text(json.dumps({
            'clean_import': 'pass', 'resources': 'pass',
            'persisted_files_unchanged': len(before),
            'negative_probes': ['wrong-id', 'wrong-placement', 'duplicate-id', 'wrong-material-uid',
                                'wrong-loop', 'missing-source', 'unused-script'],
        }, indent=2) + '\n')


if __name__ == '__main__':
    main()
