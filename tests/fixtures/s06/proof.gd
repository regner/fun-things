extends SceneTree
## Isolated actual-body route proof and saved changed-placement counterexamples.

const FIXTURE: String = "res://tests/fixtures/s06/intersection.tscn"
const CASES: Array[String] = ["foot", "east_to_north", "west_to_south"]

var failures: Array[String] = []
var checks: Array[String] = []
var trajectories: Dictionary = {}


## Defers until the tree can install saved fixture bodies and physics callbacks.
func _initialize() -> void:
	_run.call_deferred()


## Exercises public APIs, saved-data invalidation and actual body routes with finite deadlines.
func _run() -> void:  # gdstyle:ignore=quality/max-local-variables
	var fixture: S06Fixture = load(FIXTURE).instantiate()
	root.add_child(fixture)
	await process_frame
	var city: S06City = fixture.get_node("City")
	_expect(city.validate_content() == "OK", "current content admitted")
	var denied: S06Controller = S06Controller.new()
	_expect(denied.bind_route(city, "FOOT", &"s06/foot/west",
		&"s06/foot/east", false) == "NOT_OWNER", "passive controller refused")
	_expect(city.route("TRAFFIC", &"s06/lane/north",
		&"s06/lane/west").code == "NO_ROUTE", "traffic reverse direction refused")
	var foot: Dictionary = city.route("FOOT", &"s06/foot/west", &"s06/foot/east")
	_expect(foot.code == "OK" and foot.link_ids == [
		&"s06/foot/approach_west", &"s06/foot/crossing",
		&"s06/foot/approach_east"], "explicit crossing connectivity")
	var map: Dictionary = city.map_data()
	var geometry: Array[Dictionary] = []
	_collect_geometry(city, geometry)
	var controller_points: Dictionary = {}
	controller_points.foot = _json_points(foot.world_points_m)
	controller_points.east_to_north = _json_points(city.route("TRAFFIC",
		&"s06/lane/west", &"s06/lane/north").world_points_m)
	controller_points.west_to_south = _json_points(city.route("TRAFFIC",
		&"s06/lane/east", &"s06/lane/south").world_points_m)
	_passive_and_map_checks(fixture, city)
	_saved_counterexamples(fixture, city)
	_expect(city.validate_content() == "OK", "restored content admitted")

	if not "--content-only" in OS.get_cmdline_user_args():
		await _test_routes(fixture)

	var map_json: Array[Dictionary] = []
	for road: Dictionary in map.road_polylines_m:
		map_json.append({ "id": road.id, "width_m": road.width_m,
			"points": _json_points(road.points) })
	var result: Dictionary = { "failures": failures, "checks": checks,
		"trajectories": trajectories, "routes": controller_points, "roads": map_json,
		"geometry": geometry, "signature": city.signature(),
		"engine": Engine.get_version_info(),
		"camera": { "height_m": 47, "fov": 42, "yaw": 0, "viewport": [1280, 800] } }
	var file: FileAccess = FileAccess.open("res://s06-result.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()
	fixture.queue_free()
	await process_frame
	print("S06_RESULT ", JSON.stringify({ "failures": failures, "checks": checks }))
	quit(0 if failures.is_empty() else 1)


## Saves and reloads changed scene state in this isolated copy, proving fail-closed bake admission.
func _saved_counterexamples(fixture: S06Fixture, city: S06City) -> void:
	var original: S06Bake = city.derived
	var sector: Node3D = city.get_node("Sectors/West")
	sector.position.x += 1.0
	_expect(city.validate_content() == "CONTENT_INVALID", "moved sector rejects stale bake")
	_expect(city.map_data().code == "CONTENT_INVALID", "stale minimap refused")
	_expect(fixture.start_route("foot") == "CONTENT_INVALID", "stale controller refused")
	var changed: PackedScene = PackedScene.new()
	_expect(changed.pack(fixture) == OK, "changed placement packed")
	_expect(ResourceSaver.save(changed, "res://s06-changed.tscn") == OK,
		"changed placement saved")
	var reloaded: S06Fixture = load("res://s06-changed.tscn").instantiate()
	root.add_child(reloaded)
	var reloaded_city: S06City = reloaded.get_node("City")
	_expect(reloaded_city.validate_content() == "CONTENT_INVALID",
		"saved reloaded changed placement refuses original signature")
	reloaded.queue_free()
	sector.position.x -= 1.0
	var link: S06Link = city.get_node("Sectors/West/Topology/Crossing")
	var former_id: StringName = link.to_id
	link.to_id = &"s06/foot/west"
	_expect(city.validate_content() == "CONTENT_INVALID", "connectivity change invalidates")
	link.to_id = &"s06/missing"
	_expect(city.validate_content() == "CONTENT_INVALID", "missing endpoint ID rejected")
	link.to_id = former_id
	var anchor: S06Anchor = city.get_node("Sectors/East/Topology/CrossEast")
	var former_anchor_id: StringName = anchor.world_id
	anchor.world_id = &"s06/foot/west"
	_expect(city.validate_content() == "CONTENT_INVALID", "duplicate ID rejected")
	anchor.world_id = former_anchor_id
	city.topology_revision += 1
	_expect(city.validate_content() == "CONTENT_INVALID", "wrong topology revision rejected")
	city.topology_revision -= 1
	_rebake_counterexample(city, original)


## Proves explicit bake refresh follows a coherent authored translation.
func _rebake_counterexample(city: S06City, original: S06Bake) -> void:

	# Coherent authored translation preserves connectors but requires an explicit new bake.
	city.position.x = 1.0
	_expect(city.validate_content() == "CONTENT_INVALID", "coherent placement stale")
	var rebaked: S06Bake = city.bake_content()
	_expect(rebaked != null, "coherent changed placement explicitly rebaked")
	city.derived = rebaked
	_expect(city.validate_content() == "OK", "new signature admits changed placement")
	var route: Dictionary = city.route("FOOT", &"s06/foot/west", &"s06/foot/east")
	_expect(route.world_points_m[0].distance_to(Vector3(-19, 0.001, 6.5)) < 0.001,
		"rebaked route follows actual changed placement")
	var road: Dictionary = city.map_data().road_polylines_m[0]
	_expect(road.points[0].distance_to(Vector3(1, 0, 0)) < 0.001,
		"rebaked minimap follows actual changed placement")
	_expect(ResourceSaver.save(rebaked, "res://s06-rebaked.tres") == OK,
		"explicit changed bake saved")
	city.position.x = 0.0
	city.derived = original


## Records engine-imported geometry for independent footprint/map comparison outside GDScript.
func _collect_geometry(node: Node, rows: Array[Dictionary]) -> void:
	if node is MeshInstance3D:
		var bounds: AABB = node.global_transform * node.get_aabb()
		rows.append({ "name": str(node.name), "minimum": [bounds.position.x,
			bounds.position.y, bounds.position.z], "size": [bounds.size.x,
			bounds.size.y, bounds.size.z], "mesh": node.mesh.resource_path })
	for child: Node in node.get_children():
		_collect_geometry(child, rows)


## Converts engine route values to lossless numeric JSON arrays.
func _json_points(points: PackedVector3Array) -> Array[Array]:
	var result: Array[Array] = []
	for point: Vector3 in points:
		result.append([point.x, point.y, point.z])
	return result


## Retains every independent expectation and failure without suppressing engine diagnostics.
func _expect(condition: bool, label: String) -> void:
	checks.append(label)
	if not condition:
		failures.append(label)


## Runs exactly three finite physics routes; each owner has a hard tick deadline.
func _test_routes(fixture: S06Fixture) -> void:
	for case_name: String in CASES:
		_expect(fixture.start_route(case_name) == "OK", case_name + " route admitted")
		var finished: Array = await fixture.route_finished  # gdstyle:ignore=quality/await-in-loop
		trajectories[case_name] = finished[1]
		_expect(not finished[2], case_name + " bounded route completed")
		var state: Dictionary = fixture.body_state(case_name)
		var target: Vector3 = Vector3(20, 0.001, 6.5)
		var yaw: float = -PI / 2.0
		if case_name == "east_to_north":
			target = Vector3(2.25, 0, -20)
			yaw = 0.0
		elif case_name == "west_to_south":
			target = Vector3(-2.25, 0, 20)
			yaw = PI

		_expect(state.position.distance_to(target) <= 0.5,
			case_name + " independent destination")
		_expect(absf(wrapf(state.yaw - yaw, -PI, PI)) <= deg_to_rad(10),
			case_name + " independent exit direction")
		_expect(state.velocity.length() == 0.0, case_name + " stopped before notification")


## Checks pre-tree passive bodies, actual minimap projection and corrupted bake rejection.
func _passive_and_map_checks(fixture: S06Fixture, city: S06City) -> void:
	var west: S04Kinematic = fixture.get_node("CarWest")
	var east: S04Kinematic = fixture.get_node("CarEast")
	var person: S02ActorMotion = fixture.get_node("Person")
	_expect(not west.simulation_enabled and not east.simulation_enabled and
		west.collision_layer == 0 and east.collision_mask == 0 and
		person.collision_layer == 0, "bodies passive before command admission")
	fixture.authoritative = false
	_expect(fixture.start_route("foot") == "NOT_OWNER", "passive fixture refuses body commands")
	fixture.authoritative = true
	var minimap: S06Minimap = fixture.get_node("Ui/Minimap")
	_expect(minimap.project_point(Vector3(-24, 0, 0)).distance_to(Vector2(8, 80)) < 0.1,
		"actual minimap west endpoint projection")
	_expect(minimap.project_point(Vector3(24, 0, 0)).distance_to(Vector2(152, 80)) < 0.1,
		"actual minimap east endpoint projection")
	_expect(minimap.project_point(Vector3.ZERO).distance_to(Vector2(80, 80)) < 0.1,
		"actual minimap shared seam projection")
	_expect(city.map_data().world_xz_bounds_m == Rect2(-24, -24, 48, 48),
		"canonical minimap bounds match imported road surfaces")
	var original: S06Bake = city.derived
	city.derived = original.duplicate(true)
	var moved: PackedVector3Array = city.derived.roads[0].points
	moved[0].x += 1.0
	city.derived.roads[0].points = moved
	_expect(city.validate_content() == "CONTENT_INVALID", "corrupted derived road refused")
	_expect(minimap.bind_city(city) == "CONTENT_INVALID" and not minimap.content_valid,
		"invalid bake clears minimap drawing")
	city.derived = original
	_expect(minimap.bind_city(city) == "OK", "restored minimap admitted")
