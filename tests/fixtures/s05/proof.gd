class_name S05Proof
extends Node
## Bounded public-API and separate-process fixture checks with independent outcomes.

const DEADLINE_MS: int = 12_000
const POLL_S: float = 0.01
const RATE_RECOVERY_S: float = 0.27
const CHAIN_ALLOWANCE_TICKS: int = 180
const API_SESSION: String = "0123456789abcdef0123456789abcdef"

var session: S03Session
var state: S05Match
var wire: S05Replication
var role: String = ""
var port: int = 0
var baseline_count: int = 0
var deadline: int = 0
var outcome: String = ""
var finished_peers: Dictionary = {}
var terminal_receipts: int = 0
var hydrated: Dictionary = {}
var failures: Array[String] = []


## Injects existing Session/Match/Replication collaborators before any operation starts.
func _ready() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			port = int(argument.trim_prefix("--port="))

	session = $Session as S03Session
	state = $View/Match as S05Match
	wire = $View/Match/Replication as S05Replication
	session.match_state = state
	session.replication = wire
	wire.match_state = state
	wire.resolve_participant = session.participant_for_peer
	wire.handoff_confirmed.connect(session.confirm_handoff)
	wire.admission_received.connect(session.receive_admission)
	wire.baseline_installed.connect(_baseline)
	wire.fire_result.connect(_fire_result)
	state.damage.changed.connect(wire.publish_cars)
	state.damage.changed.connect(_terminal)
	state.damage.exploded.connect(wire.publish_blast)
	state.damage.exploded.connect(_duplicate_blast)
	deadline = Time.get_ticks_msec() + DEADLINE_MS
	_check(not ClassDB.class_exists("Steam") and not Engine.has_singleton("Steam"),
		"isolated Steam-free runtime")
	if state.damage.bodies.size() == 12:
		$View/Match/Cars.visible = false

	if role == "api":
		await _api()
	elif role == "queue":
		await _queue_pressure()
	else:
		session.select_provider(S03Transport.new(get_tree()))
		if role == "host":
			await _host()
		elif role in ["client", "late"]:
			await _client()
		else:
			_check(false, "missing role")


## Proves host API authority, retirement, physics queries and current-state fences.
func _api() -> void:
	state.authoritative = true
	state.session_id = API_SESSION
	state.prepare_initial(1)
	state.admit(1)
	await get_tree().physics_frame
	_check(_car_contact(), "live collider query")
	var shot: Dictionary = _shot(1)
	var invalid: Dictionary = shot.duplicate()
	invalid.generation = 2
	_check(state.damage.resolve_shot(invalid, 1001) == "STALE_SHOOTER", "generation fence")
	invalid = shot.duplicate()
	invalid.session = "ffffffffffffffffffffffffffffffff"
	_check(state.damage.resolve_shot(invalid, 1001) == "STALE_CONTEXT", "session fence")
	invalid = shot.duplicate()
	invalid.match = 2
	_check(state.damage.resolve_shot(invalid, 1001) == "STALE_CONTEXT", "match fence")
	invalid = shot.duplicate()
	invalid.sequence = 0
	_check(state.damage.resolve_shot(invalid, 1001) == "INVALID", "sequence shape")
	state.damage.bodies[0].velocity = Vector3(3, 0, 0)
	_check(state.damage.resolve_shot(shot, 1001) == "OK", "root accepted")
	_check(state.damage.resolve_shot(shot, 1001) == "DUPLICATE", "active duplicate")
	while not _settled():
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_outcomes()
	_check(state.damage.tick <= 90, "finite completion deadline")
	_check(state.damage.jobs.is_empty(), "active target caches retired")
	_check(state.damage.resolve_shot(shot, 1001) == "DUPLICATE", "retired ShotId rejected")
	await get_tree().physics_frame
	_check(_car_contact(), "wreck collider retained")
	_negative_cuts()
	await _root_bound()
	_shooter_retirement()
	var metrics: Dictionary = _metrics()
	while state.damage.tick <= 302:
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(not _car_contact(), "expired wreck collider removed")
	_emit("api", metrics)
	state.clear()
	_check(state.damage.jobs.is_empty() and state.damage.shooters.is_empty() \
		and state.effects.slots.is_empty(), "session teardown histories cleared")
	await get_tree().process_frame
	_result()


## Fills every reserved car job before due work without using cosmetic capacity.
func _queue_pressure() -> void:
	state.authoritative = true
	state.session_id = API_SESSION
	state.prepare_initial(1)
	state.admit(1)
	_check(state.damage.bodies.size() == 12, "queue row requires12 saved cars")
	for batch: int in 3:
		if batch > 0:
			var previous_tick: int = state.damage.tick
			while state.damage.tick == previous_tick:
				await _poll()  # gdstyle:ignore=quality/await-in-loop

		for offset: int in 4:
			var sequence: int = batch * 4 + offset + 1
			_check(state.damage.resolve_shot(_shot(sequence), 1000 + sequence) == "OK",
				"reserved root work accepted")

	_check(state.damage.jobs.size() == 12 and state.damage.queue_peak == 12,
		"all twelve reserved jobs pending before due processing")
	while not _settled():
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_outcomes()
	_check(state.damage.tick <= 90 and state.damage.jobs.is_empty(), "all reserved work completed")
	_emit("queue", _metrics())
	state.clear()
	await get_tree().process_frame
	_result()


## Proves shooter retirement cannot reopen identity or exceed lifetime slot accounting.
func _shooter_retirement() -> void:
	state.damage.retire_shooter(1)
	_check(not state.damage.register_shooter(1, 1), "departed shooter cannot reuse identity")
	_check(state.damage.shooters[1].sequence == 5, "retired shooter floor retained")
	_check(state.damage.register_shooter(2, 1) and state.damage.register_shooter(3, 1) \
		and state.damage.register_shooter(4, 1), "four lifetime shooter slots")
	_check(not state.damage.register_shooter(5, 1), "lifetime registration bound")


## Checks current-state hydration and atomic rejection through the owner API.
func _negative_cuts() -> void:
	var current: Dictionary = state.damage.cut()
	state.damage.authoritative = false
	_check(state.damage.resolve_shot(_shot(1), 1001) == "NOT_AUTHORITY", "passive damage")
	var before: Dictionary = state.damage.cut()
	var invalid: Dictionary = current.duplicate(true)
	invalid.rows[0].generation = 2
	_check(not state.damage.apply_cut(invalid, true), "old generation cut rejected")
	_check(state.damage.cut() == before, "malformed cut atomic")
	invalid = current.duplicate(true)
	invalid.session = "ffffffffffffffffffffffffffffffff"
	_check(not state.damage.apply_cut(invalid, true), "old session cut rejected")
	invalid = current.duplicate(true)
	invalid.match = 2
	_check(not state.damage.apply_cut(invalid, true), "old match cut rejected")
	_check(not state.damage.apply_cut(current), "duplicate current cut rejected")
	_check(state.damage.apply_cut(current, true), "current wreck hydrate")
	for body: S05Car in state.damage.bodies:
		_check(not body.simulation_enabled and body.collision_layer == 0 \
			and body.collision_mask == 0, "hydrated bodies passive")

	_check(state.damage.jobs.is_empty(), "hydrate creates no chain work")
	state.damage.authoritative = true
	for index: int in state.damage.bodies.size():
		state.damage.bodies[index].apply_life(true, state.damage.rows[index].phase)

	var event: Dictionary = {"session": API_SESSION, "match": 1, "sequence": 999,
		"required": state.damage.revision + 1, "tick": state.damage.tick, "car": 1001}
	_check(not state.effects.consume(event, state.damage.revision, state.damage.tick),
		"future dependency event dropped without history")
	_check(state.effects.watermark < 999, "future event cannot advance history")
	var motion: Dictionary = {"session": API_SESSION, "revision": 1,
		"rows": [{ "entity": 1, "tick": 500, "control": 1, "durable": 1, "sample": 1.0 }]}
	before = state.damage.cut()
	_check(state.apply_movement(motion) and state.damage.cut() == before,
		"marker motion cannot overwrite car durable fields")


## Proves global per-tick admission bound without affecting completed chain outcomes.
func _root_bound() -> void:
	await get_tree().physics_frame
	for sequence: int in [2, 3, 4, 5]:
		_check(state.damage.resolve_shot(_shot(sequence), 1001) == "OK", "root work budget")

	_check(state.damage.resolve_shot(_shot(6), 1001) == "STATE_LIMIT", "root overflow")
	_check(state.damage.root_peak == 4, "root work peak bounded")


## Uses the actual physics query against the unchanged authored collider envelope.
func _car_contact() -> bool:
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	var shape: SphereShape3D = SphereShape3D.new()
	shape.radius = 0.1
	query.shape = shape
	query.transform.origin = state.damage.bodies[0].global_position + Vector3(0, 0.75, 0)
	query.collision_mask = S04DriveRules.CAR_COLLISION_LAYER
	return not state.get_world_3d().direct_space_state.intersect_shape(query, 1).is_empty()


## Starts the host, observes the client-driven chain, and retains current wrecks for join.
func _host() -> void:
	_check(session.host(port) > 0, "host accepted")
	_emit("ready", {})
	while not _settled():
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_outcomes()
	# Measure from the first destroyed root, so slower graphical process startup is not counted.
	var first_root_tick: int = state.damage.tick
	if not state.damage.completed.is_empty():
		first_root_tick = int(state.damage.completed[0].due) - S05Damage.CHAIN_DELAY_TICKS

	_check(state.damage.tick - first_root_tick <= CHAIN_ALLOWANCE_TICKS,
		"paced chain completed within allowance after the first root")
	_emit("settled", _metrics())
	while finished_peers.size() != 2:
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(session.roster.size() == 2, "two admitted actual remote processes")
	_check(state.damage.occupant_deaths == 1, "one authoritative occupant death")
	_emit("network", _metrics())
	session.leave()
	while session.phase != "IDLE":
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(state.damage.jobs.is_empty() and state.damage.shooters.is_empty(), "host teardown")
	_result()


## Exercises duplicate/invalid remote intent or a post-chain historical hydrate.
func _client() -> void:
	wire.hold_ack = true
	_check(session.join(session.provider.parse_endpoint("127.0.0.1", port)) > 0, "join accepted")
	while baseline_count == 0:
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(not state.rig.get_meta("input_enabled"), "hydrate precedes input")
	if role == "client":
		await _expect(_intent(1), "NOT_ADMITTED")
	else:
		_check(_settled(), "late baseline contains completed current wrecks")
		_check(state.effects.accepted == 0 and state.effects.dropped == 0,
			"hydrate suppresses historical explosion presentation")
		_emit("hydrate", { "cut": hydrated, "input_enabled": false, "effects": 0 })

	wire.hold_ack = false
	wire.rpc_id(1, "_applied", session.session_id, wire.last_baseline)
	while session.phase != "ACTIVE" or not state.rig.get_meta("input_enabled"):
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	if role == "client":
		await _remote_fire_cases()
	else:
		_check(state.effects.accepted == 0, "late admission cannot replay historical events")

	_emit("client_state", {"cut": state.damage.cut(), "live": wire.live_received,
		"duplicates": wire.duplicate_live_rejected, "slots": state.effects.peak,
		"accepted": state.effects.accepted, "dropped": state.effects.dropped})
	_done.rpc_id(1, session.session_id)
	while session.phase != "IDLE":
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_check(state.damage.rows.is_empty() and state.effects.slots.is_empty(), "client teardown")
	_result()


## Sends malformed/forged/duplicate cases through the actual admitted RPC boundary.
func _remote_fire_cases() -> void:
	await _expect(_intent(1), "OK")
	await _expect(_intent(1), "DUPLICATE")
	var forged: Dictionary = _intent(2)
	forged.context.entity = 1
	await _expect(forged, "STALE_CONTEXT")
	await _expect({ "bad": true }, "RATE_LIMIT")
	await get_tree().create_timer(RATE_RECOVERY_S).timeout
	await _expect({ "bad": true }, "INVALID")
	await get_tree().create_timer(RATE_RECOVERY_S).timeout
	await _expect({ "padding": "x".repeat(600) }, "INVALID")
	await get_tree().create_timer(RATE_RECOVERY_S).timeout
	await _expect(_intent(999), "WINDOW")
	while not _settled():
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	await get_tree().create_timer(RATE_RECOVERY_S).timeout
	await _expect(_intent(1), "DUPLICATE")
	var count: int = 12 if state.damage.rows.size() == 12 else 2
	_check(wire.live_received == count and wire.duplicate_live_rejected == count,
		"actual duplicate live events consumed once")
	_check(state.effects.accepted == (8 if count == 12 else 2) \
		and state.effects.dropped == (4 if count == 12 else 0), "remote cosmetic capacity")


## Injects a second real live RPC solely from the proof to test remote EventId duplicates.
func _duplicate_blast(event: Dictionary) -> void:
	wire.publish_blast(event)


## Resolves test completion identity from the actual sender without changing gameplay.
@rpc("any_peer", "call_remote", "reliable", 0)
func _done(source_session: String) -> void:
	if role != "host" or source_session != session.session_id:
		return

	var peer: int = multiplayer.get_remote_sender_id()
	if not session.roster.has(peer) or session.roster[peer].phase != "ADMITTED":
		return

	finished_peers[peer] = true


## Captures current baseline while the inherited input gate is still closed.
func _baseline(_id: int) -> void:
	baseline_count += 1
	hydrated = state.damage.cut()
	_check(not state.rig.get_meta("input_enabled"), "baseline input closed")
	for body: S05Car in state.damage.bodies:
		_check(not body.simulation_enabled and body.collision_layer == 0,
			"pre-admission passive car")


## Checks complete terminal component/body state at the moment observers see a transition.
func _terminal(cut: Dictionary) -> void:
	for index: int in cut.rows.size():
		if cut.rows[index].phase == "LIVE":
			continue

		terminal_receipts += 1
		var body: S05Car = state.damage.bodies[index]
		_check(not body.simulation_enabled and body.velocity == Vector3.ZERO,
			"terminal publication follows motion shutdown")
		_check(not cut.rows[index].seat and not cut.rows[index].occupant_alive,
			"terminal publication follows occupant release")


## Tests literal near/far and twelve-car outcomes, not a copy of the radius formula.
func _outcomes() -> void:
	var count: int = 12 if state.damage.rows.size() == 12 else 2
	for index: int in state.damage.rows.size():
		var row: Dictionary = state.damage.rows[index]
		var destroyed: bool = index < count
		_check(row.health == (0 if destroyed else 100), "known health outcome")
		_check(row.phase == ("WRECK" if destroyed else "LIVE"), "known life outcome")
		_check(row.explosions == (1 if destroyed else 0), "exactly one scheduled blast")

	_check(state.damage.damage_outcomes == count and state.damage.occupant_deaths == 1,
		"exactly-once damage and occupant death")
	_check(state.damage.total_visits == (144 if count == 12 else 6), "finite target work")
	_check(state.damage.target_peak <= 4 and state.damage.queue_peak <= 12 \
		and state.damage.cache_peak <= 12, "reserved workload peaks")
	_check(state.effects.accepted == (8 if count == 12 else 2) \
		and state.effects.dropped == (4 if count == 12 else 0), "cosmetics cannot cancel chains")
	var previous: Dictionary = {}
	for job: Dictionary in state.damage.completed:
		_check(job.tick >= job.due, "chain delay respected")
		if not previous.is_empty():
			_check(job.due > previous.due or (job.due == previous.due \
				and job.sequence > previous.sequence), "due/EventId order")

		previous = job


## Reads settled current state independently of host-only job internals.
func _settled() -> bool:
	if state.damage.rows.is_empty():
		return false

	var count: int = 12 if state.damage.rows.size() == 12 else 2
	for index: int in count:
		if state.damage.rows[index].explosions != 1:
			return false

	return true


## Creates host-local committed identity for the public resolver check.
func _shot(sequence: int) -> Dictionary:
	return {"session": state.session_id, "match": 1, "shooter": 1,
		"generation": 1, "sequence": sequence}


## Creates only a sender-owned fire intent for the remote boundary check.
func _intent(sequence: int) -> Dictionary:
	return {"context": state.context(session.local_participant),
		"sequence": sequence, "fire": true}


## Waits for one actual RPC outcome within the fixture deadline.
func _expect(envelope: Variant, expected: String) -> void:
	outcome = ""
	wire.send_fire(envelope)
	while outcome.is_empty():
		await _poll()  # gdstyle:ignore=quality/await-in-loop

	_emit("fire", { "expected": expected, "actual": outcome })
	_check(outcome == expected, "remote outcome " + expected)


## Records result signals without mutating owned state.
func _fire_result(reason: String) -> void:
	outcome = reason


## Retains finite work/queue/order/collision/effect telemetry for independent checks.
func _metrics() -> Dictionary:
	return {"cut": state.damage.cut(), "completed": state.damage.completed.duplicate(true),
		"visits": state.damage.total_visits, "target_peak": state.damage.target_peak,
		"queue_peak": state.damage.queue_peak, "cache_peak": state.damage.cache_peak,
		"root_peak": state.damage.root_peak, "damage": state.damage.damage_outcomes,
		"occupant_deaths": state.damage.occupant_deaths, "effects": state.effects.accepted,
		"effect_drops": state.effects.dropped, "effect_peak": state.effects.peak,
		"active_jobs": state.damage.jobs.size(), "terminal_receipts": terminal_receipts,
		"hidden": not $View/Match/Cars.visible, "car_bytes": wire.max_car_bytes,
		"fire_bytes": wire.max_fire_bytes, "baseline_bytes": wire.baseline_bytes}


## Yields to normal physics/network processing and fails bounded waits explicitly.
func _poll() -> void:
	_check(Time.get_ticks_msec() < deadline, "fixture wall-clock deadline")
	await get_tree().create_timer(POLL_S).timeout


## Retains a concrete independent expectation failure and terminates unsuccessfully.
func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
		_emit("failure", { "message": message })
		get_tree().quit(1)


## Writes structured bounded receipts without claiming draw/input/device evidence.
func _emit(event: String, values: Dictionary) -> void:
	values.event = event
	values.role = role
	print("S05 " + JSON.stringify(values))


## Reports pass only after scoped gameplay and teardown checks finish.
func _result() -> void:
	_emit("result", {"ok": failures.is_empty(), "failures": failures,
		"user": OS.get_user_data_dir()})
	get_tree().quit(0 if failures.is_empty() else 1)
