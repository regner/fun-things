class_name S04Dynamic
extends RigidBody3D
## Upright planar rigid candidate; custom handling retains engine contact solving.

signal sampled(pose: Dictionary)

var simulation_enabled: bool = false
var command: Dictionary = S04DriveRules.neutral()
var solver_tick: int = 0
var command_sequence: int = 0
var completed_sequence: int = 0


## Freezes passive engine physics explicitly before tree entry, independent of script processing.
func configure(authority: bool) -> void:
	simulation_enabled = authority
	freeze_mode = RigidBody3D.FREEZE_MODE_STATIC
	freeze = not authority
	custom_integrator = true
	gravity_scale = 0.0
	collision_layer = S04DriveRules.CAR_COLLISION_LAYER if authority else 0
	collision_mask = S04DriveRules.CAR_COLLISION_MASK if authority else 0
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO
	sleeping = not authority
	command = S04DriveRules.neutral()


## Supplies intent only; the physics solver callback owns simulation.
func set_command(value: Dictionary, sequence: int) -> void:
	command = value.duplicate()
	command_sequence = sequence


## Captures the completed prior solver interval before writing the next interval's velocity.
func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
	if not simulation_enabled:
		return

	solver_tick += 1
	var yaw: float = state.transform.basis.get_euler().y
	sampled.emit({"tick": solver_tick, "position": state.transform.origin,
		"yaw": yaw, "velocity": state.linear_velocity,
		"sequence": completed_sequence, "contacts": state.get_contact_count(),
		"phase": "solver_entry_prior_interval"})
	var next: Dictionary = S04DriveRules.advance(state.linear_velocity, yaw, command, state.step)
	state.linear_velocity = next.velocity
	state.angular_velocity = Vector3(0.0, next.yaw_rate, 0.0)
	completed_sequence = command_sequence


## Parks the surviving car without transferring engine authority to a driver.
func neutralize() -> void:
	command = S04DriveRules.neutral()
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO


## Returns current solved state for independent body outcome checks.
func motion_state() -> Dictionary:
	return { "position": global_position, "yaw": rotation.y, "velocity": linear_velocity }


## Retires both script-driven intent and engine-driven motion.
func retire() -> void:
	configure(false)
	visible = false
