class_name VehicleInputQueue
extends RefCounted
## Retains bounded ordered drive intent and acknowledges only host simulation work.

const MAX_QUEUED_FRAMES: int = 8
const SEQUENCE_FRESHNESS_WINDOW: int = 120
const HELD_EXPIRY_MSEC: int = 250

var _frames: Array[DriveCommand] = []
var _latest_sequence: int = 0
var _latest_client_tick: int = 0
var _sequence_tick_offset: int = 0
var _offset_set: bool = false
var _last_receipt_msec: int = -1
var _acknowledgement: int = 0
var _held_command: DriveCommand


## Offers one fresh consistently numbered command without acknowledging receipt.
func offer(command: DriveCommand, receipt_msec: int) -> bool:
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


## Consumes one current frame or explicitly supersedes stale intent on this host tick.
func consume(now_msec: int) -> Dictionary:
	if now_msec < 0:
		return _neutral_result()
	if _last_receipt_msec >= 0 and now_msec - _last_receipt_msec > HELD_EXPIRY_MSEC:
		var superseded: bool = not _frames.is_empty()
		if superseded:
			_acknowledgement = (_frames[-1] as DriveCommand).sequence
		_frames.clear()
		_held_command = null
		return {
			"command": null,
			"acknowledgement": _acknowledgement,
			"expired": true,
			"superseded": superseded,
		}
	if _frames.is_empty():
		var held: Dictionary = _neutral_result()
		held.command = _held_command
		return held

	var selected: DriveCommand = _frames[-1]
	var superseded: bool = _frames.size() > 1
	_frames.clear()
	_acknowledgement = selected.sequence
	_held_command = selected
	return {
		"command": selected,
		"acknowledgement": _acknowledgement,
		"expired": false,
		"superseded": superseded,
	}


## Clears pending intent and numbering at a control or lifecycle fence.
func clear() -> void:
	_frames.clear()
	_latest_sequence = 0
	_latest_client_tick = 0
	_sequence_tick_offset = 0
	_offset_set = false
	_last_receipt_msec = -1
	_acknowledgement = 0
	_held_command = null


## Reports whether only a new host control revision may restart this sequence.
func sequence_exceeds_freshness_window(sequence: int) -> bool:
	return sequence > _acknowledgement + SEQUENCE_FRESHNESS_WINDOW


## Reports the latest command consumed or explicitly superseded by simulation.
func acknowledgement() -> int:
	return _acknowledgement


## Reports bounded queued work for diagnostics and abuse tests.
func size() -> int:
	return _frames.size()


## Returns neutral work without advancing the host watermark.
func _neutral_result() -> Dictionary:
	return {
		"command": null,
		"acknowledgement": _acknowledgement,
		"expired": false,
		"superseded": false,
	}
