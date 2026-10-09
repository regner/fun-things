extends SceneTree
## Isolated long-run traffic measurement through the saved topology and public simulation API.

const NETWORK_SCENE: String = "res://tests/fixtures/s09/network.tscn"
const DEFAULT_TICKS: int = 36_000

var _failures: Array[String] = []
var _checks: Array[String] = []


## Defers measurement until saved script classes and the scene root are available.
func _initialize() -> void:
	_run.call_deferred()


## Validates authored routes, runs one bounded seed, and writes machine-readable evidence.
func _run() -> void:
	var options: Dictionary = _options()
	if options.is_empty():
		quit(2)
		return
	var topology: S09Topology = load(NETWORK_SCENE).instantiate()
	root.add_child(topology)
	_expect(topology.validate_content() == "OK", "saved topology admitted")
	_expect(topology.route_points(&"s09/horizontal").size() >= 300,
		"horizontal loop has dense samples")
	_expect(topology.route_points(&"s09/vertical").size() >= 300,
		"vertical loop has dense samples")
	_expect(topology.replacement_route(&"s09/horizontal") == &"s09/horizontal_detour",
		"player obstacle has an authored alternate")
	_expect(topology.replacement_route(&"s09/vertical") == &"s09/vertical_detour",
		"wreck has an authored alternate")
	var denied: S09TrafficSimulation = S09TrafficSimulation.new()
	_expect(denied.configure(null) == "CONTENT_INVALID", "missing topology refused")
	var simulation: S09TrafficSimulation = S09TrafficSimulation.new()
	_expect(simulation.configure(topology) == "OK", "host simulation admitted")
	var result: Dictionary = simulation.run(options.population, options.seed, options.ticks)
	_expect(result.code == "OK", "traffic case completed")
	if result.code == "OK":
		_expect(result.simulated_seconds == float(options.ticks) / 60.0,
			"declared simulation duration completed")
		_expect(result.drive_rule_steps == result.expected_drive_rule_steps,
			"every car uses the shared drive rule every tick")
		_expect(result.deadlocks == 0, "no four-second complete-population gridlock")
		if options.ticks >= 3600:
			_expect(result.stuck_recovery_seconds.count > 0,
				"scripted blockage produced measured recovery")
	result.failures = _failures
	result.checks = _checks
	result.engine = Engine.get_version_info()
	var file: FileAccess = FileAccess.open(options.output, FileAccess.WRITE)
	if file == null:
		_failures.append("measurement output opened")
	else:
		file.store_string(JSON.stringify(result, "\t") + "\n")
		file.close()
	print("S09_RESULT ", JSON.stringify({ "failures": _failures, "checks": _checks }))
	topology.queue_free()
	await process_frame
	quit(0 if _failures.is_empty() else 1)


## Parses one population/seed/tick/output tuple with strict finite bounds.
func _options() -> Dictionary:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.size() != 4:
		push_error("Expected: population seed ticks output")
		return {}
	var population: int = int(arguments[0])
	var seed: int = int(arguments[1])
	var ticks: int = int(arguments[2])
	var output: String = arguments[3]
	if population not in [24, 32] or seed <= 0 or ticks <= 0 or ticks > DEFAULT_TICKS:
		push_error("Invalid bounded S09 options")
		return {}
	if output.is_empty():
		push_error("Output path is required")
		return {}

	return { "population": population, "seed": seed, "ticks": ticks, "output": output }


## Records independent contract expectations without hiding later measurements.
func _expect(condition: bool, label: String) -> void:
	_checks.append(label)
	if not condition:
		_failures.append(label)
