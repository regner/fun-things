extends "res://scenes/prefabs/player_character/player_preview.gd"
## Bounded native measurement of saved frontage, mounting and static closed collision.

const MOTION_TICKS: int = 120
const SAMPLE_COUNT: int = 120
const QUERY_COUNT: int = 300
const STARTS: Array[Vector3] = [Vector3(1.95, 0, -10), Vector3(-2.9, 0, -10),
	Vector3(-.95, 0, -10), Vector3(4, 0, -10), Vector3(-4, 0, -8.5)]
const CASES: Array[String] = [
	"closed_leaf", "shell_wall", "display_pane", "side_clear", "canopy_under",
]

var samples: Array[Dictionary] = []
var outcomes: Dictionary = {}
var _phase: int = 0
var _ticks: int = 0

@onready var _actor: AssetScaleClearanceProbe = $ProbeActor
@onready var _aim: AssetLineOfSightProbe = $AimProbe


## Captures bounded renderer counters after warmup, without imposing a device budget.
func _process(_delta: float) -> void:
	if _ticks < 30 or samples.size() >= SAMPLE_COUNT:
		return

	samples.append({"process_s": Performance.get_monitor(Performance.TIME_PROCESS),
		"physics_s": Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS),
		"draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		"primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		"video_bytes": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)})


## Applies test-only probe commands to explicit blocking and unobstructed expectations.
func _physics_process(delta: float) -> void:
	if _phase >= STARTS.size():
		return

	var lateral: bool = _phase == 4
	_actor.step({"move": Vector2.RIGHT if lateral else Vector2.DOWN,
		"aim_yaw": PI / 2.0 if lateral else PI, "fire": false}, delta)
	_ticks += 1
	if _ticks < MOTION_TICKS:
		return

	var p: Vector3 = _actor.global_position
	var passed: bool = p.z < -6.9 and p.z > -7.0
	if _phase == 1:
		passed = p.z < -7.35 and p.z > -7.5
	elif _phase == 2:
		passed = p.z < -7.35 and p.z > -7.5
	elif _phase == 3:
		passed = absf(p.z) < .03
	elif lateral:
		passed = absf(p.x - 6.0) < .03

	outcomes[CASES[_phase]] = { "passed": passed, "position": [p.x, p.y, p.z] }
	_actor.neutralize()
	_phase += 1
	_ticks = 0
	if _phase < STARTS.size():
		_actor.global_position = STARTS[_phase]


## Records actual saved mesh envelopes and marker-derived fitting attachment identity.
func assembly_checks() -> Dictionary:  # gdstyle:ignore=quality/max-local-variables
	var root: Node3D = $Frontage
	var model: Node3D = root.get_node("Shell/Visuals/Model")
	var mounts: Dictionary = {"Entrance": "mount_entrance_single", "Door": "mount_door_single",
		"Window": "mount_display_window", "Canopy": "mount_canopy", "Fascia": "mount_fascia"}
	var rows: Dictionary = {}
	var passed: bool = true
	for name: String in mounts:
		var node: Node3D = root.get_node(name)
		var marker: Node3D = model.find_child(mounts[name], true, false)
		var error_m: float = node.global_position.distance_to(marker.global_position)
		passed = passed and error_m < .002 and node.scale.is_equal_approx(Vector3.ONE)
		rows[name] = {"marker_error_m": error_m, "bounds": _bounds(node),
			"prefab": node.scene_file_path, "model": node.get_node("Visuals/Model").scene_file_path}

	var window: Dictionary = rows.Window.bounds
	var canopy: Dictionary = rows.Canopy.bounds
	var fascia: Dictionary = rows.Fascia.bounds
	var window_gap: float = canopy.min[1] - window.max[1]
	var fascia_gap: float = fascia.min[1] - canopy.max[1]
	var blade: Dictionary = _bounds(root.get_node("Blade"))
	var headroom: float = blade.min[1] - 1.8
	var upper_fit: Dictionary = _upper_fit()
	passed = passed and window_gap >= .099 and fascia_gap >= .159
	passed = passed and headroom > 1.0 and upper_fit.passed
	return {"passed": passed, "mounts": rows, "window_canopy_gap_m": window_gap,
		"canopy_fascia_gap_m": fascia_gap, "blade_actor_headroom_m": headroom,
		"blade_bounds": blade, "upper_window_bounds": _bounds($UpperWindow),
		"upper_wall_model": $UpperWall.scene_file_path,
		"upper_fit": upper_fit,
		"scope": "marker-linked narrow shell; upper window in separate compatible technical wall"}


## Measures the actual technical opening and every imported window vertex behind the wall.
func _upper_fit() -> Dictionary:  # gdstyle:ignore=quality/max-local-variables
	var walls: Array[AABB] = []
	for mesh: MeshInstance3D in $UpperWall.find_children("*", "MeshInstance3D", true, false):
		walls.append(mesh.global_transform * mesh.get_aabb())

	assert(walls.size() == 4)
	var left: float = walls[0].end.x
	var right: float = walls[1].position.x
	var bottom: float = walls[2].end.y
	var top: float = walls[3].position.y
	var minimum_gap: float = INF
	var rear_m: float = -INF
	var vertices: int = 0
	for mesh: MeshInstance3D in $UpperWindow.find_children("*", "MeshInstance3D", true, false):
		for surface: int in range(mesh.mesh.get_surface_count()):
			var arrays: Array = mesh.mesh.surface_get_arrays(surface)
			var points: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			for point: Vector3 in points:
				var world: Vector3 = mesh.global_transform * point
				if world.z <= -7.0:
					continue

				vertices += 1
				minimum_gap = minf(minimum_gap, minf(world.x - left, right - world.x))
				minimum_gap = minf(minimum_gap, minf(world.y - bottom, top - world.y))
				rear_m = maxf(rear_m, world.z)

	var depth_clearance: float = walls[0].end.z - rear_m
	return {"passed": vertices > 0 and minimum_gap >= .018 and depth_clearance >= .02,
		"opening_world_xy": [left, right, bottom, top], "rear_vertices": vertices,
		"minimum_side_head_bottom_gap_m": minimum_gap, "rear_clearance_m": depth_clearance}


## Accumulates actual imported mesh bounds in the comparison world's coordinates.
func _bounds(node: Node3D) -> Dictionary:
	var result: AABB
	var first: bool = true
	for mesh: MeshInstance3D in node.find_children("*", "MeshInstance3D", true, false):
		var bounds: AABB = mesh.global_transform * mesh.get_aabb()
		result = bounds if first else result.merge(bounds)
		first = false

	assert(not first)
	var hi: Vector3 = result.end
	return {"min": [result.position.x, result.position.y, result.position.z],
		"max": [hi.x, hi.y, hi.z]}


## Exercises physical openings before/after static closed leaves and production firing queries.
func probe_queries() -> Dictionary:  # gdstyle:ignore=quality/max-local-variables
	var passed: bool = outcomes.size() == CASES.size()
	for value: Dictionary in outcomes.values():
		passed = passed and value.passed

	_actor.global_position = Vector3(1.95, 0, -9)
	_actor.step({ "move": Vector2.ZERO, "aim_yaw": PI, "fire": false }, 1.0 / 60.0)
	_aim.step(_actor, true, 1.0 / 60.0)
	var hit: String = str(_aim.last_hit.get_path()) if _aim.last_hit != null else ""
	passed = passed and hit.ends_with("Frontage/Door/Collision/Body")
	var query := PhysicsRayQueryParameters3D.create(Vector3(1.95, 1.2, -9),
		Vector3(1.95, 1.2, -5.9), 1, [$Frontage/Door/Collision/Body.get_rid()])
	var open_entrance: bool = get_world_3d().direct_space_state.intersect_ray(query).is_empty()
	query.from = Vector3(-.95, 1.2, -9)
	query.to = Vector3(-.95, 1.2, -5.9)
	query.exclude = [$Frontage/Window/Collision/Body.get_rid()]
	var open_window: bool = get_world_3d().direct_space_state.intersect_ray(query).is_empty()
	passed = passed and open_entrance and open_window
	var started: int = Time.get_ticks_usec()
	for index: int in range(QUERY_COUNT):
		get_world_3d().direct_space_state.intersect_ray(query)

	return {"passed": passed, "motion": outcomes, "aim_hit": hit,
		"entrance_structure_void": open_entrance, "display_structure_void": open_window,
		"query_iterations": QUERY_COUNT, "query_usec": Time.get_ticks_usec() - started,
		"samples": samples, "scope": "static closed decoration, no opening mechanics or transport"}
