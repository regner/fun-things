extends GutTest
## Verifies the fixed vehicle input packet and strict decode boundary.


## Round-trips all drive controls within the fixed quantization tolerance.
func test_round_trip_uses_exact_sixteen_byte_packet() -> void:
	var command := DriveCommand.new(17, 23, -0.75, 0.5, 0.25, true)
	var encoded: Dictionary = DriveCommandCodec.encode(command, 4)
	assert_true(encoded.ok)
	assert_eq((encoded.packet as PackedByteArray).size(), DriveCommandCodec.PACKET_BYTES)

	var decoded: Dictionary = DriveCommandCodec.decode(encoded.packet)
	assert_true(decoded.ok)
	assert_eq(decoded.command.sequence, 17)
	assert_eq(decoded.command.client_tick, 23)
	assert_almost_eq(decoded.command.throttle, -0.75, 0.0001)
	assert_almost_eq(decoded.command.steer, 0.5, 0.0001)
	assert_almost_eq(decoded.command.brake, 0.25, 0.0001)
	assert_true(decoded.command.handbrake)
	assert_eq(decoded.input_epoch, 4)


## Rejects wrong sizes, reserved bits, zero epochs, and invalid command ranges.
func test_decode_rejects_malformed_packets_without_partial_command() -> void:
	assert_eq(
		DriveCommandCodec.decode(PackedByteArray()).failure.code,
		&"PACKET_SIZE",
	)
	var encoded: Dictionary = DriveCommandCodec.encode(
		DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false),
		1,
	)
	var reserved: PackedByteArray = (encoded.packet as PackedByteArray).duplicate()
	reserved[DriveCommandCodec.PACKET_BYTES - 2] = 2
	assert_eq(DriveCommandCodec.decode(reserved).failure.code, &"MALFORMED_COMMAND")

	var zero_epoch: PackedByteArray = (encoded.packet as PackedByteArray).duplicate()
	zero_epoch[DriveCommandCodec.PACKET_BYTES - 1] = 0
	assert_eq(DriveCommandCodec.decode(zero_epoch).failure.code, &"MALFORMED_COMMAND")
	assert_eq(
		DriveCommandCodec.encode(
			DriveCommand.new(0, 1, 1.0, 0.0, 0.0, false),
			1,
		).failure.code,
		&"MALFORMED_COMMAND",
	)
