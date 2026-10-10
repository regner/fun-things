"""Provisional exposed-edge profiles matching the delivered boardwalk join contracts."""
from math import cos, radians, sin

ASSET = "city_boardwalk_03"
# suffix, curve angle, boundary radius, outward radial sign, straight length
VARIANTS = [("", 0, 0, 1, 6.0), ("_terminal", 0, 0, 1, 3.8)]
for angle, suffix in ((90, "90"), (45, "45"), (22.5, "22p5")):
    VARIANTS += [("_outer_" + suffix, angle, 7.8, 1, 0),
                 ("_inner_" + suffix, angle, 4.2, -1, 0)]
PROFILE = ((0, -.24), (.08, -.24), (.08, -.035), (.10, -.035), (.10, 0), (0, 0))


def station(variant, t, outward, height):
    """Map cross-section coordinates into Blender space; straight pivot is on its backing plane."""
    _suffix, angle, radius, sign, length = variant
    if not angle:
        return (outward, length * (t - .5), height)
    theta = radians(angle) * t
    r = radius + sign * outward
    return (6 - r * cos(theta), r * sin(theta), height)


def segments(variant):
    """Use the sibling bend's 2.8125-degree station spacing for exact chord mating."""
    return round(variant[1] / 2.8125) if variant[1] else 1
