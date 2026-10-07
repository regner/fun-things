class_name S02BuildingView
extends Node3D
## Local presentation-only cutaway; saved collision and placement are never modified.

const CUTAWAY: Shader = preload("res://tests/fixtures/s02/actor_cutaway.gdshader")
const PROTECTED_RADIUS_PX: float = 30.0

@export var cutaway_enabled: bool = true

var _materials: Array[ShaderMaterial] = []


## Creates local material instances while retaining imported meshes and palette colors.
func _ready() -> void:
	for node: Node in $Visuals/Model.find_children("*", "MeshInstance3D", true, false):
		var mesh: MeshInstance3D = node as MeshInstance3D
		var source: StandardMaterial3D = mesh.get_active_material(0) as StandardMaterial3D
		# One local material per imported mesh prevents cross-instance visual mutation.
		# gdstyle:ignore=quality/allocation-in-loop
		var material: ShaderMaterial = ShaderMaterial.new()
		material.shader = CUTAWAY
		material.set_shader_parameter("base_color", source.albedo_color)
		mesh.material_override = material
		_materials.append(material)


## Protects a small actual-camera disc around the actor, including its held silhouette.
func protect_actor(camera: Camera3D, position: Vector3) -> void:
	var viewport_height: float = camera.get_viewport().get_visible_rect().size.y
	var cone_radius: float = (
		tan(deg_to_rad(camera.fov * 0.5)) * PROTECTED_RADIUS_PX * 2.0 / viewport_height
	) if cutaway_enabled else 0.0
	for material: ShaderMaterial in _materials:
		material.set_shader_parameter("camera_world", camera.global_position)
		material.set_shader_parameter("actor_world", position)
		material.set_shader_parameter("cone_radius", cone_radius)
