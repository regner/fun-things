extends GutTest
## Verifies exact foot-command admission without copying movement implementation formulas.


## Accepts the complete production command shape and preserves every intent field.
func test_decode_accepts_complete_command() -> void:
	var result: Dictionary = FootCommand.decode(_valid_payload())

	assert_true(result.ok)
	var command: FootCommand = result.command
	assert_eq(command.sequence, 8)
	assert_eq(command.client_tick, 42)
	assert_eq(command.move, Vector2(0.6, -0.8))
	assert_eq(command.aim_yaw, 0.75)
	assert_true(command.fire_held)
	assert_false(command.alt_held)


## Rejects missing, extra, and incorrectly typed fields before command construction.
func test_decode_rejects_malformed_shapes() -> void:
	var malformed: Array[Variant] = [
		42,
		{},
		{
			"sequence": 8,
			"client_tick": 42,
			"move": Vector2.ZERO,
			"aim_yaw": 0.0,
			"fire_held": false,
		},
	]
	var extra: Dictionary = _valid_payload()
	extra.unexpected = true
	malformed.append(extra)
	var wrong_type: Dictionary = _valid_payload()
	wrong_type.fire_held = 1
	malformed.append(wrong_type)

	for payload: Variant in malformed:
		var result: Dictionary = FootCommand.decode(payload)
		assert_false(result.ok)
		assert_eq(result.failure.code, &"MALFORMED_COMMAND")


## Rejects nonfinite, noncanonical, and out-of-range command values.
func test_decode_rejects_out_of_range_values() -> void:
	var invalid_payloads: Array[Dictionary] = []
	for update: Dictionary in [
		{ "sequence": 0 },
		{ "client_tick": -1 },
		{ "move": Vector2(1.01, 0.0) },
		{ "move": Vector2(NAN, 0.0) },
		{ "aim_yaw": NAN },
		{ "aim_yaw": PI + 0.01 },
	]:
		var payload: Dictionary = _valid_payload()
		for key: String in update:
			payload[key] = update[key]
		invalid_payloads.append(payload)

	for payload: Dictionary in invalid_payloads:
		var result: Dictionary = FootCommand.decode(payload)
		assert_false(result.ok)
		assert_eq(result.failure.code, &"COMMAND_OUT_OF_RANGE")


## Builds one independently chosen valid payload for decoder outcomes.
func _valid_payload() -> Dictionary:
	return {
		"sequence": 8,
		"client_tick": 42,
		"move": Vector2(0.6, -0.8),
		"aim_yaw": 0.75,
		"fire_held": true,
		"alt_held": false,
	}
