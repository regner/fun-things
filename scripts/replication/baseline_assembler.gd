class_name BaselineAssembler
extends RefCounted
## Collects one bounded immutable baseline and exposes rows only after full validation.

const MAX_BASELINE_BYTES: int = 1024 * 1024
const MAX_BASELINE_CHUNKS: int = 128

var _codec: MeasuredReplicationCodec
var _metadata: Dictionary = {}
var _packets_by_index: Dictionary[int, PackedByteArray] = {}
var _received_bytes: int = 0


## Binds a fresh expected transaction without allocating from untrusted chunk declarations.
func begin(codec: MeasuredReplicationCodec, metadata: Dictionary) -> Dictionary:
	if not _valid_metadata(metadata):
		return _failure(&"MALFORMED_BASELINE")

	_codec = codec
	_metadata = metadata.duplicate(true)
	_packets_by_index.clear()
	_received_bytes = 0
	return { "ok": true }


## Accepts one current chunk, ignoring only byte-identical duplicates.
func receive(
	session_id: String,
	match_revision: int,
	baseline_id: int,
	packet: PackedByteArray,
) -> Dictionary:
	if _metadata.is_empty() or not _matches_attempt(session_id, match_revision, baseline_id):
		return _failure(&"STALE_BASELINE")

	var decoded: Dictionary = _codec.decode_movement(packet)
	if not decoded.ok:
		return decoded
	if decoded.chunk_count != _metadata.chunk_count:
		return _failure(&"MALFORMED_BASELINE")

	var chunk_index: int = decoded.chunk_index
	if _packets_by_index.has(chunk_index):
		if _packets_by_index[chunk_index] != packet:
			return _failure(&"MALFORMED_BASELINE")

		return { "ok": true, "duplicate": true, "complete": is_complete() }
	if _received_bytes + packet.size() > MAX_BASELINE_BYTES:
		return _failure(&"STATE_LIMIT")

	_packets_by_index[chunk_index] = packet.duplicate()
	_received_bytes += packet.size()
	return { "ok": true, "duplicate": false, "complete": is_complete() }


## Reports completeness without installing a partial transaction.
func is_complete() -> bool:
	return (
		not _metadata.is_empty()
		and _packets_by_index.size() == int(_metadata.chunk_count)
		and _received_bytes == int(_metadata.total_bytes)
	)


## Verifies checksum and cardinality before returning the immutable current-state rows.
func finish() -> Dictionary:
	if not is_complete():
		return _failure(&"INCOMPLETE_BASELINE")

	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		return _failure(&"CHECKSUM_FAILED")

	var rows: Array[Dictionary] = []
	for chunk_index: int in range(int(_metadata.chunk_count)):
		var packet: PackedByteArray = _packets_by_index[chunk_index]
		context.update(packet)
		var decoded: Dictionary = _codec.decode_movement(packet)
		if not decoded.ok:
			return decoded
		rows.append_array(decoded.rows)
	if context.finish().hex_encode() != String(_metadata.checksum):
		return _failure(&"CHECKSUM_FAILED")
	if rows.size() != int(_metadata.row_count):
		return _failure(&"MALFORMED_BASELINE")

	return {
		"ok": true,
		"session_id": _metadata.session_id,
		"match_revision": _metadata.match_revision,
		"baseline_id": _metadata.baseline_id,
		"cut_tick": _metadata.cut_tick,
		"cut_durable_revision": _metadata.cut_durable_revision,
		"rows": rows,
	}


## Checks transaction bounds before any packet-sized receive allocation.
func _valid_metadata(metadata: Dictionary) -> bool:
	var required: Array[String] = [
		"session_id",
		"match_revision",
		"baseline_id",
		"cut_tick",
		"cut_durable_revision",
		"chunk_count",
		"total_bytes",
		"row_count",
		"checksum",
	]
	for field: String in required:
		if not metadata.has(field):
			return false

	return (
		ReplicationIdentity.is_valid_session_id(metadata.session_id)
		and metadata.match_revision is int
		and metadata.match_revision > 0
		and metadata.baseline_id is int
		and metadata.baseline_id > 0
		and metadata.cut_tick is int
		and metadata.cut_tick >= 0
		and metadata.cut_durable_revision is int
		and metadata.cut_durable_revision >= 0
		and metadata.chunk_count is int
		and metadata.chunk_count > 0
		and metadata.chunk_count <= MAX_BASELINE_CHUNKS
		and metadata.total_bytes is int
		and metadata.total_bytes > 0
		and metadata.total_bytes <= MAX_BASELINE_BYTES
		and metadata.row_count is int
		and metadata.row_count >= 0
		and metadata.checksum is String
		and metadata.checksum.length() == 64
	)


## Fences chunks from obsolete session, match, or hydration attempts.
func _matches_attempt(session_id: String, match_revision: int, baseline_id: int) -> bool:
	return (
		session_id == _metadata.session_id
		and match_revision == _metadata.match_revision
		and baseline_id == _metadata.baseline_id
	)


## Returns one normalized transfer failure without partial rows.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
