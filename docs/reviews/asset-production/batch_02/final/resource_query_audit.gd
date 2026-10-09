extends SceneTree
## Reads exact imported resources and independently probes saved physical envelopes.

var ids = ["city_planting_03", "city_planting_04_compact", "city_planting_04_broad",
 "city_planting_05_short_tuft", "city_planting_05_spreading_clump",
 "city_roof_details_01", "city_roof_details_02", "city_shop_fittings_01"]

## Defers until the tree can accept inspected instances.
func _initialize() -> void:
	call_deferred("run")

## Converts Godot vectors into explicit numerical JSON coordinates.
func vector(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

## Reads a node's full imported visible-mesh envelope without generated geometry.
func envelope(node: Node3D) -> Dictionary:
	var first = true
	var merged = AABB()
	var meshes = []
	for child in node.find_children("*", "MeshInstance3D", true, false):
		var mesh = child as MeshInstance3D
		var box = mesh.global_transform * mesh.get_aabb()
		merged = box if first else merged.merge(box)
		first = false
		var materials = []
		for surface in range(mesh.mesh.get_surface_count()):
			var material = mesh.get_active_material(surface)
			var mat = {"class": material.get_class() if material else "null"}
			if material is BaseMaterial3D:
				mat["albedo"] = [material.albedo_color.r, material.albedo_color.g, material.albedo_color.b, material.albedo_color.a]
				mat["roughness"] = material.roughness
				mat["metallic"] = material.metallic
				mat["cull_mode"] = material.cull_mode
				mat["transparency"] = material.transparency
			materials.append(mat)
		meshes.append({"path": str(node.get_path_to(mesh)), "source": mesh.mesh.resource_path,
		 "bounds_min": vector(box.position), "bounds_max": vector(box.end), "materials": materials,
		 "override": mesh.material_override != null})
	return {"min": vector(merged.position), "max": vector(merged.end), "size": vector(merged.size), "meshes": meshes}

## Uses a small independent sphere to distinguish solids from decorative visual volumes.
func query(node: Node3D, point: Vector3, radius: float) -> Array:
	var sphere = SphereShape3D.new()
	sphere.radius = radius
	var params = PhysicsShapeQueryParameters3D.new()
	params.shape = sphere
	params.transform = Transform3D(Basis.IDENTITY, point)
	params.collision_mask = 1
	var hits = []
	for hit in node.get_world_3d().direct_space_state.intersect_shape(params, 32):
		hits.append(str(hit.collider.get_path()))
	return hits

## Inspects all eight wrappers, linked models, actual mounts and independent collision samples.
func run() -> void:
	var rows = []
	for id in ids:
		var path = "res://scenes/prefabs/environment/" + id + ".tscn"
		var packed = load(path) as PackedScene
		if packed == null:
			push_error("Missing reviewed prefab: " + path)
			quit(2)
			return
		var node = packed.instantiate()
		root.add_child(node)
		var model = node.get_node("Visuals/Model")
		var state = packed.get_state()
		var identities = []
		for index in range(state.get_node_count()):
			var entry = {"path": str(state.get_node_path(index)), "type": str(state.get_node_type(index)),
			 "instance": state.get_node_instance(index).resource_path if state.get_node_instance(index) else ""}
			if state.has_method("get_node_unique_id"):
				entry["unique_id"] = state.call("get_node_unique_id", index)
			identities.append(entry)
		var bodies = []
		for body in node.find_children("*", "CollisionObject3D", true, false):
			bodies.append({"path": str(node.get_path_to(body)), "layer": body.collision_layer, "mask": body.collision_mask})
		rows.append({"id": id,"path": path,"uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(path)),
		 "model_source": model.scene_file_path, "model_transform_identity": model.transform.is_equal_approx(Transform3D.IDENTITY),
		 "root_transform_identity": node.transform.is_equal_approx(Transform3D.IDENTITY),
		 "visual_transform_identity": node.get_node("Visuals").transform.is_equal_approx(Transform3D.IDENTITY),
		 "envelope": envelope(node), "bodies": bodies,"saved_node_identities": identities})
		node.free()
	var fixture = load("res://tests/fixtures/asset_production/batch_02_camera.tscn").instantiate()
	root.add_child(fixture)
	fixture.set_process(false)
	fixture.set_physics_process(false)
	await physics_frame
	await physics_frame
	var mounts = {}
	for label in ["Shop", "RoofVent", "RoofEnclosure", "Canopy", "CompactTree", "BroadTree", "CompactSurround", "BroadSurround", "Trough", "ShrubWest", "ShrubEast"]:
		var node = fixture.get_node(label)
		mounts[label] = {"position": vector(node.global_position),"bounds":envelope(node)}
	var samples = {}
	for point in [Vector3(-4,1,2),Vector3(-4.4,1,2),Vector3(-4,1.7,2),Vector3(-4,2.7,2),
	 Vector3(4,1,2),Vector3(-7,.5,0),Vector3(-6,.1,5),Vector3(6,.1,5),Vector3(3,11,-12),Vector3(0,2.7,-5.8)]:
		samples[str(point)] = query(fixture,point,.05)
	var actor = fixture.get_node("ProbeActor")
	actor.neutralize()
	actor.global_position = Vector3(-2,0,-5.8)
	for tick in range(120):
		actor.step({"move":Vector2.RIGHT,"aim_yaw":PI/2.0,"fire":false},1.0/60.0)
		await physics_frame
	var canopy_travel = vector(actor.global_position)
	print("INDEPENDENT_BATCH02 " + JSON.stringify({"engine":Engine.get_version_info(),"pid":OS.get_process_id(),
	 "project":ProjectSettings.globalize_path("res://"),"rows":rows,"mounts":mounts,
	 "sphere_query_radius_m":.05,"query_samples":samples,"canopy_travel":canopy_travel,
	 "fixture_camera":{"height":fixture.get_node("GameCamera").global_position.y,"fov":fixture.get_node("GameCamera").fov}}))
	fixture.queue_free()
	await process_frame
	quit(0)
