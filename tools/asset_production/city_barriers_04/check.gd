extends "res://tools/asset_production/city_quay_furniture_02/check.gd"
## Check the terminal reference using its source kit's measured interface and motion probes.

const REFERENCE := "res://scenes/prefabs/environment/city_barriers_04.tscn"
const LANDWARD := "res://scenes/prefabs/environment/city_quay_furniture_02_end_landward.tscn"
const REFERENCE_FIXTURE := "res://tools/asset_production/city_barriers_04/check_scene.tscn"
const REFERENCE_EVIDENCE := "res://docs/assets/production/city_barriers_04-evidence/validation.json"


## Normalize only owned scenes, then verify linked ancestry, bounds and inherited collision.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		_roundtrip(REFERENCE)
		_roundtrip(REFERENCE_FIXTURE)
		_report["save_reload_byte_stable"] = true

	_check_dependencies(REFERENCE_FIXTURE)
	var packed: PackedScene = load(REFERENCE_FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	var reference: Node3D = fixture.get_node("Reference")
	var rail: Node3D = reference.get_node("RailTerminal")
	_require(reference.scene_file_path == REFERENCE, "Unlinked reference")
	_require(reference.transform == Transform3D.IDENTITY, "Reference transform")
	_require(reference.get_child_count() == 1, "Unexpected assembly components")
	_require(rail.scene_file_path == LANDWARD, "Must reuse existing landward prefab")
	_require(rail.transform == Transform3D.IDENTITY, "Changed landward datum/axes/scale")
	var receipt: Dictionary = _check_model(rail, "end", "landward")
	receipt["physics"] = await _check_physics(fixture, rail, "end", "landward")
	receipt["terminal_reach"] = _check_terminal_reach(fixture, rail)
	_report["prefabs"][REFERENCE] = receipt
	fixture.free()
	if _failed:
		quit(1)
		return

	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(REFERENCE_EVIDENCE))
	if not _report.has("save_reload_byte_stable"):
		_report["save_reload_byte_stable"] = data.get("godot", {}).get(
			"save_reload_byte_stable", false,
		)

	_report["engine"] = Engine.get_version_info()["string"]
	_report["existing_prefab_identity_instance"] = true
	data["godot"] = _report
	var file: FileAccess = FileAccess.open(REFERENCE_EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "\t") + "\n")
	file.close()
	print("CITY_BARRIERS_04_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Check the return tip blocks below the tube while space beyond both footprint ends stays clear.
func _check_terminal_reach(fixture: Node3D, rail: Node3D) -> Dictionary:
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	var tip := PhysicsRayQueryParameters3D.create(Vector3(.52, .2, -1), Vector3(.52, .2, 1), 1)
	var hit: Dictionary = space.intersect_ray(tip)
	_require(not hit.is_empty(), "Return tip has no blocking envelope")
	if not hit.is_empty():
		_require(hit["collider"] == rail.get_node("Collision/RailBody"), "Wrong terminal body")

	for x: float in [-.17, .545]:
		# gdstyle:ignore=quality/allocation-in-loop
		var outside := PhysicsRayQueryParameters3D.create(
			Vector3(x, .2, -1), Vector3(x, .2, 1), 1,
		)
		_require(
			space.intersect_ray(outside).is_empty(), "Collision extends beyond terminal footprint",
		)

	return { "tip_x_m": .52, "tip_low_ray_blocked": true,
		"outside_x_m": [-.17, .545], "outside_rays_clear": true }
