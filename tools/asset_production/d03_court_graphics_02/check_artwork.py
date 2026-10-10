"""Check literal paint regions, eight distinct numerals and byte-exact Pillow reproduction."""
import hashlib
import json
from pathlib import Path

from PIL import Image

from artwork import draw_artwork

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_court_graphics_02"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
TEXTURE = ROOT / f"art/textures/environment/{NID}/play_steps_albedo.png"


def sample(image, x, y):
    """Sample a literal 3 x 6 m atlas in Blender XY, north at the image top."""
    return image.getpixel((round((x + 1.5) * 512 / 3), round((3 - y) * 1024 / 6)))


def main():
    """Assert independent color/number expectations; reject blank or duplicated labels."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    fresh = SCRATCH / "reproduced_albedo.png"
    draw_artwork(fresh)
    raw = TEXTURE.read_bytes()
    assert fresh.read_bytes() == raw
    image = Image.open(TEXTURE)
    assert image.size == (512, 1024) and image.mode == "RGB"
    teal, ivory, coral = (88, 125, 124), (206, 205, 184), (185, 131, 119)
    cells = [(0, -2.25), (0, -1.35), (-.5, -.45), (.5, -.45),
             (0, .45), (-.5, 1.35), (.5, 1.35), (0, 2.25)]
    crops, counts, samples = [], [], 0
    for number, (cx, cy) in enumerate(cells, 1):
        fill = coral if number in (3, 4) else teal
        for dx, dy, expected in [(-.30, 0, fill), (.30, 0, fill),
                                  (0, .28, fill), (0, -.28, fill),
                                  (-.42, 0, ivory), (.42, 0, ivory),
                                  (0, .37, ivory), (0, -.37, ivory)]:
            assert sample(image, cx + dx, cy + dy) == expected, (number, dx, dy)
            samples += 1
        # Sample each number at equal physical offsets, excluding the outer border.
        pixels = [sample(image, cx + x * .005, cy + y * .005)
                  for y in range(-46, 47) for x in range(-34, 35)]
        pale = sum(pixel == ivory for pixel in pixels)
        assert 400 < pale < 2600, (number, pale)
        counts.append(pale)
        crops.append(bytes(channel for pixel in pixels for channel in pixel))
    assert len(set(crops)) == 8
    # Specific glyph landmarks: upright 1, rule of 7, open counters and waist of 8.
    anchors = [(0, -2.25, ivory), (-.07, -2.25, teal),
               (.5, 1.54, ivory), (.60, 1.18, teal),
               (0, 2.35, teal), (0, 2.15, teal), (0, 2.25, ivory),
               (.40, -.30, coral)]
    for x, y, expected in anchors:
        assert sample(image, x, y) == expected, (x, y, sample(image, x, y), expected)
    report = {"ok": True, "png_bytes": len(raw), "png_sha256": hashlib.sha256(raw).hexdigest(),
              "resolution": [512, 1024], "mode": "RGB", "exact_region_samples": samples + len(anchors),
              "eight_distinct_number_crops": True, "glyph_pale_sample_counts": counts,
              "byte_identical_reproduction": True, "coral_numbers": [3, 4],
              "no_alpha_or_external_fonts": True}
    (SCRATCH / "artwork-check.json").write_text(json.dumps(report, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")
    print("PLAY_ARTWORK_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
