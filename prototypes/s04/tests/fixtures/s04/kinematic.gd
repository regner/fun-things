class_name S04Kinematic
extends CharacterBody3D
## Authoritative planar candidate; replica collision and simulation are explicitly passive.

const CORRECTION_DECAY_PER_SECOND: float = 12.0

var simulation_enabled: bool = false
var latest_sequence: int = 0
var latest_input_tick: int = 0
var latest_authoritative_speed_mps: float = 0.0

@onready var _presentation_anchor: Node3D = $PresentationAnchor


## Decays reconciliation offsets on the visual child without changing collision simulation.
func _process(delta: float) -> void:
	if not is_instance_valid(_presentation_anchor):
		return

	var weight: float = 1.0 - exp(-CORRECTION_DECAY_PER_SECOND * delta)
	_presentation_anchor.position = _presentation_anchor.position.lerp(Vector3.ZERO, weight)
	_presentation_anchor.rotation.y = lerp_angle(_presentation_anchor.rotation.y, 0.0, weight)


## Configures collision before tree entry; only the authoritative owner calls step.
func configure(authority: bool) -> void:
	simulation_enabled = authority
	collision_layer = S04DriveRules.CAR_COLLISION_LAYER if authority else 0
	collision_mask = S04DriveRules.CAR_COLLISION_MASK if authority else 0
	velocity = Vector3.ZERO


## Enables the locally owned replica to run the same collision and drive-rule path.
func configure_prediction() -> void:
	simulation_enabled = true
	collision_layer = S04DriveRules.CAR_COLLISION_LAYER
	collision_mask = S04DriveRules.CAR_COLLISION_MASK


## Advances shared handling once on the physics callback and captures solved wall contact.
func step(command: Dictionary, delta: float, tuning: Resource = null) -> void:
	assert(simulation_enabled)
	var next: Dictionary = S04DriveRules.advance(velocity, rotation.y, command, delta, tuning)
	rotation.y = wrapf(rotation.y + float(next.yaw_rate) * delta, -PI, PI)
	velocity = next.velocity
	move_and_slide()
	# Floating mode retains attempted velocity at a wall; carry solved motion into next tick.
	velocity = get_real_velocity()


## Stops control-driven motion for reauthorization and parked-car teardown.
func neutralize() -> void:
	velocity = Vector3.ZERO


## Installs authoritative movement only; seat/equipment are owned by the match binding.
func install_pose(pose: Dictionary, _receipt_ms: int) -> void:
	assert(not simulation_enabled)
	_restore_pose(pose)


## Restores host state before bounded replay on the locally predicted body.
func restore_authoritative(pose: Dictionary) -> void:
	assert(simulation_enabled)
	_restore_pose(pose)


## Keeps the pre-correction visual pose while simulation immediately adopts corrected state.
func preserve_visual_pose(previous_position: Vector3, previous_yaw: float) -> void:
	_presentation_anchor.global_position = previous_position
	_presentation_anchor.global_rotation.y = previous_yaw


## Installs movement fields without touching seat, health or other authoritative components.
func _restore_pose(pose: Dictionary) -> void:
	global_position = Vector3(pose.position[0], pose.position[1], pose.position[2])
	rotation.y = pose.yaw
	velocity = Vector3(pose.velocity[0], pose.velocity[1], pose.velocity[2])
	latest_sequence = int(pose.sequence)
	latest_input_tick = int(pose.input_tick)
	latest_authoritative_speed_mps = velocity.length()


## Retires collision and motion before lifecycle completion is observable.
func retire() -> void:
	configure(false)
	visible = false
	latest_sequence = 0
	latest_input_tick = 0
	latest_authoritative_speed_mps = 0.0
	if is_instance_valid(_presentation_anchor):
		_presentation_anchor.position = Vector3.ZERO
		_presentation_anchor.rotation = Vector3.ZERO


## Reads physical state through the body boundary.
func motion_state() -> Dictionary:
	return { "position": global_position, "yaw": rotation.y, "velocity": velocity }


## Reads the presentation anchor separately from physics for drawn-frame telemetry.
func display_state() -> Dictionary:
	var anchor: Node3D = $PresentationAnchor
	return { "position": anchor.global_position, "yaw": anchor.global_rotation.y }
