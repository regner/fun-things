"""Numerical audit predicates and a packet-ray BVH; numpy is the only dependency."""

from dataclasses import dataclass
import math

import numpy as np

PLANE_METRES = 0.001
ANGLE_DEGREES = 0.1
OVERLAP_SQUARE_METRES = 0.0025
DATUM_METRES = 0.02
CONTACT_METRES = 1e-5
AREA_EPSILON = 1e-12
VOLUME_EPSILON = 1e-12
RAY_EPSILON = 1e-5
WELD_METRES = 1e-6
LEAF_SIZE = 12


def overlap_area(a, b, normal):
    """Clip two coplanar triangles in their dominant projection, returning real m²."""
    axis = int(np.argmax(np.abs(normal)))
    axes = [i for i in range(3) if i != axis]
    polygon = [p[axes] for p in a]
    clip = b[:, axes]

    def cross(u, v):
        return u[0]*v[1] - u[1]*v[0]

    orientation = np.sign(cross(clip[1]-clip[0], clip[2]-clip[0]))
    for i in range(3):
        start, end = clip[i], clip[(i+1) % 3]
        edge = end-start
        result = []
        for j, p in enumerate(polygon):
            q = polygon[(j+1) % len(polygon)]
            dp = orientation*cross(edge, p-start)
            dq = orientation*cross(edge, q-start)
            if dp >= 0:
                result.append(p)
            if (dp < 0) != (dq < 0):
                result.append(p + (q-p)*(dp/(dp-dq)))
        polygon = result
        if len(polygon) < 3:
            return 0.0
    area = abs(sum(cross(polygon[i], polygon[(i+1) % len(polygon)])
                   for i in range(len(polygon)))) / 2
    return float(area / abs(normal[axis]))


def fully_covered(triangle, covers, normal):
    """Subtract opposing triangles from a face; overlapping covers never count twice."""
    axis = int(np.argmax(abs(normal)))
    axes = [i for i in range(3) if i != axis]
    remaining = [triangle[:, axes]]

    def cross(u, v):
        return u[0]*v[1]-u[1]*v[0]

    def polygon_area(polygon):
        return abs(sum(cross(polygon[i], polygon[(i+1) % len(polygon)])
                       for i in range(len(polygon))))/2

    def half(polygon, start, edge, sign):
        result = []
        for index, p in enumerate(polygon):
            q = polygon[(index+1) % len(polygon)]
            dp, dq = sign*cross(edge, p-start), sign*cross(edge, q-start)
            if dp >= 0:
                result.append(p)
            if (dp < 0) != (dq < 0):
                result.append(p+(q-p)*dp/(dp-dq))
        return np.array(result)

    for cover in covers:
        clip = cover[:, axes]
        sign = np.sign(cross(clip[1]-clip[0], clip[2]-clip[0]))
        leftovers = []
        for polygon in remaining:
            inside = polygon
            for i in range(3):
                if len(inside) < 3:
                    break
                start, edge = clip[i], clip[(i+1) % 3]-clip[i]
                outside = half(inside, start, edge, -sign)
                # Coincident boundaries otherwise accumulate zero-area fragments
                # exponentially across dense flush construction (marina deck regression).
                if len(outside) >= 3 and polygon_area(outside) > AREA_EPSILON:
                    leftovers.append(outside)
                inside = half(inside, start, edge, sign)
        remaining = leftovers
        if not remaining:
            return True
    area = sum(polygon_area(p) for p in remaining)
    original = abs(cross(triangle[1, axes]-triangle[0, axes],
                         triangle[2, axes]-triangle[0, axes]))/2
    return area <= max(AREA_EPSILON, original*1e-6)


@dataclass
class Branch:
    """Tight AABB and either triangle IDs or two median-split children."""

    low: np.ndarray
    high: np.ndarray
    ids: np.ndarray | None = None
    left: object = None
    right: object = None


class BVH:
    """Shared broad phase for exact triangle overlaps and bounded packet ray casts."""

    def __init__(self, triangles, double_sided=None, opaque=None):
        self.triangles = triangles
        self.a = triangles[:, 0]
        self.e1 = triangles[:, 1]-self.a
        self.e2 = triangles[:, 2]-self.a
        self.double_sided = (np.ones(len(triangles), bool) if double_sided is None else double_sided)
        self.opaque = np.ones(len(triangles), bool) if opaque is None else opaque
        self.low = triangles.min(axis=1)
        self.high = triangles.max(axis=1)
        centers = (self.low+self.high)/2

        def build(ids):
            node = Branch(self.low[ids].min(axis=0), self.high[ids].max(axis=0))
            if len(ids) <= LEAF_SIZE:
                node.ids = ids
            else:
                axis = int(np.argmax(np.ptp(centers[ids], axis=0)))
                ordered = ids[np.argsort(centers[ids, axis], kind='stable')]
                mid = len(ids)//2
                node.left, node.right = build(ordered[:mid]), build(ordered[mid:])
            return node

        self.root = build(np.arange(len(triangles))) if len(triangles) else None

    def pairs(self, tolerance=PLANE_METRES, normals=None, angle=ANGLE_DEGREES):
        """Yield each AABB-overlapping triangle pair exactly once."""
        if self.root is None:
            return
        stack = [(self.root, self.root)]
        while stack:
            a, b = stack.pop()
            if np.any(a.low > b.high+tolerance) or np.any(b.low > a.high+tolerance):
                continue
            if a is b and a.ids is None:
                stack.extend([(a.left, a.left), (a.left, a.right), (a.right, a.right)])
            elif a.ids is not None and b.ids is not None:
                left, right = np.meshgrid(a.ids, b.ids, indexing='ij')
                left, right = left.ravel(), right.ravel()
                select = left < right if a is b else left != right
                select &= np.all(self.low[left] <= self.high[right]+tolerance, axis=1)
                select &= np.all(self.low[right] <= self.high[left]+tolerance, axis=1)
                if normals is not None:
                    dot = np.einsum('ij,ij->i', normals[left], normals[right])
                    select &= abs(dot) >= math.cos(math.radians(angle))
                    separation = self.a[right]-self.a[left]
                    select &= abs(np.einsum('ij,ij->i', separation, normals[left])) <= tolerance
                for i, j in zip(left[select], right[select]):
                    yield (int(min(i, j)), int(max(i, j)))
            elif b.ids is not None or (a.ids is None and np.prod(a.high-a.low) >= np.prod(b.high-b.low)):
                stack.extend([(a.left, b), (a.right, b)])
            else:
                stack.extend([(a, b.left), (a, b.right)])

    def blocked(self, origins, direction, distance):
        """Test outside-to-face rays against opaque front faces, excluding endpoint hits."""
        origins = np.asarray(origins)
        blocked = np.zeros(len(origins), bool)
        if self.root is None or not len(origins):
            return blocked
        direction = np.asarray(direction)
        stack = [(self.root, np.arange(len(origins)))]
        while stack:
            node, ids = stack.pop()
            ids = ids[~blocked[ids]]
            if not len(ids):
                continue
            start = origins[ids]
            near, far = np.zeros(len(ids)), np.full(len(ids), distance-RAY_EPSILON)
            for axis in range(3):
                if abs(direction[axis]) < 1e-14:
                    far[(start[:, axis] < node.low[axis]-RAY_EPSILON) |
                        (start[:, axis] > node.high[axis]+RAY_EPSILON)] = -1
                else:
                    t1 = (node.low[axis]-start[:, axis])/direction[axis]
                    t2 = (node.high[axis]-start[:, axis])/direction[axis]
                    near = np.maximum(near, np.minimum(t1, t2)-RAY_EPSILON)
                    far = np.minimum(far, np.maximum(t1, t2)+RAY_EPSILON)
            ids = ids[near <= far]
            if not len(ids):
                continue
            if node.ids is None:
                stack.extend([(node.left, ids), (node.right, ids)])
                continue
            tri_ids = node.ids[self.opaque[node.ids]]
            if not len(tri_ids):
                continue
            h = np.cross(direction, self.e2[tri_ids])
            det = np.einsum('ij,ij->i', self.e1[tri_ids], h)
            valid = (det > 1e-12) | (self.double_sided[tri_ids] & (abs(det) > 1e-12))
            tri_ids, h, det = tri_ids[valid], h[valid], det[valid]
            if not len(tri_ids):
                continue
            # Limit temporary ray/triangle products even for very large planes.
            for offset in range(0, len(ids), 4096):
                batch = ids[offset:offset+4096]
                s = origins[batch, None, :] - self.a[tri_ids]
                u = np.einsum('rtk,tk->rt', s, h)/det
                q = np.cross(s, self.e1[tri_ids])
                v = np.einsum('rtk,k->rt', q, direction)/det
                t = np.einsum('rtk,tk->rt', q, self.e2[tri_ids])/det
                hit = ((u >= -1e-10) & (v >= -1e-10) & (u+v <= 1+1e-10) &
                       (t > RAY_EPSILON) & (t < distance-RAY_EPSILON))
                blocked[batch] |= hit.any(axis=1)
        return blocked


def directions():
    """Sample the complete yaw range and both elevation limits, including zenith."""
    result = [(0., 0., 1.)]
    for elevation in (35, 45, 60, 75):
        angle = math.radians(elevation)
        for azimuth in range(0, 360, 15):
            yaw = math.radians(azimuth)
            result.append((math.cos(angle)*math.cos(yaw), math.cos(angle)*math.sin(yaw),
                           math.sin(angle)))
    return np.array(result)


def face_samples(triangles):
    """Use centroid plus three inset-corner samples, not just one center ray."""
    weights = np.array([[1/3, 1/3, 1/3], [.8, .1, .1], [.1, .8, .1], [.1, .1, .8]])
    return np.einsum('sk,tkj->tsj', weights, triangles)


def unseen_faces(triangles, normals, double_sided, opaque, tree):
    """Return finite-sampling candidates, never a proof of all-direction invisibility."""
    visible = np.zeros(len(triangles), bool)
    samples = face_samples(triangles)
    distance = float(np.linalg.norm(np.ptp(triangles.reshape(-1, 3), axis=0)) + 1)
    for direction in directions():
        ids = np.flatnonzero(~visible & ((normals @ direction > 1e-8) | double_sided))
        if not len(ids):
            continue
        origins = (samples[ids] + direction*distance).reshape(-1, 3)
        blocked = tree.blocked(origins, -direction, distance).reshape(-1, 4)
        visible[ids[~blocked.all(axis=1)]] = True
    return ~visible


def closed_islands(triangles):
    """Join coordinate-welded edges across export seams; only oriented 2-manifolds qualify."""
    quantized = np.rint(triangles.reshape(-1, 3)/WELD_METRES).astype(np.int64)
    _, vertex_ids = np.unique(quantized, axis=0, return_inverse=True)
    faces = vertex_ids.reshape(-1, 3)
    parents = list(range(len(faces)))

    def root(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    edges = {}
    for i, face in enumerate(faces):
        for a, b in zip(face, np.roll(face, -1)):
            key = (min(a, b), max(a, b))
            entries = edges.setdefault(key, [])
            if entries:
                parents[root(i)] = root(entries[0][0])
            entries.append((i, a < b))
    groups = {}
    for i in range(len(faces)):
        groups.setdefault(root(i), []).append(i)
    invalid = set()
    for entries in edges.values():
        if len(entries) != 2 or entries[0][1] == entries[1][1]:
            invalid.add(root(entries[0][0]))
    return [np.array(ids) for r, ids in groups.items() if r not in invalid]


def points_inside(points, triangles):
    """Three non-axis parity rays must agree; coincident edge hits count once."""
    results = np.ones(len(points), bool)
    a, e1, e2 = triangles[:, 0], triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0]
    for direction in np.array([[1, .371, .529], [-.217, 1, .413], [.319, -.271, 1]]):
        h = np.cross(direction, e2)
        det = np.einsum('ij,ij->i', e1, h)
        valid = abs(det) > 1e-12
        for index in np.flatnonzero(results):
            s = points[index]-a[valid]
            q = np.cross(s, e1[valid])
            u = np.einsum('ij,ij->i', s, h[valid])/det[valid]
            v = (q @ direction)/det[valid]
            t = np.einsum('ij,ij->i', q, e2[valid])/det[valid]
            hits = np.sort(t[(u >= 0) & (v >= 0) & (u+v <= 1) & (t > RAY_EPSILON)])
            unique = hits[np.r_[True, np.diff(hits) > RAY_EPSILON]] if len(hits) else hits
            results[index] &= len(unique) % 2 == 1
    return results


def contained_faces(triangles, opaque):
    """Find faces sampled strictly inside a different closed opaque connected island."""
    contained = np.zeros(len(triangles), bool)
    memberships = []
    samples = np.concatenate([triangles, face_samples(triangles)], axis=1)
    low, high = triangles.min(axis=1), triangles.max(axis=1)
    for island in closed_islands(triangles):
        if not opaque[island].all():
            continue
        shell = triangles[island]
        # An inside-out single-sided shell is transparent from outside; topology alone
        # must not label its contents invisible. Reject ambiguous/zero-volume shells too.
        relative = shell-shell[0, 0]
        volume = np.einsum('ij,ij->i', relative[:, 0],
                           np.cross(relative[:, 1], relative[:, 2])).sum()/6
        if volume <= VOLUME_EPSILON:
            continue
        minimum, maximum = shell.min(axis=(0, 1)), shell.max(axis=(0, 1))
        ids = np.flatnonzero(~contained & np.all(low > minimum+RAY_EPSILON, axis=1) &
                             np.all(high < maximum-RAY_EPSILON, axis=1))
        ids = np.setdiff1d(ids, island)
        if not len(ids):
            continue
        inside = points_inside(samples[ids].reshape(-1, 3), shell).reshape(-1, 7).all(axis=1)
        contained[ids[inside]] = True
        if inside.any():
            memberships.append({'container_face': int(island[0]), 'faces': ids[inside].tolist()})
    return contained, memberships
