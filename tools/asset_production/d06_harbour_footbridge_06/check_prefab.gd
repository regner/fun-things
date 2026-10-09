extends SceneTree

const NID: String = "d06_harbour_footbridge_06"
const SCRATCH: String = "C:/tmp/ft/assets/d06_harbour_footbridge_06/"
const VARIANTS: Array[String] = [
	"junction", "span", "main", "south", "quay", "support_tall", "support_mid",
]
const WORLD_LAYER: int = 1
const TOLERANCE_M: float = 0.001
const EDITOR_STARTUP_SECONDS: float = 3.0

var _failures: Array[String] = []
var _variants: Dictionary = {}
var _observations: Dictionary = {}
var _source: Dictionary = {}


## Wait for the isolated tool tree to initialize before inspecting resources.
func _initialize() -> void:
	_run.call_deferred()


## Retain every failed contract and make the tool exit nonzero.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Resolve the default junction wrapper or an explicitly named component.
func _prefab_path(variant: String) -> String:
	var suffix: String = "" if variant == "junction" else "_" + variant
	return "res://scenes/prefabs/environment/" + NID + suffix + ".tscn"


## Normalize new wrappers and prove their second load/pack/save preserves exact bytes.
func _roundtrip(path: String) -> void:
	var first_hash: String = ""
	var packed: PackedScene = PackedScene.new()
	for pass_index: int in range(2):
		var original: PackedScene = ResourceLoader.load(
			path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
		) as PackedScene
		_expect(original != null, "Prefab loads for roundtrip: " + path)
		if original == null:
			return

		var instance: Node = original.instantiate()
		_expect(packed.pack(instance) == OK, "Pack " + path)
		_expect(ResourceSaver.save(packed, path) == OK, "Save " + path)
		instance.free()
		if pass_index == 0:
			first_hash = FileAccess.get_sha256(path)
		else:
			_expect(first_hash == FileAccess.get_sha256(path), "Byte-stable second save " + path)

	_observations["save_reload_byte_stable"] = true


## Convert the measured Blender receipt's coordinates without rounding them to display strings.
func _vector(values: Array) -> Vector3:
	return Vector3(float(values[0]), float(values[1]), float(values[2]))


## Check linked ancestry, identity, source bounds, materials, collision and resource UIDs.
func _inspect(instance: Node3D, variant: String) -> void:
	var model_path: String = (
		"res://art/models/environment/" + NID + "/" + NID + "_" + variant + ".glb"
	)
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == model_path, "Linked model ancestry")
	_expect(model.transform == Transform3D.IDENTITY, "Identity imported model")
	_expect(model.find_children("*", "Light3D", true, false).is_empty(), "No real light nodes")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One source-linked mesh")
	if meshes.is_empty():
		return

	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.global_transform * mesh.get_aabb()
	var measured: Dictionary = _source["variants"][variant]["aabb_godot"]
	_expect(bounds.position.distance_to(_vector(measured["min"])) < TOLERANCE_M, "AABB minimum")
	_expect(bounds.size.distance_to(_vector(measured["size"])) < TOLERANCE_M, "AABB dimensions")
	_expect(mesh.mesh.resource_path.begins_with(model_path), "Imported mesh dependency")
	_check_materials(mesh.mesh, variant.begins_with("support"))
	_check_collision(instance, variant)
	_observations["bounds"] = { "min": bounds.position, "size": bounds.size }
	_observations["linked_identity_model"] = true
	for path: String in [_prefab_path(variant), model_path]:
		var uid: int = ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Registered UID: " + path)
		_observations[path.get_extension() + "_uid"] = ResourceUID.id_to_text(uid)


## Require the correct opaque palette and decorative cyan emission, with no material overrides.
func _check_materials(mesh: Mesh, support: bool) -> void:
	var expected: Array[String] = ["rail_dark_teal", "edge_cyan"]
	if support:
		expected = ["deck_warm_pale", "deck_pale_fascia", "deck_petrol_underside"]

	_expect(mesh.get_surface_count() == expected.size(), "Material surface count")
	var names: Array[String] = []
	for index: int in range(mesh.get_surface_count()):
		var material: BaseMaterial3D = mesh.surface_get_material(index) as BaseMaterial3D
		_expect(material != null, "Material resolves")
		if material == null:
			continue

		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque surface")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back-culling surface")
		names.append(material.resource_name)
		if material.resource_name == "edge_cyan":
			_expect(material.emission_enabled, "Cyan emission survives import")

	_expect(names == expected, "Family material names/order")
	_observations["materials"] = names


## Inspect deliberate continuous guard prisms or simple pier boxes, not automatic mesh collision.
func _check_collision(instance: Node3D, variant: String) -> void:
	var body: StaticBody3D = instance.get_node("Collision/Body") as StaticBody3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "Static world layers")
	var expected: int = { "junction": 6, "span": 2, "main": 10, "south": 10,
		"quay": 10, "support_tall": 4, "support_mid": 4 }[variant]
	_expect(body.get_child_count() == expected, "Deliberate shape count")
	for child: Node in body.get_children():
		var shape: Shape3D = (child as CollisionShape3D).shape
		if variant.begins_with("support"):
			_expect(shape is BoxShape3D, "Simple support envelope")
		else:
			_expect(shape is ConvexPolygonShape3D, "Continuous guard prism")
			_expect((shape as ConvexPolygonShape3D).points.size() == 8, "Eight guard corners")

	_observations["collision_shapes"] = expected


## Query an independent ray and retain its endpoints, expected blocking and measured hit.
func _ray(instance: Node3D, start: Vector3, finish: Vector3, solid: bool) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var hit: Dictionary = space.intersect_ray(
		PhysicsRayQueryParameters3D.create(start, finish, WORLD_LAYER)
	)
	_expect(not hit.is_empty() == solid, "Solid/void ray %s to %s" % [start, finish])
	_observations["rays"].append({ "from": start, "to": finish, "solid": solid,
		"hit": hit.get("position", null) })


## Probe all six exposed junction edges and all three open portal centres with literal expectations.
func _junction_queries(instance: Node3D) -> void:
	for pair: Array in [
		[Vector3(-1, 0.6, -2.3), Vector3(-2, 0.6, -2.3)],
		[Vector3(-2.3, 0.6, -1), Vector3(-2.3, 0.6, -2)],
		[Vector3(-2, 0.6, 1), Vector3(-2, 0.6, 2)],
		[Vector3(0.4, 0.6, 2), Vector3(-0.3, 0.6, 2.7)],
		[Vector3(2, 0.6, 0.4), Vector3(2.7, 0.6, -0.3)],
		[Vector3(1, 0.6, -2), Vector3(2, 0.6, -2)],
	]:
		_ray(instance, pair[0], pair[1], true)

	_ray(instance, Vector3(0, 0.6, -2.5), Vector3(0, 0.6, -3.5), false)
	_ray(instance, Vector3(-2.5, 0.6, 0), Vector3(-3.5, 0.6, 0), false)
	_ray(instance, Vector3(1.8, 0.6, 1.8), Vector3(2.5, 0.6, 2.5), false)
	_capsule(instance, Vector3(0, 0.91, 0), false)


## Check span sides, clear mouths, exact inner clearance and the continuous filled guard envelope.
func _span_queries(instance: Node3D) -> void:
	for x: float in [-2.0, 2.0]:
		_ray(instance, Vector3(0, 0.5, -6), Vector3(x, 0.5, -6), true)

	_ray(instance, Vector3(0, 0.5, 1), Vector3(0, 0.5, -13), false)
	_ray(instance, Vector3(-2, 1.21, -6), Vector3(2, 1.21, -6), false)
	_ray(instance, Vector3(-2, -0.16, -6), Vector3(2, -0.16, -6), false)
	_capsule(instance, Vector3(0, 0.91, -6), false)
	_capsule(instance, Vector3(1.1, 0.91, -6), false)
	_capsule(instance, Vector3(1.3, 0.91, -6), true)


## Query each access boundary and both open route mouths without mistaking ramp tests for traversal.
func _access_queries(instance: Node3D, variant: String) -> void:
	for sample: Vector3 in [Vector3(0, 6.1, -1.6), Vector3(0, 4.725, -5.76)]:
		_ray(instance, sample, sample + Vector3(2, 0, 0), true)
		_ray(instance, sample, sample + Vector3(-2, 0, 0), true)

	_ray(instance, Vector3(0, 6.1, 0.5), Vector3(0, 6.1, -0.5), false)
	_capsule(instance, Vector3(0, 6.41, -1.6), false)
	if variant == "main":
		for sample: Vector3 in [Vector3(0, 3.35, -9.92), Vector3(0, 1.975, -14.08),
			Vector3(0, 0.6, -18.24)]:
			_ray(instance, sample, sample + Vector3(2, 0, 0), true)
			_ray(instance, sample, sample + Vector3(-2, 0, 0), true)

		_ray(instance, Vector3(0, 0.6, -19), Vector3(0, 0.6, -20.5), false)
	else:
		_turn_queries(instance, -1.0 if variant == "quay" else 1.0)

	# Boundary remains continuous at either side of each first-flight transition.
	for z: float in [-3.19, -3.21, -8.31, -8.33]:
		var y: float = 6.1 if z > -4 else 3.35
		# At a turn, the outgoing side rail also covers the 1 cm corner sample.
		_ray(instance, Vector3(0, y, z), Vector3(-2, y, z), true)
		_ray(instance, Vector3(0, y, z), Vector3(2, y, z), true)


## Probe the side-turn landing, descending second flight, apron and preserved mouth.
func _turn_queries(instance: Node3D, sign_x: float) -> void:
	_ray(instance, Vector3(0, 3.35, -9.92), Vector3(-sign_x * 2, 3.35, -9.92), true)
	_ray(instance, Vector3(0, 3.35, -9.92), Vector3(0, 3.35, -12), true)
	_ray(instance, Vector3(0, 3.35, -9.92), Vector3(sign_x * 2, 3.35, -9.92), false)
	for sample: Vector3 in [Vector3(sign_x * 4.16, 1.975, -9.92),
		Vector3(sign_x * 8.32, 0.6, -9.92)]:
		_ray(instance, sample, sample + Vector3(0, 0, 2), true)
		_ray(instance, sample, sample + Vector3(0, 0, -2), true)

	_ray(instance, Vector3(sign_x * 9, 0.6, -9.92), Vector3(sign_x * 10.5, 0.6, -9.92), false)
	_capsule(instance, Vector3(0, 3.66, -9.92), false)


## Verify conservative pier blocking and free space beside its foot and below the bearing.
func _support_queries(instance: Node3D, variant: String) -> void:
	var height: float = 5.15 if variant == "support_tall" else 2.4
	_ray(instance, Vector3(-2, 0.1, 0), Vector3(2, 0.1, 0), true)
	_ray(instance, Vector3(-2, 1, 0), Vector3(2, 1, 0), true)
	_ray(instance, Vector3(-2, height - 0.15, 0), Vector3(2, height - 0.15, 0), true)
	_ray(instance, Vector3(-2, height + 0.01, 0), Vector3(2, height + 0.01, 0), false)
	_ray(instance, Vector3(0.8, 0.4, -1), Vector3(0.8, 0.4, 1), false)
	_capsule(instance, Vector3(0, 0.91, 0), true)
	_capsule(instance, Vector3(1.1, 0.91, 0), false)


## Use an explicit 0.35 m radius / 1.8 m actor envelope for overlap, not player simulation.
func _capsule(instance: Node3D, centre: Vector3, solid: bool) -> void:
	var shape: CapsuleShape3D = CapsuleShape3D.new()
	shape.radius = 0.35
	shape.height = 1.8
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform.origin = centre
	query.collision_mask = WORLD_LAYER
	var hits: Array[Dictionary] = instance.get_world_3d().direct_space_state.intersect_shape(query)
	_expect(not hits.is_empty() == solid, "Capsule overlap at %s" % centre)
	_observations["capsules"].append({ "centre": centre, "solid": solid, "hit_count": hits.size() })


## Load all seven components, normalize when requested, and retain fresh query receipts.
func _run() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	_source = JSON.parse_string(FileAccess.get_file_as_string(
		"res://docs/assets/production/" + NID + "-evidence/validation.json"
	)) as Dictionary
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	for variant: String in VARIANTS:
		_observations = { "rays": [], "capsules": [] }
		if arguments.has("--normalize"):
			_roundtrip(_prefab_path(variant))

		var packed: PackedScene = ResourceLoader.load(_prefab_path(variant)) as PackedScene
		_expect(packed != null, "All dependencies resolve: " + variant)
		if packed == null:
			continue

		var instance: Node3D = packed.instantiate() as Node3D
		root.add_child(instance)
		_inspect(instance, variant)
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		match variant:
			"junction": _junction_queries(instance)
			"span": _span_queries(instance)
			"main", "south", "quay": _access_queries(instance, variant)
			_: _support_queries(instance, variant)

		instance.queue_free()
		await process_frame  # gdstyle:ignore=quality/await-in-loop
		_variants[variant] = _observations

	await _assembly_checks()
	var result: Dictionary = { "ok": _failures.is_empty(), "failures": _failures,
		"variants": _variants, "assembly": _observations,
		"engine": Engine.get_version_info()["string"] }
	var output: String = SCRATCH + "prefab-check.json"
	var output_index: int = arguments.find("--output")
	if output_index >= 0 and output_index + 1 < arguments.size():
		output = arguments[output_index + 1]

	var file: FileAccess = FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()
	print(JSON.stringify(result))
	quit(0 if _failures.is_empty() else 1)


## Instantiate saved components for an ephemeral geometry test, never a world placement or new mesh.
func _component(path: String, position: Vector3, yaw: float) -> Node3D:
	var packed: PackedScene = load(path) as PackedScene
	var node: Node3D = packed.instantiate() as Node3D
	node.position = position
	node.rotation.y = yaw
	root.add_child(node)
	return node


## Mate actual slabs and guards in a test-only assembly with no support placements.
func _assembly_checks() -> void:
	_observations = { "rays": [], "capsules": [], "support_instances": 0 }
	var nodes: Array[Node3D] = []
	var base: String = "res://scenes/prefabs/environment/d06_harbour_footbridge_"
	nodes.append(_component(base + "01.tscn", Vector3(0, 5.5, 0), 0))
	nodes.append(_component(_prefab_path("junction"), Vector3(0, 5.5, 0), 0))
	for entry: Array in [
		["02", "main", Vector3(0, 5.5, -3), 0.0],
		["03", "south", Vector3(2.121320344, 5.5, 2.121320344), -135.0],
		["04", "quay", Vector3(-3, 5.5, 0), 90.0],
	]:
		var yaw: float = deg_to_rad(float(entry[3]))
		var span: Node3D = _component(base + entry[0] + ".tscn", entry[2], yaw)
		nodes.append(span)
		nodes.append(_component(_prefab_path("span"), entry[2], yaw))
		var outgoing: Vector3 = (span.get_node("Sockets/Outgoing") as Node3D).global_position
		var access_path: String = base + "05" + ("" if entry[1] == "main" else "_" + entry[1])
		nodes.append(_component(access_path + ".tscn", outgoing - Vector3(0, 5.5, 0), yaw))
		nodes.append(_component(_prefab_path(entry[1]), outgoing - Vector3(0, 5.5, 0), yaw))

	await physics_frame
	await physics_frame
	# Literal family socket planes; use directions only to rotate the independent seam samples.
	for entry: Array in [
		[Vector3(0, 5.5, -3), 0.0], [Vector3(0, 5.5, -15), 0.0],
		[Vector3(2.121320344, 5.5, 2.121320344), -135.0],
		[Vector3(10.606601718, 5.5, 10.606601718), -135.0],
		[Vector3(-3, 5.5, 0), 90.0], [Vector3(-15, 5.5, 0), 90.0],
	]:
		_seam_queries(nodes[0], entry[0], deg_to_rad(float(entry[1])))

	for node: Node3D in nodes:
		node.queue_free()

	await process_frame


## Require guard continuity and unblocked route centres at both sides of each of six real seams.
func _seam_queries(instance: Node3D, centre: Vector3, yaw: float) -> void:
	var basis: Basis = Basis(Vector3.UP, yaw)
	for offset: float in [-0.01, 0.01]:
		var start: Vector3 = centre + basis * Vector3(0, 0.6, offset)
		_ray(instance, start, centre + basis * Vector3(-2, 0.6, offset), true)
		_ray(instance, start, centre + basis * Vector3(2, 0.6, offset), true)
		_capsule(instance, centre + basis * Vector3(0, 0.91, offset), false)

	_ray(instance, centre + basis * Vector3(0, 0.6, -0.5),
		centre + basis * Vector3(0, 0.6, 0.5), false)
