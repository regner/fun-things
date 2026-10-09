"""Owned guard boundary recipe in Godot metres, matching the delivered .01–.05 interfaces."""
NID = "d06_harbour_footbridge_06"
VARIANTS = ("junction", "span", "main", "south", "quay", "support_tall", "support_mid")


def edges(variant):
    """Return exposed edge endpoints and guard heights; never close mating or ground mouths."""
    if variant.startswith("support"):
        return []
    if variant == "junction":
        polygon = [(1.6, -3), (-1.6, -3), (-1.6, -1.6), (-3, -1.6),
                   (-3, 1.6), (-0.6627417, 1.6), (0.989949494, 3.252691193),
                   (3.252691193, 0.989949494), (1.6, -0.6627417)]
        return [((a[0], 0, a[1]), (b[0], 0, b[1]), 1.2)
                for i, a in enumerate(polygon) if i not in (0, 3, 6)
                for b in [polygon[(i + 1) % len(polygon)]]]
    if variant == "span":
        return [((x, 0, 0), (x, 0, -12), 1.2) for x in (-1.6, 1.6)]
    result = []
    for x in (-1.6, 1.6):
        result += [((x, 5.5, 0), (x, 5.5, -3.2), 1.2),
                   ((x, 5.5, -3.2), (x, 2.75, -8.32), 1.38)]
    if variant == "main":
        for x in (-1.6, 1.6):
            result += [((x, 2.75, -8.32), (x, 2.75, -11.52), 1.2),
                       ((x, 2.75, -11.52), (x, 0, -16.64), 1.38),
                       ((x, 0, -16.64), (x, 0, -19.84), 1.2)]
    else:
        sign = 1 if variant == "south" else -1
        # Mid-landing has an open upper edge and an open sideways exit.
        result += [((-sign * 1.6, 2.75, -8.32), (-sign * 1.6, 2.75, -11.52), 1.2),
                   ((-1.6, 2.75, -11.52), (1.6, 2.75, -11.52), 1.2)]
        for z in (-8.32, -11.52):
            result += [((sign * 1.6, 2.75, z), (sign * 6.72, 0, z), 1.38),
                       ((sign * 6.72, 0, z), (sign * 9.92, 0, z), 1.2)]
    return result


def guard_prism(a, b, bottom, top, width=0.12):
    """Create vertical end planes for a simple edge prism, including sloping stair guards."""
    dx, dz = b[0] - a[0], b[2] - a[2]
    length = (dx * dx + dz * dz) ** 0.5
    nx, nz = -dz / length * width / 2, dx / length * width / 2
    return [(p[0] + s * nx, p[1] + h, p[2] + s * nz)
            for h in (bottom, top) for p in (a, b) for s in (-1, 1)]


def prefab_suffix(variant):
    """Keep the junction as the default family wrapper; other pieces have explicit suffixes."""
    return "" if variant == "junction" else "_" + variant
