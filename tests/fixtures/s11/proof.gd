extends Node  # gdstyle:ignore=quality/max-class-variables

const TransportScript: Script = preload("res://tests/fixtures/s03/transport.gd")
const CodecScript: Script = preload("res://tests/fixtures/s11/snapshot_codec.gd")
const PEDESTRIANS: int = 64
const CARS: int = 32
const PLAYERS: int = 4
const ROCKETS: int = 16
const WRECKS: int = 16
const DEAD_PEDESTRIANS: int = 16
const ENTITY_COUNT: int = PEDESTRIANS + CARS + PLAYERS + ROCKETS + WRECKS + DEAD_PEDESTRIANS
const SNAPSHOT_INTERVAL_TICKS: int = 4
const INTERPOLATION_DELAY_TICKS: float = 12.0
const MAX_EXTRAPOLATION_TICKS: float = 12.0
const RUN_TICKS: int = 660
const FINISH_DELAY_TICKS: int = 900

var codec: S11SnapshotCodec = CodecScript.new()
var transport: S03Transport
var role: String = ""
var port: int = 0
var expected_clients: int = 1
var connected_peers: Array[int] = []
var baseline_acks: Dictionary = {}
var running: bool = false
var run_tick: int = 0
var finish_tick: int = -1
var snapshot_sequence: int = 0
var snapshot_subset: int = 0
var lifecycle_revision: int = 0
var lifecycle_generation: Dictionary = {}
var lifecycle_phase: Dictionary = {}
var samples: Dictionary = {}
var displayed: Dictionary = {}
var encode_usec: Array[int] = []
var decode_usec: Array[int] = []
var encoded_payload_bytes: int = 0
var encoded_rows: int = 0
var baseline_payload_bytes: int = 0
var snapshot_packets: int = 0
var max_packet_bytes: int = 0
var snapshot_rows_received: int = 0
var extrapolation_frames: int = 0
var interpolation_frames: int = 0
var jitter_samples_m: Array[float] = []
var lifecycle_events_received: Array[String] = []
var stale_rows_rejected: int = 0
var started_ms: int = 0
var result_emitted_ms: int = 0


## Parse the bounded process role and open the unchanged S03 ENet transport.
func _ready() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			port = int(argument.trim_prefix("--port="))
		elif argument.begins_with("--clients="):
			expected_clients = int(argument.trim_prefix("--clients="))

	if role not in ["host", "client"] or port < 1 or expected_clients < 1:
		_fail("invalid process arguments")
		return

	transport = TransportScript.new(get_tree())
	if role == "host":
		multiplayer.peer_connected.connect(_peer_connected)
		var error: Error = transport.open_host(1, port)
		if error != OK:
			_fail("host transport open failed")
			return

		multiplayer.multiplayer_peer = transport.peer
		_emit({ "event": "ready", "entities": ENTITY_COUNT })
	else:
		multiplayer.server_disconnected.connect(_host_closed)
		var target: Dictionary = transport.parse_endpoint("127.0.0.1", port)
		var error: Error = transport.open_client(1, target)
		if error != OK:
			_fail("client transport open failed")
			return

		multiplayer.multiplayer_peer = transport.peer


## Publish snapshots, lifecycle transitions and bounded completion on physics ticks.
func _physics_process(_delta: float) -> void:
	if role != "host" or not running:
		return

	run_tick += 1
	if run_tick == 120:
		_publish_lifecycle(3, 1, 1, 2, "death")
	elif run_tick == 180:
		_publish_lifecycle(4, 65, 1, 2, "wreck")
	elif run_tick == 240:
		_publish_lifecycle(2, 101, 1, 3, "despawn")
	elif run_tick == 246:
		_publish_lifecycle(1, 101, 2, 1, "spawn")

	if run_tick % SNAPSHOT_INTERVAL_TICKS == 0 and run_tick <= RUN_TICKS:
		_publish_snapshot()

	if run_tick == RUN_TICKS:
		_complete_run.rpc({ "run_ticks": run_tick, "host_entities": ENTITY_COUNT })
		finish_tick = run_tick + FINISH_DELAY_TICKS
	elif finish_tick > 0 and run_tick >= finish_tick:
		_emit_result()


## Interpolate remote rows behind estimated server time and bound extrapolation.
func _process(delta: float) -> void:  # gdstyle:ignore=quality/max-local-variables
	if role != "client":
		return
	if result_emitted_ms > 0 and Time.get_ticks_msec() - result_emitted_ms > 30_000:
		get_tree().quit(0)
		return
	if not running:
		return

	var now_ms: int = Time.get_ticks_msec()
	for entity_id: int in samples.keys():
		var history: Array = samples[entity_id]
		if history.is_empty():
			continue

		var newest: Dictionary = history.back()
		var target_tick: float = (
			float(newest.tick)
			+ float(now_ms - int(newest.receipt_ms)) * 0.06
			- INTERPOLATION_DELAY_TICKS
		)
		var position: Vector2
		var extrapolated: bool = false
		if history.size() >= 2 and target_tick <= float(newest.tick):
			var older: Dictionary = history[history.size() - 2]
			var span: float = maxf(1.0, float(newest.tick - older.tick))
			var weight: float = clampf((target_tick - float(older.tick)) / span, 0.0, 1.0)
			position = Vector2(older.x, older.z).lerp(Vector2(newest.x, newest.z), weight)
			interpolation_frames += 1
		else:
			var ahead: float = clampf(
				target_tick - float(newest.tick), 0.0, MAX_EXTRAPOLATION_TICKS
			)
			position = Vector2(newest.x, newest.z) + Vector2(newest.vx, newest.vz) * ahead / 60.0
			extrapolated = true
			extrapolation_frames += 1

		if displayed.has(entity_id):
			var actual_step: float = position.distance_to(displayed[entity_id])
			var expected_step: float = Vector2(newest.vx, newest.vz).length() * delta
			jitter_samples_m.append(absf(actual_step - expected_step))
		if extrapolated and history.size() < 2:
			jitter_samples_m.append(0.0)
		displayed[entity_id] = position


## Begin one complete reliable baseline after every expected client is connected.
func _peer_connected(peer_id: int) -> void:
	if role != "host" or peer_id in connected_peers:
		return

	connected_peers.append(peer_id)
	if connected_peers.size() != expected_clients:
		return

	var rows: Array[Dictionary] = _population_rows(0)
	var packets: Array[PackedByteArray] = codec.encode(0, 0, rows)
	var payload_bytes_per_client: int = 0
	for packet: PackedByteArray in packets:
		payload_bytes_per_client += packet.size()
	baseline_payload_bytes = payload_bytes_per_client * expected_clients
	for target_peer: int in connected_peers:
		for packet: PackedByteArray in packets:
			_baseline.rpc_id(target_peer, packet)
		_baseline_done.rpc_id(target_peer, ENTITY_COUNT, payload_bytes_per_client)

	_emit({ "event": "baseline_sent", "peers": connected_peers.size() })


## Install a reliable baseline chunk before live movement begins.
@rpc("authority", "call_remote", "reliable", 1)
func _baseline(packet: PackedByteArray) -> void:
	if role != "client" or multiplayer.get_remote_sender_id() != 1:
		return

	var decoded: Dictionary = codec.decode(packet)
	if decoded.is_empty():
		_fail("malformed baseline")
		return

	_apply_rows(decoded.rows, int(decoded.tick), true)


## Acknowledge a complete baseline only after the declared entity count is installed.
@rpc("authority", "call_remote", "reliable", 1)
func _baseline_done(entity_count: int, payload_bytes: int) -> void:
	if role != "client" or multiplayer.get_remote_sender_id() != 1:
		return
	if lifecycle_generation.size() != entity_count:
		_fail("incomplete baseline")
		return

	baseline_payload_bytes = payload_bytes
	_baseline_ack.rpc_id(1, lifecycle_generation.size())


## Open live publication after every sender-derived baseline acknowledgement.
@rpc("any_peer", "call_remote", "reliable", 0)
func _baseline_ack(entity_count: int) -> void:
	if role != "host" or entity_count != ENTITY_COUNT:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	if peer_id not in connected_peers:
		return

	baseline_acks[peer_id] = true
	if baseline_acks.size() == expected_clients:
		running = true
		started_ms = Time.get_ticks_msec()
		_emit({ "event": "snapshots_started", "baseline_payload_bytes": baseline_payload_bytes })
		_start_client.rpc()


## Start client interpolation only after host admission has closed the baseline cut.
@rpc("authority", "call_remote", "reliable", 0)
func _start_client() -> void:
	if role == "client" and multiplayer.get_remote_sender_id() == 1:
		running = true
		started_ms = Time.get_ticks_msec()
		_emit({ "event": "started", "baseline_entities": lifecycle_generation.size() })


## Decode one movement chunk from the authoritative host and update per-entity history.
@rpc("authority", "call_remote", "unreliable_ordered", 3)
func _snapshot(packet: PackedByteArray) -> void:
	if role != "client" or multiplayer.get_remote_sender_id() != 1:
		return

	var before_usec: int = Time.get_ticks_usec()
	var decoded: Dictionary = codec.decode(packet)
	decode_usec.append(Time.get_ticks_usec() - before_usec)
	if decoded.is_empty():
		return

	max_packet_bytes = maxi(max_packet_bytes, packet.size())
	snapshot_packets += 1
	_apply_rows(decoded.rows, int(decoded.tick), false)


## Apply only rows whose generation and terminal phase were installed reliably.
func _apply_rows(rows: Array, tick: int, baseline: bool) -> void:
	var receipt_ms: int = Time.get_ticks_msec()
	for value: Variant in rows:
		var row: Dictionary = value
		var entity_id: int = int(row.id)
		if baseline:
			lifecycle_generation[entity_id] = int(row.generation)
			lifecycle_phase[entity_id] = int(row.phase)
		elif (
			not lifecycle_generation.has(entity_id)
			or int(lifecycle_generation[entity_id]) != int(row.generation)
			or int(lifecycle_phase[entity_id]) == 3
		):
			stale_rows_rejected += 1
			continue

		var sample: Dictionary = row.duplicate(true)
		sample.tick = tick
		sample.receipt_ms = receipt_ms
		if not samples.has(entity_id):
			samples[entity_id] = []
		var history: Array = samples[entity_id]
		history.append(sample)
		if history.size() > 2:
			history.pop_front()
		snapshot_rows_received += 0 if baseline else 1


## Apply one ordered reliable lifecycle transition without letting motion recreate tombstones.
@rpc("authority", "call_remote", "reliable", 1)
func _lifecycle(packet: PackedByteArray, label: String) -> void:
	if role != "client" or multiplayer.get_remote_sender_id() != 1:
		return

	var event: Dictionary = codec.decode_lifecycle(packet)
	if event.is_empty() or int(event.revision) <= lifecycle_revision:
		return

	lifecycle_revision = int(event.revision)
	lifecycle_generation[event.id] = event.generation
	lifecycle_phase[event.id] = event.phase
	lifecycle_events_received.append(label)
	if int(event.phase) == 3:
		samples.erase(event.id)
		displayed.erase(event.id)


## Send one lifecycle transaction before dependent movement on the reliable state stream.
func _publish_lifecycle(
	event_kind: int, entity_id: int, generation: int, phase: int, label: String
) -> void:
	lifecycle_revision += 1
	lifecycle_generation[entity_id] = generation
	lifecycle_phase[entity_id] = phase
	var packet: PackedByteArray = codec.encode_lifecycle({
		"event_kind": event_kind,
		"id": entity_id,
		"generation": generation,
		"phase": phase,
		"revision": lifecycle_revision,
		"tick": run_tick,
	})
	_lifecycle.rpc(packet, label)


## Encode and send one full-cap population refresh split below the motion payload limit.
func _publish_snapshot() -> void:
	var population: Array[Dictionary] = _population_rows(run_tick)
	var first: int = snapshot_subset * S11SnapshotCodec.MAX_ROWS_PER_PACKET
	var last: int = mini(first + S11SnapshotCodec.MAX_ROWS_PER_PACKET, population.size())
	var rows: Array[Dictionary] = []
	rows.assign(population.slice(first, last))
	snapshot_subset = (snapshot_subset + 1) % 2
	snapshot_sequence += 1
	var before_usec: int = Time.get_ticks_usec()
	var packets: Array[PackedByteArray] = codec.encode(snapshot_sequence, run_tick, rows)
	encode_usec.append(Time.get_ticks_usec() - before_usec)
	for packet: PackedByteArray in packets:
		max_packet_bytes = maxi(max_packet_bytes, packet.size())
		encoded_payload_bytes += packet.size()
		encoded_rows += int(codec.decode(packet).rows.size())
		snapshot_packets += 1
		_snapshot.rpc(packet)


## Build deterministic rail motion for every entity at the full simultaneous caps.
func _population_rows(tick: int) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for entity_id: int in range(1, ENTITY_COUNT + 1):
		var kind: int = _kind_for(entity_id)
		var generation: int = 2 if entity_id == 101 and tick >= 246 else 1
		var phase: int = 1
		if entity_id == 1 and tick >= 120:
			phase = 2
		elif entity_id == 65 and tick >= 180:
			phase = 2
		elif entity_id == 101 and 240 <= tick and tick < 246:
			phase = 3

		var lane: int = (entity_id - 1) % 16
		var base_x: float = -24.0 + float(lane) * 3.0
		var base_z: float = -18.0 + float((entity_id - 1) / 16) * 4.0
		var speed: float = 0.0 if kind >= 5 or phase != 1 else 1.0 + float(kind) * 0.35
		var direction: float = -1.0 if entity_id % 2 == 0 else 1.0
		var travel: float = fposmod(float(tick) / 60.0 * speed, 24.0) - 12.0
		(
			rows
			. append(
				{
					"id": entity_id,
					"generation": generation,
					"kind": kind,
					"phase": phase,
					"flags": 0,
					"x": base_x + travel * direction,
					"z": base_z,
					"vx": speed * direction,
					"vz": 0.0,
					"yaw": PI / 2.0 if direction > 0.0 else -PI / 2.0,
				}
			)
		)

	return rows


## Map the fixed full-cap ID ranges to compact wire kinds.
func _kind_for(entity_id: int) -> int:
	if entity_id <= PEDESTRIANS:
		return 1
	if entity_id <= PEDESTRIANS + CARS:
		return 2
	if entity_id <= PEDESTRIANS + CARS + PLAYERS:
		return 3
	if entity_id <= PEDESTRIANS + CARS + PLAYERS + ROCKETS:
		return 4
	if entity_id <= PEDESTRIANS + CARS + PLAYERS + ROCKETS + WRECKS:
		return 5

	return 6


## Tell clients to publish their measurements after the complete run.
@rpc("authority", "call_remote", "reliable", 1)
func _complete_run(_host_summary: Dictionary) -> void:
	if role == "client" and multiplayer.get_remote_sender_id() == 1:
		running = false
		_emit_result(false)


## Exit a completed client after the authoritative process closes the transport.
func _host_closed() -> void:
	if result_emitted_ms > 0:
		get_tree().quit(0)
		return

	running = false
	_emit_result()


## Emit one machine-readable result and optionally close this owned process.
func _emit_result(quit_process: bool = true) -> void:  # gdstyle:ignore=quality/max-branches
	running = false
	var failures: Array[String] = []
	if role == "host":
		if max_packet_bytes > S11SnapshotCodec.MAX_PACKET_BYTES:
			failures.append("motion packet exceeded 1200 bytes")
		if encoded_rows < ENTITY_COUNT * 70:
			failures.append("host did not revisit every entity within the publication bound")
	else:
		if lifecycle_generation.size() != ENTITY_COUNT:
			failures.append("client population count changed")
		if lifecycle_events_received != ["death", "wreck", "despawn", "spawn"]:
			failures.append("reliable lifecycle order incomplete")
		if int(lifecycle_generation.get(101, 0)) != 2:
			failures.append("rocket generation did not advance")
		if int(lifecycle_phase.get(1, 0)) != 2 or int(lifecycle_phase.get(65, 0)) != 2:
			failures.append("terminal phases missing")
		if snapshot_rows_received < ENTITY_COUNT * 10:
			failures.append("insufficient movement refreshes")

	var result: Dictionary = {
		"event": "result",
		"ok": failures.is_empty(),
		"failures": failures,
		"role": role,
		"entities": lifecycle_generation.size() if role == "client" else ENTITY_COUNT,
		"baseline_payload_bytes": baseline_payload_bytes,
		"max_packet_bytes": max_packet_bytes,
		"snapshot_packets": snapshot_packets,
		"snapshot_rows": snapshot_rows_received if role == "client" else encoded_rows,
		"encode_usec": encode_usec,
		"decode_usec": decode_usec,
		"encoded_payload_bytes": encoded_payload_bytes,
		"bytes_per_entity_row":
		float(encoded_payload_bytes) / float(encoded_rows) if encoded_rows > 0 else 0.0,
		"interpolation_frames": interpolation_frames,
		"extrapolation_frames": extrapolation_frames,
		"jitter_p95_m": _percentile(jitter_samples_m, 0.95),
		"stale_rows_rejected": stale_rows_rejected,
		"lifecycle_events": lifecycle_events_received,
		"duration_ms": Time.get_ticks_msec() - started_ms,
	}
	_emit(result)
	result_emitted_ms = Time.get_ticks_msec()
	if quit_process:
		get_tree().quit(0 if failures.is_empty() else 1)


## Report an early process failure in the same result envelope.
func _fail(message: String) -> void:
	_emit({ "event": "result", "ok": false, "failures": [message], "role": role })
	get_tree().quit(1)


## Print one stable JSON record for the external runner.
func _emit(record: Dictionary) -> void:
	print("S11 " + JSON.stringify(record))


## Compute a nearest-rank percentile for compact retained telemetry.
func _percentile(values: Array[float], quantile: float) -> float:
	if values.is_empty():
		return 0.0

	var ordered: Array[float] = values.duplicate()
	ordered.sort()
	var index: int = clampi(ceili(float(ordered.size()) * quantile) - 1, 0, ordered.size() - 1)
	return ordered[index]
