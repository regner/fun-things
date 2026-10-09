extends SceneTree
## Loads every current asset-production fixture to catch missing dependencies after moves.

const FIXTURE_DIRECTORY: String = "res://tests/assets/asset_production"


## Defers fixture loading until the SceneTree root can accept instantiated scenes.
func _initialize() -> void:
	_check_all.call_deferred()


## Loads and instantiates every saved fixture scene, then exits with an explicit result.
func _check_all() -> void:
	var paths: Array[String] = []
	_collect_scene_paths(FIXTURE_DIRECTORY, paths)
	paths.sort()
	var loaded: Array[String] = []
	for path: String in paths:
		var resource: Resource = load(path)
		if not resource is PackedScene:
			print("ASSET_FIXTURE_CHECK invalid scene: ", path)
			quit(1)
			return

		var instance: Node = (resource as PackedScene).instantiate()
		if instance == null:
			print("ASSET_FIXTURE_CHECK failed to instantiate: ", path)
			quit(1)
			return

		root.add_child(instance)
		await process_frame  # gdstyle:ignore=quality/await-in-loop
		instance.free()
		loaded.append(path)

	print("ASSET_FIXTURE_CHECK ", JSON.stringify({ "passed": true, "scenes": loaded }))
	quit(0)


## Recursively discovers fixture scenes without depending on a stale hand-maintained list.
func _collect_scene_paths(directory: String, paths: Array[String]) -> void:
	for file_name: String in DirAccess.get_files_at(directory):
		if file_name.ends_with(".tscn"):
			paths.append(directory.path_join(file_name))

	for child_name: String in DirAccess.get_directories_at(directory):
		_collect_scene_paths(directory.path_join(child_name), paths)
