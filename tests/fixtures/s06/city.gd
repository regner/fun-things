@tool
class_name S06City
extends Node3D
## Bounded CityData candidate: references saved placement and owns connectivity queries only.

const MAX_ANCHORS: int = 64
const MAX_LINKS: int = 128
const MAX_ROUTE_LINKS: int = 64
const MAX_SAMPLES: int = 4096
const MAX_CONTROLS: int = 16
const MAX_LINK_LENGTH_M: float = 128.0
const BAKE_INTERVAL_M: float = 0.25
const ENDPOINT_TOLERANCE_M: float = 0.001
const TOOL_VERSION: String = "s06-bake-1"

@export var district_id: StringName = &"s06/district"
@export var topology_revision: int = 1
@export var derived: S06Bake


## Fails closed before route/map/controller admission when authored content differs.
func validate_content() -> String:
	var records: Dictionary = _records()
	if not records.valid or derived == null:
		return "CONTENT_INVALID"
	if derived.district_id != district_id or derived.topology_revision != topology_revision:
		return "CONTENT_INVALID"
	if derived.tool_version != TOOL_VERSION or derived.fingerprint != signature():
		return "CONTENT_INVALID"

	return "OK" if _roads_match(records.links) else "CONTENT_INVALID"


## Computes a deterministic signature of relevant saved placement, curves, collision and imports.
func signature() -> String:
	var rows: Array[String] = [str(district_id), str(topology_revision), TOOL_VERSION]
	_signature_rows(self, rows)
	return "\n".join(rows).sha256_text()


## Produces a new editor bake; callers must save it and explicitly assign it before play.
func bake_content() -> S06Bake:
	if not _records().valid:
		return null

	var result: S06Bake = S06Bake.new()
	result.district_id = district_id
	result.topology_revision = topology_revision
	result.tool_version = TOOL_VERSION
	result.fingerprint = signature()
	result.world_xz_bounds_m = _road_bounds()
	for link: S06Link in _records().links:
		if link.kind == "ROAD":
			result.roads.append({ "id": str(link.world_id), "width_m": link.width_m,
				"points": _points(link, false) })

	return result


## Searches directed traffic or undirected foot links with finite visited/path/sample work.
func route(kind: String, from_id: StringName, to_id: StringName) -> Dictionary:
	if validate_content() != "OK":
		return { "code": "CONTENT_INVALID" }
	if kind not in ["FOOT", "TRAFFIC"]:
		return { "code": "NO_ROUTE" }

	var records: Dictionary = _records()
	if not records.anchors.has(from_id) or not records.anchors.has(to_id):
		return { "code": "CONTENT_INVALID" }

	var search: Dictionary = _search(records.links, kind, from_id, to_id)
	if search.code != "OK":
		return search

	return _assemble(search.previous, from_id, to_id, search.visits)


## Visits each reachable anchor once with a bounded directed link scan.
func _search(links: Array[S06Link], kind: String, from_id: StringName,
		to_id: StringName) -> Dictionary:
	var queue: Array[StringName] = [from_id]
	var previous: Dictionary = { from_id: {} }
	var visits: int = 0
	while not queue.is_empty() and visits < MAX_ANCHORS:
		var current: StringName = queue.pop_front()
		visits += 1
		if current == to_id:
			break

		for link: S06Link in links:
			if link.kind != kind:
				continue

			var next: StringName = &""
			var reverse: bool = false
			if link.from_id == current:
				next = link.to_id
			elif kind == "FOOT" and link.to_id == current:
				next = link.from_id
				reverse = true
			if next != &"" and not previous.has(next):
				previous[next] = { "parent": current, "link": link, "reverse": reverse }
				queue.append(next)

	if not previous.has(to_id):
		return { "code": "NO_ROUTE", "visits": visits }

	return { "code": "OK", "previous": previous, "visits": visits }


## Reconstructs the selected authored links within the route sample bound.
func _assemble(previous: Dictionary, from_id: StringName, to_id: StringName,
		visits: int) -> Dictionary:
	var steps: Array[Dictionary] = []
	var cursor: StringName = to_id
	while cursor != from_id and steps.size() < MAX_ROUTE_LINKS:
		var step: Dictionary = previous[cursor]
		steps.push_front(step)
		cursor = step.parent
	if cursor != from_id:
		return { "code": "NO_ROUTE" }

	var points: PackedVector3Array = []
	var ids: Array[StringName] = []
	for step: Dictionary in steps:
		ids.append(step.link.world_id)
		for point: Vector3 in _points(step.link, step.reverse):
			if points.is_empty() or points[-1].distance_to(point) > ENDPOINT_TOLERANCE_M:
				points.append(point)
				if points.size() > MAX_SAMPLES:
					return { "code": "CONTENT_INVALID" }

	return { "code": "OK", "topology_revision": topology_revision, "link_ids": ids,
		"world_points_m": points, "visits": visits }


## Supplies shared derived roads only after current authored-content validation.
func map_data() -> Dictionary:
	if validate_content() != "OK":
		return { "code": "CONTENT_INVALID" }

	return { "code": "OK", "district_id": district_id,
		"topology_revision": topology_revision, "bake_fingerprint": derived.fingerprint,
		"world_xz_bounds_m": derived.world_xz_bounds_m, "road_polylines_m": derived.roads }


## Registers explicit IDs without deriving identity from paths, order or instance IDs.
func _records() -> Dictionary:
	var anchors: Dictionary = {}
	var links: Array[S06Link] = []
	var ids: Dictionary = {}
	var nodes: Array[Node] = [self]
	var valid: bool = topology_revision > 0 and district_id != &""
	while not nodes.is_empty():
		var node: Node = nodes.pop_back()
		nodes.append_array(node.get_children())
		if node is S06Anchor or node is S06Link or node is S06Sector:
			var identity: StringName = node.world_id
			if identity == &"" or str(identity).to_utf8_buffer().size() > 128 or ids.has(identity):
				valid = false
			ids[identity] = true
		if node is S06Anchor:
			anchors[node.world_id] = node
		if node is S06Link:
			links.append(node)

	valid = valid and anchors.size() <= MAX_ANCHORS and links.size() <= MAX_LINKS
	for link: S06Link in links:
		if not _curve_valid(link):
			valid = false
			continue
		if not anchors.has(link.from_id) or not anchors.has(link.to_id):
			valid = false
			continue

		var points: PackedVector3Array = _points(link, false)
		if points.size() > MAX_SAMPLES or points.is_empty():
			valid = false
			continue
		valid = valid and points[0].distance_to(anchors[link.from_id].global_position) <= (
			ENDPOINT_TOLERANCE_M)
		valid = valid and points[-1].distance_to(anchors[link.to_id].global_position) <= (
			ENDPOINT_TOLERANCE_M)
		valid = valid and link.kind in ["FOOT", "TRAFFIC", "ROAD"]
		valid = valid and (link.kind != "ROAD" or (
			is_finite(link.width_m) and link.width_m > 0.0))

	return { "valid": valid, "anchors": anchors, "links": links }


## Samples authored curves in world space; no independent route coordinates are stored.
func _points(link: S06Link, reverse: bool) -> PackedVector3Array:
	var result: PackedVector3Array = []
	for point: Vector3 in link.curve.get_baked_points():
		result.append(link.to_global(point))
	if reverse:
		result.reverse()

	return result


## Serializes relevant scene data and linked import bytes while excluding the derived resource.
func _signature_rows(node: Node, rows: Array[String]) -> void:
	if node is Node3D:
		rows.append(str(get_path_to(node)) + ":" + str(node.transform))
	if node is S06Anchor or node is S06Sector:
		rows.append("anchor:" + str(node.world_id))
	if node is S06Link:
		rows.append("link:%s:%s:%s:%s:%s" % [node.world_id, node.from_id,
			node.to_id, node.kind, node.width_m])
		if node.curve != null:
			rows.append(str(node.curve.bake_interval))
			for index: int in node.curve.point_count:
				rows.append(str(node.curve.get_point_position(index)) + ":" +
					str(node.curve.get_point_in(index)) + ":" +
					str(node.curve.get_point_out(index)))
	if node is CollisionShape3D and node.shape is BoxShape3D:
		rows.append("box:" + str(node.shape.size) + ":" + str(node.disabled))
	if node is CollisionObject3D:
		rows.append("collision:%s:%s" % [node.collision_layer, node.collision_mask])
	if node.scene_file_path.ends_with(".glb"):
		rows.append(node.scene_file_path + ":" + FileAccess.get_sha256(node.scene_file_path))
		rows.append(FileAccess.get_sha256(node.scene_file_path + ".import"))
	for child: Node in node.get_children():
		_signature_rows(child, rows)


## Bounds curve allocation from authored control polygons before engine baking.
func _curve_valid(link: S06Link) -> bool:
	if link.curve == null or link.curve.point_count < 2:
		return false
	if link.curve.point_count > MAX_CONTROLS or link.curve.bake_interval != BAKE_INTERVAL_M:
		return false

	var length: float = 0.0
	for index: int in link.curve.point_count:
		var point: Vector3 = link.curve.get_point_position(index)
		var incoming: Vector3 = link.curve.get_point_in(index)
		var outgoing: Vector3 = link.curve.get_point_out(index)
		if not point.is_finite() or not incoming.is_finite() or not outgoing.is_finite():
			return false
		if not link.to_global(point).is_finite():
			return false
		if index > 0:
			var previous: Vector3 = link.curve.get_point_position(index - 1)
			var previous_out: Vector3 = link.curve.get_point_out(index - 1)
			length += previous_out.length() + incoming.length() + (
				previous + previous_out).distance_to(point + incoming)

	return is_finite(length) and length <= MAX_LINK_LENGTH_M


## Detects missing, duplicated or manually corrupted derived roads as well as stale placement.
func _roads_match(links: Array[S06Link]) -> bool:
	var expected: Dictionary = {}
	for link: S06Link in links:
		if link.kind == "ROAD":
			expected[str(link.world_id)] = link
	if (derived.roads.size() != expected.size()
			or derived.world_xz_bounds_m != _road_bounds()):
		return false

	var seen: Dictionary = {}
	var samples: int = 0
	for road: Dictionary in derived.roads:
		if not road.has_all(["id", "width_m", "points"]) or not expected.has(road.id):
			return false
		if seen.has(road.id) or typeof(road.points) != TYPE_PACKED_VECTOR3_ARRAY:
			return false

		seen[road.id] = true
		var link: S06Link = expected[road.id]
		var points: PackedVector3Array = _points(link, false)
		if road.width_m != link.width_m or road.points != points:
			return false

		samples += points.size()
		if samples > MAX_SAMPLES:
			return false

	return true


## Reads the imported road surface bounds for the canonical map extent, never writing placement.
func _road_bounds() -> Rect2:
	var bounds: Rect2
	var first: bool = true
	var nodes: Array[Node] = [self]
	while not nodes.is_empty():
		var node: Node = nodes.pop_back()
		nodes.append_array(node.get_children())
		if node is MeshInstance3D and str(node.name).begins_with("Road"):
			var box: AABB = node.global_transform * node.get_aabb()
			var rectangle: Rect2 = Rect2(box.position.x, box.position.z, box.size.x, box.size.z)
			bounds = rectangle if first else bounds.merge(rectangle)
			first = false

	return bounds
