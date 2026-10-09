class_name S03RActor
extends S02ActorMotion
## Adds fixture-only replica presentation; inherited step remains the only movement rule.

const INTERPOLATION_MS: int = 100
const MAX_SAMPLES: int = 8
const CORRECTION_SMOOTH_SECONDS: float = 0.1

var remote_view: bool = false
var predicted_local: bool = false
var samples: Array[Dictionary] = []
var latest_sequence: int = 0
var latest_predicted_tick: int = 0
var _correction_from: Transform3D = Transform3D.IDENTITY
var _correction_elapsed_seconds: float = CORRECTION_SMOOTH_SECONDS

@onready var _anchor: Node3D = $PresentationAnchor


## Interpolates remote samples or decays a local correction independently of physics.
func _process(delta: float) -> void:
	if remote_view:
		_interpolate_remote()
		return
	if not predicted_local:
		_anchor.transform = Transform3D.IDENTITY
		return

	_correction_elapsed_seconds = minf(
		_correction_elapsed_seconds + delta, CORRECTION_SMOOTH_SECONDS
	)
	var weight: float = _correction_elapsed_seconds / CORRECTION_SMOOTH_SECONDS
	_anchor.transform = _correction_from.interpolate_with(Transform3D.IDENTITY, weight)


## Smooths remote presentation behind receipt time without moving its physics replica.
func _interpolate_remote() -> void:
	if samples.size() < 2:
		_anchor.transform = Transform3D.IDENTITY
		return

	var target_ms: int = Time.get_ticks_msec() - INTERPOLATION_MS
	while samples.size() > 2 and int(samples[1].time) <= target_ms:
		samples.pop_front()

	var first: Dictionary = samples[0]
	var second: Dictionary = samples[1]
	var weight: float = clampf(float(target_ms - first.time) /
		maxf(1.0, float(second.time - first.time)), 0.0, 1.0)
	_anchor.global_transform = (first.transform as Transform3D).interpolate_with(
		second.transform, weight)


## Installs one host pose for an unpredicted or remotely interpolated replica.
func install_pose(pose: Dictionary, receipt_ms: int) -> void:
	restore_authority(pose)
	samples.append({ "time": receipt_ms, "transform": global_transform })
	if samples.size() > MAX_SAMPLES:
		samples.pop_front()


## Restores authoritative simulation state without emitting presentation or gameplay effects.
func restore_authority(pose: Dictionary) -> void:
	global_position = Vector3(pose.position[0], pose.position[1], pose.position[2])
	rotation.y = pose.yaw
	velocity = Vector3(pose.velocity[0], pose.velocity[1], pose.velocity[2])
	latest_sequence = int(pose.sequence)


## Keeps the old rendered transform while a corrected physics pose wins immediately.
func smooth_correction_from(previous_display: Transform3D) -> void:
	_correction_from = global_transform.affine_inverse() * previous_display
	_correction_elapsed_seconds = 0.0
	_anchor.transform = _correction_from


## Exposes the rendered transform before reconciliation changes the physics body.
func display_transform() -> Transform3D:
	return _anchor.global_transform


## Clears motion, prediction and interpolation before observers see a retired body.
func retire() -> void:
	neutralize()
	samples.clear()
	latest_predicted_tick = 0
	_correction_from = Transform3D.IDENTITY
	_correction_elapsed_seconds = CORRECTION_SMOOTH_SECONDS
	visible = false
	collision_layer = 0
	collision_mask = 0


## Exposes the actual rendered anchor pose separately from physics state.
func display_state() -> Dictionary:
	return { "position": _anchor.global_position, "yaw": _anchor.global_rotation.y }
