class_name FootCommand
extends RefCounted
## Immutable-by-convention held foot intent accepted by standalone, authority, and replay.

const FIELD_COUNT: int = 6
const MAX_MOVE_LENGTH_SQUARED: float = 1.0

var sequence: int
var client_tick: int
var move: Vector2
var aim_yaw: float
var fire_held: bool
var alt_held: bool


## Creates all six protocol fields; callers must check is_valid before simulation.
func _init(  # gdstyle:ignore=quality/max-parameters
	command_sequence: int,
	command_client_tick: int,
	command_move: Vector2,
	command_aim_yaw: float,
	command_fire_held: bool,
	command_alt_held: bool
) -> void:
	sequence = command_sequence
	client_tick = command_client_tick
	move = command_move
	aim_yaw = command_aim_yaw
	fire_held = command_fire_held
	alt_held = command_alt_held


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
		or not fields.move is Vector2
		or not fields.aim_yaw is float
		or not fields.fire_held is bool
		or not fields.alt_held is bool
	):
		return _failure(&"MALFORMED_COMMAND")

	var command := FootCommand.new(
		fields.sequence,
		fields.client_tick,
		fields.move,
		fields.aim_yaw,
		fields.fire_held,
		fields.alt_held
	)
	if not command.is_valid():
		return _failure(&"COMMAND_OUT_OF_RANGE")
	return { "ok": true, "command": command }


## Requires every command field exactly once so unknown data cannot be ignored.
static func _has_exact_fields(fields: Dictionary) -> bool:
	if fields.size() != FIELD_COUNT:
		return false
	for field: StringName in [
		&"sequence",
		&"client_tick",
		&"move",
		&"aim_yaw",
		&"fire_held",
		&"alt_held",
	]:
		if not fields.has(field):
			return false
	return true


## Reports whether every field is finite, canonical, and inside its admitted range.
func is_valid() -> bool:
	return (
		sequence > 0
		and client_tick >= 0
		and move.is_finite()
		and move.length_squared() <= MAX_MOVE_LENGTH_SQUARED
		and is_finite(aim_yaw)
		and aim_yaw >= -PI
		and aim_yaw <= PI
	)


## Returns a normalized decode failure shape for future admission callers.
static func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
