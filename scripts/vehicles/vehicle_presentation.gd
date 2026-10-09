class_name VehiclePresentation
extends Node3D
## Drives imported wheel steering and spin from VehicleMotion telemetry only.

const MAX_STEER_ANGLE_RAD: float = 0.45
const WHEEL_RADIUS_M: float = 0.32
const FRONT_STEER_NAMES: Array[StringName] = [
	&"SteerFrontLeft",
	&"SteerFrontRight",
]
const SPIN_NAMES: Array[StringName] = [
	&"SpinFrontLeft",
	&"SpinFrontRight",
	&"SpinRearLeft",
	&"SpinRearRight",
]

var _front_steer_nodes: Array[Node3D] = []
var _spin_nodes: Array[Node3D] = []


## Resolves the stable source-authored wheel names once after the imported model is ready.
func _ready() -> void:
	for wheel_name: StringName in FRONT_STEER_NAMES:
		var wheel: Node = find_child(String(wheel_name), true, false)
		if wheel is Node3D:
			_front_steer_nodes.append(wheel as Node3D)
	for spin_name: StringName in SPIN_NAMES:
		var spin: Node = find_child(String(spin_name), true, false)
		if spin is Node3D:
			_spin_nodes.append(spin as Node3D)


## Applies steering and travelled-distance spin without querying gameplay collision.
func apply_motion(motion_state: Dictionary, delta_seconds: float) -> void:
	var steer: float = float(motion_state.steer)
	for wheel: Node3D in _front_steer_nodes:
		wheel.rotation.y = -steer * MAX_STEER_ANGLE_RAD

	var spin_delta: float = (
		-float(motion_state.forward_speed_mps) * delta_seconds / WHEEL_RADIUS_M
	)
	for spin: Node3D in _spin_nodes:
		spin.rotation.x = wrapf(spin.rotation.x + spin_delta, -PI, PI)


## Reports whether all imported wheel controls required by the presentation contract resolved.
func has_complete_wheel_rig() -> bool:
	return (
		_front_steer_nodes.size() == FRONT_STEER_NAMES.size()
		and _spin_nodes.size() == SPIN_NAMES.size()
	)
