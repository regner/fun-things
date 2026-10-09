extends SceneTree
## Bounded API/resource checks; this headless harness makes no pixel or performance claim.

const DIRECTORY: String = "res://scenes/effects/weapon_effects/weapon_effects_a_"

var _finished_counts: Dictionary = {}


## Start after the SceneTree exists; no authored visible hierarchy is constructed here.
func _initialize() -> void:
	_run.call_deferred()


## Fail the process explicitly instead of allowing a diagnostic-only assertion to pass CI.
func _require(condition: bool, message: String) -> void:
	if not condition:
		push_error(message)
		quit(1)
		assert(false, message)


## Count completion through the public signal and identify each independent instance.
func _on_finished(label: String) -> void:
	_finished_counts[label] += 1


## Instantiate saved resources and validate idle, busy, expiry, trail stop and restart behavior.
func _run() -> void:
	var effects: Array[Node3D] = []
	for index: int in range(14):
		var kind: String = "explosion" if index < 12 else "muzzle" if index == 12 else "hit"
		var packed: PackedScene = load(DIRECTORY + kind + ".tscn")
		_require(packed != null, "Missing saved scene: " + kind)
		var effect: Node3D = packed.instantiate()
		effect.name = "Effect" + str(index)
		root.add_child(effect)
		_finished_counts[effect.name] = 0
		effect.finished.connect(_on_finished.bind(str(effect.name)))
		_require(not effect.is_active() and not effect.visible, "Effect must start idle")
		_require(effect.play(), "Fresh root rejected an event")
		_require(not effect.play(), "Busy root accepted a destructive retrigger")
		_require(effect.is_active() and effect.visible, "Busy request erased an active effect")
		for emitter: Node in effect.get_children():
			_require(emitter is GPUParticles3D and emitter.emitting, "Missing visible emitter")
			_require(emitter.draw_pass_1 is ArrayMesh, "Draw mesh is not a source import")
			_require(emitter.draw_pass_1.resource_path.ends_with("_mesh.res"), "Embedded mesh")
			_require(emitter.get_node("MeshSource").scene_file_path.ends_with(".glb"),
				"Missing linked source")

		effects.append(effect)

	var trail: Node3D = load(DIRECTORY + "trail.tscn").instantiate()
	root.add_child(trail)
	_require(trail.play(), "Trail did not start")
	await create_timer(1.8).timeout
	for effect: Node3D in effects:
		_require(not effect.is_active() and not effect.visible, "One-shot did not finish")
		_require(_finished_counts[effect.name] == 1, "Completion signal count incorrect")
		_require(effect.play(), "Settled root cannot be reused")
		effect.clear()
		_require(not effect.visible and not effect.is_active(), "Explicit clear failed")
		effect.queue_free()

	_require(trail.is_active() and trail.visible, "Continuous trail expired before stop")
	trail.stop_emission()
	_require(trail.is_active() and trail.visible, "Trail popped out instead of settling")
	for emitter: GPUParticles3D in trail.get_children():
		_require(not emitter.emitting and not emitter.local_coords, "Trail stop/space mismatch")

	await create_timer(0.8).timeout
	_require(not trail.is_active() and not trail.visible, "Stopped trail did not settle")
	trail.queue_free()
	print("WEAPON_EFFECTS_API_PASS 12 independent explosions; muzzle; hit; continuous trail")
	quit(0)
