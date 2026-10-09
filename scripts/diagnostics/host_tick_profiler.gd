class_name HostTickProfiler
extends RefCounted
## Records bounded inclusive host-tick and named subsystem timings when explicitly enabled.

const TOTAL_SECTION: StringName = &"total"
const DEFAULT_SAMPLE_CAPACITY: int = 36_000

var _enabled: bool = false
var _sample_capacity: int = DEFAULT_SAMPLE_CAPACITY
var _samples: Dictionary[StringName, PackedInt64Array] = {}
var _current_sections: Dictionary[StringName, int] = {}
var _sample_count: int = 0
var _write_index: int = 0
var _tick_started_usec: int = 0
var _section_started_usec: int = 0
var _tick_active: bool = false
var _section_active: bool = false
var _active_section: StringName = &""
var _clock: Callable
var _timer_read_count: int = 0


## Sets the bounded history and optional deterministic clock before registering sections.
func configure(
	sample_capacity: int = DEFAULT_SAMPLE_CAPACITY,
	clock: Callable = Callable(),
) -> bool:
	if sample_capacity <= 0:
		return false
	if not clock.is_null() and not clock.is_valid():
		return false

	_sample_capacity = sample_capacity
	_clock = clock
	_samples.clear()
	_samples[TOTAL_SECTION] = PackedInt64Array()
	clear()
	return true


## Registers one stable subsystem name before samples are collected.
func register_section(section: StringName) -> bool:
	if section == &"" or section == TOTAL_SECTION or _samples.has(section):
		return false
	if _sample_count > 0 or _tick_active:
		return false

	_samples[section] = PackedInt64Array()
	return true


## Enables or disables timer reads without changing the retained report.
func set_enabled(enabled: bool) -> void:
	_enabled = enabled
	if not enabled:
		_tick_started_usec = 0
		_section_started_usec = 0
		_tick_active = false
		_section_active = false
		_active_section = &""
		_current_sections.clear()


## Reports whether the coordinator should enter timing brackets this tick.
func is_enabled() -> bool:
	return _enabled


## Starts one inclusive host tick; disabled calls return before reading the clock.
func begin_tick() -> bool:
	if not _enabled:
		return false
	if _tick_active:
		return false

	_current_sections.clear()
	_tick_started_usec = _now_usec()
	_tick_active = true
	return true


## Starts one registered subsystem bracket inside the active host tick.
func begin_section(section: StringName) -> bool:
	if not _enabled:
		return false
	if not _tick_active or _section_active or not _samples.has(section):
		return false
	if section == TOTAL_SECTION:
		return false

	_active_section = section
	_section_started_usec = _now_usec()
	_section_active = true
	return true


## Closes the current matching section and accumulates repeated brackets in one tick.
func end_section(section: StringName) -> bool:
	if not _enabled:
		return false
	if not _section_active or section != _active_section:
		return false

	var elapsed_usec: int = maxi(0, _now_usec() - _section_started_usec)
	_current_sections[section] = _current_sections.get(section, 0) + elapsed_usec
	_active_section = &""
	_section_started_usec = 0
	_section_active = false
	return true


## Closes and stores one complete tick after all sections have ended.
func end_tick() -> bool:
	if not _enabled:
		return false
	if not _tick_active or _section_active:
		return false

	var total_usec: int = maxi(0, _now_usec() - _tick_started_usec)
	_tick_started_usec = 0
	_tick_active = false
	_store_tick(total_usec)
	return true


## Removes retained samples and in-progress brackets while preserving registered names.
func clear() -> void:
	for section: StringName in _samples:
		_samples[section] = PackedInt64Array()
	_current_sections.clear()
	_sample_count = 0
	_write_index = 0
	_tick_started_usec = 0
	_section_started_usec = 0
	_tick_active = false
	_section_active = false
	_active_section = &""
	_timer_read_count = 0


## Returns nearest-rank median/p95/p99 reports without changing retained samples.
func summary() -> Dictionary:
	var sections: Dictionary[StringName, Dictionary] = {}
	for section: StringName in _samples:
		if section == TOTAL_SECTION:
			continue
		sections[section] = _series_summary(_samples[section])
	return {
		"sample_count": _sample_count,
		"sample_capacity": _sample_capacity,
		"timer_read_count": _timer_read_count,
		"total": _series_summary(_samples.get(TOTAL_SECTION, PackedInt64Array())),
		"sections": sections,
	}


## Exposes timer-read receipts so disabled-overhead tests need no wall-clock assumptions.
func timer_read_count() -> int:
	return _timer_read_count


## Stores current values in a fixed-capacity ring outside the measured total bracket.
func _store_tick(total_usec: int) -> void:
	for section: StringName in _samples:
		var value_usec: int = total_usec if section == TOTAL_SECTION else (
			_current_sections.get(section, 0)
		)
		var series: PackedInt64Array = _samples[section]
		if _sample_count < _sample_capacity:
			series.append(value_usec)
		else:
			series[_write_index] = value_usec
		_samples[section] = series

	if _sample_count < _sample_capacity:
		_sample_count += 1
	else:
		_write_index = (_write_index + 1) % _sample_capacity


## Summarizes one microsecond series with the S17 nearest-rank percentile rule.
func _series_summary(values: PackedInt64Array) -> Dictionary:
	if values.is_empty():
		return { "count": 0, "median_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0 }

	var sorted_values: PackedInt64Array = values.duplicate()
	sorted_values.sort()
	return {
		"count": sorted_values.size(),
		"median_ms": _nearest_rank_usec(sorted_values, 0.50) / 1000.0,
		"p95_ms": _nearest_rank_usec(sorted_values, 0.95) / 1000.0,
		"p99_ms": _nearest_rank_usec(sorted_values, 0.99) / 1000.0,
	}


## Selects one nearest-rank value from an already sorted nonempty series.
func _nearest_rank_usec(sorted_values: PackedInt64Array, percentile: float) -> int:
	var rank: int = ceili(sorted_values.size() * percentile) - 1
	var index: int = clampi(rank, 0, sorted_values.size() - 1)
	return sorted_values[index]


## Reads the monotonic engine clock or an injected deterministic test clock.
func _now_usec() -> int:
	_timer_read_count += 1
	if not _clock.is_null():
		return int(_clock.call())
	return Time.get_ticks_usec()
