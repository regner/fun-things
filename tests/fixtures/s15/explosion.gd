extends Node3D
## Reusable saved explosion presentation with a guaranteed reduced-quality tier.

var _active: bool = true


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
