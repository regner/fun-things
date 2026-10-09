extends SceneTree

const CodecScript: Script = preload("res://tests/fixtures/s11/snapshot_codec.gd")
const PolicyScript: Script = preload("res://tests/fixtures/s11/population_policy.gd")


## Exercise codec and population policy through their public APIs with independent outcomes.
func _initialize() -> void:
	var failures: Array[String] = []
	_check_codec(failures)
	_check_population_policy(failures)
	print("S11_PROBE " + JSON.stringify({ "ok": failures.is_empty(), "failures": failures }))
	quit(0 if failures.is_empty() else 1)


## Check chunk bounds, quantization, malformed rejection and lifecycle roundtrip.
func _check_codec(failures: Array[String]) -> void:
	var codec: S11SnapshotCodec = CodecScript.new()
	var rows: Array[Dictionary] = []
	for entity_id: int in range(1, 149):
		(
			rows
			. append(
				{
					"id": entity_id,
					"generation": 1,
					"kind": 1,
					"phase": 1,
					"flags": 0,
					"x": -12.345,
					"z": 7.891,
					"vx": 1.234,
					"vz": -0.456,
					"yaw": 1.25,
				}
			)
		)

	var packets: Array[PackedByteArray] = codec.encode(9, 42, rows)
	if packets.size() != 2 or packets[0].size() > 1200 or packets[1].size() > 1200:
		failures.append("codec did not split 148 rows below 1200 bytes")
	var decoded_rows: Array = []
	for packet: PackedByteArray in packets:
		var decoded: Dictionary = codec.decode(packet)
		if decoded.is_empty() or decoded.sequence != 9 or decoded.tick != 42:
			failures.append("snapshot header roundtrip failed")
			return
		decoded_rows.append_array(decoded.rows)
	if decoded_rows.size() != 148:
		failures.append("snapshot row count changed")
	elif (
		absf(float(decoded_rows[0].x) - -12.35) > 0.001
		or absf(float(decoded_rows[0].vx) - 1.23) > 0.001
	):
		failures.append("snapshot quantization was not centimetre bounded")

	var malformed: PackedByteArray = packets[0].slice(0, packets[0].size() - 1)
	if not codec.decode(malformed).is_empty():
		failures.append("truncated snapshot was accepted")
	var lifecycle: Dictionary = codec.decode_lifecycle(codec.encode_lifecycle(
		{ "event_kind": 4, "id": 65, "generation": 1, "phase": 2, "revision": 7, "tick": 90 }
	))
	if lifecycle.get("id") != 65 or lifecycle.get("revision") != 7 or lifecycle.get("phase") != 2:
		failures.append("lifecycle transaction roundtrip failed")


## Check caps, all-player view exclusion, shared clearance reservation and reset.
func _check_population_policy(failures: Array[String]) -> void:
	var policy: S11PopulationPolicy = PolicyScript.new()
	policy.reset()
	var candidates: Array[Dictionary] = [
		{ "position": Vector2(5.0, 0.0) },
		{ "position": Vector2(50.0, 0.0) },
		{ "position": Vector2(80.0, 0.0) },
	]
	var players: Array[Vector2] = [Vector2.ZERO, Vector2(100.0, 0.0)]
	var first: Dictionary = policy.reserve_replenishment("pedestrian", candidates, players, 1.0)
	if first.is_empty() or first.position != Vector2(50.0, 0.0):
		failures.append("replenishment did not choose an out-of-view candidate")
		return

	var blocked: Array[Dictionary] = [{ "position": Vector2(51.0, 0.0) }]
	if not policy.reserve_replenishment("car", blocked, players, 1.5).is_empty():
		failures.append("clearance allowed overlapping reservations")
	if not policy.commit(first) or int(policy.counts.pedestrian) != 1:
		failures.append("reservation commit did not own the count")

	policy.counts.pedestrian = S11PopulationPolicy.PEDESTRIAN_CAP
	if policy.can_add("pedestrian"):
		failures.append("pedestrian cap was exceeded")
	policy.reset()
	if not policy.reservations.is_empty() or int(policy.counts.pedestrian) != 0:
		failures.append("reset did not clear population state")
