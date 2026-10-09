class_name ReplicationIdentity
extends RefCounted
## Validates session, participant, match, and entity identities at replication boundaries.

const SESSION_BYTES: int = 16
const SESSION_HEX_LENGTH: int = SESSION_BYTES * 2
const MAX_WIRE_ENTITY_ID: int = 65_535
const MAX_WIRE_GENERATION: int = 255


## Creates one cryptographically random session identity in the canonical wire spelling.
static func create_session_id() -> String:
	return Crypto.new().generate_random_bytes(SESSION_BYTES).hex_encode()


## Accepts only a lowercase 128-bit session identity.
static func is_valid_session_id(session_id: Variant) -> bool:
	if session_id is not String or session_id.length() != SESSION_HEX_LENGTH:
		return false

	for character: String in session_id:
		var code: int = character.unicode_at(0)
		var is_digit: bool = code >= 48 and code <= 57
		var is_lower_hex: bool = code >= 97 and code <= 102
		if not is_digit and not is_lower_hex:
			return false

	return true


## Builds one bounded entity reference accepted by the measured movement codec.
static func entity_ref(entity_id: int, generation: int) -> Dictionary:
	if not is_valid_entity_ref({ "id": entity_id, "generation": generation }):
		return {}

	return { "id": entity_id, "generation": generation }


## Validates an exact entity-reference shape and its positive wire ranges.
static func is_valid_entity_ref(value: Variant) -> bool:
	return value is Dictionary and value.size() == 2 and has_valid_entity_ref_fields(value)


## Validates entity-reference fields embedded in a larger fixed record.
static func has_valid_entity_ref_fields(value: Variant) -> bool:
	if value is not Dictionary or not value.has("id") or not value.has("generation"):
		return false

	var entity_id: Variant = value.id
	var generation: Variant = value.generation
	return (
		entity_id is int
		and generation is int
		and entity_id > 0
		and entity_id <= MAX_WIRE_ENTITY_ID
		and generation > 0
		and generation <= MAX_WIRE_GENERATION
	)


## Validates the session and revision fence carried beside a fixed codec payload.
static func is_current_envelope(
	session_id: Variant,
	match_revision: Variant,
	expected_session_id: String,
	expected_match_revision: int,
) -> bool:
	return (
		is_valid_session_id(session_id)
		and session_id == expected_session_id
		and match_revision is int
		and match_revision > 0
		and match_revision == expected_match_revision
	)
