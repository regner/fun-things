class_name S03InputFrameQueue
extends RefCounted
## Retains a bounded set of validated numbered inputs for one-step authoritative use.

const DEFAULT_CAPACITY: int = 120

var _capacity: int
var _frames: Dictionary = {}


## Creates a queue with a positive hard frame limit.
func _init(capacity: int = DEFAULT_CAPACITY) -> void:
	assert(capacity > 0)
	_capacity = capacity


## Atomically offers fresh frames, accepting identical redundant copies only.
func offer(frames: Array, processed_tick: int) -> bool:
	var additions: Dictionary = {}
	for frame: Dictionary in frames:
		var tick: int = int(frame.input_tick)
		if tick <= processed_tick:
			continue
		if _frames.has(tick):
			if _frames[tick] != frame:
				return false
			continue
		if additions.has(tick) and additions[tick] != frame:
			return false
		additions[tick] = frame.duplicate(true)

	if _frames.size() + additions.size() > _capacity:
		return false
	for tick: int in additions:
		_frames[tick] = additions[tick]
	return true


## Pops the oldest available frame for exactly one authoritative simulation step.
func pop_next(processed_tick: int) -> Dictionary:
	for tick: int in _frames.keys():
		if tick <= processed_tick:
			_frames.erase(tick)
	if _frames.is_empty():
		return {}

	var ticks: Array = _frames.keys()
	ticks.sort()
	var next_tick: int = int(ticks[0])
	var frame: Dictionary = _frames[next_tick].duplicate(true)
	_frames.erase(next_tick)
	frame["superseded_count"] = (
		0 if processed_tick == 0 else maxi(0, next_tick - processed_tick - 1)
	)
	return frame


## Clears all pending inputs for a new control lifecycle.
func clear() -> void:
	_frames.clear()


## Returns the bounded number of pending authoritative input frames.
func size() -> int:
	return _frames.size()
