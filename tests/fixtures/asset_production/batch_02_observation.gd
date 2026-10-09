extends "res://scenes/prefabs/player_character/player_preview.gd"
## Bounded native and separate-process observation of saved batch-two props.

const OBSERVATION_FRAMES: int = 120
const MOTION_TICKS: int = 120
const QUERY_ITERATIONS: int = 300
const MOTION_STARTS: Array[Vector3] = [
	Vector3(-4, 0, 6), Vector3(4, 0, 6), Vector3(-2.5, 0, 6), Vector3(-2, 0, -5.8),
]
const MOTION_NAMES: Array[String] = [
	"compact_surround", "broad_surround", "clear_bypass", "canopy_under",
]

var frame_samples: Array[Dictionary] = []
var motion_outcomes: Dictionary = {}
var _phase: int = 0
var _ticks: int = 0

@onready var _actor: S02ActorMotion = $ProbeActor
@onready var _aim: S02AimProbe = $AimProbe


## Records named desktop counters, excluding the first thirty warmup frames.
func _process(_delta: float) -> void:
	if _ticks < 30 or frame_samples.size() >= OBSERVATION_FRAMES:
		return

	frame_samples.append({"process_s": Performance.get_monitor(Performance.TIME_PROCESS),
		"physics_s": Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS),
		"draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		"primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		"video_bytes": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)})


## Exercises trunk stops and clear routes with the existing public motion owner.
func _physics_process(delta: float) -> void:
	if _phase >= MOTION_STARTS.size():
		return

	var under: bool = _phase == 3
	_actor.step({"move": Vector2.RIGHT if under else Vector2.UP,
		"aim_yaw": PI / 2.0 if under else 0.0, "fire": false}, delta)
	_ticks += 1
	if _ticks < MOTION_TICKS:
		return

	var position_now: Vector3 = _actor.global_position
	var passed: bool = position_now.z < -3.5
	if _phase < 2:
		passed = position_now.z >= 3.25 and position_now.z < 3.45
	if under:
		passed = position_now.x > 7.5

	motion_outcomes[MOTION_NAMES[_phase]] = {"passed": passed,
		"position": [position_now.x, position_now.y, position_now.z], "yaw": _actor.rotation.y}
	_actor.neutralize()
	_phase += 1
	_ticks = 0
	if _phase < MOTION_STARTS.size():
		_actor.global_position = MOTION_STARTS[_phase]


## Compares independent physical expectations, firing query and declared mounting margins.
func probe_queries() -> Dictionary:  # gdstyle:ignore=quality/max-local-variables
	var shape: CapsuleShape3D = ($ProbeActor/Collision as CollisionShape3D).shape
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.collision_mask = 1
	var points: Dictionary = {
		"compact_trunk": Vector3(-4, .9, 2), "broad_trunk": Vector3(4, .9, 2),
		"crown_not_solid": Vector3(-4, 2.7, 2), "shrub_not_solid": Vector3(-7, .9, 0),
		"tuft_not_solid": Vector3(-6, .9, 5), "clump_not_solid": Vector3(6, .9, 5),
		"roof_gear_not_solid": Vector3(3, 11.1, -12),
		"canopy_under_clear": Vector3(0, .9, -5.8),
	}
	var outcomes: Dictionary = {}
	var passed: bool = motion_outcomes.size() == MOTION_STARTS.size()
	for label: String in points:
		query.transform = Transform3D(Basis.IDENTITY, points[label])
		var hit: bool = not get_world_3d().direct_space_state.intersect_shape(query, 1).is_empty()
		var expected: bool = label in ["compact_trunk", "broad_trunk"]
		outcomes[label] = { "hit": hit, "expected": expected }
		passed = passed and hit == expected

	for value: Dictionary in motion_outcomes.values():
		passed = passed and value.passed

	_actor.global_position = Vector3(3.57, 0, 4)
	_actor.step({ "move": Vector2.ZERO, "aim_yaw": 0.0, "fire": false }, 1.0 / 60.0)
	_aim.step(_actor, true, 1.0 / 60.0)
	var aim_path: String = str(_aim.last_hit.get_path()) if _aim.last_hit != null else ""
	passed = passed and aim_path.ends_with("BroadTree/Collision/PoleBody")
	query.transform = Transform3D(Basis.IDENTITY, Vector3(0, .9, -5.8))
	var start_usec: int = Time.get_ticks_usec()
	for index: int in range(QUERY_ITERATIONS):
		get_world_3d().direct_space_state.intersect_shape(query, 1)

	return {"passed": passed, "overlaps": outcomes, "motion": motion_outcomes,
		"aim_hit": aim_path, "query_iterations": QUERY_ITERATIONS,
		"query_batch_usec": Time.get_ticks_usec() - start_usec,
		"frame_samples": frame_samples, "canopy_lowest_y_m": 2.58,
		"actor_height_m": shape.height, "roof_plane_y_m": 10.0,
		"required_roof_edge_margin_m": .5, "scope": "saved fixture / public S02 motion and aim"}


## Measures saved mounting transforms against imported roof and wall geometry.
func placement_receipt() -> Dictionary:
	var shop_bounds: AABB = _global_bounds($Shop)
	var roof_rows: Dictionary = {}
	var passed: bool = true
	for label: String in ["RoofVent", "RoofEnclosure"]:
		var bounds: AABB = _global_bounds(get_node(label))
		var margin: float = minf(
			minf(bounds.position.x - shop_bounds.position.x, shop_bounds.end.x - bounds.end.x),
			minf(bounds.position.z - shop_bounds.position.z, shop_bounds.end.z - bounds.end.z)
		)
		var plane_error: float = absf(bounds.position.y - shop_bounds.end.y)
		roof_rows[label] = { "edge_margin_m": margin, "roof_plane_error_m": plane_error }
		passed = passed and margin >= .5 and plane_error <= .002

	var canopy: AABB = _global_bounds($Canopy)
	var wall_error: float = absf($Canopy.global_position.z - shop_bounds.end.z)
	var height: float = ($ProbeActor/Collision.shape as CapsuleShape3D).height
	passed = passed and canopy.position.y >= 2.58 - .001 and wall_error <= .002
	return {"passed": passed, "roof": roof_rows, "roof_top_y_m": shop_bounds.end.y,
		"canopy_lowest_y_m": canopy.position.y, "canopy_wall_datum_error_m": wall_error,
		"canopy_actor_headroom_m": canopy.position.y - height,
		"tree_surround_ground_datum_error_m": maxf(
			absf($CompactTree.position.y - $CompactSurround.position.y),
			absf($BroadTree.position.y - $BroadSurround.position.y))}


## Aggregates transformed bounds of existing imported meshes without changing placement.
func _global_bounds(node: Node3D) -> AABB:
	var result: AABB
	var first: bool = true
	for mesh: MeshInstance3D in node.find_children("*", "MeshInstance3D", true, false):
		var bounds: AABB = mesh.global_transform * mesh.get_aabb()
		result = bounds if first else result.merge(bounds)
		first = false

	assert(not first)
	return result
