class_name S03Proof
extends Node

const POLL_S: float = 0.01
const CASE_DEADLINE_MS: int = 8000
const SNAPSHOT_STEP_S: float = 0.12

var session: S03Session
var match_state: S03Match
var replication: S03Replication
var role: String = ""
var port: int = 0
var baseline_count: int = 0
var outcomes: Array[String] = []
var completions: Dictionary = {}
var cases: Array[String] = []
var deadline_ms: int = 0
var snapshots_done: bool = false
var diagnostic_state: String = ""


## Bind the proposed public boundaries and run one side of the real-process proof.
func _ready() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			port = int(argument.trim_prefix("--port="))

	session = $Session as S03Session
	match_state = $View/Match as S03Match
	replication = $View/Match/Replication as S03Replication
	session.match_state = match_state
	session.replication = replication
	replication.match_state = match_state
	replication.resolve_participant = session.participant_for_peer
	replication.handoff_confirmed.connect(session.confirm_handoff)
	replication.admission_received.connect(session.receive_admission)
	replication.baseline_installed.connect(_baseline_installed)
	replication.held_result.connect(_held_result)
	replication.snapshot_requested.connect(_snapshots)
	session.completed.connect(_completed)
	session.changed.connect(_session_changed)
	session.close_started.connect(_close_started)
	_check(not ClassDB.class_exists("Steam"), "Steam native class absent")
	_check(not Engine.has_singleton("Steam"), "Steam singleton absent")
	session.select_provider(S03Transport.new(get_tree()))
	if role == "host":
		await _host()
	elif role == "client":
		await _client()
	else:
		_check(false, "missing role")


## Observe host simulation changes without deciding or rewriting outcomes.
func _physics_process(_delta: float) -> void:
	if role != "host" or match_state == null:
		return

	var rows: Dictionary = {}
	for participant: int in match_state.bindings:
		rows[participant] = match_state.bindings[participant].duplicate()

	var state: Dictionary = {"bindings": rows, "accepted": match_state.accepted_count,
		"rejected": match_state.rejected.duplicate()}
	var signature: String = JSON.stringify(state)
	if signature != diagnostic_state:
		diagnostic_state = signature
		_emit("simulation_observed", state)


## Assert host-owned provisional rollback, admission and simulation outcomes.
func _host() -> void:
	_check(session.host(port) > 0, "host accepted")
	_check(session.phase == "ACTIVE", "host active")
	_check(match_state.rig != null, "host local rig")
	_emit("ready", { "role": role, "user_dir": OS.get_user_data_dir() })
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	while session.disconnected_count < 1:
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(match_state.bindings.size() == 1, "canceled provisional life removed")
	_check(match_state.entities.size() == 1, "canceled entity removed")
	_check(replication.pending.is_empty(), "canceled baseline discarded")
	cases.append("provisional_rollback")
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	while not snapshots_done:
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(match_state.accepted_count == 2, "only valid held frames consumed across resync")
	_check(match_state.rejected.get("NOT_ADMITTED", 0) == 2, "provisional input rejected")
	_check(match_state.rejected.get("WINDOW", 0) == 3, "every retained frame out of window")
	_check(match_state.rejected.get("INVALID", 0) >= 2, "malformed/nonfinite rejected")
	_check(match_state.rejected.get("STALE_CONTEXT", 0) >= 2, "stale/wrong ownership rejected")
	_check(match_state.rejected.get("STALE_SEQUENCE", 0) >= 1, "stale sequence rejected")
	for binding: Dictionary in match_state.bindings.values():
		_check(binding.held == 0.0, "held expiry neutralizes input")

	cases.append("authority_validation_and_expiry")
	session.leave()
	_check(session.phase == "CLOSING", "async close remains closing")
	await _wait_phase("IDLE")
	await get_tree().process_frame
	_check(match_state.entities.is_empty() and match_state.rig == null, "host cleanup")
	_result()


## Exercise substitution, cancel/retry, held-window recovery and split snapshots.
func _client() -> void:
	await _provider_substitution()
	var provider: S03Transport = S03Transport.new(get_tree())
	_check(session.select_provider(provider), "select ENet")
	replication.hold_ack = true
	var first: int = session.join(provider.parse_endpoint("127.0.0.1", port))
	_check(first > 0, "join accepted")
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	while baseline_count == 0:
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(session.phase == "SYNCHRONIZING", "baseline before admission")
	_check(not match_state.rig.get_meta("input_enabled"), "provisional input disabled")
	_check(match_state.bindings[session.local_participant].health == 75, "immutable cut installed")
	_check_rigs()
	await _send_expect({
		"context": match_state.context(session.local_participant), "sequence": 1, "move": 1.0,
	}, "NOT_ADMITTED")
	session.cancel(first)
	_check(session.phase == "CLOSING", "cancel asynchronous")
	_check(session.join(provider.parse_endpoint("127.0.0.1", port)) == 0, "retry waits for idle")
	session.cancel(first)
	await _wait_phase("IDLE")
	await get_tree().process_frame
	_check(match_state.rig == null and match_state.entities.is_empty(), "cancel clears replica")
	_check(completions[first] == ["CANCELED"], "single canceled completion")
	await get_tree().create_timer(0.1).timeout
	replication.hold_ack = false
	_check(
		session.join(provider.parse_endpoint("127.0.0.1", port)) > first,
		"fresh retry operation",
	)
	await _wait_input()
	_check(match_state.bindings.size() == 2, "host and client distinct players")
	_check(match_state.bindings[session.local_participant].health == 70, "journal before admission")
	_check_rigs()
	cases.append("baseline_cancel_retry")
	await _held_case()
	await _snapshot_case()
	await _wait_phase("IDLE")
	_check(session.close_outcome == "HOST_LOST", "host loss cleanup")
	_check(match_state.rig == null and match_state.entities.is_empty(), "client cleanup")
	_result()


## Check independent subset recovery through the native fault schedule.
func _snapshot_case() -> void:
	replication.request_snapshots()
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	while not _snapshot_complete():
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(match_state.bindings[1].sample == 11.0, "lost subset refreshed")
	_check(match_state.bindings[session.local_participant].sample == 22.0, "other subset refreshed")
	_check(match_state.bindings[session.local_participant].health == 70, "motion preserves health")
	_check(
		replication.movement_received == 5,
		"native ordered stream dropped reordered and lost packets",
	)
	var enet: ENetMultiplayerPeer = multiplayer.multiplayer_peer as ENetMultiplayerPeer
	var host_peer: ENetPacketPeer = enet.get_peer(1) if enet != null else null
	_check(host_peer != null and host_peer.get_statistic(
		ENetPacketPeer.PEER_PACKET_THROTTLE_LIMIT) == ENetPacketPeer.PACKET_THROTTLE_SCALE,
		"host bandwidth cannot throttle unreliable held input")
	cases.append("subset_reorder_loss_recovery")


## Prove canceled late native results cannot replace the subsequent attempt.
func _provider_substitution() -> void:
	var fake: S03FakeTransport = S03FakeTransport.new(get_tree())
	_check(session.select_provider(fake), "fake substituted")
	var first: int = session.host(port)
	session.cancel(first)
	await _wait_phase("IDLE")
	var second: int = session.host(port)
	_check(second > first, "new provider operation")
	await _wait_phase("ACTIVE")
	_check(fake.obsolete_peers_closed == 1, "old native result disposed")
	_check(completions[first] == ["CANCELED"] and completions[second] == ["OK"],
		"exactly one completion per accepted operation")
	session.leave()
	await _wait_phase("IDLE")
	await get_tree().process_frame
	cases.append("provider_substitution_late_cleanup")


## Reject invalid intent and recover a fully exhausted held sequence window.
func _held_case() -> void:
	var participant: int = session.local_participant
	var previous: Dictionary = match_state.context(participant)
	await _send_expect({ "context": previous, "sequence": 1, "move": 1.0 }, "OK")
	await _send_expect({ "context": previous, "sequence": 1, "move": 0.0 }, "STALE_SEQUENCE")
	var stolen: Dictionary = previous.duplicate()
	stolen.entity = match_state.bindings[1].entity
	await _send_expect({ "context": stolen, "sequence": 2, "move": 1.0 }, "STALE_CONTEXT")
	await _send_expect({ "context": previous, "sequence": 3, "move": NAN }, "INVALID")
	await _send_expect({ "context": previous, "sequence": 4, "move": "bad" }, "INVALID")
	for sequence: int in [122, 123, 124]:
		# All retained frames exceed the window; there is no accepted fallback frame.
		# gdstyle:ignore=quality/await-in-loop
		await _send_expect(
			{ "context": previous, "sequence": sequence, "move": 1.0 }, "WINDOW"
		)

	await _recover_sequence(previous)
	await _send_expect({ "context": previous, "sequence": 1, "move": 1.0 }, "STALE_CONTEXT")
	await _send_expect({"context": match_state.context(participant), "sequence": 1,
		"move": 0.5}, "OK")
	cases.append("held_window_resync")


## Withhold the current acknowledgement and prove old markers cannot reopen admission.
func _recover_sequence(previous: Dictionary) -> void:
	var participant: int = session.local_participant
	var old_baseline: int = replication.last_baseline
	replication.hold_ack = true
	# Age the completed join deadline without waiting fifteen seconds in this smoke proof.
	session.deadline_ms = Time.get_ticks_msec() - 1
	session.request_resync()
	_check(session.deadline_ms > Time.get_ticks_msec(), "resync gets a fresh deadline")
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	while replication.last_baseline <= old_baseline:
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	replication.rpc_id(1, "_marker_ack", session.session_id, old_baseline, 1)
	await _send_expect({"context": match_state.context(participant), "sequence": 1,
		"move": 0.0}, "NOT_ADMITTED")
	_check(session.phase == "SYNCHRONIZING", "obsolete marker cannot admit")
	_check(not match_state.rig.get_meta("input_enabled"), "resync input disabled")
	replication.hold_ack = false
	replication.rpc_id(1, "_applied", session.session_id, replication.last_baseline)
	await _wait_input()
	_check(match_state.context(participant).entity == previous.entity, "resync retains entity")
	_check(match_state.bindings[participant].health == 70, "resync retains injured health")
	_check(match_state.context(participant).control == previous.control + 1,
		"fresh control revision")


## Wait for the actual remote validator outcome, with a case deadline.
func _send_expect(envelope: Dictionary, expected: String) -> void:
	outcomes.clear()
	_emit("held_send", { "sequence": envelope.get("sequence"), "expected": expected })
	replication.send_held(envelope)
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	while outcomes.is_empty():
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(outcomes[0] == expected, "held outcome: " + expected)
	await get_tree().create_timer(0.03).timeout


## Drive separated native movement packets; the runner proxy reorders and loses them.
func _snapshots(peer_id: int) -> void:
	_emit("snapshots", {})
	await get_tree().create_timer(SNAPSHOT_STEP_S).timeout
	var participant: int = session.participant_for_peer(peer_id)
	replication.send_movement(peer_id, [1], 100, 1.0)
	await get_tree().create_timer(SNAPSHOT_STEP_S).timeout
	replication.send_movement(peer_id, [participant], 101, 2.0)
	await get_tree().create_timer(SNAPSHOT_STEP_S).timeout
	replication.send_movement(peer_id, [1], 102, 3.0)
	await get_tree().create_timer(SNAPSHOT_STEP_S).timeout
	replication.send_movement(peer_id, [participant], 103, 22.0)
	await get_tree().create_timer(SNAPSHOT_STEP_S).timeout
	replication.send_movement(peer_id, [1], 104, 11.0)
	await get_tree().create_timer(SNAPSHOT_STEP_S).timeout
	snapshots_done = true


## Observe complete refreshed state for both independently delivered subsets.
func _snapshot_complete() -> bool:
	if not match_state.bindings.has(session.local_participant):
		return false

	var host_entity: int = int(match_state.bindings[1].entity)
	var local_entity: int = int(match_state.bindings[session.local_participant].entity)
	return match_state.motion_ticks.get(host_entity, 0) == 104 and (
		match_state.motion_ticks.get(local_entity, 0) == 103)


## Count saved rigs and verify replica pre-tree configuration.
func _check_rigs() -> void:
	var rigs: int = 0
	for child: Node in match_state.get_children():
		if child.name == "LocalRig":
			rigs += 1

	_check(rigs == 1, "exactly one local rig per process")
	for actor: S03Entity in match_state.entities.values():
		_check(actor.ready_configured, "configured before ready")
		_check(actor.authoritative == match_state.authoritative, "simulation role")


## Timestamp published session state in this process clock domain.
func _session_changed() -> void:
	_emit("session_changed", { "participant": session.local_participant })


## Record close initiation before peer replacement and match teardown.
func _close_started(outcome: String) -> void:
	_emit("close_started", { "outcome": outcome })


## Count completed baseline applications.
func _baseline_installed(_baseline_id: int) -> void:
	baseline_count += 1
	_emit("baseline_installed", { "baseline": _baseline_id })


## Count terminal operation signals independently of the service's deduplication.
func _completed(source_operation: int, outcome: String) -> void:
	if not completions.has(source_operation):
		completions[source_operation] = []

	completions[source_operation].append(outcome)
	_emit("completed", { "source_operation": source_operation, "outcome": outcome })


## Retain the observed network validation result.
func _held_result(reason: String, _sequence: int) -> void:
	outcomes.append(reason)
	_emit("held_receipt", { "sequence": _sequence, "reason": reason })


## Await a specific lifecycle state within a bounded wall-clock interval.
func _wait_phase(expected: String) -> void:
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	while session.phase != expected:
		await _poll()  # gdstyle:ignore=quality/await-in-loop


## Await both host admission and fresh matching movement before control.
func _wait_input() -> void:
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	while session.phase != "ACTIVE" or match_state.rig == null or (
		not match_state.rig.get_meta("input_enabled", false)):
		await _poll()  # gdstyle:ignore=quality/await-in-loop


## Yield to live network processing; paced polling must not block the engine main loop.
func _poll() -> void:
	_check(Time.get_ticks_msec() < deadline_ms, "case deadline in " + session.phase)
	await get_tree().create_timer(POLL_S).timeout


## Emit a structured failure and a nonzero exit for any contract violation.
func _check(condition: bool, message: String) -> void:
	if condition:
		return

	_emit("result", { "role": role, "ok": false, "failure": message, "cases": cases })
	get_tree().quit(1)


## Print readiness/results for the bounded parent runner.
func _emit(event: String, data: Dictionary) -> void:
	data.event = event
	data.ticks_usec = Time.get_ticks_usec()
	data.clock_domain = "engine_elapsed_usec_pid_" + str(OS.get_process_id())
	data.pid = OS.get_process_id()
	data.role = role
	data.phase = session.phase
	data.operation = session.operation_id
	data.close_outcome = session.close_outcome
	data.session_deadline_ms = session.deadline_ms
	data.case_deadline_ms = deadline_ms
	print("S03 " + JSON.stringify(data))


## Report retained case evidence after cleanup.
func _result() -> void:
	_emit("result", {"role": role, "ok": true, "cases": cases,
		"steam_available": false, "user_dir": OS.get_user_data_dir(),
		"baseline_bytes": replication.baseline_bytes,
		"max_movement_bytes": replication.max_movement_bytes,
		"max_held_bytes": replication.max_held_bytes,
		"movement_received": replication.movement_received})
	get_tree().quit()
