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
	if OS.get_environment("PLAYER_CAMERA") == "game":
		scene.get_node("GameCamera").make_current()
	if not OS.get_environment("PLAYER_SEQUENCE").is_empty():
		await capture_sequence(actor)
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
	await process_frame
	await RenderingServer.frame_post_draw
	var output: String = OS.get_environment("PLAYER_CAPTURE_PATH")
	assert(not output.is_empty())
	var error: Error = root.get_texture().get_image().save_png(output)
	assert(error == OK)
	print("PLAYER_CAPTURE_SAVED ", output)
	quit()


## Select existing clips and layers for a finite review; no new motion is authored.
func sequence_segments() -> Array[Array]:
	if OS.get_environment("PLAYER_SEQUENCE_KIND") == "armed":
		return [
			["pistol_walk", ""], ["pistol_run", ""], ["pistol_fire", ""],
			["pistol_reload", ""], ["smg_walk", ""], ["smg_run", ""],
			["smg_fire", ""], ["smg_reload", ""], ["launcher_walk", ""],
			["launcher_run", ""], ["launcher_fire", ""],
		]
	if OS.get_environment("PLAYER_SEQUENCE_KIND") == "layered":
		return [
			["walk_back", "pistol_hold"], ["walk_left", "pistol_fire"],
			["run_right", "pistol_reload"], ["walk_right", "smg_hold"],
			["run_back", "smg_fire"], ["walk_left", "smg_reload"],
			["run_left", "launcher_hold"], ["walk_back", "launcher_fire"],
		]
	return [["idle", ""], ["walk", ""], ["run", ""], ["pistol_hold", ""],
		["smg_hold", ""], ["launcher_hold", ""], ["death", ""]]


## Select the exact staged static dependency and the saved bone-to-grip transform.
func show_weapon(actor: PlayerCharacterVisual, clip: String) -> void:
	for weapon: String in ["pistol", "smg", "launcher"]:
		var model: Node3D = actor.get_node("Sockets/WeaponMount/" + weapon.capitalize())
		model.visible = clip.begins_with(weapon)
		if model.visible:
			var selected: bool = actor.select_grip(StringName(weapon))
			assert(selected)


## Sample each complete action, retaining a manifest so footage can be independently inspected.
func capture_sequence(actor: PlayerCharacterVisual) -> void:
	var directory: String = OS.get_environment("PLAYER_SEQUENCE")
	var error: Error = DirAccess.make_dir_recursive_absolute(directory)
	assert(error == OK)
	var frame_number: int = 0
	for segment: Array in sequence_segments():
		var layered: bool = not str(segment[1]).is_empty()
		show_weapon(actor, str(segment[1] if layered else segment[0]))
		var selected: bool = actor.play_layered(segment[0], segment[1]) if layered \
			else actor.play_clip(segment[0])
		assert(selected)
		var player: AnimationPlayer = actor.get_node("UpperBodyPlayer") if layered \
			else actor.get_animation_player()
		player.pause()
		var duration: float = player.current_animation_length
		if layered:
			actor.get_node("LowerBodyPlayer").pause()
		print("SEGMENT ", frame_number, " ", JSON.stringify(segment), " seconds=", duration)
		for frame: int in range(int(round(duration * 30)) + 1):
			player.seek(frame / 30.0, true)
			if layered:
				actor.get_node("LowerBodyPlayer").seek(frame / 30.0, true)
			await save_frame(directory, frame_number)  # gdstyle:ignore=quality/await-in-loop
			frame_number += 1
	print("PLAYER_SEQUENCE_SAVED ", frame_number)


## Wait for a rendered sample and save its native-resolution pixels.
func save_frame(directory: String, frame_number: int) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var path: String = directory.path_join("%04d.png" % frame_number)
	var error: Error = root.get_texture().get_image().save_png(path)
	assert(error == OK)
