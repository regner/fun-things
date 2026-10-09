class_name S04DriveHud
extends CanvasLayer
## Presents standalone speed, controls and editable values without owning simulation decisions.

@onready var _speed: Label = $Panel/Margin/Rows/Speed
@onready var _values: Label = $Panel/Margin/Rows/Values
@onready var _notice: Label = $Panel/Margin/Rows/Notice


## Refreshes the compact tuning panel from coordinator-owned state.
func update_display(speed_mps: float, tuning: S04DriveTuning, selected: int,
		notice: String) -> void:
	_speed.text = "SPEED  %5.1f m/s  (%3.0f km/h)" % [speed_mps, speed_mps * 3.6]
	var lines: PackedStringArray = []
	for index: int in tuning.value_count():
		var marker: String = ">" if index == selected else " "
		lines.append("%s F%d  %-24s %6.2f" % [
			marker, index + 1, tuning.display_name(index), tuning.value(index),
		])
	_values.text = "\n".join(lines)
	_notice.text = notice
