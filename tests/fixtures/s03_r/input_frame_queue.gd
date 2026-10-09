class_name S03InputFrameQueue
extends RefCounted
## Retains bounded, consistently numbered inputs for one-step authoritative use.

const DEFAULT_CAPACITY: int = 8
const DEFAULT_SEQUENCE_WINDOW: int = 120
const MAX_PENDING_LAG_FRAMES: int = 3

var _capacity: int
var _sequence_window: int
var _frames: Dictionary = {}
var _known_by_tick: Dictionary = {}
var _tick_by_sequence: Dictionary = {}
var _latest_sequence: int = 0
var _latest_tick: int = 0
var _tick_offset: int = 0
var _tick_offset_set: bool = false
var _last_offer_added: bool = false


## Creates a queue with separate positive pending-capacity and freshness limits.
func _init(
	capacity: int = DEFAULT_CAPACITY, sequence_window: int = DEFAULT_SEQUENCE_WINDOW
) -> void:
	assert(capacity > 0)
	assert(sequence_window > 0)
	_capacity = capacity
	_sequence_window = sequence_window


## Atomically offers exact redundancies or consistently advancing fresh frames.
func offer(  # gdstyle:ignore=quality/max-returns,quality/max-branches
	frames: Array, processed_sequence: int, processed_tick: int
) -> bool:
	_last_offer_added = false
	var additions: Dictionary = {}
	var addition_ticks_by_sequence: Dictionary = {}
	var next_offset: int = _tick_offset
	var next_offset_set: bool = _tick_offset_set
	var next_sequence: int = _latest_sequence
	var next_tick: int = _latest_tick
	if not next_offset_set and processed_sequence > 0 and processed_tick > 0:
		next_offset = processed_tick - processed_sequence
		next_offset_set = true

	for frame: Dictionary in frames:
		var sequence: int = int(frame.sequence)
		var tick: int = int(frame.input_tick)
		if _known_by_tick.has(tick):
			if _known_by_tick[tick] != frame:
				return false
			continue
		if additions.has(tick):
			if additions[tick] != frame:
				return false
			continue
		if _tick_by_sequence.has(sequence) or addition_ticks_by_sequence.has(sequence):
			return false
		if sequence <= processed_sequence or tick <= processed_tick:
			return false
		if sequence > processed_sequence + _sequence_window:
			return false
		if processed_sequence > 0 and tick > processed_tick + _sequence_window:
			return false
		if not next_offset_set:
			next_offset = tick - sequence
			next_offset_set = true
		if tick - sequence != next_offset:
			return false
		if sequence <= next_sequence or tick <= next_tick:
			return false

		additions[tick] = frame.duplicate(true)
		addition_ticks_by_sequence[sequence] = tick
		next_sequence = sequence
		next_tick = tick

	if _frames.size() + additions.size() > _capacity:
		return false
	_commit_offer(additions, next_sequence, next_tick, next_offset, next_offset_set)
	return true


## Commits one fully validated offer and its numbering state.
func _commit_offer(
	additions: Dictionary, next_sequence: int, next_tick: int,
	next_offset: int, next_offset_set: bool
) -> void:
	for tick: int in additions:
		var frame: Dictionary = additions[tick]
		_frames[tick] = frame
		_known_by_tick[tick] = frame
		_tick_by_sequence[int(frame.sequence)] = tick
	_last_offer_added = not additions.is_empty()
	_latest_sequence = next_sequence
	_latest_tick = next_tick
	_tick_offset = next_offset
	_tick_offset_set = next_offset_set
	_prune_known()


## Pops one frame after discarding enough obsolete backlog to restore the lag bound.
func pop_next(processed_sequence: int, processed_tick: int) -> Dictionary:
	_discard_processed(processed_sequence, processed_tick)
	if _frames.is_empty():
		return {}

	var ticks: Array = _frames.keys()
	ticks.sort()
	var newest_tick: int = int(ticks[-1])
	var newest_sequence: int = int(_frames[newest_tick].sequence)
	var selected_tick: int = newest_tick
	for candidate: int in ticks:
		var candidate_sequence: int = int(_frames[candidate].sequence)
		if newest_tick - candidate <= MAX_PENDING_LAG_FRAMES and (
			newest_sequence - candidate_sequence <= MAX_PENDING_LAG_FRAMES
		):
			selected_tick = candidate
			break
	var frame: Dictionary = _frames[selected_tick].duplicate(true)
	for tick: int in ticks:
		if tick <= selected_tick:
			_frames.erase(tick)
	frame["superseded_count"] = maxi(0, int(frame.sequence) - processed_sequence - 1)
	return frame


## Supersedes every pending frame so an expiry step can acknowledge neutral intent.
func supersede_all(processed_sequence: int, processed_tick: int) -> Dictionary:
	_discard_processed(processed_sequence, processed_tick)
	if _frames.is_empty():
		return {}

	var ticks: Array = _frames.keys()
	ticks.sort()
	var newest: Dictionary = _frames[int(ticks[-1])].duplicate(true)
	_frames.clear()
	newest["superseded_count"] = maxi(0, int(newest.sequence) - processed_sequence)
	return newest


## Reports whether the last valid offer contained at least one fresh numbered frame.
func last_offer_added() -> bool:
	return _last_offer_added


## Clears pending and remembered input for a new control lifecycle.
func clear() -> void:
	_frames.clear()
	_known_by_tick.clear()
	_tick_by_sequence.clear()
	_latest_sequence = 0
	_latest_tick = 0
	_tick_offset = 0
	_tick_offset_set = false
	_last_offer_added = false


## Returns the bounded number of pending authoritative input frames.
func size() -> int:
	return _frames.size()


## Removes inputs already covered by the authoritative watermark.
func _discard_processed(processed_sequence: int, processed_tick: int) -> void:
	for tick: int in _frames.keys():
		var frame: Dictionary = _frames[tick]
		if tick <= processed_tick or int(frame.sequence) <= processed_sequence:
			_frames.erase(tick)


## Retains only one freshness window of exact-copy validation history.
func _prune_known() -> void:
	var sequence_floor: int = _latest_sequence - _sequence_window
	for tick: int in _known_by_tick.keys():
		var sequence: int = int(_known_by_tick[tick].sequence)
		if sequence <= sequence_floor:
			_known_by_tick.erase(tick)
			_tick_by_sequence.erase(sequence)
