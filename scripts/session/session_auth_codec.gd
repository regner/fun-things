class_name SessionAuthCodec
extends RefCounted
## Encodes and validates the fixed raw SceneMultiplayer authentication protocol.

const MAX_ID_BYTES: int = 128
const MAX_HANDSHAKE_LOGICAL_BYTES: int = 512
const HANDSHAKE_HEADER_BYTES: int = 18
const ADMISSION_FAILURE_BYTES: int = 11
const ADMISSION_SUCCESS_BYTES: int = 43
const MAX_WIRE_INTEGER: int = 2_147_483_647
const STATUS_ACCEPTED: int = 1
const CODE_NONE: int = 0
const CODE_INCOMPATIBLE: int = 1
const CODE_CONTENT_INVALID: int = 2
const CODE_FULL: int = 3


## Encodes an operation and three bounded UTF-8 identities into the auth wire shape.
static func encode_handshake(
	client_operation_id: int,
	compatibility: Dictionary,
) -> PackedByteArray:
	var content: PackedByteArray = String(compatibility.content_id).to_utf8_buffer()
	var district: PackedByteArray = String(compatibility.district_id).to_utf8_buffer()
	var definitions: PackedByteArray = String(compatibility.definition_set_id).to_utf8_buffer()
	var payload := PackedByteArray()
	payload.resize(HANDSHAKE_HEADER_BYTES + content.size() + district.size() + definitions.size())
	payload.encode_u32(0, client_operation_id)
	payload.encode_u32(4, compatibility.protocol_version)
	payload.encode_u32(8, compatibility.topology_revision)
	payload.encode_u16(12, content.size())
	payload.encode_u16(14, district.size())
	payload.encode_u16(16, definitions.size())
	var write_offset: int = HANDSHAKE_HEADER_BYTES
	for field: PackedByteArray in [content, district, definitions]:
		for byte: int in field:
			payload[write_offset] = byte
			write_offset += 1

	return payload


## Decodes exact bounded auth bytes, validating UTF-8 before StringName allocation.
static func decode_handshake(payload: PackedByteArray) -> Dictionary:
	if payload.size() < HANDSHAKE_HEADER_BYTES or payload.size() > MAX_HANDSHAKE_LOGICAL_BYTES:
		return {}

	var field_sizes: Array[int] = [
		payload.decode_u16(12),
		payload.decode_u16(14),
		payload.decode_u16(16),
	]
	for field_size: int in field_sizes:
		if field_size < 1 or field_size > MAX_ID_BYTES:
			return {}
	if payload.size() != HANDSHAKE_HEADER_BYTES + _sum(field_sizes):
		return {}

	var fields: Array[String] = _decode_fields(payload, field_sizes)
	if fields.is_empty():
		return {}

	var client_operation_id: int = payload.decode_u32(0)
	var protocol_version: int = payload.decode_u32(4)
	var topology_revision: int = payload.decode_u32(8)
	if not _valid_wire_integers(client_operation_id, protocol_version, topology_revision):
		return {}

	return {
		"client_operation_id": client_operation_id,
		"compatibility": {
			"protocol_version": protocol_version,
			"content_id": fields[0],
			"district_id": StringName(fields[1]),
			"topology_revision": topology_revision,
			"definition_set_id": fields[2],
		},
	}


## Encodes one fixed-size authentication verdict without Variant fields.
static func encode_verdict(
	client_operation_id: int,
	failure_code: StringName,
	participant_id: int,
	capacity: int,
	session_id: String,
) -> PackedByteArray:
	var accepted: bool = failure_code == &""
	var payload := PackedByteArray()
	payload.resize(ADMISSION_SUCCESS_BYTES if accepted else ADMISSION_FAILURE_BYTES)
	payload.encode_u32(0, client_operation_id)
	payload[4] = STATUS_ACCEPTED if accepted else 0
	payload[5] = _code_to_wire(failure_code)
	payload.encode_u32(6, participant_id)
	payload[10] = capacity
	if accepted:
		var session_bytes: PackedByteArray = session_id.to_utf8_buffer()
		for index: int in session_bytes.size():
			payload[11 + index] = session_bytes[index]

	return payload


## Decodes one exact authentication verdict and rejects malformed status combinations.
static func decode_verdict(payload: PackedByteArray) -> Dictionary:
	if not _valid_verdict_shape(payload):
		return {}

	var admitted: bool = payload[4] == STATUS_ACCEPTED
	var failure_code: StringName = _code_from_wire(payload[5])

	var session_id: String = ""
	if admitted:
		var session_raw: PackedByteArray = payload.slice(11, ADMISSION_SUCCESS_BYTES)
		session_id = session_raw.get_string_from_utf8()
		if session_id.to_utf8_buffer() != session_raw:
			return {}

	return {
		"client_operation_id": payload.decode_u32(0),
		"admitted": admitted,
		"failure_code": failure_code,
		"participant_id": payload.decode_u32(6),
		"capacity": payload[10],
		"session_id": session_id,
	}


## Validates fixed verdict lengths, status, and the finite code vocabulary.
static func _valid_verdict_shape(payload: PackedByteArray) -> bool:
	if payload.size() not in [ADMISSION_FAILURE_BYTES, ADMISSION_SUCCESS_BYTES]:
		return false
	if payload[4] not in [0, STATUS_ACCEPTED]:
		return false

	var admitted: bool = payload[4] == STATUS_ACCEPTED
	var known_rejection: bool = payload[5] in [
		CODE_INCOMPATIBLE,
		CODE_CONTENT_INVALID,
		CODE_FULL,
	]
	return (
		(admitted and payload[5] == CODE_NONE and payload.size() == ADMISSION_SUCCESS_BYTES)
		or (not admitted and known_rejection and payload.size() == ADMISSION_FAILURE_BYTES)
	)


## Decodes three exact UTF-8 fields after their raw lengths have passed bounds.
static func _decode_fields(payload: PackedByteArray, field_sizes: Array[int]) -> Array[String]:
	var fields: Array[String] = []
	var read_offset: int = HANDSHAKE_HEADER_BYTES
	for field_size: int in field_sizes:
		var raw: PackedByteArray = payload.slice(read_offset, read_offset + field_size)
		var decoded: String = raw.get_string_from_utf8()
		if decoded.is_empty() or decoded.to_utf8_buffer() != raw:
			return []

		fields.append(decoded)
		read_offset += field_size

	return fields


## Sums the fixed three wire field lengths.
static func _sum(values: Array[int]) -> int:
	var total: int = 0
	for value: int in values:
		total += value

	return total


## Validates integer ranges before compatibility state is allocated.
static func _valid_wire_integers(
	client_operation_id: int,
	protocol_version: int,
	topology_revision: int,
) -> bool:
	return (
		client_operation_id >= 1
		and client_operation_id <= MAX_WIRE_INTEGER
		and protocol_version >= 1
		and protocol_version <= MAX_WIRE_INTEGER
		and topology_revision >= 0
		and topology_revision <= MAX_WIRE_INTEGER
	)


## Converts public rejection codes to one-byte authentication values.
static func _code_to_wire(failure_code: StringName) -> int:
	match failure_code:
		&"INCOMPATIBLE":
			return CODE_INCOMPATIBLE
		&"CONTENT_INVALID":
			return CODE_CONTENT_INVALID
		&"FULL":
			return CODE_FULL
		_:
			return CODE_NONE


## Decodes only finite admission rejection values.
static func _code_from_wire(code: int) -> StringName:
	match code:
		CODE_INCOMPATIBLE:
			return &"INCOMPATIBLE"
		CODE_CONTENT_INVALID:
			return &"CONTENT_INVALID"
		CODE_FULL:
			return &"FULL"
		_:
			return &""
