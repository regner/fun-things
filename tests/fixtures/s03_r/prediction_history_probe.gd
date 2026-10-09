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
	print("S03-P HISTORY PASS")
	quit(0)
