extends SceneTree
## Headless entry point for one seed across normal/storm and both S10 movement options.

const BENCHMARK_SCENE: PackedScene = preload("res://tests/fixtures/s10/benchmark.tscn")
const MOTIONS: Array[String] = ["graph_kinematic", "character_body"]
const SCENARIOS: Array[bool] = [false, true]

var _seed: int = 0
var _output: String = ""


## Defers execution until the staged project and physics space have entered the tree.
func _initialize() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	var parsed: Dictionary = _parse_arguments(arguments)
	if not parsed.valid:
		printerr(parsed.error)
		quit(2)
		return

	_seed = parsed.seed
	_output = parsed.output
	_run.call_deferred()


## Executes four ten-minute simulations and writes a compact seed receipt.
func _run() -> void:
	await process_frame
	var runs: Array[Dictionary] = []
	var failures: Array[String] = []
	var negative_reactions: Dictionary = { 1: { "expected": 64, "observed": 0 } }
	var negative_latencies: Array[int] = []
	var reaction_guard: Array[String] = S10Population.reaction_failures(
		negative_reactions, negative_latencies)
	var negative_graph: Dictionary = {}
	var graph_guard: Array[String] = S10Population.graph_errors(negative_graph)
	if reaction_guard.is_empty() or graph_guard.is_empty():
		failures.append("negative reaction or graph admission guard did not fail closed")
	for storm: bool in SCENARIOS:
		for motion: String in MOTIONS:
			var result: Dictionary = _run_case(storm, motion)
			runs.append(result)
			for failure: String in result.failures:
				failures.append("%s/%s: %s" % [result.scenario, motion, failure])

	var receipt: Dictionary = {
		"seed": _seed,
		"engine": Engine.get_version_info().string,
		"population": S10Population.POPULATION_COUNT,
		"negative_reaction_guard_failures": reaction_guard,
		"negative_graph_guard_failures": graph_guard,
		"runs": runs,
		"failures": failures,
	}
	var file: FileAccess = FileAccess.open(_output, FileAccess.WRITE)
	if file == null:
		printerr("could not write S10 output: " + _output)
		quit(3)
		return

	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	print("S10_RESULT " + JSON.stringify({
		"seed": _seed, "runs": runs.size(), "failures": failures.size() }))
	quit(0 if failures.is_empty() else 1)


## Creates, validates, measures and retires one isolated saved fixture instance.
func _run_case(storm: bool, motion: String) -> Dictionary:
	var fixture: Node3D = BENCHMARK_SCENE.instantiate() as Node3D
	root.add_child(fixture)
	var city: S06City = fixture.get_node("City") as S06City
	var graph: Dictionary = _graph_input(city)
	var graph_admission: Array[String] = S10Population.graph_errors(graph)
	if not graph_admission.is_empty():
		fixture.free()
		return {
			"scenario": "flee_storm" if storm else "normal",
			"motion": motion,
			"failures": graph_admission,
		}

	var population: S10Population = S10Population.new()
	var result: Dictionary = population.run_case(fixture, graph, _seed, motion, storm)
	result["city_validation"] = city.validate_content()
	fixture.free()
	return result


## Builds traversal and independent legality regions solely through current S06 public APIs.
func _graph_input(city: S06City) -> Dictionary:
	var full: Dictionary = city.route("FOOT", &"s06/foot/west", &"s06/foot/east")
	var west: Dictionary = city.route(
		"FOOT", &"s06/foot/west", &"s06/foot/cross_west")
	var crossing: Dictionary = city.route(
		"FOOT", &"s06/foot/cross_west", &"s06/foot/cross_east")
	var east: Dictionary = city.route(
		"FOOT", &"s06/foot/cross_east", &"s06/foot/east")
	var map: Dictionary = city.map_data()
	for result: Dictionary in [full, west, crossing, east, map]:
		if result.code != "OK":
			return {}
	var full_points: PackedVector3Array = full.world_points_m
	var crossing_points: PackedVector3Array = crossing.world_points_m
	return {
		"route_points": full_points,
		"link_ids": full.link_ids,
		"crossing_range": Vector2i(
			_nearest_route_index(full_points, crossing_points[0]),
			_nearest_route_index(full_points, crossing_points[-1])),
		"legal_regions": [
			{ "kind": "SIDEWALK", "points": west.world_points_m },
			{ "kind": "CROSSING", "points": crossing.world_points_m },
			{ "kind": "SIDEWALK", "points": east.world_points_m },
		],
		"roads": map.road_polylines_m,
	}


## Resolves a semantic-region endpoint back to the admitted full-route index.
func _nearest_route_index(points: PackedVector3Array, target: Vector3) -> int:
	var nearest_index: int = 0
	var nearest_distance: float = INF
	for index: int in points.size():
		var distance: float = points[index].distance_squared_to(target)
		if distance < nearest_distance:
			nearest_index = index
			nearest_distance = distance
	return nearest_index


## Parses a required integer seed and absolute external JSON output path.
func _parse_arguments(arguments: PackedStringArray) -> Dictionary:
	var seed: int = -1
	var output: String = ""
	var index: int = 0
	while index < arguments.size():
		if arguments[index] == "--seed" and index + 1 < arguments.size():
			seed = arguments[index + 1].to_int()
			index += 2
		elif arguments[index] == "--output" and index + 1 < arguments.size():
			output = arguments[index + 1]
			index += 2
		else:
			return { "valid": false, "error": "unknown or incomplete argument" }
	if seed < 0 or output.is_empty() or not output.is_absolute_path():
		return { "valid": false, "error": "--seed and absolute --output are required" }

	return { "valid": true, "seed": seed, "output": output }
