class_name PlayerPreviewCapture
extends SceneTree
## Bounded 60 FPS capture of a saved asset preview; no gameplay or authored placement.


## Load the existing review scene and defer capture until rendering is ready.
func _initialize() -> void:
	Engine.max_fps = 60
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	root.size = Vector2i(1280, 800)
	var path: String = OS.get_environment("PLAYER_SCENE")
	if path.is_empty():
		path = "res://scenes/prefabs/player_character/preview.tscn"
	var packed: PackedScene = load(path)
	root.add_child(packed.instantiate())
	capture.call_deferred()


## Save one native-resolution image after a bounded rendering warmup and quit.
func capture() -> void:
	# Bounded render warmup, not a simulation loop.
	for frame: int in range(12):
		await process_frame  # gdstyle:ignore=quality/await-in-loop
	await RenderingServer.frame_post_draw
	var scene: Node = root.get_child(root.get_child_count() - 1)
	var overlay: CanvasLayer = scene.get_node_or_null("ReviewOverlay")
	if overlay != null:
		overlay.hide()
	var actor: PlayerCharacterVisual = scene.get_node("Courier")
	var player: AnimationPlayer = actor.get_animation_player()
	if not OS.get_environment("PLAYER_SEQUENCE").is_empty():
		await capture_sequence(actor, player)
		quit()
		return
	var clip: String = OS.get_environment("PLAYER_CLIP")
	if clip.is_empty():
		clip = "idle"
	assert(actor.play_clip(StringName(clip)))
	player.pause()
	player.seek(float(OS.get_environment("PLAYER_TIME")), true)
	var weapon: String = OS.get_environment("PLAYER_WEAPON")
	if not weapon.is_empty():
		assert(actor.select_grip(StringName(weapon)))
		actor.get_node("Sockets/WeaponMount/" + weapon.capitalize()).show()
	if OS.get_environment("PLAYER_CAMERA") == "game":
		scene.get_node("GameCamera").make_current()
	await process_frame
	await RenderingServer.frame_post_draw
	var output: String = OS.get_environment("PLAYER_CAPTURE_PATH")
	assert(not output.is_empty())
	var error: Error = root.get_texture().get_image().save_png(output)
	assert(error == OK)
	print("PLAYER_CAPTURE_SAVED ", output)
	quit()


## Record a finite 30 FPS sequence by sampling saved clips; no new motion is authored here.
func capture_sequence(actor: PlayerCharacterVisual, player: AnimationPlayer) -> void:
	var directory: String = OS.get_environment("PLAYER_SEQUENCE")
	assert(DirAccess.make_dir_recursive_absolute(directory) == OK)
	var frame_number: int = 0
	var clips: Array[StringName] = [
		&"idle", &"walk", &"run", &"pistol_hold", &"smg_hold", &"launcher_hold", &"death",
	]
	for clip: StringName in clips:
		for weapon: String in ["pistol", "smg", "launcher"]:
			var model: Node3D = actor.get_node("Sockets/WeaponMount/" + weapon.capitalize())
			model.visible = str(clip).begins_with(weapon)
			if model.visible:
				assert(actor.select_grip(StringName(weapon)))
		assert(actor.play_clip(clip))
		player.pause()
		var duration: float = 1.2 if clip == &"death" else 1.0
		for frame: int in range(int(duration * 30) + 1):
			player.seek(frame / 30.0, true)
			await process_frame  # gdstyle:ignore=quality/await-in-loop
			await RenderingServer.frame_post_draw  # gdstyle:ignore=quality/await-in-loop
			var path: String = directory.path_join("%04d.png" % frame_number)
			assert(root.get_texture().get_image().save_png(path) == OK)
			frame_number += 1
	print("PLAYER_SEQUENCE_SAVED ", frame_number)
