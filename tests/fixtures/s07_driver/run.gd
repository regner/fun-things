extends SceneTree
## Paced simulation-only saved-fixture reload driver; never restores poses by direct assignment.

const FIXTURE: String = "res://tests/fixtures/s07_driver/intersection.tscn"
const CASES: Array[String] = ["foot", "east_to_north", "west_to_south"]
const MAX_DURATION_SECONDS: float = 600.0
const MIN_TRAVERSALS_PER_ROUTE: int = 2

var failures: Array[String] = []
var traversals: int = 0
var counts: Dictionary = { "foot": 0, "east_to_north": 0, "west_to_south": 0 }
var stream: FileAccess
var measurement_start_usec: int = 0
var duration_seconds: float = 0.0
var simulation_seconds: float = 0.0
var loading_usec: int = 0
var teardown_usec: int = 0


## Defers loading until the SceneTree can admit the saved hierarchy.
func _initialize() -> void:
	_run.call_deferred()


## Runs complete sequential routes over the requested real interval with fail-closed teardown.
func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 1 or not args[0].is_valid_float():
		quit(2)
		return

	duration_seconds = args[0].to_float()
	if not is_finite(duration_seconds) or duration_seconds < 0.0:
		quit(2)
		return
	if duration_seconds > MAX_DURATION_SECONDS:
		quit(2)
		return

	stream = FileAccess.open("res://traversals.jsonl", FileAccess.WRITE)
	if stream == null:
		quit(2)
		return

	measurement_start_usec = Time.get_ticks_usec()
	while failures.is_empty() and _more_work():
		await _traverse(CASES[traversals % CASES.size()])  # gdstyle:ignore=quality/await-in-loop

	stream.close()
	var result: Dictionary = {
		"failures": failures, "counts": counts, "traversals": traversals,
		"requested_wall_seconds": duration_seconds, "elapsed_wall_seconds": _elapsed_seconds(),
		"traversal_simulation_seconds": simulation_seconds,
		"loading_seconds": loading_usec / 1000000.0,
		"teardown_seconds": teardown_usec / 1000000.0,
		"engine": Engine.get_version_info(), "headless": DisplayServer.get_name() == "headless",
		"scope": "simulation only; reload/loading/lifetime are not normal traversal cost"}
	var file: FileAccess = FileAccess.open("res://result.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()
	print("S07_DRIVER_RESULT ", JSON.stringify(result))
	quit(0 if failures.is_empty() else 1)


## Continues until both the actual wall interval and independent repetition minimum are met.
func _more_work() -> bool:
	for case_name: String in CASES:
		if counts[case_name] < MIN_TRAVERSALS_PER_ROUTE:
			return true

	return _elapsed_seconds() < duration_seconds


## Loads saved state, validates admission, records a real route and retires the owned fixture.
func _traverse(case_name: String) -> void:  # gdstyle:ignore=quality/max-local-variables
	var load_start: int = Time.get_ticks_usec()
	var packed: PackedScene = load(FIXTURE)
	if packed == null:
		failures.append("saved fixture unavailable")
		return

	var fixture: S07DriverFixture = packed.instantiate() as S07DriverFixture
	fixture.authoritative = true
	root.add_child(fixture)
	await process_frame
	var loaded: int = Time.get_ticks_usec()
	loading_usec += loaded - load_start
	var start: Dictionary = _state_json(fixture.body_state(case_name))
	var city: S06City = fixture.get_node("City")
	var signature: String = city.signature()
	var route: Dictionary = _route(city, case_name)
	var outcome: Dictionary = await _run_route(fixture, case_name)
	var code: String = outcome.code
	var rows: Array = outcome.rows
	var timed_out: bool = outcome.timed_out
	var end: Dictionary = _state_json(fixture.body_state(case_name))
	var stopped: bool = _record_route_outcome(case_name, fixture, rows, timed_out, end)
	var traversal_end: int = Time.get_ticks_usec()
	fixture.cancel_owned()
	var disconnected: bool = not fixture.controller.enabled and fixture.active_body == null
	fixture.queue_free()
	await process_frame
	var retired: int = Time.get_ticks_usec()
	var freed: bool = not is_instance_valid(fixture)
	teardown_usec += retired - traversal_end
	if not freed or not disconnected:
		failures.append("fixture lifetime/commands not retired")

	counts[case_name] += 1
	traversals += 1
	var receipt: Dictionary = {
		"case": case_name, "ordinal": traversals, "route_ordinal": counts[case_name],
		"start": start, "end": end, "samples": rows, "timed_out": timed_out,
		"admission": code, "stopped_before_notification": stopped, "freed": freed,
		"commands_cancelled": disconnected, "signature": signature,
		"route": _points_json(route.get("world_points_m", PackedVector3Array())),
		"load_start_seconds": (load_start - measurement_start_usec) / 1000000.0,
		"traversal_start_seconds": (loaded - measurement_start_usec) / 1000000.0,
		"traversal_end_seconds": (traversal_end - measurement_start_usec) / 1000000.0,
		"retired_seconds": (retired - measurement_start_usec) / 1000000.0}
	stream.store_line(JSON.stringify(receipt))
	stream.flush()


## Starts one admitted route and waits for its completion signal.
func _run_route(fixture: S07DriverFixture, case_name: String) -> Dictionary:
	var code: String = fixture.begin_route(case_name)
	var rows: Array = []
	var timed_out: bool = true
	if code == "OK":
		var finished: Array = await fixture.route_finished
		rows = finished[1]
		timed_out = finished[2]
	else:
		failures.append(case_name + " admission: " + code)

	return { "code": code, "rows": rows, "timed_out": timed_out }


## Records route completion, destination, simulation duration, and contact expectations.
func _record_route_outcome(
	case_name: String,
	fixture: S07DriverFixture,
	rows: Array,
	timed_out: bool,
	end: Dictionary,
) -> bool:
	var stopped: bool = fixture.passive_valid() and end.velocity == [0.0, 0.0, 0.0]
	if timed_out or rows.is_empty() or not stopped:
		failures.append(case_name + " timeout/empty/uncancelled route")
	if not _destination_valid(case_name, fixture.body_state(case_name)):
		failures.append(case_name + " destination/exit direction")
	for row: Dictionary in rows:
		simulation_seconds += float(row.delta)
		if not row.contacts.is_empty():
			failures.append(case_name + " solid contact")
			break

	return stopped


## Queries canonical routes without constructing an independent path or placement writer.
func _route(city: S06City, case_name: String) -> Dictionary:
	if case_name == "foot":
		return city.route("FOOT", &"s06/foot/west", &"s06/foot/east")
	if case_name == "east_to_north":
		return city.route("TRAFFIC", &"s06/lane/west", &"s06/lane/north")

	return city.route("TRAFFIC", &"s06/lane/east", &"s06/lane/south")


## Enforces literal destinations and exit headings independently of the controller formula.
func _destination_valid(case_name: String, state: Dictionary) -> bool:
	var target: Vector3 = Vector3(20, 0.001, 6.5)
	var yaw: float = -PI / 2.0
	if case_name == "east_to_north":
		target = Vector3(2.25, 0, -20)
		yaw = 0.0
	elif case_name == "west_to_south":
		target = Vector3(-2.25, 0, 20)
		yaw = PI

	return (state.position.distance_to(target) <= 0.5
		and absf(wrapf(state.yaw - yaw, -PI, PI)) <= deg_to_rad(10))


## Serializes public physical state with neutral velocity retained as an explicit assertion input.
func _state_json(state: Dictionary) -> Dictionary:
	return {"position": [state.position.x, state.position.y, state.position.z],
		"yaw": state.yaw, "velocity": [state.velocity.x, state.velocity.y, state.velocity.z]}


## Serializes canonical route points for independent continuity and legal-lane checks.
func _points_json(points: PackedVector3Array) -> Array[Array]:
	var result: Array[Array] = []
	for point: Vector3 in points:
		result.append([point.x, point.y, point.z])

	return result


## Reads actual monotonic wall duration, separately from physics delta and lifecycle phases.
func _elapsed_seconds() -> float:
	return (Time.get_ticks_usec() - measurement_start_usec) / 1000000.0
