extends Node  # gdstyle:ignore=quality/max-class-variables
## Drives production vehicle replication and prediction through two real ENet processes.

const PREFIX: String = "M1-B1.1 "
const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const REMOTE_PARTICIPANT_ID: int = 2
const PROCESS_TIMEOUT_MSEC: int = 45_000
const COMMAND_TICKS: int = 460
const RESULT_GRACE_TICKS: int = 90

var _role: String = ""
var _port: int = 0
var _deadline_msec: int = 0
var _match: Node3D
var _replication: MatchReplication
var _granted: bool = false
var _entry_requested: bool = false
var _entry_confirmed: bool = false
var _vehicle_id: int = 0
var _sequence: int = 0
var _test_ticks: int = 0
var _movement_receipts: int = 0
var _prediction_before_authority: bool = false
var _start_position: Vector3 = Vector3.INF
var _contact_vehicle: VehicleMotion
var _wall_contact_observed: bool = false
var _moving_contact_observed: bool = false
var _phase_outcomes: Dictionary[StringName, bool] = {
	&"straight": false,
	&"turn": false,
	&"brake": false,
	&"reverse": false,
	&"handbrake": false,
}
var _phase_evidence: Dictionary[StringName, Dictionary] = {}
var _phase_start_position: Vector3 = Vector3.ZERO
var _phase_start_yaw: float = 0.0
var _phase_start_speed: float = 0.0
var _phase_min_speed: float = INF
var _authority_mode: StringName = &""
var _finished: bool = false

@onready var _session: SessionService = $Session
@onready var _transport: ENetTransport = $Session/ENetTransport


## Starts one bounded host or client through the production SessionService path.
func _ready() -> void:
	Engine.max_fps = 60
	_parse_arguments()
	if _role not in ["host", "client"] or _port <= 0:
		_finish(false, "arguments")
		return
	_session.changed.connect(_on_session_changed)
	_transport.peer_ready.connect(_on_transport_peer_ready)
	_session.participant_admitted.connect(_on_participant_admitted)
	_session.participant_disconnected.connect(_on_participant_disconnected)
	if not _session.register_transport(_transport).get("ok", false):
		_finish(false, "transport registration")
		return

	_deadline_msec = Time.get_ticks_msec() + PROCESS_TIMEOUT_MSEC
	if _role == "host":
		_session.host(
			{
				"provider_id": &"enet",
				"district_id": &"brackett_island",
				"capacity": 2,
				"provider_options": { "port": _port, "bind_address": "127.0.0.1" },
			}
		)
	else:
		var parsed: Dictionary = _transport.parse_endpoint("127.0.0.1", _port)
		_session.join(parsed.target)


## Samples one numbered drive frame per client physics tick and checks bounded completion.


# gdstyle:ignore=quality/max-returns,quality/max-branches,quality/max-function-length
func _physics_process(delta_seconds: float) -> void:
	if _finished:
		return
	if Time.get_ticks_msec() >= _deadline_msec:
		_finish(false, "deadline")
		return
	if not is_instance_valid(_replication):
		return
	if _vehicle_id == 0 and _role == "host":
		_prepare_host_entry()
	elif _vehicle_id == 0 and _role == "client":
		_try_client_entry()
		var binding: Dictionary = _replication._vehicle_replicator.binding_for_participant(
			REMOTE_PARTICIPANT_ID
		)
		_vehicle_id = int(binding.get("id", 0))
	if _vehicle_id == 0:
		return

	var vehicle: VehicleMotion = _replication.vehicle_for_entity(_vehicle_id)
	if vehicle == null:
		return
	if _start_position == Vector3.INF:
		_start_position = vehicle.global_position
	_observe_contacts(vehicle)
	if _role == "client" and not _granted:
		return
	if _role == "client" and _test_ticks < COMMAND_TICKS:
		_submit_profile_command(vehicle, delta_seconds)
		return
	var authority_acknowledgement: int = (
		_replication._vehicle_replicator.acknowledgement(REMOTE_PARTICIPANT_ID)
	)
	if _role == "host" and authority_acknowledgement == 0:
		return
	if _role == "host":
		_measure_authority_phase(vehicle, authority_acknowledgement)
	if _role == "host" and _test_ticks < 120:
		_step_contact_vehicle(delta_seconds)

	_test_ticks += 1
	if _test_ticks < COMMAND_TICKS + RESULT_GRACE_TICKS:
		return
	var displacement: float = vehicle.global_position.distance_to(_start_position)
	var prediction: Dictionary = _replication.vehicle_prediction_diagnostics()
	var phases_complete: bool = not false in _phase_outcomes.values()
	var ok: bool = displacement > 0.5
	if _role == "host":
		ok = ok and phases_complete and _wall_contact_observed and _moving_contact_observed
	else:
		ok = (
			ok
			and _entry_confirmed
			and _prediction_before_authority
			and phases_complete
			and _movement_receipts > 1
			and int(prediction.get("acknowledgement", 0)) > 1
			and int(prediction.get("reconciliation_count", 0)) > 1
			and int(prediction.get("history_size", 0)) <= VehiclePrediction.HISTORY_CAPACITY
		)
	_finish(
		ok,
		"complete",
		{
			"displacement_metres": displacement,
			"entry_confirmed": _entry_confirmed,
			"phase_evidence": _phase_evidence,
			"phase_outcomes": _phase_outcomes,
			"moving_contact_observed": _moving_contact_observed,
			"wall_contact_observed": _wall_contact_observed,
			"movement_receipts": _movement_receipts,
			"prediction": prediction,
			"prediction_before_authority": _prediction_before_authority,
		},
	)


## Emits readiness only after ENet published the bound host endpoint.
func _on_transport_peer_ready(operation_id: int, _peer: MultiplayerPeer) -> void:
	if _role == "host":
		_print_event({ "event": "host_ready", "operation_id": operation_id })


## Instantiates the saved production Match after Session reaches ACTIVE.
func _on_session_changed(view: Dictionary) -> void:
	if view.phase != SessionService.PHASE_ACTIVE or is_instance_valid(_match):
		return
	_match = MATCH_SCENE.instantiate() as Node3D
	add_child(_match)
	_replication = _match.get_node("Replication") as MatchReplication
	_replication.set_local_input_enabled(false)
	_replication.input_granted.connect(_on_input_granted)
	_replication.movement_applied.connect(_on_movement_applied)
	_replication.vehicle_action_resolved.connect(_on_vehicle_action_resolved)
	if not _replication.configure_network(
		view.session_id,
		view.local_participant_id,
		view.operation_kind == SessionService.OPERATION_HOST,
	):
		_finish(false, "match configuration")


## Mirrors Session mapping before the client requests a production seat transaction.
func _on_participant_admitted(native_peer_id: int, participant_id: int) -> void:
	if not is_instance_valid(_replication):
		_finish(false, "host match missing")
		return
	if not _replication.admit_peer(native_peer_id, participant_id):
		_finish(false, "participant handoff")
		return
	_prepare_host_entry()


## Applies production disconnect cleanup to the confirmed seat transaction.
func _on_participant_disconnected(native_peer_id: int, participant_id: int) -> void:
	if is_instance_valid(_replication):
		_replication.remove_peer(native_peer_id, participant_id)


## Places the authoritative remote actor at an authored entry before client intent arrives.
func _prepare_host_entry() -> void:
	if _role != "host" or _vehicle_id != 0:
		return
	var actor: ActorMotion = _replication.actor_for_participant(REMOTE_PARTICIPANT_ID)
	if actor == null:
		return
	var descriptors: Array[Dictionary] = _replication._vehicle_replicator.descriptor_rows()
	if descriptors.is_empty():
		return
	_vehicle_id = int(descriptors[0].id)
	var vehicle: VehicleMotion = _replication.vehicle_for_entity(_vehicle_id)
	var entry: Marker3D = vehicle.get_node("Sockets/EntryLeft") as Marker3D
	actor.global_position = entry.global_position
	_configure_contact_vehicle()
	_print_event({ "event": "entry_ready", "vehicle_id": _vehicle_id })


## Sends the production reliable entry intent only after client admission is granted.
func _try_client_entry() -> void:
	if _role != "client" or not _granted or _entry_requested:
		return
	var descriptors: Array[Dictionary] = _replication._vehicle_replicator.descriptor_rows()
	if descriptors.is_empty():
		return
	_entry_requested = _replication.request_local_vehicle_entry(int(descriptors[0].id), 1)
	if not _entry_requested:
		_finish(false, "vehicle entry request")
		return
	_print_event({ "event": "entry_requested", "vehicle_id": int(descriptors[0].id) })


## Records the processed reliable result while descriptor state remains the control writer.
func _on_vehicle_action_resolved(result: Dictionary) -> void:
	if int(result.get("action_sequence", 0)) != 1:
		return
	if result.get("status") != VehicleInteraction.STATUS_APPLIED:
		_finish(false, "vehicle entry rejected")
		return
	_entry_confirmed = true
	_print_event({ "event": "entry_confirmed" })


## Opens deterministic drive input only after baseline and handoff grant.
func _on_input_granted(participant_id: int) -> void:
	if participant_id != REMOTE_PARTICIPANT_ID:
		return
	_granted = true
	var binding: Dictionary = _replication._vehicle_replicator.binding_for_participant(
		participant_id
	)
	_vehicle_id = int(binding.get("id", 0))
	_print_event({ "event": "input_granted", "vehicle_id": _vehicle_id })


## Counts authoritative movement receipts separately from immediate prediction.
func _on_movement_applied(participant_id: int) -> void:
	if participant_id == REMOTE_PARTICIPANT_ID:
		_movement_receipts += 1


## Places one authority-only crossing car for real moving-contact replication proof.
func _configure_contact_vehicle() -> void:
	for descriptor: Dictionary in _replication._vehicle_replicator.descriptor_rows():
		var entity_id: int = int(descriptor.id)
		if entity_id == _vehicle_id:
			continue
		_contact_vehicle = _replication.vehicle_for_entity(entity_id)
		_contact_vehicle.global_position = Vector3(-109.0, 0.05, -3.0)
		_contact_vehicle.rotation.y = 0.0
		return


## Advances the crossing car through the same production authority motion step.
func _step_contact_vehicle(delta_seconds: float) -> void:
	if not is_instance_valid(_contact_vehicle):
		return
	var command := DriveCommand.new(
		maxi(1, _test_ticks + 1),
		maxi(1, _test_ticks + 1),
		1.0,
		0.0,
		0.0,
		false,
	)
	_contact_vehicle.step(command, delta_seconds, VehicleMotion.StepMode.AUTHORITY)
	_observe_contacts(_contact_vehicle)


## Records actual CharacterBody contacts with the authored wall and crossing car.
func _observe_contacts(vehicle: VehicleMotion) -> void:
	for index: int in range(vehicle.get_slide_collision_count()):
		var collision: KinematicCollision3D = vehicle.get_slide_collision(index)
		var collider: Object = collision.get_collider()
		if collider is VehicleMotion:
			_moving_contact_observed = true
		elif collider is StaticBody3D and (collider as Node).name == &"ContactWall":
			_wall_contact_observed = true


## Submits straight, turn, brake, reverse, and handbrake frames in one bounded run.
func _submit_profile_command(vehicle: VehicleMotion, delta_seconds: float) -> void:
	_sequence += 1
	_test_ticks += 1
	var controls: Dictionary = _controls_for_tick(_test_ticks)
	if _test_ticks in [1, 91, 171, 271, 371]:
		_begin_phase(vehicle)
	var before_position: Vector3 = vehicle.global_position
	var receipts_before: int = _movement_receipts
	var command := DriveCommand.new(
		_sequence,
		_sequence,
		float(controls.throttle),
		float(controls.steer),
		float(controls.brake),
		bool(controls.handbrake),
	)
	if not _replication.predict_and_submit_local_vehicle_command(command, delta_seconds):
		_finish(false, "command rejected")
		return
	if (
		_movement_receipts == receipts_before
		and vehicle.global_position.distance_to(before_position) > 0.0001
	):
		_prediction_before_authority = true
	_measure_phase_outcome(vehicle, StringName(controls.mode), _test_ticks)


## Captures body state at the start of one behavioral acceptance phase.
func _begin_phase(vehicle: VehicleMotion) -> void:
	_phase_start_position = vehicle.global_position
	_phase_start_yaw = vehicle.rotation.y
	_phase_start_speed = vehicle.velocity.length()
	_phase_min_speed = _phase_start_speed


## Proves each control phase changed motion rather than merely submitting input.
func _measure_phase_outcome(vehicle: VehicleMotion, mode: StringName, tick: int) -> void:
	var speed: float = vehicle.velocity.length()
	_phase_min_speed = minf(_phase_min_speed, speed)
	if mode == &"straight" and tick == 90:
		var distance: float = vehicle.global_position.distance_to(_phase_start_position)
		_phase_outcomes[mode] = distance > 1.0
		_phase_evidence[mode] = { "distance_metres": distance }
	elif mode == &"turn" and tick == 170:
		var heading_change: float = absf(angle_difference(_phase_start_yaw, vehicle.rotation.y))
		_phase_outcomes[mode] = heading_change > 0.05
		_phase_evidence[mode] = { "heading_change_radians": heading_change }
	elif mode == &"brake" and tick == 270:
		var deceleration: float = _phase_start_speed - _phase_min_speed
		_phase_outcomes[mode] = deceleration > 0.5
		_phase_evidence[mode] = {
			"deceleration_mps": deceleration,
			"start_speed_mps": _phase_start_speed,
			"minimum_speed_mps": _phase_min_speed,
		}
	elif mode == &"reverse":
		var forward_speed: float = float(vehicle.motion_state().forward_speed_mps)
		if forward_speed < -0.25:
			_phase_outcomes[mode] = true
			_phase_evidence[mode] = { "forward_speed_mps": forward_speed }
	elif mode == &"handbrake" and tick == COMMAND_TICKS:
		var speed_reduction: float = _phase_start_speed - _phase_min_speed
		var handbrake_yaw: float = absf(angle_difference(_phase_start_yaw, vehicle.rotation.y))
		_phase_outcomes[mode] = speed_reduction > 0.25 and handbrake_yaw > 0.02
		_phase_evidence[mode] = {
			"heading_change_radians": handbrake_yaw,
			"speed_reduction_mps": speed_reduction,
		}


## Measures the same behavioral outcomes from the host's consumed acknowledgement phases.
func _measure_authority_phase(vehicle: VehicleMotion, acknowledgement: int) -> void:
	var mode: StringName = StringName(_controls_for_tick(acknowledgement).mode)
	if mode != _authority_mode:
		if _authority_mode != &"":
			_finalize_authority_phase(vehicle, _authority_mode)
		_authority_mode = mode
		_begin_phase(vehicle)

	_phase_min_speed = minf(_phase_min_speed, vehicle.velocity.length())
	if mode == &"reverse":
		var forward_speed: float = float(vehicle.motion_state().forward_speed_mps)
		if forward_speed < -0.25:
			_phase_outcomes[mode] = true
			_phase_evidence[mode] = { "forward_speed_mps": forward_speed }
	elif mode == &"handbrake" and acknowledgement >= COMMAND_TICKS:
		_finalize_authority_phase(vehicle, mode)


## Finalizes one authoritative phase using observed body motion, not submitted intent.
func _finalize_authority_phase(vehicle: VehicleMotion, mode: StringName) -> void:
	if mode == &"straight":
		var distance: float = vehicle.global_position.distance_to(_phase_start_position)
		_phase_outcomes[mode] = distance > 1.0
		_phase_evidence[mode] = { "distance_metres": distance }
	elif mode == &"turn":
		var heading_change: float = absf(angle_difference(_phase_start_yaw, vehicle.rotation.y))
		_phase_outcomes[mode] = heading_change > 0.05
		_phase_evidence[mode] = { "heading_change_radians": heading_change }
	elif mode == &"brake":
		var deceleration: float = _phase_start_speed - _phase_min_speed
		_phase_outcomes[mode] = deceleration > 0.5
		_phase_evidence[mode] = {
			"deceleration_mps": deceleration,
			"start_speed_mps": _phase_start_speed,
			"minimum_speed_mps": _phase_min_speed,
		}
	elif mode == &"handbrake":
		var speed_reduction: float = _phase_start_speed - _phase_min_speed
		var heading_change: float = absf(angle_difference(_phase_start_yaw, vehicle.rotation.y))
		_phase_outcomes[mode] = speed_reduction > 0.25 and heading_change > 0.02
		_phase_evidence[mode] = {
			"heading_change_radians": heading_change,
			"speed_reduction_mps": speed_reduction,
		}


## Returns one complete phase command without changing the shared handling rule.
func _controls_for_tick(tick: int) -> Dictionary:
	if tick <= 90:
		return _controls(&"straight", 1.0, 0.0, 0.0, false)
	if tick <= 170:
		return _controls(&"turn", 0.7, 0.25, 0.0, false)
	if tick <= 270:
		return _controls(&"brake", 0.0, 0.0, 1.0, false)
	if tick <= 370:
		return _controls(&"reverse", -0.5, -0.2, 0.0, false)
	return _controls(&"handbrake", 0.5, 0.2, 0.0, true)


## Builds one concise deterministic phase row for the integration driver.
func _controls(
	mode: StringName,
	throttle: float,
	steer: float,
	brake: float,
	handbrake: bool,
) -> Dictionary:
	return {
		"mode": mode,
		"throttle": throttle,
		"steer": steer,
		"brake": brake,
		"handbrake": handbrake,
	}


## Reads only bounded role and port arguments after the Godot separator.
func _parse_arguments() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			_role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			_port = argument.trim_prefix("--port=").to_int()


## Emits one terminal result and exits with a truthful status.
func _finish(ok: bool, detail: String, evidence: Dictionary = {}) -> void:
	if _finished:
		return
	_finished = true
	var event: Dictionary = { "event": "finished", "ok": ok, "detail": detail }
	event.merge(evidence)
	_print_event(event)
	get_tree().quit(0 if ok else 1)


## Prints one machine-readable readiness or result receipt.
func _print_event(event: Dictionary) -> void:
	event["role"] = _role
	print(PREFIX + JSON.stringify(event))
