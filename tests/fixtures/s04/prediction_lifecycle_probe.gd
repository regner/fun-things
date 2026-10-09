extends SceneTree
## Independent bounded-history, replay, moving-exit and disconnect-coast API regression.

const DELTA_SECONDS: float = 1.0 / 60.0
const COAST_STEPS: int = 120
const PREDICTION_STEPS: int = 130

var failures: Array[String] = []


## Defers until the root can own the saved fixture bodies used by move_and_slide.
func _initialize() -> void:
	_run.call_deferred()


## Exercises prediction and host lifecycle outcomes through the production fixture APIs.
func _run() -> void:
	_prediction_replay()
	_exit_and_disconnect()
	print("S04_PREDICTION " + JSON.stringify(
		{ "ok": failures.is_empty(), "failures": failures }
	))
	quit(0 if failures.is_empty() else 1)


## Requires bounded per-tick history and an authoritative rewind with remaining replay.
func _prediction_replay() -> void:
	var fixture: Node = _fixture("Prediction")
	var match_state: S04Match = fixture.get_node("View/Match")
	match_state.session_id = "prediction-regression"
	match_state.authoritative = true
	match_state.prepare_initial(1)
	match_state.prepare_initial(2)
	var baseline: Dictionary = match_state.baseline(2, 1)
	match_state.clear()
	match_state.authoritative = false
	_require(match_state.apply_baseline(baseline), "prediction baseline rejected")
	match_state.admit(2)
	match_state.enable_local()
	var command: Dictionary = S04DriveRules.neutral()
	command.throttle = 1.0
	for tick: int in range(1, PREDICTION_STEPS + 1):
		match_state.queue_local_input(tick, command)
		match_state._physics_process(DELTA_SECONDS)
	_require(match_state.prediction_ticks.size() == S04Match.PREDICTION_HISTORY_LIMIT,
		"prediction history was not bounded")
	_require(match_state.prediction_overflowed, "history overflow did not select snap recovery")
	var pose: Dictionary = baseline.poses[1].duplicate(true)
	pose.tick = 2
	pose.input_tick = 20
	pose.position[2] -= 0.25
	_require(match_state.apply_movement({"session": match_state.session_id,
		"revision": 1, "rows": [pose]}), "authoritative correction rejected")
	match_state._physics_process(DELTA_SECONDS)
	_require(not match_state.last_correction.is_empty(), "correction did not reconcile")
	_require(match_state.prediction_ticks.is_empty(), "overflow correction did not snap history")
	fixture.queue_free()


## Requires host-only moving exit rejection and neutral coasting after driver disconnect.
func _exit_and_disconnect() -> void:
	var fixture: Node = _fixture("Lifecycle")
	var match_state: S04Match = fixture.get_node("View/Match")
	match_state.authoritative = true
	match_state.session_id = "lifecycle-regression"
	match_state.prepare_initial(1)
	match_state.prepare_initial(2)
	match_state.admit(1)
	match_state.admit(2)
	var exiting: S04Kinematic = match_state.body_for_entity[2]
	exiting.velocity = Vector3(0.0, 0.0, -S04Match.EXIT_STOP_SPEED_MPS)
	_require(match_state.request_exit(2) == "EXIT_MOVING", "moving exit was not rejected")
	_require(match_state.seats.has(2) and match_state.bindings[2].admitted,
		"moving exit changed seat state")
	exiting.velocity = Vector3(0.0, 0.0, -(S04Match.EXIT_STOP_SPEED_MPS - 0.01))
	_require(match_state.request_exit(2) == "OK", "stopped exit was rejected")
	_require(not match_state.seats.has(2) and not match_state.bindings[2].admitted,
		"accepted exit retained driver ownership")
	var coasting: S04Kinematic = match_state.body_for_entity[1]
	coasting.velocity = Vector3(0.0, 0.0, -4.0)
	var start: Vector3 = coasting.global_position
	match_state.rollback(1)
	_require(match_state.coasting_bodies.has(1), "disconnect retired car instead of coasting")
	_require(not match_state.bindings.has(1) and not match_state.seats.has(1),
		"disconnect retained driver authority")
	for step: int in COAST_STEPS:
		match_state._physics_process(DELTA_SECONDS)
	_require(coasting.global_position.distance_to(start) > 0.1, "disconnected car did not coast")
	_require(coasting.velocity.length() < S04Match.PARKED_SPEED_MPS,
		"disconnected car did not coast to a stop")
	fixture.queue_free()


## Instantiates saved composition while disabling only its network experiment coordinator.
func _fixture(label: String) -> Node:
	var fixture: Node = load("res://tests/fixtures/s04/boot.tscn").instantiate()
	fixture.name = label
	fixture.set_script(null)
	root.add_child(fixture)
	return fixture


## Retains all independent expectation failures in the final structured result.
func _require(condition: bool, label: String) -> void:
	if not condition:
		failures.append(label)
