@tool
extends Node
## Asset-local inspection bridge; never rebuilds or overwrites the authored scene hierarchy.

const MODELS: String = "res://art/models/weapon_effects/weapon_effects_a_"
const KINDS: Array[String] = [
	"muzzle_drop", "fire_lobe", "smoke_puff", "spark", "chip", "trail_puff",
]


## Report exact editor identity before a caller requests inspection or import metadata repair.
func context() -> Dictionary:
	return {
		"project": ProjectSettings.globalize_path("res://").trim_suffix("/"),
		"pid": OS.get_process_id(),
		"editor": Engine.is_editor_hint(),
	}


## Compare linked GLB meshes, extracted draw resources and importer UID targets.
func inspect_sources() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var options: ConfigFile = ConfigFile.new()
	for kind: String in KINDS:
		var source: Node = load(MODELS + kind + ".glb").instantiate()
		var imported: Mesh = (source.get_child(0) as MeshInstance3D).mesh
		var path: String = MODELS + kind + "_mesh.res"
		var draw_mesh: Mesh = load(path)
		var uid: String = ResourceUID.id_to_text(ResourceLoader.get_resource_uid(path))
		options.clear()
		assert(options.load(MODELS + kind + ".glb.import") == OK)
		var meshes: Dictionary = options.get_value("params", "_subresources")["meshes"]
		var mesh_options: Dictionary = meshes.values()[0]
		rows.append({
			"kind": kind,
			"same_resource": imported == draw_mesh,
			"mesh_path": draw_mesh.resource_path,
			"actual_uid": uid,
			"import_uid": mesh_options["save_to_file/path"],
			"aabb": str(draw_mesh.get_aabb()),
		})
		source.free()

	return rows


## Repair only stale extraction UID references, retaining mesh files and scene identities.
func synchronize_import_uids() -> Array[Dictionary]:
	assert(Engine.is_editor_hint())
	var options: ConfigFile = ConfigFile.new()
	for kind: String in KINDS:
		var path: String = MODELS + kind + "_mesh.res"
		options.clear()
		var import_path: String = MODELS + kind + ".glb.import"
		assert(options.load(import_path) == OK)
		var resources: Dictionary = options.get_value("params", "_subresources")
		for key: String in resources["meshes"]:
			resources["meshes"][key]["save_to_file/path"] = ResourceUID.id_to_text(
				ResourceLoader.get_resource_uid(path)
			)
			resources["meshes"][key]["save_to_file/fallback_path"] = path

		options.set_value("params", "_subresources", resources)
		assert(options.save(import_path) == OK)

	return inspect_sources()


## Refresh the editor index after importer-created external mesh files change their UID.
func refresh_mesh_indices() -> void:
	for kind: String in KINDS:
		EditorInterface.get_resource_filesystem().update_file(MODELS + kind + "_mesh.res")
