class_name S04DriveTuning
extends Resource
## Editable standalone-drive values whose defaults match the accepted S04 rule constants.

const PROPERTY_NAMES: Array[StringName] = [
	&"acceleration_mps2",
	&"brake_mps2",
	&"coast_mps2",
	&"max_forward_mps",
	&"max_reverse_mps",
	&"grip_per_second",
	&"slide_grip_per_second",
	&"turn_rad_per_second",
	&"full_steer_speed_mps",
	&"handbrake_mps2",
]
const DISPLAY_NAMES: Array[String] = [
	"Acceleration (m/s²)",
	"Brake (m/s²)",
	"Coast (m/s²)",
	"Max forward (m/s)",
	"Max reverse (m/s)",
	"Grip (/s)",
	"Handbrake side grip (/s)",
	"Turn rate (rad/s)",
	"Full-steer speed (m/s)",
	"Handbrake brake (m/s²)",
]
const INCREMENTS: Array[float] = [
	0.5, 0.5, 0.25, 0.5, 0.5, 0.25, 0.25, 0.05, 0.25, 0.5,
]
const MINIMUMS: Array[float] = [
	1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.1, 0.5, 0.0,
]
const MAXIMUMS: Array[float] = [
	40.0, 40.0, 20.0, 40.0, 20.0, 20.0, 20.0, 4.0, 20.0, 40.0,
]

@export_range(1.0, 40.0, 0.5) var acceleration_mps2: float = 12.0
@export_range(1.0, 40.0, 0.5) var brake_mps2: float = 18.0
@export_range(0.0, 20.0, 0.25) var coast_mps2: float = 4.0
@export_range(1.0, 40.0, 0.5) var max_forward_mps: float = 20.0
@export_range(1.0, 20.0, 0.5) var max_reverse_mps: float = 6.0
@export_range(0.0, 20.0, 0.25) var grip_per_second: float = 6.0
@export_range(0.0, 20.0, 0.25) var slide_grip_per_second: float = 1.0
@export_range(0.1, 4.0, 0.05) var turn_rad_per_second: float = 1.5
@export_range(0.5, 20.0, 0.25) var full_steer_speed_mps: float = 4.0
@export_range(0.0, 40.0, 0.5) var handbrake_mps2: float = 10.0


## Returns the number of selectable tuning values.
func value_count() -> int:
	return PROPERTY_NAMES.size()


## Returns the panel label for one selectable value.
func display_name(index: int) -> String:
	return DISPLAY_NAMES[index]


## Reads one selectable value by its stable resource property.
func value(index: int) -> float:
	return float(get(PROPERTY_NAMES[index]))


## Adjusts one value by its documented increment while preserving useful bounds.
func adjust(index: int, direction: float) -> void:
	var next: float = value(index) + INCREMENTS[index] * direction
	set(PROPERTY_NAMES[index], clampf(next, MINIMUMS[index], MAXIMUMS[index]))


## Provides stable names and current numbers for stdout and owner feedback.
func as_dictionary() -> Dictionary:
	var values: Dictionary = {}
	for index: int in PROPERTY_NAMES.size():
		values[String(PROPERTY_NAMES[index])] = value(index)

	return values
