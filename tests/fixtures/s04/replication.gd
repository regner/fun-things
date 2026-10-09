class_name S04Replication
extends S03Replication
## Extends the existing S03 RPC writer with actual poses; provider/admission stay unchanged.

signal exit_result(reason: String)


## Sends complete refreshed actual movement rows within the original message budget.
func send_movement(peer_id: int, participants: Array, _tick: int, _sample: float) -> void:
	var actual: S04Match = match_state as S04Match
	var rows: Array = []
	for participant: int in participants:
		rows.append(actual.pose_for_entity(int(actual.bindings[participant].entity)))

	var envelope: Dictionary = { "session": actual.session_id, "revision": 1, "rows": rows }
	max_movement_bytes = maxi(max_movement_bytes, var_to_bytes(envelope).size())
	assert(max_movement_bytes <= MAX_HELD_BYTES)
	_movement.rpc_id(peer_id, envelope)


## Requests an authoritative seat exit without changing predicted client ownership locally.
func request_exit() -> void:
	_request_exit.rpc_id(1, match_state.session_id)


## Derives the participant from the RPC sender and returns the host-owned exit verdict.
@rpc("any_peer", "call_remote", "reliable", 0)
func _request_exit(session: String) -> void:
	if not multiplayer.is_server() or session != match_state.session_id:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	var participant: int = int(resolve_participant.call(peer_id))
	var reason: String = (match_state as S04Match).request_exit(participant)
	_exit_result.rpc_id(peer_id, reason)


## Publishes the verdict for presentation; rejection leaves prediction and seat untouched.
@rpc("authority", "call_remote", "reliable", 0)
func _exit_result(reason: String) -> void:
	exit_result.emit(reason)
