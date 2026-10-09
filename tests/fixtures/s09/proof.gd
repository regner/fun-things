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
	_configuration_regression()
	_overlap_regressions()
	_gridlock_regression()
	var simulation: S09TrafficSimulation = S09TrafficSimulation.new()
	_expect(simulation.configure(topology) == "OK", "host simulation admitted")
	var result: Dictionary = simulation.run(options.population, options.seed, options.ticks)
	_expect(result.code == "OK", "traffic case completed")
	if result.code == "OK":
		_expect(result.simulated_seconds == float(options.ticks) / 60.0,
			"declared simulation duration completed")
		_expect(result.drive_rule_steps == result.expected_drive_rule_steps,
			"every car uses the shared drive rule every tick")
		_expect(result.intersection_gridlock.episodes == 0 and
			result.intersection_gridlock.unresolved == 0,
			"no intersection-local gridlock episode")
		_expect(result.ai_collisions == 0, "no provisional S04 footprint overlap")
		if options.ticks >= 3600:
			_expect(result.stuck_recovery_seconds.count == 6,
				"all six blocked cars clear and resume sustained progress")
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


## Proves failed non-null configuration clears admission and leaves run unavailable.
func _configuration_regression() -> void:
	var denied: S09TrafficSimulation = S09TrafficSimulation.new()
	_expect(denied.configure(null) == "CONTENT_INVALID", "missing topology refused")
	var malformed: S09Topology = load(NETWORK_SCENE).instantiate()
	root.add_child(malformed)
	var lane: S09Lane = malformed.get_node("Horizontal")
	lane.world_id = &""
	_expect(denied.configure(malformed) == "CONTENT_INVALID", "malformed topology refused")
	_expect(denied.run(24, 11, 1).code == "INVALID_ARGUMENT",
		"failed configuration leaves simulation unavailable")
	malformed.queue_free()


## Proves oriented envelopes catch overlaps the retired 1.7 metre center test missed.
func _overlap_regressions() -> void:
	_expect(S09TrafficSimulation.footprints_overlap(Vector3.ZERO, 0.0,
		Vector3(0, 0, 2.0), 0.0), "parallel long-envelope overlap detected")
	_expect(S09TrafficSimulation.footprints_overlap(Vector3.ZERO, 0.0,
		Vector3(1.5, 0, 1.5), PI / 2.0), "perpendicular envelope overlap detected")
	_expect(not S09TrafficSimulation.footprints_overlap(Vector3.ZERO, 0.0,
		Vector3(0, 0, 4.0), 0.0), "separated envelopes remain clear")


## Proves moving outer traffic cannot hide a stopped local episode and its resolution.
func _gridlock_regression() -> void:
	var tracker: S09GridlockTracker = S09GridlockTracker.new()
	tracker.configure(Vector3.ZERO)
	var local: Dictionary = { "id": 1, "family": "horizontal", "position": Vector3.ZERO }
	var outer: Dictionary = { "id": 2, "family": "outer", "position": Vector3.ZERO }
	var cars: Array[Dictionary] = [local, outer]
	for tick: int in S09GridlockTracker.PROGRESS_WINDOW_TICKS + 1:
		outer.position.x = float(tick)
		tracker.advance(cars)
	var blocked: Dictionary = tracker.receipt()
	_expect(blocked.episodes == 1 and blocked.unresolved == 1,
		"outer motion cannot mask local gridlock")
	local.position.x = 1.0
	tracker.advance(cars)
	var resumed: Dictionary = tracker.receipt()
	_expect(resumed.resolved == 1 and resumed.unresolved == 0,
		"local progress resolves gridlock episode")


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
