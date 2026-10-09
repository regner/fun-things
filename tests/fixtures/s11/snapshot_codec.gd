class_name S11SnapshotCodec
extends RefCounted

const MAGIC: int = 0x5311
const HEADER_BYTES: int = 12
const ROW_BYTES: int = 16
const MAX_PACKET_BYTES: int = 1200
const MAX_ROWS_PER_PACKET: int = (MAX_PACKET_BYTES - HEADER_BYTES) / ROW_BYTES
const POSITION_SCALE: float = 100.0
const VELOCITY_SCALE: float = 100.0
const YAW_SCALE: float = 65535.0 / TAU


## Encode complete quantized movement rows into bounded independently decodable chunks.
func encode(sequence: int, tick: int, rows: Array[Dictionary]) -> Array[PackedByteArray]:
	var packets: Array[PackedByteArray] = []
	var chunk_count: int = maxi(1, ceili(float(rows.size()) / MAX_ROWS_PER_PACKET))
	for chunk_index: int in range(chunk_count):
		var first: int = chunk_index * MAX_ROWS_PER_PACKET
		var count: int = mini(MAX_ROWS_PER_PACKET, rows.size() - first)
		var stream: StreamPeerBuffer = StreamPeerBuffer.new()
		stream.big_endian = true
		stream.put_u16(MAGIC)
		stream.put_u16(sequence & 0xffff)
		stream.put_u32(tick)
		stream.put_u8(chunk_index)
		stream.put_u8(chunk_count)
		stream.put_u8(count)
		stream.put_u8(0)
		for row_index: int in range(first, first + count):
			_put_row(stream, rows[row_index])

		packets.append(stream.data_array)

	return packets


## Decode one bounded chunk, rejecting malformed lengths and unsupported fields before rows.
func decode(packet: PackedByteArray) -> Dictionary:
	if packet.size() < HEADER_BYTES or packet.size() > MAX_PACKET_BYTES:
		return {}

	var stream: StreamPeerBuffer = StreamPeerBuffer.new()
	stream.big_endian = true
	stream.data_array = packet
	if stream.get_u16() != MAGIC:
		return {}

	var sequence: int = stream.get_u16()
	var tick: int = stream.get_u32()
	var chunk_index: int = stream.get_u8()
	var chunk_count: int = stream.get_u8()
	var row_count: int = stream.get_u8()
	stream.get_u8()
	if chunk_count < 1 or chunk_index >= chunk_count or row_count > MAX_ROWS_PER_PACKET:
		return {}
	if packet.size() != HEADER_BYTES + row_count * ROW_BYTES:
		return {}

	var rows: Array[Dictionary] = []
	for _row_index: int in range(row_count):
		rows.append(_get_row(stream))

	return {
		"sequence": sequence,
		"tick": tick,
		"chunk_index": chunk_index,
		"chunk_count": chunk_count,
		"rows": rows,
	}


## Encode one reliable lifecycle transaction on the dedicated state stream.
func encode_lifecycle(
	event_kind: int, entity_id: int, generation: int, phase: int, revision: int, tick: int
) -> PackedByteArray:
	var stream: StreamPeerBuffer = StreamPeerBuffer.new()
	stream.big_endian = true
	stream.put_u16(MAGIC)
	stream.put_u8(event_kind)
	stream.put_u8(phase)
	stream.put_u16(entity_id)
	stream.put_u8(generation)
	stream.put_u8(0)
	stream.put_u32(revision)
	stream.put_u32(tick)
	return stream.data_array


## Decode one exact-size lifecycle transaction without accepting extra trailing fields.
func decode_lifecycle(packet: PackedByteArray) -> Dictionary:
	if packet.size() != 16:
		return {}

	var stream: StreamPeerBuffer = StreamPeerBuffer.new()
	stream.big_endian = true
	stream.data_array = packet
	if stream.get_u16() != MAGIC:
		return {}

	var event_kind: int = stream.get_u8()
	var phase: int = stream.get_u8()
	var entity_id: int = stream.get_u16()
	var generation: int = stream.get_u8()
	stream.get_u8()
	var revision: int = stream.get_u32()
	var tick: int = stream.get_u32()
	if event_kind < 1 or event_kind > 4 or entity_id < 1 or generation < 1:
		return {}

	return {
		"event_kind": event_kind,
		"phase": phase,
		"id": entity_id,
		"generation": generation,
		"revision": revision,
		"tick": tick,
	}


## Write one fixed-width quantized movement row.
func _put_row(stream: StreamPeerBuffer, row: Dictionary) -> void:
	stream.put_u16(int(row.id))
	stream.put_u8(int(row.generation))
	stream.put_u8(int(row.kind))
	stream.put_u8(int(row.phase))
	stream.put_u8(int(row.get("flags", 0)))
	stream.put_u16(_signed_to_u16(roundi(float(row.x) * POSITION_SCALE)))
	stream.put_u16(_signed_to_u16(roundi(float(row.z) * POSITION_SCALE)))
	stream.put_u16(_signed_to_u16(roundi(float(row.vx) * VELOCITY_SCALE)))
	stream.put_u16(_signed_to_u16(roundi(float(row.vz) * VELOCITY_SCALE)))
	stream.put_u16(posmod(roundi(float(row.yaw) * YAW_SCALE), 65_536))


## Read one fixed-width movement row into local metric units.
func _get_row(stream: StreamPeerBuffer) -> Dictionary:
	return {
		"id": stream.get_u16(),
		"generation": stream.get_u8(),
		"kind": stream.get_u8(),
		"phase": stream.get_u8(),
		"flags": stream.get_u8(),
		"x": float(_u16_to_signed(stream.get_u16())) / POSITION_SCALE,
		"z": float(_u16_to_signed(stream.get_u16())) / POSITION_SCALE,
		"vx": float(_u16_to_signed(stream.get_u16())) / VELOCITY_SCALE,
		"vz": float(_u16_to_signed(stream.get_u16())) / VELOCITY_SCALE,
		"yaw": float(stream.get_u16()) / YAW_SCALE,
	}


## Preserve a signed quantized value in an unsigned wire field.
func _signed_to_u16(value: int) -> int:
	return value & 0xffff


## Recover a signed quantized value from an unsigned wire field.
func _u16_to_signed(value: int) -> int:
	return value - 65_536 if value >= 32_768 else value
