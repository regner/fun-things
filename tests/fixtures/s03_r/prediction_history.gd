class_name S03PredictionHistory
extends RefCounted
## Stores bounded numbered simulation inputs for acknowledgement and deterministic replay.

const DEFAULT_CAPACITY: int = 120

var _capacity: int
var _frames: Array[Dictionary] = []
var _dropped_through_tick: int = -1
var _latest_tick: int = -1


## Creates a history with a positive hard frame limit.
func _init(capacity: int = DEFAULT_CAPACITY) -> void:
	assert(capacity > 0)
	_capacity = capacity


## Records one strictly newer input frame and reports whether old history was dropped.
func push(tick: int, command: Dictionary, delta_seconds: float) -> bool:
	assert(tick > _latest_tick)
	assert(is_finite(delta_seconds) and delta_seconds > 0.0)
	_latest_tick = tick
	_frames.append({ "tick": tick, "command": command.duplicate(true),
		"delta": delta_seconds })
	if _frames.size() <= _capacity:
		return false

	var dropped: Dictionary = _frames.pop_front()
	_dropped_through_tick = int(dropped.tick)
	return true


## Discards acknowledged frames and returns the remaining replay or a required snap.
func acknowledge(processed_tick: int) -> Dictionary:
	if processed_tick < _dropped_through_tick:
		var dropped_tick: int = _dropped_through_tick
		clear()
		return { "frames": [], "history_exhausted": true,
			"dropped_through": dropped_tick }

	while not _frames.is_empty() and int(_frames[0].tick) <= processed_tick:
		_frames.pop_front()

	return {"frames": _frames.duplicate(true), "history_exhausted": false,
		"dropped_through": _dropped_through_tick}


## Clears every retained frame and overflow watermark for a new control lifecycle.
func clear() -> void:
	_frames.clear()
	_dropped_through_tick = -1
	_latest_tick = -1


## Returns the bounded number of currently replayable input frames.
func size() -> int:
	return _frames.size()
