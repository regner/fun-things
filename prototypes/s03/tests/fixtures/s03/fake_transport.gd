class_name S03FakeTransport
extends S03Transport

const READY_DELAY_S: float = 0.06

var obsolete_peers_closed: int = 0


## Delay a native completion beyond cancellation to exercise correlation.
func open_host(operation_id: int, _port: int) -> Error:
	_deliver_late(operation_id, epoch)
	return OK


## Correlate a late result with its original operation, never the current one.
func _deliver_late(operation_id: int, source_epoch: int) -> void:
	await tree.create_timer(READY_DELAY_S).timeout
	var candidate: OfflineMultiplayerPeer = OfflineMultiplayerPeer.new()
	# Canceled operations keep cleanup-only ownership even after provider replacement.
	if source_epoch != epoch:
		dispose_obsolete(candidate)
		return

	peer_ready.emit(operation_id, candidate)


## Record disposal of a stale result at the adapter boundary.
func dispose_obsolete(candidate: MultiplayerPeer) -> void:
	candidate.close()
	obsolete_peers_closed += 1
