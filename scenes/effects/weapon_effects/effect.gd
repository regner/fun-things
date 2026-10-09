extends Node3D
## Presentation-only saved effect; the integrator owns event identity and instance allocation.

signal finished

@export var settle_seconds: float = 1.6
@export var continuous: bool = false

var _active: bool = false
var _emitting: bool = false
var _elapsed_seconds: float = 0.0


## Keep imported particle assemblies idle until an explicit presentation request arrives.
func _ready() -> void:
	visible = false
	set_process(false)


## Publish completion after all authored particles have settled.
func _process(delta: float) -> void:
	if _emitting:
		return

	_elapsed_seconds += delta
	if _elapsed_seconds < settle_seconds:
		return

	clear()
	finished.emit()


## Retain an active effect; callers allocate another root for another accepted event.
func play() -> bool:
	if _active:
		return false

	_active = true
	_emitting = continuous
	_elapsed_seconds = 0.0
	visible = true
	for child: Node in get_children():
		if child is GPUParticles3D:
			child.restart()
			child.emitting = true

	set_process(true)
	return true


## Stop future trail emission while existing world-space puffs finish their authored lifetime.
func stop_emission() -> void:
	if not _active or not continuous:
		return

	_emitting = false
	_elapsed_seconds = 0.0
	for child: Node in get_children():
		if child is GPUParticles3D:
			child.emitting = false


## Clear presentation during teardown; this does not alter any gameplay outcome.
func clear() -> void:
	_active = false
	_emitting = false
	_elapsed_seconds = 0.0
	visible = false
	for child: Node in get_children():
		if child is GPUParticles3D:
			child.emitting = false

	set_process(false)


## Expose presentation occupancy so an external allocator can retain every accepted event.
func is_active() -> bool:
	return _active
