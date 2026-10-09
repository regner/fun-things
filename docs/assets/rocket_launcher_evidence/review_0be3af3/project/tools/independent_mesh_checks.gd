extends SceneTree

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	var report: Dictionary = {}
	for file in ["dock_thumper_launcher_a", "dock_thumper_rocket_a", "dock_thumper_preview_stage"]:
		var path: String = "res://art/models/rocket_launcher/" + file + ".glb"
		var packed: PackedScene = load(path)
		assert(packed != null)
		var model: Node3D = packed.instantiate()
		root.add_child(model)
		assert(model.transform.is_equal_approx(Transform3D.IDENTITY))
		var rows: Array = []
		for child in model.find_children("*", "MeshInstance3D", true, false):
			var mesh_node: MeshInstance3D = child
			assert(mesh_node.scale.is_equal_approx(Vector3.ONE))
			assert(mesh_node.basis.is_equal_approx(Basis.IDENTITY))
			assert(mesh_node.material_override == null)
			for index in range(mesh_node.mesh.get_surface_count()):
				var material: StandardMaterial3D = mesh_node.mesh.surface_get_material(index)
				assert(material != null)
				assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
				var arrays: Array = mesh_node.mesh.surface_get_arrays(index)
				var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
				var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
				var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
				assert(normals.size() == vertices.size())
				var zero_triangles: int = 0
				for triangle in range(0, indices.size(), 3):
					var a: Vector3 = vertices[indices[triangle]]
					var b: Vector3 = vertices[indices[triangle + 1]]
					var c: Vector3 = vertices[indices[triangle + 2]]
					if (b-a).cross(c-a).length() == 0.0:
						zero_triangles += 1
				for normal in normals:
					assert(normal.is_finite() and absf(normal.length()-1) < 0.001)
				rows.append({"object":mesh_node.name,"material":material.resource_name,
					"triangles":indices.size()/3,"zero_triangles":zero_triangles,
					"normal_count":normals.size(),"color":str(material.albedo_color),
					"roughness":material.roughness,"metallic":material.metallic,
					"emission_enabled":material.emission_enabled,"cull_mode":material.cull_mode})
		report[file] = rows
		model.queue_free()
		await process_frame
	var out: FileAccess = FileAccess.open("res://independent_mesh_checks.json",FileAccess.WRITE)
	out.store_string(JSON.stringify(report,"\t")+"\n")
	print("INDEPENDENT_MESH_CHECKS_PASS")
	quit()
