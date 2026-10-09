class_name S12Combat  # gdstyle:ignore=quality/max-class-variables
extends Node3D
## Owns the bounded hit-registration experiment without granting client damage authority.

signal receipt(record: Dictionary)
signal client_finished(summary: Dictionary)
signal host_finished(summary: Dictionary)

const MATCH_REVISION: int = 1
const SNAPSHOT_INTERVAL_TICKS: int = 3
const INTERPOLATION_DELAY_USEC: int = 100_000
const MAX_REWIND_USEC: int = 250_000
const HISTORY_LIMIT: int = 24
const PRESENTATION_LIMIT: int = 12
const MAX_INTENT_BYTES: int = 512
const SEQUENCE_WINDOW: int = 16
const FIRE_INTERVAL_USEC: int = 100_000
const CLIENT_FIRE_INTERVAL_USEC: int = 125_000
const MAGAZINE_SIZE: int = 30
const RELOAD_USEC: int = 1_800_000
const SHOT_COUNT: int = 64
const ROCKET_COOLDOWN_USEC: int = 1_000_000
const ROCKET_SPEED_MPS: float = 18.0
const MAX_RANGE_M: float = 50.0
const AIM_FACTORS: Array[float] = [-1.2, -0.6, 0.0, 0.6, 1.2]

var session: S03Session
var role: String = "host"
var targets: Dictionary = {}
var history: Array[Dictionary] = []
var presentation: Dictionary = {}
var host_tick: int = 0
var history_peak_bytes: int = 0
var last_sequence_by_peer: Dictionary = {}
var next_fire_by_peer: Dictionary = {}
var magazine_by_peer: Dictionary = {}
var reload_end_by_peer: Dictionary = {}
var next_rocket_by_peer: Dictionary = {}
var host_rejections: Dictionary = {}
var client_started_usec: int = 0
var client_next_fire_usec: int = 0
var client_sequence: int = 0
var client_responses: int = 0
var probe_responses: int = 0
var rocket_sent: int = 0
var rocket_responses: int = 0
var client_rows: Array[Dictionary] = []
var rocket_rows: Array[Dictionary] = []
var probes_sent: bool = false
var done_sent: bool = false


## Bind session identity and the authored target actors before measurement starts.
func configure(source_session: S03Session, source_role: String) -> void:
	session = source_session
	role = source_role
	for child: Node in get_children():
		if child is S12Target:
			targets[(child as S12Target).target_id] = child


## Advance authority or generate bounded client fire intent after admission.
func physics_step(delta: float) -> void:
	if session == null or session.phase != "ACTIVE":
		return

	if role == "host":
		_host_step(delta)
	else:
		_client_step()


## Capture authoritative target history and publish replaceable presentation snapshots.
func _host_step(delta: float) -> void:
	host_tick += 1
	for target: S12Target in targets.values():
		target.step(delta)

	var now: int = _wall_usec()
	var positions: Dictionary = {}
	for target_id: String in targets:
		positions[target_id] = (targets[target_id] as S12Target).global_position

	history.append({ "usec": now, "positions": positions })
	if history.size() > HISTORY_LIMIT:
		history.pop_front()
	history_peak_bytes = maxi(history_peak_bytes, var_to_bytes(history).size())
	if host_tick % SNAPSHOT_INTERVAL_TICKS == 0:
		_snapshot.rpc({"session": session.session_id, "match": MATCH_REVISION,
			"tick": host_tick, "usec": now, "positions": positions})


## Send deterministic client shots against the delayed target presentation.
func _client_step() -> void:
	var now: int = _wall_usec()
	if client_started_usec == 0:
		client_started_usec = now
		client_next_fire_usec = now + INTERPOLATION_DELAY_USEC
		return

	if client_sequence < SHOT_COUNT and now >= client_next_fire_usec:
		client_next_fire_usec += CLIENT_FIRE_INTERVAL_USEC
		_send_shot()
		if client_sequence % 8 == 1:
			_send_rocket()
	elif client_sequence == SHOT_COUNT and client_responses >= SHOT_COUNT and not probes_sent:
		_send_validation_probes()
	elif probes_sent and probe_responses >= 3 and rocket_responses >= rocket_sent and not done_sent:
		done_sent = true
		_done.rpc_id(1, session.session_id, MATCH_REVISION)


## Store bounded target snapshots for the client's interpolation-delayed view.
@rpc("authority", "call_remote", "unreliable_ordered", 3)
func _snapshot(envelope: Dictionary) -> void:
	if role != "client" or envelope.get("session") != session.session_id or (
		envelope.get("match") != MATCH_REVISION):
		return

	var positions: Variant = envelope.get("positions")
	if not positions is Dictionary:
		return

	for target_id: String in targets:
		if not positions.has(target_id) or not positions[target_id] is Vector3:
			return

	var row: Dictionary = {"host_usec": int(envelope.get("usec", 0)),
		"receipt_usec": _wall_usec(), "positions": positions.duplicate()}
	for target_id: String in targets:
		if not presentation.has(target_id):
			presentation[target_id] = []
		var rows: Array = presentation[target_id]
		rows.append({"host_usec": row.host_usec, "receipt_usec": row.receipt_usec,
			"position": row.positions[target_id]})
		if rows.size() > PRESENTATION_LIMIT:
			rows.pop_front()


## Build one plausible fire intent from the client's delayed view, including local verdict only.
func _send_shot() -> void:
	var target_id: String = "pedestrian" if client_sequence % 2 == 0 else "car"
	var view: Dictionary = _presentation_row(target_id)
	if view.is_empty():
		client_next_fire_usec += CLIENT_FIRE_INTERVAL_USEC
		return

	client_sequence += 1
	var target: S12Target = targets[target_id]
	var factor: float = AIM_FACTORS[(client_sequence - 1) % AIM_FACTORS.size()]
	var aim_point: Vector3 = view.position + Vector3.RIGHT * factor * target.hit_radius_m
	var direction: Vector3 = (aim_point - global_position).normalized()
	var client_hit: bool = _ray_hits(global_position, direction, view.position,
		target.hit_radius_m)
	var envelope: Dictionary = {"session": session.session_id, "match": MATCH_REVISION,
		"sequence": client_sequence, "target": target_id, "view_usec": view.host_usec,
		"direction": direction, "client_hit": client_hit}
	_fire_intent.rpc_id(1, envelope)
	receipt.emit({"event": "shot_sent", "sequence": client_sequence, "target": target_id,
		"view_age_ms": (_wall_usec() - int(view.host_usec)) / 1000.0,
		"client_hit": client_hit})


## Choose the newest snapshot whose receipt is at least 100 ms old.
func _presentation_row(target_id: String) -> Dictionary:
	if not presentation.has(target_id):
		return {}

	var rows: Array = presentation[target_id]
	var cutoff: int = _wall_usec() - INTERPOLATION_DELAY_USEC
	var selected: Dictionary = {}
	for row: Dictionary in rows:
		if int(row.receipt_usec) <= cutoff:
			selected = row

	return selected


## Derive sender identity, bound payload/rate/ammo, and compare current versus rewind queries.
@rpc("any_peer", "call_remote", "reliable", 0)
func _fire_intent(envelope: Variant) -> void:
	if role != "host":
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	var rejection: String = _validate_intent(peer_id, envelope)
	if not rejection.is_empty():
		_count_rejection(rejection)
		_verdict.rpc_id(peer_id, {"accepted": false, "reason": rejection,
			"sequence": envelope.get("sequence", -1) if envelope is Dictionary else -1})
		return

	var intent: Dictionary = envelope
	var now: int = _wall_usec()
	var target: S12Target = targets[intent.target]
	var current_hit: bool = _ray_hits(global_position, intent.direction,
		target.global_position, target.hit_radius_m)
	var cpu_start: int = Time.get_ticks_usec()
	var rewound: Dictionary = _rewound_position(intent.target, int(intent.view_usec), now)
	var rewind_hit: bool = _ray_hits(global_position, intent.direction, rewound.position,
		target.hit_radius_m)
	var cpu_usec: int = Time.get_ticks_usec() - cpu_start
	_verdict.rpc_id(peer_id, {"accepted": true, "reason": "OK", "sequence": intent.sequence,
		"target": intent.target, "speed": target.speed_mps, "client_hit": intent.client_hit,
		"current_hit": current_hit, "rewind_hit": rewind_hit,
		"rewind_age_ms": (now - int(rewound.usec)) / 1000.0,
		"rewind_clamped": rewound.clamped, "rewind_cpu_usec": cpu_usec})


## Validate exact primitive shape, sender admission, sequence, fire rate, and magazine state.
func _validate_intent(  # gdstyle:ignore=quality/max-returns,quality/max-branches
	peer_id: int,
	envelope: Variant,
) -> String:
	if not session.roster.has(peer_id) or session.roster[peer_id].phase != "ADMITTED":
		return "NOT_ADMITTED"
	if not envelope is Dictionary or var_to_bytes(envelope).size() > MAX_INTENT_BYTES:
		return "INVALID"

	var intent: Dictionary = envelope
	var fields: Array[String] = ["session", "match", "sequence", "target", "view_usec",
		"direction", "client_hit"]
	if intent.size() != fields.size():
		return "INVALID"
	for field: String in fields:
		if not intent.has(field):
			return "INVALID"
	if intent.session != session.session_id or intent.match != MATCH_REVISION:
		return "STALE_STATE"
	if not intent.sequence is int or not intent.view_usec is int or (
		not intent.target is String) or not targets.has(intent.target) or (
		not intent.client_hit is bool) or not intent.direction is Vector3:
		return "INVALID"
	var direction: Vector3 = intent.direction
	if not direction.is_finite() or absf(direction.length() - 1.0) > 0.01:
		return "INVALID"

	var previous: int = int(last_sequence_by_peer.get(peer_id, 0))
	if intent.sequence <= previous:
		return "STALE_SEQUENCE"
	if intent.sequence > previous + SEQUENCE_WINDOW:
		return "WINDOW"
	last_sequence_by_peer[peer_id] = intent.sequence
	var now: int = _wall_usec()
	_update_reload(peer_id, now)
	if now < int(next_fire_by_peer.get(peer_id, 0)):
		return "RATE_LIMITED"
	if int(magazine_by_peer.get(peer_id, MAGAZINE_SIZE)) <= 0:
		if int(reload_end_by_peer.get(peer_id, 0)) == 0:
			reload_end_by_peer[peer_id] = now + RELOAD_USEC
		return "RELOADING"

	magazine_by_peer[peer_id] = int(magazine_by_peer.get(peer_id, MAGAZINE_SIZE)) - 1
	next_fire_by_peer[peer_id] = now + FIRE_INTERVAL_USEC
	return ""


## Complete unlimited-reserve reload when the host timer reaches its deadline.
func _update_reload(peer_id: int, now: int) -> void:
	var deadline: int = int(reload_end_by_peer.get(peer_id, 0))
	if deadline > 0 and now >= deadline:
		magazine_by_peer[peer_id] = MAGAZINE_SIZE
		reload_end_by_peer[peer_id] = 0


## Find the nearest retained sample after clamping requested history to 250 ms.
func _rewound_position(target_id: String, requested_usec: int, now: int) -> Dictionary:
	var cutoff: int = now - MAX_REWIND_USEC
	var query: int = maxi(requested_usec, cutoff)
	var selected: Dictionary = history.back()
	var best_distance: int = absi(int(selected.usec) - query)
	for row: Dictionary in history:
		var distance: int = absi(int(row.usec) - query)
		if distance < best_distance:
			selected = row
			best_distance = distance

	return {"position": selected.positions[target_id], "usec": selected.usec,
		"clamped": requested_usec < cutoff}


## Test a finite ray against a top-down circular target cross-section.
func _ray_hits(origin: Vector3, direction: Vector3, target_position: Vector3,
		radius: float) -> bool:
	var relative: Vector3 = target_position - origin
	var along: float = relative.dot(direction)
	if along < 0.0 or along > MAX_RANGE_M:
		return false

	return (relative - direction * along).length() <= radius


## Record authoritative current/rewind verdicts on the requesting client.
@rpc("authority", "call_remote", "reliable", 0)
func _verdict(row: Dictionary) -> void:
	if role != "client":
		return

	if probes_sent:
		probe_responses += 1
	else:
		client_responses += 1
		if row.get("accepted", false):
			client_rows.append(row)
	receipt.emit({ "event": "verdict", "row": row })


## Send duplicate, nonfinite, and oversized probes through the actual RPC boundary.
func _send_validation_probes() -> void:
	probes_sent = true
	var base: Dictionary = {"session": session.session_id, "match": MATCH_REVISION,
		"sequence": SHOT_COUNT, "target": "pedestrian", "view_usec": _wall_usec(),
		"direction": Vector3.FORWARD, "client_hit": false}
	_fire_intent.rpc_id(1, base)
	base = base.duplicate()
	base.sequence = SHOT_COUNT + 1
	base.direction = Vector3(NAN, 0.0, -1.0)
	_fire_intent.rpc_id(1, base)
	base = base.duplicate()
	base.sequence = SHOT_COUNT + 2
	base.direction = Vector3.FORWARD
	base.extra = "x".repeat(MAX_INTENT_BYTES)
	_fire_intent.rpc_id(1, base)


## Send a locally predicted rocket launch while keeping impact authority on the host.
func _send_rocket() -> void:
	rocket_sent += 1
	_rocket_intent.rpc_id(1, {"session": session.session_id, "match": MATCH_REVISION,
		"sequence": rocket_sent, "sent_usec": _wall_usec()})


## Validate cooldown and return launch timing without accepting a client impact claim.
@rpc("any_peer", "call_remote", "reliable", 0)
func _rocket_intent(envelope: Dictionary) -> void:
	if role != "host":
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	var now: int = _wall_usec()
	var accepted: bool = session.roster.has(peer_id) and envelope.get("session") == (
		session.session_id) and envelope.get("match") == MATCH_REVISION and (
		envelope.get("sequence") is int) and envelope.get("sent_usec") is int and (
		now >= int(next_rocket_by_peer.get(peer_id, 0)))
	if accepted:
		next_rocket_by_peer[peer_id] = now + ROCKET_COOLDOWN_USEC
	_rocket_result.rpc_id(peer_id, {"sequence": envelope.get("sequence", -1),
		"accepted": accepted, "sent_usec": envelope.get("sent_usec", 0),
		"launch_usec": now})


## Measure predicted rocket lead when the authoritative launch receipt arrives.
@rpc("authority", "call_remote", "reliable", 0)
func _rocket_result(row: Dictionary) -> void:
	if role != "client":
		return

	rocket_responses += 1
	if row.get("accepted", false):
		var offset_m: float = ROCKET_SPEED_MPS * (
			int(row.launch_usec) - int(row.sent_usec)) / 1_000_000.0
		rocket_rows.append({ "sequence": row.sequence, "offset_m": offset_m })
	receipt.emit({ "event": "rocket", "row": row })


## Request the host's bounded memory/rejection summary after all client receipts.
@rpc("any_peer", "call_remote", "reliable", 0)
func _done(source_session: String, match_revision: int) -> void:
	if role != "host" or source_session != session.session_id or (
		match_revision != MATCH_REVISION):
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	var summary: Dictionary = {"history_peak_bytes": history_peak_bytes,
		"history_samples": history.size(), "rejections": host_rejections.duplicate(),
		"magazine": magazine_by_peer.get(peer_id, MAGAZINE_SIZE)}
	_host_summary.rpc_id(peer_id, summary)
	host_finished.emit(summary)


## Complete the client measurement with host-owned diagnostics attached.
@rpc("authority", "call_remote", "reliable", 0)
func _host_summary(host_summary: Dictionary) -> void:
	if role != "client":
		return

	client_finished.emit({"shots": client_rows, "rockets": rocket_rows,
		"host": host_summary, "attempts": SHOT_COUNT, "responses": client_responses})
	_finish_ack.rpc_id(1, session.session_id)


## Let the host close only after the client has retained its final summary.
@rpc("any_peer", "call_remote", "reliable", 0)
func _finish_ack(source_session: String) -> void:
	if role == "host" and source_session == session.session_id:
		receipt.emit({ "event": "finish_ack" })


## Count bounded rejection reasons for independent runner assertions.
func _count_rejection(reason: String) -> void:
	host_rejections[reason] = int(host_rejections.get(reason, 0)) + 1


## Return a shared-machine wall timestamp used only by this measurement fixture.
func _wall_usec() -> int:
	return int(Time.get_unix_time_from_system() * 1_000_000.0)
