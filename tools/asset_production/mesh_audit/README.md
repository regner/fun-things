# Read-only exported-mesh audit

Run from the repository root with the existing Python and numpy installation
(verified Python 3.14.2 / numpy 2.5.1). No Blender, Godot, downloads, import cache,
or third-party geometry library is needed. Nothing under `art/` or `scenes/` is written.

```sh
python -m unittest tools.test_mesh_audit -v
# Fresh directory outside every checkout; full inventory, two bounded CPU workers.
timeout 3600 python -m tools.asset_production.mesh_audit.run \
  --output C:/tmp/ft/mesh-audit/full-05
# A future asset's strict geometry gate; existing assets are NOT all clean.
timeout 180 python -m tools.asset_production.mesh_audit.run \
  --asset art/models/environment/example/example.glb --no-prefabs \
  --fail-on z_fighting_pairs --fail-on zero_area \
  --output C:/tmp/ft/mesh-audit/example-01
```

`--asset` is repeatable. Without it every GLB below `art/models` is audited. Unless
`--no-prefabs` is supplied, every saved `.tscn` under `scenes/prefabs` is resolved,
including nested/inherited scenes and repeated instances of the **same** GLB.
Only prefabs with multiple render instances need the additional cross-instance test.
The thin `tools/test_mesh_audit.py` exposes the real synthetic-GLB tests to canonical
`production_checks.py`; full-inventory analysis is a separate command, not a slow
production-check layer.

Exit **0** means the scan completed and no **selected** gate failed; it does not mean
there are no findings. Exit **1** means at least one `--fail-on` finding, **2** means
an incomplete scan or invalid CLI use. The JSON always lists per-input errors after
an attempted scan. No blanket suppressions/baseline exemptions are installed.

## Numerical contract

- Metres, right-handed **Z-up** output: `(glTF x, -glTF z, glTF y)`. Node TRS/matrices,
  negative/nonuniform scales and prefab parent transforms are applied once. Geometric
  triangle normals, not smoothed vertex normals, determine the checks.
- Downward: normal Z < -0.9; datum bottom: **all three** vertices within 0.02 m of
  asset zero, not minimum bounds. Other downward faces are elevated flags.
- Same-facing or double-sided opposite-facing coplanar overlap: both triangles within
  1 mm of the other's plane, <= 0.1 degrees normal difference (opposites allowed),
  clipped overlap **strictly greater than 0.0025 m²**. CLI thresholds are explicit.
  Touching edges, adjacent roof triangulation and AABB overlap alone do not qualify.
- Sealed: single-sided opaque opposite triangles flush within 0.01 mm and covering
  the full target triangle, with no sampled visibility of the target. The visibility
  condition protects deliberate two-sided sheets. Polygon subtraction unions multiple
  covers without counting overlapping covers twice. Partial/near contacts remain pair findings,
  not fully sealed-face counts. Coplanar pairs are triangle pairs, not defect sites.
- Occlusion: outside-bounds rays toward a centroid and three inset corners, over
  97 directions (15-degree yaw intervals; elevations 35, 45, 60, 75 and 90 degrees).
  Only opaque front-facing or double-sided blockers count. Zero sampled visibility
  is **a candidate**, not proof that no small opening or unsampled view exists.
- Containment: coordinate-welded (1 micrometre) outward-oriented, positive-volume,
  closed 2-manifold islands;
  test each candidate's vertices plus four face samples against *other* opaque
  islands with three independent parity rays. Duplicate edge-hit distances count
  once. Open/nonmanifold islands cannot certify containment. Concave shell crossing
  between samples remains a review risk, not a proof of full-face containment.
- Degenerate: area <= 1e-12 m². Vertices count exported accessor rows per instantiated
  primitive, not welded Blender vertices. Loose = unused index rows. Exact duplicate
  = duplicate **all exported attributes**. Position duplicates are separate diagnostic
  counts; UV, hard-normal, tangent, skin and material splits must not be welded blindly.

`removable_candidates` is the union of downward single-sided, sealed, sampled-unseen
and sampled-contained triangles, excluding degenerate, nonopaque, keep-underside and
dynamic-pose cases. It is not the sum of overlapping categories. This is a triage
upper estimate, **not approved savings or an automatic removal recipe**. Recheck
silhouette, holes, sun shadows, reflections, and actual placement before fixing.
`policy.json` holds explicit conservative bridge/water exceptions for **all negative-Z
normals**, including sloping undersides outside check 1's -0.9 threshold. Extend it for any
new asset with an over-water or walk-below usage; asset-local geometry cannot infer
future placement. Animated/skinned assets and weapon/vehicle/effect families retain
all candidate geometry because a static orientation is insufficient for deletion.

## JSON and limits

`audit.json` contains schema version, thresholds, policy, input/tool hashes, source
revision, completion and selected-gate results, per-asset summaries, per-prefab
summaries and detailed pairs. Each primitive group retains source, instance, material,
exported face offset, counts, and primitive-local triangle ID lists for every check.
Pair IDs and container IDs are global within that asset/prefab; locate them using
`face_offset <= ID < face_offset + triangles`, then subtract the offset. Pair centers
are the average of triangle centroids (a locator, **not** an overlap centroid).
Per-asset JSON receipts survive an interrupted run; an interrupted run has no complete
`audit.json` and cannot pass a gate. Elapsed wall time is contended, not performance evidence.

Supported inputs are GLB 2 uncompressed TRIANGLES (indexed/unindexed, strided/sparse
accessors), active scene hierarchy, saved static PackedScene composition with
`Transform3D`, and external StandardMaterial surface overrides. Unknown required
extensions, geometry modes, placement encodings and unresolved inherited nodes fail
rather than silently become identity geometry. Shader overrides conservatively count
as double-sided/non-occluding. CollisionShape/CollisionPolygon nodes and glTF
`-colonly`/`-convcolonly` meshes are not render triangles. Prefab evaluation applies saved external import material remaps as well as node
overrides. Nonunit import root scale and import scripts fail closed rather than
being approximated. This tool reads exported meshes, **not** engine-generated LODs
or runtime shader/script geometry. Animation, morph deformation, skin poses, displacement and gameplay hiding
are not simulated. Static prefab results therefore need actual rendered confirmation
before a visible-defect repair, especially for the character/weapon preview scenes.
