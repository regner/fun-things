extends SceneTree
## Checks the reusable visual asset through its saved production-facing scene paths.

const PREFAB_PATH: String = "res://scenes/prefabs/pistol_coral_stub/pistol_coral_stub.tscn"
const MODEL_PATH: String = "res://art/models/weapons/pistol_coral_stub/pistol_coral_stub.glb"
const CAMERA_PATH: String = "res://scenes/prefabs/pistol_coral_stub/preview_game_camera.tscn"
const POSITION_TOLERANCE_M: float = 0.001
const EXPECTED_MUZZLE_M: Vector3 = Vector3(0.0, 0.122, -0.421)

var _failures: int = 0
var _mesh_count: int = 0
var _triangle_count: int = 0
var _materials: Dictionary = {}
var _bounds: AABB
var _has_bounds: bool = false


## Schedules checks after SceneTree initialization.
func _initialize() -> void:
	_run.call_deferred()


## Verifies linked import, unit transforms, source-relayed sockets and preview camera.
func _run() -> void:
	var packed: PackedScene = load(PREFAB_PATH) as PackedScene
	_expect(packed != null, "saved prefab loads")
	if packed == null:
		quit(1)
		return

	var asset: Node3D = packed.instantiate() as Node3D
	root.add_child(asset)
	var model: Node3D = asset.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL_PATH, "model remains a linked GLB instance")
	_expect(asset.transform.is_equal_approx(Transform3D.IDENTITY), "grip-origin unit root")
	_expect(model.transform.is_equal_approx(Transform3D.IDENTITY), "no corrective model transform")
	_expect(asset.get_script() == null, "editor bridge is detached from reusable asset")
	var grip: Node3D = asset.get_node("Sockets/Grip") as Node3D
	var muzzle: Node3D = asset.get_node("Sockets/Muzzle") as Node3D
	_expect(grip.position.length() < POSITION_TOLERANCE_M, "grip socket is local origin")
	_expect(muzzle.position.distance_to(EXPECTED_MUZZLE_M) < POSITION_TOLERANCE_M,
		"muzzle matches declared emission position")
	_expect(muzzle.basis.is_equal_approx(Basis.IDENTITY), "muzzle is local -Z forward / +Y up")
	var authored: Node3D = model.find_child("socket_muzzle", true, false) as Node3D
	_expect(authored != null, "source muzzle survives GLB import")
	if authored != null:
		_expect(muzzle.global_transform.is_equal_approx(authored.global_transform),
			"wrapper relays authored muzzle transform")

	_inspect_node(model, model)
	_expect(_mesh_count == 12, "declared twelve render objects import")
	_expect(_materials.size() == 6, "six declared PBR materials import")
	_expect(_bounds.size.x > 0.14 and _bounds.size.x < 0.16, "compact grip-sized width")
	_expect(_bounds.size.y > 0.39 and _bounds.size.y < 0.43, "declared vertical visual envelope")
	_expect(_bounds.size.z > 0.55 and _bounds.size.z < 0.58, "declared short pistol length")
	var preview: Node3D = (load(CAMERA_PATH) as PackedScene).instantiate() as Node3D
	var camera: Camera3D = preview.get_node("Camera") as Camera3D
	_expect(camera.position.is_equal_approx(Vector3(0, 47, 0)), "47m camera height")
	_expect(is_equal_approx(camera.fov, 42.0), "42-degree perspective field of view")
	_expect(camera.projection == Camera3D.PROJECTION_PERSPECTIVE, "perspective projection")
	_expect((-camera.basis.z).is_equal_approx(Vector3.DOWN), "camera looks vertically down")
	print("PISTOL_OBSERVATION ", JSON.stringify({"bounds_min_m": str(_bounds.position),
		"bounds_max_m": str(_bounds.end), "size_xyz_m": str(_bounds.size),
		"meshes": _mesh_count, "triangles": _triangle_count, "materials": _materials.keys(),
		"muzzle_m": str(muzzle.position), "failures": _failures}))
	preview.free()
	asset.queue_free()
	quit(0 if _failures == 0 else 1)


## Inspects actual imported surfaces and rejects gameplay/collision nodes in this visual.
func _inspect_node(node: Node, model: Node3D) -> void:
	_expect(not node is CollisionObject3D, "visual contains no gameplay collision")
	_expect(not node is AnimationPlayer, "static export has no unintended animation")
	if node is Node3D:
		var spatial: Node3D = node as Node3D
		_expect(spatial.scale.is_equal_approx(Vector3.ONE), "positive unit node scale")

	if node is MeshInstance3D:
		var mesh_node: MeshInstance3D = node as MeshInstance3D
		_mesh_count += 1
		var relative: Transform3D = (
			model.global_transform.affine_inverse() * mesh_node.global_transform
		)
		var bounds: AABB = relative * mesh_node.get_aabb()
		_bounds = _bounds.merge(bounds) if _has_bounds else bounds
		_has_bounds = true
		for surface: int in range(mesh_node.mesh.get_surface_count()):
			var arrays: Array = mesh_node.mesh.surface_get_arrays(surface)
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			_triangle_count += indices.size() / 3
			var mat: Material = mesh_node.get_active_material(surface)
			_expect(mat != null, "imported surface has material")
			if mat != null:
				_materials[mat.resource_name] = true

	for child: Node in node.get_children():
		_inspect_node(child, model)


## Reports each independent contract violation while retaining remaining observations.
func _expect(condition: bool, label: String) -> void:
	if not condition:
		_failures += 1
		push_error("PISTOL_CHECK: " + label)
