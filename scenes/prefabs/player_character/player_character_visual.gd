class_name PlayerCharacterVisual
extends Node3D
## Presentation-only character with a stable skeleton and interchangeable compatible skins.

const RIG_BONE_COUNT: int = 28
const REST_TOLERANCE: float = 0.00001

@export var appearance: PackedScene

@onready var _grip_profiles: Dictionary = get_meta("authored_grip_profiles", {})
@onready var _model: Node3D = $PresentationAnchor/Visuals/Model
@onready var _animation: AnimationPlayer = $AnimationPlayer
@onready var _skeleton: Skeleton3D = _model.get_node("Rig/Skeleton3D")
@onready var _skin: MeshInstance3D = _model.find_children("*", "MeshInstance3D", true, false)[0]


## Apply an optional compatible skin after the saved scene's skeleton enters the tree.
func _ready() -> void:
	if appearance != null:
		if not apply_skin(appearance):
			push_error("Player skin does not match shared_humanoid/1.0.0")


## Replace only mesh and inverse-bind resources; preserve skeleton, clips and playback time.
func apply_skin(candidate: PackedScene) -> bool:
	if candidate == null:
		return false

	var source: Node = candidate.instantiate()
	var source_skeleton: Skeleton3D = source.find_child("Skeleton3D", true, false) as Skeleton3D
	var meshes: Array[Node] = source.find_children("*", "MeshInstance3D", true, false)
	var compatible: bool = source_skeleton != null and meshes.size() == 1
	if compatible:
		compatible = _compatible_skeleton(source_skeleton)

	if compatible:
		var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
		compatible = _identity_chain(mesh) and _identity_chain(source_skeleton)
		compatible = compatible and mesh.mesh != null and _compatible_bind(mesh, source_skeleton)
		if compatible:
			_skin.mesh = mesh.mesh
			_skin.skin = mesh.skin
			appearance = candidate

	source.free()
	return compatible


## Reject transformed skin hierarchies rather than dropping their authored offsets.
func _identity_chain(node: Node) -> bool:
	var current: Node = node
	while current != null:
		if current is Node3D and not current.transform.is_equal_approx(Transform3D.IDENTITY):
			return false
		current = current.get_parent()
	return true


## Validate named inverse binds against the candidate's canonical global rest transforms.
func _compatible_bind(mesh: MeshInstance3D, skeleton: Skeleton3D) -> bool:
	if mesh.skin == null or mesh.skin.get_bind_count() == 0:
		return false
	for index: int in range(mesh.skin.get_bind_count()):
		var name: StringName = mesh.skin.get_bind_name(index)
		var bone: int = skeleton.find_bone(name) if name != &"" else mesh.skin.get_bind_bone(index)
		if bone < 0 or bone >= RIG_BONE_COUNT:
			return false
		var expected: Transform3D = skeleton.get_bone_global_rest(bone).affine_inverse()
		if not _same_transform(mesh.skin.get_bind_pose(index), expected):
			return false
	return true


## Compare rest and bind transforms with the documented import tolerance.
func _same_transform(actual: Transform3D, expected: Transform3D) -> bool:
	if actual.origin.distance_to(expected.origin) > REST_TOLERANCE:
		return false
	for axis: int in range(3):
		if actual.basis[axis].distance_to(expected.basis[axis]) > REST_TOLERANCE:
			return false
	return true


## Reject changed rest poses, bone ordering or hierarchy instead of guessing a retarget.
func _compatible_skeleton(candidate: Skeleton3D) -> bool:
	if candidate.get_bone_count() != RIG_BONE_COUNT or _skeleton.get_bone_count() != RIG_BONE_COUNT:
		return false

	for index: int in range(RIG_BONE_COUNT):
		if candidate.get_bone_name(index) != _skeleton.get_bone_name(index):
			return false

		if candidate.get_bone_parent(index) != _skeleton.get_bone_parent(index):
			return false

		var expected: Transform3D = _skeleton.get_bone_rest(index)
		var actual: Transform3D = candidate.get_bone_rest(index)
		if actual.origin.distance_to(expected.origin) > REST_TOLERANCE:
			return false

		for axis: int in range(3):
			if actual.basis[axis].distance_to(expected.basis[axis]) > REST_TOLERANCE:
				return false

	return true


## Select a presentation clip; simulation and authoritative state remain external.
func play_clip(clip: StringName) -> bool:
	var key: StringName = StringName("player/" + str(clip))
	if not _animation.has_animation(key):
		return false

	$UpperBodyPlayer.stop()
	$LowerBodyPlayer.stop()
	_animation.play(key)
	return true


## Expose the existing skeleton for attachment/configuration consumers without replacing it.
func get_skeleton() -> Skeleton3D:
	return _skeleton


## Expose the existing animation player for asset-local inspection and playback controls.
func get_animation_player() -> AnimationPlayer:
	return _animation


## Play disjoint bone libraries for motion relative to a separately aimed character heading.
func play_layered(locomotion: StringName, upper_body: StringName) -> bool:
	var lower: AnimationPlayer = $LowerBodyPlayer
	var upper: AnimationPlayer = $UpperBodyPlayer
	if not lower.has_animation(locomotion) or not upper.has_animation(upper_body):
		return false
	_animation.stop()
	lower.play(locomotion)
	upper.play(upper_body)
	return true


## Select an authored bone-to-grip frame; weapon scenes attach beneath this stable marker.
func select_grip(profile: StringName) -> bool:
	if not _grip_profiles.has(profile):
		return false
	$Sockets/WeaponMount.transform = _grip_profiles[profile]
	return true
