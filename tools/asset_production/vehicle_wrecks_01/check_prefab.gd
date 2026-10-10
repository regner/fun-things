extends SceneTree

const PREFAB := "res://scenes/prefabs/city_cars/vehicle_wrecks_01.tscn"
const MODEL := "res://art/models/vehicles/vehicle_wrecks_01/vehicle_wrecks_01.glb"
const RECEIPT := "res://docs/assets/production/vehicle_wrecks_01-evidence/validation.json"

var _failures: Array[String] = []
var _mesh_count := 0
var _surfaces := 0
var _bounds := AABB()


## Defer resource and physics checks until the isolated scene tree is initialized.
func _initialize() -> void:
	_run.call_deferred()


## Retain explicit failures so a failed assertion exits nonzero rather than hanging headlessly.
func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Verify imported ancestry and collect the actual transformed render bounds.
func _inspect(node: Node, model: Node3D) -> void:
	if node is MeshInstance3D:
		var mesh_node := node as MeshInstance3D
		var local: AABB = model.global_transform.affine_inverse() * mesh_node.global_transform \
			* mesh_node.get_aabb()
		_bounds = local if _mesh_count == 0 else _bounds.merge(local)
		_mesh_count += 1
		_surfaces += mesh_node.mesh.get_surface_count()
		_check(mesh_node.mesh.resource_path.begins_with(MODEL), "Mesh must stay source-linked")
		for index in mesh_node.mesh.get_surface_count():
			_check(mesh_node.get_surface_override_material(index) == null, "No material overrides")

	for child in node.get_children():
		_inspect(child, model)


## Load, normalize, prove two stable roundtrips, and query the authored static collider.
func _run() -> void:
	var packed := load(PREFAB) as PackedScene
	_check(packed != null, "Prefab dependencies must resolve")
	if packed == null:
		quit(1)
		return

	var instance := packed.instantiate() as Node3D
	root.add_child(instance)
	var model := instance.get_node("Visuals/Model") as Node3D
	_check(model.transform == Transform3D.IDENTITY, "Identity-linked model transform")
	_check(model.scene_file_path == MODEL, "Visuals/Model must instance the GLB")
	_inspect(model, model)
	_check(_mesh_count == 1 and _surfaces == 8, "Expected one mesh/eight surfaces")
	_check(_bounds.position.distance_to(Vector3(-0.9665, 0, -2.145)) < 0.003, "AABB minimum")
	_check(_bounds.end.distance_to(Vector3(0.9665, 1.3392, 2.137)) < 0.003, "AABB maximum")
	_check_collision(instance)
	var normalized_hash := _roundtrip(instance)
	await physics_frame
	await physics_frame
	var observations := _probe_collision(instance)
	_write_receipt(model, normalized_hash, observations)
	instance.free()
	quit(0 if _failures.is_empty() else 1)


## Confirm that collision is a single explicit grounded static-world box.
func _check_collision(instance: Node3D) -> void:
	var body := instance.get_node("Collision/WreckBody") as StaticBody3D
	var shape := body.get_node("Shape") as CollisionShape3D
	_check(body.get_child_count() == 1, "One static collider only")
	_check(body.collision_layer == 1 and body.collision_mask == 0, "Static-world collision policy")
	_check(shape.shape is BoxShape3D, "Dimension-derived box, never render mesh collision")
	_check((shape.shape as BoxShape3D).size == Vector3(1.78, 1.30, 4.26), "Authored box size")
	_check(shape.position == Vector3(0, 0.65, -0.004), "Grounded collision datum")


## Normalize once and ensure two reload/save cycles retain exact scene bytes and IDs.
func _roundtrip(instance: Node3D) -> String:
	var uid := ResourceLoader.get_resource_uid(PREFAB)
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
		ResourceUID.add_id(uid, PREFAB)

	var saved := PackedScene.new()
	_check(saved.pack(instance) == OK, "Pack linked scene")
	_check(ResourceSaver.save(saved, PREFAB) == OK, "Normalize scene UID and node identities")
	_check(ResourceSaver.set_uid(PREFAB, uid) == OK, "Save scene UID")
	var normalized_hash := FileAccess.get_sha256(PREFAB)
	for iteration in 2:
		var reload := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) \
			as PackedScene
		var copy := reload.instantiate()
		_check(saved.pack(copy) == OK, "Roundtrip pack")
		_check(ResourceSaver.save(saved, PREFAB) == OK, "Roundtrip save")
		_check(ResourceSaver.set_uid(PREFAB, uid) == OK, "Preserve scene UID")
		copy.free()
		_check(
			FileAccess.get_sha256(PREFAB) == normalized_hash,
			"Byte-stable roundtrip %d" % iteration,
		)

	return normalized_hash


## Probe contact and clear bypasses with a radius 0.35 m / height 1.8 m actor envelope.
func _probe_collision(instance: Node3D) -> Array[Dictionary]:
	var query := PhysicsShapeQueryParameters3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.8
	query.shape = capsule
	query.collision_mask = 1
	var observations: Array[Dictionary] = []
	# Independent solid, corner-contact and bypass expectations for the production actor envelope.
	for sample: Array in [
		[Vector3(0, 0.9, 0), true, "body blocks"],
		[Vector3(1.10, 0.9, 2.25), true, "rear corner blocks"],
		[Vector3(-1.10, 0.9, -2.25), true, "front corner blocks"],
		[Vector3(1.30, 0.9, 0), false, "side bypass clear"],
		[Vector3(0, 0.9, 2.60), false, "rear bypass clear"],
	]:
		query.transform = Transform3D(Basis.IDENTITY, sample[0])
		var hit := not instance.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
		_check(hit == sample[1], sample[2])
		observations.append({ "case": sample[2], "hit": hit, "expected": sample[1] })

	return observations


## Add actual engine observations to the source/export receipt without claiming gameplay approval.
func _write_receipt(
	model: Node3D, normalized_hash: String, observations: Array[Dictionary]
) -> void:
	_check(ResourceLoader.get_resource_uid(PREFAB) != ResourceUID.INVALID_ID, "Valid prefab UID")
	_check(ResourceLoader.get_resource_uid(MODEL) != ResourceUID.INVALID_ID, "Valid import UID")
	var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(RECEIPT))
	report["engine"] = {
		"version": Engine.get_version_info()["string"],
		"status": "PASS" if _failures.is_empty() else "FAIL",
		"mesh_count": _mesh_count,
		"surface_count": _surfaces,
		"aabb_min": [_bounds.position.x, _bounds.position.y, _bounds.position.z],
		"aabb_max": [_bounds.end.x, _bounds.end.y, _bounds.end.z],
		"identity_linked_model": model.transform == Transform3D.IDENTITY,
		"stable_roundtrips": 2,
		"prefab_sha256": normalized_hash,
		"prefab_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(PREFAB)),
		"capsule_queries": observations,
		"failures": _failures,
	}
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()
	print("WRECK_PREFAB ", JSON.stringify(report["engine"]))
