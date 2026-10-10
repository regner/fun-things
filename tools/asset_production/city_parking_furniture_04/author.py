"""Author an original bus-stop pictogram for the existing small road-sign carrier."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = "city_parking_furniture_04"
OUTPUT = ROOT / f"art/textures/environment/{NID}/bus_stop_albedo.png"
SIZE = 512
SUPERSAMPLE = 4
PETROL = "#123646"
IVORY = "#F6F1DC"
AMBER = "#FFC05A"


def artwork():
    """Draw broad bus-front shapes without fonts, brand marks or route promises."""
    image = Image.new("RGB", (SIZE * SUPERSAMPLE,) * 2, PETROL)
    draw = ImageDraw.Draw(image)

    def rounded(bounds, radius, color):
        """Scale authored pixel coordinates once for clean antialiased curves."""
        draw.rounded_rectangle(tuple(v * SUPERSAMPLE for v in bounds),
                               radius=radius * SUPERSAMPLE, fill=color)

    # The amber roof/destination strip ties this quiet travel prop to parking furniture.
    # Wheels are separated below the broad body; the split windscreen reads as a bus.
    rounded((142, 351, 186, 411), 13, IVORY)
    rounded((326, 351, 370, 411), 13, IVORY)
    rounded((117, 100, 395, 379), 44, IVORY)
    rounded((166, 119, 346, 148), 9, AMBER)
    rounded((144, 171, 368, 282), 14, PETROL)
    draw.rectangle((249 * SUPERSAMPLE, 170 * SUPERSAMPLE,
                    263 * SUPERSAMPLE, 283 * SUPERSAMPLE), fill=IVORY)
    rounded((145, 315, 192, 341), 10, PETROL)
    rounded((320, 315, 367, 341), 10, PETROL)
    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main():
    """Write the sole runtime image reproducibly; hardware is intentionally not duplicated."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    artwork().save(OUTPUT, compress_level=9)
    print(f"BUS_STOP_ARTWORK_PASS {OUTPUT}")


if __name__ == "__main__":
    main()
