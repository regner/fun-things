@tool
class_name PedestrianWorkerVisual
extends Node3D
## Source-linked civilian presentation. The integrator owns simulation and lifecycle.

const REGIONS: PackedStringArray = [
	"skin", "jacket", "yoke", "trousers", "cap", "shirt", "boots", "trim", "hair",
]
const CLIPS: PackedStringArray = ["idle", "walk", "run", "death"]

@export var palette: PackedColorArray = PackedColorArray([
	Color("b77d53"), Color("eca23e"), Color("326dc0"), Color("48596c"), Color("22525d"),
	Color("26333b"), Color("202b32"), Color("e2d6b9"), Color("392c25"),
]):
	set(colors):
		if colors.size() != REGIONS.size():
			return
		palette = colors.duplicate()
		_apply_palette_uniforms()

@export var palette_material: ShaderMaterial
@export var npc_library: AnimationLibrary
@export_enum("idle", "walk", "run", "death") var initial_clip: String = "idle"

var _mesh: MeshInstance3D
var _player: AnimationPlayer


## Configure shared resources and independent instance parameters after model import.
func _ready() -> void:
	_mesh = $PresentationAnchor/Visuals/Model.find_child("WorkerMesh", true, false)
	_player = $PresentationAnchor/Visuals/Model.find_child("AnimationPlayer", true, false)
	assert(_mesh != null and _player != null, "Worker import contract changed")
	_mesh.material_override = palette_material
	apply_palette(palette)
	for library_name: StringName in _player.get_animation_library_list():
		_player.remove_animation_library(library_name)
	_player.add_animation_library(&"npc", npc_library)
	play_clip(initial_clip, 0.0)
	if Engine.is_editor_hint():
		_player.seek(0.0, true)
		_player.pause()


## Set all nine regions without mutating the material shared by other instances.
func apply_palette(colors: PackedColorArray) -> bool:
	if colors.size() != REGIONS.size():
		return false
	palette = colors
	return true


## Play a civilian clip; death naturally holds its final pose until another clip is requested.
func play_clip(clip: String, blend_seconds: float = 0.12) -> bool:
	if clip not in CLIPS or not is_instance_valid(_player):
		return false
	_player.play("npc/" + clip, maxf(0.0, blend_seconds))
	return true


## Expose the existing imported player for asset review and presentation coordination.
func animation_player() -> AnimationPlayer:
	return _player


## Refresh per-instance uniforms for both Inspector changes and runtime API calls.
func _apply_palette_uniforms() -> void:
	if not is_instance_valid(_mesh):
		return
	for index: int in REGIONS.size():
		_mesh.set_instance_shader_parameter(REGIONS[index] + "_color", palette[index])
