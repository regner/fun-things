class_name S04BodyComparison
extends Node3D
## Independent bounded outcomes through saved candidate APIs, not copied movement formulas.

const TICK_SECONDS: float = 1.0 / 60.0
const SETTLE_TICKS: int = 3
const WALL_MIN_Z_M: float = -17.85
const RESPONSE_MIN_YAW_RAD: float = PI / 4.0

var failures: Array[String] = []
var solver_samples: Array[Dictionary] = []

@onready var kinematic: S04Kinematic = $Kinematic
@onready var dynamic: S04Dynamic = $Dynamic
@onready var passive: S04Dynamic = $Passive


## Sets saved bodies' roles before their callbacks or engine physics can start.
func _enter_tree() -> void:
	($Kinematic as S04Kinematic).configure(false)
	($Dynamic as S04Dynamic).configure(false)
	($Passive as S04Dynamic).configure(false)


## Serializes identical track cases and explicitly checks the untouched passive engine body.
func _ready() -> void:  # gdstyle:ignore=quality/await-in-loop
	dynamic.sampled.connect(_on_solver_sample)
	_check_handbrake_rule()
	_check_sideways_handbrake_rule()
	var passive_origin: Vector3 = passive.global_position
	await _compare(kinematic)
	kinematic.retire()
	await _compare(dynamic)
	dynamic.retire()

	await _advance(null, S04DriveRules.neutral(), 30)
	_expect(passive.global_position == passive_origin and passive.freeze
		and passive.freeze_mode == RigidBody3D.FREEZE_MODE_STATIC
		and passive.collision_mask == 0 and passive.collision_layer == 0
		and passive.linear_velocity == Vector3.ZERO and passive.angular_velocity == Vector3.ZERO,
		"passive engine body drifted or retained collision")
	_record({"event": "comparison_result", "ok": failures.is_empty(), "failures": failures,
		"solver_samples": solver_samples.size(), "passive_unchanged": (
			passive.global_position == passive_origin)})
	get_tree().quit(0 if failures.is_empty() else 1)


## Checks handbrake deceleration and throttle suppression through the shared public rule API.
func _check_handbrake_rule() -> void:
	var command: Dictionary = S04DriveRules.neutral()
	command.handbrake = true
	var velocity: Vector3 = Vector3(0.0, 0.0, -20.0)
	for _tick: int in 60:
		velocity = S04DriveRules.advance(
			velocity, 0.0, command, TICK_SECONDS
		).velocity

	_expect(absf(velocity.length() - 10.0) < 0.05,
		"default handbrake did not reduce 20 m/s to about 10 m/s after one second")
	command.throttle = 1.0
	var throttled: Vector3 = Vector3(0.0, 0.0, -5.0)
	for _tick: int in 15:
		throttled = S04DriveRules.advance(
			throttled, 0.0, command, TICK_SECONDS
		).velocity

	_expect(throttled.length() <= 5.0,
		"throttle accelerated while the handbrake was held")
	command.throttle = 0.0
	command.brake = 1.0
	var service_braked: Vector3 = Vector3(0.0, 0.0, -20.0)
	for _tick: int in 30:
		service_braked = S04DriveRules.advance(
			service_braked, 0.0, command, TICK_SECONDS
		).velocity

	_expect(absf(service_braked.length() - 11.0) < 0.05,
		"service brake did not override weaker handbrake deceleration")
	_record({"event": "rule_case", "case": "handbrake",
		"one_second_speed_mps": velocity.length(),
		"throttle_held_speed_mps": throttled.length(),
		"combined_brake_speed_mps": service_braked.length()})


## Checks full-vector handbrake scrub and sideways steering through the public rule API.
func _check_sideways_handbrake_rule() -> void:
	var command: Dictionary = S04DriveRules.neutral()
	command.handbrake = true
	var sideways: Vector3 = Vector3(15.0, 0.0, 0.0)
	for _tick: int in 60:
		sideways = S04DriveRules.advance(
			sideways, 0.0, command, TICK_SECONDS
		).velocity

	_expect(absf(sideways.length() - 5.0) < 0.05,
		"sideways handbrake did not scrub 15 m/s to about 5 m/s after one second")
	command.steer = 1.0
	var steering: Dictionary = S04DriveRules.advance(
		Vector3(12.0, 0.0, 0.0), 0.0, command, TICK_SECONDS
	)
	_expect(absf(float(steering.yaw_rate) + 1.5) < 0.001,
		"sideways handbrake slide lost full steering authority")
	command.handbrake = false
	var ordinary_steering: Dictionary = S04DriveRules.advance(
		Vector3(12.0, 0.0, 0.0), 0.0, command, TICK_SECONDS
	)
	_expect(float(ordinary_steering.yaw_rate) == 0.0,
		"sideways ordinary motion gained steering authority")
	_record({"event": "rule_case", "case": "sideways_handbrake",
		"one_second_speed_mps": sideways.length(), "yaw_rate": steering.yaw_rate,
		"ordinary_yaw_rate": ordinary_steering.yaw_rate})


## Uses independent speed/heading/contact expectations for both adapters on one authored track.
func _compare(body: Node3D) -> void:
	_reset(body, Vector3(15.0, 0.001, 10.0), Vector3.ZERO)
	var forward: Dictionary = {"throttle": 1.0, "steer": 0.0,
		"brake": 0.0, "handbrake": false}
	await _advance(body, forward, 120)
	var acceleration: Dictionary = body.motion_state()
	_expect(acceleration.velocity.length() > 8.0, body.name + " slow acceleration")
	_expect(absf(acceleration.position.x - 15.0) < 0.05, body.name + " straight lateral drift")
	_record({"event": "body_case", "body": body.name, "case": "acceleration",
		"state": _encode(acceleration)})

	_reset(body, Vector3(15.0, 0.001, 10.0), Vector3(0.0, 0.0, -10.0))
	var braking: Dictionary = S04DriveRules.neutral()
	braking.brake = 1.0
	await _advance(body, braking, 60)
	var stopped: Dictionary = body.motion_state()
	_expect(stopped.velocity.length() < 0.2, body.name + " brake did not settle")
	_record({"event": "body_case", "body": body.name, "case": "braking",
		"distance_m": stopped.position.distance_to(Vector3(15.0, 0.001, 10.0)),
		"state": _encode(stopped)})

	_reset(body, Vector3(15.0, 0.001, 10.0), Vector3(0.0, 0.0, -10.0))
	var steering: Dictionary = forward.duplicate()
	steering.steer = 1.0
	await _advance(body, steering, 60)
	var turned: Dictionary = body.motion_state()
	_expect(absf(turned.yaw) > RESPONSE_MIN_YAW_RAD, body.name + " steering did not turn")
	_record({"event": "body_case", "body": body.name, "case": "turning",
		"extent_m": turned.position.distance_to(Vector3(15.0, 0.001, 10.0)),
		"state": _encode(turned)})

	await _compare_contact(body)


## Compares lateral retention and wall recovery in serial normally paced cases.
func _compare_contact(body: Node3D) -> void:  # gdstyle:ignore=quality/await-in-loop
	var forward: Dictionary = { "throttle": 1.0, "steer": 0.0,
		"brake": 0.0, "handbrake": false }
	var lateral: Array[float] = []
	var planar_speed: Array[float] = []
	for sliding: bool in [false, true]:
		_reset(body, Vector3(15.0, 0.001, 10.0), Vector3(5.0, 0.0, -5.0))
		var grip: Dictionary = S04DriveRules.neutral()
		grip.handbrake = sliding
		# Serial cases must complete before resetting the same engine body.
		await _advance(body, grip, 30)  # gdstyle:ignore=quality/await-in-loop
		var velocity: Vector3 = body.motion_state().velocity
		lateral.append(absf(velocity.x))
		planar_speed.append(Vector2(velocity.x, velocity.z).length())

	var slip_share: Array[float] = [
		lateral[0] / planar_speed[0], lateral[1] / planar_speed[1],
	]
	_expect(lateral[1] >= lateral[0] * 4.0,
		body.name + " handbrake did not retain four times ordinary lateral speed")
	_expect(slip_share[1] >= slip_share[0] + 0.25,
		body.name + " handbrake did not retain a materially higher slip share")
	_record({"event": "body_case", "body": body.name, "case": "slide",
		"ordinary_lateral_mps": lateral[0], "handbrake_lateral_mps": lateral[1],
		"ordinary_slip_share": slip_share[0], "handbrake_slip_share": slip_share[1]})

	_reset(body, Vector3(0.0, 0.001, -10.0), Vector3.ZERO)
	await _advance(body, forward, 120)
	var contact: Dictionary = body.motion_state()
	_expect(contact.position.z >= WALL_MIN_Z_M and contact.position.z < -17.0,
		body.name + " wall containment failed")
	var reverse: Dictionary = S04DriveRules.neutral()
	reverse.throttle = -1.0
	await _advance(body, reverse, 60)
	var recovered: Dictionary = body.motion_state()
	_expect(recovered.position.z > contact.position.z + 2.0,
		body.name + " reverse failed to recover from wall")
	_record({"event": "body_case", "body": body.name, "case": "wall_recovery",
		"contact": _encode(contact), "recovered": _encode(recovered)})


## Resets only dynamic test state between declared cases, never authored track placement.
func _reset(body: Node3D, position_m: Vector3, velocity_mps: Vector3) -> void:
	body.configure(false)
	body.global_position = position_m
	body.rotation = Vector3.ZERO
	body.configure(true)
	if body is S04Kinematic:
		body.velocity = velocity_mps
	else:
		body.linear_velocity = velocity_mps
	body.visible = true


## Runs normal engine-paced ticks with one custom step or one solver-owned integration.
func _advance(
	body: Node3D,
	command: Dictionary,
	ticks: int,
) -> void:  # gdstyle:ignore=quality/await-in-loop
	for tick: int in ticks:
		# Normal physics pacing is the measurement; no forced render or bulk stepping.
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
		if body is S04Kinematic:
			body.step(command, TICK_SECONDS)
		elif body is S04Dynamic:
			body.set_command(command, tick + 1)


## Retains actual solver-phase samples for contact and acknowledgement interpretation.
func _on_solver_sample(pose: Dictionary) -> void:
	solver_samples.append(pose)
	_record({"event": "solver_sample", "tick": pose.tick, "sequence": pose.sequence,
		"phase": pose.phase, "contacts": pose.contacts, "state": _encode(pose)})


## Collects outcome failures without dropping subsequent useful comparison evidence.
func _expect(condition: bool, reason: String) -> void:
	if not condition:
		failures.append(reason)


## Encodes physical state for independent analysis without native Variant objects.
func _encode(state: Dictionary) -> Dictionary:
	var position_m: Vector3 = state.position
	var velocity_mps: Vector3 = state.velocity
	return {"position": [position_m.x, position_m.y, position_m.z],
		"velocity": [velocity_mps.x, velocity_mps.y, velocity_mps.z], "yaw": state.yaw}


## Records monotonic experiment receipts independently of simulation rule calculations.
func _record(value: Dictionary) -> void:
	value["time_ms"] = Time.get_ticks_msec()
	print("S04 " + JSON.stringify(value))
