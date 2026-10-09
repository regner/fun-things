class_name S04Kinematic
extends CharacterBody3D
## Authoritative planar candidate; replica collision and simulation are explicitly passive.

var simulation_enabled: bool = false
var latest_sequence: int = 0


## Configures collision before tree entry; only the authoritative owner calls step.
func configure(authority: bool) -> void:
	simulation_enabled = authority
	collision_layer = S04DriveRules.CAR_COLLISION_LAYER if authority else 0
	collision_mask = S04DriveRules.CAR_COLLISION_MASK if authority else 0
	velocity = Vector3.ZERO


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
	global_position = Vector3(pose.position[0], pose.position[1], pose.position[2])
	rotation.y = pose.yaw
	velocity = Vector3(pose.velocity[0], pose.velocity[1], pose.velocity[2])
	latest_sequence = int(pose.sequence)


## Retires collision and motion before lifecycle completion is observable.
func retire() -> void:
	configure(false)
	visible = false
	latest_sequence = 0


## Reads physical state through the body boundary.
func motion_state() -> Dictionary:
	return { "position": global_position, "yaw": rotation.y, "velocity": velocity }


## Reads the presentation anchor separately from physics for drawn-frame telemetry.
func display_state() -> Dictionary:
	var anchor: Node3D = $PresentationAnchor
	return { "position": anchor.global_position, "yaw": anchor.global_rotation.y }
