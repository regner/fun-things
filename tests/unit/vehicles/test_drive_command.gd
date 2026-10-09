extends GutTest
## Verifies exact vehicle-command admission without copying handling formulas.


## Accepts the complete production command shape and preserves every intent field.
func test_decode_accepts_complete_command() -> void:
	var result: Dictionary = DriveCommand.decode(_valid_payload())

	assert_true(result.ok)
	var command: DriveCommand = result.command
	assert_eq(command.sequence, 8)
	assert_eq(command.client_tick, 42)
	assert_eq(command.throttle, -0.75)
	assert_eq(command.steer, 0.5)
	assert_eq(command.brake, 0.25)
	assert_true(command.handbrake)


## Rejects missing, extra, and incorrectly typed fields before construction.
func test_decode_rejects_malformed_shapes() -> void:
	var malformed: Array[Variant] = [
		42,
		{},
		{
			"sequence": 8,
			"client_tick": 42,
			"throttle": 0.0,
			"steer": 0.0,
			"brake": 0.0,
		},
	]
	var extra: Dictionary = _valid_payload()
	extra.unexpected = true
	malformed.append(extra)
	var wrong_type: Dictionary = _valid_payload()
	wrong_type.throttle = 1
	malformed.append(wrong_type)

	for payload: Variant in malformed:
		var result: Dictionary = DriveCommand.decode(payload)
		assert_false(result.ok)
		assert_eq(result.failure.code, &"MALFORMED_COMMAND")


## Rejects nonfinite and out-of-range sequence, tick, and analog values.
func test_decode_rejects_out_of_range_values() -> void:
	var invalid_payloads: Array[Dictionary] = []
	for update: Dictionary in [
		{ "sequence": 0 },
		{ "client_tick": -1 },
		{ "throttle": 1.01 },
		{ "throttle": NAN },
		{ "steer": -1.01 },
		{ "steer": NAN },
		{ "brake": -0.01 },
		{ "brake": 1.01 },
		{ "brake": NAN },
	]:
		var payload: Dictionary = _valid_payload()
		for key: String in update:
			payload[key] = update[key]
		invalid_payloads.append(payload)

	for payload: Dictionary in invalid_payloads:
		var result: Dictionary = DriveCommand.decode(payload)
		assert_false(result.ok)
		assert_eq(result.failure.code, &"COMMAND_OUT_OF_RANGE")


## Produces one independently chosen valid payload for decoder outcomes.
func _valid_payload() -> Dictionary:
	return {
		"sequence": 8,
		"client_tick": 42,
		"throttle": -0.75,
		"steer": 0.5,
		"brake": 0.25,
		"handbrake": true,
	}
