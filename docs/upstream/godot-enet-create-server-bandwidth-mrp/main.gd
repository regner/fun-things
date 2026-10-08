extends SceneTree
## Reproduces the create_server channel/bandwidth argument mix-up on loopback.

const CHANNEL_COUNT: int = 4
const MAX_CLIENTS: int = 3
const PACKET_BYTES: int = 512
const PORT: int = 24_999
const REPORT_INTERVAL_S: float = 0.5
const RUN_DURATION_S: float = 2.25

var server: ENetMultiplayerPeer = ENetMultiplayerPeer.new()
var client: ENetMultiplayerPeer = ENetMultiplayerPeer.new()
var elapsed_s: float = 0.0
var next_report_s: float = REPORT_INTERVAL_S
var sent_packets: int = 0
var received_packets: int = 0
var minimum_throttle_limit: int = ENetPacketPeer.PACKET_THROTTLE_SCALE
var use_workaround: bool = false
var payload: PackedByteArray


## Polls both peers and sends enough unreliable data to keep the bad limit observable.
func _process(delta: float) -> bool:
	elapsed_s += delta
	server.poll()
	client.poll()
	_drain_server_packets()

	if client.get_connection_status() == MultiplayerPeer.CONNECTION_CONNECTED:
		client.transfer_mode = MultiplayerPeer.TRANSFER_MODE_UNRELIABLE
		client.set_target_peer(1)
		var send_error: Error = client.put_packet(payload)
		if send_error != OK:
			printerr("MRP ERROR: put_packet failed")
			quit(1)
			return true
		sent_packets += 1
		_sample_throttle_limit()

	if elapsed_s >= next_report_s:
		next_report_s += REPORT_INTERVAL_S
		_print_sample()

	if elapsed_s < RUN_DURATION_S:
		return false

	_print_result()
	server.close()
	client.close()
	return true


## Creates both loopback peers, optionally restoring unlimited host bandwidth.
func _initialize() -> void:
	use_workaround = "--workaround" in OS.get_cmdline_user_args()
	payload.resize(PACKET_BYTES)
	payload.fill(1)

	var server_error: Error = server.create_server(PORT, MAX_CLIENTS, CHANNEL_COUNT)
	if server_error != OK:
		_fail("create_server failed: %s" % error_string(server_error))
		return

	if use_workaround:
		server.host.bandwidth_limit(0, 0)

	var client_error: Error = client.create_client("127.0.0.1", PORT, CHANNEL_COUNT)
	if client_error != OK:
		_fail("create_client failed: %s" % error_string(client_error))
		return

	print(
		"START mode=%s channels=%d workaround_before_connect=%s"
		% [_mode_name(), CHANNEL_COUNT, use_workaround]
	)


## Removes received payloads so the server queue cannot affect the observation.
func _drain_server_packets() -> void:
	while server.get_available_packet_count() > 0:
		server.get_packet()
		received_packets += 1


## Records the lowest client-side limit observed for the server peer.
func _sample_throttle_limit() -> void:
	var host_peer: ENetPacketPeer = client.get_peer(1)
	if host_peer == null:
		return

	var limit: int = int(
		host_peer.get_statistic(ENetPacketPeer.PEER_PACKET_THROTTLE_LIMIT)
	)
	minimum_throttle_limit = mini(minimum_throttle_limit, limit)


## Prints one human-readable live sample.
func _print_sample() -> void:
	var host_peer: ENetPacketPeer = client.get_peer(1)
	var limit: int = -1
	if host_peer != null:
		limit = int(host_peer.get_statistic(ENetPacketPeer.PEER_PACKET_THROTTLE_LIMIT))

	print(
		"SAMPLE elapsed_s=%.2f throttle_limit=%d/%d sent=%d received=%d"
		% [
			elapsed_s,
			limit,
			ENetPacketPeer.PACKET_THROTTLE_SCALE,
			sent_packets,
			received_packets,
		]
	)


## Prints the stable result line quoted by the write-up.
func _print_result() -> void:
	var host_peer: ENetPacketPeer = client.get_peer(1)
	var final_limit: int = -1
	if host_peer != null:
		final_limit = int(host_peer.get_statistic(ENetPacketPeer.PEER_PACKET_THROTTLE_LIMIT))

	print(
		(
			"RESULT mode=%s elapsed_s=%.2f minimum_limit=%d final_limit=%d scale=%d "
			+ "sent=%d received=%d"
		)
		% [
			_mode_name(),
			elapsed_s,
			minimum_throttle_limit,
			final_limit,
			ENetPacketPeer.PACKET_THROTTLE_SCALE,
			sent_packets,
			received_packets,
		]
	)


## Returns a concise label for retained output comparison.
func _mode_name() -> String:
	return "workaround" if use_workaround else "defect"


## Reports startup/runtime failures and assigns a failing process exit code.
func _fail(message: String) -> void:
	printerr("MRP ERROR: %s" % message)
	quit(1)
