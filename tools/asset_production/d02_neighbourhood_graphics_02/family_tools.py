"""Retarget existing notice tooling in memory; never copy or mutate sibling carrier/tool files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_02"
FAMILY = ROOT / "tools/asset_production/d02_neighbourhood_graphics_01"
REUSED = ("export.py", "validate.py", "preview.py", "finalize.py", "manifest.py")


def load_tool(filename):
    """Preserve the sibling's assertions while redirecting its output ID and artwork stem."""
    assert filename in REUSED
    path = FAMILY / filename
    code = path.read_text(encoding="utf-8")
    assert "d02_neighbourhood_graphics_01" in code, "Family tool interface changed"
    code = code.replace("d02_neighbourhood_graphics_01", NID)
    code = code.replace("d02_neighbourhood_graphics.01", "d02_neighbourhood_graphics.02")
    code = code.replace("watch_notice", "parking_request").replace("WATCH_", "PARKING_")
    namespace = {"__file__": str(Path(__file__).with_name(filename)),
                 "__name__": "parking_notice_" + Path(filename).stem}
    exec(compile(code, str(path), "exec"), namespace)
    if filename == "validate.py":
        namespace["DEPENDENCIES"].extend(
            str((FAMILY / name).relative_to(ROOT)).replace("\\", "/")
            for name in (*REUSED, "author.py", "check_prefab.gd")
        )
    return namespace
