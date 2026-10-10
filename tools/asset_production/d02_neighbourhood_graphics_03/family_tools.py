"""Reuse existing artwork tooling in memory while targeting the accepted fascia interface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_03"
FAMILY = ROOT / "tools/asset_production/d02_neighbourhood_graphics_01"
HALL = ROOT / "tools/asset_production/d06_commercial_graphics_01"
REUSED = ("export.py", "validate.py", "finalize.py", "manifest.py")


def replace_once(code, old, new):
    """Fail on upstream contract drift instead of silently skipping a required adaptation."""
    assert code.count(old) == 1, old
    return code.replace(old, new)


def load_tool(filename):
    """Redirect outputs, preserving shared export/audit assertions and inventory logic."""
    assert filename in (*REUSED, "preview.py")
    path = (HALL if filename == "preview.py" else FAMILY) / filename
    code = path.read_text(encoding="utf-8")
    if filename == "preview.py":
        code = code.replace("d06_commercial_graphics_01", NID)
        code = code.replace("hall_title", "corner_cupboard").replace("HALL_", "CORNER_")
        code = replace_once(code, 'default_value = 0.56', 'default_value = 0.8')
        code = replace_once(code, 'resolution_y = 800', 'resolution_y = 720')
        code = replace_once(code, 'scene.cycles.samples = 32', 'scene.cycles.samples = 24')
        code = replace_once(code, 'scene.render.film_transparent = False',
                            'scene.render.film_transparent = False\n'
                            'scene.render.image_settings.color_mode = "RGB"\n'
                            'scene.render.image_settings.compression = 100\n'
                            'scene.render.dither_intensity = 0')
    else:
        code = code.replace("d02_neighbourhood_graphics_01", NID)
        code = code.replace("d02_neighbourhood_graphics.01", "d02_neighbourhood_graphics.03")
        code = code.replace("watch_notice", "corner_cupboard").replace("WATCH_", "CORNER_")
        code = code.replace("city_sign_supports_01", "city_shop_fittings_02")
        code = code.replace("[1220, 820]", "[2000, 400]")
        if filename == "validate.py":
            code = replace_once(code, "[1.4, 1.0, 0.1]", "[3.2, 0.8, 0.14]")
            code = replace_once(
                code, 'old = "E=ROOT/\'docs/assets/production/city_shop_fittings_02-evidence\'"',
                'old = "E=Path(sys.argv[1]) if len(sys.argv)>1 else " '
                '+ "ROOT/\'docs/assets/production/city_shop_fittings_02-evidence/f1_culling\'"')
    namespace = {"__file__": str(Path(__file__).with_name(filename)),
                 "__name__": "corner_shop_" + Path(filename).stem}
    exec(compile(code, str(path), "exec"), namespace)
    if filename == "validate.py":
        namespace["DEPENDENCIES"].extend(
            (p.relative_to(ROOT).as_posix()) for p in [
                *(FAMILY / name for name in (*REUSED, "author.py", "check_prefab.gd")),
                HALL / "preview.py", ROOT / "tools/assets/blender/export_settings.json",
            ]
        )
    return namespace
