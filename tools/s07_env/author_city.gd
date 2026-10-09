extends SceneTree
## Procedural authoring tool that saves fixed-density S07 environment measurement scenes.

const ALLOWED_BLOCK_COUNTS: Array[int] = [6, 24, 96, 384]
const BLOCK_SIZE_M: float = 48.0
const BUILDING_OFFSET_M: float = 16.25
const CAMERA_HEIGHT_M: float = 47.0
const CAMERA_FOV_DEGREES: float = 42.0
const CAMERA_FAR_M: float = 160.0
const ROAD_SCENES: Array[String] = [
	"res://tests/fixtures/s06/west.tscn",
	"res://tests/fixtures/s06/east.tscn",
]
const BUILDING_SCENES: Array[String] = [
	"res://tests/fixtures/s02/low_prefab.tscn",
	"res://tests/fixtures/s02/near_prefab.tscn",
	"res://tests/fixtures/s02/tall_prefab.tscn",
	"res://tests/fixtures/s02/low_prefab.tscn",
]
const GRID_COLUMNS: Dictionary = { 6: 3, 24: 6, 96: 12, 384: 24 }


## Parses one supported block count, authors its scene, and exits nonzero on failure.
func _initialize() -> void:
	var block_count: int = _parse_block_count(OS.get_cmdline_user_args())
	if block_count == 0:
		quit(2)
		return

	var error: Error = _author_city(block_count)
	if error != OK:
		push_error("S07_ENV_AUTHOR_FAILED error=%s" % error_string(error))
		quit(1)
		return

	quit()


## Returns the requested supported block count, or zero after reporting invalid arguments.
func _parse_block_count(arguments: PackedStringArray) -> int:
	if arguments.size() != 2 or arguments[0] != "--blocks":
		push_error("usage: --script tools/s07_env/author_city.gd -- --blocks N")
		return 0

	var block_count: int = arguments[1].to_int()
	if block_count not in ALLOWED_BLOCK_COUNTS:
		push_error("blocks must be one of %s" % ALLOWED_BLOCK_COUNTS)
		return 0

	return block_count


## Creates one saved city from linked road-sector and building prefab instances.
func _author_city(block_count: int) -> Error:  # gdstyle:ignore=quality/max-local-variables
	var road_scenes: Array[PackedScene] = _load_scenes(ROAD_SCENES)
	var building_scenes: Array[PackedScene] = _load_scenes(BUILDING_SCENES)
	if road_scenes.size() != ROAD_SCENES.size() or building_scenes.size() != BUILDING_SCENES.size():
		return ERR_CANT_ACQUIRE_RESOURCE

	var root_node := Node3D.new()
	root_node.name = "City%s" % block_count
	var roads := Node3D.new()
	roads.name = "RoadSectors"
	root_node.add_child(roads)
	roads.owner = root_node
	var buildings := Node3D.new()
	buildings.name = "Buildings"
	root_node.add_child(buildings)
	buildings.owner = root_node

	var columns: int = GRID_COLUMNS[block_count]
	var rows: int = block_count / columns
	root_node.set_meta("block_count", block_count)
	root_node.set_meta("grid_columns", columns)
	root_node.set_meta("grid_rows", rows)
	root_node.set_meta("block_size_m", BLOCK_SIZE_M)
	_place_blocks(root_node, road_scenes, building_scenes, columns, rows)
	_add_presentation(root_node, columns, rows)

	var packed := PackedScene.new()
	var pack_error: Error = packed.pack(root_node)
	if pack_error != OK:
		root_node.free()
		return pack_error

	var output_path: String = "res://tests/fixtures/s07_env/city_%s.tscn" % block_count
	var save_error: Error = ResourceSaver.save(packed, output_path)
	root_node.free()
	if save_error != OK:
		return save_error
	var uid_error: Error = _ensure_saved_uid(output_path)
	if uid_error == OK:
		print("S07_ENV_AUTHORED blocks=%s path=%s" % [block_count, output_path])
	return uid_error


## Assigns a persistent resource UID to a newly generated scene while preserving an existing one.
func _ensure_saved_uid(output_path: String) -> Error:
	var resource_uid: int = ResourceLoader.get_resource_uid(output_path)
	if resource_uid == ResourceUID.INVALID_ID:
		resource_uid = ResourceUID.create_id()
	return ResourceSaver.set_uid(output_path, resource_uid)


## Loads all referenced saved scenes without manufacturing replacement content.
func _load_scenes(paths: Array[String]) -> Array[PackedScene]:
	var scenes: Array[PackedScene] = []
	for path: String in paths:
		var scene: PackedScene = load(path) as PackedScene
		if scene == null:
			push_error("cannot load %s" % path)
			return []
		scenes.append(scene)

	return scenes


## Places two linked road sectors and four mixed-height buildings for every block.
func _place_blocks(
	root_node: Node3D,
	road_scenes: Array[PackedScene],
	building_scenes: Array[PackedScene],
	columns: int,
	rows: int,
) -> void:
	var roads: Node3D = root_node.get_node("RoadSectors")
	var buildings: Node3D = root_node.get_node("Buildings")
	var block_index: int = 0
	for row: int in range(rows):
		for column: int in range(columns):
			var centre := Vector3(
				(column - (columns - 1) / 2.0) * BLOCK_SIZE_M,
				0.0,
				(row - (rows - 1) / 2.0) * BLOCK_SIZE_M,
			)
			for road_index: int in range(road_scenes.size()):
				var road: Node3D = road_scenes[road_index].instantiate() as Node3D
				road.name = "Block%03d%s" % [block_index, "West" if road_index == 0 else "East"]
				road.position = centre
				roads.add_child(road)
				road.owner = root_node
			_place_buildings(root_node, buildings, building_scenes, block_index, centre)
			block_index += 1


## Places one prefab on each buildable corner, cycling heights between neighboring blocks.
func _place_buildings(
	root_node: Node3D,
	buildings: Node3D,
	building_scenes: Array[PackedScene],
	block_index: int,
	centre: Vector3,
) -> void:
	var offsets: Array[Vector3] = [
		Vector3(-BUILDING_OFFSET_M, 0.0, -BUILDING_OFFSET_M),
		Vector3(BUILDING_OFFSET_M, 0.0, -BUILDING_OFFSET_M),
		Vector3(-BUILDING_OFFSET_M, 0.0, BUILDING_OFFSET_M),
		Vector3(BUILDING_OFFSET_M, 0.0, BUILDING_OFFSET_M),
	]
	for corner: int in range(offsets.size()):
		var prefab_index: int = (block_index + corner) % building_scenes.size()
		var building: Node3D = building_scenes[prefab_index].instantiate() as Node3D
		building.name = "Block%03dBuilding%d" % [block_index, corner]
		building.position = centre + offsets[corner]
		buildings.add_child(building)
		building.owner = root_node


## Adds the fixed ratified camera and simple saved lighting used by every measured variant.
func _add_presentation(root_node: Node3D, columns: int, rows: int) -> void:
	var camera := Camera3D.new()
	camera.name = "Camera"
	camera.position = Vector3(
		-(columns - 1) * BLOCK_SIZE_M / 2.0,
		CAMERA_HEIGHT_M,
		-(rows - 1) * BLOCK_SIZE_M / 2.0,
	)
	camera.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
	camera.fov = CAMERA_FOV_DEGREES
	camera.near = 0.1
	camera.far = CAMERA_FAR_M
	camera.current = true
	root_node.add_child(camera)
	camera.owner = root_node

	var sun := DirectionalLight3D.new()
	sun.name = "Sun"
	sun.rotation_degrees = Vector3(-60.0, -30.0, 0.0)
	sun.light_energy = 1.2
	root_node.add_child(sun)
	sun.owner = root_node

	var world_environment := WorldEnvironment.new()
	world_environment.name = "Environment"
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.02, 0.03, 0.04)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color.WHITE
	environment.ambient_light_energy = 0.65
	world_environment.environment = environment
	root_node.add_child(world_environment)
	world_environment.owner = root_node
