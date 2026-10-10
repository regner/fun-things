class_name PlayerCharacterVisual
extends Node3D
## Presentation-only character with a stable skeleton and interchangeable compatible skins.

const RIG_BONE_COUNT: int = 28
const REST_TOLERANCE: float = 0.00001
const CONTACT_SAMPLE_COUNT: int = 24
const CONTACT_FOOT_BONE: StringName = &"foot_r"
const MOVEMENT_SPEED_EPSILON_MPS: float = 0.001

@export var appearance: PackedScene

var _contact_profiles: Dictionary[StringName, Vector2] = {}

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


## Play disjoint bone libraries and match authored foot contact travel to body speed.
func play_layered(
	locomotion: StringName,
	upper_body: StringName,
	movement_speed_mps: float = 0.0,
) -> bool:
	var lower: AnimationPlayer = $LowerBodyPlayer
	var upper: AnimationPlayer = $UpperBodyPlayer
	if not lower.has_animation(locomotion) or not upper.has_animation(upper_body):
		return false

	var playback_scale: float = locomotion_playback_scale(locomotion, movement_speed_mps)
	if playback_scale <= 0.0:
		return false

	_animation.stop()
	lower.speed_scale = playback_scale
	if lower.current_animation != locomotion or not lower.is_playing():
		lower.play(locomotion)
	if upper.current_animation != upper_body or not upper.is_playing():
		upper.play(upper_body)
	return true


## Derive playback from the clip's measured stance displacement without a visual-speed cap.
func locomotion_playback_scale(locomotion: StringName, movement_speed_mps: float) -> float:
	if movement_speed_mps <= MOVEMENT_SPEED_EPSILON_MPS:
		return 1.0

	var profile: Vector2 = _authored_contact_profile(locomotion)
	if profile.x <= 0.0 or profile.y <= 0.0:
		return 0.0
	return movement_speed_mps * profile.y / profile.x


## Measure one foot's maximum grounded travel and the lower of its two cycle arcs.
func _authored_contact_profile(locomotion: StringName) -> Vector2:
	if _contact_profiles.has(locomotion):
		return _contact_profiles[locomotion]

	var lower: AnimationPlayer = $LowerBodyPlayer
	var animation: Animation = lower.get_animation(locomotion)
	var foot_index: int = _skeleton.find_bone(CONTACT_FOOT_BONE)
	if animation == null or animation.length <= 0.0 or foot_index < 0:
		return Vector2.ZERO

	lower.play(locomotion)
	lower.speed_scale = 1.0
	var positions: Array[Vector3] = []
	for sample: int in range(CONTACT_SAMPLE_COUNT):
		lower.seek(animation.length * float(sample) / CONTACT_SAMPLE_COUNT, true)
		positions.append(_skeleton.get_bone_global_pose(foot_index).origin)
	lower.stop()

	var profile: Vector2 = _contact_profile_from_samples(positions, animation.length)
	_contact_profiles[locomotion] = profile
	return profile


## Find contact travel and duration among the grounded quarter of the vertical range.
func _contact_profile_from_samples(positions: Array[Vector3], cycle_seconds: float) -> Vector2:
	var endpoints: Vector3 = _contact_endpoints(positions)
	var start_index: int = int(endpoints.x)
	var end_index: int = int(endpoints.y)
	if start_index < 0 or end_index < 0:
		return Vector2.ZERO

	var direct_mean: float = _arc_mean_height(positions, start_index, end_index, false)
	var wrapped_mean: float = _arc_mean_height(positions, end_index, start_index, true)
	var direct_samples: int = end_index - start_index
	var stance_samples: int = direct_samples if direct_mean <= wrapped_mean else (
		positions.size() - direct_samples
	)
	return Vector2(endpoints.z, cycle_seconds * float(stance_samples) / positions.size())


## Locate the most separated low foot samples as stance endpoints.
func _contact_endpoints(positions: Array[Vector3]) -> Vector3:
	var minimum_y: float = INF
	var maximum_y: float = -INF
	for position: Vector3 in positions:
		minimum_y = minf(minimum_y, position.y)
		maximum_y = maxf(maximum_y, position.y)
	var contact_ceiling: float = minimum_y + (maximum_y - minimum_y) * 0.25
	var endpoints := Vector3(-1.0, -1.0, 0.0)

	for first: int in range(positions.size()):
		if positions[first].y > contact_ceiling:
			continue
		for second: int in range(first + 1, positions.size()):
			if positions[second].y > contact_ceiling:
				continue
			var delta: Vector3 = positions[second] - positions[first]
			delta.y = 0.0
			if delta.length() > endpoints.z:
				endpoints = Vector3(first, second, delta.length())
	return endpoints


## Average sampled foot height over one inclusive direct or wrapped cycle arc.
func _arc_mean_height(
	positions: Array[Vector3],
	start_index: int,
	end_index: int,
	wrapped: bool,
) -> float:
	var total: float = 0.0
	var count: int = 0
	var index: int = start_index
	while true:
		total += positions[index].y
		count += 1
		if index == end_index:
			break
		index = (index + 1) % positions.size() if wrapped else index + 1
	return total / count


## Select an authored bone-to-grip frame; weapon scenes attach beneath this stable marker.
func select_grip(profile: StringName) -> bool:
	if not _grip_profiles.has(profile):
		return false
	$Sockets/WeaponMount.transform = _grip_profiles[profile]
	return true
