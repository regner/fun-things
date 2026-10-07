@tool
class_name S02EditorProbe
extends S01EditorProbe
## S02 editor bridge for discovered toolkit tools absent from the callable surface.

const INPUT_COMMANDS_PATH: String = (
	"res://addons/godot_mcp_toolkit/commands/input_map_commands.gd"
)


## Reports project and unsaved tabs before any scene switching.
func editor_state() -> Dictionary:
	return {
		"project": ProjectSettings.globalize_path("res://"),
		"open": EditorInterface.get_open_scenes(),
		"unsaved": EditorInterface.get_unsaved_scenes(),
	}


## Reads enum values from the exact pinned engine for editor property authoring.
func enum_values(type_name: String, enum_name: String) -> Dictionary:
	var values: Dictionary = {}
	for key: String in ClassDB.class_get_enum_constants(type_name, enum_name):
		values[key] = ClassDB.class_get_integer_constant(type_name, key)
	return values


## Copies a source-authored marker into a stable saved prefab socket.
func socket(source_path: String, target_path: String) -> void:
	var edited: Node = EditorInterface.get_edited_scene_root()
	var source: Node3D = edited.get_node(source_path)
	var target: Node3D = edited.get_node(target_path)
	target.global_transform = source.global_transform
	EditorInterface.mark_scene_as_unsaved()


## Delegates input-map edits to the installed toolkit without vendor changes.
func input_action(parameters: Dictionary) -> Dictionary:
	var commands: GDScript = load(INPUT_COMMANDS_PATH)
	return commands._cmd_input_map_action(parameters)


## Delegates saved device bindings to the installed toolkit.
func input_event(parameters: Dictionary) -> Dictionary:
	var commands: GDScript = load(INPUT_COMMANDS_PATH)
	parameters["event"] = JSON.parse_string(parameters["event_json"])
	return commands._cmd_input_map_event(parameters)
