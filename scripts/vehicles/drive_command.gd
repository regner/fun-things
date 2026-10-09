class_name DriveCommand
extends RefCounted
## Immutable-by-convention vehicle intent shared by standalone, authority, replay, and AI.

const FIELD_COUNT: int = 6

var sequence: int
var client_tick: int
var throttle: float
var steer: float
var brake: float
var handbrake: bool


## Creates the complete command shape; callers must check is_valid before simulation.
func _init(  # gdstyle:ignore=quality/max-parameters
	command_sequence: int,
	command_client_tick: int,
	command_throttle: float,
	command_steer: float,
	command_brake: float,
	command_handbrake: bool
) -> void:
	sequence = command_sequence
	client_tick = command_client_tick
	throttle = command_throttle
	steer = command_steer
	brake = command_brake
	handbrake = command_handbrake


## Supplies fresh neutral intent so controllers never share a mutable command.
static func neutral(command_sequence: int, command_client_tick: int) -> DriveCommand:
	return DriveCommand.new(command_sequence, command_client_tick, 0.0, 0.0, 0.0, false)


## Decodes the exact local command schema without mutating simulation on failure.
static func decode(payload: Variant) -> Dictionary:
	if not payload is Dictionary:
		return _failure(&"MALFORMED_COMMAND")

	var fields: Dictionary = payload
	if not _has_exact_fields(fields):
		return _failure(&"MALFORMED_COMMAND")
	if (
		not fields.sequence is int
		or not fields.client_tick is int
		or not fields.throttle is float
		or not fields.steer is float
		or not fields.brake is float
		or not fields.handbrake is bool
	):
		return _failure(&"MALFORMED_COMMAND")

	var command := DriveCommand.new(
		fields.sequence,
		fields.client_tick,
		fields.throttle,
		fields.steer,
		fields.brake,
		fields.handbrake
	)
	if not command.is_valid():
		return _failure(&"COMMAND_OUT_OF_RANGE")
	return { "ok": true, "command": command }


## Reports whether every field is finite and inside its admitted range.
func is_valid() -> bool:
	return (
		sequence > 0
		and client_tick >= 0
		and is_finite(throttle)
		and throttle >= -1.0
		and throttle <= 1.0
		and is_finite(steer)
		and steer >= -1.0
		and steer <= 1.0
		and is_finite(brake)
		and brake >= 0.0
		and brake <= 1.0
	)


## Requires every command field exactly once so unknown data cannot be ignored.
static func _has_exact_fields(fields: Dictionary) -> bool:
	if fields.size() != FIELD_COUNT:
		return false
	for field: StringName in [
		&"sequence",
		&"client_tick",
		&"throttle",
		&"steer",
		&"brake",
		&"handbrake",
	]:
		if not fields.has(field):
			return false
	return true


## Returns a normalized decode failure shape for future admission callers.
static func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
