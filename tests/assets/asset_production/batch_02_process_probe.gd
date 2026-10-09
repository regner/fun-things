extends SceneTree
## Replays identical bounded commands in separately isolated physics processes.

const STEP_SECONDS: float = 1.0 / 60.0
const TICKS_PER_CASE: int = 120
const STARTS: Array[Vector3] = [Vector3(-4, 0, 6), Vector3(4, 0, 6), Vector3(0, 0, 6)]


## Defers loaded fixture setup until the tree accepts authored scene children.
func _initialize() -> void:
	_run.call_deferred()


## Measures real trunk blocking, clear movement and public aiming without network claims.
func _run() -> void:  # gdstyle:ignore=quality/max-local-variables
	var packed: PackedScene = load("res://tests/assets/asset_production/batch_02_trunks.tscn")
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var actor: AssetScaleClearanceProbe = fixture.get_node("ProbeActor")
	var aim: AssetLineOfSightProbe = fixture.get_node("AimProbe")
	var rows: Array[Dictionary] = []
	var passed: bool = true
	for index: int in range(STARTS.size()):
		var position_now: Vector3 = await _travel(  # gdstyle:ignore=quality/await-in-loop
			actor, STARTS[index]
		)
		var correct: bool = position_now.z > 2.58 and position_now.z < 2.75
		if index == 2:
			correct = absf(position_now.z + 4.0) < .03

		passed = passed and correct
		rows.append({"case": index, "passed": correct,
			"position": [position_now.x, position_now.y, position_now.z]})

	actor.global_position = Vector3(3.57, 0, 4)
	actor.step({ "move": Vector2.ZERO, "aim_yaw": 0.0, "fire": false }, STEP_SECONDS)
	aim.step(actor, true, STEP_SECONDS)
	var hit_path: String = str(aim.last_hit.get_path()) if aim.last_hit != null else ""
	passed = passed and hit_path.ends_with("BroadTree/Collision/PoleBody")
	print("BATCH02_PROCESS ", JSON.stringify({"passed": passed, "pid": OS.get_process_id(),
		"engine": Engine.get_version_info().string, "rows": rows, "aim_hit": hit_path,
		"scope": "independent command replay in two physics processes; no transport protocol"}))
	fixture.queue_free()
	await process_frame
	quit(0 if passed else 1)


## Advances fixed commands through the same motion owner and live physics world.
func _travel(actor: AssetScaleClearanceProbe, start: Vector3) -> Vector3:
	actor.neutralize()
	actor.global_position = start
	await physics_frame
	for tick: int in range(TICKS_PER_CASE):
		actor.step({ "move": Vector2.UP, "aim_yaw": 0.0, "fire": false }, STEP_SECONDS)
		await physics_frame  # gdstyle:ignore=quality/await-in-loop

	actor.neutralize()
	return actor.global_position
