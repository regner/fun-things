extends Node
## Drives two real SessionService processes through saved Match replication and remote walking.

const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const SESSION_IDENTITY_TIMEOUT_MSEC: int = 15_000
const HOST_RESULT_GRACE_MSEC: int = 750
const REMOTE_PARTICIPANT_ID: int = 2
const REMOTE_START_X: float = -80.0
const REQUIRED_MOVEMENT_METRES: float = 0.5

var _role: String = ""
var _port: int = 0
var _deadline_msec: int = 0
var _match: Node3D
var _replication: MatchReplication
var _granted: bool = false
var _sequence: int = 0
var _receipt_printed: bool = false
var _host_result_msec: int = 0

@onready var _session: SessionService = $Session
@onready var _transport: ENetTransport = $Session/ENetTransport


## Starts one host or client through the production SessionService boundary.
func _ready() -> void:
	Engine.max_fps = 60
	_parse_arguments()
	if _role not in ["host", "client"] or _port <= 0:
		_finish(false, "arguments")
		return

	_session.changed.connect(_on_session_changed)
	_session.participant_admitted.connect(_on_participant_admitted)
	_session.participant_disconnected.connect(_on_participant_disconnected)
	if not _session.register_transport(_transport).get("ok", false):
		_finish(false, "transport registration")
		return

	_deadline_msec = Time.get_ticks_msec() + SESSION_IDENTITY_TIMEOUT_MSEC
	if _role == "host":
		_session.host(
			{
				"provider_id": &"enet",
				"district_id": &"brackett_island",
				"capacity": 4,
				"provider_options": { "port": _port },
			}
		)
	else:
		var parsed: Dictionary = _transport.parse_endpoint("127.0.0.1", _port)
		_session.join(parsed.target)


## Submits deterministic client intent and verifies both processes observe authority movement.
func _physics_process(_delta: float) -> void:
	if Time.get_ticks_msec() >= _deadline_msec:
		_finish(false, "deadline")
		return
	if not is_instance_valid(_replication):
		return

	if _role == "client" and _granted:
		_sequence += 1
		_replication.submit_local_command(
			FootCommand.new(_sequence, _sequence, Vector2.RIGHT, 0.0, false, false)
		)
	_check_replication_result()


## Loads the same saved Match on both sides only after Session admission is active.
func _on_session_changed(view: Dictionary) -> void:
	if view.phase != SessionService.PHASE_ACTIVE or is_instance_valid(_match):
		return

	_match = MATCH_SCENE.instantiate() as Node3D
	add_child(_match)
	_replication = _match.get_node("Replication") as MatchReplication
	_replication.set_local_input_enabled(false)
	_replication.input_granted.connect(_on_input_granted)
	if not _replication.configure_network(
		view.session_id,
		view.local_participant_id,
		view.operation_kind == SessionService.OPERATION_HOST,
	):
		_finish(false, "match configuration")


## Mirrors the production Boot handoff from Session-owned peer mapping to Match.
func _on_participant_admitted(native_peer_id: int, participant_id: int) -> void:
	if not is_instance_valid(_replication):
		_finish(false, "host match missing")
		return
	if not _replication.admit_peer(native_peer_id, participant_id):
		_finish(false, "participant handoff")


## Applies production disconnect cleanup if a process exits before the receipt.
func _on_participant_disconnected(native_peer_id: int, participant_id: int) -> void:
	if is_instance_valid(_replication):
		_replication.remove_peer(native_peer_id, participant_id)


## Opens deterministic intent only after baseline installation and reliable handoff.
func _on_input_granted(participant_id: int) -> void:
	_granted = participant_id == REMOTE_PARTICIPANT_ID


## Requires both courier bodies and authority movement visible in the local Match.
func _check_replication_result() -> void:
	if (
		_receipt_printed
		and _role == "host"
		and Time.get_ticks_msec() >= _host_result_msec
	):
		get_tree().quit(0)
		return
	if _replication.player_count() != 2:
		return
	var remote_actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if remote_actor == null or remote_actor.global_position.x < (
		REMOTE_START_X + REQUIRED_MOVEMENT_METRES
	):
		return

	if not _receipt_printed:
		_receipt_printed = true
		print(
			"M1-A2.2 "
			+ _role
			+ " "
			+ JSON.stringify(
				{
					"match_loaded": is_instance_valid(_match),
					"ok": true,
					"players": _replication.player_count(),
					"remote_x": remote_actor.global_position.x,
				}
			)
		)
	if _role == "client":
		get_tree().quit(0)
	elif _host_result_msec == 0:
		_host_result_msec = Time.get_ticks_msec() + HOST_RESULT_GRACE_MSEC
	elif Time.get_ticks_msec() >= _host_result_msec:
		get_tree().quit(0)


## Reads only the harness role and endpoint arguments after the Godot separator.
func _parse_arguments() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			_role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			_port = argument.trim_prefix("--port=").to_int()


## Emits one machine-readable process result before bounded failure exit.
func _finish(ok: bool, detail: String) -> void:
	print(
		"M1-A2.2 "
		+ _role
		+ " "
		+ JSON.stringify({ "detail": detail, "ok": ok })
	)
	get_tree().quit(0 if ok else 1)
