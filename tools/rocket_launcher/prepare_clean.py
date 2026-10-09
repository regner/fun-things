"""Copy only the launcher runtime assets and focused checks to a fresh test project."""
import shutil
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
target = Path(sys.argv[1]).resolve()
assert not target.exists(), "Use a fresh directory; this tool never replaces an existing project."
target.mkdir(parents=True)
paths = list((root / "art/models/rocket_launcher").glob("*"))
paths += list((root / "scenes/prefabs/rocket_launcher").glob("*.tscn"))
paths += [root / "tests/fixtures/rocket_launcher" / name for name in [
    "preview.tscn", "stage.tscn", "preview.gd", "preview.gd.uid", "studio_environment.tres",
]]
paths += [root / "tools/rocket_launcher" / name for name in ["capture_check.gd", "capture_check.gd.uid"]]
for source in paths:
    destination = target / source.relative_to(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
(target / "docs/assets/rocket_launcher_evidence").mkdir(parents=True)
(target / "project.godot").write_text('''config_version=5

[application]
config/name="Dock Thumper isolated asset check"

[display]
window/size/viewport_width=1280
window/size/viewport_height=800
''')
print(f"Prepared {len(paths)} source-identical runtime files in {target}")
