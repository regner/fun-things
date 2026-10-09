extends Node3D
## Runs capped real-time host sections for 64 pedestrians and four available actors.

const TRACKING_ACTOR_SCENE: PackedScene = preload(
	"res://tests/performance/host_budget/tracking_actor.tscn"
)
const FRAME_CAP: int = 60
const PEDESTRIAN_COUNT: int = 64
const PLAYER_COUNT: int = 4
const DEFAULT_WARMUP_TICKS: int = 600
const DEFAULT_MEASURED_TICKS: int = 3600
const SOFT_TOTAL_P95_MS: float = 4.0

var _navigation: SyntheticHostNavigation
var _reservations: CrossingReservations
var _pedestrian_core: PedestrianCore
var _pedestrian_agent_ids: PackedInt64Array = PackedInt64Array()
var _pedestrian_actors: Array[ActorMotion] = []
var _player_actors: Array[ActorMotion] = []
var _profiler: HostTickProfiler
var _coordinator: HostTickCoordinator
var _warmup_ticks: int = DEFAULT_WARMUP_TICKS
var _measured_ticks: int = DEFAULT_MEASURED_TICKS
var _completed_ticks: int = 0
var _output_path: String = ""
var _tree: SceneTree


## Applies the cap before creating actors and begins the bounded physics run.
func _ready() -> void:
	_tree = get_tree()
	Engine.max_fps = FRAME_CAP
	Engine.physics_ticks_per_second = FRAME_CAP
	_output_path = OS.get_environment("HOST_BUDGET_OUTPUT")
	_warmup_ticks = _positive_environment_int("HOST_BUDGET_WARMUP_TICKS", DEFAULT_WARMUP_TICKS)
	_measured_ticks = _positive_environment_int(
		"HOST_BUDGET_MEASURED_TICKS", DEFAULT_MEASURED_TICKS
	)
	if _output_path.is_empty():
		_fail("HOST_BUDGET_OUTPUT_REQUIRED")
		return
	if not _configure_simulation():
		_fail("HOST_BUDGET_CONFIGURATION_FAILED")


## Advances one real 60 Hz owner tick and writes the report at the exact bound.
func _physics_process(_delta: float) -> void:
	if _completed_ticks == _warmup_ticks:
		_profiler.clear()
		_profiler.set_enabled(true)

	var host_tick: int = _completed_ticks
	var fixed_delta: float = 1.0 / float(Engine.physics_ticks_per_second)
	var player_commands: Array[FootCommand] = _player_commands(host_tick)
	if not _coordinator.step(host_tick, fixed_delta, player_commands):
		set_physics_process(false)
		# Coordinator access is a bound RefCounted dependency, not a node lookup.
		# gdstyle:ignore=quality/process-get-node
		var failure_message: String = "HOST_BUDGET_TICK_FAILED tick=%d reason=%s" % [
			host_tick,
			_coordinator.last_failure(),
		]
		# The helper owns the cached tree; this call performs no node lookup.
		# gdstyle:ignore=quality/process-get-node
		Callable(_fail).call_deferred(failure_message)
		return

	_completed_ticks += 1
	if _completed_ticks >= _warmup_ticks + _measured_ticks:
		_profiler.set_enabled(false)
		_write_report()
		_tree.quit()


## Configures production owners and saved tracking actors before measurement.
func _configure_simulation() -> bool:  # gdstyle:ignore=quality/max-returns
	_navigation = SyntheticHostNavigation.new()
	_reservations = CrossingReservations.new()
	if not _reservations.configure(_navigation):
		return false
	_pedestrian_core = PedestrianCore.new()
	if not _pedestrian_core.configure(_navigation, _reservations):
		return false

	for slot: int in PEDESTRIAN_COUNT:
		var agent_id: int = slot + 1
		var start: Vector2 = _navigation.node_position(slot)
		var actor: ActorMotion = _add_tracking_actor(Vector3(start.x, 0.0, start.y))
		if actor == null or not _pedestrian_core.add_agent(agent_id, slot, start):
			return false
		_pedestrian_agent_ids.append(agent_id)
		_pedestrian_actors.append(actor)
	for slot: int in PLAYER_COUNT:
		var player: ActorMotion = _add_tracking_actor(Vector3(60.0, 0.0, slot * 3.0))
		if player == null:
			return false
		_player_actors.append(player)

	_profiler = HostTickProfiler.new()
	if not _profiler.configure(_measured_ticks):
		return false
	_coordinator = HostTickCoordinator.new()
	if not _coordinator.configure(_profiler):
		return false
	if not _coordinator.bind_pedestrians(
		_pedestrian_core, _pedestrian_agent_ids, _pedestrian_actors
	):
		return false
	return _coordinator.bind_players(_player_actors)


## Instantiates one saved CharacterBody fixture without composing nodes in code.
func _add_tracking_actor(position: Vector3) -> ActorMotion:
	var actor: ActorMotion = TRACKING_ACTOR_SCENE.instantiate() as ActorMotion
	if actor == null:
		return null
	actor.position = position
	add_child(actor)
	return actor


## Builds four deterministic player intents outside the measured simulation bracket.
func _player_commands(host_tick: int) -> Array[FootCommand]:
	var commands: Array[FootCommand] = []
	for slot: int in PLAYER_COUNT:
		var angle: float = (host_tick + slot * 15) * 0.01
		commands.append(
			# Commands are immutable per tick; allocation is outside the measured bracket.
			FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
				host_tick + 1,
				host_tick,
				Vector2(cos(angle), sin(angle)) * 0.5,
				wrapf(angle, -PI, PI),
				false,
				false,
			)
		)
	return commands


## Writes one small self-describing JSON report outside the checkout.
func _write_report() -> void:
	var timing: Dictionary = _profiler.summary()
	var total_p95_ms: float = timing.total.p95_ms
	var report: Dictionary = {
		"ok": true,
		"engine": Engine.get_version_info().string,
		"display_server": DisplayServer.get_name(),
		"renderer": RenderingServer.get_current_rendering_method(),
		"video_adapter": RenderingServer.get_video_adapter_name(),
		"frame_cap": FRAME_CAP,
		"physics_ticks_per_second": Engine.physics_ticks_per_second,
		"warmup_ticks": _warmup_ticks,
		"measured_ticks": _measured_ticks,
		"population": {
			"pedestrians": _pedestrian_actors.size(),
			"players": _player_actors.size(),
		},
		"timing_ms": timing,
		"soft_target": {
			"total_p95_ms": SOFT_TOTAL_P95_MS,
			"observed_total_p95_ms": total_p95_ms,
			"status": "within" if total_p95_ms <= SOFT_TOTAL_P95_MS else "above",
			"report_only": true,
		},
		"sections": {
			"pedestrian_decisions": "PedestrianCore.step decisions and command emission",
			"actor_motion": "ActorMotion.step plus pedestrian pose handoff",
		},
	}
	var file: FileAccess = FileAccess.open(_output_path, FileAccess.WRITE)
	if file == null:
		_fail("HOST_BUDGET_OUTPUT_OPEN_FAILED path=%s" % _output_path)
		return
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()


## Reads one positive integer override while retaining a bounded default on invalid input.
func _positive_environment_int(name: String, default_value: int) -> int:
	var text: String = OS.get_environment(name)
	if text.is_valid_int() and text.to_int() > 0:
		return text.to_int()
	return default_value


## Prints one stable failure marker and exits nonzero without hanging.
func _fail(message: String) -> void:
	print(message)
	set_physics_process(false)
	_tree.quit(2)
