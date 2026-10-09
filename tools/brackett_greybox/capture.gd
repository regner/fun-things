extends SceneTree
## Bounded graphical evidence from saved preview cameras; never authors world geometry.

const BASE: String = "res://scenes/world/brackett_greybox/"
const OUTPUT: String = "res://art/source/models/brackett_greybox/review/"


## Defers loading until the root viewport exists.
func _initialize() -> void:
	Engine.max_fps = 60
	_capture.call_deferred()


## Captures the actual saved Godot scene at 1280 by 800, then exits its own process.
func _capture() -> void:
	root.size = Vector2i(1280, 800)
	DisplayServer.window_set_size(Vector2i(1280, 800))
	var packed: PackedScene = load(BASE + "preview.tscn")
	var preview: Node3D = packed.instantiate()
	root.add_child(preview)
	await process_frame
	DirAccess.make_dir_recursive_absolute(OUTPUT)
	var records: Array[Dictionary] = []
	for node: Node in preview.get_node("Cameras").get_children():
		var camera: Camera3D = node as Camera3D
		camera.make_current()
		# Each saved camera must render before capture; this loop is bounded to eleven views.
		await process_frame # gdstyle:ignore=quality/await-in-loop
		await process_frame # gdstyle:ignore=quality/await-in-loop
		await RenderingServer.frame_post_draw # gdstyle:ignore=quality/await-in-loop
		var image: Image = root.get_texture().get_image()
		var path: String = OUTPUT + str(camera.name).to_snake_case() + ".png"
		assert(image.save_png(path) == OK)
		records.append({"camera": camera.name, "position": str(camera.position),
			"rotation": str(camera.rotation_degrees), "fov": camera.fov,
			"projection": camera.projection, "size": camera.size, "image": path})
	var file: FileAccess = FileAccess.open(OUTPUT + "capture.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine": Engine.get_version_info(),
		"renderer": RenderingServer.get_current_rendering_method(),
		"adapter": RenderingServer.get_video_adapter_name(), "viewport": [1280, 800],
		"views": records}, "\t"))
	print("BRACKETT_CAPTURE_COMPLETE ", records.size())
	quit()
