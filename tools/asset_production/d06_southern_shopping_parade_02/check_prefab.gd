@tool
extends SceneTree

const NID: String = "d06_southern_shopping_parade_02"
const PREFIX: String = "res://scenes/prefabs/environment/"
const SCRATCH: String = "C:/tmp/ft/assets/d06_southern_shopping_parade_02/"
const TOLERANCE_M: float = 0.001
const EDITOR_STARTUP_SECONDS: float = 3.0
const WORLD_LAYER: int = 1
const BAY_CENTRES: Array[float] = [-25, -15, -5, 5, 15, 25]
const MOUNTS: Dictionary = {
	"Entrance": ["entrance_single", "city_shop_fittings_03_single"],
	"Door": ["door_single", "city_shop_fittings_06_single"],
	"Window": ["display_window", "city_shop_fittings_05"],
	"Canopy": ["canopy", "city_shop_fittings_01"],
	"Fascia": ["fascia", "city_shop_fittings_02"],
}

var _failures: Array[String] = []
var _result: Dictionary = {}
var _models: Array[Dictionary] = []


## Defer checks until resource and physics services are available.
func _initialize() -> void:
	_run.call_deferred()


## Retain every failed contract and return a nonzero exit.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Save only the two owned compositions, preserving linked prefab and GLB ancestry.
func _normalize() -> void:
	for suffix: String in ["_bay", ""]:
		var path: String = PREFIX + NID + suffix + ".tscn"
		var previous_hash: String = ""
		for pass_index: int in range(2):
			var packed: PackedScene = ResourceLoader.load(
				path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
			) as PackedScene
			var instance: Node = packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
			var saved: PackedScene = PackedScene.new() # gdstyle:ignore=quality/allocation-in-loop
			_expect(saved.pack(instance) == OK, "Pack " + path)
			_expect(ResourceSaver.save(saved, path) == OK, "Save " + path)
			instance.free()
			var current_hash: String = FileAccess.get_sha256(path)
			if pass_index == 1:
				_expect(current_hash == previous_hash, "Second save must be byte-stable: " + path)

			previous_hash = current_hash

	_result["save_reload_byte_stable"] = _failures.is_empty()


## Serialize an engine transform for read-only Blender evidence, never runtime placement.
func _matrix(transform: Transform3D) -> Array:
	return [
		[transform.basis.x.x, transform.basis.y.x, transform.basis.z.x, transform.origin.x],
		[transform.basis.x.y, transform.basis.y.y, transform.basis.z.y, transform.origin.y],
		[transform.basis.x.z, transform.basis.y.z, transform.basis.z.z, transform.origin.z],
		[0, 0, 0, 1],
	]


## Inspect actual imported meshes and record reusable model-instance transforms for evidence.
func _inspect_model(prefab: Node3D) -> AABB:
	var model: Node3D = prefab.get_node("Visuals/Model") as Node3D
	_expect(model.transform == Transform3D.IDENTITY, "Identity model: " + str(prefab.get_path()))
	_expect(model.scene_file_path.ends_with(".glb"), "Linked GLB required")
	var bounds: AABB
	var first: bool = true
	for node: Node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh_node: MeshInstance3D = node as MeshInstance3D
		_expect(mesh_node.mesh.resource_path.begins_with(model.scene_file_path), "Imported mesh")
		var box: AABB = mesh_node.global_transform * mesh_node.get_aabb()
		bounds = box if first else bounds.merge(box)
		first = false
		for surface: int in range(mesh_node.mesh.get_surface_count()):
			var material: BaseMaterial3D = (
				mesh_node.mesh.surface_get_material(surface) as BaseMaterial3D
			)
			_expect(material != null, "Every surface retains its material")
			_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque")
			_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back culling")

	_models.append({"prefab": prefab.scene_file_path, "model": model.scene_file_path,
		"path": str(prefab.get_path()), "matrix_godot": _matrix(model.global_transform)})
	return bounds


## Check every saved bay against actual source-owned shell mounts and independent extents.
func _inspect_bays(instance: Node3D) -> void: # gdstyle:ignore=quality/max-local-variables
	var shell: Node3D = instance.get_node("Shell") as Node3D
	_expect(shell.scene_file_path == PREFIX + "d06_southern_shopping_parade_01.tscn", "Shell link")
	_expect(shell.transform == Transform3D.IDENTITY, "Unmodified shell placement")
	var full_bounds: AABB = _inspect_model(shell)
	var observations: Array[Dictionary] = []
	for index: int in range(BAY_CENTRES.size()):
		var station_name: String = "west_bay_%02d" % (index + 1)
		var bay: Node3D = instance.get_node("WestBays/WestBay%02d" % (index + 1)) as Node3D
		var station: Node3D = shell.find_child(station_name, true, false) as Node3D
		_expect(bay.scene_file_path == PREFIX + NID + "_bay.tscn", "Repeated linked bay")
		_expect(bay.global_transform.is_equal_approx(station.global_transform), "Station datum")
		_expect(bay.position.distance_to(Vector3(-9, 0, BAY_CENTRES[index])) < TOLERANCE_M,
			"Independent station centre")
		_expect((-bay.basis.z).distance_to(Vector3.LEFT) < TOLERANCE_M, "West outward axis")
		var boxes: Dictionary = {}
		for label: String in MOUNTS:
			var fitting: Node3D = bay.get_node(label) as Node3D
			var marker: Node3D = station.get_node(station_name + "_mount_" + MOUNTS[label][0])
			_expect(fitting.scene_file_path == PREFIX + MOUNTS[label][1] + ".tscn", "Fitting link")
			_expect(fitting.global_transform.is_equal_approx(marker.global_transform),
				"Fitting must match shell marker: " + station_name + "/" + label)
			boxes[label] = _inspect_model(fitting)
			full_bounds = full_bounds.merge(boxes[label])

		var window: AABB = boxes["Window"]
		var canopy: AABB = boxes["Canopy"]
		var fascia: AABB = boxes["Fascia"]
		var window_gap: float = canopy.position.y - window.end.y
		var fascia_gap: float = fascia.position.y - canopy.end.y
		_expect(absf(window_gap - 0.1) < TOLERANCE_M, "Window-canopy separation")
		_expect(absf(fascia_gap - 0.16) < TOLERANCE_M, "Canopy-fascia separation")
		_expect(absf(canopy.position.y - 2.58) < TOLERANCE_M, "Canopy headroom datum")
		observations.append({"station": station_name, "window_canopy_gap_m": window_gap,
			"canopy_fascia_gap_m": fascia_gap, "canopy_bottom_m": canopy.position.y})

	_expect(full_bounds.position.distance_to(Vector3(-10.1, 0, -30.035)) < TOLERANCE_M,
		"Full fitted bounds minimum")
	_expect(full_bounds.end.distance_to(Vector3(9.04, 5.4, 30.035)) < TOLERANCE_M,
		"Full fitted bounds maximum")
	_result["aabb_min"] = [full_bounds.position.x, full_bounds.position.y, full_bounds.position.z]
	_result["aabb_max"] = [full_bounds.end.x, full_bounds.end.y, full_bounds.end.z]
	_result["bays"] = observations
	_result["model_instances"] = _models


## Prove all nested pane/leaf shapes stay disabled after inherited scene roundtrips.
func _inspect_collision(instance: Node3D) -> void:
	var active: Array[String] = []
	var disabled: int = 0
	for node: Node in instance.find_children("*", "CollisionShape3D", true, false):
		var shape: CollisionShape3D = node as CollisionShape3D
		if shape.disabled:
			disabled += 1
		else:
			active.append(str(instance.get_path_to(shape)))

	_expect(active == ["Shell/Collision/Body/SolidFootprint"], "Only shell owns active collision")
	_expect(disabled == 18, "All six leaves and twelve panes disabled")
	_result["active_collision_shapes"] = active
	_result["disabled_fitting_shapes"] = disabled


## Query the full assembled resource, proving closed entries and unobstructed exterior samples.
func _physics_checks(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var ray_results: Array[Dictionary] = []
	for centre: float in BAY_CENTRES:
		var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
			Vector3(-12, 1, centre - 1.95), Vector3(-8, 1, centre - 1.95), WORLD_LAYER
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_expect(not hit.is_empty(), "Closed entry must be blocked")
		if not hit.is_empty():
			_expect(hit["collider"] == instance.get_node("Shell/Collision/Body"), "Shell ray owner")
			_expect(absf(hit["position"].x + 9) < TOLERANCE_M, "Solid envelope remains -9m")
			ray_results.append({ "station_z": centre, "hit_x": hit["position"].x })

	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.8
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var clear_points: Array[Vector3] = [
		Vector3(-9.4, 0.9, -24.05), Vector3(-11, 0.9, 0),
		Vector3(9.4, 0.9, 0), Vector3(0, 0.9, -30.4), Vector3(0, 0.9, 30.4),
	]
	for point: Vector3 in clear_points:
		query.transform.origin = point
		_expect(space.intersect_shape(query).is_empty(),
			"Clear exterior capsule sample " + str(point))

	_result["closed_entry_rays"] = ray_results
	_result["clear_exterior_capsule_samples"] = clear_points.size()


## Run isolated saved-resource checks; the normal game and live editor are never started.
func _run() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout

	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.has("--normalize"):
		_normalize()
	else:
		var packed: PackedScene = load(PREFIX + NID + ".tscn") as PackedScene
		_expect(packed != null, "Reference dependencies must load")
		if packed != null:
			var instance: Node3D = packed.instantiate() as Node3D
			root.add_child(instance)
			_inspect_bays(instance)
			_inspect_collision(instance)
			await physics_frame
			await physics_frame
			_physics_checks(instance)
			instance.queue_free()
			await process_frame

	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var filename: String = "normalize.json" if args.has("--normalize") else "prefab.json"
	var file: FileAccess = FileAccess.open(SCRATCH + filename, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
