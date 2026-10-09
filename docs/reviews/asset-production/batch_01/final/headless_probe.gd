extends SceneTree
## Reads imported candidate resources from an isolated CLI project.


## Runs one bounded independent interface audit and writes only reviewer evidence.
func _initialize() -> void:
	var script: Script = load("/home/regner/.paseo/worktrees/0u71f39f/asset-register-production/docs/reviews/asset-production/batch_01/final/engine_probe.gd")
	var ids: Array[String] = ["city_lights_01", "city_lights_01_cool", "city_lights_02",
		"city_lights_02_cool", "city_lights_04", "city_lights_04_cool", "city_sign_supports_01",
		"city_planting_01", "city_planting_02"]
	var paths: Array = []
	for id: String in ids:
		paths.append("res://scenes/prefabs/environment/" + id + ".tscn")
	var data: Dictionary = script.new().inspect(paths)
	var output := FileAccess.open("/home/regner/.paseo/worktrees/0u71f39f/asset-register-production/docs/reviews/asset-production/batch_01/final/independent-engine-interfaces.json", FileAccess.WRITE)
	output.store_string(JSON.stringify(data, "\t") + "\n")
	print("Independent mesh/material/collision/UID interface audit completed for ", data.prefabs.size(), " prefabs")
	quit()
