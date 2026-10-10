extends GutTest
## Verifies the fixed held-input wire shape before host authority processing.


## Round-trips every FootCommand field within the frozen quantization error.
func test_round_trip_uses_exact_fixed_packet() -> void:
	var command := FootCommand.new(71, 990, Vector2(0.25, -0.75), 1.2, true, false)
	var encoded: Dictionary = FootCommandCodec.encode(command, 7, 3)
	var decoded: Dictionary = FootCommandCodec.decode(encoded.packet)

	assert_true(encoded.ok)
	assert_eq(encoded.packet.size(), FootCommandCodec.PACKET_BYTES)
	assert_true(decoded.ok)
	assert_eq(decoded.command.sequence, command.sequence)
	assert_eq(decoded.command.client_tick, command.client_tick)
	assert_eq(decoded.generation, 7)
	assert_eq(decoded.input_epoch, 3)
	assert_almost_eq(decoded.command.move.x, command.move.x, 0.0001)
	assert_almost_eq(decoded.command.move.y, command.move.y, 0.0001)
	assert_almost_eq(decoded.command.aim_yaw, command.aim_yaw, 0.0001)
	assert_true(decoded.command.fire_held)
	assert_false(decoded.command.alt_held)

	var diagonal: Dictionary = FootCommandCodec.decode(
		FootCommandCodec.encode(
			FootCommand.new(72, 991, Vector2.ONE.normalized(), -PI, false, true), 7, 3
		).packet
	)
	assert_true(diagonal.ok)
	assert_lte(diagonal.command.move.length_squared(), 1.0)


## Rejects undersize and oversize packets before field decoding.
func test_decode_rejects_every_non_fixed_size() -> void:
	var undersize := PackedByteArray()
	undersize.resize(FootCommandCodec.PACKET_BYTES - 1)
	var oversize := PackedByteArray()
	oversize.resize(MeasuredReplicationCodec.MAX_PACKET_BYTES + 1)

	assert_eq(FootCommandCodec.decode(undersize).failure.code, &"PACKET_SIZE")
	assert_eq(FootCommandCodec.decode(oversize).failure.code, &"PACKET_SIZE")


## Rejects action-flag mutations and missing generation without exposing a command.
func test_decode_rejects_malformed_fixed_packet() -> void:
	var encoded: Dictionary = FootCommandCodec.encode(
		FootCommand.new(1, 2, Vector2.ZERO, 0.0, false, false), 1, 1
	)
	var reserved_packet: PackedByteArray = encoded.packet.duplicate()
	reserved_packet[FootCommandCodec.PACKET_BYTES - 1] = 0
	var flags_packet: PackedByteArray = encoded.packet.duplicate()
	flags_packet[FootCommandCodec.PACKET_BYTES - 2] = 0x80

	assert_eq(FootCommandCodec.decode(reserved_packet).failure.code, &"MALFORMED_COMMAND")
	assert_eq(FootCommandCodec.decode(flags_packet).failure.code, &"MALFORMED_COMMAND")
