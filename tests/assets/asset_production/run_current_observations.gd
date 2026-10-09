extends SceneTree
## Replays current batch observations through test-only scale, clearance, and sight probes.

const MAX_PHYSICS_TICKS: int = 700
const CASES: Array[Dictionary] = [
	{
		"batch": "batch_01",
		"scene": "res://tests/assets/asset_production/batch_01_camera.tscn",
		"outcomes": 4,
		"outcome_property": "motion_outcomes",
		"extra": "",
	},
	{
		"batch": "batch_02",
		"scene": "res://tests/assets/asset_production/batch_02_camera.tscn",
		"outcomes": 4,
		"outcome_property": "motion_outcomes",
		"extra": "placement_receipt",
	},
	{
		"batch": "batch_03",
		"scene": "res://tests/assets/asset_production/batch_03_camera.tscn",
		"outcomes": 5,
		"outcome_property": "outcomes",
		"extra": "assembly_checks",
	},
]


## Defers observation setup until the SceneTree root can accept the saved fixtures.
func _initialize() -> void:
	_run.call_deferred()


## Runs each saved observation to completion and emits one machine-readable receipt.
func _run() -> void:  # gdstyle:ignore=quality/max-local-variables,quality/max-function-length
	var rows: Array[Dictionary] = []
	var passed: bool = true
	for case: Dictionary in CASES:
		var scene_path: String = case.scene
		var expected_outcomes: int = case.outcomes
		var outcome_property: String = case.outcome_property
		var extra_method: String = case.extra
		var packed: PackedScene = load(scene_path)
		var fixture: Node = packed.instantiate()
		root.add_child(fixture)
		var ticks: int = 0
		while _outcome_count(fixture, outcome_property) < expected_outcomes:
			await physics_frame  # gdstyle:ignore=quality/await-in-loop
			ticks += 1
			if ticks >= MAX_PHYSICS_TICKS:
				break

		var probe_value: Variant = fixture.call("probe_queries")
		if not probe_value is Dictionary:
			print("ASSET_CURRENT_OBSERVATIONS invalid probe result: ", case.batch)
			fixture.free()
			quit(1)
			return

		var probe: Dictionary = probe_value
		probe.erase("frame_samples")
		probe.erase("render_samples")
		probe.erase("samples")
		var row: Dictionary = {
			"batch": case.batch,
			"physics_ticks": ticks,
			"probe": probe,
		}
		if not extra_method.is_empty():
			var extra_value: Variant = fixture.call(extra_method)
			if not extra_value is Dictionary:
				print("ASSET_CURRENT_OBSERVATIONS invalid extra result: ", case.batch)
				fixture.free()
				quit(1)
				return

			var extra_result: Dictionary = extra_value
			row["extra"] = extra_result
			passed = passed and extra_result.passed

		passed = passed and probe.passed and ticks < MAX_PHYSICS_TICKS
		rows.append(row)
		fixture.free()
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	print("ASSET_CURRENT_OBSERVATIONS ", JSON.stringify({ "passed": passed, "rows": rows }))
	quit(0 if passed else 1)


## Returns the current completed-case count without assuming a concrete fixture script type.
func _outcome_count(fixture: Node, property_name: String) -> int:
	var value: Variant = fixture.get(property_name)
	return value.size() if value is Dictionary else 0
