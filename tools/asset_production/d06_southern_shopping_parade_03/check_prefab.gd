@tool
extends SceneTree

const COMPONENT: String = "res://scenes/prefabs/environment/d06_southern_shopping_parade_03.tscn"
const REFERENCE: String = (
	"res://scenes/prefabs/environment/d06_southern_shopping_parade_03_reference.tscn"
)
const MODEL: String = (
	"res://art/models/environment/d06_southern_shopping_parade_03/"
	+ "d06_southern_shopping_parade_03.glb"
)
const SCRATCH: String = "C:/tmp/ft/assets/d06_southern_shopping_parade_03/"
const TOLERANCE_M: float = 0.001
const WORLD_LAYER: int = 1
const EDITOR_STARTUP_SECONDS: float = 3.0
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-8.7, 0, -0.18), Vector3(17.4, 4.8, 0.18))

var _failures: Array[String] = []
var _result: Dictionary = {}
var _models: Array[Dictionary] = []


## Defer until resources and the isolated physics world are available.
func _initialize() -> void:
	_run.call_deferred()


## Accumulate actionable failures and return a failing exit status.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Save only the two owned wrappers, preserving linked ancestry and verifying stable bytes.
func _normalize() -> void:
	for path: String in [COMPONENT, REFERENCE]:
		var first: String = ""
		for pass_index: int in range(2):
			_save_once(path)
			if pass_index == 0:
				first = FileAccess.get_sha256(path)
			else:
				_expect(first == FileAccess.get_sha256(path), "Byte-stable reload: " + path)

	_result["save_reload_byte_stable"] = _failures.is_empty()


## Pack and save one owned wrapper without modifying dependencies.
func _save_once(path: String) -> void:
	var scene: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	_expect(scene != null, "Roundtrip load: " + path)
	if scene == null:
		return

	var instance: Node = scene.instantiate()
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Pack: " + path)
	_expect(ResourceSaver.save(packed, path) == OK, "Save: " + path)
	instance.free()


## Check the actual linked component's geometry, material and small collision contract.
func _inspect_component(instance: Node3D) -> void:
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL, "Identity GLB link")
	_expect(model.transform == Transform3D.IDENTITY, "No corrective model transform")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One relief mesh")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.global_transform * mesh.get_aabb()
	_expect(bounds.position.distance_to(EXPECTED_BOUNDS.position) < TOLERANCE_M, "Local bounds min")
	_expect(bounds.size.distance_to(EXPECTED_BOUNDS.size) < TOLERANCE_M, "Local bounds size")
	_expect(mesh.mesh.resource_path.begins_with(MODEL), "No embedded replacement mesh")
	_expect(mesh.mesh.get_surface_count() == 5, "Five relief materials")
	for surface: int in range(mesh.mesh.get_surface_count()):
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface) as BaseMaterial3D
		_expect(material != null, "Material resolves")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque surface")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back-culling surface")

	var body: StaticBody3D = instance.get_node("Collision/Body") as StaticBody3D
	var shape: CollisionShape3D = body.get_node("ReliefEnvelope") as CollisionShape3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "Collision layers")
	_expect(body.get_child_count() == 1 and not shape.disabled, "One active envelope")
	_expect((shape.shape as BoxShape3D).size == Vector3(17.4, 4.8, 0.18), "Thin box size")
	_expect(shape.position == Vector3(0, 2.4, -0.09), "Flush wall/ground collision datum")
	_result["component_bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["component_bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	var identities: Dictionary = {}
	for path: String in [MODEL, COMPONENT, REFERENCE]:
		var uid: int = ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Registered UID: " + path)
		identities[path] = ResourceUID.id_to_text(uid)

	_result["registered_uids"] = identities


## Record actual saved GLB placements for Blender evidence, not a competing placement plan.
func _collect_models(node: Node, assembly: Node) -> void:
	if node is Node3D and node.scene_file_path.ends_with(".glb"):
		var spatial: Node3D = node as Node3D
		var transform: Transform3D = spatial.global_transform
		var basis: Basis = transform.basis
		var origin: Vector3 = transform.origin
		_models.append({
			"path": str(assembly.get_path_to(node)), "model": node.scene_file_path,
			"matrix_godot": [
				[basis.x.x, basis.y.x, basis.z.x, origin.x],
				[basis.x.y, basis.y.y, basis.z.y, origin.y],
				[basis.x.z, basis.y.z, basis.z.z, origin.z], [0, 0, 0, 1],
			],
		})
		_expect(spatial.transform == Transform3D.IDENTITY, "GLB local identity: " + str(node.name))

	for child: Node in node.get_children():
		_collect_models(child, assembly)


## Check datum matching, immutable composition and the two deliberate solid envelopes.
func _inspect_reference(instance: Node3D) -> void:
	var datum: Node3D = instance.get_node(
		"Parade/Shell/Visuals/Model/D06SouthernShoppingParade01/north_facade_datum"
	) as Node3D
	var facade: Node3D = instance.get_node("NorthFacade") as Node3D
	_expect(facade.global_transform.is_equal_approx(datum.global_transform), "North datum matches")
	_expect(facade.position == Vector3(0, 0, -30), "Literal north mount")
	_expect(instance.get_node("Parade").transform == Transform3D.IDENTITY,
		"Original parade identity")
	var active_shapes: int = 0
	for node: Node in instance.find_children("*", "CollisionShape3D", true, false):
		if not (node as CollisionShape3D).disabled:
			active_shapes += 1

	_expect(active_shapes == 2, "Only shell plus relief collision; fittings remain disabled")
	_result["active_collision_shapes"] = active_shapes
	_collect_models(instance, instance)
	_expect(_models.size() == 32, "Original 31 GLB instances plus one relief")
	_result["model_instances"] = _models


## Measure the assembled imported bounds against the literal family envelope.
func _reference_bounds(instance: Node3D) -> void:
	var meshes: Array[Node] = instance.find_children("*", "MeshInstance3D", true, false)
	var bounds: AABB
	for index: int in range(meshes.size()):
		var mesh: MeshInstance3D = meshes[index] as MeshInstance3D
		var current: AABB = mesh.global_transform * mesh.get_aabb()
		bounds = current if index == 0 else bounds.merge(current)

	_expect(meshes.size() == 158, "157 reused meshes plus one relief")
	_expect(bounds.position.distance_to(Vector3(-10.1, 0, -30.18)) < TOLERANCE_M,
		"Reference minimum bounds")
	_expect(bounds.end.distance_to(Vector3(9.04, 5.4, 30.035)) < TOLERANCE_M,
		"Reference maximum bounds")
	_result["reference_bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["reference_bounds_max"] = [bounds.end.x, bounds.end.y, bounds.end.z]
	_result["reference_mesh_count"] = meshes.size()


## Query actual assembled collision at the relief and uncovered corner.
func _ray_checks(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var ray_hits: Array[Dictionary] = []
	for x: float in [-7.0, 0.0, 7.0, 8.9]:
		var query: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
			Vector3(x, 1, -33), Vector3(x, 1, -29), WORLD_LAYER
		)
		var hit: Dictionary = space.intersect_ray(query)
		_expect(not hit.is_empty(), "North ray hits building")
		if hit.is_empty():
			continue

		var expected_z: float = -30.0 if x > 8.7 else -30.18
		var position: Vector3 = hit["position"]
		_expect(absf(position.z - expected_z) < TOLERANCE_M, "North ray envelope")
		ray_hits.append({
			"x": x, "z": position.z, "body": str(instance.get_path_to(hit["collider"])),
		})

	_result["north_rays"] = ray_hits


## Verify clear forecourt samples and move an actual capsule against the relief.
func _capsule_checks(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state

	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.8
	var samples: Array[Dictionary] = []
	for sample: Dictionary in [
		{ "point": Vector3(0, 0.9, -30.56), "solid": false },
		{ "point": Vector3(0, 0.9, -30.40), "solid": true },
		{ "point": Vector3(0, 0.9, -35), "solid": false },
		{ "point": Vector3(-9.4, 0.9, -30.5), "solid": false },
		{ "point": Vector3(9.4, 0.9, -30.5), "solid": false },
	]:
		var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
		query.shape = capsule
		query.collision_mask = WORLD_LAYER
		query.transform.origin = sample["point"]
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == sample["solid"], "Forecourt capsule sample")
		samples.append({ "point": str(sample["point"]), "solid": solid })

	var actor: CharacterBody3D = CharacterBody3D.new()
	var shape: CollisionShape3D = CollisionShape3D.new()
	shape.shape = capsule
	actor.add_child(shape)
	actor.collision_layer = 0
	actor.collision_mask = WORLD_LAYER
	root.add_child(actor)
	actor.position = Vector3(0, 0.9, -32)
	await physics_frame
	var collision: KinematicCollision3D = actor.move_and_collide(Vector3(0, 0, 4))
	_expect(collision != null, "Approaching capsule stops")
	_expect(absf(actor.position.z + 30.531) < 0.003, "Capsule stops outside projecting relief")
	_result["capsule_stop_z"] = actor.position.z
	actor.free()
	_result["capsule_queries"] = samples


## Execute independent resource checks and a bounded runtime physics pass with an external receipt.
func _run() -> void:
	var normalizing: bool = OS.get_cmdline_user_args().has("--normalize")
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout

	if normalizing:
		_normalize()
	else:
		var component: Node3D = (load(COMPONENT) as PackedScene).instantiate() as Node3D
		root.add_child(component)
		_inspect_component(component)
		component.free()
		var reference: Node3D = (load(REFERENCE) as PackedScene).instantiate() as Node3D
		root.add_child(reference)
		_inspect_reference(reference)
		_reference_bounds(reference)
		await physics_frame
		await physics_frame
		_ray_checks(reference)
		await _capsule_checks(reference)
		reference.free()

	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var output: String = SCRATCH + ("normalize.json" if normalizing else "prefab.json")
	var file: FileAccess = FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
