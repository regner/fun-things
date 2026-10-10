class_name FootCommandCodec
extends RefCounted
## Encodes held foot intent into one fixed packet before the remotely callable boundary.

const PACKET_BYTES: int = 16
const MAX_CLIENT_TICK: int = 0x00ff_ffff
const MAX_INPUT_EPOCH: int = 0xff
const MOVE_ENCODE_SCALE: float = 32_766.0
const MOVE_DECODE_SCALE: float = 32_767.0
const YAW_SCALE: float = 32_767.0 / PI
const FLAG_FIRE: int = 1
const FLAG_ALT: int = 2
const VALID_FLAGS: int = FLAG_FIRE | FLAG_ALT


## Encodes one valid command with its entity generation and recoverable input epoch.
static func encode(command: FootCommand, generation: int, input_epoch: int) -> Dictionary:
	if command == null or not command.is_valid():
		return _failure(&"MALFORMED_COMMAND")
	if (
		command.sequence > 0xffff_ffff
		or command.client_tick > MAX_CLIENT_TICK
		or generation <= 0
		or generation > ReplicationIdentity.MAX_WIRE_GENERATION
		or input_epoch <= 0
		or input_epoch > MAX_INPUT_EPOCH
	):
		return _failure(&"COMMAND_OUT_OF_RANGE")

	var stream := StreamPeerBuffer.new()
	stream.big_endian = true
	stream.put_u32(command.sequence)
	stream.put_u32((input_epoch << 24) | command.client_tick)
	stream.put_u16(_signed_to_u16(roundi(command.move.x * MOVE_ENCODE_SCALE)))
	stream.put_u16(_signed_to_u16(roundi(command.move.y * MOVE_ENCODE_SCALE)))
	stream.put_u16(_signed_to_u16(roundi(command.aim_yaw * YAW_SCALE)))
	var flags: int = 0
	if command.fire_held:
		flags |= FLAG_FIRE
	if command.alt_held:
		flags |= FLAG_ALT
	stream.put_u8(flags)
	stream.put_u8(generation)
	return { "ok": true, "packet": stream.data_array }


## Rejects size before reading fields, then validates reserved bits and command ranges.
static func decode(packet: PackedByteArray) -> Dictionary:
	if packet.size() != PACKET_BYTES:
		return _failure(&"PACKET_SIZE")

	var stream := StreamPeerBuffer.new()
	stream.big_endian = true
	stream.data_array = packet
	var sequence: int = stream.get_u32()
	var packed_tick: int = stream.get_u32()
	var input_epoch: int = packed_tick >> 24
	var client_tick: int = packed_tick & MAX_CLIENT_TICK
	var move := Vector2(
		float(_u16_to_signed(stream.get_u16())) / MOVE_DECODE_SCALE,
		float(_u16_to_signed(stream.get_u16())) / MOVE_DECODE_SCALE,
	)
	var aim_yaw: float = float(_u16_to_signed(stream.get_u16())) / YAW_SCALE
	var flags: int = stream.get_u8()
	var generation: int = stream.get_u8()
	if generation == 0 or input_epoch == 0 or flags & ~VALID_FLAGS != 0:
		return _failure(&"MALFORMED_COMMAND")

	var command := FootCommand.new(
		sequence,
		client_tick,
		move,
		aim_yaw,
		flags & FLAG_FIRE != 0,
		flags & FLAG_ALT != 0,
	)
	if not command.is_valid():
		return _failure(&"COMMAND_OUT_OF_RANGE")
	return {
		"ok": true,
		"command": command,
		"generation": generation,
		"input_epoch": input_epoch,
	}


## Preserves one signed quantized value in an unsigned wire field.
static func _signed_to_u16(value: int) -> int:
	return value & 0xffff


## Recovers one signed quantized value from an unsigned wire field.
static func _u16_to_signed(value: int) -> int:
	return value - 65_536 if value >= 32_768 else value


## Returns one normalized codec failure without a partially exposed command.
static func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
