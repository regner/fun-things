class_name SharedHumanoidBindCheck
extends SceneTree
## Inspect the source-linked canonical rig without altering any scene.


## Check imported joint names and armature-space head locations against source data.
func _initialize() -> void:
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
		"res://art/source/models/characters/shared_humanoid/shared_humanoid_v1.json"))
	var packed: PackedScene = load(
		"res://art/models/characters/shared_humanoid/shared_humanoid_bind_v1.glb"
	)
	var model: Node = packed.instantiate()
	var skeleton: Skeleton3D = model.find_child("Skeleton3D", true, false) as Skeleton3D
	assert(skeleton != null)
	assert(skeleton.get_bone_count() == 28)
	for row: Dictionary in manifest.bones:
		var index: int = skeleton.find_bone(row.name)
		assert(index >= 0)
		var head: Array = row.head_blender_m
		var expected: Vector3 = Vector3(head[0], head[2], -head[1])
		assert(skeleton.get_bone_global_rest(index).origin.distance_to(expected) < 0.00001,
			"Rest origin mismatch: " + str(row.name))
		var parent: int = skeleton.get_bone_parent(index)
		if row.parent == null:
			assert(parent == -1)
		else:
			assert(skeleton.get_bone_name(parent) == row.parent)
	print(
		"PLAYER_BIND_CHECK PASS: 28 exact named rest origins/parents; path=",
		model.get_path_to(skeleton),
	)
	model.free()
	quit()
