"""Independent pixel expectations protect quiet space, paint layout and export reproducibility."""
import hashlib
import io
import json
from pathlib import Path
from PIL import Image
from artwork import artwork, TEXTURE

SCRATCH = Path('C:/tmp/ft/assets/d01_sports_surface_02')


def main():
    """Check actual committed PNG, including literal field landmarks and unpainted regions."""
    raw = TEXTURE.read_bytes()
    fresh = io.BytesIO()
    artwork().save(fresh, format='PNG', compress_level=9)
    assert fresh.getvalue() == raw
    image = Image.open(TEXTURE)
    assert image.size == (2048, 1024) and image.mode == 'RGBA'
    assert all(channel.getextrema() == (value, value)
               for channel, value in zip(image.split()[:3], (246, 241, 220)))
    alpha = image.getchannel('A')

    def sample(x, z):
        """Sample independent Godot-axis metre positions in the saved artwork."""
        return alpha.getpixel((round((x + 26) * 2048 / 52),
                               round((z + 13) * 1024 / 26)))

    for x, z in [(-25, 0), (25, 8), (10, -12), (-10, 12), (0, 8), (0, 0),
                 (3.5, 0), (-3.5, 0), (19, 0), (-19, 4), (22, 6), (-22, -6),
                 (23, 1), (-23, -1), (24, 3), (-24, -3)]:
        assert sample(x, z) > 245, (x, z, sample(x, z))
    for x, z in [(10, 0), (-10, 0), (1, 1), (24, 1), (21, 4), (10, 11),
                 (25.6, 0), (-25.6, 0), (0, 12.6), (0, -12.6), (5, 5)]:
        assert sample(x, z) == 0, (x, z)
    histogram = alpha.histogram()
    coverage = sum(histogram[128:]) / (2048 * 1024)
    assert .03 < coverage < .04, coverage
    # Border and middle lanes of the image remain transparent; no opaque grass rectangle.
    assert alpha.crop((0, 0, 2048, 20)).getextrema() == (0, 0)
    assert alpha.crop((0, 1004, 2048, 1024)).getextrema() == (0, 0)
    # Literal transverse section at X=10 crosses only the two touchlines.
    column = [sample(10, -12.5 + step * .025) >= 128 for step in range(1000)]
    runs = sum(value and (i == 0 or not column[i - 1]) for i, value in enumerate(column))
    assert runs == 2
    report = {'ok': True, 'byte_identical_reproduction': True,
              'png_bytes': len(raw), 'png_sha256': hashlib.sha256(raw).hexdigest(),
              'size': [2048, 1024], 'mode': 'RGBA', 'opaque_fraction_at_half_alpha': coverage,
              'independent_paint_landmarks': 16, 'independent_clear_landmarks': 11,
              'transverse_boundary_runs': runs, 'transparent_border': True,
              'uniform_ivory_rgb': True, 'pillow': '12.3.0'}
    (SCRATCH / 'artwork-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print('FIELD_ARTWORK_PASS', json.dumps(report))


if __name__ == '__main__':
    main()
