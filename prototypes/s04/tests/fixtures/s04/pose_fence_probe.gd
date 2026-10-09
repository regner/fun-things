extends SceneTree
## Isolated API regression for installed-baseline ordering and genuinely fresh admission.

const BASELINE_TICK: int = 100
const FIXED_DELTA_S: float = 1.0 / 60.0

var failures: Array[String] = []


## Defers until the copied project's script classes and root can own the saved fixture.
func _initialize() -> void:
	_run.call_deferred()


## Exercises stale/equal/fresh movement, grant ordering, replacement and teardown.
func _run() -> void:
	var fixture: Node = load("res://tests/fixtures/s04/boot.tscn").instantiate()
	# Keep saved composition; disable only the network experiment driver for this API probe.
	fixture.set_script(null)
	fixture.process_mode = Node.PROCESS_MODE_DISABLED
	var match_state: S04Match = fixture.get_node("View/Match")
	var replication: S04Replication = fixture.get_node("View/Match/Replication")
	match_state.session_id = "pose-fence-regression"
	replication.match_state = match_state
	root.add_child(fixture)
	match_state.prepare_initial(1)
	match_state.prepare_initial(2)
	var baseline: Dictionary = match_state.baseline(2, 1)
	for pose: Dictionary in baseline.poses:
		pose.tick = BASELINE_TICK
		pose.position[0] = 10.0
	_require(match_state.apply_baseline(baseline), "initial baseline")
	replication.last_baseline = 1
	var actor: S04Kinematic = match_state.body_for_entity[2]
	var remote: S04Kinematic = match_state.body_for_entity[1]
	for tick: int in [BASELINE_TICK - 1, BASELINE_TICK]:
		_deliver(replication, baseline.poses[0], tick)
		_deliver(replication, baseline.poses[1], tick)
		match_state._physics_process(FIXED_DELTA_S)
		_require(actor.global_position.x == 10.0 and remote.global_position.x == 10.0,
			"stale/equal pose regressed baseline")
		_require(match_state.pending_poses.is_empty(), "stale/equal pose queued")
		_require(match_state.motion_ticks.is_empty(), "baseline satisfied fresh receipt")

	replication._grant(match_state.session_id, 1, match_state.durable_revision)
	_require(not match_state.rig.get_meta("input_enabled"), "grant enabled without fresh pose")
	_deliver(replication, baseline.poses[1], BASELINE_TICK + 1)
	match_state._physics_process(FIXED_DELTA_S)
	_require(actor.global_position.x == 0.0, "fresh pose not installed")
	_require(match_state.rig.get_meta("input_enabled"), "fresh pose plus grant not enabled")

	_replace_cut(match_state, replication, baseline)
	match_state.rollback(1)
	_require(not match_state.baseline_ticks.has(1), "rollback retained baseline floor")
	match_state.clear()
	_require(match_state.baseline_ticks.is_empty(), "clear retained baseline floors")
	_require(match_state.motion_ticks.is_empty(), "clear retained fresh receipt")
	_require(match_state.pending_poses.is_empty(), "clear retained queued pose")
	print("S04_FENCE " + JSON.stringify({ "ok": failures.is_empty(), "failures": failures }))
	fixture.queue_free()
	quit(0 if failures.is_empty() else 1)


## Replaces the cut/control revision and requires fresh delivery plus a new grant.
func _replace_cut(match_state: S04Match, replication: S04Replication,
	baseline: Dictionary) -> void:
	baseline.baseline = 2
	baseline.rows[1].control = 2
	baseline.poses[1].control = 2
	replication.last_baseline = 2
	for pose: Dictionary in baseline.poses:
		pose.tick = BASELINE_TICK * 2
		pose.position[0] = 20.0
	_require(match_state.apply_baseline(baseline), "replacement baseline")
	var actor: S04Kinematic = match_state.body_for_entity[2]
	_require(match_state.motion_ticks.is_empty(), "replacement retained fresh receipt")
	_require(not match_state.rig.get_meta("input_enabled"), "replacement retained enabled input")
	_deliver(replication, baseline.poses[1], BASELINE_TICK + 1)
	match_state._physics_process(FIXED_DELTA_S)
	_require(actor.global_position.x == 20.0, "replacement floor did not supersede old floor")
	_deliver(replication, baseline.poses[1], BASELINE_TICK * 2 + 1)
	match_state._physics_process(FIXED_DELTA_S)
	_require(actor.global_position.x == 0.0, "replacement fresh pose not installed")
	_require(not match_state.rig.get_meta("input_enabled"), "fresh pose enabled before new grant")
	replication._grant(match_state.session_id, 2, match_state.durable_revision)
	_require(match_state.rig.get_meta("input_enabled"), "new grant plus fresh pose not enabled")


## Calls the existing replication receive API; peer authentication is covered by ENet cases.
func _deliver(replication: S04Replication, source: Dictionary, tick: int) -> void:
	var pose: Dictionary = source.duplicate(true)
	pose.tick = tick
	pose.position[0] = 0.0
	replication._movement({"session": replication.match_state.session_id,
		"revision": 1, "rows": [pose]})


## Keeps failed independent expectations visible in the log and process status.
func _require(condition: bool, label: String) -> void:
	if not condition:
		failures.append(label)
