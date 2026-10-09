extends SceneTree
## Independent CPU reconstruction of the imported Godot skin's world-space ground contact.


## Start after singleton initialization.
func _initialize() -> void:
	_check.call_deferred()


## Use imported bind matrices and current Godot poses, independent of source authoring formulas.
func _check() -> void:
	var packed: PackedScene = load(
		"res://scenes/prefabs/pedestrian_civilian/pedestrian_worker_a.tscn"
	)
	var actor: Node3D = packed.instantiate()
	root.add_child(actor)
	var mesh: MeshInstance3D = actor.find_child("WorkerMesh", true, false)
	var skeleton: Skeleton3D = actor.find_child("Skeleton3D", true, false)
	var rows: Array[Dictionary] = _sample_contacts(actor, mesh, skeleton)
	var receipt := FileAccess.open(
		"res://docs/assets/pedestrian_worker_a-evidence/imported_contact.json",
		FileAccess.WRITE,
	)
	receipt.store_string(JSON.stringify(rows, "\t") + "\n")
	print("WORKER_IMPORTED_CONTACT " + JSON.stringify(rows))
	quit()


## Sample every retained clip at the original four normalized times.
func _sample_contacts(
	actor: Node3D, mesh: MeshInstance3D, skeleton: Skeleton3D
) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for clip: String in ["idle", "walk", "run", "death"]:
		actor.play_clip(clip, 0)
		var player: AnimationPlayer = actor.animation_player()
		var duration: float = player.get_animation("npc/" + clip).length
		for time: float in [0.0, duration * .25, duration * .5, duration]:
			player.seek(time, true)
			player.advance(0)
			skeleton.force_update_all_bone_transforms()
			var minimum: float = _minimum_vertex_y(mesh, skeleton)
			assert(minimum >= -.006 and minimum <= .006, "Imported stance contact outside 6 mm")
			rows.append(_contact_row(clip, time, minimum))
	return rows


## Preserve the original receipt fields for one sampled contact.
func _contact_row(clip: String, time: float, minimum: float) -> Dictionary:
	return {
		"clip": clip,
		"time": time,
		"world_min_y": minimum,
	}


## Reconstruct the lowest skinned vertex in world space for the current pose.
func _minimum_vertex_y(mesh: MeshInstance3D, skeleton: Skeleton3D) -> float:
	var arrays: Array = mesh.mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
	var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
	var transforms: Array[Transform3D] = _skin_transforms(mesh, skeleton)
	var minimum: float = INF
	for index: int in vertices.size():
		var position: Vector3 = Vector3.ZERO
		for influence: int in 4:
			var offset: int = index * 4 + influence
			position += (transforms[bones[offset]] * vertices[index]) * weights[offset]
		minimum = minf(minimum, position.y)
	return minimum


## Resolve each imported bind to the current world-space bone transform.
func _skin_transforms(
	mesh: MeshInstance3D, skeleton: Skeleton3D
) -> Array[Transform3D]:
	var transforms: Array[Transform3D] = []
	for bind: int in mesh.skin.get_bind_count():
		var bone: int = skeleton.find_bone(mesh.skin.get_bind_name(bind))
		if bone < 0:
			bone = mesh.skin.get_bind_bone(bind)
		transforms.append(
			skeleton.global_transform
			* skeleton.get_bone_global_pose(bone)
			* mesh.skin.get_bind_pose(bind)
		)
	return transforms
