extends SceneTree

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	var ids: Array[String] = ["city_shop_fittings_02", "city_shop_fittings_03_single", "city_shop_fittings_03_double", "city_shop_fittings_05", "city_shop_fittings_06_single", "city_shop_fittings_06_double", "city_shop_fittings_07", "city_shop_fittings_08", "city_small_shop_shells_01"]
	var rows: Array = []
	var passed: bool = true
	for ident: String in ids:
		var path: String = "res://scenes/prefabs/environment/" + ident + ".tscn"
		var packed: PackedScene = load(path)
		if packed == null:
			passed = false
			continue
		var n: Node3D = packed.instantiate()
		var model: Node3D = n.get_node("Visuals/Model")
		var source_id: String = ident.trim_suffix("_single").trim_suffix("_double")
		var expected: String = "res://art/models/environment/" + source_id + "/" + ident + ".glb"
		var valid: bool = model.scene_file_path == expected and model.transform == Transform3D.IDENTITY
		var meshes: Array = []
		for child: Node in model.find_children("*", "MeshInstance3D", true, false):
			var mesh: MeshInstance3D = child
			valid = valid and mesh.mesh.resource_path.begins_with(expected + "::") and mesh.material_override == null
			var mats: Array = []
			var triangles: int = 0
			for s: int in range(mesh.mesh.get_surface_count()):
				var arrays: Array = mesh.mesh.surface_get_arrays(s)
				triangles += arrays[Mesh.ARRAY_INDEX].size()/3
				var m: StandardMaterial3D = mesh.mesh.surface_get_material(s)
				valid = valid and m != null and m.cull_mode == BaseMaterial3D.CULL_BACK and m.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED and mesh.get_surface_override_material(s) == null
				mats.append({"slot":s,"name":m.resource_name,"cull":m.cull_mode,"alpha":m.transparency})
			meshes.append({"name":mesh.name,"path":mesh.mesh.resource_path,"bounds":str(mesh.get_aabb()),"materials":mats,"triangles":triangles})
		var bodies: Array = []
		for body: Node in n.find_children("*", "StaticBody3D", true, false):
			valid = valid and body.collision_layer == 1 and body.collision_mask == 0
			bodies.append(str(body.get_path()) if body.is_inside_tree() else str(n.get_path_to(body)))
		passed = passed and valid
		rows.append({"path":path,"model":model.scene_file_path,"valid":valid,"meshes":meshes,"bodies":bodies,"uid":ResourceUID.id_to_text(ResourceLoader.get_resource_uid(path))})
		n.free()
	print("REVIEW_RESOURCE ",JSON.stringify({"engine":Engine.get_version_info().string,"project":ProjectSettings.globalize_path("res://"),"passed":passed,"rows":rows}))
	quit(0 if passed else 1)
