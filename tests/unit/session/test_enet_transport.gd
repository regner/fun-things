extends GutTest
## Verifies ENet endpoint and fixed-stream contracts without opening external sockets.

var _transport: ENetTransport


## Creates the production adapter so process-lifetime signal bindings are exercised.
func before_each() -> void:
	_transport = ENetTransport.new()
	add_child_autofree(_transport)


## Accepts bounded hostnames/IPs and rejects malformed or expired text shapes.
func test_parse_endpoint_owns_address_validation() -> void:
	var local: Dictionary = _transport.parse_endpoint("  LOCALHOST  ", 24_900)
	assert_true(local.ok)
	assert_eq(local.target.provider_id, &"enet")
	assert_eq(local.target.kind, &"TRANSPORT_READY")
	assert_eq(local.target.local_handle.address, "localhost")
	assert_eq(local.target.local_handle.port, 24_900)

	assert_true(_transport.parse_endpoint("127.0.0.1", 65_535).ok)
	assert_false(_transport.parse_endpoint("bad host", 24_900).ok)
	assert_false(_transport.parse_endpoint("-bad.example", 24_900).ok)
	assert_false(_transport.parse_endpoint(".localhost", 24_900).ok)
	assert_false(_transport.parse_endpoint("bad..example", 24_900).ok)
	assert_false(_transport.parse_endpoint("localhost.", 24_900).ok)
	assert_false(_transport.parse_endpoint("localhost", 0).ok)
	assert_false(_transport.parse_endpoint("localhost", 65_536).ok)

	assert_true(_transport.close(1).ok)
	var expired: Dictionary = _transport.open_client(2, local.target)
	assert_false(expired.ok)
	assert_eq(expired.failure.code, &"TARGET_EXPIRED")


## Publishes four distinct channels with the ratified delivery and payload profile.
func test_capabilities_match_required_stream_profile() -> void:
	var capabilities: Dictionary = _transport.capabilities()
	assert_true(capabilities.available)
	assert_eq(capabilities.identity_assurance, &"NONE")
	assert_false(capabilities.native_receive_packet_limit_available)
	assert_eq(capabilities.max_receive_packet_bytes, 0)
	assert_eq(capabilities.max_auth_payload_bytes, SessionService.MAX_HANDSHAKE_LOGICAL_BYTES)
	assert_eq(capabilities.streams.size(), 4)
	assert_eq(capabilities.streams[0].delivery, &"RELIABLE_ORDERED")
	assert_eq(capabilities.streams[1].max_logical_payload_bytes, 16 * 1024)
	assert_eq(capabilities.streams[2].delivery, &"UNRELIABLE_ORDERED")
	assert_eq(capabilities.streams[2].max_logical_payload_bytes, 1200)
	assert_eq(capabilities.streams[3].queue_policy, &"REPLACEABLE_LOSSY")
