"""Independent saved-pixel checks for court proportions, linework, palette and quiet space."""
import hashlib
import io
import json
from pathlib import Path
import PIL
from PIL import Image
from artwork import artwork, TEXTURE

SCRATCH = Path('C:/tmp/ft/assets/d01_sports_surface_03')


def main():
    """Compare a fresh drawing with the PNG and sample independently specified landmarks."""
    raw = TEXTURE.read_bytes()
    fresh = io.BytesIO()
    artwork().save(fresh, format='PNG', compress_level=9)
    assert fresh.getvalue() == raw
    image = Image.open(TEXTURE)
    assert image.size == (1792, 1024) and image.mode == 'RGB'

    def sample(x, z):
        """Sample a literal Godot-axis metre coordinate in the saved atlas."""
        return image.getpixel((round((x + 14) * 64), round((z + 8) * 64)))

    painted = [(-12, 0), (12, 2), (3, -6), (-3, 6), (8, -4.5), (-8, 4.5),
               (-6, 2), (6, -2), (4, 0), (-4, 0), (0, 5), (0, -5), (0, 0)]
    green = [(-10, 2), (10, -2), (3, 3), (-3, -3), (9, 5.3), (-9, -5.3), (7, 0)]
    apron = [(-13, 0), (13, 0), (0, 7), (0, -7), (-13, -7), (13, 7)]
    for point in painted:
        assert min(sample(*point)) > 210, (point, sample(*point))
    for point in green:
        assert sample(*point) == (50, 101, 86), (point, sample(*point))
    for point in apron:
        assert sample(*point) == (41, 78, 73), (point, sample(*point))
    for box in ((0, 0, 1792, 20), (0, 1004, 1792, 1024),
                (0, 0, 20, 1024), (1772, 0, 1792, 1024)):
        assert image.crop(box).getextrema() == ((41, 41), (78, 78), (73, 73))
    # Far from service boxes, a transverse slice crosses exactly four parallel sidelines.
    column = [min(sample(9, -7 + step * .025)) > 180 for step in range(560)]
    runs = sum(value and (i == 0 or not column[i - 1]) for i, value in enumerate(column))
    assert runs == 4
    coverage = sum(min(color) > 180 for color in image.get_flattened_data()) / (1792 * 1024)
    assert .05 < coverage < .065, coverage
    report = {'ok': True, 'byte_identical_reproduction': True,
              'png_bytes': len(raw), 'png_sha256': hashlib.sha256(raw).hexdigest(),
              'size': [1792, 1024], 'mode': 'RGB', 'paint_fraction': coverage,
              'independent_paint_landmarks': len(painted),
              'independent_green_landmarks': len(green), 'independent_apron_landmarks': len(apron),
              'transverse_sideline_runs': runs, 'solid_green_border': True,
              'pillow': PIL.__version__}
    (SCRATCH / 'artwork-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print('COURT_ARTWORK_PASS', json.dumps(report))


if __name__ == '__main__':
    main()
