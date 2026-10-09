extends SceneTree

const NID: String = "d06_harbour_footbridge_05"
const SCRATCH: String = "C:/tmp/ft/assets/d06_harbour_footbridge_05/"
const TOLERANCE_M: float = 0.001
const SEAM_HEIGHT_TOLERANCE_M: float = 0.007
const WORLD_LAYER: int = 1
const EDITOR_STARTUP_SECONDS: float = 3.0

var _failures: Array[String] = []
var _variants: Dictionary = {}
var _observations: Dictionary = {}


## Wait for the standalone headless tree to initialize.
func _initialize() -> void:
	_run.call_deferred()


## Retain every failed contract and guarantee a failing process exit.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Resolve the three owned wrappers without changing the default main variant path.
func _prefab_path(variant: String) -> String:
	var suffix: String = "" if variant == "main" else "_" + variant
	return "res://scenes/prefabs/environment/" + NID + suffix + ".tscn"


## Normalize each newly authored wrapper and require a byte-identical second save.
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


## Inspect linked geometry, materials, identity transforms and registered resource identities.
func _inspect(instance: Node3D, variant: String) -> void:
	var model_path: String = (
		"res://art/models/environment/" + NID + "/" + NID + "_" + variant + ".glb"
	)
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == model_path, "Linked model ancestry")
	_expect(model.transform == Transform3D.IDENTITY, "Identity imported instance")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One source-linked mesh")
	if meshes.is_empty():
		return

	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.global_transform * mesh.get_aabb()
	var expected: AABB = AABB(Vector3(-1.6, -0.35, -19.84), Vector3(3.2, 5.85, 19.84))
	if variant == "south":
		expected = AABB(Vector3(-1.6, -0.35, -11.52), Vector3(11.52, 5.85, 11.52))
	elif variant == "quay":
		expected = AABB(Vector3(-9.92, -0.35, -11.52), Vector3(11.52, 5.85, 11.52))

	_expect(bounds.position.distance_to(expected.position) < TOLERANCE_M, "AABB minimum")
	_expect(bounds.size.distance_to(expected.size) < TOLERANCE_M, "AABB dimensions")
	_expect(mesh.mesh.resource_path.begins_with(model_path), "Imported mesh dependency")
	_expect(mesh.mesh.get_surface_count() == 3, "Three material surfaces")
	var materials: Array[String] = []
	for index: int in range(mesh.mesh.get_surface_count()):
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(index) as BaseMaterial3D
		_expect(material != null, "Material dependency resolves")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back-culling material")
		materials.append(material.resource_name)

	_expect(materials == ["deck_warm_pale", "deck_pale_fascia", "deck_petrol_underside"],
		"Family surface names/order")
	_check_collision(instance)

	_observations["bounds"] = { "min": bounds.position, "size": bounds.size }
	_observations["materials"] = materials
	_observations["collision_shapes"] = 5
	_observations["linked_identity_model"] = true
	for path: String in [_prefab_path(variant), model_path]:
		var uid: int = ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Registered UID: " + path)
		_observations[path.get_extension() + "_uid"] = ResourceUID.id_to_text(uid)

	_check_sockets(instance, model, variant)


## Inspect the saved three landing boxes and two continuous ramp prisms.
func _check_collision(instance: Node3D) -> void:
	var body: StaticBody3D = instance.get_node("Collision/Body") as StaticBody3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "Static world layers")
	_expect(body.get_child_count() == 5, "Three landings and two flights only")
	for child: Node in body.get_children():
		var shape: Shape3D = (child as CollisionShape3D).shape
		if str(child.name).begins_with("Flight"):
			_expect(
				shape is ConvexPolygonShape3D,
				"Continuous convex flight, not stepped collision",
			)
			_expect((shape as ConvexPolygonShape3D).points.size() == 8, "Eight ramp prism corners")
		else:
			_expect(shape is BoxShape3D, "Simple landing box")
			_expect((shape as BoxShape3D).size.distance_to(Vector3(3.2, 0.35, 3.2)) < TOLERANCE_M,
				"Landing box dimensions")


## Compare public markers to the complete source transforms and independent local expectations.
func _check_sockets(instance: Node3D, model: Node3D, variant: String) -> void:
	var ground: Vector3 = Vector3(0, 0, -19.84)
	var outward: Vector3 = Vector3.FORWARD
	if variant == "south":
		ground = Vector3(9.92, 0, -9.92)
		outward = Vector3.RIGHT
	elif variant == "quay":
		ground = Vector3(-9.92, 0, -9.92)
		outward = Vector3.LEFT

	for entry: Dictionary in [
		{ "public": "Incoming", "source": "incoming", "position": Vector3(0, 5.5, 0),
			"forward": Vector3.BACK },
		{ "public": "Ground", "source": "ground", "position": ground, "forward": outward },
	]:
		var marker: Node3D = instance.get_node("Sockets/" + entry["public"]) as Node3D
		var source: Node3D = model.find_child(
			"socket_" + entry["source"] + "_" + variant, true, false
		) as Node3D
		_expect(source != null, "Exported socket exists")
		if source == null:
			continue

		_expect(
			marker.global_transform.is_equal_approx(source.global_transform),
			"Socket full mapping",
		)
		_expect(marker.position.distance_to(entry["position"]) < TOLERANCE_M, "Socket position")
		_expect((-marker.basis.z).distance_to(entry["forward"]) < TOLERANCE_M,
			"Socket outward -Z " + variant + "/" + str(entry["public"]))
		_expect(marker.basis.y.distance_to(Vector3.UP) < TOLERANCE_M, "Socket up")

	_observations["socket_transforms_match_source"] = true
	_observations["ground_socket"] = ground


## Query one independent top location and record height, solid/void and actual slope.
func _ray(instance: Node3D, sample: Vector3, solid: bool, tolerance: float) -> Dictionary:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var hit: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(
		Vector3(sample.x, 7, sample.z), Vector3(sample.x, -1, sample.z), WORLD_LAYER
	))
	_expect(not hit.is_empty() == solid, "Solid/void ray at %s" % sample)
	if not hit.is_empty():
		var position: Vector3 = hit["position"]
		var normal: Vector3 = hit["normal"]
		_expect(absf(position.y - sample.y) < tolerance, "Surface height at %s" % sample)
		return {
			"sample": sample,
			"height": position.y,
			"slope_degrees": rad_to_deg(normal.angle_to(Vector3.UP)),
		}

	return { "sample": sample, "solid": false }


## Measure both flight slopes, all landings, boundary voids and continuous landing transitions.
func _physics_checks(instance: Node3D, variant: String) -> void:
	var observations: Array[Dictionary] = []
	for sample: Vector3 in [Vector3(0, 5.5, -1.6), Vector3(0, 4.125, -5.76),
		Vector3(0, 2.75, -9.92)]:
		observations.append(_ray(instance, sample, true, TOLERANCE_M))

	var sign_x: float = -1.0 if variant == "quay" else 1.0
	var flight: Vector3 = Vector3(0, 1.375, -14.08)
	var apron: Vector3 = Vector3(0, 0, -18.24)
	if variant != "main":
		flight = Vector3(sign_x * 4.16, 1.375, -9.92)
		apron = Vector3(sign_x * 8.32, 0, -9.92)

	observations.append(_ray(instance, flight, true, TOLERANCE_M))
	observations.append(_ray(instance, apron, true, TOLERANCE_M))
	for index: int in [1, 3]:
		var slope: float = observations[index].get("slope_degrees", -1.0)
		_expect(slope > 28.2 and slope < 28.3, "Independent flight slope range")

	for sample: Vector3 in [Vector3(1.61, 0, -5.76), Vector3(-1.61, 0, -5.76),
		Vector3(0, 0, 0.1), Vector3(3, 0, -2)]:
		observations.append(_ray(instance, sample, false, TOLERANCE_M))

	for sample: Vector3 in [Vector3(0, 5.5, -3.19), Vector3(0, 5.5, -3.21),
		Vector3(0, 2.75, -8.31), Vector3(0, 2.75, -8.33)]:
		observations.append(_ray(instance, sample, true, SEAM_HEIGHT_TOLERANCE_M))

	if variant == "main":
		for sample: Vector3 in [Vector3(0, 2.75, -11.51), Vector3(0, 2.75, -11.53),
			Vector3(0, 0, -16.63), Vector3(0, 0, -16.65)]:
			observations.append(_ray(instance, sample, true, SEAM_HEIGHT_TOLERANCE_M))
	else:
		for sample: Vector3 in [Vector3(sign_x * 1.59, 2.75, -9.92),
			Vector3(sign_x * 1.61, 2.75, -9.92), Vector3(sign_x * 6.71, 0, -9.92),
			Vector3(sign_x * 6.73, 0, -9.92)]:
			observations.append(_ray(instance, sample, true, SEAM_HEIGHT_TOLERANCE_M))

	_observations["isolated_rays"] = observations


## Mate each saved access prefab to its actual family span and query both sides of the upper seam.
func _span_seam(instance: Node3D, variant: String) -> void:
	var family_id: String = { "main": "02", "south": "03", "quay": "04" }[variant]
	var span_scene: PackedScene = load(
		"res://scenes/prefabs/environment/d06_harbour_footbridge_" + family_id + ".tscn"
	) as PackedScene
	var span: Node3D = span_scene.instantiate() as Node3D
	span.position = Vector3(0, 5.5, 12)
	root.add_child(span)
	var outgoing: Node3D = span.get_node("Sockets/Outgoing") as Node3D
	var incoming: Node3D = instance.get_node("Sockets/Incoming") as Node3D
	_expect(incoming.global_position.distance_to(outgoing.global_position) < TOLERANCE_M,
		"Span outgoing/access incoming coincide")
	_expect(incoming.global_basis.z.distance_to(-outgoing.global_basis.z) < TOLERANCE_M,
		"Span/access outward axes opposed")
	await physics_frame
	await physics_frame
	var observations: Array[Dictionary] = []
	for sample: Vector3 in [Vector3(-1.5, 5.5, 0.01), Vector3(-1.5, 5.5, -0.01),
		Vector3(0, 5.5, 0.01), Vector3(0, 5.5, -0.01),
		Vector3(1.5, 5.5, 0.01), Vector3(1.5, 5.5, -0.01)]:
		observations.append(_ray(instance, sample, true, TOLERANCE_M))

	_observations["span_" + family_id + "_seam"] = observations
	span.queue_free()
	await process_frame


## Run only resource/geometry checks; record production actor limitations without altering gameplay.
func _run() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	for variant: String in ["main", "south", "quay"]:
		_observations = {}
		if arguments.has("--normalize"):
			_roundtrip(_prefab_path(variant))

		var packed: PackedScene = ResourceLoader.load(
			_prefab_path(variant), "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
		) as PackedScene
		_expect(packed != null, "All prefab dependencies resolve")
		if packed == null:
			continue

		var instance: Node3D = packed.instantiate() as Node3D
		root.add_child(instance)
		_inspect(instance, variant)
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		_physics_checks(instance, variant)
		await _span_seam(instance, variant)  # gdstyle:ignore=quality/await-in-loop
		instance.queue_free()
		await process_frame  # gdstyle:ignore=quality/await-in-loop
		_variants[variant] = _observations

	var actor_state: Dictionary = _actor_contract()
	var result: Dictionary = { "ok": _failures.is_empty(), "failures": _failures,
		"variants": _variants, "actor_contract_observed": actor_state,
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


## Record the production player floor settings without entering the tree or simulating movement.
func _actor_contract() -> Dictionary:
	var player_scene: PackedScene = load("res://scenes/entities/player.tscn") as PackedScene
	var player: CharacterBody3D = player_scene.instantiate() as CharacterBody3D
	var actor_state: Dictionary = {
		"floor_max_angle_degrees": rad_to_deg(player.floor_max_angle),
		"motion_mode": player.motion_mode,
		"traversal": "Pending: current player is FLOATING; ActorMotion has no gravity/descent.",
	}
	_expect(rad_to_deg(player.floor_max_angle) > 28.3, "Ramp slope below production floor angle")
	player.free()
	return actor_state
