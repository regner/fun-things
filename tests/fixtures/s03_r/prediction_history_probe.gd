extends SceneTree
## Verifies bounded acknowledgement, replay ordering and overflow snap without scene mutation.


## Runs deterministic history outcomes and exits nonzero on any contract failure.
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
	_verify_numbered_input_mapping()
	print("S03-P HISTORY PASS")
	quit(0)


## Proves matching numbered frames stay correction-free across packet loss and a host stall.
func _verify_numbered_input_mapping() -> void:  # gdstyle:ignore=quality/max-local-variables
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
	var consumed: int = 0

	for tick: int in range(1, FRAME_COUNT + 1):
		var move: Vector2 = Vector2.UP if tick < 80 else Vector2.RIGHT
		var frame: Dictionary = {
			"sequence": tick, "input_tick": tick, "move": move, "aim_yaw": 0.0,
		}
		client_position = _advance_position(client_position, frame, DELTA)
		client_positions[tick] = client_position
		recent.append(frame)
		if recent.size() > 4:
			recent.pop_front()

		if tick % 2 == 0 and tick not in [18, 76]:
			var packet: Array = recent.duplicate(true)
			if tick >= STALL_START and tick < STALL_END:
				deferred_packets.append(packet)
			else:
				assert(queue.offer(packet, consumed))
		if tick == STALL_END:
			for packet: Array in deferred_packets:
				assert(queue.offer(packet, consumed))
			deferred_packets.clear()

		if tick < STALL_START or tick >= STALL_END:
			var consumed_frame: Dictionary = queue.pop_next(consumed)
			if not consumed_frame.is_empty():
				consumed = _consume_and_check(
					consumed_frame, host_position, client_positions, DELTA
				)
				host_position = client_positions[consumed]

	while queue.size() > 0:
		var consumed_frame: Dictionary = queue.pop_next(consumed)
		consumed = _consume_and_check(consumed_frame, host_position, client_positions, DELTA)
		host_position = client_positions[consumed]
	assert(consumed == FRAME_COUNT)
	print("S03-P FRAME MAP PASS")


## Advances one collision-free authority frame and compares its source-tick pose.
func _consume_and_check(
	frame: Dictionary, host_position: Vector3, client_positions: Dictionary, delta: float
) -> int:
	var next_position: Vector3 = _advance_position(host_position, frame, delta)
	assert(next_position.is_equal_approx(client_positions[frame.input_tick]))
	return frame.input_tick


## Applies the shared pure foot rule without introducing collision or presentation state.
func _advance_position(position: Vector3, frame: Dictionary, delta: float) -> Vector3:
	var state: Dictionary = S02MotionRules.advance(
		{ "yaw": 0.0 },
		{ "move": frame.move, "aim_yaw": frame.aim_yaw, "fire": false }
	)
	return position + state.velocity * delta
