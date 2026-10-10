extends RefCounted
## Stateless XZ footprint geometry for the Brackett clearance gate (test_brackett_clearance.gd).

const CYLINDER_SIDES: int = 16


## Walks a subtree and returns XZ footprints for collision shapes and visible geometry.
##
## Transforms are accumulated from `root_to_world` so prefabs outside the tree can be measured;
## non-3D nodes pass their parent's transform through.
static func collect_footprints(
	root: Node, root_to_world: Transform3D, failures: PackedStringArray
) -> Array[Footprint]:
	var footprints: Array[Footprint] = []
	var pending: Array[Array] = [[root, root_to_world, true]]
	while not pending.is_empty():
		var entry: Array = pending.pop_back()
		var node: Node = entry[0]
		var world: Transform3D = entry[1]
		var visible: bool = entry[2] and not (node is Node3D and not (node as Node3D).visible)
		var footprint: Footprint = node_footprint(root, node, world, visible, failures)
		if footprint != null:
			footprints.append(footprint)
		for child: Node in node.get_children():
			var child_world: Transform3D = world * (child as Node3D).transform if (
				child is Node3D
			) else world
			pending.append([child, child_world, visible])
	return footprints


## Returns the footprint of one collision shape or visible geometry node, if it has one.
static func node_footprint(
	root: Node, node: Node, world: Transform3D, visible: bool, failures: PackedStringArray
) -> Footprint:
	var source: String = str(root.get_path_to(node))
	if node is CollisionPolygon3D:
		failures.append("unsupported CollisionPolygon3D at " + source)
		return null
	if node is CollisionShape3D:
		var points: PackedVector3Array = shape_points((node as CollisionShape3D).shape)
		if points.is_empty():
			failures.append("unsupported collision shape at " + source)
			return null
		return make_footprint(points, world, true, source)
	if visible and (node is GeometryInstance3D or node is Decal):
		var aabb: AABB = (node as VisualInstance3D).get_aabb()
		return make_footprint(box_points(aabb.position, aabb.end), world, false, source)
	return null


## Returns conservative local hull points for supported shapes, or none to fail closed.
static func shape_points(shape: Shape3D) -> PackedVector3Array:
	if shape is BoxShape3D:
		var half: Vector3 = (shape as BoxShape3D).size * 0.5
		return box_points(-half, half)
	if shape is CylinderShape3D:
		var cylinder: CylinderShape3D = shape as CylinderShape3D
		# Circumscribed polygon, so the footprint never under-covers the circle.
		var radius: float = cylinder.radius / cos(PI / CYLINDER_SIDES)
		var points := PackedVector3Array()
		for side: int in CYLINDER_SIDES:
			var angle: float = TAU * side / CYLINDER_SIDES
			var rim := Vector3(cos(angle) * radius, 0.0, sin(angle) * radius)
			points.append(rim + Vector3.UP * cylinder.height * 0.5)
			points.append(rim - Vector3.UP * cylinder.height * 0.5)
		return points
	if shape is ConvexPolygonShape3D:
		return (shape as ConvexPolygonShape3D).points
	return PackedVector3Array()


## Lists the eight corners of an axis-aligned local box.
static func box_points(low: Vector3, high: Vector3) -> PackedVector3Array:
	var points := PackedVector3Array()
	for x: float in [low.x, high.x]:
		for y: float in [low.y, high.y]:
			for z: float in [low.z, high.z]:
				points.append(Vector3(x, y, z))
	return points


## Projects transformed local points to an XZ convex hull with its lowest world height.
static func make_footprint(
	points: PackedVector3Array, world: Transform3D, is_collision: bool, source: String
) -> Footprint:
	var planar := PackedVector2Array()
	var bottom: float = INF
	for point: Vector3 in points:
		var world_point: Vector3 = world * point
		planar.append(Vector2(world_point.x, world_point.z))
		bottom = minf(bottom, world_point.y)
	var footprint := Footprint.new()
	footprint.polygon = hull(planar)
	footprint.bottom_m = bottom
	footprint.is_collision = is_collision
	footprint.source = source
	footprint.bounds = PolygonIndex.polygon_bounds(footprint.polygon)
	return footprint


## Returns an open convex hull; Godot repeats the first hull point at the end.
static func hull(points: PackedVector2Array) -> PackedVector2Array:
	var closed: PackedVector2Array = Geometry2D.convex_hull(points)
	if closed.size() > 1 and closed[0] == closed[closed.size() - 1]:
		closed.remove_at(closed.size() - 1)
	return closed


## Returns the collision or the visual footprints of a list, keeping the typed array.
static func of_kind(footprints: Array[Footprint], collision: bool) -> Array[Footprint]:
	var selected: Array[Footprint] = []
	for footprint: Footprint in footprints:
		if footprint.is_collision == collision:
			selected.append(footprint)
	return selected


## Returns a rigidly transformed copy; transforms are yaw-only, so hulls stay exact.
static func transformed_copy(footprint: Footprint, transform: Transform3D) -> Footprint:
	var copy: Footprint = shifted_copy(footprint, Vector2.ZERO)
	var polygon := PackedVector2Array()
	for point: Vector2 in footprint.polygon:
		var moved: Vector3 = transform * Vector3(point.x, 0.0, point.y)
		polygon.append(Vector2(moved.x, moved.z))
	copy.polygon = polygon
	copy.bounds = PolygonIndex.polygon_bounds(polygon)
	copy.bottom_m = footprint.bottom_m + transform.origin.y
	return copy


## Returns a translated copy of a footprint.
static func shifted_copy(footprint: Footprint, shift: Vector2) -> Footprint:
	var copy := Footprint.new()
	copy.owner_id = footprint.owner_id
	copy.is_placement = footprint.is_placement
	copy.district_id = footprint.district_id
	copy.source = footprint.source
	copy.is_collision = footprint.is_collision
	copy.bottom_m = footprint.bottom_m
	var polygon := PackedVector2Array()
	for point: Vector2 in footprint.polygon:
		polygon.append(point + shift)
	copy.polygon = polygon
	copy.bounds = PolygonIndex.polygon_bounds(polygon)
	return copy


## Returns the union of footprint bounds.
static func union_bounds(footprints: Array) -> Rect2:
	var bounds: Rect2 = (footprints[0] as Footprint).bounds
	for footprint: Footprint in footprints:
		bounds = bounds.merge(footprint.bounds)
	return bounds


## Returns an exact yaw basis for the quarter turns used by fit options.
static func quarter_turn_basis(yaw_degrees: float) -> Basis:
	var radians: float = deg_to_rad(yaw_degrees)
	var cosine: float = roundf(cos(radians))
	var sine: float = roundf(sin(radians))
	return Basis(Vector3(cosine, 0.0, -sine), Vector3.UP, Vector3(sine, 0.0, cosine))


## Returns the shoelace area of a simple polygon.
static func polygon_area(polygon: PackedVector2Array) -> float:
	# Vertices are made relative to the first one and multiplied as 64-bit script floats;
	# single-precision Vector2.cross loses square metres at island coordinates.
	var twice: float = 0.0
	for index: int in range(1, polygon.size() - 1):
		var first: Vector2 = polygon[index] - polygon[0]
		var second: Vector2 = polygon[index + 1] - polygon[0]
		twice += first.x * second.y - first.y * second.x
	return absf(twice) * 0.5


## Returns the vertex centroid of a polygon.
static func polygon_centroid(polygon: PackedVector2Array) -> Vector2:
	var sum := Vector2.ZERO
	for point: Vector2 in polygon:
		sum += point
	return sum / polygon.size()


## Returns the area a polygon shares with the indexed surface triangles.
static func overlap_area(polygon: PackedVector2Array, surface: PolygonIndex) -> float:
	var area: float = 0.0
	var bounds: Rect2 = PolygonIndex.polygon_bounds(polygon)
	for index: int in surface.query(bounds):
		var triangle: PackedVector2Array = surface.polygons[index]
		if not PolygonIndex.polygon_bounds(triangle).intersects(bounds):
			continue
		for part: PackedVector2Array in Geometry2D.intersect_polygons(polygon, triangle):
			area += polygon_area(part)
	return area


## Returns the area of a polygon outside a container polygon.
static func outside_area(polygon: PackedVector2Array, container: PackedVector2Array) -> float:
	var area: float = 0.0
	for part: PackedVector2Array in Geometry2D.clip_polygons(polygon, container):
		area += polygon_area(part)
	return area


## Returns the separation of two polygons, or zero when they overlap.
static func polygon_distance(first: PackedVector2Array, second: PackedVector2Array) -> float:
	if not Geometry2D.intersect_polygons(first, second).is_empty():
		return 0.0
	return boundary_distance(first, second)


## Returns the shortest distance between two polygon boundaries.
static func boundary_distance(first: PackedVector2Array, second: PackedVector2Array) -> float:
	return minf(vertex_edge_distance(first, second), vertex_edge_distance(second, first))


## Returns the shortest distance from any vertex of one polygon to the edges of another.
static func vertex_edge_distance(points: PackedVector2Array, polygon: PackedVector2Array) -> float:
	var best: float = INF
	for point: Vector2 in points:
		for index: int in polygon.size():
			var closest: Vector2 = Geometry2D.get_closest_point_to_segment(
				point, polygon[index], polygon[(index + 1) % polygon.size()]
			)
			best = minf(best, point.distance_to(closest))
	return best


## One XZ footprint of a collision shape or visual part, in world space.
class Footprint:
	var owner_id: String
	var is_placement: bool = false
	var district_id: int = 0
	var source: String
	var is_collision: bool = false
	var polygon := PackedVector2Array()
	var bottom_m: float = 0.0
	var bounds := Rect2()


## Uniform-grid broad phase over XZ polygons; item indices follow insertion order.
class PolygonIndex:
	const CELL_SIZE_M: float = 32.0

	var polygons: Array[PackedVector2Array] = []
	var _cells: Dictionary[Vector2i, Array] = {}


	## Stores one polygon and registers it in every grid cell its bounds touch.
	func add(polygon: PackedVector2Array) -> void:
		var index: int = polygons.size()
		polygons.append(polygon)
		for cell: Vector2i in _cells_for(polygon_bounds(polygon)):
			if not _cells.has(cell):
				_cells[cell] = []
			_cells[cell].append(index)


	## Returns each stored polygon index whose cells touch the query rectangle once.
	func query(area: Rect2) -> PackedInt32Array:
		var seen: Dictionary[int, bool] = {}
		for cell: Vector2i in _cells_for(area):
			for index: int in _cells.get(cell, []):
				seen[index] = true
		return PackedInt32Array(seen.keys())


	## Lists the grid cells covered by one rectangle.
	func _cells_for(area: Rect2) -> Array[Vector2i]:
		var first := Vector2i(
			floori(area.position.x / CELL_SIZE_M),
			floori(area.position.y / CELL_SIZE_M),
		)
		var last := Vector2i(floori(area.end.x / CELL_SIZE_M), floori(area.end.y / CELL_SIZE_M))
		var cells: Array[Vector2i] = []
		for x: int in range(first.x, last.x + 1):
			for y: int in range(first.y, last.y + 1):
				cells.append(Vector2i(x, y))
		return cells


	## Returns the axis-aligned bounds of a polygon.
	static func polygon_bounds(polygon: PackedVector2Array) -> Rect2:
		var bounds := Rect2(polygon[0], Vector2.ZERO)
		for point: Vector2 in polygon:
			bounds = bounds.expand(point)
		return bounds
