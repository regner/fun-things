extends GutTest
## Protects the measured S11 row sizes, strict decoding, and island-centred position range.

const CITY_SCENE: PackedScene = preload("res://scenes/world/brackett_greybox/city.tscn")


## Keeps 148 full-cap rows in two 1,196-byte measured packets.
func test_full_cap_shape_and_roundtrip_match_s11_measurement() -> void:
	var codec := MeasuredReplicationCodec.new()
	var rows: Array[Dictionary] = []
	for entity_id: int in range(1, 149):
		rows.append(_row(entity_id, -12.345, 407.891))

	var encoded: Dictionary = codec.encode_movement(9, 42, rows)
	assert_true(encoded.ok)
	assert_eq(encoded.packets.size(), 2)
	assert_eq(encoded.packets[0].size(), 1196)
	assert_eq(encoded.packets[1].size(), 1196)

	var decoded: Dictionary = codec.decode_movement(encoded.packets[0])
	assert_true(decoded.ok)
	assert_eq(decoded.rows.size(), 74)
	assert_almost_eq(float(decoded.rows[0].x), -12.33565, 0.011)
	assert_almost_eq(float(decoded.rows[0].z), 407.88865, 0.011)
	assert_almost_eq(float(decoded.rows[0].vx), 1.23, 0.001)


## Saturates out-of-domain positions, records the clamp, and never wraps the island.
func test_position_overflow_clamps_and_is_counted() -> void:
	var codec := MeasuredReplicationCodec.new()
	var encoded: Dictionary = codec.encode_movement(1, 1, [_row(1, 5000.0, -5000.0)])
	var decoded: Dictionary = codec.decode_movement(encoded.packets[0])

	assert_true(encoded.ok)
	assert_eq(encoded.clamped_rows, 2)
	assert_eq(codec.position_clamp_count, 2)
	assert_almost_eq(
		float(decoded.rows[0].x),
		MeasuredReplicationCodec.POSITION_ORIGIN_X + 655.34,
		0.001,
	)
	assert_almost_eq(
		float(decoded.rows[0].z),
		MeasuredReplicationCodec.POSITION_ORIGIN_Z - 655.36,
		0.001,
	)


## Rejects malformed sizes, reserved bytes, schema extensions, and nonfinite values.
func test_malformed_payloads_fail_before_exposing_rows() -> void:
	var codec := MeasuredReplicationCodec.new()
	var encoded: Dictionary = codec.encode_movement(1, 1, [_row(1, 0.0, 0.0)])
	var packet: PackedByteArray = encoded.packets[0]

	assert_false(codec.decode_movement(packet.slice(0, packet.size() - 1)).ok)
	var reserved: PackedByteArray = packet.duplicate()
	reserved[11] = 1
	assert_false(codec.decode_movement(reserved).ok)
	var invalid_phase: PackedByteArray = packet.duplicate()
	invalid_phase[16] = 0
	assert_false(codec.decode_movement(invalid_phase).ok)

	var extra: Dictionary = _row(1, 0.0, 0.0)
	extra.health = 100
	assert_false(codec.encode_movement(1, 1, [extra]).ok)
	var nonfinite: Dictionary = _row(1, 0.0, 0.0)
	nonfinite.x = NAN
	assert_false(codec.encode_movement(1, 1, [nonfinite]).ok)


## Round-trips the exact 16-byte durable lifecycle shape and rejects trailing data.
func test_durable_shape_is_exact_and_bounded() -> void:
	var codec := MeasuredReplicationCodec.new()
	var encoded: Dictionary = (
		codec
		. encode_durable(
			{
				"event_kind": 3,
				"phase": 2,
				"id": 65,
				"generation": 1,
				"revision": 7,
				"tick": 90,
			}
		)
	)

	assert_true(encoded.ok)
	assert_eq(encoded.packet.size(), MeasuredReplicationCodec.DURABLE_BYTES)
	var decoded: Dictionary = codec.decode_durable(encoded.packet)
	assert_true(decoded.ok)
	assert_eq(decoded.id, 65)
	assert_eq(decoded.revision, 7)
	var trailing: PackedByteArray = encoded.packet.duplicate()
	trailing.append(0)
	assert_false(codec.decode_durable(trailing).ok)


## Verifies every saved Brackett node origin remains inside the codec's 50 m safe margin.
func test_saved_brackett_origins_fit_codec_range_with_margin() -> void:
	var city: Node3D = CITY_SCENE.instantiate()
	add_child_autofree(city)
	var safe_bounds: Rect2 = MeasuredReplicationCodec.safe_world_bounds()
	var checked: int = _check_saved_origins(city, safe_bounds)

	assert_gt(checked, 100)


## Builds one complete row without reusing codec quantization formulas as expectations.
func _row(entity_id: int, x: float, z: float) -> Dictionary:
	return {
		"id": entity_id,
		"generation": 1,
		"kind": 1,
		"phase": 1,
		"flags": 0,
		"x": x,
		"z": z,
		"vx": 1.234,
		"vz": -0.456,
		"yaw": 1.25,
	}


## Traverses the instantiated saved composition and asserts each planar global origin.
func _check_saved_origins(node: Node, safe_bounds: Rect2) -> int:
	var checked: int = 0
	if node is Node3D:
		checked = 1
		var origin: Vector3 = (node as Node3D).global_position
		assert_true(
			safe_bounds.has_point(Vector2(origin.x, origin.z)),
			"saved origin outside measured codec range: %s" % node.get_path(),
		)
	for child: Node in node.get_children():
		checked += _check_saved_origins(child, safe_bounds)

	return checked
