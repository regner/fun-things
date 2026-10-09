extends SceneTree
## Checks the imported weapon's static contract through saved production resources.

const WRAPPER: String = "res://scenes/prefabs/weapons_smg/smg_wedgewire_a.tscn"
const PREVIEW: String = "res://scenes/previews/weapons_smg/smg_wedgewire_a_preview.tscn"
const GAME_VIEW: String = "res://scenes/previews/weapons_smg/smg_wedgewire_a_game_camera.tscn"
const TOLERANCE_M: float = 0.001

var _failures: Array[String] = []
var _bounds: AABB
var _has_bounds: bool = false
var _mesh_count: int = 0
var _triangles: int = 0


## Defers inspection until the scene tree can own loaded resource instances.
func _initialize() -> void:
	call_deferred("_check")


## Records failed contracts explicitly so a logged failure cannot return success.
func _require(condition: bool, description: String) -> void:
	if not condition:
		_failures.append(description)


## Accumulates imported render bounds without constructing or copying visible geometry.
func _inspect_meshes(node: Node, relative_to: Node3D) -> void:
	_require(not node is CollisionObject3D, "Visual wrapper has no gameplay collision")
	if node is MeshInstance3D:
		var instance: MeshInstance3D = node as MeshInstance3D
		var local_bounds: AABB = (
			relative_to.global_transform.affine_inverse() * instance.global_transform
		) * instance.get_aabb()
		_bounds = _bounds.merge(local_bounds) if _has_bounds else local_bounds
		_has_bounds = true
		_mesh_count += 1
		_triangles += instance.mesh.get_faces().size() / 3
		_require(instance.scale.is_equal_approx(Vector3.ONE), "Mesh scales remain unit")

	for child: Node in node.get_children():
		_inspect_meshes(child, relative_to)


## Compares stable wrapper sockets to independent dimensions and imported source markers.
func _check_socket(weapon: Node3D, source_name: String, target_name: String,
		expected: Vector3) -> Dictionary:
	var target: Node3D = weapon.get_node("Sockets/" + target_name) as Node3D
	var model: Node3D = weapon.get_node("Visuals/Model") as Node3D
	var source: Node3D = model.find_child(source_name, true, false) as Node3D
	var authored: Transform3D = weapon.global_transform.affine_inverse() * source.global_transform
	_require(target.position.distance_to(expected) < TOLERANCE_M, target_name + " position")
	_require(target.transform.is_equal_approx(authored), target_name + " source relay")
	_require(target.basis.is_equal_approx(Basis.IDENTITY), target_name + " weapon frame")
	return { "position": target.position, "basis": target.basis, "source": source_name }


## Checks that a contact lies on the nearest authored surface along its outward normal.
func _contact_error(weapon: Node3D, target_name: String, normal: Vector3) -> float:
	var target: Node3D = weapon.get_node("Sockets/" + target_name) as Node3D
	var probe_distance: float = 0.05
	var origin: Vector3 = target.position + normal * probe_distance
	var nearest: float = INF
	for node: Node in weapon.find_children("*", "MeshInstance3D", true, false):
		var instance: MeshInstance3D = node as MeshInstance3D
		var relative: Transform3D = (
			weapon.global_transform.affine_inverse() * instance.global_transform
		)
		var faces: PackedVector3Array = instance.mesh.get_faces()
		for index: int in range(0, faces.size(), 3):
			var hit: Variant = Geometry3D.ray_intersects_triangle(
				origin, -normal, relative * faces[index],
				relative * faces[index + 1], relative * faces[index + 2]
			)
			if hit is Vector3:
				nearest = minf(nearest, origin.distance_to(hit as Vector3))

	return absf(nearest - probe_distance)


## Verifies linked resources, bounds, axes, contact markers and the inherited camera.
func _check() -> void:
	var weapon: Node3D = (load(WRAPPER) as PackedScene).instantiate() as Node3D
	root.add_child(weapon)
	_require(weapon.scale.is_equal_approx(Vector3.ONE), "Weapon root unit scale")
	var model: Node3D = weapon.get_node("Visuals/Model") as Node3D
	_require(model.scene_file_path.ends_with("/smg_wedgewire_a.glb"), "Linked imported GLB")
	_require(model.transform.is_equal_approx(Transform3D.IDENTITY), "No model compensation")
	_inspect_meshes(weapon, weapon)
	_require(_mesh_count == 16, "Expected sixteen authored mesh parts")
	_require(_bounds.size.distance_to(Vector3(0.27, 0.344, 0.80)) < TOLERANCE_M, "Envelope")
	_require(_bounds.position.distance_to(Vector3(-0.135, -0.131, -0.52)) < TOLERANCE_M,
		"Grip-relative AABB")
	var sockets: Dictionary = {
		"Grip": _check_socket(weapon, "socket_grip", "Grip", Vector3.ZERO),
		"Muzzle": _check_socket(weapon, "socket_muzzle", "Muzzle", Vector3(0, 0.14, -0.52)),
		"GripContact": _check_socket(
			weapon, "socket_grip_contact", "GripContact", Vector3(0.032, 0, 0)
		),
		"SupportHand": _check_socket(
			weapon, "socket_support_hand", "SupportHand", Vector3(0, 0.055, -0.31)
		),
		"Shoulder": _check_socket(
			weapon, "socket_shoulder", "Shoulder", Vector3(0, 0.128, 0.28)
		),
	}
	var contact_errors: Dictionary = {
		"GripContact": _contact_error(weapon, "GripContact", Vector3.RIGHT),
		"SupportHand": _contact_error(weapon, "SupportHand", Vector3.DOWN),
		"Shoulder": _contact_error(weapon, "Shoulder", Vector3.BACK),
	}
	for contact: String in contact_errors:
		_require(float(contact_errors[contact]) < TOLERANCE_M, contact + " surface contact")

	_check_preview()
	print("SMG_CHECK " + JSON.stringify({
		"ok": _failures.is_empty(), "failures": _failures, "bounds": _bounds,
		"mesh_count": _mesh_count, "triangles": _triangles, "sockets": sockets,
		"contact_surface_errors_m": contact_errors,
		"version": Engine.get_version_info(),
	}))
	weapon.free()
	quit(0 if _failures.is_empty() else 1)


## Checks the saved and inherited camera setup without running gameplay.
func _check_preview() -> void:
	var preview: Node3D = (load(PREVIEW) as PackedScene).instantiate() as Node3D
	var game_view: Node3D = (load(GAME_VIEW) as PackedScene).instantiate() as Node3D
	var camera: Camera3D = game_view.get_node("GameCamera") as Camera3D
	_require(camera.position.is_equal_approx(Vector3(0, 47, 0)), "47 m camera")
	_require(is_equal_approx(camera.fov, 42.0), "42 degree camera")
	_require(camera.rotation_degrees.is_equal_approx(Vector3(-90, 0, 0)), "North-up vertical")
	_require(camera.current, "Inherited game view selects game camera")
	_require(not (game_view.get_node("OverviewCamera") as Camera3D).current,
		"Inherited overview camera inactive")
	_require((preview.get_node("Weapon") as Node3D).scale.is_equal_approx(Vector3.ONE),
		"Preview keeps weapon scale")
	preview.free()
	game_view.free()
