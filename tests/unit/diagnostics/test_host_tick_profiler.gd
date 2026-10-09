extends GutTest
## Verifies disabled overhead, bounded retention, and nearest-rank host-tick reports.

var _clock_values: PackedInt64Array = PackedInt64Array()
var _clock_index: int = 0


## Resets the deterministic microsecond clock before every timing contract test.
func before_each() -> void:
	_clock_values.clear()
	_clock_index = 0


## Proves disabled brackets retain no samples and never read the monotonic timer.
func test_disabled_brackets_do_not_read_clock() -> void:
	var profiler := HostTickProfiler.new()
	assert_true(profiler.configure(4, Callable(self, "_next_clock_usec")))
	assert_true(profiler.register_section(&"simulation"))
	assert_false(profiler.begin_tick())
	assert_false(profiler.begin_section(&"simulation"))
	assert_false(profiler.end_section(&"simulation"))
	assert_false(profiler.end_tick())
	assert_eq(profiler.timer_read_count(), 0)
	assert_eq(profiler.summary().sample_count, 0)


## Reports exact nearest-rank values for deterministic total and section brackets.
func test_summary_reports_total_and_registered_sections() -> void:
	var profiler := HostTickProfiler.new()
	assert_true(profiler.configure(5, Callable(self, "_next_clock_usec")))
	assert_true(profiler.register_section(&"simulation"))
	profiler.set_enabled(true)
	for tick: int in 5:
		var base: int = tick * 1000
		_clock_values.append_array([base, base + 10, base + 110 + tick * 10, base + 500])
		assert_true(profiler.begin_tick())
		assert_true(profiler.begin_section(&"simulation"))
		assert_true(profiler.end_section(&"simulation"))
		assert_true(profiler.end_tick())

	var report: Dictionary = profiler.summary()
	assert_eq(report.sample_count, 5)
	assert_eq(report.timer_read_count, 20)
	assert_eq(report.total.median_ms, 0.5)
	assert_eq(report.total.p95_ms, 0.5)
	assert_eq(report.total.p99_ms, 0.5)
	assert_eq(report.sections.simulation.median_ms, 0.12)
	assert_eq(report.sections.simulation.p95_ms, 0.14)
	assert_eq(report.sections.simulation.p99_ms, 0.14)


## Retains only the newest fixed-capacity samples without growing the report.
func test_sample_history_is_a_fixed_capacity_ring() -> void:
	var profiler := HostTickProfiler.new()
	assert_true(profiler.configure(2, Callable(self, "_next_clock_usec")))
	profiler.set_enabled(true)
	_clock_values.append_array([0, 100, 1000, 1200, 2000, 2300])
	for _tick: int in 3:
		assert_true(profiler.begin_tick())
		assert_true(profiler.end_tick())

	var report: Dictionary = profiler.summary()
	assert_eq(report.sample_count, 2)
	assert_eq(report.total.median_ms, 0.2)
	assert_eq(report.total.p95_ms, 0.3)


## Supplies deterministic timer values and fails loudly on an unexpected read.
func _next_clock_usec() -> int:
	assert_lt(_clock_index, _clock_values.size())
	var value: int = _clock_values[_clock_index]
	_clock_index += 1
	return value
