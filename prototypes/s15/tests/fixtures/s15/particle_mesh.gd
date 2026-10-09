extends GPUParticles3D
## Binds a saved linked Blender mesh instance as this particle emitter's draw pass.

@onready var mesh_source: MeshInstance3D = $MeshSource.get_child(0) as MeshInstance3D


## Installs the imported mesh resource without copying vertex data into the owned scene.
func _ready() -> void:
	draw_pass_1 = mesh_source.mesh
