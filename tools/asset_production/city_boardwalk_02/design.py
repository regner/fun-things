"""Provisional bend geometry shared by source authoring and saved collision authoring."""
from math import cos, radians, sin

ASSET = "city_boardwalk_02"
RADIUS = 6.0
WIDTH = 3.6
DEPTH = .24
BOARD_DEPTH = .08
BOARD_GAP = .012
# One radial timber every 2.8125 degrees; centre-line pitch approximately .295 m.
VARIANTS = (("", 90.0, 32), ("_45", 45.0, 16), ("_22p5", 22.5, 8))


def point(radius, angle, z=0):
    """Return a Blender point on a right bend with entry at the surface origin."""
    return (RADIUS - radius * cos(angle), radius * sin(angle), z)


def outline(angle_degrees, segments, inset=0):
    """Return the anticlockwise annular plan polygon, retaining straight end planes."""
    angle = radians(angle_degrees)
    outer = [point(RADIUS + WIDTH / 2 - inset, angle * i / segments)[:2]
             for i in range(segments + 1)]
    inner = [point(RADIUS - WIDTH / 2 + inset, angle * i / segments)[:2]
             for i in reversed(range(segments + 1))]
    return list(reversed(outer + inner))
