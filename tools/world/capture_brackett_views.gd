extends SceneTree
## Captures north-up 47 m / 42 degree Brackett review views over the saved preview lighting.
##
## Run as a bounded windowed game process (headless has no renderer), killed by the caller at
## 120 s:
## godot --path . --max-fps 60 --resolution 1280x800
##     --script res://tools/world/capture_brackett_views.gd
##     -- --views res://tools/world/district_02_views.json --output C:/tmp/ft/lanes/<lane>/captures
## Each view names either a saved preview `camera` (District0N, Overview, Plan) or a `centre`
## [x, z] in metres for the saved district camera moved over that point. The output directory
## must be outside the checkout; it receives one PNG per view and `capture.json`.

const PREVIEW_SCENE_PATH: String = "res://scenes/world/brackett_greybox/preview.tscn"
const CAMERAS_PATH: NodePath = ^"Cameras"
const OVERLAY_PATH: NodePath = ^"ReviewOverlay"
## Saved 47 m / 42 degree north-up district camera reused for every `centre` view.
const CENTRE_TEMPLATE_CAMERA: String = "District01"
const CAMERA_HEIGHT_M: float = 47.0
const CAMERA_FOV_DEGREES: float = 42.0
const VIEWPORT_SIZE := Vector2i(1280, 800)
const FRAME_CAP: int = 60
const VIEWS_SCHEMA: int = 1
const MAX_VIEWS: int = 32
const VIEW_NAME_PATTERN: String = "^[a-z0-9_]{1,48}$"
## Accepted centre range: the saved island extent (X -555..554, Z -291..690) plus margin.
const ISLAND_CENTRE_BOUNDS := Rect2(-600.0, -350.0, 1200.0, 1100.0)
const EXIT_FAILURE: int = 1

var _output: String
var _template_saved_position: Vector3


## Applies the frame cap and defers the run until the root viewport exists.
func _initialize() -> void:
	Engine.max_fps = FRAME_CAP
	_run.call_deferred()


## Validates arguments and views, renders every view, and writes the capture record.
func _run() -> void:
	var arguments: Dictionary = _parse_arguments(OS.get_cmdline_user_args())
	if arguments.has("error"):
		_fail(arguments.error)
		return

	var views: Array = _load_views(arguments.views)
	if views.is_empty():
		return
	_output = arguments.output
	if DirAccess.make_dir_recursive_absolute(_output) != OK:
		_fail("BRACKETT_CAPTURE_OUTPUT_FAILED " + _output)
		return

	root.size = VIEWPORT_SIZE
	DisplayServer.window_set_size(VIEWPORT_SIZE)
	var preview: Node3D = (load(PREVIEW_SCENE_PATH) as PackedScene).instantiate() as Node3D
	root.add_child(preview)
	# The key legend is review-window chrome, not world content.
	(preview.get_node(OVERLAY_PATH) as CanvasLayer).visible = false
	var cameras: Node = preview.get_node(CAMERAS_PATH)
	var template: Camera3D = cameras.get_node(CENTRE_TEMPLATE_CAMERA) as Camera3D
	if not _is_review_camera(template):
		_fail("BRACKETT_CAPTURE_TEMPLATE_NOT_47M_42DEG " + CENTRE_TEMPLATE_CAMERA)
		return
	_template_saved_position = template.position

	var records: Array[Dictionary] = []
	for view: Dictionary in views:
		var camera: Camera3D = _view_camera(cameras, template, view)
		if camera == null:
			_fail("BRACKETT_CAPTURE_UNKNOWN_CAMERA " + str(view.get("camera")))
			return
		# Views render one at a time; the loop is bounded by MAX_VIEWS.
		var row: Dictionary = await _capture(camera, view)  # gdstyle:ignore=quality/await-in-loop
		if row.is_empty():
			return
		records.append(row)

	_write_record(arguments, records)
	print("BRACKETT_CAPTURE_COMPLETE ", records.size())
	quit()


## Reads `--views <path> --output <directory>` and rejects output inside the checkout.
func _parse_arguments(user_args: PackedStringArray) -> Dictionary:
	var parsed: Dictionary = {}
	for index: int in range(0, user_args.size() - 1, 2):
		parsed[user_args[index].trim_prefix("--")] = user_args[index + 1]
	if user_args.size() != 4 or not parsed.has("views") or not parsed.has("output"):
		return { "error": "usage: -- --views <views.json> --output <directory>" }

	var output: String = String(parsed.output).replace("\\", "/").simplify_path()
	var project: String = ProjectSettings.globalize_path("res://").simplify_path()
	if output.is_relative_path() or output.to_lower().begins_with(project.to_lower()):
		return { "error": "BRACKETT_CAPTURE_OUTPUT_MUST_BE_ABSOLUTE_OUTSIDE_CHECKOUT " + output }
	parsed.output = output
	return parsed


## Loads and validates the bounded views file; reports the first problem and fails.
func _load_views(path: String) -> Array:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary or parsed.get("schema") != float(VIEWS_SCHEMA):
		_fail("BRACKETT_CAPTURE_VIEWS_INVALID %s (schema %d required)" % [path, VIEWS_SCHEMA])
		return []
	var views: Variant = parsed.get("views")
	if not views is Array or views.is_empty() or views.size() > MAX_VIEWS:
		_fail("BRACKETT_CAPTURE_VIEWS_INVALID %s (1..%d views required)" % [path, MAX_VIEWS])
		return []

	var pattern := RegEx.create_from_string(VIEW_NAME_PATTERN)
	var names: Dictionary[String, bool] = {}
	for view: Variant in views:
		var problem: String = _view_problem(view, pattern, names)
		if not problem.is_empty():
			_fail("BRACKETT_CAPTURE_VIEW_INVALID %s: %s" % [path, problem])
			return []
		names[String(view.name)] = true
	return views


## Describes why one view entry is invalid, or returns an empty string.
func _view_problem(view: Variant, pattern: RegEx, names: Dictionary[String, bool]) -> String:
	if not view is Dictionary:
		return "view is not an object"
	var name: String = str(view.get("name", ""))
	if pattern.search(name) == null or names.has(name):
		return "name must be unique and match %s: %s" % [VIEW_NAME_PATTERN, name]
	if view.has("camera") == view.has("centre"):
		return "%s needs exactly one of camera or centre" % name
	if view.has("camera"):
		return "" if view.camera is String else "%s camera must be a string" % name
	return _centre_problem(name, view.centre)


## Describes why a view centre is not a numeric [x, z] on the island, or returns "".
func _centre_problem(name: String, centre: Variant) -> String:
	if not centre is Array or centre.size() != 2:
		return "%s centre must be [x, z]" % name
	if not (centre[0] is float and centre[1] is float):
		return "%s centre must be numeric" % name
	if not ISLAND_CENTRE_BOUNDS.has_point(Vector2(centre[0], centre[1])):
		return "%s centre lies outside the island" % name
	return ""


## Returns the saved camera for a named view, or the district template moved over a centre.
func _view_camera(cameras: Node, template: Camera3D, view: Dictionary) -> Camera3D:
	if view.has("camera"):
		# A centre view may have moved the template; saved views use the saved position.
		template.position = _template_saved_position
		return cameras.get_node_or_null(NodePath(String(view.camera))) as Camera3D
	template.position = Vector3(view.centre[0], CAMERA_HEIGHT_M, view.centre[1])
	return template


## Checks that a saved camera is the 47 m / 42 degree north-up perspective review camera.
func _is_review_camera(camera: Camera3D) -> bool:
	return (
		camera != null
		and camera.projection == Camera3D.PROJECTION_PERSPECTIVE
		and is_equal_approx(camera.fov, CAMERA_FOV_DEGREES)
		and is_equal_approx(camera.position.y, CAMERA_HEIGHT_M)
		and (-camera.global_basis.z).is_equal_approx(Vector3.DOWN)
		and camera.global_basis.y.is_equal_approx(Vector3.FORWARD)
	)


## Renders one view after its camera has drawn a complete frame and saves the PNG.
func _capture(camera: Camera3D, view: Dictionary) -> Dictionary:
	camera.make_current()
	# A camera switch takes effect on the next frame; wait for that frame's draw to finish.
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	var view_name: String = view.name
	var image_path: String = _output.path_join(view_name + ".png")
	if image.get_size() != VIEWPORT_SIZE or image.save_png(image_path) != OK:
		_fail("BRACKETT_CAPTURE_SAVE_FAILED %s size %s" % [image_path, image.get_size()])
		return {}
	return {
		"name": view_name,
		"camera": String(camera.name),
		"position": [camera.global_position.x, camera.global_position.y, camera.global_position.z],
		"fov": camera.fov,
		"projection": camera.projection,
		"size": camera.size,
		"image": image_path,
	}


## Writes the self-describing capture record beside the PNGs.
func _write_record(arguments: Dictionary, records: Array[Dictionary]) -> void:
	var file: FileAccess = FileAccess.open(
		_output.path_join("capture.json"), FileAccess.WRITE
	)
	file.store_string(
		JSON.stringify(
			{
				"engine": Engine.get_version_info().string,
				"renderer": RenderingServer.get_current_rendering_method(),
				"adapter": RenderingServer.get_video_adapter_name(),
				"viewport": [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y],
				"max_fps": Engine.max_fps,
				"preview_scene": PREVIEW_SCENE_PATH,
				"views_file": arguments.views,
				"overlay_hidden": true,
				"views": records,
			},
			"\t",
		) + "\n"
	)
	file.close()


## Reports a failure and exits non-zero instead of waiting for the caller's deadline.
func _fail(message: String) -> void:
	push_error(message)
	quit(EXIT_FAILURE)
