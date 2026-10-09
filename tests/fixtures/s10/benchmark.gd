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
	var route: Dictionary = city.route("FOOT", &"s06/foot/west", &"s06/foot/east")
	if route.code != "OK":
		fixture.free()
		return {
			"scenario": "flee_storm" if storm else "normal",
			"motion": motion,
			"failures": ["saved S06 foot route was unavailable"],
		}

	var population: S10Population = S10Population.new()
	var result: Dictionary = population.run_case(fixture, _seed, motion, storm)
	result["city_validation"] = city.validate_content()
	result["route_point_count"] = (route.world_points_m as PackedVector3Array).size()
	fixture.free()
	return result


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
