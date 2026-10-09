class_name S17Host
extends Node3D
## Coordinates one accelerated full-cap host tick through the selected spike owners.

const TICKS_PER_SECOND: int = 60
const WARMUP_TICKS: int = 60 * TICKS_PER_SECOND
const MEASURED_TICKS: int = 10 * 60 * TICKS_PER_SECOND
const CHAIN_INTERVAL_TICKS: int = 5_000
const CHAIN_COUNT: int = 8
const SESSION_ID: String = "05050505050505050505050505050505"
const CLIENT_COUNT: int = 3
const SNAPSHOT_ENTITY_COUNT: int = 148
const EQUIVALENCE_TICKS: int = 120
const EMPTY_TIMER_SAMPLES: int = 10_000
const SUBSYSTEMS: Array[String] = [
	"pedestrians", "traffic", "combat", "explosions", "snapshot_encode",
	"snapshot_encode_production_schedule", "total", "total_production_schedule",
]

var _traffic: S17TrafficAdapter = S17TrafficAdapter.new()
var _pedestrians: S17PedestrianAdapter = S17PedestrianAdapter.new()
var _combat_adapter: S17CombatAdapter = S17CombatAdapter.new()
var _codec: S11SnapshotCodec = S11SnapshotCodec.new()
var _timings: Dictionary = {}
var _chain_receipts: Array[Dictionary] = []
var _current_chain_trigger_tick: int = -1
var _current_chain_outcome: String = ""
var _snapshot_shape: Dictionary = {}

@onready var _topology: S09Topology = $Traffic
@onready var _pedestrian_fixture: Node3D = $Pedestrians
@onready var _combat: S12Combat = $Combat
@onready var _session: S03Session = $Session
@onready var _damage: S05Damage = $Explosion/Damage
@onready var _cars: Node3D = $Explosion/Cars


## Runs one warmup plus ten measured minutes and returns bounded integrated evidence.
func run_seed(seed: int) -> Dictionary:
	var failures: Array[String] = []
	var traffic_admission: String = _traffic.begin(_topology, seed)
	if traffic_admission != "OK":
		failures.append("S09 traffic admission failed: " + traffic_admission)
	var pedestrian_failures: Array[String] = _pedestrians.begin(_pedestrian_fixture, seed)
	failures.append_array(pedestrian_failures)
	_combat_adapter.begin(_combat, _session)
	_bind_damage()
	_start_chain_session()

	var equivalence: Dictionary = _adapter_equivalence(seed)
	for subsystem: String in equivalence:
		if not equivalence[subsystem].ok:
			failures.append("%s adapter equivalence failed" % subsystem)

	_warm_up()
	_prepare_measurement(failures)
	for measured_tick: int in MEASURED_TICKS:
		_measure_tick(WARMUP_TICKS + measured_tick, measured_tick)
	_retain_chain_receipt()

	var receipts: Dictionary = _owner_receipts()
	_validate_receipts(failures, receipts)
	var result: Dictionary = _build_result(seed, failures, equivalence, receipts)
	_pedestrians.finish()
	return result


## Runs short source-equivalence checks before any warmup state is measured.
func _adapter_equivalence(seed: int) -> Dictionary:
	return {
		"traffic": S17TrafficAdapter.equivalence(_topology, seed, EQUIVALENCE_TICKS),
		"pedestrians": S17PedestrianAdapter.equivalence(self, seed, EQUIVALENCE_TICKS),
		"combat": _combat_adapter.equivalence(),
	}


## Advances every composed owner for 3,600 unmeasured ticks and warms both codec paths.
func _warm_up() -> void:
	for tick: int in WARMUP_TICKS:
		_pedestrians.step(tick)
		_traffic.step(tick)
		_combat_adapter.step(tick)
		if tick == 0:
			_current_chain_outcome = _resolve_root_shot()
		_damage.advance()
		_encode_conservative_snapshot(tick)
		_encode_production_snapshot(tick)


## Clears measurement counters only while retaining warmed AI, history and route state.
func _prepare_measurement(failures: Array[String]) -> void:
	if _current_chain_outcome != "OK" or _damage.completed.size() != 12:
		failures.append("warmup S05 chain did not settle before measurement")
	_traffic.begin_measurement()
	_pedestrians.begin_measurement()
	_combat_adapter.begin_measurement()
	_start_chain_session()
	_current_chain_trigger_tick = -1
	_current_chain_outcome = ""
	_chain_receipts.clear()
	for subsystem: String in SUBSYSTEMS:
		_timings[subsystem] = [] as Array[int]
	_snapshot_shape = _snapshot_probe(WARMUP_TICKS)
	_timings.empty_timer_baseline = _measure_empty_timer_baseline()


## Moves measured chain receipt bookkeeping ahead of the total bracket when due.
func _prepare_chain_tick(measured_tick: int) -> bool:
	var chain_due: bool = measured_tick % CHAIN_INTERVAL_TICKS == 0
	if chain_due and _current_chain_trigger_tick >= 0:
		_retain_chain_receipt()
	if chain_due:
		_current_chain_trigger_tick = measured_tick
	return chain_due


## Measures owners without array appends inside either reported total timing boundary.
func _measure_tick(tick: int, sample: int) -> void:  # gdstyle:ignore=quality/max-function-length
	var pedestrians_usec: int = 0
	var traffic_usec: int = 0
	var combat_usec: int = 0
	var explosions_usec: int = 0
	var snapshot_usec: int = 0
	var production_snapshot_usec: int = 0
	var total_usec: int = 0
	var total_started: int = 0
	var section_started: int = 0
	var chain_due: bool = _prepare_chain_tick(sample)

	total_started = Time.get_ticks_usec()
	section_started = Time.get_ticks_usec()
	_pedestrians.step(tick)
	pedestrians_usec = Time.get_ticks_usec() - section_started

	section_started = Time.get_ticks_usec()
	_traffic.step(tick)
	traffic_usec = Time.get_ticks_usec() - section_started

	section_started = Time.get_ticks_usec()
	_combat_adapter.step(tick)
	combat_usec = Time.get_ticks_usec() - section_started

	section_started = Time.get_ticks_usec()
	if chain_due:
		_start_chain_session()
		_current_chain_outcome = _resolve_root_shot()
	_damage.advance()
	explosions_usec = Time.get_ticks_usec() - section_started

	section_started = Time.get_ticks_usec()
	_encode_conservative_snapshot(tick)
	snapshot_usec = Time.get_ticks_usec() - section_started
	total_usec = Time.get_ticks_usec() - total_started

	section_started = Time.get_ticks_usec()
	_encode_production_snapshot(tick)
	production_snapshot_usec = Time.get_ticks_usec() - section_started

	_append_timing_samples({
		"pedestrians": pedestrians_usec,
		"traffic": traffic_usec,
		"combat": combat_usec,
		"explosions": explosions_usec,
		"snapshot_encode": snapshot_usec,
		"snapshot_encode_production_schedule": production_snapshot_usec,
		"total": total_usec,
		"total_production_schedule": maxi(
			0, total_usec - snapshot_usec + production_snapshot_usec),
	})


## Appends all observation samples after the measured work brackets have closed.
func _append_timing_samples(samples: Dictionary) -> void:
	for subsystem: String in SUBSYSTEMS:
		(_timings[subsystem] as Array[int]).append(samples[subsystem])


## Binds the twelve saved S05 car instances to the unchanged damage/chain owner.
func _bind_damage() -> void:
	var bodies: Array[S05Car] = []
	for child: Node in _cars.get_children():
		bodies.append(child as S05Car)
	_damage.bind_bodies(bodies)


## Starts one fresh S05 authoritative chain session with all four shooters admitted.
func _start_chain_session() -> void:
	_damage.begin(true, SESSION_ID)
	for shooter: int in range(1, S17CombatAdapter.PLAYER_COUNT + 1):
		_damage.register_shooter(shooter, 1)


## Triggers one root shot through S05's public authoritative API.
func _resolve_root_shot() -> String:
	return _damage.resolve_shot({
		"session": SESSION_ID, "match": 1, "shooter": 1, "generation": 1,
		"sequence": 1,
	}, S05Damage.CAR_ID_START)


## Retains one settled measured chain outside every host-tick timing bracket.
func _retain_chain_receipt() -> void:
	_chain_receipts.append({
		"trigger_tick": _current_chain_trigger_tick,
		"outcome": _current_chain_outcome,
		"completed": _damage.completed.size(),
		"target_visits": _damage.total_visits,
		"target_peak": _damage.target_peak,
		"queue_peak": _damage.queue_peak,
	})


## Encodes three complete 148-row snapshots as the conservative every-tick case.
func _encode_conservative_snapshot(tick: int) -> void:
	var rows: Array[Dictionary] = _snapshot_rows(tick)
	for client_index: int in CLIENT_COUNT:
		_codec.encode(tick * CLIENT_COUNT + client_index, tick, rows)


## Encodes one broadcast 74-row subset every four ticks, matching S11's schedule.
func _encode_production_snapshot(tick: int) -> void:
	if tick % 4 != 0:
		return
	var rows: Array[Dictionary] = _snapshot_rows(tick)
	var subset: int = int(tick / 4) % 2
	var first: int = subset * S11SnapshotCodec.MAX_ROWS_PER_PACKET
	var selected: Array[Dictionary] = []
	selected.assign(rows.slice(first, first + S11SnapshotCodec.MAX_ROWS_PER_PACKET))
	_codec.encode(tick / 4, tick, selected)


## Builds the full simultaneous movement rows once for the selected codec path.
func _snapshot_rows(tick: int) -> Array[Dictionary]:
	var rows: Array[Dictionary] = _pedestrians.snapshot_rows(1)
	rows.append_array(_traffic.snapshot_rows(rows.size() + 1))
	rows.append_array(_synthetic_rows(rows.size() + 1, tick))
	assert(rows.size() == SNAPSHOT_ENTITY_COUNT)
	return rows


## Measures packet sizes once outside the timed interval for receipt validation.
func _snapshot_probe(tick: int) -> Dictionary:
	var rows: Array[Dictionary] = _snapshot_rows(tick)
	var full_packets: Array[PackedByteArray] = _codec.encode(0, tick, rows)
	var subset_rows: Array[Dictionary] = []
	subset_rows.assign(rows.slice(0, S11SnapshotCodec.MAX_ROWS_PER_PACKET))
	var subset_packets: Array[PackedByteArray] = _codec.encode(0, tick, subset_rows)
	return {
		"full_packet_sizes": _packet_sizes(full_packets),
		"subset_packet_sizes": _packet_sizes(subset_packets),
	}


## Returns packet sizes for untimed evidence and payload-bound checks.
func _packet_sizes(packets: Array[PackedByteArray]) -> Array[int]:
	var sizes: Array[int] = []
	for packet: PackedByteArray in packets:
		sizes.append(packet.size())
	return sizes


## Measures two adjacent monotonic timer reads without host work between them.
func _measure_empty_timer_baseline() -> Array[int]:
	var samples: Array[int] = []
	for _sample: int in EMPTY_TIMER_SAMPLES:
		var started: int = Time.get_ticks_usec()
		var elapsed: int = Time.get_ticks_usec() - started
		samples.append(elapsed)
	return samples


## Supplies four players and retained projectile/lifecycle rows not owned by S09/S10.
func _synthetic_rows(first_id: int, tick: int) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for player: int in 4:
		rows.append(_snapshot_row(first_id + rows.size(), 3,
			Vector3(-6.0 + player * 4.0, 0.0, -8.0), Vector3.ZERO, 1))
	for rocket: int in 16:
		var rocket_position: Vector3 = Vector3(-20.0 + rocket * 2.0, 0.0,
			-16.0 + fmod(float(tick) * 0.3, 32.0))
		rows.append(_snapshot_row(first_id + rows.size(), 4, rocket_position,
			Vector3(0.0, 0.0, 18.0), 1))
	for wreck: int in 16:
		rows.append(_snapshot_row(first_id + rows.size(), 2,
			Vector3(float(wreck % 4) * 4.0, 0.0, float(wreck / 4) * 4.0),
			Vector3.ZERO, 2))
	for dead: int in 16:
		rows.append(_snapshot_row(first_id + rows.size(), 1,
			Vector3(-24.0 + float(dead % 8) * 3.0, 0.0, 20.0 + float(dead / 8) * 3.0),
			Vector3.ZERO, 2))
	return rows


## Builds one complete movement row accepted by the unchanged S11 codec.
func _snapshot_row(entity_id: int, kind: int, position: Vector3, velocity: Vector3,
		phase: int) -> Dictionary:
	return {
		"id": entity_id, "generation": 1, "kind": kind, "phase": phase, "flags": 0,
		"x": position.x, "z": position.z, "vx": velocity.x, "vz": velocity.z,
		"yaw": 0.0,
	}


## Collects current owner receipts after the complete measured interval.
func _owner_receipts() -> Dictionary:
	return {
		"pedestrians": _pedestrians.receipt(),
		"traffic": _traffic.receipt(),
		"combat": _combat_adapter.receipt(),
	}


## Checks cardinality, measured chains and owner receipts independently of timing budgets.
func _validate_receipts(failures: Array[String], receipts: Dictionary) -> void:
	var pedestrians: Dictionary = receipts.pedestrians
	var traffic: Dictionary = receipts.traffic
	var combat: Dictionary = receipts.combat
	if pedestrians.slots != 64 or pedestrians.off_sidewalk_agent_ticks != 0 or (
		pedestrians.road_outside_crossing_agent_ticks != 0):
		failures.append("pedestrian population or graph legality receipt failed")
	if traffic.moving_cars != 24 or traffic.parked_cars != 8 or (
		traffic.drive_rule_steps != 24 * MEASURED_TICKS):
		failures.append("traffic population or S04 drive-rule receipt failed")
	if combat.players != 4 or combat.accepted_shots <= 0 or combat.rewind_queries != (
		combat.accepted_shots):
		failures.append("four-player S12 validation receipt failed")
	if _chain_receipts.size() != CHAIN_COUNT:
		failures.append("expected eight measured explosion chains")
	for chain: Dictionary in _chain_receipts:
		if chain.outcome != "OK" or chain.completed != 12 or chain.target_visits != 144:
			failures.append("S05 chain did not complete all twelve cars with bounded work")
	for sizes: Array[int] in [_snapshot_shape.full_packet_sizes,
		_snapshot_shape.subset_packet_sizes]:
		if sizes.is_empty() or sizes.max() > S11SnapshotCodec.MAX_PACKET_BYTES:
			failures.append("S11 snapshot packet size bound failed")


## Builds the seed receipt after all independent outcome validation has completed.
func _build_result(seed: int, failures: Array[String], equivalence: Dictionary,
		receipts: Dictionary) -> Dictionary:
	var conservative_total: Dictionary = _distribution(_timings.total)
	var production_total: Dictionary = _distribution(_timings.total_production_schedule)
	return {
		"seed": seed,
		"warmup_ticks": WARMUP_TICKS,
		"measured_ticks": MEASURED_TICKS,
		"simulated_warmup_seconds": WARMUP_TICKS / TICKS_PER_SECOND,
		"simulated_measured_seconds": MEASURED_TICKS / TICKS_PER_SECOND,
		"environment": _environment_receipt(),
		"population": {
			"pedestrians": 64, "moving_cars": 24, "parked_cars": 8, "players": 4,
			"rockets": 16, "wrecks": 16, "dead_pedestrians": 16,
		},
		"equivalence": equivalence,
		"timing_ms": _timing_summaries(),
		"timing_usec_samples": _timings,
		"empty_timer_baseline_ms": _distribution(_timings.empty_timer_baseline),
		"empty_timer_usec_samples": _timings.empty_timer_baseline,
		"pedestrians": receipts.pedestrians,
		"traffic": receipts.traffic,
		"combat": receipts.combat,
		"explosion_chains": _chain_receipts,
		"snapshot": _snapshot_receipt(),
		"budget": {
			"p95_limit_ms": 4.0, "p99_limit_ms": 8.0,
			"conservative_p95_pass": conservative_total.p95 <= 4.0,
			"conservative_p99_pass": conservative_total.p99 <= 8.0,
			"production_schedule_p95_pass": production_total.p95 <= 4.0,
			"production_schedule_p99_pass": production_total.p99 <= 8.0,
			"traffic_audit_share_ms": 1.5,
			"traffic_s09_share_ms": 2.0,
			"pedestrian_share_ms": 1.0,
		},
		"failures": failures,
	}


## Reports conservative and production-schedule packet work from untimed packet probes.
func _snapshot_receipt() -> Dictionary:
	var full_bytes: int = 0
	for size: int in _snapshot_shape.full_packet_sizes:
		full_bytes += size
	var subset_bytes: int = 0
	for size: int in _snapshot_shape.subset_packet_sizes:
		subset_bytes += size
	var production_publications: int = ceili(float(MEASURED_TICKS) / 4.0)
	return {
		"clients": CLIENT_COUNT,
		"entities": SNAPSHOT_ENTITY_COUNT,
		"conservative_every_tick": {
			"encodes": MEASURED_TICKS * CLIENT_COUNT,
			"packets": MEASURED_TICKS * CLIENT_COUNT * (
				_snapshot_shape.full_packet_sizes.size()),
			"encoded_bytes": MEASURED_TICKS * CLIENT_COUNT * full_bytes,
			"packet_sizes": _snapshot_shape.full_packet_sizes,
		},
		"s11_production_schedule": {
			"interval_ticks": 4,
			"rows_per_publication": S11SnapshotCodec.MAX_ROWS_PER_PACKET,
			"publications": production_publications,
			"encodes": production_publications,
			"broadcast_clients": CLIENT_COUNT,
			"encoded_bytes": production_publications * subset_bytes,
			"packet_sizes": _snapshot_shape.subset_packet_sizes,
		},
	}


## Captures engine and headless renderer identity with each seed receipt.
func _environment_receipt() -> Dictionary:
	return {
		"godot_version": Engine.get_version_info().string,
		"display_server": DisplayServer.get_name(),
		"headless": DisplayServer.get_name() == "headless",
		"can_draw": DisplayServer.window_can_draw(),
		"renderer": RenderingServer.get_current_rendering_method(),
		"video_adapter": RenderingServer.get_video_adapter_name(),
		"video_adapter_api": RenderingServer.get_video_adapter_api_version(),
	}


## Summarizes each subsystem's complete measured tick samples in milliseconds.
func _timing_summaries() -> Dictionary:
	var summaries: Dictionary = {}
	for subsystem: String in SUBSYSTEMS:
		summaries[subsystem] = _distribution(_timings[subsystem])
	return summaries


## Reports nearest-rank median/p95/p99/worst from integer microsecond samples.
func _distribution(samples: Array[int]) -> Dictionary:
	var ordered: Array[int] = samples.duplicate()
	ordered.sort()
	return {
		"count": ordered.size(),
		"median": float(_percentile(ordered, 0.50)) / 1000.0,
		"p95": float(_percentile(ordered, 0.95)) / 1000.0,
		"p99": float(_percentile(ordered, 0.99)) / 1000.0,
		"worst": float(_percentile(ordered, 1.0)) / 1000.0,
	}


## Selects one nearest-rank sample from an already sorted nonempty array.
func _percentile(ordered: Array[int], fraction: float) -> int:
	return ordered[clampi(ceili(float(ordered.size()) * fraction) - 1,
		0, ordered.size() - 1)]
