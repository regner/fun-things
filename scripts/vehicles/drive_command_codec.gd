class_name DriveCommandCodec
extends RefCounted
## Encodes held vehicle intent into one fixed packet before the remote command boundary.

const PACKET_BYTES: int = 16
const MAX_CLIENT_TICK: int = 0xffff_ffff
const MAX_INPUT_EPOCH: int = 0xff
const AXIS_ENCODE_SCALE: float = 32_766.0
const AXIS_DECODE_SCALE: float = 32_767.0
const FLAG_HANDBRAKE: int = 1
const VALID_FLAGS: int = FLAG_HANDBRAKE


## Encodes one complete bounded drive command and its current control epoch.
static func encode(command: DriveCommand, input_epoch: int) -> Dictionary:
	if command == null or not command.is_valid():
		return _failure(&"MALFORMED_COMMAND")
	if (
		command.sequence > 0xffff_ffff
		or command.client_tick > MAX_CLIENT_TICK
		or input_epoch <= 0
		or input_epoch > MAX_INPUT_EPOCH
	):
		return _failure(&"COMMAND_OUT_OF_RANGE")

	var stream := StreamPeerBuffer.new()
	stream.big_endian = true
	stream.put_u32(command.sequence)
	stream.put_u32(command.client_tick)
	stream.put_u16(_signed_to_u16(roundi(command.throttle * AXIS_ENCODE_SCALE)))
	stream.put_u16(_signed_to_u16(roundi(command.steer * AXIS_ENCODE_SCALE)))
	stream.put_u16(_signed_to_u16(roundi(command.brake * AXIS_ENCODE_SCALE)))
	stream.put_u8(FLAG_HANDBRAKE if command.handbrake else 0)
	stream.put_u8(input_epoch)
	return { "ok": true, "packet": stream.data_array }


## Rejects size and reserved bits before exposing one decoded command.
static func decode(packet: PackedByteArray) -> Dictionary:
	if packet.size() != PACKET_BYTES:
		return _failure(&"PACKET_SIZE")

	var stream := StreamPeerBuffer.new()
	stream.big_endian = true
	stream.data_array = packet
	var command := DriveCommand.new(
		stream.get_u32(),
		stream.get_u32(),
		float(_u16_to_signed(stream.get_u16())) / AXIS_DECODE_SCALE,
		float(_u16_to_signed(stream.get_u16())) / AXIS_DECODE_SCALE,
		float(_u16_to_signed(stream.get_u16())) / AXIS_DECODE_SCALE,
		false,
	)
	var flags: int = stream.get_u8()
	var input_epoch: int = stream.get_u8()
	if input_epoch == 0 or flags & ~VALID_FLAGS != 0:
		return _failure(&"MALFORMED_COMMAND")
	command.handbrake = flags & FLAG_HANDBRAKE != 0
	if not command.is_valid():
		return _failure(&"COMMAND_OUT_OF_RANGE")
	return { "ok": true, "command": command, "input_epoch": input_epoch }


## Preserves one signed quantized control in an unsigned wire field.
static func _signed_to_u16(value: int) -> int:
	return value & 0xffff


## Recovers one signed quantized control from its unsigned wire field.
static func _u16_to_signed(value: int) -> int:
	return value - 65_536 if value >= 32_768 else value


## Returns one normalized codec refusal without partial command state.
static func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
