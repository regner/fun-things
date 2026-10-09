class_name S05Session
extends S03Session
## Adds only lifetime shooter-slot admission fencing to the unchanged S03 session API.


## Reserves at most four lifetime shooter identities including pending initial joins.
@rpc("any_peer", "call_remote", "reliable", 0)
func _hello(client_operation: int, protocol: int, content: String) -> void:
	if not is_host or phase != "ACTIVE" or protocol != PROTOCOL or content != CONTENT:
		return

	var peer: int = multiplayer.get_remote_sender_id()
	if peer <= 0 or client_operation <= 0:
		return

	var reserved: int = match_state.next_entity_id
	for row: Dictionary in roster.values():
		if row.phase == "LOADING":
			reserved += 1

	if not roster.has(peer) and reserved >= S05Damage.MAX_SHOOTERS:
		multiplayer.multiplayer_peer.disconnect_peer(peer)
		return

	super._hello(client_operation, protocol, content)
