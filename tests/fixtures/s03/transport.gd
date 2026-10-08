class_name S03Transport
extends RefCounted

signal peer_ready(operation_id: int, peer: MultiplayerPeer)
signal closed(operation_id: int)

const CHANNEL_COUNT: int = 4
const CLOSE_DELAY_S: float = 0.02

var tree: SceneTree
var peer: MultiplayerPeer
var epoch: int = 0


## Supply the lifetime used for asynchronous close completion.
func _init(scene_tree: SceneTree = null) -> void:
	tree = scene_tree


## Report the modes exercised by the ENet fixture.
func capabilities() -> Dictionary:
	return {"available": true, "reliable": true, "unreliable_ordered": true,
		"channel_count": CHANNEL_COUNT}


## Validate an adapter-local endpoint; gameplay never receives its native peer.
func parse_endpoint(address: String, port: int) -> Dictionary:
	if address.is_empty() or address.to_utf8_buffer().size() > 255:
		return {}

	if port < 1 or port > 65_535:
		return {}

	return { "transport": "ENET", "address": address, "port": port, "epoch": epoch }


## Open a loopback listen server with bounded native peers.
func open_host(operation_id: int, port: int) -> Error:
	var candidate: ENetMultiplayerPeer = ENetMultiplayerPeer.new()
	candidate.set_bind_ip("127.0.0.1")
	var error: Error = candidate.create_server(port, 3, CHANNEL_COUNT)
	if error != OK:
		candidate.close()
		return error

	# Pinned create_server passes its channel count as incoming bandwidth (6 B/s here), which
	# collapses each client's unreliable throttle; restore the intended unlimited bandwidth.
	candidate.host.bandwidth_limit(0, 0)
	peer = candidate
	peer_ready.emit(operation_id, peer)
	return OK


## Open a client only for a current adapter-owned target.
func open_client(operation_id: int, target: Dictionary) -> Error:
	if target.get("epoch", -1) != epoch or target.get("transport") != "ENET":
		return ERR_INVALID_PARAMETER

	var candidate: ENetMultiplayerPeer = ENetMultiplayerPeer.new()
	var error: Error = candidate.create_client(target.address, target.port, CHANNEL_COUNT)
	if error != OK:
		candidate.close()
		return error

	peer = candidate
	peer_ready.emit(operation_id, peer)
	return OK


## Release native resources before asynchronously confirming cleanup.
func close(operation_id: int) -> void:
	epoch += 1
	if peer != null:
		peer.close()
		peer = null

	await tree.create_timer(CLOSE_DELAY_S).timeout
	closed.emit(operation_id)
