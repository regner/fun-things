extends SceneTree
## Deterministic 20 fps review recording of the saved imported animations, not a performance test.

const OUTPUT: String = "/tmp/brackett-pedestrian-production/motion_frames/"
const PREVIEW: String = (
	"res://tests/assets/characters/pedestrian_worker/pedestrian_worker_a_preview.tscn"
)


## Start after the main loop can own the saved preview scene.
func _initialize() -> void:
	_capture.call_deferred()


## Sample imported clips through their presentation API and capture the saved overview camera.
func _capture() -> void:
	Engine.max_fps = 60
	root.size = Vector2i(1280, 800)
	DirAccess.make_dir_recursive_absolute(OUTPUT)
	var scene: Node3D = load(PREVIEW).instantiate()
	root.add_child(scene)
	current_scene = scene
	scene.get_node("OverviewCamera").make_current()
	scene.get_node("ReviewLabels/Context").text = (
		"OFF-SHIFT WORKER / IMPORTED NPC CLIPS\n"
		+ "Left to right: death · run · walk · idle / independent colours\n"
		+ "20 fps review recording / separate game-camera still available"
	)
	for frame: int in 64:
		var time: float = frame / 20.0
		for actor: Node3D in scene.get_node("Workers").get_children():
			actor.play_clip(actor.initial_clip, 0)
			var player: AnimationPlayer = actor.animation_player()
			var length: float = player.get_animation("npc/" + actor.initial_clip).length
			player.seek(
				minf(time, length) if actor.initial_clip == "death" else fmod(time, length),
				true,
			)
			player.advance(0)
			player.pause()
		# Sequential frame waits are required so each finite sample is fully rendered.
		await process_frame  # gdstyle:ignore=quality/await-in-loop
		await RenderingServer.frame_post_draw  # gdstyle:ignore=quality/await-in-loop
		root.get_texture().get_image().save_png(OUTPUT + "%03d.png" % frame)
	print("WORKER_MOTION_CAPTURE 64 frames, 1280x800, 20 fps sampling")
	quit()
