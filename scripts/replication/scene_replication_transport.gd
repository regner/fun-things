class_name SceneReplicationTransport
extends ReplicationTransport
## Adapts admission output to one saved Match replication node's reliable RPC boundary.

var _root: MatchReplication


## Binds the match-local RPC owner without taking authority over replicated state.
func _init(root: MatchReplication) -> void:
	_root = root


## Sends immutable baseline metadata followed by independently bounded chunks.
func send_baseline(
	native_peer_id: int,
	metadata: Dictionary,
	packets: Array[PackedByteArray],
) -> bool:
	return _root.send_baseline_to_peer(native_peer_id, metadata, packets)


## Sends one ordered lifecycle record to an admitted or synchronizing peer.
func send_durable(native_peer_id: int, packet: PackedByteArray) -> bool:
	return _root.send_durable_to_peer(native_peer_id, packet)


## Sends one complete lifecycle snapshot before its matching handoff marker.
func send_lifecycle(native_peer_id: int, lifecycle_revision: int) -> bool:
	return _root.send_lifecycle_to_peer(native_peer_id, lifecycle_revision)


## Sends the reliable cut marker after journal and lifecycle state through both revisions.
func send_handoff(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
	lifecycle_revision: int,
) -> bool:
	return _root.send_handoff_to_peer(
		native_peer_id,
		baseline_id,
		commit_revision,
		lifecycle_revision,
	)


## Opens input only after the current durable and lifecycle handoff acknowledgement.
func send_grant(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
	lifecycle_revision: int,
) -> bool:
	return _root.send_grant_to_peer(
		native_peer_id,
		baseline_id,
		commit_revision,
		lifecycle_revision,
	)


## Supersedes one old-match transfer before a reset baseline begins.
func send_reset_begin(native_peer_id: int, match_revision: int) -> bool:
	return _root.send_reset_begin_to_peer(native_peer_id, match_revision)


## Disconnects one failed admission without affecting host simulation or other peers.
func abort_admission(native_peer_id: int, failure_code: StringName) -> void:
	_root.abort_peer(native_peer_id, failure_code)
