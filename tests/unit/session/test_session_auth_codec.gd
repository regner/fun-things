extends GutTest
## Verifies raw authentication bytes are bounded and strictly decoded before admission.


## Proves a valid fixed handshake round-trips without Variant decoding.
func test_valid_handshake_round_trips() -> void:
	var payload: PackedByteArray = SessionAuthCodec.encode_handshake(7, _compatibility())
	var decoded: Dictionary = SessionAuthCodec.decode_handshake(payload)
	assert_eq(decoded.client_operation_id, 7)
	assert_eq(decoded.compatibility, _compatibility())


## Proves both the application cap and per-field cap reject raw authentication bytes.
func test_oversized_handshakes_are_rejected() -> void:
	var packet := PackedByteArray()
	packet.resize(70 * 1024)
	assert_true(SessionAuthCodec.decode_handshake(packet).is_empty())

	var compatibility: Dictionary = _compatibility()
	compatibility.content_id = "x".repeat(SessionAuthCodec.MAX_ID_BYTES + 1)
	assert_true(
		SessionAuthCodec.decode_handshake(
			SessionAuthCodec.encode_handshake(1, compatibility)
		).is_empty()
	)


## Proves malformed UTF-8 is rejected before a StringName field is allocated.
func test_invalid_utf8_is_rejected() -> void:
	var payload: PackedByteArray = SessionAuthCodec.encode_handshake(1, _compatibility())
	payload[SessionAuthCodec.HANDSHAKE_HEADER_BYTES] = 0xff
	assert_true(SessionAuthCodec.decode_handshake(payload).is_empty())


## Proves admission verdicts have fixed sizes and reject unknown failure codes.
func test_admission_verdicts_round_trip() -> void:
	var accepted: Dictionary = SessionAuthCodec.decode_verdict(
		SessionAuthCodec.encode_verdict(9, &"", 2, 4, "0123456789abcdef0123456789abcdef")
	)
	assert_true(accepted.admitted)
	assert_eq(accepted.participant_id, 2)

	var rejected: Dictionary = SessionAuthCodec.decode_verdict(
		SessionAuthCodec.encode_verdict(9, &"FULL", 0, 4, "")
	)
	assert_false(rejected.admitted)
	assert_eq(rejected.failure_code, &"FULL")

	var malformed: PackedByteArray = SessionAuthCodec.encode_verdict(9, &"FULL", 0, 4, "")
	malformed[5] = 255
	assert_true(SessionAuthCodec.decode_verdict(malformed).is_empty())


## Returns one canonical compatibility record for codec expectations.
func _compatibility() -> Dictionary:
	return {
		"protocol_version": 4,
		"content_id": "development",
		"district_id": &"brackett_island",
		"topology_revision": 0,
		"definition_set_id": "development",
	}
