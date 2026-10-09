extends Node3D
## Technical shared-rig presentation with palette and explicit animation-detail controls.

const LOOPING_STATES: Array[StringName] = [&"idle", &"walk", &"run"]

@export var palette_material: Material
@export var benchmark_visible: bool = true
@export var start_at_death_final: bool = false

var _animation_player: AnimationPlayer
var _current_state: StringName = &"idle"
var _throttling_enabled: bool = false
var _death_final: bool = false

@onready var _notifier: VisibleOnScreenNotifier3D = $VisibleOnScreenNotifier3D


## Resolves imported presentation children and applies saved appearance/state.
func _ready() -> void:
	_animation_player = find_child("AnimationPlayer", true, false) as AnimationPlayer
	if _animation_player == null:
		push_error("S13 character requires the imported AnimationPlayer")
		return

	_apply_palette()
	_animation_player.animation_finished.connect(_on_animation_finished)
	_notifier.screen_entered.connect(_on_screen_entered)
	_notifier.screen_exited.connect(_on_screen_exited)
	if start_at_death_final:
		set_death_final_pose()
	else:
		set_animation_state(&"idle")


## Selects one imported technical clip without changing simulation state.
func set_animation_state(state: StringName) -> void:
	if _animation_player == null or state not in [&"idle", &"walk", &"run", &"death"]:
		return

	_current_state = state
	_death_final = false
	_animation_player.active = not _throttling_enabled or benchmark_visible
	_animation_player.play(state)


## Installs and freezes the authored final death pose for a static corpse presentation.
func set_death_final_pose() -> void:
	if _animation_player == null or not _animation_player.has_animation(&"death"):
		return

	_current_state = &"death"
	_death_final = true
	_animation_player.active = true
	_animation_player.play(&"death")
	_animation_player.seek(_animation_player.get_animation(&"death").length, true)
	_animation_player.pause()
	_animation_player.active = false


## Enables full-rate updates or visibility-gated updates for non-death animations.
func set_animation_throttling(enabled: bool) -> void:
	_throttling_enabled = enabled
	if _animation_player == null or _death_final:
		return

	_animation_player.active = not enabled or benchmark_visible


## Reports whether this presentation currently spends AnimationPlayer process work.
func is_animation_active() -> bool:
	return _animation_player != null and _animation_player.active


## Returns the imported clip names exposed by the presentation API.
func get_animation_names() -> PackedStringArray:
	if _animation_player == null:
		return PackedStringArray()

	return _animation_player.get_animation_list()


## Returns the imported rig's stable bone names for fixture validation.
func get_bone_names() -> PackedStringArray:
	var skeleton: Skeleton3D = find_child("Skeleton3D", true, false) as Skeleton3D
	var names := PackedStringArray()
	if skeleton == null:
		return names

	for bone_index: int in skeleton.get_bone_count():
		names.append(skeleton.get_bone_name(bone_index))
	return names


## Returns imported triangle count without copying or generating render geometry.
func get_triangle_count() -> int:
	var triangle_count: int = 0
	for child: Node in find_children("*", "MeshInstance3D", true, false):
		var mesh_instance: MeshInstance3D = child as MeshInstance3D
		if mesh_instance.mesh != null:
			triangle_count += mesh_instance.mesh.get_faces().size() / 3
	return triangle_count


## Applies a wrapper-owned material override while retaining the linked imported mesh.
func _apply_palette() -> void:
	if palette_material == null:
		return

	for child: Node in find_children("*", "MeshInstance3D", true, false):
		var mesh_instance: MeshInstance3D = child as MeshInstance3D
		mesh_instance.material_override = palette_material


## Repeats only locomotion clips; death remains a one-shot final pose.
func _on_animation_finished(animation_name: StringName) -> void:
	if animation_name == _current_state and animation_name in LOOPING_STATES:
		_animation_player.play(_current_state)


## Resumes visibility-gated locomotion when any camera renders the character bounds.
func _on_screen_entered() -> void:
	if _throttling_enabled and not _death_final:
		_animation_player.active = true


## Stops visibility-gated locomotion when no camera renders the character bounds.
func _on_screen_exited() -> void:
	if _throttling_enabled and not _death_final:
		_animation_player.active = false
