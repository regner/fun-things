extends SceneTree
## Independent real-grant/real-producer regression using the saved boot composition.

const BASELINE_TICK: int = 1000
const DELTA_SECONDS: float = 1.0 / 60.0

var failures: Array[String] = []


## Defers saved fixture binding until the tree can own its descendants.
func _initialize() -> void:
	_run.call_deferred()


## Tests both grant/movement orders and closed-gate stale/control delivery.
func _run() -> void:
	var fixture: S04Proof = load("res://tests/fixtures/s04/boot.tscn").instantiate()
	fixture.set_script(load("res://tests/fixtures/s04/producer_proof.gd"))
	fixture.process_mode = Node.PROCESS_MODE_DISABLED
	var replication: S04Replication = fixture.get_node("View/Match/Replication")
	replication.set_script(load("res://tests/fixtures/s04/producer_replication.gd"))
	root.add_child(fixture)
	var actual: S04Match = fixture.match_state
	actual.session_id = "producer-regression"
	actual.prepare_initial(1)
	actual.prepare_initial(2)
	actual.bindings[2].control = 2
	var cut: Dictionary = actual.baseline(2, 1)
	for pose: Dictionary in cut.poses:
		pose.tick = BASELINE_TICK
	_require(actual.apply_baseline(cut), "control2 baseline")
	fixture.session.match_state = actual
	fixture.session.local_participant = 2
	fixture.session.phase = "SYNCHRONIZING"
	replication.match_state = actual
	replication.last_baseline = 1
	replication.admission_received.connect(fixture.session.receive_admission)
	fixture.role = "client"
	fixture.started_ms = 1
	fixture.local_tick = 1091
	fixture.sequence = 17
	fixture.control = 1
	replication._grant(actual.session_id, 1, actual.durable_revision)
	_expect_closed(fixture, replication, "grant before fresh pose")
	for kind: int in 3:
		var pose: Dictionary = cut.poses[1].duplicate(true)
		pose.tick = BASELINE_TICK - 1 if kind == 0 else BASELINE_TICK
		if kind == 2:
			pose.tick = BASELINE_TICK + 1
			pose.control = 1
		_deliver(replication, pose)
		actual._physics_process(DELTA_SECONDS)
		_expect_closed(fixture, replication, "stale/equal/wrong control")
	var fresh: Dictionary = cut.poses[1].duplicate(true)
	fresh.tick = BASELINE_TICK + 1
	_deliver(replication, fresh)
	actual._physics_process(DELTA_SECONDS)
	_expect_open(fixture, replication, 2)
	_movement_before_grant(fixture, replication, cut)
	print("S04_PRODUCER " + JSON.stringify({ "ok": failures.is_empty(), "failures": failures }))
	fixture.queue_free()
	quit(0 if failures.is_empty() else 1)


## Observes two send-eligible callbacks without copying collection or admission rules.
func _expect_closed(fixture: S04Proof, replication: S04Replication, label: String) -> void:
	var sequence: int = fixture.sequence
	var sent: Array = replication.get("sent")
	var count: int = sent.size()
	fixture.input_collector.set_focused(true)
	var key: InputEventKey = InputEventKey.new()
	key.physical_keycode = KEY_W
	key.pressed = true
	fixture.input_collector._unhandled_input(key)
	for step: int in 4:
		fixture._physics_process(DELTA_SECONDS)
	_require(not fixture.match_state.rig.get_meta("input_enabled"), label + " gate opened")
	_require(sent.size() == count and fixture.sequence == sequence, label + " produced intent")
	_require(fixture.input_collector.drive_sample().throttle == 0.0,
		label + " retained closed-gate key")


## Requires new control/sequence and neutral former keys once both dependencies arrive.
func _expect_open(fixture: S04Proof, replication: S04Replication, control: int) -> void:
	var sent: Array = replication.get("sent")
	var count: int = sent.size()
	for step: int in 2:
		fixture._physics_process(DELTA_SECONDS)
	_require(fixture.match_state.rig.get_meta("input_enabled"), "fresh handoff gate stayed closed")
	_require(sent.size() == count + 1, "fresh handoff did not produce exactly one envelope")
	if sent.size() > count:
		_require(sent[count].context.control == control and sent[count].sequence == 1,
			"new control did not reset producer sequence")
		_require(sent[count].move == S04DriveRules.neutral(), "old held keys resumed")


## Requires matching grant even when a newer dependent pose arrives first.
func _movement_before_grant(fixture: S04Proof, replication: S04Replication,
	cut: Dictionary) -> void:
	cut.baseline = 2
	cut.rows[1].control = 3
	cut.poses[1].control = 3
	cut.poses[1].tick = BASELINE_TICK * 2
	replication.last_baseline = 2
	_require(fixture.match_state.apply_baseline(cut), "control3 replacement")
	var fresh: Dictionary = cut.poses[1].duplicate(true)
	fresh.tick += 1
	_deliver(replication, fresh)
	fixture.match_state._physics_process(DELTA_SECONDS)
	_expect_closed(fixture, replication, "fresh pose before matching grant")
	replication._grant(fixture.match_state.session_id, 2, fixture.match_state.durable_revision)
	_expect_open(fixture, replication, 3)


## Calls the actual snapshot receiver; peer authentication is covered by separate ENet runs.
func _deliver(replication: S04Replication, pose: Dictionary) -> void:
	replication._movement({ "session": replication.match_state.session_id,
		"revision": 1, "rows": [pose] })


## Retains independent failures without dropping later ordering cases.
func _require(condition: bool, label: String) -> void:
	if not condition:
		failures.append(label)
