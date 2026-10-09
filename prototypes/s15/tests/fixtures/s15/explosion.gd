extends Node3D
## Reusable saved explosion presentation with a guaranteed reduced-quality tier.

var _active: bool = true


## Binds each saved linked Blender mesh as its matching particle draw pass.
func _ready() -> void:
	for child: Node in get_children():
		if child is GPUParticles3D:
			var source_root: Node = child.get_node("MeshSource")
			var source: MeshInstance3D = source_root.get_child(0) as MeshInstance3D
			child.draw_pass_1 = source.mesh


## Enables or disables this authored effect slot without removing it from the stress scene.
func set_active(active: bool) -> void:
	_active = active
	visible = active
	process_mode = Node.PROCESS_MODE_INHERIT if active else Node.PROCESS_MODE_DISABLED
	for child: Node in get_children():
		if child is GPUParticles3D:
			child.emitting = false


## Applies a bounded particle ratio while retaining at least one particle per emitter.
func set_quality(ratio: float) -> void:
	for child: Node in get_children():
		if child is GPUParticles3D:
			var minimum_ratio: float = 1.0 / float(child.amount)
			child.amount_ratio = clampf(ratio, minimum_ratio, 1.0)


## Restarts every authored layer together; reduced quality never drops the effect root.
func trigger() -> void:
	if not _active:
		return

	for child: Node in get_children():
		if child is GPUParticles3D:
			child.restart()
