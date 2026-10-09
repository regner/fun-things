extends SceneTree
## Deterministic malformed, flood, deduplication, queue, and revision counterexamples.

var failures: Array[String] = []


## Runs every boundary counterexample without opening a network endpoint.
func _init() -> void:
	_probe_hydration()
	_probe_input()
	_probe_rejected_entry_continuity()
	_probe_actions()
	_probe_client_messages()
	if failures.is_empty():
		print("S04-T BOUNDARY PASS")
		quit(0)
		return

	for failure: String in failures:
		push_error(failure)
	quit(1)


## Proves one exact hydration is admitted and duplicates cannot amplify a response.
func _probe_hydration() -> void:
	var match_state := S04TMatch.new()
	_require(match_state.admit_hydration_request(2, { "protocol": 1 }), "valid hydration")
	_require(not match_state.admit_hydration_request(2, { "protocol": 1 }), "duplicate hydration")
	_require(not match_state.admit_hydration_request(3, { "protocol": 1, "extra": 1 }),
		"hydration exact fields")
	match_state.free()


## Proves malformed controls, sequence windows, capacity, expiry, and revision reset bounds.
func _probe_input() -> void:
	var match_state := _admitted_match()
	var first: Dictionary = _foot_envelope(1, 10)
	_require(match_state.admit_input_envelope(2, first, 1000) == "OK", "valid foot input")
	_require(match_state.input_queue.size() == 3, "three queued foot frames")
	_require(match_state.admit_input_envelope(2, first, 1000) == "OK", "exact redundancy")
	_require(match_state.input_queue.size() == 3, "redundancy did not grow queue")

	var malformed: Dictionary = first.duplicate(true)
	malformed.frames[0]["move"] = Vector2(NAN, 0.0)
	_require(match_state.admit_input_envelope(2, malformed, 1000) == "INVALID",
		"non-finite foot input")
	malformed = first.duplicate(true)
	malformed["extra"] = true
	_require(match_state.admit_input_envelope(2, malformed, 1000) == "INVALID",
		"input exact fields")
	_require(not match_state._serialized_within({ "value": "x".repeat(1300) }, 1200),
		"serialized held limit")

	_require(match_state.admit_input_envelope(2, _foot_envelope(4, 13), 1001) == "OK",
		"second foot batch")
	_require(match_state.admit_input_envelope(2, _foot_envelope(7, 16), 1002) == "INPUT_QUEUE",
		"eight-frame queue capacity")
	_require(match_state.input_queue.size() <= S03InputFrameQueue.DEFAULT_CAPACITY,
		"queue remained bounded")
	_require(match_state.admit_input_envelope(2, _foot_envelope(121, 130), 1003) == "INPUT_QUEUE",
		"sequence-ahead window")

	match_state.host_mode = "car"
	match_state.host_vehicle = "parked"
	match_state.control_revision = 2
	match_state._reset_input_binding()
	_require(match_state.input_queue.size() == 0 and match_state.processed_input_tick == 0,
		"revision reset queue and watermark")
	_require(match_state.admit_input_envelope(2, _car_envelope(1, 50), 1100) == "OK",
		"car sequence restarts at fresh revision")
	var car_bad: Dictionary = _car_envelope(4, 53)
	car_bad.frames[0]["brake"] = 1.1
	_require(match_state.admit_input_envelope(2, car_bad, 1101) == "INVALID",
		"car control range")
	match_state.free()


## Proves rejected speculation preserves numbering in its unchanged control revision.
func _probe_rejected_entry_continuity() -> void:
	var authority := _admitted_match()
	var authority_foot := S03RActor.new()
	authority.add_child(authority_foot)
	authority.foot = authority_foot
	_require(authority.admit_input_envelope(2, _foot_envelope(1, 1), 1000) == "OK",
		"continuity initial foot input")
	for _index: int in range(3):
		authority._consume_authority_input()
	_require(authority.processed_input_sequence == 3, "continuity authority watermark")

	var client := S04TMatch.new()
	client.control_revision = 1
	client.local_input_sequence = 3
	client.input_tick = 4
	client._clear_local_input_redundancy()
	var speculative: Dictionary = client._build_local_input_envelope("parked", {
		"throttle": 0.5, "steer": 0.0, "brake": 0.0, "handbrake": false,
	})
	_require(authority.admit_input_envelope(2, speculative, 1001) == "STALE_CONTEXT",
		"speculative car input rejected without changing revision")

	client.input_tick = 5
	client._clear_local_input_redundancy()
	var resumed: Dictionary = client._build_local_input_envelope("foot", {
		"move": Vector2(0.25, 0.0), "aim_yaw": 0.1,
	})
	_require(resumed.frames[0].sequence == 5, "rejected entry kept monotonic sequence")
	_require(authority.admit_input_envelope(2, resumed, 1002) == "OK",
		"post-rejection foot input admitted")
	authority.free()
	client.free()


## Proves action queue/rate/work/cache/sequence limits and deduplication.
func _probe_actions() -> void:
	var match_state := _admitted_match()
	_require(match_state.admit_action_envelope(2, _action(1), 1000) == "QUEUED",
		"valid action")
	_require(match_state.admit_action_envelope(2, _action(1), 1000) == "DUPLICATE_QUEUED",
		"queued deduplication")
	for sequence: int in range(2, 17):
		_require(match_state.admit_action_envelope(2, _action(sequence), 1000) == "QUEUED",
			"fill action queue %d" % sequence)
	_require(match_state.admit_action_envelope(2, _action(17), 1000) == "QUEUE_FULL",
		"action queue capacity")
	_require(match_state.action_queue.size() == S04TMatch.ACTION_QUEUE_LIMIT,
		"action queue stayed bounded")
	_require(match_state.take_action_batch().size() == S04TMatch.ACTIONS_PER_TICK,
		"per-tick action cap")

	var window_match := _admitted_match()
	_require(window_match.admit_action_envelope(2, _action(65), 1000) == "WINDOW",
		"action sequence-ahead window")
	var rate_match := _admitted_match()
	var admitted_tokens: int = 0
	for _index: int in range(40):
		if rate_match.take_rate_token("action", 1000, 16.0, 32.0):
			admitted_tokens += 1
	_require(admitted_tokens == 32, "action token bucket burst")

	var duplicate_match := _admitted_match()
	duplicate_match.cache_action_result(1, { "sequence": 1 })
	for _index: int in range(32):
		_require(duplicate_match.admit_action_envelope(2, _action(1), 5000) == "CACHED",
			"cached action deduplication")
	_require(duplicate_match.admit_action_envelope(2, _action(1), 5000) == "RATE_LIMIT",
		"duplicate action token bucket")

	for sequence: int in range(1, 81):
		match_state.cache_action_result(sequence, { "sequence": sequence })
	_require(match_state.action_results.size() == S04TMatch.ACTION_RESULT_CACHE,
		"action result cache capacity")
	_require(match_state.action_results.has(80) and not match_state.action_results.has(1),
		"action result retirement floor")
	match_state.free()
	window_match.free()
	rate_match.free()
	duplicate_match.free()


## Proves client-bound snapshots and reliable transitions reject malformed finite data.
func _probe_client_messages() -> void:
	var match_state := S04TMatch.new()
	var snapshot: Dictionary = _snapshot()
	_require(match_state._snapshot_valid(snapshot), "valid snapshot")
	var malformed: Dictionary = snapshot.duplicate(true)
	malformed.foot.position[0] = INF
	_require(not match_state._snapshot_valid(malformed), "snapshot finite coordinates")
	malformed = snapshot.duplicate(true)
	malformed["extra"] = true
	_require(not match_state._snapshot_valid(malformed), "snapshot exact fields")
	var transition: Dictionary = {
		"sequence": 1, "failure": "", "vehicle": "parked", "revision": 1,
		"snapshot": snapshot,
	}
	_require(match_state._transition_message_valid(transition), "valid transition")
	transition["failure"] = "ATTACKER_VALUE"
	_require(not match_state._transition_message_valid(transition), "transition failure enum")
	match_state.free()


## Creates one admitted authority state for direct boundary admission checks.
func _admitted_match() -> S04TMatch:
	var match_state := S04TMatch.new()
	match_state.role = "host"
	match_state.peer_id = 2
	match_state.hydrated_peers[2] = true
	match_state.host_mode = "foot"
	match_state.control_revision = 1
	return match_state


## Builds three sequential varying foot frames with a stable sequence/tick offset.
func _foot_envelope(first_sequence: int, first_tick: int) -> Dictionary:
	var frames: Array[Dictionary] = []
	for index: int in range(3):
		frames.append({
			"sequence": first_sequence + index, "input_tick": first_tick + index,
			"move": Vector2(0.1 + index * 0.1, -0.2), "aim_yaw": float(index) * 0.1,
		})
	return { "mode": "foot", "revision": 1, "frames": frames }


## Builds three sequential varying car frames for the fresh revision.
func _car_envelope(first_sequence: int, first_tick: int) -> Dictionary:
	var frames: Array[Dictionary] = []
	for index: int in range(3):
		frames.append({
			"sequence": first_sequence + index, "input_tick": first_tick + index,
			"throttle": 0.5 + index * 0.1, "steer": -0.1 + index * 0.1,
			"brake": 0.0, "handbrake": false,
		})
	return { "mode": "parked", "revision": 2, "frames": frames }


## Builds one exact sequential ENTER request for queue/flood checks.
func _action(sequence: int) -> Dictionary:
	return {
		"context": { "control": 1 }, "action_sequence": sequence,
		"kind": "enter", "payload": { "vehicle": "parked" },
	}


## Builds one complete finite initial snapshot for client-bound validation.
func _snapshot() -> Dictionary:
	var foot_pose: Dictionary = {
		"position": [0.0, 0.0, 0.0], "yaw": 0.0,
		"velocity": [0.0, 0.0, 0.0], "sequence": 0,
	}
	var car_pose: Dictionary = {
		"position": [1.0, 0.0, 0.0], "yaw": 0.0,
		"velocity": [0.0, 0.0, 0.0], "sequence": 0, "input_tick": 0,
	}
	return {
		"tick": 1, "mode": "foot", "vehicle": "", "seat_claimant": 0,
		"control": 1, "ack": 0, "foot": foot_pose,
		"parked": car_pose, "traffic": car_pose.duplicate(true), "traffic_ai": true,
	}


## Records one failed independent expectation without hiding later counterexamples.
func _require(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
