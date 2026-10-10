"""Independently check palette, landmark regions, texture format and exact Pillow reproduction."""
import hashlib
import json
import math
from pathlib import Path

from PIL import Image

from artwork import draw_artwork

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_court_graphics_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
TEXTURE = ROOT / f"art/textures/environment/{NID}/communal_circle_albedo.png"


def sample(image, radius, degrees):
    """Sample the literal 14 m artwork footprint, clockwise from east/screen right."""
    angle = math.radians(degrees)
    x = round(512 + math.cos(angle) * radius * 1024 / 14)
    y = round(512 + math.sin(angle) * radius * 1024 / 14)
    return image.getpixel((x, y))


def main():
    """Reject region, palette, dimensional or deterministic-authoring regressions."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    fresh = SCRATCH / "reproduced_albedo.png"
    draw_artwork(fresh)
    raw = TEXTURE.read_bytes()
    assert fresh.read_bytes() == raw
    image = Image.open(TEXTURE)
    assert image.size == (1024, 1024) and image.mode == "RGB"
    colors = {"teal": (88, 125, 124), "ivory": (206, 205, 184),
              "joint": (136, 156, 151), "stone": (155, 168, 162),
              "panel": (167, 176, 165), "coral": (185, 131, 119)}
    samples = 0
    for angle in range(15, 360, 30):
        for radius, color in [(6.8, "teal"), (4.48, "teal"), (6.45, "ivory")]:
            assert sample(image, radius, angle) == colors[color]
            samples += 1
    # Twelve independent sector-centre expectations; coral is a single 60-degree southwest corner.
    expected = ["panel", "stone", "panel", "coral", "coral", "stone",
                "panel", "stone", "panel", "stone", "panel", "stone"]
    for index, color in enumerate(expected):
        assert sample(image, 5.5, index * 30 + 15) == colors[color]
        samples += 1
    # Joints are broad, low contrast, and the unconsumed centre is quiet rather than a target icon.
    for angle in (0, 90, 180, 270):
        assert sample(image, 5.5, angle) == colors["joint"]
        samples += 1
    assert image.getpixel((512, 512)) == colors["stone"]
    report = {"ok": True, "png_bytes": len(raw), "png_sha256": hashlib.sha256(raw).hexdigest(),
              "resolution": [1024, 1024], "mode": "RGB", "exact_region_samples": samples + 1,
              "byte_identical_reproduction": True, "clockwise_coral_sectors": [3, 4],
              "no_alpha_or_external_fonts": True}
    (SCRATCH / "artwork-check.json").write_text(json.dumps(report, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")
    print("MOTIF_ARTWORK_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
