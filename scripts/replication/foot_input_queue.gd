class_name FootInputQueue
extends RefCounted
## Retains bounded ordered foot intent and advances acknowledgements only on host steps.

const MAX_QUEUED_FRAMES: int = 8
const SEQUENCE_FRESHNESS_WINDOW: int = 120
const MAX_PENDING_LAG_TICKS: int = 3
const HELD_EXPIRY_MSEC: int = 250

var _frames: Array[FootCommand] = []
var _latest_sequence: int = 0
var _latest_client_tick: int = 0
var _sequence_tick_offset: int = 0
var _offset_set: bool = false
var _last_receipt_msec: int = -1
var _acknowledgement: int = 0
var _acknowledged_client_tick: int = 0


## Offers one fresh consistently numbered frame without acknowledging receipt.
func offer(command: FootCommand, receipt_msec: int) -> bool:
	if command == null or not command.is_valid() or receipt_msec < 0:
		return false
	if (
		command.sequence <= _latest_sequence
		or command.client_tick <= _latest_client_tick
		or command.sequence > _acknowledgement + SEQUENCE_FRESHNESS_WINDOW
		or _frames.size() >= MAX_QUEUED_FRAMES
	):
		return false

	var offset: int = command.client_tick - command.sequence
	if _offset_set and offset != _sequence_tick_offset:
		return false

	_frames.append(command)
	_latest_sequence = command.sequence
	_latest_client_tick = command.client_tick
	_sequence_tick_offset = offset
	_offset_set = true
	_last_receipt_msec = receipt_msec
	return true


## Consumes or supersedes at most one watermark on this authoritative simulation step.
func consume(now_msec: int) -> Dictionary:
	if now_msec < 0:
		return _neutral_result()
	if _frames.is_empty():
		return _neutral_result()
	if _last_receipt_msec >= 0 and now_msec - _last_receipt_msec > HELD_EXPIRY_MSEC:
		var expired: FootCommand = _frames[-1]
		_frames.clear()
		_advance_acknowledgement(expired)
		return {
			"command": null,
			"acknowledgement": _acknowledgement,
			"expired": true,
			"superseded": true,
		}

	var newest: FootCommand = _frames[-1]
	var selected_index: int = _frames.size() - 1
	for index: int in range(_frames.size()):
		var candidate: FootCommand = _frames[index]
		if (
			newest.sequence - candidate.sequence <= MAX_PENDING_LAG_TICKS
			and newest.client_tick - candidate.client_tick <= MAX_PENDING_LAG_TICKS
		):
			selected_index = index
			break

	var selected: FootCommand = _frames[selected_index]
	var superseded: bool = selected_index > 0
	for _index: int in range(selected_index + 1):
		_frames.pop_front()
	_advance_acknowledgement(selected)
	return {
		"command": selected,
		"acknowledgement": _acknowledgement,
		"expired": false,
		"superseded": superseded,
	}


## Clears pending input and numbering at a life, control, collision, or generation fence.
func clear() -> void:
	_frames.clear()
	_latest_sequence = 0
	_latest_client_tick = 0
	_sequence_tick_offset = 0
	_offset_set = false
	_last_receipt_msec = -1
	_acknowledgement = 0
	_acknowledged_client_tick = 0


## Reports the last sequence consumed or explicitly superseded by a host step.
func acknowledgement() -> int:
	return _acknowledgement


## Reports the bounded pending-frame count.
func size() -> int:
	return _frames.size()


## Reports when only an authorized epoch reset can make this sequence admissible.
func sequence_exceeds_freshness_window(sequence: int) -> bool:
	return sequence > _acknowledgement + SEQUENCE_FRESHNESS_WINDOW


## Advances both ordered fields together after authoritative work is selected.
func _advance_acknowledgement(command: FootCommand) -> void:
	_acknowledgement = command.sequence
	_acknowledged_client_tick = command.client_tick


## Returns neutral work without advancing the acknowledgement watermark.
func _neutral_result() -> Dictionary:
	return {
		"command": null,
		"acknowledgement": _acknowledgement,
		"expired": false,
		"superseded": false,
	}
