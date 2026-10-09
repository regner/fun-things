class_name S17Host
extends Node3D
## Coordinates one accelerated full-cap host tick through the selected spike owners.

const TICKS_PER_SECOND: int = 60
const SIMULATION_TICKS: int = 10 * 60 * TICKS_PER_SECOND
const CHAIN_INTERVAL_TICKS: int = 120 * TICKS_PER_SECOND
const CHAIN_COUNT: int = 5
const SESSION_ID: String = "05050505050505050505050505050505"
const CLIENT_COUNT: int = 3
const SNAPSHOT_ENTITY_COUNT: int = 148
const EQUIVALENCE_TICKS: int = 120
const SUBSYSTEMS: Array[String] = [
	"pedestrians", "traffic", "combat", "explosions", "snapshot_encode", "total",
]

var _traffic: S17TrafficAdapter = S17TrafficAdapter.new()
var _pedestrians: S17PedestrianAdapter = S17PedestrianAdapter.new()
var _combat_adapter: S17CombatAdapter = S17CombatAdapter.new()
var _codec: S11SnapshotCodec = S11SnapshotCodec.new()
var _timings: Dictionary = {}
var _chain_receipts: Array[Dictionary] = []
var _snapshot_packets: int = 0
var _snapshot_bytes: int = 0
var _snapshot_max_packet_bytes: int = 0

@onready var _topology: S09Topology = $Traffic
@onready var _pedestrian_fixture: Node3D = $Pedestrians
@onready var _combat: S12Combat = $Combat
@onready var _session: S03Session = $Session
@onready var _damage: S05Damage = $Explosion/Damage
@onready var _cars: Node3D = $Explosion/Cars


## Runs one seeded ten-minute integrated host composition and returns bounded evidence.
func run_seed(seed: int) -> Dictionary:
	for subsystem: String in SUBSYSTEMS:
		_timings[subsystem] = [] as Array[int]
	var failures: Array[String] = []
	var traffic_admission: String = _traffic.begin(_topology, seed)
	if traffic_admission != "OK":
		failures.append("S09 traffic admission failed: " + traffic_admission)
	var pedestrian_failures: Array[String] = _pedestrians.begin(_pedestrian_fixture, seed)
	failures.append_array(pedestrian_failures)
	_combat_adapter.begin(_combat, _session)
	_bind_damage()
	_start_chain_session()

	var equivalence: Dictionary = {
		"traffic": S17TrafficAdapter.equivalence(_topology, seed, EQUIVALENCE_TICKS),
		"pedestrians": S17PedestrianAdapter.equivalence(self, seed, EQUIVALENCE_TICKS),
		"combat": _combat_adapter.equivalence(),
	}
	for subsystem: String in equivalence:
		if not equivalence[subsystem].ok:
			failures.append("%s adapter equivalence failed" % subsystem)

	for tick: int in SIMULATION_TICKS:
		_measure_tick(tick)
	_finalize_chain()

	var pedestrian_receipt: Dictionary = _pedestrians.receipt()
	var traffic_receipt: Dictionary = _traffic.receipt()
	var combat_receipt: Dictionary = _combat_adapter.receipt()
	_validate_receipts(failures, pedestrian_receipt, traffic_receipt, combat_receipt)
	var receipts: Dictionary = {
		"pedestrians": pedestrian_receipt,
		"traffic": traffic_receipt,
		"combat": combat_receipt,
	}
	var result: Dictionary = _build_result(seed, failures, equivalence, receipts)
	_pedestrians.finish()
	return result


## Builds the seed receipt after all independent outcome validation has completed.
func _build_result(seed: int, failures: Array[String], equivalence: Dictionary,
		receipts: Dictionary) -> Dictionary:
	var total_timing: Dictionary = _distribution(_timings.total)
	return {
		"seed": seed,
		"ticks": SIMULATION_TICKS,
		"simulated_seconds": SIMULATION_TICKS / TICKS_PER_SECOND,
		"population": {
			"pedestrians": 64, "moving_cars": 24, "parked_cars": 8, "players": 4,
			"rockets": 16, "wrecks": 16, "dead_pedestrians": 16,
		},
		"equivalence": equivalence,
		"timing_ms": _timing_summaries(),
		"timing_usec_samples": _timings,
		"pedestrians": receipts.pedestrians,
		"traffic": receipts.traffic,
		"combat": receipts.combat,
		"explosion_chains": _chain_receipts,
		"snapshot": {
			"clients_per_tick": CLIENT_COUNT,
			"entities_per_client_tick": SNAPSHOT_ENTITY_COUNT,
			"packets": _snapshot_packets,
			"encoded_bytes": _snapshot_bytes,
			"maximum_packet_bytes": _snapshot_max_packet_bytes,
		},
		"budget": {
			"p95_limit_ms": 4.0, "p99_limit_ms": 8.0,
			"p95_pass": total_timing.p95 <= 4.0,
			"p99_pass": total_timing.p99 <= 8.0,
			"traffic_audit_share_ms": 1.5,
			"traffic_s09_share_ms": 2.0,
			"pedestrian_share_ms": 1.0,
		},
		"failures": failures,
	}


## Measures every selected subsystem and the inclusive sequential host-tick total.
func _measure_tick(tick: int) -> void:
	var total_started: int = Time.get_ticks_usec()
	var started: int = Time.get_ticks_usec()
	_pedestrians.step(tick)
	(_timings.pedestrians as Array[int]).append(Time.get_ticks_usec() - started)

	started = Time.get_ticks_usec()
	_traffic.step(tick)
	(_timings.traffic as Array[int]).append(Time.get_ticks_usec() - started)

	started = Time.get_ticks_usec()
	_combat_adapter.step(tick)
	(_timings.combat as Array[int]).append(Time.get_ticks_usec() - started)

	started = Time.get_ticks_usec()
	if tick % CHAIN_INTERVAL_TICKS == 0:
		_trigger_chain(tick)
	_damage.advance()
	(_timings.explosions as Array[int]).append(Time.get_ticks_usec() - started)

	started = Time.get_ticks_usec()
	_encode_snapshots(tick)
	(_timings.snapshot_encode as Array[int]).append(Time.get_ticks_usec() - started)
	(_timings.total as Array[int]).append(Time.get_ticks_usec() - total_started)


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


## Restarts settled S05 cars and triggers the next root shot through its public API.
func _trigger_chain(tick: int) -> void:
	if tick > 0:
		_finalize_chain()
		_start_chain_session()
	var outcome: String = _damage.resolve_shot({
		"session": SESSION_ID, "match": 1, "shooter": 1, "generation": 1,
		"sequence": 1,
	}, S05Damage.CAR_ID_START)
	if outcome != "OK":
		_chain_receipts.append({ "trigger_tick": tick, "outcome": outcome, "completed": 0 })


## Retains completion and bounded-work facts before the next chain reset.
func _finalize_chain() -> void:
	if not _chain_receipts.is_empty() and _chain_receipts[-1].get("completed") == 0:
		return
	_chain_receipts.append({
		"trigger_tick": 0 if _chain_receipts.is_empty() else (
			_chain_receipts.size() * CHAIN_INTERVAL_TICKS),
		"outcome": "OK",
		"completed": _damage.completed.size(),
		"target_visits": _damage.total_visits,
		"target_peak": _damage.target_peak,
		"queue_peak": _damage.queue_peak,
	})


## Encodes one full-cap S11 movement snapshot independently for each remote client.
func _encode_snapshots(tick: int) -> void:
	var rows: Array[Dictionary] = _pedestrians.snapshot_rows(1)
	rows.append_array(_traffic.snapshot_rows(rows.size() + 1))
	rows.append_array(_synthetic_rows(rows.size() + 1, tick))
	assert(rows.size() == SNAPSHOT_ENTITY_COUNT)
	for client_index: int in CLIENT_COUNT:
		var packets: Array[PackedByteArray] = _codec.encode(
			tick * CLIENT_COUNT + client_index, tick, rows)
		_snapshot_packets += packets.size()
		for packet: PackedByteArray in packets:
			_snapshot_bytes += packet.size()
			_snapshot_max_packet_bytes = maxi(_snapshot_max_packet_bytes, packet.size())


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


## Checks cardinality, bounded chains and owner receipts independently of timing budgets.
func _validate_receipts(failures: Array[String], pedestrians: Dictionary,
		traffic: Dictionary, combat: Dictionary) -> void:
	if pedestrians.slots != 64 or pedestrians.off_sidewalk_agent_ticks != 0 or (
		pedestrians.road_outside_crossing_agent_ticks != 0):
		failures.append("pedestrian population or graph legality receipt failed")
	if traffic.moving_cars != 24 or traffic.parked_cars != 8 or (
		traffic.drive_rule_steps != 24 * SIMULATION_TICKS):
		failures.append("traffic population or S04 drive-rule receipt failed")
	if combat.players != 4 or combat.accepted_shots <= 0 or combat.rewind_queries != (
		combat.accepted_shots):
		failures.append("four-player S12 validation receipt failed")
	if _chain_receipts.size() != CHAIN_COUNT:
		failures.append("expected five triggered explosion chains")
	for chain: Dictionary in _chain_receipts:
		if chain.outcome != "OK" or chain.completed != 12 or chain.target_visits != 144:
			failures.append("S05 chain did not complete all twelve cars with bounded work")
	if _snapshot_max_packet_bytes > S11SnapshotCodec.MAX_PACKET_BYTES or (
		_snapshot_packets != SIMULATION_TICKS * CLIENT_COUNT * 2):
		failures.append("S11 snapshot packet count or size bound failed")


## Summarizes each subsystem's complete tick sample set in milliseconds.
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
