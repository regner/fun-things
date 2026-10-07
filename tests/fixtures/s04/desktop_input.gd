class_name S04DesktopInput
extends S02DesktopInput
## Reuses physical aliases/focus collection; interprets Space as car handbrake.


## Converts sampled bindings to drive intent without deciding vehicle outcomes.
func drive_sample() -> Dictionary:
	var value: Dictionary = sample()
	return {"throttle": value.move, "steer": value.turn,
		"brake": 0.0, "handbrake": value.fire}
