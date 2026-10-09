extends SceneTree
## Verifies bounded replay plus numbered-input freshness, lag and expiry contracts.


## Runs deterministic history and authority-input outcomes, then exits.
func _initialize() -> void:
	var history: S03PredictionHistory = S03PredictionHistory.new(3)
	var command: Dictionary = { "move": Vector2.UP, "aim_yaw": 0.0, "fire": false }
	for tick: int in range(1, 5):
		history.push(tick, command, 1.0 / 60.0)
	var exhausted: Dictionary = history.acknowledge(0)
	assert(exhausted.history_exhausted)
	assert(history.size() == 0)

	history.push(5, command, 1.0 / 60.0)
	history.push(6, command, 1.0 / 60.0)
	var replay: Dictionary = history.acknowledge(5)
	assert(not replay.history_exhausted)
	assert(replay.frames.size() == 1)
	assert(replay.frames[0].tick == 6)
	_verify_frame_map()
	_verify_expiry_with_backlog()
	_verify_submit_freshness()
	print("S03-P HISTORY PASS")
	quit(0)


## Proves loss/stall supersession restores declared lag without extra host steps.
func _verify_frame_map(  # gdstyle:ignore=quality/max-function-length,quality/max-local-variables
) -> void:
	const FRAME_COUNT: int = 120
	const STALL_START: int = 50
	const STALL_END: int = 65
	const DELTA: float = 1.0 / 60.0
	var queue: S03InputFrameQueue = S03InputFrameQueue.new(FRAME_COUNT)
	var client_position: Vector3 = Vector3.ZERO
	var host_position: Vector3 = Vector3.ZERO
	var client_positions: Dictionary = {}
	var recent: Array = []
	var deferred_packets: Array = []
	var consumed_sequence: int = 0
	var consumed_tick: int = 0
	var superseded_count: int = 0

	for tick: int in range(1, FRAME_COUNT + 1):
		var move: Vector2 = _probe_move(tick)
		var frame: Dictionary = {
			"sequence": tick, "input_tick": tick, "move": move, "aim_yaw": 0.0,
		}
		client_position = _advance_position(client_position, frame, DELTA)
		client_positions[tick] = client_position
		recent.append(frame)
		if recent.size() > 3:
			recent.pop_front()

		if tick % 2 == 0 and tick not in [18, 76]:
			var packet: Array = recent.duplicate(true)
			if tick >= STALL_START and tick < STALL_END:
				deferred_packets.append(packet)
			else:
				assert(queue.offer(packet, consumed_sequence, consumed_tick))
		if tick == STALL_END:
			for packet: Array in deferred_packets:
				assert(queue.offer(packet, consumed_sequence, consumed_tick))
			deferred_packets.clear()

		if tick < STALL_START or tick >= STALL_END:
			var consumed: Dictionary = queue.pop_next(consumed_sequence, consumed_tick)
			if not consumed.is_empty():
				host_position = _advance_position(host_position, consumed, DELTA)
				if not host_position.is_equal_approx(client_positions[consumed.input_tick]):
					print("FRAME MAP MISMATCH ", tick, " ", consumed, " ", host_position,
						" ", client_positions[consumed.input_tick])
				assert(host_position.is_equal_approx(client_positions[consumed.input_tick]))
				consumed_sequence = int(consumed.sequence)
				consumed_tick = int(consumed.input_tick)
				superseded_count += int(consumed.superseded_count)
			if tick >= STALL_END:
				assert(tick - consumed_tick <= S03InputFrameQueue.MAX_PENDING_LAG_FRAMES)

	# This is one later normal authority tick, not an extra step in the stall frame.
	var final_frame: Dictionary = queue.pop_next(consumed_sequence, consumed_tick)
	if not final_frame.is_empty():
		host_position = _advance_position(host_position, final_frame, DELTA)
		assert(host_position.is_equal_approx(client_positions[final_frame.input_tick]))
		consumed_tick = int(final_frame.input_tick)
		superseded_count += int(final_frame.superseded_count)
	assert(FRAME_COUNT - consumed_tick <= S03InputFrameQueue.MAX_PENDING_LAG_FRAMES)
	assert(queue.size() <= S03InputFrameQueue.MAX_PENDING_LAG_FRAMES)
	assert(superseded_count > 0)
	print("S03-P FRAME MAP PASS")
	print("S03-P STALL LAG PASS")


## Proves a stopped producer with a large queue is neutral by expiry plus one tick.
func _verify_expiry_with_backlog() -> void:
	var match_state: S03RMatch = S03RMatch.new()
	var queue: S03InputFrameQueue = S03InputFrameQueue.new()
	var frames: Array = []
	for tick: int in range(1, 25):
		frames.append({
			"sequence": tick, "input_tick": tick,
			"move": Vector2.UP, "aim_yaw": 0.0,
		})
		if frames.size() == 3:
			assert(queue.offer(frames, 0, 0))
			frames.clear()
	assert(queue.size() >= 22)
	match_state.input_queues[1] = queue
	match_state.bindings[1] = {
		"sequence": 0, "last_input_tick": 0, "superseded_count": 0, "sample": 1.0,
	}
	var command: Dictionary = match_state.consume_authority_input(
		1, 0.0, S03Match.HELD_EXPIRY_MS + 17
	)
	assert(command.move == Vector2.ZERO)
	assert(queue.size() == 0)
	assert(match_state.bindings[1].sequence == 24)
	assert(match_state.bindings[1].last_input_tick == 24)
	assert(match_state.bindings[1].superseded_count == 24)
	match_state.free()
	print("S03-P EXPIRY PASS")


## Proves cross-packet sequence/tick conflicts cannot mutate held admission state.
func _verify_submit_freshness() -> void:
	var match_state: S03RMatch = S03RMatch.new()
	match_state.authoritative = true
	match_state.session_id = "freshness-probe"
	match_state.bindings[1] = {
		"admitted": true, "entity": 1, "generation": 1, "life": 1, "control": 1,
		"sequence": 50, "last_input_tick": 150, "pending": 50, "receipt_ms": 0,
		"superseded_count": 0, "sample": 0.0,
	}
	match_state.input_queues[1] = S03InputFrameQueue.new()
	var context: Dictionary = match_state.context(1)
	var invalid_pairs: Array[Vector2i] = [
		Vector2i(1, 151), Vector2i(50, 151), Vector2i(51, 271),
	]
	for pair: Vector2i in invalid_pairs:
		var invalid: Dictionary = _frame(pair.x, pair.y)
		assert(match_state.submit_held(1, { "context": context, "frames": [invalid] }) == (
			"INPUT_QUEUE"
		))
	assert(match_state.bindings[1].pending == 50)

	var valid: Dictionary = _frame(51, 151)
	var envelope: Dictionary = { "context": context, "frames": [valid] }
	assert(match_state.submit_held(1, envelope) == "OK")
	assert(match_state.submit_held(1, envelope.duplicate(true)) == "OK")
	assert(match_state.input_queues[1].size() == 1)
	match_state.free()
	print("S03-P FRESHNESS PASS")


## Builds one complete normalized frame for freshness tests.
func _frame(sequence: int, tick: int) -> Dictionary:
	return {"sequence": sequence, "input_tick": tick,
		"move": Vector2.UP, "aim_yaw": 0.0}


## Keeps intentionally skipped packet/stall frames motionless for exact pose comparison.
func _probe_move(tick: int) -> Vector2:
	if tick in [17, 75] or (tick >= 48 and tick <= 63):
		return Vector2.ZERO
	return Vector2.UP if tick < 80 else Vector2.RIGHT


## Applies the shared pure foot rule without collision or presentation state.
func _advance_position(position: Vector3, frame: Dictionary, delta: float) -> Vector3:
	var state: Dictionary = S02MotionRules.advance(
		{ "yaw": 0.0 },
		{ "move": frame.move, "aim_yaw": frame.aim_yaw, "fire": false }
	)
	return position + state.velocity * delta
