class_name S03RReplication
extends S03Replication
## Extends the existing S03 RPC writer with actual poses; provider/admission stay unchanged.


## Sends complete refreshed actual movement rows within the original message budget.
func send_movement(peer_id: int, participants: Array, _tick: int, _sample: float) -> void:
	var actual: S03RMatch = match_state as S03RMatch
	var rows: Array = []
	for participant: int in participants:
		rows.append(actual.pose_for_entity(int(actual.bindings[participant].entity)))

	var envelope: Dictionary = { "session": actual.session_id, "revision": 1, "rows": rows }
	max_movement_bytes = maxi(max_movement_bytes, var_to_bytes(envelope).size())
	assert(max_movement_bytes <= MAX_HELD_BYTES)
	_movement.rpc_id(peer_id, envelope)
