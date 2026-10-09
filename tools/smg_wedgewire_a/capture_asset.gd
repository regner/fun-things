extends SceneTree
## Captures only the saved asset-local preview in a bounded graphical process.

const PREVIEW: String = "res://scenes/previews/weapons_smg/smg_wedgewire_a_preview.tscn"
const WARMUP_SECONDS: float = 0.5
const PREVIEW_MAX_FPS: int = 60


## Loads authored composition and schedules a finite visual observation.
func _initialize() -> void:
	call_deferred("_capture")


## Chooses an authored camera, captures real pixels and exits without gameplay.
func _capture() -> void:
	Engine.max_fps = PREVIEW_MAX_FPS
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var view: String = args[0] if args.size() > 0 else "OverviewCamera"
	var output: String = args[1] if args.size() > 1 else "/tmp/brackett-smg/overview.png"
	var preview: Node3D = (load(PREVIEW) as PackedScene).instantiate() as Node3D
	root.add_child(preview)
	var camera: Camera3D = preview.get_node(view) as Camera3D
	camera.make_current()
	await create_timer(WARMUP_SECONDS).timeout
	await RenderingServer.frame_post_draw
	var pixels: Image = root.get_texture().get_image()
	var result: Error = pixels.save_png(output)
	print("SMG_CAPTURE " + JSON.stringify({
		"save_error": result, "path": output, "view": view,
		"size": pixels.get_size(), "camera": camera.global_transform, "fov": camera.fov,
		"renderer": RenderingServer.get_current_rendering_method(),
		"adapter": RenderingServer.get_video_adapter_name(), "max_fps": Engine.max_fps,
		"version": Engine.get_version_info(),
	}))
	quit(result)
