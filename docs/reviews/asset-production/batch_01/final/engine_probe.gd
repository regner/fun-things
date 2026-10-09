@tool
extends RefCounted
## Independently reads saved prefab resources without editor or resource mutations.


## Captures linked mesh interfaces, world bounds, materials and registered identities.
func inspect(paths: Array) -> Dictionary:
	var results: Array = []
	for path: String in paths:
		var packed: PackedScene = load(path)
		var root: Node = packed.instantiate()
		var rows: Array = []
		walk(root, Transform3D.IDENTITY, rows)
		var model: Node3D = root.get_node("Visuals/Model")
		var uid: int = ResourceLoader.get_resource_uid(path)
		var model_uid: int = ResourceLoader.get_resource_uid(model.scene_file_path)
		results.append({"path": path, "uid": ResourceUID.id_to_text(uid),
			"uid_registered": ResourceUID.has_id(uid), "uid_path": ResourceUID.get_id_path(uid),
			"model": model.scene_file_path, "model_transform": str(model.transform),
			"model_uid": ResourceUID.id_to_text(model_uid),
			"model_registered": ResourceUID.has_id(model_uid),
			"model_uid_path": ResourceUID.get_id_path(model_uid), "rows": rows})
		root.free()
	return {"prefabs": results}


## Recursively measures imported meshes and saved collision shapes.
func walk(node: Node, parent: Transform3D, rows: Array) -> void:
	var pose: Transform3D = parent
	if node is Node3D:
		pose = parent * node.transform
	if node is MeshInstance3D:
		var surfaces: Array = []
		for i: int in node.mesh.get_surface_count():
			var arrays: Array = node.mesh.surface_get_arrays(i)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
			var normal_min: float = INF
			var normal_max: float = 0
			var finite: bool = true
			for vertex: Vector3 in vertices:
				finite = finite and vertex.is_finite()
			for normal: Vector3 in normals:
				finite = finite and normal.is_finite()
				normal_min = min(normal_min, normal.length())
				normal_max = max(normal_max, normal.length())
			var mat: Material = node.get_active_material(i)
			var material: Dictionary = {"class": mat.get_class(), "name": mat.resource_name,
				"path": mat.resource_path}
			if mat is StandardMaterial3D:
				material.merge({"albedo": str(mat.albedo_color), "metallic": mat.metallic,
					"roughness": mat.roughness, "emission_enabled": mat.emission_enabled,
					"emission": str(mat.emission), "cull_mode": mat.cull_mode,
					"albedo_texture": str(mat.albedo_texture)})
			surfaces.append({"vertices": vertices.size(), "normals": normals.size(),
				"normal_min": normal_min, "normal_max": normal_max, "finite": finite,
				"uv_count": arrays[Mesh.ARRAY_TEX_UV].size() if arrays[Mesh.ARRAY_TEX_UV] != null else 0,
				"indices": arrays[Mesh.ARRAY_INDEX].size(), "material": material})
		var bounds: AABB = pose * node.get_aabb()
		rows.append({"node": str(node.name), "type": "mesh", "mesh_path": node.mesh.resource_path,
			"min": [bounds.position.x,bounds.position.y,bounds.position.z],
			"max": [bounds.end.x,bounds.end.y,bounds.end.z], "surfaces": surfaces})
	if node is CollisionShape3D:
		var shape: Shape3D = node.shape
		var row: Dictionary = {"node": str(node.name), "type": "collision", "class": shape.get_class(),
			"pose": str(pose), "disabled": node.disabled}
		if shape is CylinderShape3D:
			row.merge({"radius": shape.radius,"height": shape.height})
		if shape is BoxShape3D:
			row["size"] = str(shape.size)
		if shape is ConvexPolygonShape3D:
			row["points"] = str(shape.points)
		rows.append(row)
	if node is CollisionObject3D:
		rows.append({"node": str(node.name), "type": "body", "layer": node.collision_layer,
			"mask": node.collision_mask})
	for child: Node in node.get_children():
		walk(child, pose, rows)


## Independently probes ring clearance and visible-overhead collision boundaries.
func runtime_probe(scene: Node3D) -> Dictionary:
	var shape := SphereShape3D.new()
	shape.radius = 0.02
	var parameter := PhysicsShapeQueryParameters3D.new()
	parameter.shape = shape
	parameter.collision_mask = 1
	var results: Array = []
	var positions: Array[Vector3] = [Vector3(-4,0.25,3),Vector3(-3.41,0.25,3),
		Vector3(-3.34,0.25,3),Vector3(-3.15,0.25,3),Vector3(0,0.3,3),
		Vector3(1.25,0.3,3),Vector3(-2,5.4,0),Vector3(-2,5.6,0),
		Vector3(2,2.5,0),Vector3(2,2.8,0)]
	for position: Vector3 in positions:
		parameter.transform = Transform3D(Basis.IDENTITY,position)
		var hits: Array[Dictionary] = scene.get_world_3d().direct_space_state.intersect_shape(parameter,32)
		var paths: Array = []
		for hit: Dictionary in hits:
			paths.append(str(hit.collider.get_path()))
		results.append({"position":str(position),"hit_paths":paths})
	return {"small_sphere_radius":shape.radius,"independent_queries":results,
		"public_fixture_observations":scene.probe_queries()}
