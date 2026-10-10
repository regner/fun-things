extends SceneTree
## Extract fresh imported player actions and complementary layers without a live editor.


## Reuse the editor extraction contract in an isolated headless process.
func _initialize() -> void:
	var bridge: PlayerAssetEditorBridge = PlayerAssetEditorBridge.new()
	var summary: Dictionary = bridge.save_motion_libraries()
	bridge.save_layer_libraries()
	bridge.free()
	print("PLAYER_MOTION_EXTRACTED ", JSON.stringify(summary))
	quit()
