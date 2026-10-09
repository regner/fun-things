class_name S04DesktopInput
extends S02DesktopInput
## Reuses physical aliases/focus collection while preserving dedicated car meanings.


## Converts WASD bindings to throttle/steer and only Space to handbrake intent.
func drive_sample() -> Dictionary:
	return {
		"throttle": action_strength(&"s02_forward") - action_strength(&"s02_back"),
		"steer": action_strength(&"s02_right") - action_strength(&"s02_left"),
		"brake": 0.0,
		"handbrake": action_strength(&"s02_fire_alt") > 0.0,
	}
