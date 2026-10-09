class_name S09Topology
extends Node3D
## Saved looping lane network and authored blockage references for the traffic simulation.

const MAX_ROUTES: int = 8
const INTERSECTION_RADIUS_M: float = 8.0


## Fails closed when route IDs, replacement links or authored obstacles are invalid.
func validate_content() -> String:
	var routes: Dictionary = _routes()
	if routes.is_empty() or routes.size() > MAX_ROUTES:
		return "CONTENT_INVALID"
	for route: S09Lane in routes.values():
		if not route.is_valid() or route.sampled_points().size() < 16:
			return "CONTENT_INVALID"
		if route.replacement_for != &"" and not routes.has(route.replacement_for):
			return "CONTENT_INVALID"
	if not routes.has(&"s09/horizontal") or not routes.has(&"s09/vertical"):
		return "CONTENT_INVALID"
	if not has_node("PlayerObstacle") or not has_node("Wreck"):
		return "CONTENT_INVALID"

	return "OK"


## Returns a defensive copy of sampled points for one directed route.
func route_points(route_id: StringName) -> PackedVector3Array:
	if validate_content() != "OK" or not _routes().has(route_id):
		return PackedVector3Array()

	return _routes()[route_id].sampled_points()


## Finds the authored alternate lane around a blocked base route.
func replacement_route(route_id: StringName) -> StringName:
	for lane: S09Lane in _routes().values():
		if lane.replacement_for == route_id:
			return lane.world_id

	return &""


## Supplies authored obstacle positions without giving the controller transform ownership.
func blockages() -> Array[Dictionary]:
	return [
		{ "id": "player_obstacle", "route_id": &"s09/horizontal",
			"position": get_node("PlayerObstacle").global_position, "radius_m": 2.5 },
		{ "id": "wreck", "route_id": &"s09/vertical",
			"position": get_node("Wreck").global_position, "radius_m": 2.5 },
	]


## Returns the authored four-way conflict-zone center.
func intersection_center() -> Vector3:
	return get_node("Intersection").global_position


## Indexes unique saved lane identities without deriving gameplay identity from node paths.
func _routes() -> Dictionary:
	var result: Dictionary = {}
	for child: Node in get_children():
		if child is not S09Lane:
			continue
		if child.world_id == &"" or result.has(child.world_id):
			return {}
		result[child.world_id] = child

	return result
