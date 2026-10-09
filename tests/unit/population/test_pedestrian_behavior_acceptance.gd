extends GutTest
## Applies recorded S10-compatible thresholds to seeded 64-agent production-core runs.

const SEEDS: Array[int] = [101, 202, 303]
const MAX_SAMPLED_OVERLAP_PAIRS: int = 24
const MAX_CONTINUOUS_OVERLAP_TICKS: int = 3 * 60
const MAX_STUCK_IDENTITIES: int = 26
const MAX_CROSSING_WAIT_TICKS: int = 6 * 60
const MAX_CROSSING_QUEUE: int = 16
const MAX_RESERVATION_OVERLAP_TICKS: int = 5 * 60
const MAX_FLEE_REACTION_TICKS: int = PedestrianCore.DECISION_INTERVAL_TICKS - 1


## Passes normal and flee runs for three deterministic 64-agent seeds.
func test_seeded_normal_and_flee_behavior_thresholds() -> void:
	var behavior_case: PedestrianBehaviorCase = PedestrianBehaviorCase.new()
	var results: Array[Dictionary] = []
	for storm: bool in [false, true]:
		for seed: int in SEEDS:
			var result: Dictionary = behavior_case.run(seed, storm)
			results.append(result)
			_assert_thresholds(result)

	gut.p("C3_BEHAVIOR_RESULTS %s" % JSON.stringify(results))


## Checks the recorded overlap, stuck, crossing, and reaction thresholds.
func _assert_thresholds(result: Dictionary) -> void:
	var label: String = "%s seed %d" % [result.get("scenario", "unknown"), result.seed]
	assert_true(result.ok, "%s completed every expected reaction" % label)
	assert_lte(
		result.max_sampled_overlap_pairs,
		MAX_SAMPLED_OVERLAP_PAIRS,
		"%s sampled overlap pairs" % label,
	)
	assert_lte(
		result.max_continuous_overlap_ticks,
		MAX_CONTINUOUS_OVERLAP_TICKS,
		"%s continuous overlap duration" % label,
	)
	assert_lte(
		result.stuck_identities,
		MAX_STUCK_IDENTITIES,
		"%s identities below 0.25 m per four seconds" % label,
	)
	assert_lte(
		result.max_crossing_wait_ticks,
		MAX_CROSSING_WAIT_TICKS,
		"%s crossing queue age" % label,
	)
	assert_lte(
		result.max_crossing_queue,
		MAX_CROSSING_QUEUE,
		"%s crossing queue length" % label,
	)
	assert_lte(
		result.max_reservation_overlap_ticks,
		MAX_RESERVATION_OVERLAP_TICKS,
		"%s active reservation duration" % label,
	)
	assert_lte(
		result.max_flee_reaction_ticks,
		MAX_FLEE_REACTION_TICKS,
		"%s flee reaction latency" % label,
	)
