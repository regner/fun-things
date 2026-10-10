"""Read-only per-face findings, explicit keep policies and non-overcounted candidate totals."""

from fnmatch import fnmatch
import numpy as np

from .geometry import (ANGLE_DEGREES, AREA_EPSILON, BVH, CONTACT_METRES, DATUM_METRES,
                       OVERLAP_SQUARE_METRES,
                       PLANE_METRES, contained_faces, fully_covered, overlap_area, unseen_faces)


def flatten(parts):
    """Retain primitive-local face IDs alongside contiguous numerical arrays."""
    triangles = np.concatenate([p.vertices[p.indices] for p in parts])
    groups = np.concatenate([np.full(len(p.indices), i, int) for i, p in enumerate(parts)])
    double = np.array([p.double_sided for p in parts])[groups]
    opaque = np.array([p.opaque for p in parts])[groups]
    crosses = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])
    length = np.linalg.norm(crosses, axis=1)
    normals = crosses / np.where(length > 0, length, 1)[:, None]
    return triangles, groups, double, opaque, normals, length/2


def coplanar_pairs(parts, triangles, groups, double, normals, areas, tree, cross_instance=False,
                   plane=PLANE_METRES, angle=ANGLE_DEGREES, overlap=OVERLAP_SQUARE_METRES):
    """Find projected overlaps and full opposing flush cover without double counting."""
    pairs = []
    contacts = {}
    sealed = np.zeros(len(triangles), bool)
    for i, j in tree.pairs(plane, normals, angle):
        if areas[i] <= AREA_EPSILON or areas[j] <= AREA_EPSILON:
            continue
        if cross_instance and parts[groups[i]].instance == parts[groups[j]].instance:
            continue
        separation = max(abs((triangles[j]-triangles[i, 0]) @ normals[i]).max(),
                         abs((triangles[i]-triangles[j, 0]) @ normals[j]).max())
        if separation > plane:
            continue
        amount = overlap_area(triangles[i], triangles[j], normals[i])
        same = normals[i] @ normals[j] > 0
        if (not same and separation <= CONTACT_METRES and amount > AREA_EPSILON and
                not (double[i] or double[j]) and parts[groups[i]].opaque and parts[groups[j]].opaque):
            contacts.setdefault(i, []).append(j)
            contacts.setdefault(j, []).append(i)
        if amount <= overlap:
            continue
        kind = 'z_fighting' if same or double[i] or double[j] else 'contact'
        pairs.append({'faces': [i, j], 'kind': kind, 'same_facing': bool(same),
                      'overlap_m2': round(amount, 8),
                      'plane_gap_m': round(float(abs((triangles[j, 0]-triangles[i, 0]) @ normals[i])), 8),
                      'center_z_up_m': np.mean([triangles[i].mean(axis=0),
                                               triangles[j].mean(axis=0)], axis=0).round(6).tolist()})
    for face, covers in contacts.items():
        sealed[face] = fully_covered(triangles[face], triangles[covers], normals[face])
    return pairs, sealed


def vertex_counts(part):
    """Separate exact full-attribute duplicates from necessary UV/normal position splits."""
    vertices = len(part.vertices)
    used = np.unique(part.indices)
    attributes = np.concatenate([part.attributes[key].reshape(vertices, -1)
                                 for key in sorted(part.attributes)], axis=1) if part.attributes else part.vertices
    return {'vertices': vertices, 'loose_vertices': vertices-len(used),
            'duplicate_vertices': vertices-len(np.unique(attributes, axis=0)),
            'position_duplicates': vertices-len(np.unique(part.vertices, axis=0))}


def analyze(parts, *, keep_reason='', dynamic=False, cross_instance=False,
            plane=PLANE_METRES, angle=ANGLE_DEGREES, overlap=OVERLAP_SQUARE_METRES):
    """Measure geometry; candidate IDs are review work, never an automatic deletion recipe."""
    if not parts or not any(len(p.indices) for p in parts):
        return {'summary': {'triangles': 0, 'vertices': 0}, 'groups': [], 'pairs': []}
    parts = [p for p in parts if len(p.indices)]
    triangles, groups, double, opaque, normals, areas = flatten(parts)
    tree = BVH(triangles, double, opaque)
    pairs, sealed = coplanar_pairs(parts, triangles, groups, double, normals, areas, tree,
                                   cross_instance, plane, angle, overlap)
    masks = {'zero_area': areas <= AREA_EPSILON}
    containers = []
    if not cross_instance:
        downward = normals[:, 2] < -.9
        bottom = downward & (abs(triangles[:, :, 2]).max(axis=1) <= DATUM_METRES)
        masks.update({'bottoms': bottom, 'elevated_undersides': downward & ~bottom,
                      'sealed': sealed})
        masks['unseen_sampled'] = unseen_faces(triangles, normals, double, opaque, tree)
        # Opposite coincident triangles can also be a deliberate two-sided sheet.
        # Full contact alone cannot make a face sealed if any sampled view sees it.
        masks['sealed'] &= masks['unseen_sampled']
        masks['inside_closed_island'], containers = contained_faces(triangles, opaque)
        # Downward double-sided carriers can be seen from above. Alpha/animated geometry
        # cannot be called removable from its rest mesh or used as a closed occluder.
        # Reflection/walk-below exceptions include sloping undersides, not only the
        # steep downward faces selected by the separate normal.z < -0.9 check.
        masks['keep_exception'] = (normals[:, 2] < 0) & bool(keep_reason)
        masks['removable_candidates'] = ((downward & ~double) | sealed |
                                         masks['unseen_sampled'] | masks['inside_closed_island'])
        masks['removable_candidates'] &= ~masks['keep_exception'] & ~masks['zero_area'] & opaque
        if dynamic:
            masks['removable_candidates'][:] = False
    report_groups = []
    offset = 0
    for index, part in enumerate(parts):
        count = len(part.indices)
        row = {'name': part.name, 'source': part.source, 'instance': part.instance,
               'material': part.material, 'double_sided': part.double_sided,
               'opaque': part.opaque, 'face_offset': offset, 'triangles': count,
               **vertex_counts(part)}
        row['faces'] = {key: np.flatnonzero(value[offset:offset+count]).tolist()
                        for key, value in masks.items()}
        report_groups.append(row)
        offset += count
    summary = {'triangles': len(triangles),
               **{key: sum(g[key] for g in report_groups) for key in
                  ('vertices', 'loose_vertices', 'duplicate_vertices', 'position_duplicates')},
               **{key: int(value.sum()) for key, value in masks.items()},
               'z_fighting_pairs': sum(p['kind'] == 'z_fighting' for p in pairs),
               'contact_pairs': sum(p['kind'] == 'contact' for p in pairs)}
    summary['removable_percent'] = round(100*summary.get('removable_candidates', 0)/len(triangles), 2)
    return {'summary': summary, 'groups': report_groups, 'pairs': pairs,
            'closed_containers': containers, 'keep_reason': keep_reason,
            'dynamic_rest_pose_only': dynamic,
            'bounds_z_up_m': [triangles.min(axis=(0, 1)).tolist(), triangles.max(axis=(0, 1)).tolist()]}


def policy_reason(path, policy):
    """Apply explicit reviewed path rules only; no inference from an arbitrary mesh name."""
    return '; '.join(rule['reason'] for rule in policy.get('keep_undersides', [])
                     if fnmatch(path, rule['glob']))


def gate_failures(report, checks):
    """Select measured finding counts without conflating audit completion with clean assets."""
    failures = []
    for scope in ('assets', 'prefabs'):
        for row in report[scope]:
            for check in checks:
                value = row['summary'].get(check, 0)
                if value:
                    failures.append({'path': row['path'], 'check': check, 'count': value})
    return failures
