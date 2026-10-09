class_name MeasuredReplicationCodec
extends RefCounted
## Encodes only S11's measured 12-byte header, 16-byte row, and 16-byte durable shape.

const MAGIC: int = 0x5311
const HEADER_BYTES: int = 12
const ROW_BYTES: int = 16
const DURABLE_BYTES: int = 16
const MAX_PACKET_BYTES: int = 1200
const MAX_ROWS_PER_PACKET: int = (MAX_PACKET_BYTES - HEADER_BYTES) / ROW_BYTES
const MAX_CHUNKS: int = 255
const POSITION_STEP_METRES: float = 0.02
const POSITION_ORIGIN_X: float = -0.51565
const POSITION_ORIGIN_Z: float = 199.42865
const POSITION_QUANTIZED_MIN: int = -32_768
const POSITION_QUANTIZED_MAX: int = 32_767
const POSITION_MARGIN_METRES: float = 50.0
const VELOCITY_SCALE: float = 100.0
const YAW_SCALE: float = 65_535.0 / TAU
const MOVEMENT_FIELDS: Array[String] = [
	"id",
	"generation",
	"kind",
	"phase",
	"flags",
	"x",
	"z",
	"vx",
	"vz",
	"yaw",
]
const DURABLE_FIELDS: Array[String] = [
	"event_kind",
	"phase",
	"id",
	"generation",
	"revision",
	"tick",
]

var position_clamp_count: int = 0


## Encodes complete rows into independently decodable measured chunks.
func encode_movement(sequence: int, tick: int, rows: Array[Dictionary]) -> Dictionary:
	if (
		sequence < 0
		or sequence > 65_535
		or tick < 0
		or tick > 0xffff_ffff
		or rows.size() > MAX_ROWS_PER_PACKET * MAX_CHUNKS
	):
		return _failure(&"OUT_OF_RANGE")
	for row: Dictionary in rows:
		if not _valid_movement_row(row):
			return _failure(&"MALFORMED_ROW")

	var packets: Array[PackedByteArray] = []
	var clamped_before: int = position_clamp_count
	var chunk_count: int = maxi(1, ceili(float(rows.size()) / MAX_ROWS_PER_PACKET))
	for chunk_index: int in range(chunk_count):
		var first: int = chunk_index * MAX_ROWS_PER_PACKET
		var row_count: int = mini(MAX_ROWS_PER_PACKET, rows.size() - first)
		# Each independently useful chunk owns one fixed buffer below the measured ceiling.
		# gdstyle:ignore=quality/allocation-in-loop
		var stream := StreamPeerBuffer.new()
		stream.big_endian = true
		stream.put_u16(MAGIC)
		stream.put_u16(sequence)
		stream.put_u32(tick)
		stream.put_u8(chunk_index)
		stream.put_u8(chunk_count)
		stream.put_u8(row_count)
		stream.put_u8(0)
		for row_index: int in range(first, first + row_count):
			_put_movement_row(stream, rows[row_index])

		packets.append(stream.data_array)

	return {
		"ok": true,
		"packets": packets,
		"clamped_rows": position_clamp_count - clamped_before,
	}


## Decodes one exact measured movement chunk before exposing any row mutation.
func decode_movement(packet: PackedByteArray) -> Dictionary:
	if packet.size() < HEADER_BYTES or packet.size() > MAX_PACKET_BYTES:
		return _failure(&"PACKET_SIZE")

	var stream := StreamPeerBuffer.new()
	stream.big_endian = true
	stream.data_array = packet
	if stream.get_u16() != MAGIC:
		return _failure(&"BAD_MAGIC")

	var sequence: int = stream.get_u16()
	var tick: int = stream.get_u32()
	var chunk_index: int = stream.get_u8()
	var chunk_count: int = stream.get_u8()
	var row_count: int = stream.get_u8()
	var reserved: int = stream.get_u8()
	if (
		chunk_count < 1
		or chunk_index >= chunk_count
		or row_count > MAX_ROWS_PER_PACKET
		or reserved != 0
		or packet.size() != HEADER_BYTES + row_count * ROW_BYTES
	):
		return _failure(&"MALFORMED_PACKET")

	var rows: Array[Dictionary] = []
	for _row_index: int in range(row_count):
		var row: Dictionary = _get_movement_row(stream)
		if not _valid_movement_row(row):
			return _failure(&"MALFORMED_ROW")

		rows.append(row)

	return {
		"ok": true,
		"sequence": sequence,
		"tick": tick,
		"chunk_index": chunk_index,
		"chunk_count": chunk_count,
		"rows": rows,
	}


## Encodes one exact reliable lifecycle record on the durable stream.
func encode_durable(event: Dictionary) -> Dictionary:
	if not _valid_durable_event(event):
		return _failure(&"MALFORMED_DURABLE")

	var stream := StreamPeerBuffer.new()
	stream.big_endian = true
	stream.put_u16(MAGIC)
	stream.put_u8(int(event.event_kind))
	stream.put_u8(int(event.phase))
	stream.put_u16(int(event.id))
	stream.put_u8(int(event.generation))
	stream.put_u8(0)
	stream.put_u32(int(event.revision))
	stream.put_u32(int(event.tick))
	return { "ok": true, "packet": stream.data_array }


## Decodes one exact reliable lifecycle record and rejects trailing or reserved data.
func decode_durable(packet: PackedByteArray) -> Dictionary:
	if packet.size() != DURABLE_BYTES:
		return _failure(&"PACKET_SIZE")

	var stream := StreamPeerBuffer.new()
	stream.big_endian = true
	stream.data_array = packet
	if stream.get_u16() != MAGIC:
		return _failure(&"BAD_MAGIC")

	var event: Dictionary = {
		"event_kind": stream.get_u8(),
		"phase": stream.get_u8(),
		"id": stream.get_u16(),
		"generation": stream.get_u8(),
	}
	var reserved: int = stream.get_u8()
	event.revision = stream.get_u32()
	event.tick = stream.get_u32()
	if reserved != 0 or not _valid_durable_event(event):
		return _failure(&"MALFORMED_DURABLE")

	event.ok = true
	return event


## Returns the fixed planar world bounds after reserving the required growth margin.
static func safe_world_bounds() -> Rect2:
	var minimum := Vector2(
		POSITION_ORIGIN_X + POSITION_QUANTIZED_MIN * POSITION_STEP_METRES,
		POSITION_ORIGIN_Z + POSITION_QUANTIZED_MIN * POSITION_STEP_METRES,
	)
	var maximum := Vector2(
		POSITION_ORIGIN_X + POSITION_QUANTIZED_MAX * POSITION_STEP_METRES,
		POSITION_ORIGIN_Z + POSITION_QUANTIZED_MAX * POSITION_STEP_METRES,
	)
	return Rect2(
		minimum + Vector2.ONE * POSITION_MARGIN_METRES,
		maximum - minimum - Vector2.ONE * POSITION_MARGIN_METRES * 2.0,
	)


## Writes one measured row, clamping planar positions rather than allowing integer wrap.
func _put_movement_row(stream: StreamPeerBuffer, row: Dictionary) -> void:
	stream.put_u16(int(row.id))
	stream.put_u8(int(row.generation))
	stream.put_u8(int(row.kind))
	stream.put_u8(int(row.phase))
	stream.put_u8(int(row.flags))
	stream.put_u16(_signed_to_u16(_quantize_position(float(row.x), POSITION_ORIGIN_X)))
	stream.put_u16(_signed_to_u16(_quantize_position(float(row.z), POSITION_ORIGIN_Z)))
	stream.put_u16(_signed_to_u16(roundi(float(row.vx) * VELOCITY_SCALE)))
	stream.put_u16(_signed_to_u16(roundi(float(row.vz) * VELOCITY_SCALE)))
	stream.put_u16(posmod(roundi(float(row.yaw) * YAW_SCALE), 65_536))


## Reads one measured row without granting its phase field durable-writer authority.
func _get_movement_row(stream: StreamPeerBuffer) -> Dictionary:
	return {
		"id": stream.get_u16(),
		"generation": stream.get_u8(),
		"kind": stream.get_u8(),
		"phase": stream.get_u8(),
		"flags": stream.get_u8(),
		"x": POSITION_ORIGIN_X + float(_u16_to_signed(stream.get_u16())) * POSITION_STEP_METRES,
		"z": POSITION_ORIGIN_Z + float(_u16_to_signed(stream.get_u16())) * POSITION_STEP_METRES,
		"vx": float(_u16_to_signed(stream.get_u16())) / VELOCITY_SCALE,
		"vz": float(_u16_to_signed(stream.get_u16())) / VELOCITY_SCALE,
		"yaw": float(stream.get_u16()) / YAW_SCALE,
	}


## Accepts only the complete primitive movement row and finite representable velocity.
func _valid_movement_row(row: Dictionary) -> bool:
	if not _has_exact_fields(row, MOVEMENT_FIELDS):
		return false
	if not ReplicationIdentity.has_valid_entity_ref_fields(row):
		return false
	if (
		row.kind is not int
		or row.kind < 1
		or row.kind > 255
		or row.phase is not int
		or row.phase < 1
		or row.phase > 3
		or row.flags is not int
		or row.flags < 0
		or row.flags > 255
	):
		return false

	for field: String in ["x", "z", "vx", "vz", "yaw"]:
		var value: Variant = row[field]
		if (value is not float and value is not int) or not is_finite(float(value)):
			return false
	if absf(float(row.vx)) > 327.67 or absf(float(row.vz)) > 327.67:
		return false

	return true


## Accepts only S11's four lifecycle kinds and positive exact-width values.
func _valid_durable_event(event: Dictionary) -> bool:
	if not _has_exact_fields(event, DURABLE_FIELDS):
		return false

	return (
		event.event_kind is int
		and event.event_kind >= 1
		and event.event_kind <= 4
		and event.phase is int
		and event.phase >= 1
		and event.phase <= 3
		and ReplicationIdentity.has_valid_entity_ref_fields(event)
		and event.revision is int
		and event.revision > 0
		and event.revision <= 0xffff_ffff
		and event.tick is int
		and event.tick >= 0
		and event.tick <= 0xffff_ffff
	)


## Rejects missing and extension fields so schema changes require a new measured version.
func _has_exact_fields(value: Dictionary, expected: Array[String]) -> bool:
	if value.size() != expected.size():
		return false
	for field: String in expected:
		if not value.has(field):
			return false

	return true


## Quantizes around the fixed island origin and records every saturated coordinate.
func _quantize_position(value: float, origin: float) -> int:
	var quantized: int = roundi((value - origin) / POSITION_STEP_METRES)
	var clamped: int = clampi(quantized, POSITION_QUANTIZED_MIN, POSITION_QUANTIZED_MAX)
	if clamped != quantized:
		position_clamp_count += 1

	return clamped


## Preserves a signed quantized value in an unsigned wire field.
func _signed_to_u16(value: int) -> int:
	return value & 0xffff


## Recovers a signed quantized value from an unsigned wire field.
func _u16_to_signed(value: int) -> int:
	return value - 65_536 if value >= 32_768 else value


## Returns one normalized codec failure without partial decoded state.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
