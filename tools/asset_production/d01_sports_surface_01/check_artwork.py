"""Check runtime PNG pixels, lane readability and deterministic artwork reproduction."""
import hashlib
import json
from pathlib import Path

from PIL import Image

from artwork import create_artwork

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_sports_surface_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
TEXTURE = ROOT / f"art/textures/environment/{NID}/oval_track_albedo.png"


def pixel(image, x, z):
    """Sample independently specified Godot-space points in the plan atlas."""
    return image.getpixel((round((x + 40) * 51.2), round((z + 22.5) * 51.2)))


def main():
    """Require seven boundaries, six marked lanes, a south-only finish and quiet base."""
    image = Image.open(TEXTURE)
    assert image.size == (4096, 2304) and image.mode == "RGB"
    assert pixel(image, 0, 0) == (171, 115, 95)
    # At an unadorned straight, seven separated ivory runs must delimit the six lanes.
    runs = []
    active = None
    for row in range(1920, 2304):
        bright = min(image.getpixel((2048, row))) > 200
        if bright and active is None:
            active = row
        elif not bright and active is not None:
            runs.append([active, row - 1])
            active = None
    assert active is None and len(runs) == 7, runs
    assert all(5 <= last - first + 1 <= 9 for first, last in runs)
    centres = [(first + last) / 2 for first, last in runs]
    assert all(53 <= b - a <= 56 for a, b in zip(centres, centres[1:]))
    lane_centres = [16.55, 17.61, 18.67, 19.73, 20.79, 21.85]
    for z in lane_centres:
        assert min(pixel(image, 9, z)) > 210, "Finish bar must cross every south lane"
        assert pixel(image, 9, -z) == (171, 115, 95), "No duplicate north finish"
        assert pixel(image, 0, z) == (171, 115, 95), "Quiet solid lane fill"
        crop = image.crop((round(46.75 * 51.2), round((z + 22.08) * 51.2),
                           round(47.53 * 51.2), round((z + 22.92) * 51.2)))
        bright_pixels = sum(min(rgb) > 200 for rgb in crop.get_flattened_data())
        assert 100 < bright_pixels < 650, (z, bright_pixels)
    recreated = SCRATCH / "recreated_albedo.png"
    create_artwork().save(recreated, compress_level=9)
    assert recreated.read_bytes() == TEXTURE.read_bytes()
    report = {
        "ok": True, "dimensions": list(image.size), "mode": image.mode,
        "seven_lane_boundaries": runs, "boundary_spacing_pixels": [
            b - a for a, b in zip(centres, centres[1:])],
        "six_numeral_regions_have_paint": True, "south_only_finish": True,
        "quiet_fill_rgb": [171, 115, 95], "byte_identical_reproduction": True,
        "png_bytes": TEXTURE.stat().st_size,
        "png_sha256": hashlib.sha256(TEXTURE.read_bytes()).hexdigest(),
    }
    (SCRATCH / "artwork-check.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("TRACK_ARTWORK_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
