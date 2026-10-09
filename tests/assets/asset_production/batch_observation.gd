extends "res://scenes/prefabs/player_character/player_preview.gd"
## Saved batch observation using real imported prefabs and public physics APIs.

const QUERY_MASK: int = 1
const QUERY_ITERATIONS: int = 300
const OBSERVATION_FRAMES: int = 120
const MOTION_TICKS_PER_CASE: int = 120

var frame_samples: Array[Dictionary] = []
var _motion_phase: int = 0
var _motion_ticks: int = 0
var motion_outcomes: Dictionary = {}

@onready var _actor: AssetScaleClearanceProbe = $ProbeActor


## Records desktop render/query observation without deciding any gameplay outcome.
func _process(_delta: float) -> void:
	if frame_samples.size() >= OBSERVATION_FRAMES:
		return

	frame_samples.append({"frame_s": Performance.get_monitor(Performance.TIME_PROCESS),
		"physics_s": Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS),
		"draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		"primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		"video_bytes": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)})


## Runs actual bounded standalone movement against the saved planter and clear bypass.
func _physics_process(delta: float) -> void:
	if _motion_phase > 1:
		return

	var actor: AssetScaleClearanceProbe = _actor
	actor.step({ "move": Vector2(0, -1), "aim_yaw": 0.0, "fire": false }, delta)
	_motion_ticks += 1
	if _motion_ticks < MOTION_TICKS_PER_CASE:
		return

	if _motion_phase == 0:
		motion_outcomes["planter_stop_z_m"] = actor.global_position.z
		motion_outcomes["planter_stopped"] = actor.global_position.z >= 3.80
		actor.neutralize()
		actor.global_position = Vector3(3, 0, 6)
	else:
		motion_outcomes["bypass_end_z_m"] = actor.global_position.z
		motion_outcomes["bypass_crossed"] = actor.global_position.z < -3.5
		actor.neutralize()

	_motion_ticks = 0
	_motion_phase += 1


## Tests solid envelopes, ring opening and wall clearance against independent expectations.
func probe_queries() -> Dictionary:  # gdstyle:ignore=quality/max-local-variables
	var actor: AssetScaleClearanceProbe = _actor
	var shape: CapsuleShape3D = ($ProbeActor/Collision as CollisionShape3D).shape
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.collision_mask = QUERY_MASK
	query.collide_with_areas = false
	var points: Dictionary = {
		"street_pole_solid": Vector3(-2, 0.9, 0),
		"pedestrian_pole_solid": Vector3(2, 0.9, 0),
		"rectangular_planter_solid": Vector3(0, 0.9, 3),
		"round_ring_solid": Vector3(-3.22, 0.9, 3),
		"round_centre_clear": Vector3(-4, 0.9, 3),
		"rectangular_walkway_clear": Vector3(0, 0.9, 4.0),
		"below_wall_lamp_clear": Vector3(-2, 0.9, -5.2),
	}
	var expected: Dictionary = {
		"street_pole_solid": true, "pedestrian_pole_solid": true,
		"rectangular_planter_solid": true, "round_ring_solid": true,
		"round_centre_clear": false, "rectangular_walkway_clear": false,
		"below_wall_lamp_clear": false,
	}
	var outcomes: Dictionary = {}
	var passed: bool = true
	for label: String in points:
		query.transform = Transform3D(Basis.IDENTITY, points[label])
		var hit: bool = not get_world_3d().direct_space_state.intersect_shape(query, 1).is_empty()
		outcomes[label] = { "hit": hit, "expected": expected[label] }
		passed = passed and hit == expected[label]

	var target: Transform3D = Transform3D(Basis.IDENTITY, Vector3(0, 0, 6))
	var blocked: bool = actor.test_move(target, Vector3(0, 0, -4))
	var bypass: bool = actor.test_move(
		Transform3D(Basis.IDENTITY, Vector3(3, 0, 6)), Vector3(0, 0, -4)
	)
	passed = passed and blocked and not bypass
	passed = passed and motion_outcomes.get("planter_stopped", false)
	passed = passed and motion_outcomes.get("bypass_crossed", false)
	var started_usec: int = Time.get_ticks_usec()
	for index: int in range(QUERY_ITERATIONS):
		query.transform = Transform3D(Basis.IDENTITY, Vector3(0, 0.9, 4.0))
		get_world_3d().direct_space_state.intersect_shape(query, 1)

	return {"passed": passed, "outcomes": outcomes, "test_move_blocked": blocked,
		"test_move_bypass_blocked": bypass, "actor_radius_m": shape.radius,
		"actor_height_m": shape.height, "queries": QUERY_ITERATIONS,
		"query_batch_usec": Time.get_ticks_usec() - started_usec,
		"render_samples": frame_samples, "motion_outcomes": motion_outcomes,
		"scope": "test-only accepted foot envelope/public physics APIs"}
