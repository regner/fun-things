"""Reproduce P0-07's deliberately flawed copy; never modifies the source project.

Run from any cwd: python docs/reviews/fixtures/p0_07.py --root <repository>
The printed /tmp directory is retained for independent review. This is a one-off
review experiment recipe, not an asset authoring or production validation tool.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    temporary = Path(tempfile.mkdtemp(prefix='p0-07-review-', dir='/tmp'))
    project = temporary / 'project'
    project.mkdir()
    # Asset profile follows S01: no plugins, autoloads or shared editor connection.
    for directory in ('art', 'tests/fixtures/s01', 'tools/s01'):
        shutil.copytree(root / directory, project / directory,
                        ignore=shutil.ignore_patterns('__pycache__'))
    for filename in ('mise.toml', 'tools/check.py', 'icon.svg', 'icon.svg.import'):
        shutil.copy2(root / filename, project / filename)
    configuration = (root / 'project.godot').read_text()
    for section in ('autoload', 'editor_plugins'):
        configuration = re.sub(r'(?ms)^\[' + section + r'\]\n.*?(?=^\[|\Z)', '',
                               configuration)
    (project / 'project.godot').write_text(configuration)
    edits = {
        'tests/fixtures/s01/static_prefab.tscn': [
            ('size = Vector3(2, 1, 1)', 'size = Vector3(4, 1, 1)'),
            ('0, 0.5, 0)', '0, 1.5, 0)'),
        ],
        'tests/fixtures/s01/roundtrip.tscn': [
            ('s01/roundtrip/staticb', 's01/roundtrip/statica'),
        ],
    }
    diff = []
    for relative, replacements in edits.items():
        path = project / relative
        before = path.read_text()
        after = before
        for old, new in replacements:
            assert after.count(old) == 1, (relative, old)
            after = after.replace(old, new)
        path.write_text(after)
        diff.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                        fromfile='original/' + relative,
                                        tofile='candidate/' + relative))
    (temporary / 'fixture.patch').write_text(''.join(diff))
    preserved = {}
    for original in sorted((root / 'art').rglob('*')):
        if original.is_file():
            relative = str(original.relative_to(root))
            copied = project / relative
            assert original.read_bytes() == copied.read_bytes(), relative
            preserved[relative] = {'original_sha256': digest(original),
                                   'copy_sha256': digest(copied)}
    manifest = {
        'base_revision': subprocess.check_output(
            ['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
        'source_root': str(root), 'temporary_root': str(temporary),
        'changed_fixture_files': list(edits), 'preserved_art_files': preserved,
        'scope': 'Temporary negative fixture only; no source/export/visible mesh changes',
    }
    (temporary / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(temporary)


if __name__ == '__main__':
    main()
