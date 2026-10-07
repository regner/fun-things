extends SceneTree
## Captures actual rendered candidate views and records projection measurements.

const FIXTURE: PackedScene = preload("res://tests/fixtures/s02/corner.tscn")
const STUDIES: PackedScene = preload("res://tests/fixtures/s02/weapon_studies.tscn")
const SETTLE_FRAMES: int = 30

var _fixture: S02Fixture
var _output: String
var _measurements: Array[Dictionary] = []


## Starts the graphical capture sequence after scene-tree initialization.
func _initialize() -> void:
	root.show()
	_run.call_deferred()


## Captures matched settings, tower approaches and three source-authored held silhouettes.
func _run() -> void:
	_output = OS.get_environment("S02_CAPTURE_DIR")
	if _output.is_empty():
		push_error("S02_CAPTURE_DIR must name a writable evidence directory")
		quit(1)
		return

	_fixture = FIXTURE.instantiate() as S02Fixture
	_fixture.manual_mode = true
	root.add_child(_fixture)
	await process_frame
	for fov: float in [50.0, 42.0]:
		_fixture.rig.set_candidate_fov(fov)
		_fixture.actor.position = Vector3(0, 0.001, 6)
		await _capture("start_%d" % fov)  # gdstyle:ignore=quality/await-in-loop
		_fixture.actor.position = Vector3(0, 0.001, -8)
		await _capture("alley_%d" % fov)  # gdstyle:ignore=quality/await-in-loop

	_fixture.rig.set_candidate_fov(42.0)
	_fixture.actor.position = Vector3(3.57, 0.001, 3)
	await _capture("blocked_target_42")
	_fixture.actor.position = Vector3(3.57, 0.001, -9)
	await _capture("clear_target_42")
	_fixture.actor.position = Vector3(5.61, 0.001, -9)
	_fixture.actor.rotation.y = -PI / 2.0
	await _capture("tower_edge_42")
	_fixture.actor.position = Vector3(0, 0.001, -14)
	_fixture.actor.rotation.y = 0.0
	await _capture("between_towers_42")
	var file: FileAccess = FileAccess.open(_output.path_join("camera-measurements.json"),
		FileAccess.WRITE)
	file.store_string(JSON.stringify(_measurements, "\t") + "\n")
	file.close()
	_fixture.queue_free()
	await process_frame
	var studies: Node3D = STUDIES.instantiate()
	root.add_child(studies)
	for frame: int in SETTLE_FRAMES:
		await process_frame  # gdstyle:ignore=quality/await-in-loop
	RenderingServer.force_draw()
	var error: Error = root.get_texture().get_image().save_png(
		_output.path_join("held_weapons_47m_42deg.png")
	)
	assert(error == OK)
	studies.queue_free()
	await process_frame
	quit()


## Waits for live rendering, saves the viewport, and records matching camera/actor data.
func _capture(label: String) -> void:
	_fixture.rig.bind(_fixture.actor)
	for frame: int in SETTLE_FRAMES:
		# Frame progression and draw completion prevent cached/suspended-image evidence.
		await process_frame  # gdstyle:ignore=quality/await-in-loop
	RenderingServer.force_draw()
	var camera: Camera3D = _fixture.rig.camera()
	var actor_position: Vector3 = _fixture.actor.global_position
	var shoulder_left: Vector2 = camera.unproject_position(actor_position + Vector3(-0.375, 1.4, 0))
	var shoulder_right: Vector2 = camera.unproject_position(actor_position + Vector3(0.375, 1.4, 0))
	var image: Image = root.get_texture().get_image()
	var error: Error = image.save_png(_output.path_join(label + ".png"))
	assert(error == OK)
	_measurements.append({
		"capture": label, "viewport": str(root.size), "camera": str(camera.global_transform),
		"fov": camera.fov, "near": camera.near, "far": camera.far,
		"actor": str(actor_position), "shoulder_span_px": shoulder_left.distance_to(shoulder_right),
		"renderer": RenderingServer.get_current_rendering_method(),
	})
	print("S02_CAPTURE ", label, " ", image.get_size())
